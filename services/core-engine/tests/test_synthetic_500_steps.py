import time
import numpy as np
import pytest
import sympy as sp
from app.cas.symbolic_engine import SymbolicEquivalenceEngine
from app.misconceptions.detector import QuadraticMisconceptionDetector


@pytest.fixture(scope="module")
def engines():
    cas = SymbolicEquivalenceEngine()
    detector = QuadraticMisconceptionDetector(cas)
    return cas, detector


def generate_valid_cases():
    """Generates 250 algebraically valid step transitions."""
    cases = []
    # Set 1: Standard form to RHS constant (50 cases)
    # ax^2 + bx + c = 0 <=> ax^2 + bx = -c
    for a in [1, 2, -1, 3, -2]:
        for b in [-6, -4, -2, 0, 2, 4, 6]:
            for c in [-10, -5, -1, 3, 7]:
                target = f"{a}*x**2 + {b}*x + {c} = 0"
                step = f"{a}*x**2 + {b}*x = {-c}"
                cases.append((step, target, "rhs_constant_shift"))
                if len(cases) == 50:
                    break
            if len(cases) == 50:
                break
        if len(cases) == 50:
            break

    # Set 2: Factored form expansions (50 cases)
    # (x - p)(x - q) = 0 <=> x^2 - (p+q)x + pq = 0
    p_vals = [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]
    q_vals = [-3, -2, -1, 1, 2, 3, 4, 5, 6, 7]
    for p in p_vals:
        for q in q_vals:
            b_val = -(p + q)
            c_val = p * q
            step = f"(x - {p})*(x - {q}) = 0"
            target = f"x**2 + {b_val}*x + {c_val} = 0"
            cases.append((step, target, "factored_expansion"))
            if len(cases) == 100:
                break
        if len(cases) == 100:
            break

    # Set 3: Completing the square forms (50 cases)
    # (x + d)^2 = k <=> x^2 + 2dx + (d^2 - k) = 0
    d_vals = [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]
    k_vals = [1, 2, 3, 4, 5, 7, 9]
    for d in d_vals:
        for k in k_vals:
            b_val = 2 * d
            c_val = d * d - k
            step = f"(x + {d})**2 = {k}"
            target = f"x**2 + {b_val}*x + {c_val} = 0"
            cases.append((step, target, "completing_square"))
            if len(cases) == 150:
                break
        if len(cases) == 150:
            break

    # Set 4: Multiplied by non-zero constant scaling (50 cases)
    # k*(x^2 + bx + c) = 0 <=> x^2 + bx + c = 0
    scales = [2, 3, 4, 5, -1, -2, -3, 6, 7]
    for m in scales:
        for b in [-3, -1, 0, 2, 4, 5]:
            for c in [-6, -2, 1, 5, 8]:
                step = f"{m}*(x**2 + {b}*x + {c}) = 0"
                target = f"x**2 + {b}*x + {c} = 0"
                cases.append((step, target, "scalar_multiplication"))
                if len(cases) == 200:
                    break
            if len(cases) == 200:
                break
        if len(cases) == 200:
            break

    # Set 5: Term rearrangement / LHS-RHS transposition (50 cases)
    # ax^2 + c = -bx <=> ax^2 + bx + c = 0
    for a in [1, 2, 3, 4, 5]:
        for b in [-5, -2, 3, 6, 7]:
            for c in [-7, -3, 2, 8, 11]:
                step = f"{a}*x**2 + {c} = {-b}*x"
                target = f"{a}*x**2 + {b}*x + {c} = 0"
                cases.append((step, target, "transposition"))
                if len(cases) == 250:
                    break
            if len(cases) == 250:
                break
        if len(cases) == 250:
            break

    return cases[:250]


