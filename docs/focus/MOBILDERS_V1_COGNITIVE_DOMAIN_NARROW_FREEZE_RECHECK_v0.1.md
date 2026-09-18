# MOBILDERS — V1 COGNITIVE DOMAIN NARROW FREEZE RECHECK

**Version:** 0.1  
**Review Target:** `MOBILDERS_V1_COGNITIVE_DOMAIN_CONTRACT_v0.4.md`  
**Prior Review:** `MOBILDERS_V1_COGNITIVE_DOMAIN_FREEZE_REVIEW_v0.1.md`  
**Review Type:** Narrow correction recheck  
**Scope Rule:** R1–R9 only; no new product/domain ideation  
**Verdict:** `SHIP / FROZEN`  
**Freeze Authorization:** `GRANTED`  
**Implementation Status:** Foundation implementation may continue under frozen contract  

---

# 0. Recheck Standard

This review does not ask whether Mobilders should broaden the curriculum, add a new UI, add a new misconception family, or redesign Experience.

It asks only whether v0.4 correctly closes the previously enumerated freeze requirements:

```text
R1  VALID_INCOMPLETE
R2  PR-N1-01 + N1 RepairEdge wiring
R3  KC-Q0 micro-domain alignment
R4  fully instantiated active intervention templates
R5  S3 BranchWorkItem semantics
R6  VALID_SHORTCUT prior-evidence preservation
R7  correct probe-count metadata
R8  ErrorObservation wording/authority
R9  canonical SolutionSet representation
```

Freeze passes only if all nine are closed without introducing a new contradiction inside the reviewed scope.

---

# 1. Executive Verdict

```text
BLOCKER = 0
MAJOR   = 0
MINOR   = 0 within narrow freeze scope
```

Result:

```text
MOBILDERS_V1_COGNITIVE_DOMAIN_CONTRACT_v0.4
=
FROZEN
```

The prior `FIX-FIRST` decision is resolved.

This freeze does **not** authorize arbitrary curriculum expansion or legacy-system rewrites. It freezes the V1 Alpha cognitive-domain contract described by v0.4.

---

# 2. R1 — VALID_INCOMPLETE

## Requirement

The domain needed a state for mathematically valid but incomplete work.

## v0.4 result

Canonical `AttemptJudgment` now contains:

```text
VALID_EXPECTED
VALID_INCOMPLETE
VALID_SHORTCUT
INVALID_MATHEMATICS
AMBIGUOUS_INPUT
UNSUPPORTED_STEP_FORM
UNSUPPORTED_DOMAIN
```

`VALID_INCOMPLETE` is explicitly separated from `INVALID_MATHEMATICS`.

Canonical branch example:

```text
Expected:
x-2=0 OR x+3=0

Learner:
x-2=0

Judgment:
VALID_INCOMPLETE
```

Allowed side effects:

```text
CompositeTaskFailure where applicable
positive evidence for directly observed valid sub-action
```

Forbidden:

```text
mathematical ErrorObservation merely because the second branch is missing
durable barrier creation from incompleteness alone
false completion
false recovery
```

## Recheck verdict

```text
R1 = CLOSED
```

No contradiction found.

---

# 3. R2 — PR-N1-01 and N1 RepairEdges

## Requirement

Prior RepairEdges referenced a signed-addition check that had no canonical evidence producer.

## v0.4 result

Canonical probe now exists:

```text
PR-N1-01 — Signed Addition/Subtraction Check
```

It can emit:

```text
positive KC-N1 evidence
KC-N1 gap evidence
weaker KC-N1 gap evidence
INCONCLUSIVE
```

without inventing a durable N1 barrier family.

N1-targeting active RepairEdges are explicitly wired to `PR-N1-01`:

```text
RE-F1-N1
RE-F2-N1
```

Their required evidence is no longer an undefined human-readable placeholder.

## Executable contract check

The foundation registry validates:

```text
all active N1 RepairEdges
→ preferred_probe_id == PR-N1-01
```

## Recheck verdict

```text
R2 = CLOSED
```

---

# 4. R3 — KC-Q0 Micro-Domain Alignment

## Requirement

The old KC-Q0 description was narrower than its own probe/intervention behavior.

## v0.4 result

KC-Q0 now explicitly supports the bounded additive equality-preservation forms:

```text
x + a = r
x - a = r
```

with the core transformation:

```text
L = R
→
L + k = R + k
```

This matches:

```text
PR-Q0-01
IT-Q0-01
```

Explicit non-scope remains:

```text
general ax+b=c family
variables on both sides
multiplicative equality transformations
division-based solving
fractions
systems
inequalities
```

Therefore the fix aligns the micro-domain without accidentally reopening general linear equations.

## Recheck verdict

```text
R3 = CLOSED
```

---

# 5. R4 — Intervention Template Completeness

## Requirement

Every Alpha-active intervention needed a mechanically inspectable contract.

## v0.4 result

The required fields are defined:

```text
intervention_id
target_kc_or_task
eligible_barriers_or_failures
allowed_barrier_states
student_action
prompt_schema
truth_rule
success_condition
failure_condition
max_attempts
next_action_on_success
next_action_on_failure
prohibited_scaffolds
```

