# MOBILDERS — FOCUS KERNEL IMPLEMENTATION ROUND 05

**Status:** COMPLETE / CHECKPOINT  
**Authority:** Experience v0.5 FROZEN + Cognitive Domain v0.4 FROZEN + Implementation Erratum v0.1  
**Implementation Mode:** Persistence Boundary / Event-Sourced Reference Kernel  
**Production Authorization:** NOT YET  

---

# 0. Mission

Round 05 makes the Focus episode recoverable across process failure without weakening the frozen cognitive semantics.

The new persistence boundary is:

```text
Focus command
↓
pure FocusEpisodeOrchestrator
↓
validated next state
↓
append-only FocusEvent
↓
hash-chained journal
↓
snapshot/checkpoint
↓
replay/reconstruction
```

The journal is the source of truth.

Snapshots are acceleration artifacts only.

---

# 1. Added Persistence Module

New file:

```text
services/core-engine/app/focus_domain/persistence.py
```

It adds:

```text
FocusEventType
FocusEventDraft
FocusEvent
FocusEpisodeSnapshotRecord

FocusEventJournal Protocol
FocusSnapshotStore Protocol

InMemoryFocusEventRepository
InMemoryFocusSnapshotRepository

FocusEventReducer
FocusEpisodeReconstructor
FocusEpisodePersistenceService
```

The in-memory implementations are reference adapters.

Core services depend on the ports/protocols rather than a specific production database.

---

# 2. Append-Only Event Model

Current event types:

```text
EPISODE_CREATED
ATTEMPT_HANDLED
PROBE_RESPONSE_APPLIED
REPAIR_BEGUN
REPAIR_ACTION_SUCCEEDED
ORIGINAL_SELF_CORRECTION_SUCCEEDED
TRANSFER_RECORDED
```

No event mutates prior journal history.

Every event has:

```text
episode_id
idempotency_key
sequence
event_type
payload
occurred_at
previous_event_hash
event_hash
domain_contract_version
schema_version
```

---

# 3. Hash Chain

Each episode stream begins with:

```text
previous_event_hash = GENESIS
```

Then:

```text
event N hash
→
event N+1 previous_event_hash
```

Replay validates:

```text
contiguous sequence
correct previous hash
correct event hash
single episode identity
supported schema version
supported frozen-domain version
```

A modified event payload fails reconstruction.

---

# 4. Idempotent Command Application

Idempotency keys are scoped to:

```text
episode_id + idempotency_key
```

Semantics:

```text
same episode
+
same key
+
same logical command
→ return original event/result
→ no duplicate event
```

But:

```text
same episode
+
same key
+
different command
→ EventJournalConflict
```

This is checked before re-executing phase-sensitive commands.

Therefore a network retry of:

```text
PROBE_RESPONSE_APPLIED
```

does not fail merely because the first successful call already moved the episode out of `PROBING`.

---

# 5. Optimistic Stream Version

Every append request carries:

```text
expected_previous_sequence
```

The repository atomically verifies:

```text
expected_previous_sequence
==
current stream sequence
```

before append.

If two writers both read sequence 4:

```text
writer A appends sequence 5
writer B attempts append based on sequence 4
→ STALE STREAM CONFLICT
```

The second write is not silently appended to stale cognitive state.

This is mandatory for eventual database/API integration.

---

# 6. Atomic Reference Append

The in-memory event repository uses an append lock around:

```text
idempotency check
stream-version check
sequence allocation
hash creation
journal append
idempotency index update
```

This is reference behavior.

A production store must provide the same semantics with a transaction / unique constraint / compare-and-swap equivalent.

---

# 7. Invalid Commands Do Not Pollute the Journal

Command order is:

```text
load/reconstruct current state
↓
validate command through pure orchestrator
↓
derive next state
↓
append event
```

If the command is illegal:

```text
transfer before repair/self-correction
wrong probe phase
unsupported transition
```

no event is appended.

---

# 8. Crash / Replay

`FocusEventReducer` replays events through the same frozen episode semantics.

Example recovery:

```text
EPISODE_CREATED
ATTEMPT_HANDLED
PROBE_RESPONSE_APPLIED
REPAIR_BEGUN
REPAIR_ACTION_SUCCEEDED
ORIGINAL_SELF_CORRECTION_SUCCEEDED
TRANSFER_RECORDED
```

reconstructs the same:

```text
FocusEpisodeState
LearnerEvidenceSnapshot
EpisodePhase
repair metadata
probe budget/evidence
```

as the live execution.

Round 05 tests this with a complete F2 repair episode.

---

# 9. Snapshot Boundary

`FocusEpisodeSnapshotRecord` stores:

```text
episode_id
last_sequence
journal_head_hash
state
state_hash
domain_contract_version
schema_version
```

On load:

```text
snapshot state hash verified
snapshot journal anchor verified
tail sequence/hash chain verified
tail replayed
```

