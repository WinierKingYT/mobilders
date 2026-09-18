# MOBILDERS — V1 COGNITIVE DOMAIN IMPLEMENTATION ERRATUM

**Version:** 0.1  
**Target:** `MOBILDERS_V1_COGNITIVE_DOMAIN_CONTRACT_v0.4.md`  
**Type:** Narrow Frozen-Spec Implementation Erratum  
**Status:** `ACCEPTED / FROZEN ERRATUM`  
**Scope Expansion:** `NONE`  
**Implementation Authorization:** `FOUNDATION KERNEL AUTHORIZED`

---

# 0. Why This Erratum Exists

Implementation of the frozen v0.4 domain exposed one closure defect that the document review did not catch.

The frozen graph contains three legal repair routes into:

```text
KC-N1 — Signed Addition / Subtraction
```

Specifically:

```text
RE-F1-N1
RE-F2-N1
RE-Q1-N1
```

`PR-N1-01` can establish KC-N1 gap evidence, and the repair graph can legally descend into KC-N1.

However, v0.4 contains no executable KC-N1 intervention template.

Therefore the graph could diagnose and route into KC-N1 but could not complete the promised repair.

This violates the frozen support rule:

> A RepairableKC must have a bounded intervention path.

The freeze cannot silently preserve this contradiction.

---

# 1. Severity

```text
BLOCKER = 1 implementation-closure defect
```

This is **not** a new product, curriculum, KC, barrier, problem family, goal, or experience requirement.

It is a missing executable contract for an already-frozen repair target.

---

# 2. Correction E1 — Add IT-N1-01

Add:

# `IT-N1-01 — Signed Sum Decomposition`

Target:

```text
KC-N1
```

Durable barrier identity:

```text
NONE REQUIRED
```

This is intentional. KC-N1 may have strong gap evidence without a sufficiently bounded durable misconception identity.

Allowed KC states:

```text
SUPPORTED_GAP
CONFIRMED_GAP
RELAPSED
```

Student action:

```text
complete one structured signed-sum decomposition
```

Prompt behavior:

```text
normalize subtraction into signed addition when needed

same-sign case
→ preserve sign and combine magnitudes

opposite-sign case
→ expose zero-pair cancellation / remaining signed magnitude
```

Truth rule:

```text
deterministic signed integer addition/subtraction
```

Success:

```text
structured decomposition is valid
AND
final signed result is correct
```

Failure:

```text
signed result remains invalid
OR
response is non-interpretable
```

Maximum attempts:

```text
1
```

Success action:

```text
RETURN_TO_ORIGINAL
```

Prohibited:

```text
revealing the parent-task answer
inventing a durable KC-N1 misconception label
opening a second major repair detour
```

---

# 3. Correction E2 — InterventionTemplate Supports Barrierless KC Repair

The intervention schema previously encoded:

```text
allowed_barrier_states
```

but no equivalent contract for a KC-level intervention when no durable barrier is asserted.

Add:

```text
allowed_kc_states[]
```

This field is used for interventions such as `IT-N1-01` where:

```text
KC gap evidence is sufficient for bounded repair
BUT
no durable misconception identity is claimed
```

Canonical invariant:

```text
Repairable KC
≠ mandatory durable barrier identity
```

This protects diagnostic integrity.

---

# 4. Correction E3 — Wire Existing N1 RepairEdges

The following routes now enter `IT-N1-01` when their evidence guard passes:

```text
RE-F1-N1 → IT-N1-01
RE-F2-N1 → IT-N1-01
RE-Q1-N1 → IT-N1-01
```

The repair evaluator must still enforce:

```text
eligible ErrorObservation
+
PR-N1-01 GAP evidence
OR explicitly fresh strong KC-N1 gap evidence where that edge permits it
+
no disqualifying recent transfer evidence
```

Routing remains evidence-gated.

---

# 5. Metadata Correction

Frozen v0.4 states:

```text
11 Intervention Templates
```

Effective frozen authority after this erratum is:

```text
12 Intervention Templates
```

No other coverage count changes.

---

# 6. What Does Not Change

The following remain unchanged:

```text
10 Repairable KCs
1 Composite Task
2 Truth Invariants
2 Boundary Assumptions
10 Durable Barrier Families
1 CompositeTaskFailure family
11 Probe Templates
13 Problem Families
2 Transfer Levels
3 User-Facing Goals
7 AttemptJudgment classes
```

No new curriculum surface is authorized.

---

# 7. Freeze Authority

From this erratum onward, the frozen Cognitive Domain authority is:

```text
MOBILDERS_V1_COGNITIVE_DOMAIN_CONTRACT_v0.4.md
+
MOBILDERS_V1_COGNITIVE_DOMAIN_IMPLEMENTATION_ERRATUM_v0.1.md
```

If the two conflict only on:

```text
KC-N1 intervention closure
allowed_kc_states
intervention count
N1 RepairEdge intervention target
```

this erratum wins.

All other v0.4 contracts remain frozen.

---

# 8. Verification Requirement

Executable registry validation must fail if:

```text
an active RepairEdge has no intervention target
an N1 RepairEdge does not use PR-N1-01
an N1 RepairEdge does not route to IT-N1-01
an intervention references an unsupported registry ID
```

This requirement is implemented in Focus Kernel Round 03.

---

# 9. Final Decision

```text
ERRATUM = ACCEPTED
SCOPE EXPANSION = NONE
DOMAIN FREEZE = PRESERVED WITH ERRATUM
IMPLEMENTATION = CONTINUE
```
