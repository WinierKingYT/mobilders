# MOBILDERS — V1 COGNITIVE DOMAIN CONTRACT

**Version:** 0.4  
**Status:** FREEZE CORRECTION / NARROW FREEZE RECHECK CANDIDATE  
**Parent Authority:** `MOBILDERS_FOCUS_ARCHITECTURE_v0.2.md`  
**Experience Authority:** `MOBILDERS_V1_EXPERIENCE_ARCHITECTURE_v0.5.md` — `FROZEN`  
**Supersedes:** `MOBILDERS_V1_COGNITIVE_DOMAIN_CONTRACT_v0.3.md`  
**Review Basis:** `MOBILDERS_V1_COGNITIVE_DOMAIN_FREEZE_REVIEW_v0.1.md`  
**Scope:** V1 Alpha Cognitive Mathematics Domain  
**Implementation Authorization:** FOUNDATION IMPLEMENTATION MAY BEGIN ON ISOLATED BRANCH  
**Freeze Authorization:** PENDING NARROW DOMAIN FREEZE RECHECK  

---

# 0. Revision Mission

V0.4 is a freeze-correction revision.

It does not add a new curriculum area, knowledge component, durable barrier, user goal, or product surface.

It closes exactly the freeze-review requirements:

```text
R1  add VALID_INCOMPLETE
R2  add PR-N1-01 and wire N1 RepairEdges to it
R3  align KC-Q0 micro-domain with its probe/intervention
R4  fully instantiate every active intervention template
R5  specify S3 BranchWorkItem semantics
R6  preserve prior learner evidence under VALID_SHORTCUT
R7  correct probe-count metadata
R8  remove ambiguous ErrorObservation wording
R9  define canonical SolutionSet representation
```

No other scope change is authorized.

---

# 1. Frozen-Upstream Invariants

The Experience Architecture remains authoritative.

Canonical repair order:

```text
ERROR / BLOCKER EVIDENCE
↓
PROBE WHEN NEEDED
↓
MICRO-REPAIR
↓
RETURN TO ORIGINAL PROBLEM
↓
ORIGINAL SELF-CORRECTION
↓
TRANSFER
↓
TEMPORARY RECOVERY ELIGIBLE
```

Domain V0.4 must not contradict this order.

Alpha remains bounded to:

```text
10 Repairable KCs
1 Composite Task
2 Truth Invariants
2 Boundary Assumptions
10 Durable Barrier Families
1 CompositeTaskFailure family
3 User-Facing Domain Goals
```

---

# 2. Repairable Knowledge Components

The v0.3 KC set is unchanged.

```text
KC-N1  Signed Addition / Subtraction
KC-N2  Signed Multiplication
KC-N3  Unary Negation Interpretation

KC-E1  Distribution
KC-E2  Like-Term Combination

KC-Q0  Equality Preservation
KC-Q1  Simple Factor Equation Solve

KC-F1  Binomial Product Structure
KC-F2  Monic Factor-Pair Reasoning

KC-Z1  Zero-Product Reasoning
```

No new KC is introduced by this revision.

---

# 3. Composite Task

```text
CT-QF1 — Solve Monic Quadratic by Factoring
```

Canonical stages:

```text
S1 FACTOR
→ KC-F2

S2 BRANCH
→ KC-Z1

S3 SOLVE_FACTOR_EQUATIONS
→ KC-Q1

S4 COMPLETE_SOLUTION_SET
→ composite completion check
```

---

# 4. Attempt Judgment — Final Candidate

V0.4 adds the missing partial-success state.

Canonical enum:

```text
VALID_EXPECTED
VALID_INCOMPLETE
VALID_SHORTCUT
INVALID_MATHEMATICS
AMBIGUOUS_INPUT
UNSUPPORTED_STEP_FORM
UNSUPPORTED_DOMAIN
```

These values are mutually semantically distinct.

---

# 5. VALID_EXPECTED

Definition:

> A supported, mathematically valid attempt that satisfies the current stage action and completion contract.

Allowed effects:

```text
positive stage evidence
positive KC evidence when reasoning is directly observed
stage progress
```

It does not automatically mean:

```text
durable mastery
```