Therefore the snapshot cannot silently detach from the event journal.

---

# 10. Snapshot Is Not Authority

Canonical rule:

```text
JOURNAL = SOURCE OF TRUTH
SNAPSHOT = REPLAY ACCELERATOR
```

A snapshot may never invent or replace Focus events.

---

# 11. External Mutation Isolation

The reference repositories return deep copies.

Therefore code outside the repository cannot silently mutate:

```text
stored event payloads
stored snapshot state
```

and alter journal authority by object reference.

---

# 12. Frozen Contract Version Pinning

Current event pin:

```text
DOMAIN_CONTRACT_VERSION
=
0.4+implementation-erratum-0.1
```

Replay fails closed if persisted data claims a different contract version.

This avoids silently replaying old evidence semantics through a new cognitive model.

Future migration must be explicit.

---

# 13. Persistence Ports

Core persistence contracts:

```text
FocusEventJournal
FocusSnapshotStore
```

The service does not require the in-memory classes.

Future adapters can implement:

```text
SQLite
PostgreSQL
Cloud database
durable local mobile queue
```

without changing the Focus decision kernel.

---

# 14. Persistence Service

`FocusEpisodePersistenceService` currently exposes reference operations for:

```text
start_episode
load
handle_attempt
apply_probe_response
begin_current_repair
record_repair_action_success
record_original_self_correction_success
record_transfer_result
checkpoint
```

These methods preserve the same ordering enforced by `FocusEpisodeOrchestrator`.

---

# 15. Persistence Invariants Now Executable

```text
P1 journal is append-only
P2 sequence is contiguous
P3 event chain is hash-linked
P4 retry is idempotent
P5 idempotency collision is rejected
P6 stale concurrent writer is rejected
P7 invalid command writes no event
P8 snapshot must be hash-valid
P9 snapshot must anchor to journal
P10 replay equals live execution
P11 frozen contract version must match
P12 external object mutation cannot mutate repository storage
```

---

# 16. Test Coverage Added

New test file:

```text
tests/test_focus_persistence_round05.py
```

It verifies:

```text
contiguous sequence and hash chain
attempt retry idempotency
probe retry after phase transition
same-key/different-command conflict
full repair crash/replay equivalence
snapshot + tail equivalence
snapshot tamper detection
event payload tamper detection
invalid-phase no-write behavior
per-episode idempotency scope
optimistic concurrency conflict
repository deep-copy isolation
```

---

# 17. Test Result

```text
PYTHONPATH=. pytest -q tests/test_focus_*.py

80 passed
```

Compilation:

```text
python -m compileall -q app/focus_domain tests/test_focus_*.py

COMPILE_OK
```

---

# 18. Current Kernel State

```text
Attempt Language                DONE — foundation
Stage Judgment                  DONE — foundation
Truth Adapter                   DONE — foundation
ErrorObservation                DONE — foundation
RepairEdge Eligibility          DONE — foundation
Learner State Machine           DONE — foundation
ProbeResponseEvaluator          DONE — foundation
Active-KC Diagnostic Routing    DONE — foundation
Focus Decision Pipeline         DONE — foundation
Episode Orchestrator            DONE — foundation

Persistence Ports               DONE — foundation
Append-Only Event Journal       DONE — reference adapter
Idempotency                     DONE — reference semantics
Optimistic Concurrency          DONE — reference semantics
Hash Chain                      DONE — reference semantics
Snapshot Reconstruction         DONE — reference semantics
Crash / Replay                  DONE — reference semantics

Production DB Adapter           NOT STARTED
API Adapter                     NOT STARTED
Feature Flag                    NOT STARTED
Mobile Integration              NOT STARTED
Legacy Migration                NOT STARTED
Production Rollout              NOT AUTHORIZED
```

---

# 19. Remaining Persistence Limits

The reference repository is intentionally not production storage.

Still missing:

```text
durable database transaction implementation
cross-process concurrency control
database migrations
retention / archival policy
journal compaction policy
PII/data classification
backup/restore operations
observability/metrics
```

Those belong to production readiness, not the pure reference kernel.

---

# 20. Next Correct Engineering Slice

The next Focus implementation slice should be:

```text
Focus Application/API Boundary
```

Recommended order:

```text
1. typed command/request DTOs
2. Focus service facade
3. dedicated /focus API adapter
4. feature flag / isolation from legacy endpoints
5. idempotency key transport
6. optimistic-concurrency conflict mapping
7. structured response DTO
8. API contract tests
9. no direct legacy detector mutation
```

A real SQL adapter can follow after the API contract is stable, or in parallel behind the `FocusEventJournal` / `FocusSnapshotStore` ports.

---

# 21. Round Verdict

```text
ROUND 05
=
COMPLETE

PERSISTENCE BOUNDARY
=
FOUNDATION READY

TESTS
=
80 PASS

COMPILE
=
PASS

PRODUCTION STORAGE
=
NOT YET
```
