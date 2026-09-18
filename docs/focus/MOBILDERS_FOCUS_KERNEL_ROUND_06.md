# MOBILDERS — FOCUS KERNEL IMPLEMENTATION ROUND 06

**Status:** COMPLETE / CHECKPOINT  
**Work Area:** Application / API Boundary  
**Feature Flag:** `FOCUS_V1_ENABLED=false` by default  
**Production Authorization:** NOT YET  

---

# 0. Round Objective

Expose the frozen Focus kernel through a narrow, typed, server-authoritative application/API boundary without allowing the client to become mathematical or cognitive truth authority.

---

# 1. Added Files

```text
app/focus_domain/application.py
app/focus_domain/api.py
tests/test_focus_application_api_round06.py
docs/focus/MOBILDERS_FOCUS_APPLICATION_API_BOUNDARY_v0.1.md
docs/focus/MOBILDERS_FOCUS_KERNEL_ROUND_06.md
```

Integration overlay:

```text
app/main.py
app/core/config.py
```

---

# 2. Application Layer

Added:

```text
FocusAttemptInputKind
FocusAttemptAssessment
FocusCommandResult
FocusEpisodeView
CTQF1AttemptAssessmentService
FocusServiceFacade
```

The facade is the first boundary that coordinates:

```text
server-owned problem context
attempt normalization
stage judgment
truth
observations
persistence
decisions
```

---

# 3. Server-Owned CT-QF1 Context

Added:

```text
CTQF1TaskContext
```

The server derives the unique Alpha factor pair from `b,c`.

Example:

```text
b=5
c=6

→ factor_pair=(2,3)
→ roots=(-3,-2)
```

Repeated-root, zero-root, non-factorable, or generation-profile-invalid tasks are rejected before episode creation.

---

# 4. Stage Progression

CT-QF1-enabled episode state now carries:

```text
composite_task_id
current_stage
task_context
```

Expected progression:

```text
S1 / KC-F2
→ S2 / KC-Z1
→ S3 / KC-Q1
→ S4 completion
→ COMPLETED
```

Legacy/non-CT-QF1 FocusEpisodeState instances remain compatible because these fields are optional.

---

# 5. S3 Public Branch Work

Round 06 adds:

```text
BRANCH_WORK
```

so the public expected path can reach S4 without turning every correct S3 result into a shortcut.

One solved branch:

```text
VALID_INCOMPLETE
```

Two correct branch assignments:

```text
VALID_EXPECTED
→ advance S4
```

---

# 6. Idempotency Correction

Round 05 persistence already had event idempotency.

Round 06 closes an application-level gap:

Before:

```text
retry raw attempt
→ re-assess using current stage
→ then ask persistence about idempotency
```

This could change the meaning of an old retry after stage progression.

Now:

```text
raw command
↓
lookup episode+idempotency key
↓
if same raw command exists:
    return original historical result
else:
    assess current command
```

Different raw command with same key:

```text
hard conflict
```

---

# 7. Historical State Replay

Added:

```text
FocusEpisodePersistenceService.load_at_sequence()
```

Idempotent retry now returns the state at the original command's event sequence.

This also fixes response fidelity for persistence-level retries.

---

# 8. Client Stream Version

Persistence mutation methods now accept optional:

```text
expected_previous_sequence
```

The API requires:

```text
X-Focus-Expected-Sequence
```

for post-creation mutations.

This transports optimistic concurrency all the way from HTTP to journal append.

---

# 9. Feature-Flagged Integration

Added setting:

```text
FOCUS_V1_ENABLED
```

Default:

```text
false
```

`main.py` installs Focus only when the setting is true.

Default production behavior therefore remains unchanged.

---

# 10. Public Endpoints

```text
POST /focus/v1/episodes
GET  /focus/v1/episodes/{episode_id}
POST /focus/v1/episodes/{episode_id}/attempts
POST /focus/v1/episodes/{episode_id}/probe-responses
POST /focus/v1/episodes/{episode_id}/repair/begin
```

