# MOBILDERS — FOCUS KERNEL IMPLEMENTATION ROUND 03

**Round:** 03  
**Status:** `IMPLEMENTED / TESTED`  
**Authority:** Frozen Experience + Frozen Domain v0.4 + Implementation Erratum v0.1  
**Scope:** Truth → Observation → Repair Eligibility → Learner-State Transition  
**Production Rollout:** `NOT AUTHORIZED`

---

# 1. Objective

Round 03 converts the frozen cognitive-domain rules into a deeper executable kernel.

The implemented pipeline is now conceptually:

```text
SupportedAttempt
↓
StageJudgment
↓
AlphaTruthAdapter
↓
ErrorObservationProducer
↓
RepairEvidenceContext
↓
RepairEdgeEligibilityEvaluator
↓
Bounded Intervention Target
↓
LearnerStateTransitionService
```

The central rule remains:

```text
Mathematical invalidity
≠ ErrorObservation
≠ Barrier diagnosis
≠ Repair authorization
≠ Recovery
```

Each transition is represented separately.

---

# 2. New Kernel Modules

```text
app/focus_domain/truth_adapter.py
app/focus_domain/observations.py
app/focus_domain/repair_evaluator.py
app/focus_domain/learner_state.py
```

New tests:

```text
tests/test_focus_truth_observation_repair_state.py
```

Existing Focus tests remain active.

---

# 3. Alpha Truth Adapter

`AlphaTruthAdapter` is deliberately narrower than the legacy CAS.

It provides deterministic truth checks only for frozen Alpha capabilities:

```text
signed addition
signed multiplication
unary negation
distribution
like-term action
additive equality preservation
simple factor root solving
binomial product structure
factor-pair constraints
zero-product application
```

It does not expose the broad legacy mathematical function whitelist.

This prevents technical solver breadth from silently redefining product support.

---

# 4. Generated CT-QF1 Truth Spec

`AlphaQuadraticTaskSpec` deterministically derives:

```text
b = m+n
c = mn
factor pair
branch equations
solution roots
canonical polynomial
```

Generation constraints remain:

```text
m,n != 0
m != n
abs(m),abs(n) <= GenerationProfile.alpha.factor_abs_max
```

The ±6 bound is treated as generation policy, not learner cognition.

`x²-9=0` remains valid Alpha content through:

```text
m=3
n=-3
```

---

# 5. Truth Facts Are Not Diagnoses

The truth adapter emits bounded mathematical facts such as:

```text
TF-SIGN-WRONG
TF-SIGNED-SUM-WRONG
TF-PARTIAL-DISTRIBUTION
TF-DISTRIBUTION-SIGN-COMPOSITION-WRONG
TF-EQUALITY-ONE-SIDE-CHANGED
TF-FACTOR-PAIR-SUM-MISMATCH
TF-FACTOR-PAIR-PRODUCT-MISMATCH
TF-ZERO-PRODUCT-MISAPPLIED
```

These are deterministic mathematical facts.

They are not learner identities.

---

# 6. ErrorObservation Producer

`ErrorObservationProducer` enforces the frozen rule:

```text
AttemptJudgment must equal INVALID_MATHEMATICS
```

before an ordinary mathematical `ErrorObservation` can exist.

Therefore:

```text
VALID_EXPECTED      → no ErrorObservation
VALID_INCOMPLETE    → no mathematical ErrorObservation
VALID_SHORTCUT      → no ErrorObservation
AMBIGUOUS_INPUT     → no ErrorObservation
UNSUPPORTED_STEP    → no ErrorObservation
UNSUPPORTED_DOMAIN  → no ErrorObservation
```

Only deterministic invalid supported mathematics may emit observations.

---

# 7. Unknown Invalidity Is Preserved Without Overdiagnosis

Not every invalid response matches one of the bounded Alpha error patterns.

Round 03 therefore adds:

```text
EO-UNKNOWN-INVALID-STEP
```

This means:

> The mathematics is deterministically invalid, but the current bounded model cannot responsibly assign a more specific error pattern.

This preserves evidence without manufacturing a misconception.

---

# 8. Machine-Evaluable Repair Evidence

Before Round 03, `RepairEdge.required_evidence` was explanatory text.

Round 03 adds:

```text
RepairEvidencePolicy
```

with executable fields:

```text
accepted_probe_evidence
allowed_target_kc_states
state_support_required_flags
required_flags
disqualifying_flags
```

Human-readable `required_evidence` remains documentation only.

Routing authority is now the structured policy.

---

# 9. Repair Edge Evaluator

`RepairEdgeEligibilityEvaluator` returns explicit statuses:

```text
ELIGIBLE
NEEDS_PROBE
BLOCKED_PROBE_BUDGET
MISSING_REQUIRED_CONTEXT
DISQUALIFIED
INELIGIBLE_ACTIVE_KC
INELIGIBLE_OBSERVATION
```

A legal graph edge is therefore not automatically executable.

It requires:

```text
active KC match
+
eligible ErrorObservation
+
structured evidence guard
+
required context
+
no disqualifying evidence
+
probe budget compatibility
```

---

# 10. Freshness Guard

Some frozen routes permit:

```text
strong recent prior KC gap evidence
```

A raw KC state alone is insufficient to prove recency.

Round 03 therefore requires:

```text
FRESH_TARGET_GAP_EVIDENCE
```

when a route uses prior KC-state evidence instead of a current probe.

