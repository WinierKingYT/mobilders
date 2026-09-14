import re
from typing import Optional, Dict, Any, List
import sympy as sp
from app.models.schemas import DiagnosticPayload
from app.cas.symbolic_engine import SymbolicEquivalenceEngine


class QuadraticMisconceptionDetector:
    """
    Kuadratik Denklemlerde 5 Temel Bozuk Kuralı (Buggy Rules) Tespit Eden Motor.
    VanLehn (1990) ve Brown & Burton (1978) kuramsal modellerine dayanır.
    """

    def __init__(self, cas_engine: Optional[SymbolicEquivalenceEngine] = None):
        self.cas = cas_engine or SymbolicEquivalenceEngine()
        self.x = sp.Symbol("x")

    def detect(
        self,
        user_step_str: str,
        previous_step_str: str,
        target_equation_str: str,
    ) -> Optional[DiagnosticPayload]:
        """
        Kullanıcının yazdığı adımı önceki adımlarla kıyaslayarak 5 temel bozuk kuralı arar.
        """
        clean_user = user_step_str.strip().replace("^", "**")
        clean_prev = (previous_step_str or target_equation_str).strip().replace("^", "**")

        # 1. BUG-QUAD-01: Sıfır Olmayan Sayıya Sıfır-Çarpım Transferi
        # Örnek: x(x+6) = 2 => x = 2 veya x+6 = 2
        bug1 = self._check_bug_quad_01(clean_user, clean_prev)
        if bug1:
            return bug1

        # 2. BUG-QUAD-02: Eksik Karekök / Negatif Kök Kaybı
        # Örnek: x^2 = 25 => x = 5 veya (x+3)^2 = 11 => x+3 = sqrt(11)
        bug2 = self._check_bug_quad_02(clean_user, clean_prev)
        if bug2:
            return bug2

        # 3. BUG-QUAD-03: Dağılma Özelliğini Üslere Yanlış Genelleme
        # Örnek: (x + 3)^2 = x^2 + 9 (2ax çapraz terimi eksik)
        bug3 = self._check_bug_quad_03(clean_user, clean_prev)
        if bug3:
            return bug3

        # 4. BUG-QUAD-04: Sadeleştirme Yanılsaması / Kök Katli
        # Örnek: x^2 = 6x => x = 6 (x=0 kökü kayboldu)
        bug4 = self._check_bug_quad_04(clean_user, clean_prev)
        if bug4:
            return bug4

        # 5. BUG-QUAD-05: Kuadratik Formülde İşaret Hatası
        # Örnek: b negatifken (-b) yerine b yazılması
        bug5 = self._check_bug_quad_05(clean_user, clean_prev)
        if bug5:
            return bug5

        # 6. BUG-QUAD-06: Eşitsizlikte Negatif Sayıyla Bölmede Yön Değiştirmeme
        bug6 = self._check_bug_quad_06(clean_user, clean_prev)
        if bug6:
            return bug6

        # 7. BUG-QUAD-07: Çift Katlı Kökte İşaret Değiştirme
        bug7 = self._check_bug_quad_07(clean_user, clean_prev)
        if bug7:
            return bug7

        # 8. BUG-QUAD-08: Parabol Tepe Noktasında Eksi İşaretini Unutma
        bug8 = self._check_bug_quad_08(clean_user, clean_prev)
        if bug8:
            return bug8

        # 9. BUG-QUAD-09: Yatay Fonksiyon Ötelemesinde Yönü Ters Anlama
        bug9 = self._check_bug_quad_09(clean_user, clean_prev)
        if bug9:
            return bug9

        # 10. BUG-QUAD-10: Eşitsizlik Çözümünde Kök Bölgesini Ters Seçme
        bug10 = self._check_bug_quad_10(clean_user, clean_prev)
        if bug10:
            return bug10

        return None

    def _check_bug_quad_01(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-QUAD-01: Sıfır Olmayan Sayıya Sıfır-Çarpım Transferi."""
        if "=" in prev_str and "=" in user_str:
            prev_parts = prev_str.split("=")
            rhs_prev = prev_parts[1].strip()
            lhs_prev = prev_parts[0].strip()

            if rhs_prev not in {"0", "0.0"} and ("(" in lhs_prev or "*" in lhs_prev):
                user_parts = user_str.split("=")
                lhs_user = user_parts[0].strip()
                rhs_user = user_parts[1].strip()

                # BUG-QUAD-01: Kullanıcı önceki çarpımın çarpanlarından birini doğrudan rhs_prev'e eşitledi
                if rhs_user == rhs_prev and not ("**2" in lhs_user or "^2" in lhs_user):
                    try:
                        lhs_prev_expr = self.cas.parse_to_sympy(lhs_prev)
                        lhs_user_expr = self.cas.parse_to_sympy(lhs_user)
                        poly_prev = sp.Poly(lhs_prev_expr, self.x)
                        poly_user = sp.Poly(lhs_user_expr, self.x)

                        if poly_user.degree() < poly_prev.degree() and poly_user.degree() >= 1:
                            rem = sp.rem(lhs_prev_expr, lhs_user_expr)
                            if rem == 0:
                                return DiagnosticPayload(
                                    bug_id="BUG-QUAD-01",
                                    severity="CRITICAL",
                                    category="CONCEPTUAL_TRANSFER",
                                    description="Sıfır-çarpım kuralı (A*B=0 => A=0 v B=0) eşitliğin sağ tarafı sıfırdan farklı bir sayı iken geçersizdir.",
                                    remediation_directive="Çarpımları bu sayı eden sonsuz çift olduğunu vurgula; sağ taraf sıfır olmadan çarpanların bu sayıya eşitlenemeyeceğini göster.",
                                    offending_term=user_str,
                                )
                    except Exception:
                        pass
        return None

    def _check_bug_quad_02(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-QUAD-02: Eksik Karekök / Negatif Kök Kaybı."""
        if "**2" in prev_str or "^2" in prev_str:
            if "±" not in user_str and "veya" not in user_str and "or" not in user_str:
                if "sqrt" in user_str or not ("**2" in user_str or "^2" in user_str):
                    try:
                        prev_expr = self.cas.parse_to_sympy(prev_str)
                        roots = sp.solve(prev_expr, self.x)
                        if len(roots) == 2 and any(r > 0 for r in roots) and any(r < 0 for r in roots):
                            user_expr = self.cas.parse_to_sympy(user_str)
                            user_roots = sp.solve(user_expr, self.x)
                            if len(user_roots) == 1 and user_roots[0] > 0:
                                return DiagnosticPayload(
                                    bug_id="BUG-QUAD-02",
                                    severity="CRITICAL",
                                    category="INCOMPLETE_REPRESENTATION",
                                    description="Karesi pozitif bir sayı olan iki simetrik kök (+ ve -) vardır; negatif kök unutuldu.",
                                    remediation_directive="Karesi hedef sayı eden negatif ikiz kökün varlığını sorgulatan Sokratik Sezgi Freni işlet.",
                                    offending_term=user_str,
                                )
                    except Exception:
                        pass
        return None

    def _check_bug_quad_03(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-QUAD-03: Dağılma Özelliğini Üslere Yanlış Genelleme ((x+a)^2 = x^2 + a^2)."""
        try:
            if "**2" in user_str and ("(" in prev_str and "**2" in prev_str):
                user_e = self.cas.parse_to_sympy(user_str)
                prev_e = self.cas.parse_to_sympy(prev_str)
                diff = sp.simplify(prev_e - user_e)
                poly = sp.Poly(diff, self.x)
                coeffs = poly.all_coeffs()
                if poly.degree() == 1 and len(coeffs) >= 1 and coeffs[0] != 0:
                    return DiagnosticPayload(
                        bug_id="BUG-QUAD-03",
                        severity="CRITICAL",
                        category="STRUCTURAL_MISCONCEPTION",
                        description="Tam kare açılımında çarpımın iki katı (2ab) terimi ihmal edildi; dağılma kuralı üslere yanlış uyarlandı.",
                        remediation_directive="Geometrik karo modelini göster; (x+a) karesinin alanında iki adet (ax) dikdörtgeninin varlığını hatırlat.",
                        offending_term=user_str,
                    )
        except Exception:
            pass
        return None

    def _check_bug_quad_04(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-QUAD-04: Sadeleştirme Yanılsaması / Kök Katli (x^2 = 6x => x = 6)."""
        try:
            prev_e = self.cas.parse_to_sympy(prev_str)
            user_e = self.cas.parse_to_sympy(user_str)
            prev_roots = set(sp.solve(prev_e, self.x))
            user_roots = set(sp.solve(user_e, self.x))

            if sp.S.Zero in prev_roots and sp.S.Zero not in user_roots and len(user_roots) < len(prev_roots):
                return DiagnosticPayload(
                    bug_id="BUG-QUAD-04",
                    severity="CRITICAL",
                    category="ROOT_DELETION",
                    description="Her iki tarafı x ile bölerken x=0 kökü yok edildi; sıfıra bölme hatası yapıldı.",
                    remediation_directive="x=0 değerinin orijinal denklemi sağlayıp sağlamadığını test ettir; sadeleştirme yerine ortak paranteze almayı öner.",
                    offending_term=user_str,
                )
        except Exception:
            pass
        return None

    def _check_bug_quad_05(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-QUAD-05: Kuadratik Formülde İşaret Hatası (-b yerinde hata)."""
        try:
            prev_e = self.cas.parse_to_sympy(prev_str)
            poly = sp.Poly(prev_e, self.x)
            if poly.degree() == 2:
                coeffs = poly.all_coeffs()
                a_val, b_val, c_val = coeffs[0], coeffs[1], coeffs[2]
                if b_val < 0:
                    b_str = str(b_val)
                    if b_str in user_str and ("/" in user_str or "sqrt" in user_str or "±" in user_str):
                        return DiagnosticPayload(
                            bug_id="BUG-QUAD-05",
                            severity="WARNING",
                            category="SIGN_SLIP",
                            description="Kuadratik formüldeki (-b) terimi b'nin kendi eksi işaretiyle çarpıldığında pozitif olmalıdır; eksi işaret dağıtımı atlandı.",
                            remediation_directive="-(-b) çarpım kuralını hatırlatan Sokratik bir işaret kontrolü sor.",
                            offending_term=user_str,
                        )
        except Exception:
            pass
        return None

    def _check_bug_quad_06(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-QUAD-06: Eşitsizlikte Negatif Sayıyla Bölmede Yön Değiştirmeme (-2x < 6 => x < -3)."""
        for op in ["<=", ">=", "<", ">"]:
            if op in prev_str and op in user_str:
                prev_parts = prev_str.split(op)
                user_parts = user_str.split(op)
                lhs_prev, rhs_prev = prev_parts[0].strip(), prev_parts[1].strip()
                lhs_user, rhs_user = user_parts[0].strip(), user_parts[1].strip()

                match_neg = re.match(r"^-\s*(\d*)\s*\*?\s*x$", lhs_prev)
                if match_neg and lhs_user in {"x", "+x"}:
                    coeff_val = -float(match_neg.group(1)) if match_neg.group(1) else -1.0
                    try:
                        rhs_prev_val = float(sp.sympify(rhs_prev))
                        expected_flipped_rhs = rhs_prev_val / coeff_val
                        rhs_user_val = float(sp.sympify(rhs_user))
                        if abs(rhs_user_val - expected_flipped_rhs) < 1e-4:
                            return DiagnosticPayload(
                                bug_id="BUG-QUAD-06",
                                severity="CRITICAL",
                                category="INEQUALITY_SIGN_REVERSAL",
                                description="Eşitsizliğin her iki tarafı negatif bir sayıya bölündüğünde eşitsizlik yön değiştirmelidir; aynı yön korundu.",
                                remediation_directive="-2 < 4 iken her iki tarafı -1'e böldüğümüzde sıralamanın nasıl değiştiğini inceleten Sokratik bir soru sor.",
                                offending_term=user_str,
                            )
                    except Exception:
                        pass
        return None

    def _check_bug_quad_07(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-QUAD-07: Çift Katlı Kökte İşaret Değiştirme ((x-2)^2 <= 0 => x <= 2)."""
        if ("**2" in prev_str or "^2" in prev_str) and any(op in prev_str for op in ["<=", "<"]):
            if "0" in prev_str and any(op in user_str for op in ["<=", "<", ">=", ">"]) and "veya" not in user_str:
                return DiagnosticPayload(
                    bug_id="BUG-QUAD-07",
                    severity="CRITICAL",
                    category="SIGN_TABLE_DOUBLE_ROOT",
                    description="Çift katlı köklerde (tam kare ifadelerde) kökün sağında ve solunda işaret değişmez; bir reel sayının karesi asla negatif olamaz.",
                    remediation_directive="Tam kare bir ifadenin işaret tablosunda işaretin çift katlı kökten geçerken neden değişmediğini sorgula.",
                    offending_term=user_str,
                )
        return None

    def _check_bug_quad_08(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-QUAD-08: Parabol Tepe Noktasında Eksi İşaretini Unutma (r = b/(2a))."""
        try:
            if "r" in user_str and "=" in user_str:
                prev_e = self.cas.parse_to_sympy(prev_str.split("=")[0])
                poly = sp.Poly(prev_e, self.x)
                if poly.degree() == 2:
                    coeffs = poly.all_coeffs()
                    a_val, b_val = float(coeffs[0]), float(coeffs[1])
                    true_r = -b_val / (2.0 * a_val)
                    buggy_r = b_val / (2.0 * a_val)

                    user_val_str = user_str.split("=")[1].strip()
                    user_val = float(sp.sympify(user_val_str))
                    if abs(user_val - buggy_r) < 1e-4 and abs(true_r - buggy_r) > 1e-4:
                        return DiagnosticPayload(
                            bug_id="BUG-QUAD-08",
                            severity="CRITICAL",
                            category="PARABOLA_VERTEX_SIGN",
                            description="Parabolün tepe noktası apsisi r = -b/(2a) formülüyle bulunur; formülün başındaki eksi işareti ihmal edildi.",
                            remediation_directive="Simetri ekseninin köklerin aritmetik ortalaması ((x1+x2)/2 = -b/(2a)) olduğunu hatırlatan Sokratik bir soru sor.",
                            offending_term=user_str,
                        )
        except Exception:
            pass
        return None

    def _check_bug_quad_09(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-QUAD-09: Yatay Fonksiyon Ötelemesinde Yönü Ters Anlama."""
        clean_u = user_str.lower()
        if "sola" in clean_u and ("-" in prev_str or "-" in clean_u):
            if any(term in prev_str for term in ["(x -", "(x-", "(x - "]):
                return DiagnosticPayload(
                    bug_id="BUG-QUAD-09",
                    severity="WARNING",
                    category="FUNCTION_TRANSFORMATION_DIRECTION",
                    description="Fonksiyonlarda f(x - h) dönüşümü grafiği h birim SAĞA öteler; parantez içi eksi işareti sola değil sağa kaydırır.",
                    remediation_directive="Yeni tepe noktasının x=h için sıfırlandığını göstererek neden sağa kaydığını Sokratik olarak sorgula.",
                    offending_term=user_str,
                )
        if "sağa" in clean_u and ("+" in prev_str or "+" in clean_u):
            if any(term in user_str for term in ["(x +", "(x+", "(x + "]):
                return DiagnosticPayload(
                    bug_id="BUG-QUAD-09",
                    severity="WARNING",
                    category="FUNCTION_TRANSFORMATION_DIRECTION",
                    description="Sağa öteleme yaparken x yerine (x - h) yazılmalıdır; (x + h) yazıldığında grafik sola ötelenir.",
                    remediation_directive="x=0 noktasının yeni değerini nereye taşıdığını test ettiren bir değer denemesi yaptır.",
                    offending_term=user_str,
                )
        return None

    def _check_bug_quad_10(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-QUAD-10: Eşitsizlik Çözümünde Kök Bölgesini Ters Seçme."""
        try:
            if any(op in prev_str for op in [">", ">="]):
                if ("(" in user_str or "[" in user_str) and "∪" not in user_str and "veya" not in user_str:
                    prev_lhs = prev_str.split(">")[0].strip()
                    lhs_expr = self.cas.parse_to_sympy(prev_lhs)
                    poly = sp.Poly(lhs_expr, self.x)
                    if poly.degree() == 2 and poly.all_coeffs()[0] > 0:
                        roots = sorted([float(r) for r in sp.solve(lhs_expr, self.x)])
                        if len(roots) == 2:
                            match_interval = re.findall(r"[-+]?\d*\.?\d+", user_str)
                            if len(match_interval) >= 2:
                                u_r1, u_r2 = float(match_interval[0]), float(match_interval[1])
                                if abs(u_r1 - roots[0]) < 1e-4 and abs(u_r2 - roots[1]) < 1e-4:
                                    return DiagnosticPayload(
                                        bug_id="BUG-QUAD-10",
                                        severity="CRITICAL",
                                        category="INEQUALITY_REGION_INVERSION",
                                        description="İkinci dereceden eşitsizlikte başkatsayı pozitif iken > 0 eşitsizliği köklerin dışını ister; köklerin arası seçildi.",
                                        remediation_directive="Köklerin arasından bir test noktası seçtirip (ör. x=2) ifadenin işaretini kontrol ettir.",
                                        offending_term=user_str,
                                    )
        except Exception:
            pass
        return None

