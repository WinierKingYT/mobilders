# MOBILDERS V1 COGNITIVE DOMAIN CONTRACT: CT-PAR1 & CT-POLY1
## Version: v0.1 | Status: Canonical Focus Extension
## Authority: Focus Domain Mathematical & Pedagogical Architecture (PLE Hedef 4)

---

### 1. Scope and Mission
This document formally defines the cognitive domain contracts for:
1. **`CT-PAR1`**: Paraboller ve Tepe Noktası ($f(x) = ax^2 + bx + c$, Tepe Noktası $T(r, k)$ ve Ekstremum Karakteri).
2. **`CT-POLY1`**: Polinomlar ve Kalan Teoremi ($P(x) = ax^2 + bx + c$ polinomunun $x - d$ ile bölümünden kalan $K = P(d)$).

These topics extend the Focus Kernel cognitive architecture into high school curriculum (Faz I / Hedef 4), operating under the **Server-Only Truth Invariant** and deterministic cognitive state management.

---

### 2. Theoretical Pedagogical Principles
1. **Server-Only Mathematical & Diagnostic Authority**: Client applications only submit student inputs (strings, numbers, choices). The server evaluates mathematical validity, diagnoses misconceptions, evaluates probes, and controls stage progression.
2. **Closed Pedagogical Repair Loop**:
   $$\text{Error Observation (EO)} \longrightarrow \text{Diagnostic Probe (PR)} \longrightarrow \text{Socratic Intervention (IT)} \longrightarrow \text{Original Self-Correction} \longrightarrow \text{Transfer Task (TT)}$$
3. **Target Root Misconceptions**:
   - `BUG-PARAB-01`: Parabolün tepe noktası apsisinde eksi işareti hatası ($r = b/(2a)$ instead of $-b/(2a)$).
   - `BUG-PARAB-02`: Tepe ordinatını sabit terim sanma ($k = c$ instead of $f(r)$).
   - `BUG-POLY-01`: Kalan teoreminde bölen kökünde işaret hatası ($x - d = 0 \implies x = -d$).
   - `BUG-POLY-02`: Kalan hesabı yerine katsayılar toplamını $P(1)$ veya sabit terimi $P(0)$ yazma.

---

### 3. Knowledge Component (KC) Catalog

| KC ID | Name | Canonical Definition | Associated Barriers |
| :--- | :--- | :--- | :--- |
| `KC-P1` | Parabola Vertex Coordinates ($r, k$) | The vertex abscissa is $r = -\frac{b}{2a}$, and ordinate is $k = f(r) = c - \frac{b^2}{4a}$. | `BH-P1-01` |
| `KC-P2` | Parabola Extrema Direction | If $a > 0$, vertex is a global minimum; if $a < 0$, vertex is a global maximum. | `BH-P2-01` |
| `KC-PL1` | Polynomial Remainder Theorem | The remainder of $P(x)$ divided by $x - d$ is the value $P(d)$. | `BH-PL1-01` |
| `KC-PL2` | Polynomial Divisor Root Isolation | Setting divisor $x - d = 0$ yields root $x = d$ (reversing the sign of constant). | `BH-PL2-01` |

---

### 4. Topic 1: `CT-PAR1` (Parabolas & Vertex Calculation)

#### 4.1 Task Context Schema (`CTPAR1TaskContext`)
- Coefficients: $a, b, c \in \mathbb{Z}$ with $a \neq 0$, such that $r = -b / (2a)$ is an integer or simple half-integer.
- Target equation: $f(x) = ax^2 + bx + c$.
- Expected vertex: $r^* = -b / (2a)$, $k^* = a(r^*)^2 + b(r^*) + c$.
- Extrema: `is_minimum = (a > 0)`.

#### 4.2 Stage State Machine
- `S1_CALCULATE_R`:
  - Learner submits $r$ value (e.g., `r = 2` or `2`).
  - Truth Adapter evaluates `check_parabola_vertex_r(a, b, observed_r)`.
  - If valid $\rightarrow$ advance to `S2_CALCULATE_K`.
  - If invalid:
    - If `observed_r == b / (2a)` $\rightarrow$ emit `EO-VERTEX-FORMULA-SIGN-INVERTED` (`BUG-PARAB-01`).
    - Otherwise $\rightarrow$ emit `EO-CALCULATION-ERROR`.