---

# 6. VALID_INCOMPLETE

Definition:

> A supported and mathematically valid attempt that satisfies only part of the current stage completion contract.

Canonical example:

```text
Expected S2:

(x-2)(x+3)=0
↓
x-2=0 OR x+3=0

Learner submits only:

x-2=0
```

Judgment:

```text
VALID_INCOMPLETE
```

Not:

```text
INVALID_MATHEMATICS
```

Possible side effects:

```text
CompositeTaskFailure may be recorded
task-completion state may remain incomplete
positive evidence may be attached only to the directly observed valid sub-action
```

Forbidden side effects:

```text
no mathematical ErrorObservation claiming invalidity
no durable barrier identity from incompleteness alone
no false stage completion
no false recovery
```

---

# 7. VALID_SHORTCUT

Definition:

> A supported and mathematically correct later-stage/final result that bypasses one or more expected evidence-producing stages.

Example:

```text
x²+5x+6=0
↓
learner immediately gives:
{x=-2,x=-3}
```

Possible effect:

```text
CT-QF1 → COMPLETED_INDEPENDENTLY
```

But it does not produce positive evidence for bypassed:

```text
KC-F2
KC-Z1
KC-Q1
```

unless equivalent evidence exists elsewhere.

---

# 8. VALID_SHORTCUT — Prior Evidence Preservation

This section closes freeze-review R6.

Canonical invariant:

```text
CompositeTaskSuccess
≠
LearnerStateReset
```

A `VALID_SHORTCUT` may complete the current composite task.

It must not automatically:

```text
clear SUSPECTED_GAP
clear SUPPORTED_GAP
clear CONFIRMED_GAP
resolve a durable barrier
clear RETEST_DUE
clear RELAPSED
satisfy delayed retest
create TEMPORARILY_RECOVERED
create DURABLE_EVIDENCE
```

for bypassed KCs.

Exception:

```text
the attempt is explicitly registered
as the transfer/retest item
for that exact KC/barrier
```

and satisfies that item's evidence contract.

A correct final answer can therefore coexist with:

```text
CT-QF1 = COMPLETED_INDEPENDENTLY
KC-F2 = RETEST_DUE
```

This is intentional.

---

# 9. INVALID_MATHEMATICS

Definition:

> A supported and unambiguously parsed mathematical attempt whose mathematical content is invalid for the current mathematical context.

Only this ordinary attempt class may generate mathematical `ErrorObservation`s.

Examples:

```text
(-3)(-2) = -6
3(x+2) = 3x+2
A+B=0 → A=0 or B=0
```

---

# 10. AMBIGUOUS_INPUT

Definition:

> The input maps to more than one materially different supported interpretation.

Effects:

```text
no ErrorObservation
no durable barrier inference
no RepairEdge activation
request clarification or structured input
```

---

# 11. UNSUPPORTED_STEP_FORM

Definition:

> The notation may be mathematically meaningful but cannot be represented by Alpha `SupportedAttemptLanguage`.

Effects:

```text
no learner error
no ErrorObservation
no cognitive diagnosis
```

Parser limitation must never become learner deficit.

---

# 12. UNSUPPORTED_DOMAIN

Definition:

> The parsed mathematics requires concepts or problem families outside Alpha.

Effects:

```text
fail closed
no generic LLM tutor fallback
no cognitive diagnosis
```

---

# 13. Attempt Evidence Matrix

| Judgment | Mathematical error observation? | Composite failure? | Positive KC evidence? | Can complete task? |
|---|---:|---:|---:|---:|
| `VALID_EXPECTED` | No | No | Yes, if directly observed | Yes/Progress |
| `VALID_INCOMPLETE` | No | Yes, when applicable | Only observed sub-action | No |
| `VALID_SHORTCUT` | No | No | Not for bypassed KCs | Yes |
| `INVALID_MATHEMATICS` | Yes | Possibly separate | No | No |
| `AMBIGUOUS_INPUT` | No | No | No | No |
| `UNSUPPORTED_STEP_FORM` | No | No | No | No |
| `UNSUPPORTED_DOMAIN` | No | No | No | No |

