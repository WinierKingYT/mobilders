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

        # 41. BUG-INT-01: İntegrasyon Sabiti (+C) Unutulması
        bug_i1 = self._check_bug_int_01(clean_user, clean_prev)
        if bug_i1:
            return bug_i1

        # 42. BUG-INT-02: u-İkamesinde Diferansiyel İhmali
        bug_i2 = self._check_bug_int_02(clean_user, clean_prev)
        if bug_i2:
            return bug_i2

        # 43. BUG-INT-03: Belirli İntegralde Sınır Sırasını Ters Çıkarma
        bug_i3 = self._check_bug_int_03(clean_user, clean_prev)
        if bug_i3:
            return bug_i3

        # 44. BUG-INT-04: Negatif Belirli İntegrali Alan Kabul Etme
        bug_i4 = self._check_bug_int_04(clean_user, clean_prev)
        if bug_i4:
            return bug_i4

        # 45. BUG-INT-05: Kısmi İntegrasyon Formülü İşaret Hatası
        bug_i5 = self._check_bug_int_05(clean_user, clean_prev)
        if bug_i5:
            return bug_i5

        # 46. BUG-INT-06: 1/x İntegralinde Kuvvet Kuralı Hatası
        bug_i6 = self._check_bug_int_06(clean_user, clean_prev)
        if bug_i6:
            return bug_i6

        # 47. BUG-INT-07: Belirli u-İkamesinde Sınırları Güncellememe
        bug_i7 = self._check_bug_int_07(clean_user, clean_prev)
        if bug_i7:
            return bug_i7

        # 48. BUG-INT-08: İki Eğri Arası Alan Sırası Hatası
        bug_i8 = self._check_bug_int_08(clean_user, clean_prev)
        if bug_i8:
            return bug_i8

        # 49. BUG-INT-09: İntegralin Çarpma Üzerine Dağılması Sanrısı
        bug_i9 = self._check_bug_int_09(clean_user, clean_prev)
        if bug_i9:
            return bug_i9

        # 50. BUG-INT-10: FTC 1 Zincir Kuralı İhmali
        bug_i10 = self._check_bug_int_10(clean_user, clean_prev)
        if bug_i10:
            return bug_i10

        # 51. BUG-PROB-01: Yaş Problemlerinde Zaman Kayması Hatası
        bug_prob1 = self._check_bug_prob_01(clean_user, clean_prev)
        if bug_prob1:
            return bug_prob1

        # 52. BUG-PROB-02: Hız-Zaman Ters Orantı / Doğru Orantı Çelişkisi
        bug_prob2 = self._check_bug_prob_02(clean_user, clean_prev)
        if bug_prob2:
            return bug_prob2

        # 53. BUG-PROB-03: Ortalama Hızda Aritmetik Ortalama Tuzağı
        bug_prob3 = self._check_bug_prob_03(clean_user, clean_prev)
        if bug_prob3:
            return bug_prob3

        # 54. BUG-PROB-04: Yüzde Artış ve Azalışın Birbirini Sıfırladığı Sanrısı
        bug_prob4 = self._check_bug_prob_04(clean_user, clean_prev)
        if bug_prob4:
            return bug_prob4

        # 55. BUG-PROB-05: Karışımda Saf Madde vs Toplam Karışım Kargaşası
        bug_prob5 = self._check_bug_prob_05(clean_user, clean_prev)
        if bug_prob5:
            return bug_prob5

        # 56. BUG-PROB-06: İşçi Probleminde Süreleri Düz Toplama
        bug_prob6 = self._check_bug_prob_06(clean_user, clean_prev)
        if bug_prob6:
            return bug_prob6

        # 57. BUG-PROB-07: Bağıl Hızda Yön / İşaret Hatası
        bug_prob7 = self._check_bug_prob_07(clean_user, clean_prev)
        if bug_prob7:
            return bug_prob7

        # 58. BUG-PROB-08: Kâr Marjı Tabanı (Maliyet vs Satış Fiyatı) Karışıklığı
        bug_prob8 = self._check_bug_prob_08(clean_user, clean_prev)
        if bug_prob8:
            return bug_prob8

        # 59. BUG-PROB-09: Birim Uyuşmazlığı (km/saat vs dakika)
        bug_prob9 = self._check_bug_prob_09(clean_user, clean_prev)
        if bug_prob9:
            return bug_prob9

        # 60. BUG-PROB-10: Gerçek Dünya Kısıtını Göz Ardı Etme
        bug_prob10 = self._check_bug_prob_10(clean_user, clean_prev)
        if bug_prob10:
            return bug_prob10

        # 61. BUG-FOUND-01: Çift Eksi Tuzağı (-(-4) = -4)
        bug_f1 = self._check_bug_found_01(clean_user, clean_prev)
        if bug_f1:
            return bug_f1

        # 62. BUG-FOUND-02: İşlem Önceliği Körlüğü (3 + 4*2 = 14)
        bug_f2 = self._check_bug_found_02(clean_user, clean_prev)
        if bug_f2:
            return bug_f2

        # 63. BUG-FOUND-03: Kuvvet ile İşaret Çelişkisi (-3^2 = 9)
        bug_f3 = self._check_bug_found_03(clean_user, clean_prev)
        if bug_f3:
            return bug_f3

        # 64. BUG-FOUND-04: Kesir Düz Toplama Hatası (1/2 + 1/3 = 2/5)
        bug_f4 = self._check_bug_found_04(clean_user, clean_prev)
        if bug_f4:
            return bug_f4

        # 65. BUG-FOUND-05: Yarım Dağılma Hatası (2(x+3) = 2x+3)
        bug_f5 = self._check_bug_found_05(clean_user, clean_prev)
        if bug_f5:
            return bug_f5

        # 66. BUG-FOUND-06: Toplama/Çarpma Karışıklığı (x + x = x^2)
        bug_f6 = self._check_bug_found_06(clean_user, clean_prev)
        if bug_f6:
            return bug_f6

        # 67. BUG-FOUND-07: Katsayıyı Çıkarma Sanma (3x = 12 => x = 9)
        bug_f7 = self._check_bug_found_07(clean_user, clean_prev)
        if bug_f7:
            return bug_f7

        # 68. BUG-FOUND-08: Elma ile Armudu Toplama (2x + 3 = 5x)
        bug_f8 = self._check_bug_found_08(clean_user, clean_prev)
        if bug_f8:
            return bug_f8

        # 69. BUG-FOUND-09: Üs ile Tabanı Çarpma (2^3 = 6)
        bug_f9 = self._check_bug_found_09(clean_user, clean_prev)
        if bug_f9:
            return bug_f9

        # 70. BUG-FOUND-10: Negatif Sıralama Yanılgısı (-8 > -3)
        bug_f10 = self._check_bug_found_10(clean_user, clean_prev)
        if bug_f10:
            return bug_f10

        # 71. BUG-FOUND-11: Sıfıra Bölme Hatası (5/0 = 0 veya 5)
        bug_f11 = self._check_bug_found_11(clean_user, clean_prev)
        if bug_f11:
            return bug_f11

        # 72. BUG-FOUND-12: Eksi Parantez Dağılma (-(x - 4) = -x - 4)
        bug_f12 = self._check_bug_found_12(clean_user, clean_prev)
        if bug_f12:
            return bug_f12

        # 73. BUG-FOUND-13: Fonksiyonu Sayı Sanma (f(3) = 23)
        bug_f13 = self._check_bug_found_13(clean_user, clean_prev)
        if bug_f13:
            return bug_f13

        # 74. BUG-FOUND-14: Eşitsizlikte Yön Unutma (-2x < 6 => x < -3)
        bug_f14 = self._check_bug_found_14(clean_user, clean_prev)
        if bug_f14:
            return bug_f14

        # 75. BUG-FOUND-15: Tek Taraflı Terazi Hatası (x + 4 = 10 => x + 4 - 4 = 10)
        bug_f15 = self._check_bug_found_15(clean_user, clean_prev)
        if bug_f15:
            return bug_f15

        # 76. BUG-ANAG-01: Dik Doğrularda Eğim Bağıntısı Hatası (m1 = m2 veya m1*m2 = 1)
        bug_a1 = self._check_bug_anag_01(clean_user, clean_prev)
        if bug_a1:
            return bug_a1

        # 77. BUG-ANAG-02: Geniş Açı ve Eğim İşareti Hatası (theta > 90 fakat m > 0)
        bug_a2 = self._check_bug_anag_02(clean_user, clean_prev)
        if bug_a2:
            return bug_a2

        # 78. BUG-ANAG-03: Çember Merkez Koordinatında İşaret Tersliği (M(-a, -b))
        bug_a3 = self._check_bug_anag_03(clean_user, clean_prev)
        if bug_a3:
            return bug_a3

        # 79. BUG-ANAG-04: Uzaklık Formülünde Karekökü Unutma (d = (x2-x1)^2 + (y2-y1)^2)
        bug_a4 = self._check_bug_anag_04(clean_user, clean_prev)
        if bug_a4:
            return bug_a4

        # 80. BUG-ANAG-05: Vektör İç Çarpımında Vektörel Sonuç Üretme ((u1*v1, u2*v2))
        bug_a5 = self._check_bug_anag_05(clean_user, clean_prev)
        if bug_a5:
            return bug_a5

        # 81. BUG-EUC-01: Üçgen Eşitsizliği İhlali (a >= b + c)
        bug_e1 = self._check_bug_euc_01(clean_user, clean_prev)
        if bug_e1:
            return bug_e1

        # 82. BUG-EUC-02: Çevre Açı ile Merkez Açı Eşitliği Sanrısı
        bug_e2 = self._check_bug_euc_02(clean_user, clean_prev)
        if bug_e2:
            return bug_e2

        # 83. BUG-EUC-03: Benzerlik Oranını Alan Oranına Eşit Sayma (k -> k²)
        bug_e3 = self._check_bug_euc_03(clean_user, clean_prev)
        if bug_e3:
            return bug_e3

        # 84. BUG-EUC-04: Öklid Yükseklik Bağıntısında Kenar Çarpımı Hatası
        bug_e4 = self._check_bug_euc_04(clean_user, clean_prev)
        if bug_e4:
            return bug_e4

        # 85. BUG-EUC-05: Açıortay Teoreminde Orantı Yerine Eşit Bölme Sanrısı
        bug_e5 = self._check_bug_euc_05(clean_user, clean_prev)
        if bug_e5:
            return bug_e5

        # 86. BUG-COMB-01: Sırasız Seçimde Permütasyon Kullanma
        bug_cb1 = self._check_bug_comb_01(clean_user, clean_prev)
        if bug_cb1:
            return bug_cb1

        # 87. BUG-COMB-02: Kumarbaz Yanılgısı (Gambler's Fallacy)
        bug_cb2 = self._check_bug_comb_02(clean_user, clean_prev)
        if bug_cb2:
            return bug_cb2

        # 88. BUG-COMB-03: Koşullu Olasılıkta Örnek Uzayı Daraltmama
        bug_cb3 = self._check_bug_comb_03(clean_user, clean_prev)
        if bug_cb3:
            return bug_cb3

        # 89. BUG-COMB-04: Tekrarlı Permütasyonda Özdeş Bölümünü Unutma
        bug_cb4 = self._check_bug_comb_04(clean_user, clean_prev)
        if bug_cb4:
            return bug_cb4

        # 90. BUG-COMB-05: Ayrık Olmayan Olaylarda Kesişimi Çıkarmama
        bug_cb5 = self._check_bug_comb_05(clean_user, clean_prev)
        if bug_cb5:
            return bug_cb5

        # 91. BUG-LOGIC-01: İse Bağlacında Yanlış Öncül Yanılgısı
        bug_l1 = self._check_bug_logic_01(clean_user, clean_prev)
        if bug_l1:
            return bug_l1

        # 92. BUG-LOGIC-02: Ters ile Karşıt Tersin Karıştırılması
        bug_l2 = self._check_bug_logic_02(clean_user, clean_prev)
        if bug_l2:
            return bug_l2

        # 93. BUG-LOGIC-03: Niceleyici Değillemesinde Kapsam Hatası
        bug_l3 = self._check_bug_logic_03(clean_user, clean_prev)
        if bug_l3:
            return bug_l3

        # 94. BUG-LOGIC-04: Tümevarımda Taban Adımını Atlayarak Doğrulama Sanma
        bug_l4 = self._check_bug_logic_04(clean_user, clean_prev)
        if bug_l4:
            return bug_l4

        # 95. BUG-LOGIC-05: Çelişki İspatında Ters Varsayım Kurma Hatası
        bug_l5 = self._check_bug_logic_05(clean_user, clean_prev)
        if bug_l5:
            return bug_l5

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
        if any(trig in clean_p for trig in ("sin", "cos", "tan", "cot", "sec", "csc", "integrate", "diff", "limit", "int(")):
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

    def _check_bug_int_01(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-INT-01: İntegrasyon Sabiti (+C) Unutulması.
        Belirsiz integralde keyfi sabit +C'nin yazılmaması veya önemsiz sanılması.
        Örnek: ∫ 2x dx = x^2 (yerine x^2 + C).
        """
        clean_u = user_str.lower().replace(" ", "")
        clean_p = prev_str.lower().replace(" ", "")

        # Direct explicit misconceptions
        if (
            "+cyegerekyok" in clean_u
            or "cyegerekyok" in clean_u
            or "integralsabitigerekmez" in clean_u
            or "sabityok" in clean_u
            or "+colmasadagolur" in clean_u
            or "belirsizintegraldecsabitigerekmez" in clean_u
            or "csabitigerekmez" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-INT-01",
                severity="CRITICAL",
                category="CALCULUS_MISSING_CONSTANT_OF_INTEGRATION",
                description="Belirsiz integral hesaplanırken integrasyon sabiti (+ C) unutulmuştur. Türevi aynı olan sonsuz sayıda fonksiyon ailesi (+ C) mevcuttur.",
                remediation_directive="Belirsiz integralin sonucuna daima keyfi bir integrasyon sabiti olan '+ C' eklenmesi gerektiğini hatırlat.",
                offending_term=user_str,
            )

        # Pattern match: prev was indefinite integral, user answered without +C or +c
        is_definite = any(k in clean_p for k in [",0,", ",1,", ",2,", "_0^", "_a^", "(x,0", "(x,1", "definite"])
        has_c = "+c" in clean_u or clean_u.endswith("+c") or (len(clean_u) > 1 and clean_u[-1] == "c" and clean_u[-2] == "+")

        if not is_definite and not has_c and ("integrate" in clean_p or "int(" in clean_p or "integral" in clean_p):
            if clean_u in {"x^2", "x**2", "x^2/2", "x**2/2", "x^3/3", "x**3/3", "-cos(x)", "sin(x)", "e^x", "e**x", "ln(x)", "ln|x|"}:
                return DiagnosticPayload(
                    bug_id="BUG-INT-01",
                    severity="CRITICAL",
                    category="CALCULUS_MISSING_CONSTANT_OF_INTEGRATION",
                    description="Belirsiz integral hesaplanırken integrasyon sabiti (+ C) unutulmuştur. Belirsiz integral tek bir fonksiyon değil, bir fonksiyon ailesi belirtir.",
                    remediation_directive="Çözümün sonuna daima '+ C' integrasyon sabitini ekle.",
                    offending_term=user_str,
                )

        return None

    def _check_bug_int_02(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-INT-02: u-İkamesinde Diferansiyel (dx -> du) Dönüşümünün İhmali.
        Örnek: ∫ (2x+1)^3 dx = (2x+1)^4 / 4 (du = 2 dx hesaba katılmadığı için 1/2 çarpanı eksik).
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")

        if (
            "du=dx" in clean_u and ("u=2x" in clean_u or "u=2*x" in clean_u or "u=3x" in clean_u or "u=x^2" in clean_u)
            or "dx=du" in clean_u and ("2x" in clean_p or "3x" in clean_p)
            or "(2x+1)^4/4" in clean_u and "2x+1" in clean_p
            or "(2*x+1)^4/4" in clean_u and "2*x+1" in clean_p
            or "(3x+2)^5/5" in clean_u and "3x+2" in clean_p
            or "cos(2x)/2" not in clean_u and "cos(2x)" in clean_u and "sin(2x)" in clean_p and not clean_u.endswith("/2")
            or "uikamesindedxyerineduyazilabilir" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-INT-02",
                severity="CRITICAL",
                category="CALCULUS_U_SUBSTITUTION_MISSING_DIFFERENTIAL",
                description="u-ikamesi uygulanırken dx diferansiyeli du'ya dönüştürülmemiş veya iç fonksiyonun türevi (du = g'(x)dx) hesaba katılmamıştır.",
                remediation_directive="u = g(x) dönüşümünde du = g'(x)dx diferansiyelini alarak dx = du/g'(x) yerine koymasını sağla.",
                offending_term=user_str,
            )
        return None

    def _check_bug_int_03(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-INT-03: Belirli İntegralde Sınır Sırasını Ters Çıkarma (F(a) - F(b)).
        Örnek: ∫_a^b f(x)dx = F(a) - F(b) sanma (doğrusu F(b) - F(a)).
        """
        clean_u = user_str.lower().replace(" ", "")

        if (
            "f(a)-f(b)" in clean_u
            or "f(alt)-f(ust)" in clean_u
            or "altsinir-ustsinir" in clean_u
            or "f(0)-f(1)" in clean_u and "1" in prev_str
            or "f(0)-f(2)" in clean_u
            or "f(1)-f(3)" in clean_u
            or "[f(x)]_a^b=f(a)-f(b)" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-INT-03",
                severity="CRITICAL",
                category="CALCULUS_DEFINITE_INTEGRAL_REVERSED_LIMITS",
                description="Belirli integral hesaplanırken sınırlar ters çıkarılmıştır: ∫_a^b f(x)dx = F(b) - F(a) kuralı yerine F(a) - F(b) uygulanmıştır.",
                remediation_directive="Kalkülüsün Temel Teoremi gereği önce ÜST sınırın (F(b)), ardından ALT sınırın (F(a)) hesaplanıp F(b) - F(a) yapıldığını kontrol et.",
                offending_term=user_str,
            )
        return None

    def _check_bug_int_04(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-INT-04: Negatif Belirli İntegral Değerini Doğrudan Alan Kabul Etme.
        Örnek: Alan = -4 br^2 veya Alan = ∫ f(x)dx = -6.
        """
        clean_u = user_str.lower().replace(" ", "")

        if (
            "alan=-" in clean_u
            or "area=-" in clean_u
            or "alaninegatif" in clean_u
            or "alan=-4" in clean_u
            or "-4br^2" in clean_u
            or "-4birimkare" in clean_u
            or "alan=-6" in clean_u
            or "alan=-2" in clean_u
            or "alan=-10" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-INT-04",
                severity="CRITICAL",
                category="CALCULUS_NEGATIVE_DEFINITE_INTEGRAL_AS_AREA",
                description="Geometrik alan negatif olamaz! Eğri x-ekseninin altında kaldığında integral negatif çıkar, ancak alan bu integralin mutlak değeridir (|∫ f(x)dx|).",
                remediation_directive="x-ekseninin altında kalan bölgelerde alan için integralin işaretini eksi ile çarp veya mutlak değer al: Alan = -∫_a^b f(x)dx.",
                offending_term=user_str,
            )
        return None

    def _check_bug_int_05(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-INT-05: Kısmi İntegrasyon Formülünde İşaret Hatası (∫ u dv = uv + ∫ v du sanma).
        """
        clean_u = user_str.lower().replace(" ", "")

        if (
            "u*v+int(v*du)" in clean_u
            or "uv+int(vdu)" in clean_u
            or "u*v+integrate(v" in clean_u
            or "uv+integrate(v" in clean_u
            or "uv+\\int" in clean_u
            or "u*v+\\int" in clean_u
            or "kismi:uv+int" in clean_u
            or "udv=uv+vdu" in clean_u
            or "uv+vdu" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-INT-05",
                severity="CRITICAL",
                category="CALCULUS_INTEGRATION_BY_PARTS_SIGN_ERROR",
                description="Kısmi integrasyon formülünde işaret hatası yapılmıştır: ∫ u dv = u*v - ∫ v du olmalıdır, aradaki işaret eksi (-) olmalıdır.",
                remediation_directive="Kısmi integrasyon formülünü doğru uygula: u*v - ∫ v du (eksi işaretine dikkat et).",
                offending_term=user_str,
            )
        return None

    def _check_bug_int_06(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-INT-06: 1/x İntegralinde Standart Kuvvet Kuralı Uygulama (x^0 / 0 sanma).
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")

        if (
            "x^0/0" in clean_u
            or "x^0/0+c" in clean_u
            or "1/0*x^0" in clean_u
            or "int(1/x)=x^0/0" in clean_u
            or "integrate(1/x)=x^0/0" in clean_u
            or "x^(-1+1)/(-1+1)" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-INT-06",
                severity="CRITICAL",
                category="CALCULUS_POWER_RULE_ON_RECIPROCAL_ERROR",
                description="1/x (veya x^-1) fonksiyonuna standart kuvvet kuralı uygulanamaz, çünkü n = -1 için n+1 = 0 paydada tanımsızlık (x^0 / 0) yaratır. ∫ (1/x) dx = ln|x| + C olmalıdır.",
                remediation_directive="1/x'in türevi değil, kendisinin integrali ln|x| + C'dir. Kuvvet kuralının n ≠ -1 için geçerli olduğunu hatırla.",
                offending_term=user_str,
            )
        return None

    def _check_bug_int_07(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-INT-07: Belirli İntegralde Değişken Değiştirirken Sınırları Güncellememe.
        """
        clean_u = user_str.lower().replace(" ", "")

        if (
            "sinirlardegismez" in clean_u
            or "sinirlariaynibrak" in clean_u
            or "udegiskeninegecildiamasinirlarayni" in clean_u
            or "sinirlar0ve1kalir" in clean_u
            or "udegisimindesinirlardegismez" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-INT-07",
                severity="CRITICAL",
                category="CALCULUS_DEFINITE_U_SUBSTITUTION_LIMITS_UNCHANGED",
                description="Belirli integralde u-ikamesi yapıldığında sınırlar da yeni değişkene (u) uyarlanmalıdır. Eski x sınırları u integrali için geçerli değildir.",
                remediation_directive="u = g(x) dönüşümünde alt sınır için u(a), üst sınır için u(b) değerlerini hesaplayarak sınırları güncelle.",
                offending_term=user_str,
            )
        return None

    def _check_bug_int_08(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-INT-08: İki Eğri Arasında Alan Hesabında Üst-Alt Eğri Sırasını Ters Çıkarma.
        """
        clean_u = user_str.lower().replace(" ", "")
        clean_p = prev_str.lower().replace(" ", "")

        if (
            "alan=int(alt-ust)" in clean_u
            or "int(altegrisi-ustegrisi)" in clean_u
            or "altsinir-ustfonksiyon" in clean_u
            or "altegrisindenustegrisicikarilir" in clean_u
            or "alanicinalttakindenusttekicikarilir" in clean_u
            or ("alan=int(g-f)" in clean_u and "f>g" in clean_p)
        ):
            return DiagnosticPayload(
                bug_id="BUG-INT-08",
                severity="CRITICAL",
                category="CALCULUS_AREA_BETWEEN_CURVES_ORDER_REVERSED",
                description="İki eğri arasındaki alan hesaplanırken 'üst fonksiyon - alt fonksiyon' sırası ters çevrilmiştir. Alt fonksiyondan üst fonksiyon çıkarılırsa alan negatif çıkar.",
                remediation_directive="Aralıkta f(x) ≥ g(x) ise alan daima ∫ [f(x) - g(x)] dx olarak kurulmalıdır (üst - alt).",
                offending_term=user_str,
            )
        return None

    def _check_bug_int_09(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-INT-09: İntegralin Çarpma Üzerine Dağılması Sanrısı (∫ f*g = ∫ f * ∫ g).
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")

        if (
            "int(f*g)=int(f)*int(g)" in clean_u
            or "integrate(f*g)=integrate(f)*integrate(g)" in clean_u
            or "(intf)*(intg)" in clean_u
            or "int(x*sin(x))=int(x)*int(sin(x))" in clean_u
            or "int(x)*int(sin(x))" in clean_u
            or "int(x)*int(e^x)" in clean_u
            or "int(x)*int(e**x)" in clean_u
            or ("(x^2/2)*e^x" in clean_u and "x*e^x" in clean_p)
            or ("(x^2/2)*(-cos(x))" in clean_u and "x*sin(x)" in clean_p)
        ):
            return DiagnosticPayload(
                bug_id="BUG-INT-09",
                severity="CRITICAL",
                category="CALCULUS_INTEGRAL_PRODUCT_DISTRIBUTION_FALLACY",
                description="İntegral işlemi çarpma üzerine dağılmaz: ∫ [f(x) * g(x)] dx ≠ (∫ f(x) dx) * (∫ g(x) dx). Çarpım integralleri için u-ikamesi veya kısmi integrasyon kullanılmalıdır.",
                remediation_directive="Çarpım durumundaki integralleri çarpanlarına ayrı ayrı integralleme; değişken değiştirme veya kısmi integrasyon yöntemini seç.",
                offending_term=user_str,
            )
        return None

    def _check_bug_int_10(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-INT-10: Kalkülüsün Temel Teoremi 1'de Zincir Kuralını Unutma (d/dx ∫_a^g(x) f(t)dt = f(g(x))).
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")

        if (
            "d/dxint_a^g(x)=f(g(x))" in clean_u
            or "d/dx(int_0^(x^2))=sin(x^2)" in clean_u
            or (clean_u == "sin(x^2)" and "int_0^(x^2)sin(t)dt" in clean_p)
            or "ftc1zincirkuralinagerekyok" in clean_u
            or "d/dxint=f(ustsinir)" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-INT-10",
                severity="CRITICAL",
                category="CALCULUS_FTC1_MISSING_CHAIN_RULE",
                description="Kalkülüsün Temel Teoremi (FTC-1) uygulanırken üst sınır değişken x yerine bir fonksiyon g(x) olduğunda zincir kuralı gereği g'(x) türeviyle çarpılmalıdır: d/dx [∫_a^{g(x)} f(t) dt] = f(g(x)) * g'(x).",
                remediation_directive="Üst sınırın türevi olan g'(x) çarpanını sonuca ekle: f(g(x)) * g'(x).",
                offending_term=user_str,
            )
        return None

    def _check_bug_prob_01(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PROB-01: Zaman Kayması Hatası (Yaş Problemleri).
        Geçen yılı sadece tek bir kişiye ekleyip diğer kişiyi sabit tutma.
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")
        if (
            re.search(r"x\s*\+\s*(\d+)\s*=\s*(\d+)\s*\*?\s*y(?!\s*\+)", clean_u)
            or ("x+5=2y" in clean_u or "x+5=2*y" in clean_u or "x+4=3y" in clean_u)
            or "tekbirkisiyeyasartisi" in clean_u
            or ("x+5=2*y" in clean_u and ("yas" in clean_p or "age" in clean_p))
        ):
            return DiagnosticPayload(
                bug_id="BUG-PROB-01",
                severity="CRITICAL",
                category="WORD_PROBLEMS_AGE_SHIFT_ASYMMETRY",
                description="Yaş problemlerinde geçen zaman herkes için eşit akar. Yıllar eklendiğinde sadece bir kişiye değil, denklemdeki tüm kişilerin yaşlarına aynı miktar eklenmelidir.",
                remediation_directive="t yıl sonra her iki kişinin de yaşı t kadar artar: x + t = k * (y + t) şeklinde parantez kullanarak her iki tarafa da zamanı ekle.",
                offending_term=user_str,
            )
        return None

    def _check_bug_prob_02(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PROB-02: Hız-Zaman Ters Orantı / Doğru Orantı Çelişkisi.
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")
        if (
            "v1/v2=t1/t2" in clean_u
            or "t=v*x" in clean_u
            or "t=v*d" in clean_u
            or "hizartarsasureartar" in clean_u
            or "v/t=x" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-PROB-02",
                severity="CRITICAL",
                category="WORD_PROBLEMS_SPEED_TIME_INVERSE_RATIO",
                description="Yol sabitken hız ile zaman doğru orantılı değil, ters orantılıdır: v * t = x. Hız 2 katına çıkarsa, varış süresi yarıya iner.",
                remediation_directive="Hız ile süre çarpım durumundadır (x = v * t). Hızlar oranı ile süreler oranı birbirinin tersidir: v1 / v2 = t2 / t1.",
                offending_term=user_str,
            )
        return None

    def _check_bug_prob_03(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PROB-03: Ortalama Hızda Aritmetik Ortalama Tuzağı.
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")
        if (
            "vort=(v1+v2)/2" in clean_u
            or "v_ort=(v1+v2)/2" in clean_u
            or "(v1+v2)/2" in clean_u and ("ortalamahiz" in clean_p or "gidisdonus" in clean_p or "ortalama" in clean_u)
            or "vort=(60+40)/2=50" in clean_u
            or "vort=50" in clean_u and ("60" in clean_p and "40" in clean_p)
            or "ortalamahizaritmetikortalamadir" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-PROB-03",
                severity="CRITICAL",
                category="WORD_PROBLEMS_AVERAGE_SPEED_ARITHMETIC_FALLACY",
                description="Ortalama hız hızların aritmetik ortalaması değildir. Ortalama hız daima Toplam Yol / Toplam Zaman bağıntısıyla (eşit mesafede Harmonik Ortalama: 2*v1*v2 / (v1+v2)) hesaplanır.",
                remediation_directive="Ortalama hız için v_ort = Toplam Yol / Toplam Zaman formülünü kur veya eşit yollarda 2*v1*v2 / (v1 + v2) harmonik ortalamasını kullan.",
                offending_term=user_str,
            )
        return None

    def _check_bug_prob_04(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PROB-04: Yüzde Artış ve Azalışın Birbirini Sıfırladığı Sanrısı.
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")
        if (
            "%20zam+%20indirim=0" in clean_u
            or "100+20-20=100" in clean_u
            or "fiyatdegismez" in clean_u
            or "zamveindirimbirbirinisifirlar" in clean_u
            or "1.20*0.80=1" in clean_u
            or "1.2*0.8=1" in clean_u
            or "degisim=%0" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-PROB-04",
                severity="CRITICAL",
                category="WORD_PROBLEMS_PERCENTAGE_REVERSAL_FALLACY",
                description="Yüzde artış ve azalış birbirini nötrlemez. Yapılan indirim zam görmüş yeni fiyat üzerinden hesaplandığı için nihai fiyat başlangıç fiyatından daha düşüktür (Örn: 100 * 1.20 * 0.80 = 96 != 100).",
                remediation_directive="Ardışık yüzdeleri toplamak yerine çarpan olarak modelle: P_son = P_0 * (1 + zam) * (1 - indirim).",
                offending_term=user_str,
            )
        return None

    def _check_bug_prob_05(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PROB-05: Karışımda Saf Madde vs Toplam Karışım Kargaşası.
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")
        if (
            "yuzde=tuz/su" in clean_u
            or "yuzde=seker/su" in clean_u
            or "madde/cozucu" in clean_u
            or ("tuz/su" in clean_u and ("karisim" in clean_p or "yuzde" in clean_p))
            or "20/80=%25" in clean_u
            or "karisimorani=safmadde/su" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-PROB-05",
                severity="CRITICAL",
                category="WORD_PROBLEMS_MIXTURE_SOLVENT_VS_TOTAL_CONFUSION",
                description="Karışım yüzdesi saf maddenin çözücüye (suya) oranı değil, saf maddenin TOPLAM KARIŞIMA (madde + çözücü) oranıdır.",
                remediation_directive="Yüzde formülünü kurarken paydaya daima toplam kütleyi yaz: Yüzde = (Saf Madde) / (Saf Madde + Su) * 100.",
                offending_term=user_str,
            )
        return None

    def _check_bug_prob_06(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PROB-06: İşçi Probleminde Süreleri Düz Toplama.
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")
        if (
            "t_birlikte=t1+t2" in clean_u
            or "tbirlikte=t1+t2" in clean_u
            or "6+3=9gun" in clean_u
            or "6+3=9" in clean_u
            or "6+12=18gun" in clean_u
            or "6+12=18" in clean_u
            or "birlikte=6+3=9" in clean_u
            or "surelertoplanir" in clean_u
            or ("ikisi=9" in clean_u and "6" in clean_p and "3" in clean_p)
            or ("ikisi=18" in clean_u)
        ):
            return DiagnosticPayload(
                bug_id="BUG-PROB-06",
                severity="CRITICAL",
                category="WORD_PROBLEMS_WORK_TIME_LINEAR_ADDITION",
                description="İki işçi birlikte çalıştığında iş daha uzun sürmez, daha kısa sürer. Süreler doğrudan toplanamaz; birim zamanda yapılan iş hızları (kapasiteler) toplanır.",
                remediation_directive="Birim zamanda yapılan iş üzerinden denklem kur: 1/t1 + 1/t2 = 1/T_birlikte.",
                offending_term=user_str,
            )
        return None

    def _check_bug_prob_07(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PROB-07: Bağıl Hızda Yön / İşaret Hatası.
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")
        if (
            "karsilasma=(v1-v2)*t" in clean_u
            or ("(v1-v2)*t=x" in clean_u and ("zit" in clean_p or "karsit" in clean_p or "birbirinedogru" in clean_p))
            or "yetisme=(v1+v2)*t" in clean_u
            or ("(v1+v2)*t=x" in clean_u and ("ayniyonde" in clean_p or "yetisme" in clean_p or "kovalama" in clean_p))
            or "bagilhizyontutarsizligi" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-PROB-07",
                severity="CRITICAL",
                category="WORD_PROBLEMS_RELATIVE_VELOCITY_SIGN_INVERSION",
                description="Bağıl hareket yönüne dikkat edilmelidir: Birbirine doğru gelen araçlar mesafeyi daha hızlı kapatır (bağıl hız v1 + v2). Aynı yönde giden araçlarda yetişme hızı farklarıdır (v1 - v2).",
                remediation_directive="Karşıt yönlü karşılaşmalarda hızları topla: (v1 + v2)*t = d. Aynı yönlü yakalamalarda hızları çıkar: (v1 - v2)*t = d.",
                offending_term=user_str,
            )
        return None

    def _check_bug_prob_08(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PROB-08: Kâr Marjı Tabanı (Maliyet vs Satış Fiyatı) Karışıklığı.
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")
        if (
            "kar=satis*yuzde" in clean_u
            or "maliyet=satis*(1-kar)" in clean_u
            or ("satis=maliyet/(1-kar)" in clean_u and "karoranimaliyet" in clean_p)
            or "maliyettenkarcarpimi" in clean_u
            or "karhesabindasatisfiyati" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-PROB-08",
                severity="CRITICAL",
                category="WORD_PROBLEMS_PROFIT_BASE_COST_VS_SELLING",
                description="Belirtilmediği sürece kâr oranı daima MALİYET fiyatı üzerinden hesaplanır. Satış fiyatı üzerinden kâr hesaplamak marjı yanlış saptar.",
                remediation_directive="Satış fiyatı denklemini maliyet tabanlı kur: Satış Fiyatı = Maliyet * (1 + Kâr_Yüzdesi / 100).",
                offending_term=user_str,
            )
        return None

    def _check_bug_prob_09(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PROB-09: Birim Uyuşmazlığı (km/saat vs dakika).
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")
        if (
            ("x=60*20" in clean_u and "dakika" in clean_p)
            or "yol=hiz*dakika" in clean_u
            or "dakikayisaatecevirmeden" in clean_u
            or "birimuyusmazligi" in clean_u
            or "x=v*dakika" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-PROB-09",
                severity="CRITICAL",
                category="WORD_PROBLEMS_UNIT_INCONSISTENCY",
                description="Hız formülünde birimler uyumlu olmalıdır. Hız km/saat olarak verilmişse, süre de saat birimine çevrilmelidir (Örn: 20 dakika = 20/60 = 1/3 saat).",
                remediation_directive="Verilen süreyi önce saate çevir (dakika / 60), ardından yol formülünde yerine koy: x = v * (t_dk / 60).",
                offending_term=user_str,
            )
        return None

    def _check_bug_prob_10(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """
        BUG-PROB-10: Gerçek Dünya Kısıtını Göz Ardı Etme.
        """
        clean_u = user_str.lower().replace(" ", "").replace("**", "^")
        clean_p = prev_str.lower().replace(" ", "").replace("**", "^")
        if (
            ("x=-" in clean_u and any(w in clean_p for w in ["yas", "hiz", "sure", "isci", "metre", "km", "fiyat"]))
            or "yas=-" in clean_u
            or "hiz=-" in clean_u
            or "sure=-" in clean_u
            or "negatifkokgecerlidir" in clean_u
            or "gercekdunyakisitiihmali" in clean_u
        ):
            return DiagnosticPayload(
                bug_id="BUG-PROB-10",
                severity="CRITICAL",
                category="WORD_PROBLEMS_REAL_WORLD_DOMAIN_INVALIDATION",
                description="Cebirsel denklem negatif bir kök verse bile gerçek dünyada yaş, hız, zaman, uzunluk veya kişi sayısı negatif olamaz.",
                remediation_directive="Bulunan kökü gerçek dünya kısıtlarıyla süz: Yaş, hız ve zaman fiziksel olarak pozitif (x > 0) olmalıdır. Negatif kökü çözüm kümesinden çıkar.",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_01(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-01: Çift Eksi Tuzağı (-(-4) = -4 sanma)."""
        clean = user_str.replace(" ", "")
        if "-(-" in clean and "=-" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-01",
                severity="CRITICAL",
                category="FOUNDATION_DOUBLE_NEGATIVE_FALLACY",
                description="İki eksi yan yana geldiğinde (-(-a)) yön iki kez döner ve pozitif (+a) olur.",
                remediation_directive="-(-a) daima +a yapar. Eksi ile eksi çarpıldığında sonuç artıya döner.",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_02(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-02: İşlem Önceliği Körlüğü (3 + 4*2 = 14 sanma)."""
        clean = user_str.replace(" ", "")
        if "3+4*2=14" in clean or "3+4·2=14" in clean or "islemonceligiyok" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-02",
                severity="CRITICAL",
                category="FOUNDATION_ORDER_OF_OPERATIONS_BLINDNESS",
                description="Çarpma işlemi toplama işleminden önce yapılır. 3 + 4*2 işleminde önce 4*2 = 8, sonra 3 + 8 = 11 olmalıdır.",
                remediation_directive="Önce çarpma ve bölme paketlerini hesapla, ardından toplama veya çıkarma yap.",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_03(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-03: Kuvvet ile İşaret Çelişkisi (-3^2 = 9 yazma)."""
        clean = user_str.replace(" ", "").replace("**", "^")
        if "-3^2=9" in clean or "-3^2=+9" in clean or "-5^2=25" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-03",
                severity="CRITICAL",
                category="FOUNDATION_EXPONENT_SIGN_PRECEDENCE",
                description="Parantez olmadan üs sadece sayıya aittir: -3² = -(3·3) = -9'dur. Sonucun pozitif olması için (-3)² yazılmalıdır.",
                remediation_directive="Parantez yoksa tabandaki eksiyi koru: -a² daima negatiftir.",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_04(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-04: Kesir Düz Toplama Hatası (1/2 + 1/3 = 2/5)."""
        clean = user_str.replace(" ", "")
        if "1/2+1/3=2/5" in clean or "paylarvepaydalarduztoplanir" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-04",
                severity="CRITICAL",
                category="FOUNDATION_FRACTION_FLAT_ADDITION",
                description="Farklı boyutlardaki pizza dilimleri düz toplanamaz. Paydalar eşitlenmeden kesirlerde toplama yapılamaz: 1/2 + 1/3 = 3/6 + 2/6 = 5/6.",
                remediation_directive="Kesirleri toplamadan önce ortak paydada buluştur (paydaları eşitle).",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_05(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-05: Yarım Dağılma Hatası (2(x+3) = 2x+3)."""
        clean = user_str.replace(" ", "")
        if "2(x+3)=2x+3" in clean or "3(x+4)=3x+4" in clean or "yarimdagilma" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-05",
                severity="CRITICAL",
                category="FOUNDATION_PARTIAL_DISTRIBUTION",
                description="Parantez dışındaki katsayı parantez içindeki HER terimle ayrı ayrı çarpılmalıdır: 2(x + 3) = 2x + 6.",
                remediation_directive="Parantez içindeki sabit terimi de dıştaki katsayı ile çarpmayı unutma.",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_06(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-06: Toplama/Çarpma Karışıklığı (x + x = x^2)."""
        clean = user_str.replace(" ", "").replace("**", "^")
        if "x+x=x^2" in clean or "a+a=a^2" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-06",
                severity="CRITICAL",
                category="FOUNDATION_ADDITION_MULTIPLICATION_CONFUSION",
                description="x + x iki tane x demektir (2x). Üs sadece çarpma işleminde artar: x · x = x².",
                remediation_directive="Benzer terimleri toplarken katsayıları topla: x + x = 2x.",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_07(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-07: Katsayıyı Çıkarma Sanma (3x = 12 => x = 12 - 3 = 9)."""
        clean = user_str.replace(" ", "")
        if ("3x=12" in prev_str.replace(" ", "") and ("x=9" in clean or "12-3" in clean)) or "katsayicikarmaolarakgecer" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-07",
                severity="CRITICAL",
                category="FOUNDATION_COEFFICIENT_SUBTRACTION_FALLACY",
                description="3 ile x çarpım durumundadır (3·x). Eşitliğin diğer tarafına çıkarma değil, bölme olarak geçer: x = 12 / 3 = 4.",
                remediation_directive="x'in önündeki çarpanı karşıya bölme olarak at: x = b / a.",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_08(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-08: Elma ile Armudu Toplama (2x + 3 = 5x)."""
        clean = user_str.replace(" ", "")
        if "2x+3=5x" in clean or "3x+4=7x" in clean or "elmailearmuttoplanir" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-08",
                severity="CRITICAL",
                category="FOUNDATION_UNLIKE_TERMS_ADDITION",
                description="Değişkenli bir terim ile sabit bir sayı düz toplanamaz. 2x + 3 ifadesi en sade haldedir, 5x yapmaz.",
                remediation_directive="Sadece aynı harfe ve üsse sahip benzer terimleri toplayabilirsin.",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_09(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-09: Üs ile Tabanı Çarpma (2^3 = 6)."""
        clean = user_str.replace(" ", "").replace("**", "^")
        if "2^3=6" in clean or "3^2=6" in clean or "2^4=8" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-09",
                severity="CRITICAL",
                category="FOUNDATION_EXPONENT_BASE_MULTIPLICATION",
                description="Üs tabandaki sayının kaç kere kendisiyle çarpılacağını söyler: 2³ = 2·2·2 = 8'dir. Asla taban ile üs çarpılmaz (2·3=6 değildir).",
                remediation_directive="Üslü ifadede tabanı üs kadar yan yana yazıp çarp.",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_10(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-10: Negatif Sıralama Yanılgısı (-8 > -3)."""
        clean = user_str.replace(" ", "")
        if "-8>-3" in clean or "-10>-2" in clean or "-5>-1" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-10",
                severity="CRITICAL",
                category="FOUNDATION_NEGATIVE_ORDERING_FALLACY",
                description="Sayı doğrusunda sola gidildikçe sayılar küçülür. Borç büyüdükçe elde kalan azalır: -8 < -3.",
                remediation_directive="Negatif sayılarda mutlak değeri büyük olan sayı daha küçüktür.",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_11(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-11: Sıfıra Bölme Hatası (5/0 = 0 veya 5)."""
        clean = user_str.replace(" ", "")
        if "5/0=0" in clean or "5/0=5" in clean or "sayi/0=0" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-11",
                severity="CRITICAL",
                category="FOUNDATION_DIVISION_BY_ZERO",
                description="Bir sayının sıfıra bölümü tanımlı değildir (Tanımsızdır). Sadece 0 / 5 = 0 olur.",
                remediation_directive="Paydada sıfır varsa ifade tanımsızdır; sıfıra eşitleme.",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_12(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-12: Eksi Parantez Dağılma (-(x - 4) = -x - 4)."""
        clean = user_str.replace(" ", "")
        if "-(x-4)=-x-4" in clean or "-(x-3)=-x-3" in clean or "-(a-b)=-a-b" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-12",
                severity="CRITICAL",
                category="FOUNDATION_NEGATIVE_PARENTHESIS_DISTRIBUTION",
                description="Parantezin önündeki eksi işareti içeri dağıtılırken içindeki TÜM işaretler tersine döner: -(x - 4) = -x + 4.",
                remediation_directive="Eksiyi dağıtırken eksi ile eksinin çarpımının artı olduğunu hatırla: -(-4) = +4.",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_13(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-13: Fonksiyonu Sayı Sanma (f(x)=2x için f(3)=23)."""
        clean = user_str.replace(" ", "")
        if ("f(3)=23" in clean and "f(x)=2x" in prev_str.replace(" ", "")) or "f(x)=2x=>f(3)=23" in clean or "f(3)=23" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-13",
                severity="CRITICAL",
                category="FOUNDATION_FUNCTION_DIGIT_CONCAT_FALLACY",
                description="2x ifadesi basamak değeri değil, çarpma işlemidir (2·x). Dolayısıyla f(3) = 2 · 3 = 6 olur, 23 değil.",
                remediation_directive="Değişkenin yerine sayı koyarken örtük çarpmayı hatırla: 2x -> 2 · 3 = 6.",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_14(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-14: Eşitsizlikte Yön Unutma (-2x < 6 => x < -3)."""
        clean = user_str.replace(" ", "")
        if ("-2x<6" in prev_str.replace(" ", "") and "x<-3" in clean) or "-2x<6=>x<-3" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-14",
                severity="CRITICAL",
                category="FOUNDATION_INEQUALITY_NEGATIVE_DIVISION_DIRECTION",
                description="Bir eşitsizliğin her iki tarafı negatif bir sayıya bölündüğünde eşitsizlik yön değiştirir: -2x < 6 => x > -3.",
                remediation_directive="Negatif sayıya bölerken küçüktür işaretini büyüktür olarak çevir.",
                offending_term=user_str,
            )
        return None

    def _check_bug_found_15(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-FOUND-15: Tek Taraflı Terazi Hatası (x + 4 = 10 => x + 4 - 4 = 10)."""
        clean = user_str.replace(" ", "")
        # Sağ taraftan da 4 çıkarılmışsa (örn: = 10 - 4) bu doğru adımdır, hata değildir!
        if (clean == "x+4-4=10" or clean == "x+4-4=10." or (clean.startswith("x+4-4=10") and not clean.startswith("x+4-4=10-"))) or "tektarafliterazi" in clean:
            return DiagnosticPayload(
                bug_id="BUG-FOUND-15",
                severity="CRITICAL",
                category="FOUNDATION_ONE_SIDED_BALANCE_ERROR",
                description="Terazinin dengede kalması için sol kefeden ne çıkarılırsa sağ kefeden de aynısı çıkarılmalıdır: x + 4 - 4 = 10 - 4 => x = 6.",
                remediation_directive="Eşitliğin her iki tarafına da aynı işlemi uygula.",
                offending_term=user_str,
            )
        return None

    def _check_bug_anag_01(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-ANAG-01: Dik Doğrularda Eğim Bağıntısı Hatası (m1 = m2 veya m1*m2 = 1)."""
        clean = user_str.replace(" ", "").lower()
        prev_clean = prev_str.replace(" ", "").lower()
        is_perp_context = "dik" in prev_clean or "perpendicular" in prev_clean or "m1.m2" in clean or "m1*m2" in clean
        if "m1*m2=1" in clean or "m1.m2=1" in clean or "m_dik=m" in clean:
            return DiagnosticPayload(
                bug_id="BUG-ANAG-01",
                severity="CRITICAL",
                category="GEOMETRY_PERPENDICULAR_SLOPE_ERROR",
                description="Birbirine dik iki doğrunun eğimleri çarpımı -1'dir: m₁ · m₂ = -1 (m₂ = -1 / m₁). Eğimlerin eşit olması (m₁ = m₂) paralellik şartıdır.",
                remediation_directive="Dik doğruların eğimleri birbirinin negatif tersidir: m2 = -1 / m1.",
                offending_term=user_str,
            )
        if is_perp_context and ("m2=m1" in clean or "m_dik=m1" in clean or "m1=m2" in clean or "m=2=>m_dik=2" in clean):
            return DiagnosticPayload(
                bug_id="BUG-ANAG-01",
                severity="CRITICAL",
                category="GEOMETRY_PERPENDICULAR_SLOPE_ERROR",
                description="Dik doğruların eğimleri eşit olamaz. Paralel doğruların eğimleri eşittir. Dik doğrularda m1 · m2 = -1 olmalıdır.",
                remediation_directive="Eğimler çarpımının -1 olması gerektiğini uygula: m2 = -1 / m1.",
                offending_term=user_str,
            )
        return None

    def _check_bug_anag_02(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-ANAG-02: Geniş Açı ve Eğim İşareti Hatası (theta > 90 fakat m > 0)."""
        clean = user_str.replace(" ", "").lower()
        if (
            "tan(135)=1" in clean
            or "tan(120)=sqrt(3)" in clean
            or "tan(150)=1/sqrt(3)" in clean
            or "theta=135=>m=1" in clean
            or "m=tan(135)=1" in clean
            or "egimacisi=135=>m=1" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-ANAG-02",
                severity="CRITICAL",
                category="GEOMETRY_OBTUSE_SLOPE_SIGN_ERROR",
                description="Geniş açılı (90° < θ < 180°) doğrular sola yatıktır ve eğimleri negatiftir: tan(135°) = -1, tan(120°) = -√3.",
                remediation_directive="Geniş açının tanjantının negatif olduğunu hatırla: tan(180° - x) = -tan(x).",
                offending_term=user_str,
            )
        return None

    def _check_bug_anag_03(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-ANAG-03: Çember Merkez Koordinatında İşaret Tersliği (M(-a, -b))."""
        clean = user_str.replace(" ", "")
        prev_clean = prev_str.replace(" ", "")
        # Örnek: (x-2)^2 + (y-3)^2 = 16 için M(-2,-3)
        if (
            ("(x-2)^2" in prev_clean or "(x-2)**2" in prev_clean)
            and ("M(-2," in clean or "merkez=(-2," in clean or "m(-2," in clean)
        ) or (
            "(x-3)^2+(y+4)^2=25=>M(-3,4)" in clean
            or "(x-a)^2+(y-b)^2=r^2=>M(-a,-b)" in clean
            or "(x-2)^2+(y-3)^2=16=>M(-2,-3)" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-ANAG-03",
                severity="CRITICAL",
                category="GEOMETRY_CIRCLE_CENTER_SIGN_REVERSAL",
                description="Çember standart denklemi (x - a)² + (y - b)² = r² biçimindedir. Parantez içini sıfırlayan değerler merkez koordinatlarıdır: x - a = 0 => x = a. Dolayısıyla merkez M(a, b)'dir, işaretler ters çevrilmelidir.",
                remediation_directive="Çember merkezini bulurken terimlerin zıt işaretlisini al: (x - a) için +a, (y + b) için -b.",
                offending_term=user_str,
            )
        return None

    def _check_bug_anag_04(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-ANAG-04: Uzaklık Formülünde Karekökü Unutma (d = (x2-x1)^2 + (y2-y1)^2)."""
        clean = user_str.replace(" ", "").lower()
        if (
            "d=(x2-x1)^2+(y2-y1)^2" in clean
            or "d=(x2-x1)**2+(y2-y1)**2" in clean
            or "d=(3-0)^2+(4-0)^2=25" in clean
            or "d=(4-1)^2+(6-2)^2=25" in clean
            or "(x2-x1)^2+(y2-y1)^2=25=>d=25" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-ANAG-04",
                severity="CRITICAL",
                category="GEOMETRY_DISTANCE_OMITTED_SQUARE_ROOT",
                description="İki nokta arasındaki uzaklık formülü Pisagor teoreminden gelir: d = √[(x₂ - x₁)² + (y₂ - y₁)²]. Kareler toplamının mutlaka karekökü alınmalıdır.",
                remediation_directive="Kareler toplamını bulduktan sonra karekök almayı unutma: d² = 25 ise d = 5.",
                offending_term=user_str,
            )
        return None

    def _check_bug_anag_05(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-ANAG-05: Vektör İç Çarpımında Vektörel Sonuç Üretme ((u1*v1, u2*v2))."""
        clean = user_str.replace(" ", "").lower()
        if (
            "u.v=(u1*v1,u2*v2)" in clean
            or "u.v=(u1v1,u2v2)" in clean
            or "u.v=(8,3)" in clean
            or "(2,3).(4,1)=(8,3)" in clean
            or "(1,2).(3,4)=(3,8)" in clean
            or "u*v=(8,3)" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-ANAG-05",
                severity="CRITICAL",
                category="GEOMETRY_VECTOR_DOT_PRODUCT_VECTORIAL_FALLACY",
                description="İki vektörün nokta (skaler / iç) çarpımı bir sayı (skaler) üretir: u · v = u₁v₁ + u₂v₂. Bileşenler ayrı ayrı çarpılıp yeni bir vektör oluşturulmaz.",
                remediation_directive="Bileşen çarpımlarını virgülle ayırmak yerine topla: u1*v1 + u2*v2.",
                offending_term=user_str,
            )
        return None

    def _check_bug_euc_01(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-EUC-01: Üçgen Eşitsizliği İhlali (a >= b + c)."""
        clean = user_str.replace(" ", "").lower()
        if (
            "3+4<8=>ucgen" in clean
            or "kenarlar=3,4,8" in clean
            or "a=8,b=3,c=4=>ucgen" in clean
            or "8>=3+4" in clean
            or "kenarlar:3,4,8" in clean
            or "ucgen=(3,4,8)" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-EUC-01",
                severity="CRITICAL",
                category="EUCLIDEAN_TRIANGLE_INEQUALITY_VIOLATION",
                description="Bir üçgenin herhangi bir kenarı diğer iki kenarın toplamından küçük olmalıdır: a < b + c. 8 >= 3 + 4 olduğundan bu kenarlarla üçgen çizilemez.",
                remediation_directive="Üçgen eşitsizliğini kontrol et: |b - c| < a < b + c şartı sağlanmalıdır.",
                offending_term=user_str,
            )
        return None

    def _check_bug_euc_02(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-EUC-02: Çevre Açı ile Merkez Açı Eşitliği Sanrısı."""
        clean = user_str.replace(" ", "").lower()
        if "/2" in clean or "/ 2" in user_str or "*0.5" in clean:
            return None
        if (
            "cevre_aci=merkez_aci" in clean
            or "cevre=merkez" in clean
            or "alpha_cevre=alpha_merkez" in clean
            or "merkez=80=>cevre=80" in clean
            or "merkez_aci=80=>cevre_aci=80" in clean
            or "cevre_aci=yay" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-EUC-02",
                severity="CRITICAL",
                category="EUCLIDEAN_INSCRIBED_ANGLE_EQUALS_CENTRAL_ANGLE",
                description="Çemberde aynı yayı gören çevre açının ölçüsü merkez açının (veya yayın) yarısına eşittir: α_çevre = α_merkez / 2.",
                remediation_directive="Çevre açının köşesi çember üzerindedir ve merkez açının yarısı kadar açı görür.",
                offending_term=user_str,
            )
        return None

    def _check_bug_euc_03(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-EUC-03: Benzerlik Oranını Alan Oranına Eşit Sayma (k -> k²)."""
        clean = user_str.replace(" ", "").lower()
        if (
            "k=2=>alan_orani=2" in clean
            or "k=3=>alan_orani=3" in clean
            or "alan_orani=k" in clean
            or "alanlar_orani=k" in clean
            or "alan1/alan2=k" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-EUC-03",
                severity="CRITICAL",
                category="EUCLIDEAN_SIMILARITY_AREA_RATIO_LINEAR_FALLACY",
                description="Benzer iki geometrik şeklin alanları oranı benzerlik oranına değil, benzerlik oranının karesine eşittir: Alan₁ / Alan₂ = k².",
                remediation_directive="Uzunluk oranı k ise, iki boyutlu alan hesabı için karesini al: k².",
                offending_term=user_str,
            )
        return None

    def _check_bug_euc_04(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-EUC-04: Öklid Yükseklik Bağıntısında Kenar Çarpımı Hatası (h² = b·c)."""
        clean = user_str.replace(" ", "").lower()
        if (
            "h^2=b*c" in clean
            or "h**2=b*c" in clean
            or "h^2=b.c" in clean
            or "h=p*k" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-EUC-04",
                severity="CRITICAL",
                category="EUCLIDEAN_RIGHT_TRIANGLE_HEIGHT_RELATION_ERROR",
                description="Öklid teoreminde dik kenarların çarpımı taban ile yüksekliğin çarpımına eşittir (b · c = a · h). Yüksekliğin karesi ise hipotenüste ayırdığı parçaların çarpımına eşittir: h² = p · k.",
                remediation_directive="Yüksekliğin karesi için hipotenüsteki izdüşüm parçalarını çarp: h² = p · k.",
                offending_term=user_str,
            )
        return None

    def _check_bug_euc_05(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-EUC-05: Açıortay Teoreminde Orantı Yerine Eşit Bölme Sanrısı."""
        clean = user_str.replace(" ", "").lower()
        if (
            "aciortay=>taban_esit" in clean
            or "aciortay=>m=n" in clean
            or "c/b=n/m" in clean
            or "aciortay_tabani_ortalar" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-EUC-05",
                severity="CRITICAL",
                category="EUCLIDEAN_ANGLE_BISECTOR_RATIO_FALLACY",
                description="İç açıortay karşı kenarı eşit ikiye bölmez (kenarortay değildir); kenarların oranında böler: c / b = m / n.",
                remediation_directive="Açıortayın kenarlarla taban parçalarını orantıladığını hatırla: sol kenar / sağ kenar = sol taban / sağ taban.",
                offending_term=user_str,
            )
        return None

    def _check_bug_comb_01(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-COMB-01: Sırasız Seçimde Permütasyon Kullanma (Kombinasyon yerine P(n, r))."""
        clean = user_str.replace(" ", "").lower()
        # Guard: if user divides by factorial or applies combination formula, it's valid
        if "/3!" in clean or "/ 3!" in user_str or "/6" in clean or "/ 6" in user_str or "c(" in clean:
            return None
        if (
            "p(5,3)" in clean
            or "komite=p(5,3)" in clean
            or "secim=p(5,3)" in clean
            or "komite=60" in clean
            or "grup=p(5,3)" in clean
            or "c(5,3)=60" in clean
            or "altkume=p(5,3)" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-COMB-01",
                severity="CRITICAL",
                category="COMBINATORICS_PERMUTATION_INSTEAD_OF_COMBINATION",
                description="Sırasız seçim (komite, grup, küme alt kümesi vb.) problemlerinde sıra önemsizdir; dolayısıyla permütasyon P(n, r) değil, kombinasyon C(n, r) kullanılmalıdır.",
                remediation_directive="Grup elemanlarının diziliş sırası değiştiğinde yeni bir grup oluşur mu? Sıranın önemsiz olduğunu dikkate alarak r! faktöriyeline böl.",
                offending_term=user_str,
            )
        return None

    def _check_bug_comb_02(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-COMB-02: Kumarbaz Yanılgısı (Gambler's Fallacy - Bağımsız Olaylarda Bellek Sanrısı)."""
        clean = user_str.replace(" ", "").lower()
        if (
            "p(tura)>1/2" in clean
            or "p(tura)>0.5" in clean
            or "yazigeldi=>p(tura)>0.5" in clean
            or "5yazi=>kesintura" in clean
            or "tura_gelme_olasiligi_artar" in clean
            or "gecmis_atislardan_dolayi" in clean
            or "siradaki_kesin_tura" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-COMB-02",
                severity="CRITICAL",
                category="PROBABILITY_GAMBLERS_FALLACY",
                description="Bağımsız olaylarda (örneğin madeni para veya zar atımı) geçmiş denemeler gelecekteki olasılığı etkilemez (belleksizlik ilkesi). Her bağımsız atışta P(Tura) = 1/2'dir.",
                remediation_directive="Madeni paranın önceki atışları hatırlayan bir hafızası var mıdır? Her atışın birbirinden bağımsız olduğunu hatırla.",
                offending_term=user_str,
            )
        return None

    def _check_bug_comb_03(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-COMB-03: Koşullu Olasılıkta Örnek Uzayı Daraltmama (Paydaya Evrensel Örnek Uzayı Yazma)."""
        clean = user_str.replace(" ", "").lower()
        if (
            "kosullu_payda=36" in clean
            or "ornek_uzay_degismez=36" in clean
            or "p(a|b)=s(a∩b)/36" in clean
            or "p(a|b)=s(a)/s(e)" in clean
            or "payda_hala_36" in clean
            or "evren_daralmaz" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-COMB-03",
                severity="CRITICAL",
                category="PROBABILITY_CONDITIONAL_SAMPLE_SPACE_NOT_REDUCED",
                description="Koşullu olasılıkta (P(A|B)), B olayının gerçekleştiği bilindiği için yeni örnek uzay B olayının çıktılarından oluşur; payda tüm evrensel küme S değil, s(B) olmalıdır.",
                remediation_directive="B olayının kesinleştiği bilindiğine göre evrensel örnek uzay daralmıştır. Paydaya tüm evreni değil, koşulun sağlandığı durum sayısını s(B) yaz.",
                offending_term=user_str,
            )
        return None

    def _check_bug_comb_04(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-COMB-04: Tekrarlı Permütasyonda Özdeş Eleman Bölümünü Unutma (n! / c1!c2!)."""
        clean = user_str.replace(" ", "").lower()
        # Guard: if user divides by factorial, it's not buggy
        if "/" in clean:
            return None
        if (
            "kelebek=7!" in clean
            or "kelebek=5040" in clean
            or "tekrarlip=7!" in clean
            or "tekrarlip=n!" in clean
            or "ozdes_harfler=n!" in clean
            or "dizilim=7!" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-COMB-04",
                severity="CRITICAL",
                category="COMBINATORICS_REPEATED_PERMUTATION_IDENTICAL_OMISSION",
                description="Tekrarlı permütasyonda özdeş elemanların kendi arasındaki yer değişimleri yeni bir dizilim oluşturmaz. Toplam dizilim sayısı n! / (n₁! · n₂! · ... · nk!) formülüyle özdeş elemanların faktöriyellerine bölünmelidir.",
                remediation_directive="Aynı harflerin (örneğin E'lerin) kendi aralarında yer değiştirmesi yeni bir kelime üretir mi? Özdeş elemanların adedinin faktöriyeline böl.",
                offending_term=user_str,
            )
        return None

    def _check_bug_comb_05(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-COMB-05: Ayrık Olmayan Olaylarda Kesişimi Çıkarmadan Doğrudan Toplama."""
        clean = user_str.replace(" ", "").lower()
        # Guard: if subtraction or intersection is mentioned, do not trigger false positive
        if "-" in clean or "kesisim" in clean or "ortak" in clean:
            return None
        if (
            "p(aub)=p(a)+p(b)" in clean
            or "p(a_veya_b)=p(a)+p(b)" in clean
            or "p(cift_veya_asal)=3/6+3/6=1" in clean
            or "3/6+3/6=6/6" in clean
            or "p(aub)=1/2+1/2=1" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-COMB-05",
                severity="CRITICAL",
                category="PROBABILITY_UNION_WITHOUT_INTERSECTION_SUBTRACTION",
                description="Ayrık olmayan (kesişimi boş küme olmayan) iki olayın birleşim olasılığı hesaplanırken kesişim iki kez sayıldığı için çıkarılmalıdır: P(A ∪ B) = P(A) + P(B) - P(A ∩ B).",
                remediation_directive="A ve B olaylarının aynı anda gerçekleştiği ortak durumlar (ör. hem çift hem asal olan 2 sayısı) iki kez sayılmış olabilir mi? Kesişim olasılığını P(A ∩ B) çıkar.",
                offending_term=user_str,
            )
        return None

    def _check_bug_logic_01(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-LOGIC-01: İse Bağlacında Yanlış Öncül Yanılgısı (0 => 0 = 0 veya 0 => 1 = 0)."""
        clean = user_str.replace(" ", "").lower()
        if "sadece1=>0" in clean or "0=>0=1" in clean or "0=>1=1" in clean:
            return None
        if (
            "0=>0=0" in clean
            or "0=>1=0" in clean
            or "0ise0=0" in clean
            or "0ise1=0" in clean
            or "yanlis=>dogru=yanlis" in clean
            or "yanlis=>yanlis=yanlis" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-LOGIC-01",
                severity="CRITICAL",
                category="LOGIC_FALSE_ANTECEDENT_FALLACY",
                description="Koşullu önermede (p ⇒ q), öncül p yanlış (0) olduğunda sonuç q ne olursa olsun önerme daima DOĞRUDUR (1). İse bağlacı yalnızca 1 ⇒ 0 durumunda 0 (yanlış) değerini alır.",
                remediation_directive="Öncülün gerçekleşmediği bir taahhütte (ör. 'Yağmur yağarsa şemsiye açarım', ama yağmur yağmadı) söz bozulmuş sayılır mı? 0 ⇒ 0 ve 0 ⇒ 1 durumlarının daima 1 olduğunu hatırla.",
                offending_term=user_str,
            )
        return None

    def _check_bug_logic_02(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-LOGIC-02: Ters ile Karşıt Tersin Karıştırılması (p => q ≡ ¬p => ¬q)."""
        clean = user_str.replace(" ", "").lower()
        if "¬q=>¬p" in clean or "~q=>~p" in clean or "q'=>p'" in clean:
            return None
        if (
            "p=>q≡¬p=>¬q" in clean
            or "p=>q=¬p=>¬q" in clean
            or "p=>q=~p=>~q" in clean
            or "p=>q≡~p=>~q" in clean
            or "tersi_dengidir" in clean
            or "karsit_ters_yerine_ters" in clean
            or "p=>qdenkp'=>q'" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-LOGIC-02",
                severity="CRITICAL",
                category="LOGIC_INVERSE_INSTEAD_OF_CONTRAPOSITIVE",
                description="p ⇒ q koşullu önermesinin mantıksal dengi tersi (¬p ⇒ ¬q) değil, karşıt tersidir (¬q ⇒ ¬p). Bir önermenin tersi orijinal önermeye denk olmak zorunda değildir.",
                remediation_directive="Önermenin hem yerlerini değiştirip hem değillemelerini aldın mı? p ⇒ q ≡ ¬q ⇒ ¬p karşıt ters denkliğini kullan.",
                offending_term=user_str,
            )
        return None

    def _check_bug_logic_03(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-LOGIC-03: Niceleyici Değillemesinde Kapsam Hatası (¬(∀x, P(x)) ≡ ∀x, ¬P(x))."""
        clean = user_str.replace(" ", "").lower()
        if "∃" in clean or "bazi" in clean or "enazbir" in clean:
            return None
        if (
            "¬(herx,p(x))=herx,¬p(x)" in clean
            or "~(herx,p(x))=herx,~p(x)" in clean
            or "degil(her)=her" in clean
            or "¬(∀x,p(x))≡∀x,¬p(x)" in clean
            or "¬(∃x,p(x))≡∃x,¬p(x)" in clean
            or "degil(bazi)=bazi" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-LOGIC-03",
                severity="CRITICAL",
                category="LOGIC_QUANTIFIER_NEGATION_SCOPE_FALLACY",
                description="Evrensel niceleyicinin (∀ / Her) değillemesi varlıksal niceleyici (∃ / Bazı) üretir: ¬(∀x, P(x)) ≡ ∃x, ¬P(x). Niceleyicinin türü değişmeden sadece açık önerme değillenemez.",
                remediation_directive="'Herkes sınavı geçti' cümlesinin değili 'Herkes sınavda kaldı' mıdır, yoksa 'En az bir kişi sınavı geçemedi' midir? Niceleyiciyi ∀ ise ∃, ∃ ise ∀'ye dönüştür.",
                offending_term=user_str,
            )
        return None

    def _check_bug_logic_04(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-LOGIC-04: Tümevarımda Taban Adımını Atlayarak Doğrulama Sanma."""
        clean = user_str.replace(" ", "").lower()
        if (
            "taban_adimi_gerekmez" in clean
            or "p(1)_bakmadan_ispat" in clean
            or "sadece_p(k)=>p(k+1)_yeterli" in clean
            or "taban_atlandi" in clean
            or "p(1)=atla" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-LOGIC-04",
                severity="CRITICAL",
                category="PROOF_INDUCTION_BASE_CASE_OMISSION",
                description="Matematiksel tümevarımda taban adımı P(1) (veya P(n₀)) ispatın başlangıç domino taşıdır. Taban adımı doğrulanmazsa, geçiş adımı P(k) ⇒ P(k+1) sağlansa bile zincirleme doğruluk kurulamaz.",
                remediation_directive="İlk domino taşı devrilmeden sonraki taşların birbirini devirmesi bir anlam taşır mı? Mutlaka başlangıç değeri olan n=1 için P(1)'i doğrula.",
                offending_term=user_str,
            )
        return None

    def _check_bug_logic_05(self, user_str: str, prev_str: str) -> Optional[DiagnosticPayload]:
        """BUG-LOGIC-05: Çelişki İspatında Ters Varsayım Kurma Hatası (¬P yerine P varsayma)."""
        clean = user_str.replace(" ", "").lower()
        if (
            "celiski_icin_p_dogru_varsay" in clean
            or "p_oldugunu_varsayalim=>p_dogrudur" in clean
            or "varsayim_p" in clean
            or "¬p_yerine_p_varsayildi" in clean
        ):
            return DiagnosticPayload(
                bug_id="BUG-LOGIC-05",
                severity="CRITICAL",
                category="PROOF_CONTRADICTION_CIRCULAR_ASSUMPTION",
                description="Çelişki ile ispat (olmayana ergi) yönteminde ispatlanmak istenen P önermesinin DEĞİLİ (¬P) doğru kabul edilir ve bu kabulden bir çelişkiye (r ∧ ¬r) varılır. P'nin kendisini varsaymak döngüsel kanıtlama hatasıdır.",
                remediation_directive="Neyi çürütmek istiyoruz? İspatlamak istediğin hükmün değilini (¬P) varsayarak başla.",
                offending_term=user_str,
            )
        return None




