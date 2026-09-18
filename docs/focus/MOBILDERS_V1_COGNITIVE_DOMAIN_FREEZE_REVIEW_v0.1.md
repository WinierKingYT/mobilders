# MOBILDERS — V1 COGNITIVE DOMAIN FREEZE REVIEW

**Version:** 0.1  
**Review Target:** `MOBILDERS_V1_COGNITIVE_DOMAIN_CONTRACT_v0.3.md`  
**Review Type:** Adversarial Domain Freeze Review  
**Verdict:** `FIX-FIRST`  
**Freeze Authorization:** `DENIED`  
**Implementation Authorization:** `DENIED`  
**Overall Score:** **9.1 / 10**

---

# 0. Freeze Standard

This review asks whether v0.3 can become the authoritative frozen Alpha cognitive-domain specification without forcing implementers to invent missing semantic behavior.

Freeze requires:

```text
0 blocker
0 unresolved major semantic contradiction
closed attempt-language semantics
closed repair-routing evidence
closed probe/intervention authority
consistent task-completion semantics
```

# 1. Executive Verdict

V0.3 successfully closes the two blockers from the prior hard review:

```text
SupportedAttemptLanguage exists
KC-Q0 closes the equality diagnostic hole
```

The core ontology is strong enough to preserve.

However, the freeze review found:

```text
BLOCKER = 2
MAJOR = 4
MINOR = 3
```

No redesign is needed. The remaining work is semantic closure.

# 2. BLOCKER B1 — Incomplete-but-Mathematically-Valid Work Has No Attempt Judgment

Current judgments:

```text
VALID_EXPECTED
VALID_SHORTCUT
INVALID_MATHEMATICS
AMBIGUOUS_INPUT
UNSUPPORTED_STEP_FORM
UNSUPPORTED_DOMAIN
```

But the domain also models:

```text
CTF-QF1-01 ROOT_BRANCH_INCOMPLETE
```

A learner may submit one mathematically valid branch while omitting the other. That attempt is neither mathematically invalid, complete, nor a shortcut.

Required correction:

```text
VALID_INCOMPLETE
```

Definition:

> A supported and mathematically valid attempt that satisfies only part of the current stage completion contract.

Semantics:

```text
may create CompositeTaskFailure
must not create mathematical ErrorObservation
must not create durable barrier by itself
```

# 3. BLOCKER B2 — Some RepairEdges Depend on Undefined Evidence Producers

`RE-F1-N1` and `RE-F2-N1` require:

```text
signed-addition check fails
```

but there is no canonical `PR-N1-01`.

Required correction:

```text
PR-N1-01 — Signed Addition/Subtraction Check
```

It may update only KC-N1 evidence; no durable N1 barrier is required.

Every N1 RepairEdge must reference this exact evidence producer.

# 4. MAJOR M1 — KC-Q0 Scope Contradicts Its Own Probe and Intervention

KC-Q0 declares supported forms:

```text
x+a=0
x-a=0
```

but PR-Q0-01 uses:

```text
x+4=7
```

and IT-Q0-01 uses:

```text
x+a=r
```

Required correction:

```text
KC-Q0 supported micro-domain:
x+a=r
x-a=r
```

for bounded integers, while general linear equations remain unsupported.

# 5. MAJOR M2 — Active Intervention Templates Are Not Fully Instantiated

The completeness gate requires fully instantiated active interventions, but only IT-Q0-01 is fully specified in v0.3.

Every active Alpha intervention must define:

```text
eligible barriers
allowed barrier states
student action
prompt schema
truth rule
success condition
failure condition
max attempts
next action on success
next action on failure
prohibited scaffolds
```

# 6. MAJOR M3 — S3 Two-Branch Execution Semantics Are Under-Specified

CT-QF1 S3 has two factor branches but does not define whether solving happens as one stage with two assignments or two branch-local executions.

Recommended:

```text
S3 contains BranchWorkItem[]
branch_count = 2
```

Each item has:

```text
branch_id
source_factor
expected_equation
assignment_status
```

One solved branch becomes `VALID_INCOMPLETE`; S3 completes only when both are resolved or a valid complete shortcut is supplied.

# 7. MAJOR M4 — VALID_SHORTCUT Needs Existing-Evidence Safety

A correct shortcut must not erase prior learning evidence.

Add:

```text
VALID_SHORTCUT may complete CompositeTaskState
but must not:
clear KC gaps
resolve barriers
satisfy retests
create durable recovery
```

unless it is explicitly the declared transfer/retest for that KC.

# 8. MINOR N1 — Probe Count Metadata

v0.3 says 9 fully specified probes, but contains 10. After adding PR-N1-01 the correct count becomes 11.

# 9. MINOR N2 — Remove "valid-but-wrong"

Use explicit semantics:

```text
INVALID_MATHEMATICS → mathematical ErrorObservation allowed
VALID_INCOMPLETE → CompositeTaskFailure allowed
VALID_EXPECTED → positive task evidence
VALID_SHORTCUT → shortcut semantics
```

# 10. MINOR N3 — SolutionSet Surface Representation

Name at least one canonical structured representation:

```text
two root slots
```

and, only if free-text normalization is supported:

```text
{x=-2,x=-3}
x=-2, x=-3
```

# 11. What Passed and Should Not Be Reopened

```text
Domain focus
Generation vs cognition separation
x²-9 support
KC-N3 narrowing
KC-Q0 promotion
BH-F2-01 barrier compression
ROOT_BRANCH_INCOMPLETE as CompositeTaskFailure
NeutralSupportAction restrictions
Barrier-state intervention authority
Unsupported representation safety
```

# 12. Required v0.4 Scope

```text
R1 add VALID_INCOMPLETE
R2 add PR-N1-01 and wire N1 RepairEdges
R3 align KC-Q0 micro-domain
R4 fully instantiate active intervention templates
R5 specify S3 BranchWorkItem semantics
R6 preserve prior evidence under VALID_SHORTCUT
R7 correct probe-count metadata
R8 clean ErrorObservation wording
R9 define canonical SolutionSet representation
```

No new KC, barrier family, curriculum area or user goal.

# 13. Freeze Scorecard

| Dimension | Score |
|---|---:|
| Domain focus | 9.7 |
| Ontology separation | 9.7 |
| Scope discipline | 9.7 |
| Attempt AST | 9.4 |
| Attempt judgment completeness | 8.1 |
| Truth/diagnosis separation | 9.7 |
| Equality closure | 9.2 |
| Repair routing | 8.9 |
| Barrier boundedness | 9.5 |
| Probe semantics | 9.3 |
| Intervention closure | 8.1 |
| Composite-task semantics | 8.7 |
| Unsupported-boundary safety | 9.7 |
| Implementation readiness | 8.8 |
| **Overall** | **9.1 / 10** |

# 14. Severity Summary

```text
BLOCKER = 2

B1 no judgment for mathematically valid but incomplete work
B2 N1 RepairEdges depend on undefined signed-addition evidence producer
```

```text
MAJOR = 4

M1 KC-Q0 scope contradicts own probe/intervention
M2 intervention templates not fully instantiated
M3 S3 two-branch execution under-specified
M4 VALID_SHORTCUT prior-evidence behavior missing
```

```text
MINOR = 3

N1 probe-count metadata incorrect
N2 valid-but-wrong wording ambiguous
N3 SolutionSet representation not explicit
```

# 15. Final Verdict

```text
MOBILDERS_V1_COGNITIVE_DOMAIN_CONTRACT_v0.3
=
FIX-FIRST
```

The correct next artifact is:

```text
MOBILDERS_V1_COGNITIVE_DOMAIN_CONTRACT_v0.4
— Freeze Correction
```

Then:

```text
NARROW DOMAIN FREEZE RECHECK
```

If R1–R9 are clean:

```text
V1 COGNITIVE DOMAIN CONTRACT
=
SHIP / FROZEN
```