The active registry contains exactly 11 intervention templates:

```text
IT-N2-01
IT-N3-01
IT-E1-01
IT-E1-02
IT-E2-01
IT-Q0-01
IT-Q1-01
IT-F1-01
IT-F2-01
IT-Z1-01
IT-QF1-01
```

Each is instantiated rather than named only in prose.

`IT-QF1-01` is correctly modeled as task-completion support for `CTF-QF1-01`, not as durable-barrier remediation.

## Executable contract check

Registry self-validation asserts:

```text
len(INTERVENTION_TEMPLATES) == 11
```

and verifies referenced intervention IDs exist.

## Recheck verdict

```text
R4 = CLOSED
```

---

# 6. R5 — S3 Two-Branch Execution Semantics

## Requirement

The prior contract did not fully define execution when one factor branch was solved and the other remained unresolved.

## v0.4 result

S3 now has:

```text
BranchWorkSet
└── BranchWorkItem[]
```

Each branch records:

```text
branch_id
source_factor_ast / canonical source factor
expected_equation_ast / canonical equation
expected_assignment_ast / canonical assignment
assignment_status
observed_attempt_id?
```

Allowed assignment states:

```text
PENDING
VALID
INVALID
UNSUPPORTED
```

Alpha CT-QF1 requires two distinct branches because repeated roots remain out of scope.

Completion:

```text
both branches VALID
OR
a supported complete VALID_SHORTCUT
```

One correct + one missing branch:

```text
VALID_INCOMPLETE
+
CTF-QF1-01 ROOT_BRANCH_INCOMPLETE
```

not `INVALID_MATHEMATICS`.

## Executable contract check

The foundation models enforce exactly two distinct Alpha branches and reject repeated/equal branch equations.

Stage tests verify:

```text
VALID + PENDING
→ VALID_INCOMPLETE
```

## Recheck verdict

```text
R5 = CLOSED
```

---

# 7. R6 — VALID_SHORTCUT Existing-Evidence Safety

## Requirement

A correct shortcut must not erase previously accumulated learner evidence.

## v0.4 result

Canonical invariant:

```text
CompositeTaskSuccess
≠
LearnerStateReset
```

A `VALID_SHORTCUT` must not automatically:

```text
clear SUSPECTED_GAP
clear SUPPORTED_GAP
clear CONFIRMED_GAP
resolve durable barrier state
clear RETEST_DUE
clear RELAPSED
create TEMPORARILY_RECOVERED
create DURABLE_EVIDENCE
```

for bypassed KCs.

Exception is narrow:

```text
the item was explicitly registered as the retest/transfer item
for that exact KC/barrier
AND
its evidence contract is satisfied
```

Even then, the shortcut mechanism itself does not invent a mastery state.

## Executable contract check

Foundation tests verify:

```text
CT-QF1 may become COMPLETED_INDEPENDENTLY
while KC-F2 remains RETEST_DUE
and BH-F2-01 remains SUPPORTED
```

## Recheck verdict

```text
R6 = CLOSED
```

---

# 8. R7 — Probe Count Metadata

## Requirement

The metadata count must match the actual canonical probe registry.

## v0.4 result

Primary probes:

```text
PR-N1-01
PR-N2-01
PR-N3-01
PR-E1-01
PR-E1-02
PR-E2-01
PR-Q0-01
PR-Q1-01
PR-F1-01
PR-F2-01
PR-Z1-01
```

Count:

```text
11
```

Metadata states:

```text
11 fully specified primary Probe Templates
```

## Executable contract check

```text
len(PROBE_TEMPLATES) == 11
```

## Recheck verdict

```text
R7 = CLOSED
```

---

# 9. R8 — ErrorObservation Authority

## Requirement

Remove ambiguous language that could allow valid-but-incomplete work to produce a mathematical error observation.

## v0.4 result

Canonical ordinary-attempt rule:

```text
AttemptJudgment = INVALID_MATHEMATICS
AND
attempt form supported
AND
parser interpretation unambiguous
AND
error class deterministically identifiable
```

Only then may a mathematical `ErrorObservation` be emitted.

Explicitly:

```text
VALID_INCOMPLETE → not a mathematical error
VALID_SHORTCUT → not a mathematical error
AMBIGUOUS_INPUT → not a mathematical error
UNSUPPORTED_STEP_FORM → not a learner error
UNSUPPORTED_DOMAIN → not a learner error
```

Probe responses remain separate `ProbeEvidence`.

## Recheck verdict

```text
R8 = CLOSED
```

---

# 10. R9 — Canonical SolutionSet Representation

## Requirement

The domain needed an implementable internal representation and an explicit Alpha surface strategy.

## v0.4 result

Internal form:

```text
SolutionSet(
  assignments=[
    Assignment("x", Int(-2)),
    Assignment("x", Int(-3))
  ]
)
```

Canonical comparison is order-insensitive.

Primary Alpha UI is structured:

```text
Root 1: [ input ]
Root 2: [ input ]
```

Optional supported text spellings may normalize to the same internal value.

