# 🎯 BÖLÜM 2: TAKILMA ANINDA SOKRATIK METOT ANLATIMI

Bu goal, öğrenci bir adımda takıldığında sonucu asla söylemeyen, 3 aşamalı sezgi buldurma akışını (Grounding -> Socratic Question -> Student Self-Discovery) garanti altına alır.

---

## ⚡ ÇALIŞTIRILABİLİR /goal KOMUTU

```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Bölüm 2 "Takılma Anında Sokratik Metot Anlatımı (Yöntemi Bulduran Akış)" paketini uçtan uca uygula ve doğrula:

1. Zero-Leakage & Sıfır Sonuç Prensibi:
   - Sokratik rehberlik sırasında nihai cevabı vermek KESİNLİKLE YASAKTIR.
   - Cevap kaçaklarını regex ve AST filtreleriyle engelle.
2. 3 Aşamalı Sezgi İskelesi:
   - Aşama 1: Durum kabulü ve empati ("Harika geldin, sona çok yaklaştın!").
   - Aşama 2: Minik bir sezgi örneği (Grounding - örn: $2 < 5$ iken $-2 > -5$ olduğunu sayı doğrusunda hissettirme).
   - Aşama 3: Kuralı öğrenciye bizzat buldurma ("Negatif sayıya böldüğünde eşitsizlik yön değiştirmeli; sence şimdi ne olmalı?").
3. Eşitsizliklerde Negatif Bölme, Parantez Dağıtma ve Kesir Eşitleme Sokratik Şablonları:
   - En sık takılınan 10 kritik matematiksel eşik için deterministik sezgi iskeleleri oluştur.
4. Mobil İnteraktif Sokratik Dialog Balonu:
   - Öğrenciye çoktan seçmeli ipucu değil, serbest klavye/touchpad üzerinden keşfi tamamlatan UI akışı sun.
5. En az 25 yeni test ile pedagojik FSM durum geçişlerini ve sıfır sızıntıyı doğrula.
```

---

## 📋 Beklenen Teslimatlar
- `services/core-engine/engine/pedagogy/socratic_method_scaffold.py`
- `apps/mobile/lib/ui/features/session/widgets/socratic_hint_dialog.dart`
- `services/core-engine/tests/test_socratic_scaffold.py`