Structured probe responses use `ProbeEvidence`, not this table, unless the probe itself is modeled as an ordinary attempt.

---

# 14. ErrorObservation Rule — Final Candidate

An ordinary mathematical `ErrorObservation` may only be emitted when:

```text
AttemptJudgment = INVALID_MATHEMATICS
AND
attempt form is supported
AND
parser interpretation is unambiguous
AND
the error class is deterministically identifiable
```

`VALID_INCOMPLETE` may emit:

```text
CompositeTaskFailure
```

but not an invalid-mathematics observation merely because work is incomplete.

`VALID_SHORTCUT` is not an error.

`AMBIGUOUS_INPUT` is not an error.

`UNSUPPORTED_STEP_FORM` is not an error.

Probe response classes update:

```text
ProbeEvidence
```

according to their own probe contract.

---

# 15. CompositeTaskFailure

Canonical Alpha family remains:

```text
CTF-QF1-01 ROOT_BRANCH_INCOMPLETE
```

It represents:

> Correct branch work exists, but the composite stage/task has not represented all required branches.

This is a task-completion event.

It is not a durable learner misconception.

---

# 16. S3 Branch Execution Model

This section closes R5.

CT-QF1 Stage S3 is represented as:

```text
BranchWorkSet
```

Schema:

```text
BranchWorkSet

composite_task_id
stage_id = S3
branch_items[]
completion_status
```

Each item:

```text
BranchWorkItem

branch_id
source_factor_ast
expected_equation_ast
expected_assignment_ast
assignment_status
observed_attempt_id?
```

Allowed `assignment_status`:

```text
PENDING
VALID
INVALID
UNSUPPORTED
```

---

# 17. S3 Branch Count

For Alpha CT-QF1:

```text
branch_count = 2
```

because repeated roots are excluded.

Example:

```text
(x-2)(x+3)=0
```

creates:

```text
branch A:
x-2=0
expected x=2

branch B:
x+3=0
expected x=-3
```

---

# 18. S3 Completion

S3 is complete when:

```text
all BranchWorkItems = VALID
```

or when:

```text
a supported VALID_SHORTCUT supplies the complete correct solution set
```

One correct branch:

```text
VALID_INCOMPLETE
```

for stage-completion semantics.

The correct branch may still contribute direct positive evidence for the observed KC-Q1 action.

The missing branch does not create a mathematical error.

---

# 19. S4 Completion

S4 validates the complete solution set.

Required:

```text
all expected unique roots represented
no unsupported extra root
solution set mathematically valid
```

Order is irrelevant.

For Alpha repeated roots are excluded, so:

```text
expected unique root count = 2
```

for CT-QF1 generated tasks.

---

# 20. Canonical SolutionSet Representation

This closes R9.

Internal AST:

```text
SolutionSet(
  assignments=[
    Assignment("x", Int(-2)),
    Assignment("x", Int(-3))
  ]
)
```

Assignment order is canonicalized for comparison.

---

# 21. Structured UI Representation

Primary Alpha representation:

```text
Root 1: [ input ]
Root 2: [ input ]
```

The UI may reorder values after validation.

The cognitive engine receives a normalized `SolutionSet`.

This structured route is authoritative for Alpha.

---

# 22. Optional Text Normalization

If free-text solution-set input is enabled by the client/parser, Alpha may normalize:

```text
{x=-2,x=-3}
x=-2, x=-3
x=-2 or x=-3
```

into the same `SolutionSet`.

If a parser implementation does not explicitly support one of these spellings:

```text
UNSUPPORTED_STEP_FORM
```

must be returned.

The system must not guess.

---

# 23. KC-Q0 Equality Preservation — Corrected Micro-Domain

V0.4 aligns the KC definition with its probe/intervention.

Definition:

> Apply the minimal additive equality-preservation principle needed by Alpha factor-equation reasoning.

Supported micro-forms:

```text
x + a = r
x - a = r
```

where:

```text
a,r are bounded integers inside the Alpha arithmetic profile
```

Supported transformation concept:

```text
L = R
→
L + k = R + k
```

for bounded additive `k`.

---

# 24. KC-Q0 Explicit Non-Scope

Still unsupported:

```text
ax+b=c as a general equation family
variables on both sides
multiplicative equality transformations
division-based solving
fractional transformations
systems
inequalities
```

Therefore v0.4 does not reopen general linear equations.

---

# 25. KC-Q1 Relationship to KC-Q0

KC-Q1 remains:

```text
Simple Factor Equation Solve
```

Canonical forms:

```text
x+a=0
x-a=0
```

Therefore:

```text
KC-Q1 is a task-specific use of KC-Q0
```

plus signed arithmetic / unary-negation behavior.

---

# 26. Probe Registry — v0.4

Primary probe templates:

```text
PR-N1-01 Signed Addition/Subtraction Check
PR-N2-01 Signed Multiplication Contrast
PR-N3-01 Unary Negation Contrast

PR-E1-01 Distribution Coverage
PR-E1-02 Negative Distribution Composition
PR-E2-01 Like-Term Membership

PR-Q0-01 Equality Preservation
PR-Q1-01 Additive Inverse Root Solve

PR-F1-01 Cross-Term Structure
PR-F2-01 Dual Constraint Selection

PR-Z1-01 Product vs Sum
```

Total:

```text
11 primary probe templates
```

---

# 27. PR-N1-01 — Signed Addition/Subtraction Check

```text
probe_id: PR-N1-01
target_kc: KC-N1
candidate_barriers: []
max_steps: 1
new_prerequisites: none
```

Prompt family:

```text
a + b
a - b
a + (-b)
```

with bounded small signed integers chosen so the item directly tests signed addition/subtraction rather than large arithmetic.

Example:

```text
-3 + 5 = ?
```

Truth:

```text
2
```

Response classes:

```text
R1 exact correct result
→ positive KC-N1 evidence

R2 exact sign-inverted but magnitude-consistent result
→ KC-N1 gap evidence
→ no durable barrier identity

R3 other interpretable integer
→ weaker KC-N1 gap evidence
→ no durable barrier identity

R4 non-interpretable
→ INCONCLUSIVE
```

No `BH-N1-*` durable barrier is introduced.

---

# 28. RepairEdge Wiring — N1

The informal phrase:

```text
signed-addition check fails
```

is removed.

`RE-F1-N1` required evidence becomes:

```text
PR-N1-01 produces KC-N1 gap evidence
OR
strong recent prior KC-N1 gap evidence exists
```

`RE-F2-N1` required evidence becomes:

```text
PR-N1-01 produces KC-N1 gap evidence
OR
strong recent prior KC-N1 gap evidence exists
```

Disqualifying example:

```text
recent independent KC-N1 transfer success
without contradictory newer evidence
```

---

# 29. RepairEdge Principle

Every active RepairEdge must name one of:

```text
canonical ProbeTemplate ID
deterministically observed supported attempt evidence
strong prior KC evidence with freshness semantics
```

No human-readable placeholder such as:

```text
"check addition"
```

may satisfy a frozen RepairEdge.

---

# 30. Intervention Template Completeness Rule

Every Alpha-active intervention is now specified through the following fields:

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

For neutral support use, the same template may be used only where the template is safe across all material remaining alternatives.

---

# 31. IT-N2-01 — Sign Contrast

```text
intervention_id: IT-N2-01
target_kc: KC-N2
eligible_barriers: [BH-N2-01]
allowed_barrier_states: [SUPPORTED, CONFIRMED]
student_action: compute two contrastive signed products
prompt_schema:
  (-a)*(+b)
  (-a)*(-b)
truth_rule: deterministic signed multiplication
success_condition: both products correct
failure_condition: either product incorrect
max_attempts: 1
next_action_on_success: RETURN_TO_ORIGINAL
next_action_on_failure: FALLBACK_OR_STOP
prohibited_scaffolds:
  - revealing original parent answer
  - mnemonic-only answer without learner calculation
```

Neutral-safe use:

```text
allowed when uncertainty is between KC-N2 weakness and local slip
without claiming BH-N2-01
```

---

# 32. IT-N3-01 — Unary Negation Grouping

