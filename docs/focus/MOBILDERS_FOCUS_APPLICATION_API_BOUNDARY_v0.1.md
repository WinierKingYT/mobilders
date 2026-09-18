# MOBILDERS — FOCUS APPLICATION / API BOUNDARY

**Version:** 0.1  
**Status:** IMPLEMENTED FOUNDATION / FEATURE-FLAGGED  
**Authority:** Experience v0.5 FROZEN + Cognitive Domain v0.4 FROZEN + Implementation Erratum v0.1  
**Production Authorization:** NOT YET  

---

# 0. Mission

This contract defines the first external application boundary around the frozen Focus kernel.

Core rule:

> **The client may submit learner actions. The client may not submit mathematical truth or cognitive diagnosis.**

Therefore the public API does not accept:

```text
AttemptJudgment
ErrorObservation
KCState
BarrierState
repair eligibility
mastery claims
```

as client authority.

Those values are derived server-side.

---

# 1. Public Route Namespace

All routes are isolated under:

```text
/focus/v1
```

Current public foundation routes:

```text
POST /focus/v1/episodes
GET  /focus/v1/episodes/{episode_id}

POST /focus/v1/episodes/{episode_id}/attempts
POST /focus/v1/episodes/{episode_id}/probe-responses
POST /focus/v1/episodes/{episode_id}/repair/begin
```

No legacy endpoint is replaced.

---

# 2. Feature Flag

Integration uses:

```text
FOCUS_V1_ENABLED
```

Default:

```text
false
```

When disabled:

```text
/focus/v1 routes are not registered
```

This is stronger isolation than returning a runtime "disabled" response from an already exposed route.

---

# 3. Episode Creation

Client supplies only:

```text
episode_id
b
c
Idempotency-Key
```

For:

```text
x² + bx + c = 0
```

The server derives:

```text
factor pair
roots
branch equations
generation-profile validity
```

The client never supplies the expected factor pair or expected roots as authority.

Invalid Alpha tasks fail before learner evidence exists.

---

# 4. Server-Owned Task Context

`CTQF1TaskContext` is persisted in `FocusEpisodeState`.

It contains:

```text
b
c
factor_pair
expected_roots
factor_abs_max
```

This prevents the client from changing the mathematical task context between commands.

---

# 5. Public Attempt Inputs

Current `FocusAttemptInputKind`:

```text
FACTOR_PAIR
BRANCH_DECOMPOSITION
BRANCH_WORK
SOLUTION_SET
```

The server chooses the legal interpretation according to the persisted current stage.

The client does not submit `current_stage`.

---

# 6. Normal Expected Path

```text
S1 FACTOR
FACTOR_PAIR
↓
S2 BRANCH
BRANCH_DECOMPOSITION
↓
S3 SOLVE FACTOR EQUATIONS
BRANCH_WORK
↓
S4 COMPLETE SOLUTION SET
SOLUTION_SET
↓
COMPLETED
```

Stage progression is server-owned.

---

# 7. Shortcut Semantics

`SOLUTION_SET` is allowed before S4.

If complete and correct:

```text
S1/S2/S3
→ VALID_SHORTCUT
→ COMPLETE_TASK
```

It does not create positive evidence for bypassed KCs and does not clear prior learner debt.

---

# 8. Incomplete Work

Examples:

```text
S2:
one correct zero-product branch

S3:
one correct branch assignment
```

become:

```text
VALID_INCOMPLETE
```

not:

```text
INVALID_MATHEMATICS
```

No false misconception is created.

---

# 9. S3 BRANCH_WORK

The S3 public representation is a structured mapping:

```json
{
  "x+2=0": "x=-2",
  "x+3=0": "x=-3"
}
```

The server:

```text
matches only current expected branch equations
normalizes each assignment
marks each BranchWorkItem:
  PENDING
  VALID
  INVALID
  UNSUPPORTED
```

Then the frozen `BranchWorkSet` contract determines stage judgment.

---

# 10. Mathematical Authority

For factor-pair attempts the server executes:

```text
normalize
↓
stage judgment
↓
AlphaTruthAdapter
↓
ErrorObservationProducer
↓
Decision Pipeline
```

Example:

```text
x²+5x+6
learner pair: (1,6)

product = 6
sum = 7

→ INVALID_MATHEMATICS
→ EO-FACTOR-PAIR-SUM-MISMATCH
→ active-KC diagnostic routing
```

The client cannot forge this observation.

---

# 11. Unknown Invalidity

When a supported attempt is deterministically wrong but Alpha cannot classify the exact bounded error form:

```text
EO-UNKNOWN-INVALID-STEP
```

is preserved.

The system does not invent a more specific misconception.

---

# 12. Idempotency Transport

Every mutating public command requires:

```text
Idempotency-Key
```

The application boundary checks attempt idempotency before re-running stage-sensitive assessment.

Same episode + same key + same raw command:

```text
returns original command event/result
```

even if the episode has progressed afterward.

Same key + different raw command:

```text
409 FOCUS_STREAM_CONFLICT
```

---

# 13. Historical Retry Semantics

If event 2 originally advanced:

```text
S1 → S2
```

and the episode later reached event 5:

A retry of event 2 returns:

```text
stream_version = 2
state = state after event 2
```

not:

```text
latest state at event 5
```

This preserves response fidelity.

---

# 14. Optimistic Concurrency Transport

Mutating commands after episode creation require:

```text
X-Focus-Expected-Sequence
```

The value is passed to the journal as:

```text
expected_previous_sequence
```

Stale command:

```text
HTTP 409
FOCUS_STREAM_CONFLICT
```

No silent "apply against newest state" behavior is allowed.

---

# 15. Error Mapping

Current public mappings:

```text
404
FOCUS_EPISODE_NOT_FOUND

409
FOCUS_STREAM_CONFLICT

409
FOCUS_INVALID_TRANSITION

422
FOCUS_UNSUPPORTED_TASK

500
FOCUS_PERSISTENCE_INTEGRITY_ERROR
```

Pydantic/FastAPI request validation continues to use normal `422`.

---

# 16. Public Authority Deliberately NOT Exposed Yet

The public API does **not** expose client-controlled endpoints such as:

```text
"repair succeeded = true"
"self-correction succeeded = true"
"transfer succeeded = true"
"mastered = true"
"misconception confirmed = true"
```

Those would let the client become cognitive truth authority.

The internal orchestrator already supports these transitions, but future public endpoints must receive learner work and evaluate success server-side.

---

# 17. Repair Begin

The current public API exposes:

```text
POST /repair/begin
```

because this does not let the client decide whether repair is valid.

The server recomputes current decision authority and only begins repair if:

```text
NextAction = START_REPAIR
```

Otherwise the command fails.

---

# 18. Legacy Isolation

`main.py` keeps the existing legacy session router.

Focus is added separately:

```text
app.include_router(session_router)

install_focus_api(
    app,
    enabled=settings.FOCUS_V1_ENABLED,
)
```

No legacy detector, route, or learner model is replaced by Round 06.

---

# 19. API Integration State

```text
typed DTOs                    DONE
server-side attempt authority DONE
server-owned task context     DONE
public Focus service facade   DONE
/focus/v1 router              DONE
feature flag                  DONE / default off
idempotency transport         DONE
historical retry fidelity     DONE
optimistic concurrency        DONE
error mapping                 DONE
API contract tests            DONE
```

---

# 20. Still Not Production-Ready

Missing:

```text
authentication / authorization
rate limits specific to Focus
production SQL event adapter
production snapshot adapter
real user ownership of episode_id
PII/data-classification review
API observability / tracing
schema migration policy
mobile client integration
server-evaluated repair-result endpoints
server-evaluated transfer/retest endpoints
load/concurrency tests against real durable store
```

---

# 21. Authority Invariant

Final Round 06 invariant:

```text
CLIENT
=
learner input authority

SERVER
=
mathematical truth authority
+
cognitive evidence authority
+
state-transition authority
```

The boundary must not reverse this relationship.
