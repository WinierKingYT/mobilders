# 🔹 HEDEF 8: DEFTERDEN/KİTAPTAN SORU FOTOĞRAFLAMA VE SOKRATİK HATA TEŞHİS KAMERASI

---

## ⚡ ÇALIŞTIRILABİLİR /goal KOMUTU

```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 8 kapsamındaki "Defterden/Kitaptan Soru Fotoğraflama ve Sokratik Hata Teşhis Kamerası" paketini uygula ve doğrula:

1. Mobil Kamera Arayüzü:
   - Flutter mobil istemcide kamera ile soru veya el yazısı defter adımı çekme arayüzü (MathScannerView).
2. Vision/OCR Pipeline:
   - Görüntüden LaTeX ve cebirsel adım çıkarımı; ham görüntüyü sırayla adımlara bölen segmentasyon.
3. Sokratik Hata Teşhisi (Antitezi Photomath):
   - Doğrudan cevabı vermek KESİNLİKLE YASAKTIR.
   - Soruyu CAS ile parse edip ilgili DAG düğümüne bağla; defterdeki ara adımları analiz ederek hangi adımda hangi Buggy Rule'a düşüldüğünü tespit et.
   - Öğrenciye: "3. adımda eksi işaretini dağıtırken bir hata yapmışsın, orayı kontrol etmek ister misin?" şeklinde yönlendir.
4. Zero-Leakage Kalkanı:
   - Taranan sorunun nihai sonucunun istemciye sızdırılmasını regex/AST seviyesinde engelle.
5. Entegrasyon ve sentetik görüntü testleri ile doğrula.
```