```text
intervention_id: IT-N3-01
target_kc: KC-N3
eligible_barriers: [BH-N3-01]
allowed_barrier_states: [SUPPORTED, CONFIRMED]
student_action: evaluate the object under unary negation
prompt_schema:
  Neg(Neg(Int(a)))
truth_rule: -(-a)=a
success_condition: learner returns +a
failure_condition: sign remains negative or response uninterpretable
max_attempts: 1
next_action_on_success: RETURN_TO_ORIGINAL
next_action_on_failure: FALLBACK_OR_STOP
prohibited_scaffolds:
  - supplying the final original equation result
  - treating ordinary subtraction as unary negation
```

---

# 33. IT-E1-01 — Every Term Gets the Factor

```text
intervention_id: IT-E1-01
target_kc: KC-E1
eligible_barriers: [BH-E1-01]
allowed_barrier_states: [SUPPORTED, CONFIRMED]
student_action: fill the missing distributed product
prompt_schema:
  a(x+b) = ax + a*__
truth_rule: both additive terms receive the outside factor
success_condition: missing term structurally correct
failure_condition: outside factor omitted from second term
max_attempts: 1
next_action_on_success: RETURN_TO_ORIGINAL
next_action_on_failure: FALLBACK_OR_STOP
prohibited_scaffolds:
  - pre-filling both distributed terms
```

Neutral-safe use:

```text
allowed as NeutralSupport when distribution failure is known
but specific barrier remains uncertain
```

---

# 34. IT-E1-02 — Sign Composition

```text
intervention_id: IT-E1-02
target_kc: KC-E1
eligible_barriers: [BH-E1-02]
allowed_barrier_states: [SUPPORTED, CONFIRMED]
student_action: compute each distributed product separately
prompt_schema:
  -a(x-b)
  first: -a*x
  second: -a*(-b)
truth_rule: deterministic multiplication + distribution
success_condition: both products have correct sign and magnitude
failure_condition: sign composition remains wrong
max_attempts: 1
next_action_on_success: RETURN_TO_ORIGINAL
next_action_on_failure: use legal guarded RepairEdge or clean stop
prohibited_scaffolds:
  - declaring BH-E1-02 confirmed when N2/N3 alternatives remain
```

---

# 35. IT-E2-01 — Like-Term Sort

```text
intervention_id: IT-E2-01
target_kc: KC-E2
eligible_barriers: [BH-E2-01]
allowed_barrier_states: [SUPPORTED, CONFIRMED]
student_action: group terms by variable structure
prompt_schema:
  [ax, b, cx, d]
truth_rule: only identical variable/power structures are combinable
success_condition: x-terms grouped together and constants grouped together
failure_condition: unlike structures grouped
max_attempts: 1
next_action_on_success: RETURN_TO_ORIGINAL
next_action_on_failure: FALLBACK_OR_STOP
prohibited_scaffolds:
  - directly presenting combined final expression
```

---

# 36. IT-Q0-01 — Equality Preservation Mirror

```text
intervention_id: IT-Q0-01
target_kc: KC-Q0
eligible_barriers: [BH-Q0-01]
allowed_barrier_states: [SUPPORTED, CONFIRMED]
student_action: choose/apply the same additive operation to both sides
prompt_schema:
  x+a=r
  left: subtract a
  right: learner chooses operation/result
truth_rule: L=R → L+k=R+k
success_condition: same additive operation preserves equality
failure_condition: one-sided or arbitrary sign transformation
max_attempts: 1
next_action_on_success: RETURN_TO_ORIGINAL
next_action_on_failure: CLEAN_STOP_OR_FALLBACK
prohibited_scaffolds:
  - variables on both sides
  - multiplication/division transformation lesson
  - generic linear-equation expansion
```

---

# 37. IT-Q1-01 — Additive Inverse Reconstruction

```text
intervention_id: IT-Q1-01
target_kc: KC-Q1
eligible_barriers: [BH-Q1-01]
allowed_barrier_states: [SUPPORTED, CONFIRMED]
student_action: solve one x±a=0 factor equation
prompt_schema:
  x+a=0 or x-a=0
truth_rule: TI-02 Solution-Set Preservation
success_condition: correct signed assignment for x
failure_condition: wrong root sign or unsupported response
max_attempts: 1
next_action_on_success: RETURN_TO_ORIGINAL
next_action_on_failure:
  - legal RE-Q1-Q0 / RE-Q1-N3 / RE-Q1-N1 if guards satisfied
  - otherwise clean stop
prohibited_scaffolds:
  - general equation-solving lesson
```