Without the freshness flag:

```text
old CONFIRMED_GAP
```

does not silently reopen a repair route.

---

# 11. Transfer Evidence Can Disqualify Old Repair Debt

Routes that rely on historical N1/N2 gap state can be blocked by:

```text
RECENT_KC_N1_TRANSFER_SUCCESS
RECENT_KC_N2_TRANSFER_SUCCESS
```

This prevents stale weakness records from overriding more recent independent success.

---

# 12. N1 Implementation Closure Erratum

Implementation found that N1 repair routes had no executable intervention.

Round 03 adds:

```text
IT-N1-01 Signed Sum Decomposition
```

and wires:

```text
RE-F1-N1
RE-F2-N1
RE-Q1-N1
```

to that intervention.

No durable N1 misconception family is created.

This is documented separately in:

```text
MOBILDERS_V1_COGNITIVE_DOMAIN_IMPLEMENTATION_ERRATUM_v0.1.md
```

---

# 13. Learner-State Transition Service

`LearnerStateTransitionService` now encodes the frozen recovery semantics.

Critical transitions:

```text
SUPPORTED GAP
→ REPAIRING

REPAIR ACTION SUCCESS
→ still REPAIRING

ORIGINAL SELF-CORRECTION SUCCESS
→ still REPAIRING

TRANSFER SUCCESS
→ TEMPORARILY_RECOVERED

RETEST SCHEDULED
→ RETEST_DUE

DELAYED RETEST SUCCESS
→ DURABLE_EVIDENCE

DELAYED RETEST FAILURE
→ RELAPSED
```

Canonical invariant:

```text
MICRO_REPAIR_SUCCESS != RECOVERED
ORIGINAL_SELF_CORRECTION != RECOVERED
TRANSFER_SUCCESS = TEMPORARY_RECOVERY_ELIGIBLE
DELAYED_RETEST_SUCCESS = DURABLE_RECOVERY_EVIDENCE
```

---

# 14. State Downgrade Protection

Round 03 prevents weaker/stale events from overwriting stronger evidence.

Examples:

```text
CONFIRMED_GAP
+ later GAP_SUPPORTED event
→ remains CONFIRMED_GAP
```

and stale confirmation events cannot overwrite:

```text
REPAIRING
TEMPORARILY_RECOVERED
RETEST_DUE
RELAPSED
DURABLE_EVIDENCE
```

This prevents event-order bugs from laundering learner state.

---

# 15. Repair Cannot Start Merely Because a Retest Is Due

`RETEST_DUE` means:

```text
collect delayed evidence
```

It does not mean:

```text
confirmed active gap
```

Therefore `REPAIR_STARTED` is not legal directly from `RETEST_DUE`.

A failed retest must first create:

```text
RELAPSED
```

before a new repair begins.

---

# 16. Registry Fail-Fast Checks

Registry validation now checks:

```text
all probe IDs exist
all intervention IDs exist
all RepairEdge observations are registered EO codes
all active RepairEdges have an intervention target
human/machine disqualifying evidence does not drift
all N1 RepairEdges use PR-N1-01
```

This turns several documentation assumptions into executable invariants.

---

# 17. Test Result

Current complete Focus test suite:

```text
49 passed
```

Compilation:

```text
COMPILE_OK
```

The tests cover:

```text
attempt language
stage judgment
VALID_INCOMPLETE
VALID_SHORTCUT preservation
branch semantics
truth facts
ErrorObservation safety
unknown invalidity
repair routing
probe budgets
freshness guards
disqualifying transfer evidence
N1 intervention closure
repair/recovery transitions
delayed durability
state downgrade prevention
```

---

# 18. What Is Still Not Implemented

Round 03 does **not** yet implement:

```text
one orchestration service connecting the whole pipeline
probe-answer → ProbeEvidence classifier for every probe
persistent learner-state repository
event journal / idempotency contract
API endpoints
feature flag
mobile workspace integration
migration from legacy detector / weakness ledger
production rollout
```

These remain intentionally outside this round.

---

# 19. Current Kernel Maturity

```text
Domain Authority          FROZEN + ERRATUM
Attempt Language          IMPLEMENTED FOUNDATION
Stage Judgment            IMPLEMENTED FOUNDATION
Truth Adapter             IMPLEMENTED FOUNDATION
ErrorObservation          IMPLEMENTED FOUNDATION
Repair Eligibility        IMPLEMENTED FOUNDATION
Learner State Machine     IMPLEMENTED FOUNDATION
Persistence               NOT STARTED
API Integration           NOT STARTED
Mobile Integration        NOT STARTED
Production Migration      NOT STARTED
```

---

# 20. Next Engineering Work

The next correct implementation slice is:

# `Focus Decision Pipeline / Episode Orchestrator`

It should connect:

```text
normalized learner attempt
→ stage judgment
→ truth check
→ ErrorObservation
→ probe need / repair eligibility
→ bounded intervention decision
→ learner-state event
```

The same round should add:

```text
ProbeResponseEvaluator
```

so `ProbeEvidenceKind` is produced by deterministic code rather than passed in manually.

Only after that should persistence/API integration begin.

---

# 21. Decision

```text
ROUND 03 = PASS
KERNEL = DEEPENED
DOMAIN SCOPE = NOT WIDENED
PRODUCTION = NOT AUTHORIZED
NEXT = FOCUS DECISION PIPELINE + PROBE EVALUATOR
```