If a spelling is not explicitly supported:

```text
UNSUPPORTED_STEP_FORM
```

No guessing is authorized.

## Executable contract check

Foundation normalizer canonicalizes examples such as:

```text
{x=-3, x=2}
x=2 veya x=-3
```

into the same sorted solution-set representation.

## Recheck verdict

```text
R9 = CLOSED
```

---

# 11. Adversarial Cross-Checks

The following cases were checked because they could silently reopen prior failures.

## Case A — One valid S2 branch

```text
x-2=0
```

Expected:

```text
VALID_INCOMPLETE
CTF-QF1-01
no mathematical ErrorObservation
```

Pass.

## Case B — One correct + one wrong branch

```text
x-2=0 OR x+4=0
```

Expected:

```text
INVALID_MATHEMATICS
```

with the correct observed branch still preservable as local positive evidence.

Pass.

## Case C — Early complete final solution

Current stage:

```text
S1 FACTOR
```

Learner submits correct full solution set.

Expected:

```text
VALID_SHORTCUT
composite completion allowed
bypassed KC evidence not fabricated
```

Pass.

## Case D — Prior KC debt + shortcut

Prior:

```text
KC-F2 = RETEST_DUE
```

Correct final shortcut occurs.

Expected:

```text
KC-F2 remains RETEST_DUE
```

unless the task was explicitly the F2 retest under its evidence contract.

Pass.

## Case E — Fractional root input

Example:

```text
x=1/2
```

Expected:

```text
UNSUPPORTED_DOMAIN
```

not learner mathematical error, because fractions are outside Alpha.

Pass.

## Case F — Repeated root branch structure

Example conceptual task:

```text
(x+2)(x+2)=0
```

Expected:

```text
outside CT-QF1 Alpha
```

because repeated roots are frozen out.

Pass.

---

# 12. Executable Foundation Evidence

The first implementation slices encode the frozen contract in:

```text
app/focus_domain/models.py
app/focus_domain/registry.py
app/focus_domain/rules.py
app/focus_domain/attempt_language.py
app/focus_domain/stage_judgment.py
```

Test suites:

```text
test_focus_domain_contract_v04.py
test_focus_attempt_language_and_stage_judgment.py
```

Current result:

```text
26 passed
COMPILE_OK
```

This test result supports implementability, but freeze authority comes from the contract review rather than test count alone.

---

# 13. Scope Stability Check

v0.4 did not add:

```text
new curriculum family
new Repairable KC
new durable barrier family
new composite task
new user-facing goal
new product surface
new Experience flow
new general linear-equation domain
```

The correction remains a correction rather than a stealth expansion.

---

# 14. Frozen Counts

The following counts are now frozen for this V1 Alpha domain contract:

```text
10 Repairable KCs
1 Composite Task
2 Truth Invariants
2 Boundary Assumptions
10 Durable Barrier Families
1 CompositeTaskFailure family
11 primary Probe Templates
11 Intervention Templates
13 Problem Families
2 Transfer Levels
3 User-Facing Domain Goals
1 SupportedAttemptLanguage contract
7 AttemptJudgment classes
1 S3 BranchWorkSet contract
```

Changing these counts requires an explicit later domain revision, not incidental implementation drift.

---

# 15. Freeze Invariants

From this point, implementation must preserve:

```text
VALID_INCOMPLETE ≠ INVALID_MATHEMATICS

VALID_SHORTCUT
≠ bypassed-KC mastery evidence

parser limitation
≠ learner error

unsupported domain
≠ learner deficit

CompositeTaskFailure
≠ durable misconception

ProbeEvidence
≠ InterventionSuccess

one correct branch
≠ complete solution set
```

---

# 16. What Is Now Allowed

Implementation may proceed on the frozen contract for:

```text
SupportedAttemptLanguage parser/normalizer
stage-specific attempt judgment
narrow Alpha truth adapter
ErrorObservation producer
RepairEdge eligibility evaluator
learner-state transition service
Focus API adapter / feature flag
persistence contracts
mobile integration for the frozen Alpha flow
```

Each implementation layer still needs its own tests/review.

---

# 17. What Is Still Not Allowed By This Freeze

This freeze does not justify:

```text
general CAS exposure as Product Alpha language
broad curriculum activation
legacy detector deletion without migration evidence
OCR/voice expansion
teacher/LTI work
Learning Map expansion
generic AI tutor fallback
new durable misconception families by implementation convenience
```

---

# 18. Final Verdict

```text
V1 COGNITIVE DOMAIN CONTRACT v0.4
=
SHIP / FROZEN
```

Prior freeze-review findings:

```text
R1 CLOSED
R2 CLOSED
R3 CLOSED
R4 CLOSED
R5 CLOSED
R6 CLOSED
R7 CLOSED
R8 CLOSED
R9 CLOSED
```

Findings in narrow recheck:

```text
BLOCKER 0
MAJOR   0
MINOR   0
```

Implementation may now continue against this frozen authority.

The next engineering task is not another domain-design round. It is to deepen the executable Focus kernel while preventing legacy breadth from leaking into the Alpha contract.