- `S2_CALCULATE_K`:
  - Learner submits $k$ value (e.g., `k = -1` or `-1`).
  - Truth Adapter evaluates `check_parabola_vertex_k(a, b, c, r, observed_k)`.
  - If valid $\rightarrow$ advance to `S3_EXTREMUM_CLASSIFICATION`.
  - If invalid:
    - If `observed_k == c` and $c \neq k^*$ $\rightarrow$ emit `EO-VERTEX-ORDINATE-CONFUSED-WITH-CONSTANT` (`BUG-PARAB-02`).
    - Otherwise $\rightarrow$ emit `EO-CALCULATION-ERROR`.
- `S3_EXTREMUM_CLASSIFICATION`:
  - Learner submits classification: `minimum` or `maksimum`.
  - Truth Adapter checks `check_parabola_extremum(a, observed_is_min)`.
  - If valid $\rightarrow$ advance to `COMPLETED_INDEPENDENTLY` or `COMPLETED_WITH_SUPPORT`.

---

### 5. Topic 2: `CT-POLY1` (Polynomials & Remainder Theorem)

#### 5.1 Task Context Schema (`CTPOLY1TaskContext`)
- Coefficients: $a, b, c, d \in \mathbb{Z}$ with $a \neq 0$.
- Polynomial: $P(x) = ax^2 + bx + c$.
- Divisor: $x - d$. Divisor root is $x = d$.
- Expected remainder: $R = P(d) = a(d)^2 + b(d) + c$.

#### 5.2 Stage State Machine
- `S1_ROOT_OF_DIVISOR`:
  - Learner submits divisor root (e.g., `x = 2` or `2`).
  - Truth Adapter evaluates `check_polynomial_divisor_root(d, observed_root)`.
  - If valid $\rightarrow$ advance to `S2_EVALUATE_REMAINDER`.
  - If invalid:
    - If `observed_root == -d` $\rightarrow$ emit `EO-DIVISOR-ROOT-SIGN-INVERTED` (`BUG-POLY-01`).
    - Otherwise $\rightarrow$ emit `EO-CALCULATION-ERROR`.
- `S2_EVALUATE_REMAINDER`:
  - Learner submits remainder $K$ (e.g., `kalan = 7` or `7`).
  - Truth Adapter evaluates `check_polynomial_remainder(a, b, c, d, observed_rem)`.
  - If valid $\rightarrow$ advance to `COMPLETED_INDEPENDENTLY` or `COMPLETED_WITH_SUPPORT`.
  - If invalid:
    - If `observed_rem == a + b + c` ($P(1)$) or `observed_rem == c` ($P(0)$) $\rightarrow$ emit `EO-REMAINDER-CONFUSED-WITH-COEFF-SUM` (`BUG-POLY-02`).
    - Otherwise $\rightarrow$ emit `EO-CALCULATION-ERROR`.

---

### 6. Diagnostic Probes & Interventions

#### 6.1 Probes
- `PR-P1-01`:
  - Target KC: `KC-P1`
  - Prompt: "Parabolün tepe noktası apsisi formülü hangisidir? [-b/(2a), b/(2a), -b/a]"
  - Responses: `MINUS_B_OVER_2A` (POSITIVE), `PLUS_B_OVER_2A` (BARRIER_SUPPORT), `OTHER` (INCONCLUSIVE).
- `PR-PL1-01`:
  - Target KC: `KC-PL1`
  - Prompt: "P(x) polinomunun (x - 3) ile bölümünden kalanı bulmak için x yerine ne yazılmalıdır? [3, -3, 0]"
  - Responses: `PLUS_3` (POSITIVE), `MINUS_3` (BARRIER_SUPPORT), `OTHER` (INCONCLUSIVE).

#### 6.2 Interventions
- `IT-P1-01`:
  - Socratic guidance demonstrating $r = -b/(2a)$ through the axis of symmetry and derivative $f'(x) = 2ax + b = 0$.
- `IT-PL1-01`:
  - Socratic guidance demonstrating $P(x) = (x - d)Q(x) + K$; setting $x = d$ eliminates the quotient term $(d - d)Q(d) = 0$, leaving $P(d) = K$.
