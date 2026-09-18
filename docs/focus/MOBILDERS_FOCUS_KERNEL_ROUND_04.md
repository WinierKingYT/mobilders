# MOBILDERS — FOCUS KERNEL IMPLEMENTATION ROUND 04

**Status:** COMPLETE / CHECKPOINT  
**Authority:** Experience v0.5 FROZEN + Cognitive Domain v0.4 FROZEN + Implementation Erratum v0.1  
**Implementation Mode:** Isolated pure-domain kernel  
**Production Authorization:** NOT YET  

---

# 0. Mission

Round 04 connects previously isolated Focus components into one bounded decision path:

```text
ProbeResponseEvaluator
+
Active-KC Diagnostic Routing
+
Prerequisite Repair Routing
+
FocusDecisionPipeline
+
FocusEpisodeOrchestrator
```

The objective is not more feature breadth.

The objective is:

> **Given supported mathematical evidence, choose the smallest defensible next cognitive action without inventing diagnosis or bypassing frozen recovery order.**

---

# 1. New Executable Flow

```text
SUPPORTED ATTEMPT
↓
ATTEMPT JUDGMENT
↓
MATHEMATICAL TRUTH
↓
ERROR OBSERVATION
↓
ACTIVE-KC DIAGNOSTIC ROUTE
↓
PROBE WHEN NEEDED
↓
DIRECT REPAIR OR PREREQUISITE REPAIR
↓
BOUNDED INTERVENTION
↓
RETURN TO ORIGINAL
↓
ORIGINAL SELF-CORRECTION
↓
TRANSFER
↓
TEMPORARY RECOVERY EVIDENCE
```

No persistence/API/UI authority is introduced in this round.

---

# 2. ProbeResponseEvaluator

Added:

```text
probe_evaluator.py
```

Responsibilities:

```text
validate probe ID
validate response class
produce ProbeEvidenceKind
update bounded KC evidence
update bounded barrier evidence
produce derived diagnostic flags
preserve uncertainty
never auto-confirm a barrier
```

Critical invariant:

```text
single probe support
≠
barrier confirmation
```

---

# 3. Probe Evidence Semantics

Examples:

```text
PR-N1-01 SIGN_INVERTED
→ KC-N1 SUPPORTED_GAP
→ no durable N1 barrier invented
```

```text
PR-N2-01 EXACT_NEGATIVE
→ KC-N2 SUPPORTED_GAP
→ BH-N2-01 SUPPORTED
```

```text
PR-E1-02 NEGATIVE_PRODUCT
→ KC-E1 SUPPORTED_GAP
→ no specific barrier selected
```

because material alternatives remain.

---

# 4. Derived Diagnostic Flags

Round 04 makes two previously implicit pieces of evidence executable:

```text
PR-Q0-01 positive
→ Q0_PASSED
```

```text
PR-N2-01 positive
→ N2_ALTERNATIVE_INSUFFICIENT
```

These flags do not diagnose another KC.

They only close/remove specific alternatives where a RepairEdge contract requires that evidence.

---

# 5. Active-KC Diagnostic Routes

A major implementation correction was discovered during this round.

The initial DecisionPipeline looked only at prerequisite RepairEdges.

That was unsafe.

Example:

```text
active KC = KC-F2 Factor-Pair Reasoning
observation = FACTOR_PAIR_SUM_MISMATCH
```

The system must not immediately descend to:

```text
KC-N1 Signed Addition
```

because the smallest defensible blocker may still be:

```text
BH-F2-01 Single-Constraint Factor Selection
```

Therefore Round 04 introduces:

```text
ActiveKCDiagnosticRoute
ACTIVE_DIAGNOSTIC_ROUTES
```

Canonical ordering:

```text
1. test bounded active-KC explanation
2. if supported → repair active KC
3. if weakened/inconclusive → use prior prerequisite evidence if available
4. otherwise abstain / neutral support / clean stop
```

This directly implements:

> **smallest defensible actionable blocker, not deepest imaginable cause.**

---

# 6. Active Diagnostic Route Registry

Current executable routes include:

```text
N1 → PR-N1-01 → IT-N1-01
N2 → PR-N2-01 → IT-N2-01
N3 → PR-N3-01 → IT-N3-01
E1 partial distribution → PR-E1-01 → IT-E1-01
E1 sign composition → PR-E1-02 → IT-E1-02
E2 → PR-E2-01 → IT-E2-01
Q0 → PR-Q0-01 → IT-Q0-01
Q1 → PR-Q1-01 → IT-Q1-01
F1 → PR-F1-01 → IT-F1-01
F2 → PR-F2-01 → IT-F2-01
Z1 → PR-Z1-01 → IT-Z1-01
```

Registry validation fails fast if:

```text
probe missing
intervention missing
probe target KC mismatches route
intervention target KC mismatches route
barrier missing from probe candidates
barrier missing from intervention authority
```

---

# 7. Direct vs Prerequisite Routing

Example canonical F2 path:

```text
x²+5x+6
learner chooses (x+1)(x+6)
↓
EO-FACTOR-PAIR-SUM-MISMATCH
↓
active-KC route first
↓
PR-F2-01
```

If response is:

```text
PRODUCT_ONLY
```

then:

```text
BH-F2-01 SUPPORTED
↓
IT-F2-01
```

No prerequisite descent is required.

