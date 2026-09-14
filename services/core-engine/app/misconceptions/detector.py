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

        # 11. BUG-PARAB-01: Parabol Tepe Apsisi Formülü Eksi İşareti Hatası
        bug_p1 = self._check_bug_parab_01(clean_user, clean_prev)
        if bug_p1:
            return bug_p1

        # 12. BUG-PARAB-02: Simetri Ekseni Kargaşası ve Ordinat Yanılgısı
        bug_p2 = self._check_bug_parab_02(clean_user, clean_prev)
        if bug_p2:
            return bug_p2

        # 13. BUG-PARAB-03: Kök Geometrisi ve Tepe Noktası İlişkisi Hatası
        bug_p3 = self._check_bug_parab_03(clean_user, clean_prev)
        if bug_p3:
            return bug_p3

        # 14. BUG-PARAB-04: Y-Kesişimi ile X-Kesişimini Karıştırma
        bug_p4 = self._check_bug_parab_04(clean_user, clean_prev)
        if bug_p4:
            return bug_p4

        # 15. BUG-PARAB-05: Başkatsayı a İşaretine Göre Ekstremum Tersliği
        bug_p5 = self._check_bug_parab_05(clean_user, clean_prev)
        if bug_p5:
            return bug_p5

        # 16. BUG-POLY-01: Kalan Teoreminde Kök İşareti Yanılgısı
        bug_poly1 = self._check_bug_poly_01(clean_user, clean_prev)
        if bug_poly1:
            return bug_poly1

        # 17. BUG-POLY-02: Katsayılar Toplamı ve Sabit Terim Kargaşası
        bug_poly2 = self._check_bug_poly_02(clean_user, clean_prev)
        if bug_poly2:
            return bug_poly2

        # 18. BUG-POLY-03: Polinom Bölmesinde Derece Kuralı İhlali
        bug_poly3 = self._check_bug_poly_03(clean_user, clean_prev)
        if bug_poly3:
            return bug_poly3

        # 19. BUG-POLY-04: Polinom Derece Aritmetiğinde Çarpım/Kuvvet Yanılgısı
        bug_poly4 = self._check_bug_poly_04(clean_user, clean_prev)
        if bug_poly4:
            return bug_poly4

        # 20. BUG-POLY-05: Polinom Bölmesinde Kökü Doğrudan Kalana Eşitleme
        bug_poly5 = self._check_bug_poly_05(clean_user, clean_prev)
        if bug_poly5:
            return bug_poly5

        # 21. BUG-TRIG-01: Trigonometrik Lineerlik Tuzağı
        bug_t1 = self._check_bug_trig_01(clean_user, clean_prev)
        if bug_t1:
            return bug_t1

        # 22. BUG-TRIG-02: Fonksiyon İsim ve Argüman Sadeleştirme Hatası
        bug_t2 = self._check_bug_trig_02(clean_user, clean_prev)
        if bug_t2:
            return bug_t2

        # 23. BUG-TRIG-03: Birim Çember Eksen Karışıklığı
        bug_t3 = self._check_bug_trig_03(clean_user, clean_prev)
        if bug_t3:
            return bug_t3

        # 24. BUG-TRIG-04: Trigonometrik Denklemde Kök/Periyot Kaybı
        bug_t4 = self._check_bug_trig_04(clean_user, clean_prev)
        if bug_t4:
            return bug_t4

        # 25. BUG-TRIG-05: Negatif Açı ve Parite Yanılgısı
        bug_t5 = self._check_bug_trig_05(clean_user, clean_prev)
        if bug_t5:
            return bug_t5

        # 26. BUG-LOG-01: Logaritma Toplam-Dağılma Tuzağı
        bug_l1 = self._check_bug_log_01(clean_user, clean_prev)
        if bug_l1:
            return bug_l1

        # 27. BUG-LOG-02: Logaritma Çarpım/Kuvvet Karışıklığı
        bug_l2 = self._check_bug_log_02(clean_user, clean_prev)
        if bug_l2:
            return bug_l2

        # 28. BUG-LOG-03: Negatif Tanım Kümesi İhmali / Sahte Kök
        bug_l3 = self._check_bug_log_03(clean_user, clean_prev)
        if bug_l3:
            return bug_l3

        # 29. BUG-LOG-04: Taban Değiştirme ve Bölme Hatası
        bug_l4 = self._check_bug_log_04(clean_user, clean_prev)
        if bug_l4:
            return bug_l4

        # 30. BUG-LOG-05: Üstel/Logaritma Taban ve Kuvvet Karışıklığı
        bug_l5 = self._check_bug_log_05(clean_user, clean_prev)
        if bug_l5:
            return bug_l5

        # 31. BUG-CALC-01: Zincir Kuralında İç Türevi Unutma
        bug_c1 = self._check_bug_calc_01(clean_user, clean_prev)
        if bug_c1:
            return bug_c1

        # 32. BUG-CALC-02: Bölümün Türevinde İşaret Hatası
        bug_c2 = self._check_bug_calc_02(clean_user, clean_prev)
        if bug_c2:
            return bug_c2

        # 33. BUG-CALC-03: 0/0 Belirsizliğini Tanımsız veya Sıfır İlan Etme
        bug_c3 = self._check_bug_calc_03(clean_user, clean_prev)
        if bug_c3:
            return bug_c3

        # 34. BUG-CALC-04: f'(x)=0 Noktasını Kesin Ekstremum Sanma
        bug_c4 = self._check_bug_calc_04(clean_user, clean_prev)
        if bug_c4:
            return bug_c4

        # 35. BUG-CALC-05: Çarpımın Türevinde Sahte Doğrusallık ((uv)' = u'v')
        bug_c5 = self._check_bug_calc_05(clean_user, clean_prev)
        if bug_c5:
            return bug_c5

        # 36. BUG-CALC-06: Sabit Sayının Türevini Sıfır Yerine Kendisi Bırakma
        bug_c6 = self._check_bug_calc_06(clean_user, clean_prev)
        if bug_c6:
            return bug_c6

        # 37. BUG-CALC-07: Limiti Fonksiyon Değeriyle Özdeşleştirme Fallacy
        bug_c7 = self._check_bug_calc_07(clean_user, clean_prev)
        if bug_c7:
            return bug_c7

        # 38. BUG-CALC-08: Kosinüs Türevinde Eksi İşareti Hatası
        bug_c8 = self._check_bug_calc_08(clean_user, clean_prev)
        if bug_c8:
            return bug_c8

        # 39. BUG-CALC-09: L'Hôpital ile Bölüm Türevinin Karıştırılması ((f/g)' = f'/g')
        bug_c9 = self._check_bug_calc_09(clean_user, clean_prev)
        if bug_c9:
            return bug_c9

        # 40. BUG-CALC-10: Teğet Doğrusu Eğimini Fonksiyon Değerine Eşitleme
        bug_c10 = self._check_bug_calc_10(clean_user, clean_prev)
        if bug_c10:
            return bug_c10

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
        clean_p = prev_str.lower()
        if any(trig in clean_p for trig in ("sin", "cos", "tan", "cot", "sec", "csc")):
            return None
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

    def _extract_quadratic_poly(self, expr_str: str) -> Optional[sp.Poly]:
        """İfade metninden (f(x) = ax^2 + bx + c veya ax^2 + bx + c = 0) kuadratik polinomu çıkarır."""
        try:
            clean = expr_str.strip()
            if "=" in clean:
                parts = clean.split("=")
                lhs, rhs = parts[0].strip(), parts[1].strip()
                if lhs in {"f(x)", "y", "g(x)", "P(x)", "h(x)"}:
                    clean = rhs
                elif rhs in {"0", "0.0"}:
                    clean = lhs
                else:
                    clean = f"({lhs}) - ({rhs})"
            e = self.cas.parse_to_sympy(clean)
            poly = sp.Poly(e, self.x)
            if poly.degree() == 2:
                return poly
        except Exception:
            pass
        return None

    def _check_bug_parab_01(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PARAB-01: Parabol Tepe Noktası Apsisi Formülünde Eksi İşareti Hatası (r = b/(2a) veya r = -b/a).
        """
        try:
            clean_u = user_str.lower().replace(" ", "")
            if "r=" in clean_u or "tepeapsisi=" in clean_u:
                poly = self._extract_quadratic_poly(prev_str)
                if poly and poly.degree() == 2:
                    coeffs = poly.all_coeffs()
                    a_val, b_val = float(coeffs[0]), float(coeffs[1])
                    true_r = -b_val / (2.0 * a_val)
                    buggy_r_no_minus = b_val / (2.0 * a_val)
                    buggy_r_no_two = -b_val / a_val

                    user_val_str = user_str.split("=")[1].strip()
                    user_val = float(sp.sympify(user_val_str))
                    if abs(user_val - true_r) > 1e-4:
                        if abs(user_val - buggy_r_no_minus) < 1e-4:
                            return DiagnosticPayload(
                                bug_id="BUG-PARAB-01",
                                severity="CRITICAL",
                                category="PARABOLA_VERTEX_FORMULA_SIGN",
                                description="Parabolün tepe noktası apsisi r = -b/(2a) formülüyle bulunur; eksi işareti hatası yapıldı.",
                                remediation_directive="Türevin sıfır olduğu tepe noktası şartını (2ax + b = 0 => x = -b/(2a)) hatırlatan Sokratik bir soru sor.",
                                offending_term=user_str,
                            )
        except Exception:
            pass
        return None

    def _check_bug_parab_02(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PARAB-02: Simetri Ekseni Kargaşası ve Ordinat Yanılgısı (y = r doğrusu sanma veya k = c alma).
        """
        clean_u = user_str.lower()
        if "simetri ekseni" in clean_u:
            if re.search(r"\by\s*=", clean_u):
                return DiagnosticPayload(
                    bug_id="BUG-PARAB-02",
                    severity="CRITICAL",
                    category="PARABOLA_AXIS_CONFUSION",
                    description="Simetri ekseni düşey bir doğru olup denklemi x = r'dir (y = r yatay doğrudur).",
                    remediation_directive="Parabolü iki eş parçaya bölen simetri çizgisinin düşey olduğunu ve denkleminin x=r olduğunu göster.",
                    offending_term=user_str,
                )
        try:
            clean_tight = clean_u.replace(" ", "")
            if "k=" in clean_tight or "tepeordinati=" in clean_tight:
                poly = self._extract_quadratic_poly(prev_str)
                if poly and poly.degree() == 2:
                    coeffs = poly.all_coeffs()
                    a_val, b_val, c_val = float(coeffs[0]), float(coeffs[1]), float(coeffs[2])
                    true_r = -b_val / (2.0 * a_val)
                    true_k = c_val - (b_val ** 2) / (4.0 * a_val)
                    val_str = user_str.split("=")[1].strip()
                    user_val = float(sp.sympify(val_str))
                    if abs(user_val - c_val) < 1e-4 and abs(user_val - true_k) > 1e-4:
                        return DiagnosticPayload(
                            bug_id="BUG-PARAB-02",
                            severity="CRITICAL",
                            category="PARABOLA_AXIS_CONFUSION",
                            description="Tepe ordinatı k, sabit terim c değildir; k = f(r) değeridir (x yerine r konulmalıdır).",
                            remediation_directive="Sabit terim c'nin parabolün y-eksenini kestiği nokta olduğunu, tepe noktasının ise f(r) ile bulunduğunu sorgula.",
                            offending_term=user_str,
                        )
        except Exception:
            pass
        return None

    def _check_bug_parab_03(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PARAB-03: Kök Geometrisi ve Tepe Noktası İlişkisi Hatası (r = x1 + x2 sanma).
        """
        clean_u = user_str.lower().replace(" ", "")
        if "r=x1+x2" in clean_u or "r=kökler_toplamı" in clean_u or "r=-b/a" in clean_u:
            return DiagnosticPayload(
                bug_id="BUG-PARAB-03",
                severity="CRITICAL",
                category="PARABOLA_ROOT_GEOMETRY",
                description="Tepe noktası apsisi köklerin toplamı değil, aritmetik ortalamasıdır: r = (x1 + x2)/2.",
                remediation_directive="Köklerin simetri eksenine eşit uzaklıkta olduğunu ve orta noktanın 2'ye bölünerek bulunduğunu hatırlat.",
                offending_term=user_str,
            )
        try:
            if "r=" in clean_u:
                poly = self._extract_quadratic_poly(prev_str)
                if poly and poly.degree() == 2:
                    coeffs = poly.all_coeffs()
                    a_val, b_val = float(coeffs[0]), float(coeffs[1])
                    true_r = -b_val / (2.0 * a_val)
                    sum_roots = -b_val / a_val
                    user_val = float(sp.sympify(user_str.split("=")[1].strip()))
                    if abs(user_val - sum_roots) < 1e-4 and abs(user_val - true_r) > 1e-4:
                        return DiagnosticPayload(
                            bug_id="BUG-PARAB-03",
                            severity="CRITICAL",
                            category="PARABOLA_ROOT_GEOMETRY",
                            description="Tepe noktası apsisi kökler toplamı değildir; kökler toplamının yarısıdır (r = (x1+x2)/2).",
                            remediation_directive="Kökler toplamını (-b/a) bulduktan sonra neden 2'ye bölmemiz gerektiğini Sokratik olarak sorgula.",
                            offending_term=user_str,
                        )
        except Exception:
            pass
        return None

    def _check_bug_parab_04(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PARAB-04: Y-Kesişimi (c) ile Kökleri (X-Kesişimlerini) Karıştırma.
        """
        clean_u = user_str.lower()
        if "kök = c" in clean_u or "kök=c" in clean_u or "kökü c" in clean_u:
            return DiagnosticPayload(
                bug_id="BUG-PARAB-04",
                severity="CRITICAL",
                category="PARABOLA_INTERCEPT_CONFUSION",
                description="Parabolün y-eksenini kestiği sabit terim c ile kökler (x-kesişimleri) birbirine karıştırıldı.",
                remediation_directive="Bir fonksiyonun köklerinin f(x) = 0 yapan x değerleri olduğunu, c'nin ise f(0) olduğunu vurgula.",
                offending_term=user_str,
            )
        try:
            poly = self._extract_quadratic_poly(prev_str)
            if poly and poly.degree() == 2:
                coeffs = poly.all_coeffs()
                c_val = float(coeffs[2])
                roots = [float(r) for r in sp.solve(poly.as_expr(), self.x)]
                if re.search(r"\bx\s*=\s*" + re.escape(str(int(c_val) if c_val.is_integer() else c_val)), user_str):
                    if not any(abs(r - c_val) < 1e-4 for r in roots):
                        if "kök" in clean_u or "root" in clean_u or "sıfır" in clean_u:
                            return DiagnosticPayload(
                                bug_id="BUG-PARAB-04",
                                severity="CRITICAL",
                                category="PARABOLA_INTERCEPT_CONFUSION",
                                description="Sabit terim c doğrudan parabolün kökü sanıldı; c sadece y-ekseni kesişimidir.",
                                remediation_directive="Köklerin y=0 iken bulunduğunu, sabit terimin ise x=0 iken çıktığını sorgulat.",
                                offending_term=user_str,
                            )
        except Exception:
            pass
        return None

    def _check_bug_parab_05(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PARAB-05: Başkatsayı a'nın İşaretine Göre Kollar ve Ekstremum Yönü Tersliği.
        """
        try:
            clean_u = user_str.lower()
            poly = self._extract_quadratic_poly(prev_str)
            if poly and poly.degree() == 2:
                a_val = float(poly.all_coeffs()[0])
                if a_val > 0:
                    if "maksimum" in clean_u or "en büyük" in clean_u or "maximum" in clean_u:
                        return DiagnosticPayload(
                            bug_id="BUG-PARAB-05",
                            severity="CRITICAL",
                            category="PARABOLA_EXTREMA_ORIENTATION",
                            description="Başkatsayı a > 0 olduğunda parabol kolları yukarı bakar ve tepe noktası minimumdur; maksimum değildir.",
                            remediation_directive="Kolları yukarı bakan bir çanağın en dip noktasının en küçük değer (minimum) olduğunu canlandır.",
                            offending_term=user_str,
                        )
                elif a_val < 0:
                    if "minimum" in clean_u or "en küçük" in clean_u:
                        return DiagnosticPayload(
                            bug_id="BUG-PARAB-05",
                            severity="CRITICAL",
                            category="PARABOLA_EXTREMA_ORIENTATION",
                            description="Başkatsayı a < 0 olduğunda parabol kolları aşağı bakar ve tepe noktası maksimumdur; minimum değildir.",
                            remediation_directive="Kolları aşağı bakan bir tepenin zirvesinin en büyük değer (maksimum) olduğunu canlandır.",
                            offending_term=user_str,
                        )
        except Exception:
            pass
        return None

    def _check_bug_poly_01(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-POLY-01: Polinom Kalan Teoreminde Bölen Kökünün İşaretini Ters Alma (P(x) / (x-a) için P(-a) alma).
        """
        clean_u = user_str.replace(" ", "")
        clean_p = prev_str.replace(" ", "")
        match_div = re.search(r"\(x([+-]\d+)\)", clean_p)
        if match_div:
            offset = int(match_div.group(1))
            true_root = -offset
            buggy_root = offset
            if f"P({buggy_root})" in clean_u and f"P({true_root})" not in clean_u:
                return DiagnosticPayload(
                    bug_id="BUG-POLY-01",
                    severity="CRITICAL",
                    category="POLYNOMIAL_REMAINDER_SIGN",
                    description=f"Kalan teoreminde bölen sıfıra eşitlenmelidir (x {'+' if offset >= 0 else ''}{offset} = 0 => x = {true_root}); P({buggy_root}) yerine P({true_root}) hesaplanmalıdır.",
                    remediation_directive="Bölen ifadeyi sıfıra eşitleyen denklemi açıkça çözdürerek kökün işaretini doğrulamasını sağla.",
                    offending_term=user_str,
                )
        return None

    def _check_bug_poly_02(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-POLY-02: Katsayılar Toplamı ve Sabit Terim Kargaşası (Katsayılar toplamı için x=0 veya sabit terim için x=1).
        """
        clean_u = user_str.lower()
        if "katsayılar toplamı" in clean_u or "katsayı toplamı" in clean_u:
            if "x = 0" in clean_u or "x=0" in clean_u or "p(0)" in clean_u:
                return DiagnosticPayload(
                    bug_id="BUG-POLY-02",
                    severity="CRITICAL",
                    category="POLYNOMIAL_COEFFS_VS_CONSTANT",
                    description="Katsayılar toplamı için x = 1 yazılmalıdır; x = 0 sabit terimi verir.",
                    remediation_directive="P(x) = a*x + b polinomunda x yerine 1 koyduğumuzda a+b'nin (katsayılar toplamının) nasıl kaldığını göster.",
                    offending_term=user_str,
                )
        if "sabit terim" in clean_u:
            if "x = 1" in clean_u or "x=1" in clean_u or "p(1)" in clean_u:
                return DiagnosticPayload(
                    bug_id="BUG-POLY-02",
                    severity="CRITICAL",
                    category="POLYNOMIAL_COEFFS_VS_CONSTANT",
                    description="Sabit terim için x = 0 yazılmalıdır; x = 1 katsayılar toplamını verir.",
                    remediation_directive="x=0 konulduğunda x'e bağlı tüm değişken terimlerin sıfırlanıp sadece sabit terimin kaldığını hatırlat.",
                    offending_term=user_str,
                )
        return None

    def _check_bug_poly_03(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-POLY-03: Polinom Bölmesinde Derece Kuralı İhlali (der(Kalan) >= der(Bölen)).
        """
        clean_u = user_str.lower()
        clean_p = prev_str.lower()
        try:
            match_deg_b = (
                re.search(r"der\(b.*len\)\s*=\s*(\d+)", clean_p)
                or re.search(r"der\(b\)\s*=\s*(\d+)", clean_p)
                or re.search(r"b.*len derecesi\s*=\s*(\d+)", clean_p)
            )
            match_deg_k = (
                re.search(r"der\(kalan\)\s*=\s*(\d+)", clean_u)
                or re.search(r"der\(k\)\s*=\s*(\d+)", clean_u)
                or re.search(r"kalan derecesi\s*=\s*(\d+)", clean_u)
            )
            if match_deg_b and match_deg_k:
                deg_b = int(match_deg_b.group(1))
                deg_k = int(match_deg_k.group(1))
                if deg_k >= deg_b:
                    return DiagnosticPayload(
                        bug_id="BUG-POLY-03",
                        severity="CRITICAL",
                        category="POLYNOMIAL_REMAINDER_DEGREE_VIOLATION",
                        description=f"Kalanın derecesi ({deg_k}) bölenin derecesinden ({deg_b}) küçük olmalıdır; der(Kalan) < der(Bölen) kuralı ihlal edildi.",
                        remediation_directive="Kalanın derecesi bölenin derecesinden küçük olana kadar bölme işleminin devam etmesi gerektiğini sorgula.",
                        offending_term=user_str,
                    )
            if "kalan=" in clean_u.replace(" ", ""):
                kalan_str = user_str.split("=")[1].strip()
                k_expr = self.cas.parse_to_sympy(kalan_str)
                k_poly = sp.Poly(k_expr, self.x)
                if "x-" in clean_p or "x+" in clean_p or "derecesi 1" in clean_p or "der(b)=1" in clean_p:
                    if k_poly.degree() >= 1:
                        return DiagnosticPayload(
                            bug_id="BUG-POLY-03",
                            severity="CRITICAL",
                            category="POLYNOMIAL_REMAINDER_DEGREE_VIOLATION",
                            description="Bölen 1. dereceden iken kalan x'e bağlı olamaz (sabit bir sayı olmalıdır, der(K) = 0).",
                            remediation_directive="1. dereceden bir bölende kalanın neden sadece bir sabit reel sayı olması gerektiğini hatırlat.",
                            offending_term=user_str,
                        )
        except Exception:
            pass
        return None

    def _check_bug_poly_04(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-POLY-04: Polinom Derece Aritmetiğinde Çarpım/Kuvvet Yanılgısı (der(P*Q) = der(P) * der(Q)).
        """
        clean_u = user_str.lower().replace(" ", "")
        if "der(p*q)=der(p)*der(q)" in clean_u or "deg(p*q)=deg(p)*deg(q)" in clean_u:
            return DiagnosticPayload(
                bug_id="BUG-POLY-04",
                severity="CRITICAL",
                category="POLYNOMIAL_DEGREE_ARITHMETIC",
                description="Polinomların çarpımının derecesi derecelerin toplamıdır; dereceler birbiriyle çarpılmaz.",
                remediation_directive="x^2 ile x^3 çarpıldığında üslerin neden toplandığını (x^5) sorgulat.",
                offending_term=user_str,
            )
        match_p = re.search(r"der\(p\)\s*=\s*(\d+)", prev_str.lower())
        match_q = re.search(r"der\(q\)\s*=\s*(\d+)", prev_str.lower())
        if match_p and match_q:
            dp, dq = int(match_p.group(1)), int(match_q.group(1))
            true_deg = dp + dq
            mult_deg = dp * dq
            if mult_deg != true_deg:
                match_user = re.search(r"der\(p\*q\)\s*=\s*(\d+)", clean_u) or re.search(r"der\(p\.q\)\s*=\s*(\d+)", clean_u)
                if match_user and int(match_user.group(1)) == mult_deg:
                    return DiagnosticPayload(
                        bug_id="BUG-POLY-04",
                        severity="CRITICAL",
                        category="POLYNOMIAL_DEGREE_ARITHMETIC",
                        description=f"Polinom çarpımının derecesi dereceler toplamıdır ({dp} + {dq} = {true_deg}); dereceler çarpılarak {mult_deg} bulundu.",
                        remediation_directive="x^a * x^b = x^(a+b) üslü sayı özelliğini hatırlatan Sokratik bir soru sor.",
                        offending_term=user_str,
                    )
        return None

    def _check_bug_poly_05(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-POLY-05: Polinom Bölmesinde Bölen Kökünü Doğrudan Kalana Eşitleme (K = a sanma).
        """
        clean_u = user_str.lower().replace(" ", "")
        clean_p = prev_str.lower().replace(" ", "")
        match_div = re.search(r"\(x([+-]\d+)\)", clean_p)
        if match_div:
            offset = int(match_div.group(1))
            root_val = -offset
            match_k = re.search(r"kalan\s*=\s*([+-]?\d+)", user_str.lower()) or re.search(r"\bk\s*=\s*([+-]?\d+)", user_str.lower())
            if match_k:
                k_val = int(match_k.group(1))
                if k_val == root_val and f"p({root_val})" not in clean_u:
                    return DiagnosticPayload(
                        bug_id="BUG-POLY-05",
                        severity="CRITICAL",
                        category="POLYNOMIAL_FALSE_REMAINDER_ASSIGNMENT",
                        description=f"Bölenin kökü x = {root_val} doğrudan kalan demek değildir; kalan P({root_val}) polinom değeridir.",
                        remediation_directive="Bölme eşitliğinde x yerine kök yazıldığında kalan teriminin P(kök) değerine eşit olduğunu hatırlat.",
                        offending_term=user_str,
                    )
        return None

    def _check_bug_trig_01(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-TRIG-01: Trigonometrik Lineerlik Tuzağı (sin(a+b) = sin a + sin b sanma).
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")

        if (
            "sin(a+b)=sin(a)+sin(b)" in clean_u
            or "sin(x+y)=sin(x)+sin(y)" in clean_u
            or "cos(a+b)=cos(a)+cos(b)" in clean_u
            or "cos(a-b)=cos(a)-cos(b)" in clean_u
            or "cos(x+y)=cos(x)+cos(y)" in clean_u
            or "cos(x-y)=cos(x)-cos(y)" in clean_u
            or "tan(a+b)=tan(a)+tan(b)" in clean_u
            or "tan(x+y)=tan(x)+tan(y)" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-TRIG-01",
                severity="CRITICAL",
                category="TRIG_LINEARITY_TRAP",
                description="Trigonometrik fonksiyonlar parantez içine çarpma gibi dağıtılamaz: sin(a+b) != sin(a) + sin(b).",
                remediation_directive="Toplam-fark formüllerini hatırlat: sin(a+b) = sin(a)cos(b) + cos(a)sin(b).",
                offending_term=user_str,
            )

        m_sin = re.search(r"sin\(([a-zA-Z0-9]+)\+([a-zA-Z0-9]+)\)", clean_p)
        if m_sin:
            u_linear = f"sin({m_sin.group(1)})+sin({m_sin.group(2)})"
            if u_linear in clean_u:
                return DiagnosticPayload(
                    bug_id="BUG-TRIG-01",
                    severity="CRITICAL",
                    category="TRIG_LINEARITY_TRAP",
                    description=f"sin({m_sin.group(1)}+{m_sin.group(2)}) ifadesi sin({m_sin.group(1)}) + sin({m_sin.group(2)}) şeklinde açılamaz.",
                    remediation_directive="Toplam formülünü açtır: sin(x+y) = sin(x)cos(y) + cos(x)sin(y).",
                    offending_term=user_str,
                )
        return None

    def _check_bug_trig_02(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-TRIG-02: Fonksiyon İsim ve Argüman Sadeleştirme Hatası (sin(2x) = 2sin(x) veya sin(2x)/sin(x) = 2).
        """
        clean_u = user_str.lower().replace(" ", "")
        clean_p = prev_str.lower().replace(" ", "")

        if (
            (("sin(2x)=2sin(x)" in clean_u or "sin(2*x)=2*sin(x)" in clean_u) and "cos" not in clean_u)
            or "sin(2x)/sin(x)=2" in clean_u
            or "sin(2*x)/sin(x)=2" in clean_u
            or "cos(2x)=2cos(x)" in clean_u
            or "tan(2x)=2tan(x)" in clean_u
            or "sin(x)/x=sin" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-TRIG-02",
                severity="CRITICAL",
                category="TRIG_ARGUMENT_CANCELLATION_ERROR",
                description="Fonksiyonun içindeki açı katsayısı dışarı çarpan olarak çıkarılamaz veya fonksiyon adı sadeleştirilemez.",
                remediation_directive="Yarım açı formülünü uygulat: sin(2x) = 2*sin(x)*cos(x).",
                offending_term=user_str,
            )

        if ("sin(2x)" in clean_p or "sin(2*x)" in clean_p) and ("2*sin(x)" in clean_u or "2sin(x)" in clean_u) and "cos" not in clean_u:
            return DiagnosticPayload(
                bug_id="BUG-TRIG-02",
                severity="CRITICAL",
                category="TRIG_ARGUMENT_CANCELLATION_ERROR",
                description="sin(2x) açılımında açı katsayısı 2 dışarı çıkarıldı; yarım açı formülündeki cos(x) çarpanı unutuldu.",
                remediation_directive="İki kat açı özdeşliğini uygulat: sin(2x) = 2*sin(x)*cos(x).",
                offending_term=user_str,
            )
        return None

    def _check_bug_trig_03(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-TRIG-03: Birim Çember Eksen Karışıklığı (x eksenini sin, y eksenini cos sanma veya tan = cos/sin).
        """
        clean_u = user_str.lower().replace(" ", "")

        if (
            "tan(x)=cos(x)/sin(x)" in clean_u
            or "tan=cos/sin" in clean_u
            or "cot(x)=sin(x)/cos(x)" in clean_u
            or "cot=sin/cos" in clean_u
            or "(sin,cos)" in clean_u
            or "(sin(theta),cos(theta))" in clean_u
            or "(sin(x),cos(x))" in clean_u
            or ("x=sin" in clean_u and "y=cos" in clean_u)
            or "apsissin" in clean_u
            or "ordinatcos" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-TRIG-03",
                severity="CRITICAL",
                category="UNIT_CIRCLE_AXIS_CONFUSION",
                description="Birim çemberde yatay eksen (apsis, x) kosinüs, düşey eksen (ordinat, y) sinüstür.",
                remediation_directive="Birim çemberde P(theta) = (cos(theta), sin(theta)) ve tan = sin/cos olduğunu hatırlat.",
                offending_term=user_str,
            )
        return None

    def _check_bug_trig_04(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-TRIG-04: Trigonometrik Denklemde Kök/Periyot Kaybı.
        """
        clean_u = user_str.lower().replace(" ", "")
        clean_p = prev_str.lower().replace(" ", "")

        # Sadeleştirmede kök silme: sin(x)*cos(x) = sin(x) => cos(x) = 1 veya tan(x)*sin(x) = sin(x) => tan(x) = 1
        if (
            ("sin(x)*cos(x)=sin(x)" in clean_p or "sin(x)cos(x)=sin(x)" in clean_p
             or "tan(x)*sin(x)=sin(x)" in clean_p or "tan(x)sin(x)=sin(x)" in clean_p)
            and ("cos(x)=1" in clean_u or "tan(x)=1" in clean_u)
            and ("sin(x)=0" not in clean_u and "sin=0" not in clean_u)
        ):
            return DiagnosticPayload(
                bug_id="BUG-TRIG-04",
                severity="CRITICAL",
                category="TRIG_EQUATION_ROOT_PERIOD_LOSS",
                description="Her iki tarafı sin(x)'e bölerken sin(x) = 0 yapan kök ailesi kaybedildi.",
                remediation_directive="İfadeleri tek tarafa toplayıp ortak paranteze al: sin(x)(cos(x) - 1) = 0.",
                offending_term=user_str,
            )

        # Tek açı çözümü verip ikinci bölgeyi veya periyodu yazmama: sin(x) = 1/2 => x = 30
        if (
            ("sin(x)=1/2" in clean_p or "sin(x)=0.5" in clean_p)
            and ("x=30" in clean_u or "x=pi/6" in clean_u)
            and ("150" not in clean_u and "5pi/6" not in clean_u and "2k" not in clean_u and "k*pi" not in clean_u)
        ):
            return DiagnosticPayload(
                bug_id="BUG-TRIG-04",
                severity="CRITICAL",
                category="TRIG_EQUATION_ROOT_PERIOD_LOSS",
                description="sin(x) = 1/2 denkleminin [0, 2pi) aralığında 150 derece (5pi/6) kökü ve genel çözüm periyodu unutuldu.",
                remediation_directive="Sinüsün 2. bölgede de pozitif olduğunu ve x = pi - alpha kökünü hatırlat.",
                offending_term=user_str,
            )
        return None

    def _check_bug_trig_05(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-TRIG-05: Negatif Açı ve Parite Yanılgısı (cos(-x) = -cos(x) sanma).
        """
        clean_u = user_str.lower().replace(" ", "")

        if (
            "cos(-x)=-cos(x)" in clean_u
            or "cos(-theta)=-cos(theta)" in clean_u
            or "cos(-a)=-cos(a)" in clean_u
            or "sin(-x)=sin(x)" in clean_u
            or "sin(-theta)=sin(theta)" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-TRIG-05",
                severity="CRITICAL",
                category="TRIG_PARITY_AND_NEGATIVE_ANGLE_CONFUSION",
                description="Kosinüs çift fonksiyondur (cos(-x) = cos(x)), eksiyi dışarı atmaz; sinüs ise tek fonksiyondur (sin(-x) = -sin(x)).",
                remediation_directive="4. bölgede kosinüsün işaretini (+ olduğunu) birim çember üzerinde sorgulat.",
                offending_term=user_str,
            )
        return None

    def _check_bug_log_01(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-LOG-01: Logaritma Toplam-Dağılma Tuzağı (log(a+b) = log a + log b).
        """
        clean_u = user_str.lower().replace(" ", "")
        clean_p = prev_str.lower().replace(" ", "")

        if (
            "log(a+b)=log(a)+log(b)" in clean_u
            or "log(x+y)=log(x)+log(y)" in clean_u
            or "ln(a+b)=ln(a)+ln(b)" in clean_u
            or "ln(x+y)=ln(x)+ln(y)" in clean_u
            or "log(a-b)=log(a)-log(b)" in clean_u
            or "log(a-b)=log(a)/log(b)" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-LOG-01",
                severity="CRITICAL",
                category="LOG_ADDITION_DISTRIBUTION_TRAP",
                description="Logaritma parantez içine dağıtılamaz: log(a+b) != log(a) + log(b).",
                remediation_directive="Logaritmanın çarpımı toplama dönüştürdüğünü (log(ab) = log a + log b) hatırlat.",
                offending_term=user_str,
            )

        if ("log(x+y)" in clean_p or "log(a+b)" in clean_p) and ("log(x)+log(y)" in clean_u or "log(a)+log(b)" in clean_u):
            return DiagnosticPayload(
                bug_id="BUG-LOG-01",
                severity="CRITICAL",
                category="LOG_ADDITION_DISTRIBUTION_TRAP",
                description="İçerideki toplama işlemi logaritmaların toplamı olarak açılamaz.",
                remediation_directive="log(a) + log(b) ifadesinin log(a*b) olduğunu göster.",
                offending_term=user_str,
            )
        return None

    def _check_bug_log_02(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-LOG-02: Logaritma Çarpım/Kuvvet Karışıklığı (log(ab) = log a * log b veya (log x)^2 = 2log x).
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")

        if (
            "log(a*b)=log(a)*log(b)" in clean_u
            or "log(ab)=log(a)*log(b)" in clean_u
            or "ln(ab)=ln(a)*ln(b)" in clean_u
            or "log(a.b)=log(a).log(b)" in clean_u
            or "(log(x))^2=2*log(x)" in clean_u
            or "(log(x))^2=2log(x)" in clean_u
            or "log(x^2)=(log(x))^2" in clean_u
            or "(ln(x))^2=2ln(x)" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-LOG-02",
                severity="CRITICAL",
                category="LOG_MULTIPLICATION_POWER_CONFUSION",
                description="Logaritmada çarpımın logaritması logaritmaların toplamıdır (çarpımı değil); kuvvet kuralı log(x^2) = 2*log(x)'tir, (log x)^2 değildir.",
                remediation_directive="a^m * a^n = a^(m+n) üslü kuralı ile log(ab) = log a + log b ilişkisini kurdur.",
                offending_term=user_str,
            )
        return None

    def _check_bug_log_03(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-LOG-03: Negatif Tanım Kümesi İhmali / Sahte Kök (Extraneous Root).
        """
        clean_p = prev_str.lower()
        if "log" in clean_p or "ln" in clean_p:
            matches = re.findall(r"(?:x\s*=\s*|ç\s*=\s*\{|,\s*)([+-]?\d+(?:\.\d+)?)", user_str.lower())
            for m in matches:
                try:
                    val = float(m)
                    # Denklemin sol ve sağ tarafını kısıtlar açısından incele
                    is_valid, reason = self.cas.evaluate_domain_constraints(prev_str, variable="x", candidate_val=val)
                    if not is_valid:
                        return DiagnosticPayload(
                            bug_id="BUG-LOG-03",
                            severity="CRITICAL",
                            category="LOG_EXTRANEOUS_ROOT_DOMAIN_VIOLATION",
                            description=f"Logaritma argümanı pozitif olmak zorundadır. Bulunan x = {val} kökü orijinal denklemi tanımsız/negatif yapmaktadır ({reason}).",
                            remediation_directive="Bulunan köklerin logaritmanın tanım kümesi kısıtlarını sağlayıp sağlamadığını kontrol etmesini iste.",
                            offending_term=user_str,
                        )
                except Exception:
                    pass
        return None

    def _check_bug_log_04(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-LOG-04: Taban Değiştirme ve Bölme Hatası (log a / log b = log(a/b) sanma).
        """
        clean_u = user_str.lower().replace(" ", "")

        if (
            "log(a)/log(b)=log(a/b)" in clean_u
            or "log(a)/log(b)=log(a-b)" in clean_u
            or "ln(a)/ln(b)=ln(a/b)" in clean_u
            or "ln(a)/ln(b)=ln(a-b)" in clean_u
            or "log(x)/log(y)=log(x/y)" in clean_u
            or "log(x)/log(y)=log(x-y)" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-LOG-04",
                severity="CRITICAL",
                category="LOG_CHANGE_OF_BASE_DIVISION_ERROR",
                description="log(a)/log(b) oranı log(a/b) değil, taban değiştirme kuralı uyarınca log_b(a)'dır. log(a/b) ise log(a) - log(b)'ye eşittir.",
                remediation_directive="Bölümün logaritması ile logaritmaların oranını birbirinden ayırt ettir.",
                offending_term=user_str,
            )
        return None

    def _check_bug_log_05(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-LOG-05: Üstel/Logaritma Taban ve Kuvvet Karışıklığı (log_a(b) = c => b = c^a sanma).
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")

        if (
            "8=3^2" in clean_u
            or "b=c^a" in clean_u
            or "a=b^c" in clean_u
            or "b=c**a" in clean_u
            or "a=b**c" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-LOG-05",
                severity="CRITICAL",
                category="LOG_BASE_EXPONENT_INVERSION_ERROR",
                description="log_a(b) = c eşitliğinde taban a yerinde kalır ve b = a^c olur; taban ile üs yer değiştirilemez (b != c^a).",
                remediation_directive="Logaritmanın üstel fonksiyonun tersi olduğunu ve tabanın daima altta kaldığını hatırlat.",
                offending_term=user_str,
            )
        return None

    def _check_bug_calc_01(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-CALC-01: Zincir Kuralında İç Türevi Unutma ([f(g(x))]' = f'(g(x))).
        Örnek: d/dx(sin(2x)) = cos(2x) veya d/dx((3x+1)^4) = 4*(3x+1)^3.
        """
        clean_u = user_str.lower().replace(" ", "")
        clean_p = prev_str.lower().replace(" ", "")

        # 1. Trigonometrik iç türev kaybı: sin(k*x) -> cos(k*x), cos(k*x) -> -sin(k*x) (k != 1)
        if (
            "cos(2*x)" in clean_u or "cos(2x)" in clean_u or "cos(3*x)" in clean_u
        ) and ("sin(2*x)" in clean_p or "sin(2x)" in clean_p or "sin(3*x)" in clean_p):
            if not ("2*cos" in clean_u or "2cos" in clean_u or "3*cos" in clean_u or "*2" in clean_u or "*3" in clean_u):
                return DiagnosticPayload(
                    bug_id="BUG-CALC-01",
                    severity="CRITICAL",
                    category="CALCULUS_CHAIN_RULE_MISSING_INNER_DERIVATIVE",
                    description="Bileşke fonksiyonun türevinde iç türev kuralı unutulmuştur: d/dx[sin(2x)] = 2*cos(2x) olmalıdır, cos(2x) değil.",
                    remediation_directive="Bileşke fonksiyonlarda zincir kuralını uygula: [f(g(x))]' = f'(g(x)) * g'(x). İçteki g(x) ifadesinin türevini çarpan olarak ekle.",
                    offending_term=user_str,
                )

        # 2. Polinom kuvveti iç türev kaybı: (3x+1)^4 -> 4*(3x+1)^3 (iç türev 3 eksik)
        if (
            "4*(3*x+1)**3" in clean_u
            or "4*(3x+1)**3" in clean_u
            or "4*(3*x+1)^3" in clean_u
            or "3*(2*x+5)**2" in clean_u
            or "3*(2x+5)**2" in clean_u
        ):
            has_inner_mult = bool(
                "12*" in clean_u or "6*" in clean_u
                or re.search(r"(?<!\*)\*\s*[23]\b", clean_u)
            )
            if not has_inner_mult:
                return DiagnosticPayload(
                    bug_id="BUG-CALC-01",
                    severity="CRITICAL",
                    category="CALCULUS_CHAIN_RULE_MISSING_INNER_DERIVATIVE",
                    description="Kuvvet zincir kuralında iç fonksiyonun türevi çarpılmamıştır: [(3x+1)^4]' = 4*(3x+1)^3 * 3 = 12*(3x+1)^3 olmalıdır.",
                    remediation_directive="İç türevi (tabandaki fonksiyonun türevi) daima dış türevle çarpmayı unutma.",
                    offending_term=user_str,
                )

        # 3. Üstel fonksiyon iç türev kaybı: e^(2x) -> e^(2x) (2 çarpanı eksik)
        if ("e**(2*x)" in clean_u or "exp(2*x)" in clean_u or "e^(2x)" in clean_u) and ("e**(2*x)" in clean_p or "exp(2*x)" in clean_p or "e^(2x)" in clean_p):
            if ("diff" in clean_p or "turev" in clean_p or "'" in clean_p) and not ("2*" in clean_u or "*2" in clean_u):
                return DiagnosticPayload(
                    bug_id="BUG-CALC-01",
                    severity="CRITICAL",
                    category="CALCULUS_CHAIN_RULE_MISSING_INNER_DERIVATIVE",
                    description="Doğal üstel fonksiyonda d/dx[e^(g(x))] = g'(x)*e^(g(x)) kuralı uygulanmalı, üssün türevi 2 unutulmamalıdır.",
                    remediation_directive="e^(u) türevinde üssün türevi olan u' ile çarpmayı hatırla.",
                    offending_term=user_str,
                )

        return None

    def _check_bug_calc_02(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-CALC-02: Bölümün Türevinde İşaret Hatası ((f'g + fg') / g^2 sanma).
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")

        if (
            "(f'*g+f*g')/g^2" in clean_u
            or "(u'*v+u*v')/v^2" in clean_u
            or "(f'g+fg')/g^2" in clean_u
            or "(u'v+uv')/v^2" in clean_u
            or "(1*(x-1)+(x+1)*1)/(x-1)^2" in clean_u
            or "(1*(x-1)+(x+1)*1)/(x-1)**2" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-CALC-02",
                severity="CRITICAL",
                category="CALCULUS_QUOTIENT_RULE_SIGN_ERROR",
                description="Bölümün türev kuralında pay kısmında eksi işareti olmalıdır: [f/g]' = (f'g - fg') / g^2. Çarpımın türeviyle karıştırıp artı koyma.",
                remediation_directive="Bölüm kuralı formülünü hatırla: Pay = (Payın türevi * Payda) - (Pay * Paydanın türevi).",
                offending_term=user_str,
            )
        return None

    def _check_bug_calc_03(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-CALC-03: 0/0 Belirsizliğini Tanımsız veya Sıfır İlan Etme (0/0 = 0 veya 0/0 = tanımsız sanma).
        """
        clean_u = user_str.lower().replace(" ", "")
        clean_p = prev_str.lower().replace(" ", "")

        if (
            "0/0=0" in clean_u
            or "0/0=tanimsiz" in clean_u
            or "0/0=undefined" in clean_u
            or clean_u in {"limit=0", "lim=0", "limit=tanimsiz", "lim=tanimsiz", "tanimsiz", "undefined"}
            and ("0/0" in clean_p or "(x**2-4)/(x-2)" in clean_p or "(x^2-4)/(x-2)" in clean_p or "sin(x)/x" in clean_p)
        ):
            return DiagnosticPayload(
                bug_id="BUG-CALC-03",
                severity="CRITICAL",
                category="CALCULUS_INDETERMINATE_FORM_FALLACY",
                description="0/0 ifadesi tanımsızlık değil, bir belirsizliktir (indeterminate form). Limit değeri 0 olmak zorunda değildir ve sonlu bir gerçel sayı çıkabilir.",
                remediation_directive="0/0 belirsizliğini gidermek için çarpanlara ayırma, eşlenikle çarpma veya L'Hôpital kuralını uygula.",
                offending_term=user_str,
            )
        return None

    def _check_bug_calc_04(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-CALC-04: f'(x)=0 Noktasını Kesin Ekstremum Sanma (Büküm Noktası İhmali).
        Örnek: f(x) = x^3 için f'(0) = 0 olmasına rağmen x=0 bir büküm noktasıdır, yerel ekstremum değildir.
        """
        clean_u = user_str.lower().replace(" ", "")

        if (
            "f'(0)=0oldugundanx=0yerel" in clean_u
            or "f'(x)=0iseyerelekstremum" in clean_u
            or "x=0yerelmaksimum" in clean_u and "x^3" in prev_str.lower()
            or "x=0yerelminimum" in clean_u and "x^3" in prev_str.lower()
            or "f'(c)=0olankesinlinekstremum" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-CALC-04",
                severity="CRITICAL",
                category="CALCULUS_CRITICAL_POINT_FALSE_EXTREMA",
                description="f'(c) = 0 olması ekstremum için zorunludur ancak yeterli değildir. f'(x)'in c noktasında işaret değiştirip değiştirmediği incelenmelidir (ör. f(x)=x^3 için x=0 büküm noktasıdır).",
                remediation_directive="Birinci türev işaret tablosu yaparak türevin işaretinin (+)'dan (-)'ye veya (-)'den (+)'ya değiştiğini teyit etmesini iste.",
                offending_term=user_str,
            )
        return None

    def _check_bug_calc_05(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-CALC-05: Çarpımın Türevinde Sahte Doğrusallık ((uv)' = u'v' sanma).
        Örnek: (x * sin(x))' = 1 * cos(x) = cos(x).
        """
        clean_u = user_str.lower().replace(" ", "")

        if (
            "(uv)'=u'v'" in clean_u
            or "(fg)'=f'g'" in clean_u
            or "(u*v)'=u'*v'" in clean_u
            or "(f*g)'=f'*g'" in clean_u
            or "1*cos(x)=cos(x)" in clean_u
            or "2*x*e**x" in clean_u and "x**2*e**x" in prev_str.lower()
        ):
            return DiagnosticPayload(
                bug_id="BUG-CALC-05",
                severity="CRITICAL",
                category="CALCULUS_PRODUCT_RULE_FALSE_LINEARITY",
                description="Türev çarpma üzerine dağılmaz! İki fonksiyonun çarpımının türevi: (f * g)' = f' * g + f * g' kuralıyla hesaplanır.",
                remediation_directive="Çarpımın türevi formülünü eksiksiz uygula: Birincinin türevi * İkinci + Birinci * İkincinin türevi.",
                offending_term=user_str,
            )
        return None

    def _check_bug_calc_06(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-CALC-06: Sabit Sayının Türevini Sıfır Yerine Kendisi Bırakma (d/dx(c) = c sanma).
        Örnek: (x^2 + 5)' = 2x + 5 veya (3x + 7)' = 3 + 7.
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")

        if (
            "2*x+5" in clean_u and "x^2+5" in clean_p
            or "2x+5" in clean_u and "x^2+5" in clean_p
            or "3+7" in clean_u and ("3*x+7" in clean_p or "3x+7" in clean_p)
            or "diff(5,x)=5" in clean_u
            or "d/dx(5)=5" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-CALC-06",
                severity="CRITICAL",
                category="CALCULUS_CONSTANT_DERIVATIVE_ERROR",
                description="Sabit bir sayının türevi kendisi değil, sıfırdır: d/dx(c) = 0. Örneğin (x^2 + 5)' = 2x + 0 = 2x olmalıdır.",
                remediation_directive="Sabit sayıların değişim hızı sıfır olduğu için türevlerinin 0 olduğunu hatırla.",
                offending_term=user_str,
            )
        return None

    def _check_bug_calc_07(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-CALC-07: Limiti Fonksiyon Değeriyle Özdeşleştirme Fallacy.
        Örnek: f(a) tanımsız olduğu için limitin de olmadığını iddia etme.
        """
        clean_u = user_str.lower().replace(" ", "")

        if (
            "f(a)tanimsizolduguicinlimityoktur" in clean_u
            or "f(a)tanimsiziselimityoktur" in clean_u
            or "f(2)tanimsizoldugundanlimityoktur" in clean_u
            or "f(c)tanimsizisepuntanimsizdir" in clean_u
            or "limf(x)=f(a)herzamandogrudur" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-CALC-07",
                severity="CRITICAL",
                category="CALCULUS_LIMIT_EQUALS_FUNCTION_VALUE_FALLACY",
                description="Limit, fonksiyonun o noktadaki tanımına bağlı değildir. Fonksiyon x = a noktasında tanımsız olsa bile sağ ve sol limitler eşitse fonksiyonun limiti vardır.",
                remediation_directive="Limit kavramının o noktaya 'yaklaşma' olduğunu, fonksiyon değeriyle (f(a)) aynı şey olmadığını kavrat.",
                offending_term=user_str,
            )
        return None

    def _check_bug_calc_08(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-CALC-08: Kosinüs Türevinde Eksi İşareti Hatası (d/dx(cos x) = sin x sanma).
        """
        clean_u = user_str.lower().replace(" ", "")

        if (
            "(cos(x))'=sin(x)" in clean_u
            or "cos'(x)=sin(x)" in clean_u
            or "diff(cos(x),x)=sin(x)" in clean_u
            or "d/dx(cos(x))=sin(x)" in clean_u
            or "cos(x)'=sin(x)" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-CALC-08",
                severity="CRITICAL",
                category="CALCULUS_COSINE_DERIVATIVE_SIGN_ERROR",
                description="d/dx[cos(x)] = -sin(x)'tir. Eksi işareti unutulmuştur.",
                remediation_directive="Kosinüs fonksiyonunun türevinde daima eksi işareti bulunduğunu hatırla: d/dx(cos x) = -sin(x).",
                offending_term=user_str,
            )
        return None

    def _check_bug_calc_09(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-CALC-09: L'Hôpital ile Bölüm Türevinin Karıştırılması ((f/g)' = f'/g' sanma).
        """
        clean_u = user_str.lower().replace(" ", "")

        if (
            "(f/g)'=f'/g'" in clean_u
            or "(u/v)'=u'/v'" in clean_u
            or "d/dx(f/g)=f'/g'" in clean_u
            or "cos(x)/1=cos(x)" in clean_u and "sin(x)/x" in prev_str.lower()
        ):
            return DiagnosticPayload(
                bug_id="BUG-CALC-09",
                severity="CRITICAL",
                category="CALCULUS_LHOPITAL_QUOTIENT_CONFUSION",
                description="L'Hôpital kuralı yalnızca 0/0 limit belirsizliklerinde limit hesaplarken kullanılır; fonksiyonun bölüm türevi (f/g)' alınırken uygulanamaz.",
                remediation_directive="Türev alma ile limit hesaplamayı ayır: Bölümün türevi için (f'g - fg')/g^2 kuralını uygula.",
                offending_term=user_str,
            )
        return None

    def _check_bug_calc_10(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-CALC-10: Teğet Doğrusu Eğimini Fonksiyon Değerine Eşitleme (m = f(x_0) sanma).
        """
        clean_u = user_str.lower().replace(" ", "")

        if (
            "m=f(x_0)" in clean_u
            or "m=f(x0)" in clean_u
            or "egim=f(x0)" in clean_u
            or "m=f(a)" in clean_u
            or "egim=f(a)" in clean_u
            or "egim=y0" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-CALC-10",
                severity="CRITICAL",
                category="CALCULUS_TANGENT_SLOPE_FUNCTION_VALUE_CONFUSION",
                description="Teğet doğrusunun eğimi (m), fonksiyonun o noktadaki değerine değil, birinci türevinin o noktadaki değerine eşittir: m = f'(x_0).",
                remediation_directive="Teğet eğimi için önce f'(x) türevini alıp ardından teğet noktasının apsisini (x_0) türevde yerine koy.",
                offending_term=user_str,
            )
        return None


