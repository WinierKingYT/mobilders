# MOBILDERS V1 COGNITIVE DOMAIN CONTRACT: CT-LIN1 & CT-INEQ1
## Version: v0.1 | Status: Draft / Canonical Focus Extension
## Authority: Focus Domain Mathematical & Pedagogical Architecture

---

### 1. Scope and Mission
This document formally defines the cognitive domain contracts for:
1. **`CT-LIN1`**: Birinci Dereceden Doğrusal Denklemler ve Terazi Modeli ($ax + b = c$).
2. **`CT-INEQ1`**: Birinci Dereceden Doğrusal Eşitsizlikler ve Yön Değiştirme Sezgisi ($ax + b \le c$).

These topics extend the Focus Kernel cognitive architecture beyond `CT-QF1`, serving as both foundational prerequisites and standalone mastery modules in the PLE curriculum (MASTER_ROADMAP.md Faz 0 / Hedef 2 & Hedef 3).

---

### 2. Theoretical Pedagogical Principles
1. **Server-Only Mathematical & Diagnostic Authority**: Client applications only send user inputs (strings, coefficients, selections). The server independently evaluates truth, diagnoses misconceptions, evaluates probes, and controls stage progression.
2. **Bruner E-I-S Model (Concreteness Fading)**:
   - *Enactive*: Balance scale intuition (adding/subtracting weights from both pans).
   - *Iconic*: Visual box equation models ($a \cdot [x] + b = c$).
   - *Symbolic*: Pure algebraic transformation ($ax + b = c \implies ax = c - b \implies x = \frac{c - b}{a}$).
3. **Closed Pedagogical Repair Loop**:
   $$\text{Error Observation (EO)} \longrightarrow \text{Diagnostic Probe (PR)} \longrightarrow \text{Socratic Intervention (IT)} \longrightarrow \text{Original Self-Correction} \longrightarrow \text{Transfer Task (TT)}$$
4. **Target Root Misconceptions**:
   - `BUG-FOUND-15`: Tek Taraflı Terazi Hatası ($ax + b = c \implies ax = c + b$ or $ax = c$).
   - `BUG-FOUND-07`: Katsayıyı Çıkarma Sanma ($ax = d \implies x = d - a$).
   - `BUG-FOUND-08`: Elma ile Armudu Toplama ($ax + b = (a+b)x$).
   - `BUG-FOUND-14`: Eşitsizlikte Yön Unutma ($-ax \le d \implies x \le -d/a$ without direction flip).

---

### 3. Knowledge Component (KC) Catalog

| KC ID | Name | Canonical Definition | Associated Barriers |
| :--- | :--- | :--- | :--- |
| `KC-Q0` | Equality Additive Transform | Applying the same additive delta to both sides of an equality preserves truth ($L = R \implies L + \Delta = R + \Delta$). | `BH-Q0-01` |
| `KC-L1` | Multiplicative Balance & Coefficient Isolation | Isolating $x$ from $ax = d$ requires dividing both sides by the non-zero coefficient $a$ ($x = d/a$), NOT subtracting $a$. | `BH-L1-01` |
| `KC-L2` | Linear Solution Verification | Substituting $x^*$ back into $a(x^*) + b = c$ verifies whether the equality holds. | - |
| `KC-I1` | Inequality Negative Division Inversion | Dividing or multiplying an inequality by a negative number reverses the inequality direction ($A \le B \land k < 0 \implies kA \ge kB$). | `BH-I1-01` |
| `KC-N1` | Signed Addition / Subtraction | Bounded integer addition/subtraction. | `BH-N1-01` |
| `KC-N2` | Signed Multiplication / Division | Sign rules for product and quotient: $(-) \cdot (-) = (+)$, $(-) / (+) = (-)$. | `BH-N2-01` |

---

### 4. Topic 1: `CT-LIN1` (Linear Equations $ax + b = c$)

#### 4.1 Task Context Schema (`CTLIN1TaskContext`)
- Coefficients: $a, b, c \in \mathbb{Z}$ with $a \neq 0, a \neq 1$, and $(c - b) \pmod a == 0$.
- Expected intermediate equation: $ax = d$ where $d = c - b$.
- Expected solution: $x^* = d / a$.
- Allowed absolute bounds: $|a| \le 12, |b| \le 50, |c| \le 50$.