---

# 11. Deliberately Withheld Public Endpoints

Not exposed yet:

```text
repair-success
self-correction-success
transfer-success
retest-success
mastery updates
barrier confirmation
```

Reason:

> The client must not self-report cognitive truth.

The next round must first define server-evaluated work payloads for these transitions.

---

# 12. HTTP Safety

Supported mappings include:

```text
stale stream
→ 409 FOCUS_STREAM_CONFLICT

idempotency collision
→ 409 FOCUS_STREAM_CONFLICT

illegal transition
→ 409 FOCUS_INVALID_TRANSITION

unsupported Alpha task creation
→ 422 FOCUS_UNSUPPORTED_TASK

missing command headers
→ 422 request validation
```

---

# 13. Regression Found and Fixed During Round

A stage-progression helper insertion temporarily escaped `FocusEpisodeOrchestrator` class indentation and nested later methods under a helper function.

The suite caught:

```text
15 failures
```

The indentation was corrected.

Full pre-Round regression suite returned to:

```text
80 passed
```

before new API tests were accepted.

This regression is not present in the checkpoint.

---

# 14. Tests Added

Round 06 verifies:

```text
server derives factor pair / roots
correct S1 advances S2
partial S2 remains VALID_INCOMPLETE
S2 full root set is VALID_SHORTCUT
wrong factor pair creates server observation
active-KC probe request is server-derived
attempt retry returns historical original result
idempotency collision rejects changed raw command
feature flag disabled registers no routes
start/get/attempt HTTP contract
stale stream maps 409
unsupported task maps 422
required headers validated
complete S1→S2→S3→S4 public path
partial S3 branch work remains incomplete
```

---

# 15. Test Result

```text
PYTHONPATH=. pytest -q tests/test_focus_*.py

94 passed
```

Compilation:

```text
python -m compileall -q \
  app/focus_domain \
  app/main.py \
  app/core/config.py \
  tests/test_focus_*.py

COMPILE_OK
```

---

# 16. Current Engineering State

```text
Cognitive Kernel              DONE — foundation
Decision Pipeline             DONE — foundation
Episode Orchestrator          DONE — foundation

Persistence Ports             DONE
Event Journal                 DONE — reference
Idempotency                   DONE
Optimistic Concurrency        DONE
Crash / Replay                DONE
Snapshots                     DONE

Application Facade            DONE — foundation
Public Attempt Authority      DONE — foundation
/focus/v1 API                 DONE — foundation
Feature Flag                  DONE — default off
HTTP Conflict Mapping         DONE — foundation
API Contract Tests            DONE

Production SQL Adapter        NOT STARTED
Auth / Ownership              NOT STARTED
Server-evaluated repair work  NEXT
Server-evaluated transfer     NEXT
Mobile Integration            NOT STARTED
Production Rollout            NOT AUTHORIZED
```

---

# 17. Next Correct Slice

The next engineering slice should **not** expose boolean success commands.

It should implement:

```text
Repair Work Evaluation Boundary
```

Order:

```text
1. RepairWorkAttempt DTO
2. intervention-specific deterministic evaluator
3. repair success derived server-side
4. original self-correction attempt evaluator
5. transfer item context persisted server-side
6. transfer attempt evaluator
7. delayed-retest command/evaluator
8. API endpoints using learner work, not success booleans
9. transition contract tests
```

This is required before the full recovery loop can safely cross the public API boundary.

---

# 18. Round Verdict

```text
ROUND 06
=
COMPLETE

APPLICATION/API BOUNDARY
=
FOUNDATION READY

PUBLIC CLIENT COGNITIVE AUTHORITY
=
DENIED BY DESIGN

TESTS
=
94 PASS

COMPILE
=
PASS

FEATURE FLAG
=
DEFAULT OFF

PRODUCTION
=
NOT AUTHORIZED
```
