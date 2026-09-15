# ⚠️ BÖLÜM 5: 15 TEMEL KÖK YANILGI KATALOĞU (`BUG-FOUND-01..15`)

Bu goal, öğrencilerin en sık düştüğü 15 kök kavram yanılgısını deterministik olarak yakalayan, öğrencinin adımını ayrıştıran ve anında Bilişsel Zaaf Defterine işleyen teşhis motorunu kapsar.

---

## ⚡ ÇALIŞTIRILABİLİR /goal KOMUTU

```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Bölüm 5 "15 Temel Kök Yanılgı Kataloğu (BUG-FOUND-01..15)" paketini uçtan uca uygula ve doğrula:

1. 15 Deterministik Kök Yanılgı Kuralının İmplementasyonu:
   - BUG-FOUND-01: Çift Eksi Tuzağı (-(-4) = -4 sanma).
   - BUG-FOUND-02: İşlem Önceliği Körlüğü (3 + 4 * 2 = 14 bulma).
   - BUG-FOUND-03: Kuvvet ile İşaret Çelişkisi (-3^2 = 9 yazma).
   - BUG-FOUND-04: Kesir Düz Toplama Hatası (1/2 + 1/3 = 2/5).
   - BUG-FOUND-05: Yarım Dağılma Hatası (2(x + 3) = 2x + 3).
   - BUG-FOUND-06: Toplama/Çarpma Karışıklığı (x + x = x^2).
   - BUG-FOUND-07: Katsayıyı Çıkarma Sanma (3x = 12 => x = 9).
   - BUG-FOUND-08: Elma ile Armudu Toplama (2x + 3 = 5x).
   - BUG-FOUND-09: Üs ile Tabanı Çarpma (2^3 = 6).
   - BUG-FOUND-10: Negatif Sıralama Yanılgısı (-8 > -3).
   - BUG-FOUND-11: Sıfıra Bölme Hatası (5/0 = 0 veya 5).
   - BUG-FOUND-12: Eksi Parantez Dağılma (-(x - 4) = -x - 4).
   - BUG-FOUND-13: Fonksiyonu Sayı Sanma (f(3) = 23).
   - BUG-FOUND-14: Eşitsizlikte Yön Unutma (-2x < 6 => x < -3).
   - BUG-FOUND-15: Tek Taraflı Terazi Hatası (x + 4 = 10 => x = 10).
2. AST Seviyesinde Hata Yakalama:
   - SymPy AST karşılaştırması ile öğrencinin ara adımındaki matematiksel ifadeyi analiz et; eşleşen kök yanılgıyı mikro-saniyeler içinde etiketle.
3. Zaaf Defteri ve Otopsi Entegrasyonu:
   - Yakalanan yanılgıyı öğrencinin seans profiline kaydet ve geriye dönük telafi oturumu planla.
4. En az 35 yeni test ile %100 doğruluk ve 0 False Positive sağla.
```

---

## 📋 Beklenen Teslimatlar
- `services/core-engine/engine/diagnostics/root_misconception_catalog.py`
- `services/core-engine/tests/test_root_misconceptions.py`