#### 4.2 Stage State Machine
- `S1_ISOLATE_TERM`:
  - Learner submits rewritten equation (e.g. `3x = 9` for `3x + 6 = 15`).
  - Truth Adapter checks `check_linear_term_isolation(a, b, c, observed_ax, observed_rhs)`.
  - If valid $\rightarrow$ advance to `S2_ISOLATE_VARIABLE`.
  - If invalid:
    - If `observed_rhs == c + b` or `observed_rhs == c` $\rightarrow$ produce `EO-EQUALITY-ONE-SIDE-CHANGED` (`BUG-FOUND-15`).
    - If unlike terms combined $\rightarrow$ produce `EO-UNLIKE-TERMS-COMBINED` (`BUG-FOUND-08`).
- `S2_ISOLATE_VARIABLE`:
  - Learner submits root assignment (e.g. `x = 3`).
  - Truth Adapter checks `check_linear_coefficient_division(a, d, observed_x)`.
  - If valid $\rightarrow$ advance to `S3_VERIFY_SOLUTION`.
  - If invalid:
    - If `observed_x == d - a` $\rightarrow$ produce `EO-COEFFICIENT-SUBTRACTED` (`BUG-FOUND-07`).
    - If `observed_x == -expected_x` $\rightarrow$ produce `EO-SIGN-WRONG`.
- `S3_VERIFY_SOLUTION`:
  - Learner verifies equation truth $a(x^*) + b = c \implies c = c$.
  - Upon confirmation $\rightarrow$ transition to `COMPLETED_INDEPENDENTLY` or `COMPLETED_WITH_SUPPORT`.

---

### 5. Topic 2: `CT-INEQ1` (Linear Inequalities $ax + b \le c$)

#### 5.1 Task Context Schema (`CTINEQ1TaskContext`)
- Coefficients: $a, b, c \in \mathbb{Z}, a \neq 0, (c - b) \pmod a == 0$.
- Comparator: $\le, <, \ge, >$.
- Target solution: If $a < 0$, the comparator is inverted ($\le \to \ge$, $< \to >$, etc.).

#### 5.2 Stage State Machine
- `S1_ISOLATE_TERM`: $ax \le c - b$.
- `S2_DIRECTION_AWARE_DIVISION`:
  - If $a < 0$ and observed comparator is not inverted $\rightarrow$ produce `EO-INEQUALITY-DIRECTION-NOT-REVERSED` (`BUG-FOUND-14`).
  - If inverted and value is correct $\rightarrow$ advance to `S3_VERIFY_SOLUTION`.
- `S3_VERIFY_SOLUTION`: Test point verification.

---

### 6. Diagnostic Probes & Socratic Interventions

#### 6.1 Probes
- `PR-L1-01`:
  - Target KC: `KC-L1`
  - Candidate Barrier: `BH-L1-01`
  - Prompt: "In $ax = d$, what algebraic operation isolates $x$? [Subtract $a$, Divide by $a$, Add $a$]"
  - Responses: `DIVIDE` (POSITIVE), `SUBTRACT` (BARRIER_SUPPORT), `OTHER` (INCONCLUSIVE).
- `PR-I1-01`:
  - Target KC: `KC-I1`
  - Candidate Barrier: `BH-I1-01`
  - Prompt: "2 < 5. When both sides are multiplied by (-1), which statement is true? [-2 < -5, -2 > -5]"
  - Responses: `REVERSED` (POSITIVE), `NOT_REVERSED` (BARRIER_SUPPORT).

#### 6.2 Interventions
- `IT-L1-01`:
  - Target KC: `KC-L1`
  - Eligible Barrier: `BH-L1-01`
  - Action: Contrastive Socratic questioning: "What is the inverse operation of multiplication? Since $a$ multiplies $x$, divide both sides by $a$."
- `IT-I1-01`:
  - Target KC: `KC-I1`
  - Eligible Barrier: `BH-I1-01`
  - Action: Number line orientation grounding: "On the number line, $-2$ is to the right of $-5$, so $-2 > -5$. Multiplying or dividing by a negative number reverses the ordering."