---

# 38. IT-F1-01 — Four Product Terms

```text
intervention_id: IT-F1-01
target_kc: KC-F1
eligible_barriers: [BH-F1-01]
allowed_barrier_states: [SUPPORTED, CONFIRMED]
student_action: produce/complete four multiplicative contributions
prompt_schema:
  (x+m)(x+n)
  x*x
  x*n
  m*x
  m*n
truth_rule: TI-01 Expression Equivalence
success_condition: all four contributions represented correctly
failure_condition: cross term still omitted or malformed
max_attempts: 1
next_action_on_success: RETURN_TO_ORIGINAL
next_action_on_failure:
  - legal F1 RepairEdge if guarded
  - otherwise clean stop
prohibited_scaffolds:
  - directly supplying expanded final trinomial
```

---

# 39. IT-F2-01 — Two-Constraint Factor Table

```text
intervention_id: IT-F2-01
target_kc: KC-F2
eligible_barriers: [BH-F2-01]
allowed_barrier_states: [SUPPORTED, CONFIRMED]
student_action: choose/check pair against sum and product columns
prompt_schema:
  pair | sum | product
truth_rule:
  m+n=b
  mn=c
success_condition: pair satisfies both constraints
failure_condition: only one/no constraint satisfied
max_attempts: 1
next_action_on_success: RETURN_TO_ORIGINAL
next_action_on_failure:
  - legal N1/N2/F1 RepairEdge if guarded
  - otherwise clean stop
prohibited_scaffolds:
  - supplying the correct factor pair before learner choice
```

---

# 40. IT-Z1-01 — Product Counterexample

```text
intervention_id: IT-Z1-01
target_kc: KC-Z1
eligible_barriers: [BH-Z1-01]
allowed_barrier_states: [SUPPORTED, CONFIRMED]
student_action: distinguish zero-sum from zero-product implication
prompt_schema:
  compare A+B=0 and A*B=0
truth_rule: zero-product property
success_condition: learner identifies product relation as branch-enabling case
failure_condition: learner applies branch rule to sum
max_attempts: 1
next_action_on_success: RETURN_TO_ORIGINAL
next_action_on_failure: CLEAN_STOP_OR_FALLBACK
prohibited_scaffolds:
  - teaching unrelated factoring strategy
```

---

# 41. IT-QF1-01 — Branch Completion UI

```text
intervention_id: IT-QF1-01
target_task: CT-QF1
eligible_failures: [CTF-QF1-01]
allowed_states: [task failure only]
student_action: fill the unresolved branch/root slot
prompt_schema:
  preserve completed branch
  expose unresolved branch slot
truth_rule: complete solution set for current factored equation
success_condition: second required branch/root resolved
failure_condition: branch remains empty/invalid
max_attempts: 1
next_action_on_success: resume composite stage
next_action_on_failure: clean stop or save incomplete work
prohibited_scaffolds:
  - auto-filling missing branch
  - turning one omission into durable misconception
```

This template is task-completion support, not barrier remediation.

---

# 42. Intervention-State Safety

If barrier state is only:

```text
SUSPECTED
INCONCLUSIVE
```

a barrier-specific intervention above may only be used through `NeutralSupportAction` when:

```text
the intervention is safe across every remaining material alternative
```

and:

```text
barrier_state_side_effect = NONE
```

Otherwise:

```text
do not use that intervention
```

---

# 43. Probe/Intervention Evidence Separation

Canonical invariant:

```text
ProbeEvidence
≠ InterventionSuccess
```

A successful intervention means the learner completed the repair action.

It does not retroactively prove the original barrier.

Barrier confirmation remains evidence-driven.

---

# 44. PR-Q0 / KC-Q0 Alignment

`PR-Q0-01` remains legal because KC-Q0 now explicitly includes:

```text
x+a=r
x-a=r
```

micro-forms.

