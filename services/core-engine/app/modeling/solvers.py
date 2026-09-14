import math
from typing import Optional, Dict, Any, List, Tuple
import sympy as sp
from app.cas.symbolic_engine import SymbolicEquivalenceEngine


class AgeProblemSolver:
    """Yaş Problemleri Modelleme ve Çözüm Analizcisi."""

    @staticmethod
    def verify_age_relation(
        current_age_expr_str: str,
        years_shift: int,
        target_future_age_str: str
    ) -> bool:
        """
        Zaman kayması doğrulayıcısı: Şimdiki yaş f(x) ise t yıl sonraki yaş f(x) + t olmalıdır.
        """
        try:
            x = sp.Symbol("x")
            expr = sp.sympify(current_age_expr_str)
            target = sp.sympify(target_future_age_str)
            expected = expr + years_shift
            return sp.simplify(expected - target) == 0
        except Exception:
            return False

    @staticmethod
    def check_age_domain(age_val: float) -> Tuple[bool, Optional[str]]:
        """Yaşın reel dünya kısıtları: Pozitif olmalı ve mantıklı bir insan ömrü aralığında olmalı."""
        if age_val <= 0:
            return False, "Yaş değeri sıfırdan büyük bir pozitif sayı olmalıdır."
        if not math.isclose(age_val, round(age_val), abs_tol=1e-5):
            return False, "Yaş değeri bir tamsayı olmalıdır."
        if age_val > 150:
            return False, "Bulunan yaş biyolojik gerçeklikle uyuşmuyor (>150)."
        return True, None


class MotionProblemSolver:
    """Hareket (Hız-Zaman-Yol) Problemleri Analizcisi."""

    @staticmethod
    def solve_meeting_time(distance: float, v1: float, v2: float) -> float:
        """Karşıt yönlü karşılaşma: t = d / (v1 + v2)."""
        if v1 + v2 <= 0:
            raise ValueError("Toplam hız pozitif olmalıdır.")
        return distance / (v1 + v2)

    @staticmethod
    def solve_catchup_time(distance_ahead: float, v_fast: float, v_slow: float) -> float:
        """Aynı yönlü yetişme süresi: t = d / (v_fast - v_slow)."""
        if v_fast <= v_slow:
            raise ValueError("Yetişebilmek için arkadaki aracın hızı daha büyük olmalıdır.")
        return distance_ahead / (v_fast - v_slow)

    @staticmethod
    def solve_harmonic_average_speed(v1: float, v2: float) -> float:
        """Eşit mesafeli gidiş-dönüş harmonik ortalama hızı: 2*v1*v2 / (v1 + v2)."""
        if v1 <= 0 or v2 <= 0:
            raise ValueError("Hızlar pozitif olmalıdır.")
        return (2.0 * v1 * v2) / (v1 + v2)

    @staticmethod
    def check_motion_domain(speed_val: float, time_val: Optional[float] = None) -> Tuple[bool, Optional[str]]:
        if speed_val <= 0:
            return False, "Hız pozitif bir reel sayı olmalıdır."
        if time_val is not None and time_val <= 0:
            return False, "Zaman pozitif bir reel sayı olmalıdır."
        return True, None


class MixtureProblemSolver:
    """Karışım ve Çözelti Problemleri Analizcisi."""

    @staticmethod
    def calculate_mixture_concentration(
        amounts: List[float],
        percentages: List[float]
    ) -> float:
        """
        N adet karışımın birleşimindeki nihai yüzde:
        C_final = sum(m_i * c_i) / sum(m_i)
        """
        total_amount = sum(amounts)
        if total_amount <= 0:
            raise ValueError("Toplam karışım miktarı pozitif olmalıdır.")
        total_solute = sum(a * (p / 100.0) for a, p in zip(amounts, percentages))
        return (total_solute / total_amount) * 100.0

    @staticmethod
    def check_mixture_domain(conc_val: float, amount_val: Optional[float] = None) -> Tuple[bool, Optional[str]]:
        if conc_val < 0.0 or conc_val > 100.0:
            return False, "Karışım yüzdesi %0 ile %100 arasında olmalıdır."
        if amount_val is not None and amount_val <= 0:
            return False, "Karışım miktarı pozitif olmalıdır."
        return True, None


class WorkProblemSolver:
    """İşçi ve Havuz Problemleri Analizcisi."""

    @staticmethod
    def calculate_combined_time(times: List[float]) -> float:
        """
        Birlikte bitirme süresi T:
        1/T = 1/t_1 + 1/t_2 + ... + 1/t_n  =>  T = 1 / sum(1/t_i)
        """
        for t in times:
            if t <= 0:
                raise ValueError("Her bir işçinin bitirme süresi pozitif olmalıdır.")
        rate_sum = sum(1.0 / t for t in times)
        return 1.0 / rate_sum

    @staticmethod
    def check_work_domain(time_val: float) -> Tuple[bool, Optional[str]]:
        if time_val <= 0:
            return False, "İşin tamamlanma süresi pozitif bir değer olmalıdır."
        return True, None


class PercentageProblemSolver:
    """Yüzde ve Kâr-Zarar Problemleri Analizcisi."""

    @staticmethod
    def apply_successive_percentages(base_price: float, rate_percents: List[float]) -> float:
        """
        Art arda zam/indirim uygulama:
        P_final = P_0 * prod(1 + r_i / 100)
        """
        curr = base_price
        for r in rate_percents:
            curr = curr * (1.0 + r / 100.0)
        return curr

    @staticmethod
    def calculate_profit_margin_on_cost(cost: float, selling_price: float) -> float:
        """Maliyet üzerinden kâr oranı (%): (S - C) / C * 100."""
        if cost <= 0:
            raise ValueError("Maliyet pozitif olmalıdır.")
        return ((selling_price - cost) / cost) * 100.0


class OptimizationProblemSolver:
    """Modelleme ve Tek Değişkenli Optimizasyon Analizcisi."""

    @staticmethod
    def find_quadratic_extremum(expr_str: str, variable_str: str = "x") -> Dict[str, Any]:
        """
        ax^2 + bx + c ifadesinin tepe noktasını bulur.
        a < 0 ise maksimum, a > 0 ise minimum.
        """
        try:
            x = sp.Symbol(variable_str)
            expr = sp.sympify(expr_str)
            poly = sp.Poly(expr, x)
            coeffs = poly.all_coeffs()
            if len(coeffs) == 3:
                a, b, c = float(coeffs[0]), float(coeffs[1]), float(coeffs[2])
                if a == 0:
                    return {"is_valid": False, "error": "İkinci derece başkatsayısı 0 olamaz."}
                x_opt = -b / (2.0 * a)
                y_opt = float(expr.subs(x, x_opt))
                return {
                    "type": "MAXIMUM" if a < 0 else "MINIMUM",
                    "x_opt": x_opt,
                    "y_opt": y_opt,
                    "is_valid": True,
                }
            return {"is_valid": False, "error": "İfade ikinci dereceden kuadratik bir polinom değildir."}
        except Exception as e:
            return {"is_valid": False, "error": f"Polinom ayrıştırma hatası: {str(e)}"}