If direct F2 evidence is weakened and a fresh prior N1 gap already exists:

```text
RE-F2-N1
```

may become legal.

This avoids the false rule:

```text
deeper prerequisite
=
more correct diagnosis
```

---

# 8. Neutral Support Authority

`InterventionTemplate` now has executable metadata:

```text
neutral_support_allowed
```

This encodes already-documented low-risk usage.

Current explicitly neutral-safe barrier templates:

```text
IT-N2-01
IT-E1-01
```

If a KC gap is supported but a durable barrier is not, the pipeline may use these only as:

```text
NEUTRAL_SUPPORT
```

not as barrier-confirming repair.

---

# 9. FocusDecisionPipeline

Added:

```text
decision_pipeline.py
```

Primary decisions:

```text
ADVANCE
REQUEST_COMPLETION
COMPLETE_TASK
REQUEST_PROBE
START_REPAIR
NEUTRAL_SUPPORT
CLARIFY_INPUT
FAIL_CLOSED
CLEAN_STOP
```

Important safety behavior:

```text
multiple eligible repair routes
→ no arbitrary tie-break
→ NEUTRAL_SUPPORT
```

```text
multiple competing probes
→ no arbitrary probe selection
→ NEUTRAL_SUPPORT
```

```text
unsupported domain / representation
→ FAIL_CLOSED
```

---

# 10. Episode Orchestrator

Added:

```text
FocusEpisodeOrchestrator
```

Phases:

```text
WORKSPACE
PROBING
REPAIRING
AWAITING_ORIGINAL_SELF_CORRECTION
AWAITING_TRANSFER
COMPLETED
STOPPED
```

The orchestrator is pure application logic.

It does not own persistence, API transport or UI.

---

# 11. Recovery Ordering — Executable

The orchestrator prevents:

```text
repair
→ transfer
```

without original self-correction.

Legal sequence:

```text
START_REPAIR
↓
REPAIR_ACTION_SUCCESS
↓
AWAITING_ORIGINAL_SELF_CORRECTION
↓
ORIGINAL_SELF_CORRECTION_SUCCESS
↓
AWAITING_TRANSFER
↓
TRANSFER_SUCCESS / FAILURE
```

Transfer success:

```text
KC → TEMPORARILY_RECOVERED
```

Transfer failure:

```text
restore unresolved prior gap evidence
```

---

# 12. VALID_SHORTCUT Preservation

Episode orchestration uses the existing frozen shortcut rule.

A correct final answer may:

```text
complete composite task
```

but cannot automatically:

```text
clear RETEST_DUE
clear supported/confirmed gaps
resolve barriers
create recovery evidence
```

---

# 13. New Files

```text
services/core-engine/app/focus_domain/probe_evaluator.py
services/core-engine/app/focus_domain/decision_pipeline.py
services/core-engine/tests/test_focus_probe_and_decision_pipeline.py
```

Updated:

```text
models.py
registry.py
__init__.py
```

---

# 14. Test Result

Full Focus kernel test run:

```text
67 passed
```

Compilation:

```text
COMPILE_OK
```

Test coverage in this checkpoint includes:

```text
attempt language
stage judgment
truth adapter
ErrorObservation
RepairEdge eligibility
learner-state transitions
probe response evaluation
active-KC diagnostic routing
prerequisite routing
neutral support safety
probe budget enforcement
recovery ordering
shortcut debt preservation
unsupported fail-closed behavior
```

---

# 15. Current Engineering State

```text
Experience Architecture                FROZEN
Cognitive Domain                       FROZEN + narrow erratum

SupportedAttemptLanguage               FOUNDATION COMPLETE
Stage Judgment                         FOUNDATION COMPLETE
Alpha Truth Adapter                    FOUNDATION COMPLETE
ErrorObservation Producer              FOUNDATION COMPLETE
RepairEdge Eligibility                 FOUNDATION COMPLETE
Learner State Transition               FOUNDATION COMPLETE
ProbeResponseEvaluator                 FOUNDATION COMPLETE
Active-KC Diagnostic Routing           FOUNDATION COMPLETE
Focus Decision Pipeline                FOUNDATION COMPLETE
Episode Orchestrator                   FOUNDATION COMPLETE

Persistence                            NOT STARTED
Event Journal / Idempotency            NOT STARTED
API Adapter                            NOT STARTED
Mobile Integration                     NOT STARTED
Legacy Migration                       NOT STARTED
Production Rollout                     NOT AUTHORIZED
```

---

# 16. Remaining Risk

The kernel is still an isolated package.

It has not yet proven:

```text
persistence crash/replay semantics
concurrent/idempotent event processing
API compatibility
migration from legacy learner evidence
mobile session restoration
production telemetry
```

These are deliberately next-stage concerns.

---

# 17. Next Correct Slice

The next engineering work should be:

```text
1. Focus Event Model
2. append-only Episode Event Journal abstraction
3. idempotent event application
4. snapshot reconstruction / replay
5. in-memory repository reference implementation
6. persistence contract tests
```

Only after that:

```text
Focus API Adapter / feature flag
```

The next stage should **not** be mobile UI yet.

---

# 18. Round Verdict

```text
ROUND 04
=
COMPLETE

FOCUS DECISION KERNEL
=
FOUNDATION READY

TESTS
=
67 PASS

NEXT
=
PERSISTENCE / EVENT-JOURNAL BOUNDARY
```