`IT-Q0-01` uses the same micro-domain.

No scope contradiction remains.

---

# 45. N1 RepairEdge Contracts — Final Candidate

## RE-F1-N1

```text
from: KC-F1
to: KC-N1

eligible:
correct cross-term structure
incorrect signed sum of middle coefficients

required:
PR-N1-01 → KC-N1 gap evidence
OR strong recent prior KC-N1 gap evidence

disqualifying:
recent independent KC-N1 transfer success
without newer contradictory evidence

fallback:
NeutralSupportAction on KC-F1
```

## RE-F2-N1

```text
from: KC-F2
to: KC-N1

eligible:
EO-FACTOR-PAIR-SUM-MISMATCH
AND product constraint correct

required:
PR-N1-01 → KC-N1 gap evidence
OR strong recent prior KC-N1 gap evidence

disqualifying:
recent independent KC-N1 transfer success
without newer contradictory evidence

fallback:
IT-F2-01
```

---

# 46. One-Probe Budget Compatibility

A RepairEdge may not require multiple new probes in one path when the frozen Experience probe budget forbids them.

Therefore:

```text
if required evidence cannot be established
within the current probe budget
→ edge remains closed
```

Allowed fallback:

```text
NeutralSupportAction
continue
abstain
clean stop
```

The graph must not force diagnostic certainty.

---

# 47. Durable Barrier Registry

Unchanged:

```text
BH-N2-01 Same-sign multiplication gives negative
BH-N3-01 Unary negation preserves inner sign

BH-E1-01 Partial distribution
BH-E1-02 Negative distribution composition failure
BH-E2-01 Unlike terms combined

BH-Q0-01 One-sided equality transformation
BH-Q1-01 Additive inverse / root-sign failure

BH-F1-01 Binomial cross-term omission
BH-F2-01 Single-Constraint Factor Selection

BH-Z1-01 Zero-product overgeneralized to a sum
```

No N1 durable barrier is added.

---

# 48. Composite Failure Registry

Unchanged:

```text
CTF-QF1-01 ROOT_BRANCH_INCOMPLETE
```

May be produced by:

```text
VALID_INCOMPLETE
```

when branch-completeness semantics apply.

It does not update durable barrier memory.

---

# 49. Alpha Coverage Budget — v0.4

```text
10 Repairable KCs
1 Composite Task
2 Truth Invariants
2 Boundary Assumptions

10 Durable Barrier Families
1 CompositeTaskFailure family

11 fully specified primary Probe Templates
11 fully specified Intervention Templates

13 Problem Families
2 Transfer Levels
3 User-Facing Domain Goals

1 SupportedAttemptLanguage
7 AttemptJudgment classes
1 S3 BranchWorkSet contract
```

---

# 50. Problem Families

Unchanged:

```text
PF-N1  signed add/subtract
PF-N2  signed multiplication
PF-N3  unary negation

PF-E1  positive distribution
PF-E2  negative distribution
PF-E3  like-term combination

PF-Q0  equality-preservation micro-task
PF-Q1  simple factor equation

PF-F1  binomial expansion
PF-F2  factor-pair selection
PF-F3  full monic trinomial factoring

PF-Z1  zero-product branch

PF-QF1 full monic quadratic-by-factoring task
```

---

# 51. User-Facing Goals

Unchanged:

```text
GOAL-01 Build the foundations for factoring
GOAL-02 Practice factoring
GOAL-03 Solve quadratic equations by factoring
```

No curriculum browser is introduced.

---

# 52. Domain Boundary

Still unsupported:

```text
repeated roots
zero-root special cases
non-monic quadratics
general linear equations
fractions
common-factor extraction
arbitrary quadratic normalization
quadratic formula
completing square
irrational/complex roots
word problems
systems
inequalities
geometry
trigonometry
calculus
```

---

# 53. Canonical Vertical Proof — Partial Branch

```text
PROBLEM
x²+x-6=0

FACTOR
(x-2)(x+3)=0

S2 expected:
x-2=0 OR x+3=0

LEARNER:
x-2=0

ATTEMPT:
supported
mathematically valid
stage incomplete

JUDGMENT:
VALID_INCOMPLETE

EVIDENCE:
positive evidence for represented branch action

COMPOSITE FAILURE:
CTF-QF1-01 ROOT_BRANCH_INCOMPLETE

DURABLE BARRIER:
NONE CREATED
```