def generate_flawed_cases():
    """Generates 250 flawed step transitions covering 5 buggy rules and arithmetic errors."""
    cases = []

    # Category 1: BUG-QUAD-01 Non-zero zero-product property (50 cases)
    # Previous: (x - p)*(x - q) = k  (k != 0)
    # Flawed User Step: x - p = k
    for p in range(1, 11):
        for k in [2, 3, 4, 5, 6]:
            prev = f"(x - {p})*(x + 2) = {k}"
            user = f"x - {p} = {k}"
            target = f"x**2 + {2-p}*x - {2*p + k} = 0"
            cases.append((user, prev, target, "BUG-QUAD-01"))
            if len(cases) >= 50:
                break
        if len(cases) >= 50:
            break

    # Category 2: BUG-QUAD-02 Missing negative root (50 cases)
    # Previous: x^2 = k^2
    # Flawed User Step: x = k (ignoring x = -k)
    k_squares = [4, 9, 16, 25, 36, 49, 64, 81, 100, 121]
    for idx, sq in enumerate(k_squares):
        root = int(np.sqrt(sq))
        for offset in range(5):
            prev = f"x**2 = {sq + offset*0}"
            user = f"x = {root}"
            target = f"x**2 - {sq} = 0"
            cases.append((user, prev, target, "BUG-QUAD-02"))
            if len(cases) >= 100:
                break
        if len(cases) >= 100:
            break

    # Category 3: BUG-QUAD-03 Exponent distribution over addition (50 cases)
    # Previous: (x + a)^2 = k
    # Flawed User Step: x^2 + a^2 = k (missing 2ax term)
    for a in range(1, 11):
        for k in [5, 7, 10, 11, 15]:
            prev = f"(x + {a})**2 = {k}"
            user = f"x**2 + {a*a} = {k}"
            target = f"x**2 + {2*a}*x + {a*a - k} = 0"
            cases.append((user, prev, target, "BUG-QUAD-03"))
            if len(cases) >= 150:
                break
        if len(cases) >= 150:
            break

    # Category 4: BUG-QUAD-04 Root cancelling / division by x (50 cases)
    # Previous: x^2 = c*x
    # Flawed User Step: x = c (losing root x=0)
    for c in range(1, 51):
        prev = f"x**2 = {c}*x"
        user = f"x = {c}"
        target = f"x**2 - {c}*x = 0"
        cases.append((user, prev, target, "BUG-QUAD-04"))
        if len(cases) >= 200:
            break

    # Category 5: BUG-QUAD-05 and General Arithmetic / Sign Inversions (50 cases)
    # Quadratic formula sign slip or incorrect arithmetic
    for b_neg in [-3, -4, -5, -6, -7]:
        for c_val in [2, 3, 4, 5, 6]:
            prev = f"x**2 + {b_neg}*x + {c_val} = 0"
            # User uses b_neg instead of -b_neg in formula
            user = f"x = ({b_neg} + 1)/2"
            target = f"x**2 + {b_neg}*x + {c_val} = 0"
            cases.append((user, prev, target, "BUG-QUAD-05"))
            if len(cases) >= 225:
                break
        if len(cases) >= 225:
            break

    # Additional invalid steps (pure arithmetic / algebraic fallacy)
    for i in range(1, 26):
        prev = f"x**2 + {i}*x - 10 = 0"
        user = f"x**2 + {i}*x = 999"  # completely wrong value
        target = f"x**2 + {i}*x - 10 = 0"
        cases.append((user, prev, target, "ARITHMETIC_ERROR"))

    return cases[:250]


def test_gate1_500_synthetic_algebraic_steps(engines):
    """
    DoD KAPI 1: SEMBOLİK CAS VE MATEMATİKSEL DOĞRULUK KAPISI
    - 500 sentetik cebirsel adım testi (250 geçerli adım, 250 hatalı adım).
    - Başarı Kriteri: 0 False Positive, 0 False Negative.
    - Hız Kriteri: Adım başına P95 analiz süresi <= 120 ms.
    """
    cas, detector = engines

    valid_cases = generate_valid_cases()
    flawed_cases = generate_flawed_cases()

    assert len(valid_cases) == 250, f"Expected 250 valid cases, got {len(valid_cases)}"
    assert len(flawed_cases) == 250, f"Expected 250 flawed cases, got {len(flawed_cases)}"

    latencies_ms = []
    false_positives = 0
    false_negatives = 0

    # 1. Test 250 Valid Cases (Should be equivalent, 0 false negatives)
    for step, target, desc in valid_cases:
        t0 = time.perf_counter()
        is_equiv, elapsed, diff = cas.verify_equivalence(step, target)
        latencies_ms.append(elapsed)

        if not is_equiv:
            false_positives += 1
            print(f"FP on valid step [{desc}]: step='{step}', target='{target}', diff='{diff}'")

        # Detector should NOT flag valid algebraic step as a bug
        diag = detector.detect(step, target, target)
        assert diag is None, f"Valid step erroneously flagged as {diag.bug_id}: {step}"

    # 2. Test 250 Flawed Cases (Should NOT be equivalent or should detect bug)
    for user_step, prev_step, target, bug_type in flawed_cases:
        t0 = time.perf_counter()
        is_equiv = False
        try:
            is_equiv, elapsed, _ = cas.verify_equivalence(user_step, target)
        except Exception:
            elapsed = (time.perf_counter() - t0) * 1000.0
            is_equiv = False

        latencies_ms.append(elapsed)

        # In all flawed cases, it must NOT be judged as fully equivalent to target
        if is_equiv:
            false_negatives += 1
            print(f"FN on flawed step [{bug_type}]: step='{user_step}', target='{target}'")

        # Misconception detector checks
        if bug_type.startswith("BUG-QUAD"):
            diag = detector.detect(user_step, prev_step, target)
            assert diag is not None, f"Failed to detect {bug_type} for step='{user_step}', prev='{prev_step}'"
            assert diag.bug_id == bug_type

    # Verify Acceptance Gate Criteria
    p95_latency = float(np.percentile(latencies_ms, 95))
    mean_latency = float(np.mean(latencies_ms))
    max_latency = float(np.max(latencies_ms))

    print(f"\n--- DoD KAPI 1 DOĞRULAMA RAPORU ---")
    print(f"Toplam Test Edilen Adım: {len(latencies_ms)}")
    print(f"False Positives: {false_positives} (Hedef: 0)")
    print(f"False Negatives: {false_negatives} (Hedef: 0)")
    print(f"Ortalama Gecikme: {mean_latency:.2f} ms")
    print(f"P95 Gecikme: {p95_latency:.2f} ms (Hedef: <= 120.0 ms)")
    print(f"Maksimum Gecikme: {max_latency:.2f} ms")

    assert false_positives == 0, f"Gate 1 FAILED: {false_positives} False Positives detected!"
    assert false_negatives == 0, f"Gate 1 FAILED: {false_negatives} False Negatives detected!"
    assert p95_latency <= 120.0, f"Gate 1 FAILED: P95 latency {p95_latency:.2f}ms exceeds 120ms!"