---

# 54. Canonical Vertical Proof — N1 Repair Route

```text
ACTIVE:
KC-F2

OBSERVATION:
factor pair product correct
sum mismatch

CANDIDATES:
BH-F2-01 ignored SUM
KC-N1 gap
LOCAL_SLIP

PR-F2-01:
determines constraint-selection evidence

IF arithmetic explanation remains material:
PR-N1-01
within probe budget

PR-N1-01 fails:
RE-F2-N1 becomes eligible

REPAIR:
bounded KC-N1 intervention/support

RETURN:
original factor-pair task
```

If probe budget cannot support the extra discriminator:

```text
do not open RE-F2-N1
use safe F2 support or abstain
```

---

# 55. Canonical Vertical Proof — Shortcut With Prior Debt

Existing state:

```text
KC-F2 = RETEST_DUE
```

New task:

```text
x²+5x+6=0
```

Learner directly submits:

```text
{x=-2,x=-3}
```

Judgment:

```text
VALID_SHORTCUT
```

Task:

```text
CT-QF1 = COMPLETED_INDEPENDENTLY
```

KC:

```text
KC-F2 remains RETEST_DUE
```

unless this exact task was explicitly selected as the KC-F2 retest under its evidence contract.

No evidence laundering occurs.

---

# 56. Hard/Freeze Review Closure Matrix

| Requirement | v0.4 Status |
|---|---|
| R1 `VALID_INCOMPLETE` | **CLOSED BY CONTRACT** |
| R2 `PR-N1-01` + N1 edge wiring | **CLOSED BY CONTRACT** |
| R3 KC-Q0 micro-domain alignment | **CLOSED** |
| R4 active intervention templates | **CLOSED BY EXPLICIT TEMPLATES** |
| R5 S3 branch semantics | **CLOSED — BranchWorkSet/Item** |
| R6 shortcut prior-evidence safety | **CLOSED BY INVARIANT** |
| R7 probe count | **CLOSED — 11** |
| R8 ErrorObservation wording | **CLOSED** |
| R9 SolutionSet representation | **CLOSED** |

---

# 57. Implementation Boundary

Because v0.4 is not yet frozen, implementation may begin only as a **foundation layer** whose APIs directly encode these candidate contracts.

Allowed now:

```text
enums
typed models
registries
pure validation rules
invariant tests
attempt-judgment models
BranchWorkItem models
RepairEdge metadata
probe/intervention metadata
```

Not yet authorized from Domain v0.4:

```text
broad endpoint replacement
mobile experience rewrite
legacy learner-state migration
production rollout
deletion of existing systems
automatic replacement of old misconception detector
```

This permits implementation progress without pretending the freeze review has already passed.

---

# 58. Narrow Freeze Recheck Questions

The next review must only check:

```text
1. Is VALID_INCOMPLETE distinct and side-effect safe?
2. Is every N1 RepairEdge backed by PR-N1-01?
3. Does KC-Q0 now match PR-Q0-01 and IT-Q0-01?
4. Are all 11 interventions mechanically specified?
5. Are S3 branch semantics complete?
6. Can VALID_SHORTCUT ever erase prior evidence?
7. Do metadata counts match actual registries?
8. Can non-invalid attempt classes accidentally emit mathematical ErrorObservation?
9. Is SolutionSet representation implementable without guessing?
```

No new topic review.

---

# 59. Status

```text
V1 COGNITIVE DOMAIN CONTRACT
=
v0.4 FREEZE CORRECTION

R1-R9
=
CLOSED BY DESIGN CLAIM

EXPERIENCE
=
FROZEN

DOMAIN FREEZE
=
PENDING NARROW RECHECK

FOUNDATION IMPLEMENTATION
=
AUTHORIZED ON ISOLATED BRANCH

NEXT DOCUMENT REVIEW
=
NARROW DOMAIN FREEZE RECHECK
```

**NOT YET FROZEN.**
