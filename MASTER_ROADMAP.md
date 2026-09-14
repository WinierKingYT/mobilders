# KİŞİSEL ÖĞRENME MOTORU (PLE) — MASTER YOL HARİTASI
## Bilişsel Matematik İşletim Sistemi — 14 Kademeli Tam Müfredat ve Teknoloji Planı

Bu belge, Kişisel Öğrenme Motoru'nun lise ve üniversite hazırlık matematiğini (9-12. Sınıf, YKS, IB DP, AP Calculus) %100 kapsayan ve bilişsel öğrenme bilimi ilkeleriyle çalışan nihai yol haritasıdır.

---

## 🗺️ MASTER YOL HARİTASI GENEL BAKIŞ

```text
[ FAZ I: ALTYAPI VE MOBİL SAĞLAMLAŞTIRMA ]
  └── HEDEF 1: Üretim Hazırlığı, Çevrimdışı Kalıcılık ve Mobil E2E Sağlamlaştırma

[ FAZ II: TAM LİSE MATEMATİK MÜFREDATI (CEBİR & ANALİZ) ]
  ├── HEDEF 2: Müfredat Faz A — Paraboller, 2. Dereceden Fonksiyonlar ve Polinomlar (Cebir II)
  ├── HEDEF 3: Müfredat Faz B — Trigonometri, Logaritma ve Üstel Fonksiyonlar (İleri Fonksiyonlar)
  ├── HEDEF 4: Müfredat Faz C — Limit, Süreklilik ve Türev (Kalkülüs I / Diferansiyel Analiz)
  └── HEDEF 6: Müfredat Faz D — İntegral ve Alan Hesabı (Kalkülüs II / Tam Analiz)

[ FAZ III: MULTIMODAL ETKİLEŞİM VE DIŞ DÜNYA BAĞLANTISI ]
  ├── HEDEF 5: Defterden/Kitaptan Soru Fotoğraflama ve Sokratik Hata Teşhis Kamerası (OCR Scanner)
  └── HEDEF 8: Yeni Nesil Hikayeli Problemler ve Modelleme Motoru (Word Problems & Modeling)

[ FAZ IV: GEOMETRİ VE ŞEKİLSEL DÜŞÜNME ]
  ├── HEDEF 7: Analitik Geometri ve Vektörler Motoru (Koordinat Geometrisi)
  └── HEDEF 12: Sentetik Öklid Geometrisi ve Akıllı Ek Çizim Motoru (Visual Geometry)

[ FAZ V: BİLİŞSEL DERİNLİK, İSPAT VE İÇERİK FABRİKASI ]
  ├── HEDEF 9: Kişisel "Hata Otopsisi" Kasası ve Akıllı Zaaf Avcısı (Cognitive Mistake Vault)
  ├── HEDEF 10: Bilişsel Tuzaklı Sonsuz Soru Üretim Fabrikası (Dynamic Item Generator)
  ├── HEDEF 11: Olasılık, Kombinatorik ve İstatistik Motoru (Ayrık Matematik & Monte Carlo)
  ├── HEDEF 13: Matematiksel İspat ve Mantık Laboratuvarı ("Nedenini Anla" - Proof Engine)
  └── HEDEF 14: Yaşayan Kişisel Matematik Atlası ve Zihin Haritası Gezgini (Interactive Knowledge Navigator)
```

---

## 📋 TÜM HEDEFLER İÇİN ÇALIŞTIRILABİLİR /goal ŞABLONLARI

Aşağıdaki şablonları dilediğiniz zaman kopyalayıp sohbete `/goal <İÇERİK>` şeklinde göndererek ilgili hedefin geliştirme döngüsünü başlatabilirsiniz.

---

### 🔹 HEDEF 1: Üretim Hazırlığı, Çevrimdışı Kalıcılık ve Mobil E2E Sağlamlaştırma
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 1 kapsamındaki "Üretim Hazırlığı, Çevrimdışı Kalıcılık ve Mobil E2E Entegrasyonu" paketini uçtan uca uygula ve doğrula.
- Working tree temizliği (Inking, LTI, Ses, Erişilebilirlik ve testlerini mantıksal bir git commit'i ile kaydet).
- 23-OFFLINE-STATE-AND-SYNC uyarınca mobil tarafta kalıcı yerel kuyruk (OfflineSyncQueue) oluştur; ağ koptuğunda adımları diske yaz, ağ gelince idempotent aktar.
- VectorInkingCanvas, TunnelFocusMode ve DyscalculiaHelper bileşenlerini DailyJourneyScreen ve ayarlar çekmecesine bağla.
- Tüm mobil ve backend (123 test) testlerinin %90+ coverage ile yeşil geçtiğini doğrula.
```

---

### 🔹 HEDEF 2: Müfredat Faz A — Paraboller, 2. Dereceden Fonksiyonlar ve Polinomlar
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 2 kapsamındaki "Paraboller, İkinci Dereceden Fonksiyonlar ve Polinomlar" müfredat genişlemesini uygula ve doğrula.
- Bilgi Grafı Genişlemesi: N27-N38 (Parabol tepe noktası, simetri ekseni, kök geometrisi) ve N39-N50 (Polinom bölmesi, kalan teoremi, katsayılar toplamı).
- 10 Yeni Yanılgı Kuralı: BUG-PARAB-01..05 (-b/2a formülü eksi işareti, simetri ekseni yanılgısı) ve BUG-POLY-01..05 (bölümde sahte kök, derece karışıklığı).
- SymPy CAS motorunda fonksiyon dönüşümleri ve polinom sadeleştirmelerini güvenli AST sandbox içinde destekle.
- 40 yeni birim testi yazarak 0 False Positive ve %90+ coverage sağla.
```

---

### 🔹 HEDEF 3: Müfredat Faz B — Trigonometri, Üstel ve Logaritmik Fonksiyonlar
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 3 kapsamındaki "Trigonometri, Logaritma ve Üstel Fonksiyonlar" genişlemesini uçtan uca uygula ve doğrula.
- Bilgi Grafı Genişlemesi: N51-N65 (Birim çember, oranlar, özdeşlikler, indirgeme, trigonometrik denklemler) ve N66-N80 (Üstel model, logaritma kuralları, taban değiştirme, logaritmik denklemler).
- 10 Yeni Yanılgı Kuralı: BUG-TRIG-01..05 (Lineerlik tuzağı sin(a+b)=sin a+sin b, isim sadeleştirme, periyot/kök kaybı) ve BUG-LOG-01..05 (Dağılma tuzağı, kuvvet kuralı hatası, negatif tanım kümesi ihmali).
- SymPy CAS'a sin, cos, tan, log, ln, exp operasyonlarını güvenli ekle; tanım kümesi denetleyicisi (evaluate_domain_constraints) yaz.
- Mobil tarafta Al-Harezmi karolarının yanına interaktif Birim Çember Kanvası (UnitCircleCanvas) ekle.
- 50 yeni test ile 170+ toplam yeşil test ve %90+ coverage sağla.
```

---

### 🔹 HEDEF 4: Müfredat Faz C — Limit, Süreklilik ve Türev (Kalkülüs I)
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 4 kapsamındaki "Limit, Süreklilik ve Türev (Kalkülüs I)" paketini uçtan uca uygula ve doğrula.
- Bilgi Grafı Genişlemesi: N81-N110 (Limit sezgisel tanımı, sağ-sol limit, 0/0 belirsizliği, çarpanlara ayırma ve L'Hôpital, süreklilik, türevin limit tanımı, türev alma kuralları [çarpım, bölüm, zincir kuralı], teğet denklemi ve yerel ekstremumlar).
- 10 Yeni Yanılgı Kuralı: BUG-CALC-01..05 (Zincir kuralında iç türevi unutma [d/dx f(g(x)) = f'(g(x))], bölüm türevinde eksi işareti ve payda karesi hatası, 0/0 belirsizliğini "tanımsız" deyip bırakma, türevin sıfır olduğu her noktayı mutlak ekstremum sanma).
- CAS Genişlemesi: SymPy Limit ve Derivative nesnelerini güvenli AST sandbox'a bağla; adım adım türev alma kurallarını doğrula.
- Mobil Görsel Kanvas: Ekranda fonksiyon grafiği üzerinde h/delta_x sıfıra yaklaşırken teğetin oluşumunu gösteren Dinamik Teğet Eğimi Kanvası (DynamicTangentCanvas) geliştir.
- 50 yeni birim testi koşturarak sıfır hata ve %90+ coverage sağla.
```

---

### 🔹 HEDEF 5: Defterden/Kitaptan Soru Fotoğraflama ve Sokratik Hata Teşhis Kamerası
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 5 kapsamındaki "Defterden/Kitaptan Soru Fotoğraflama ve Sokratik Hata Teşhis Kamerası" paketini uygula ve doğrula.
- Mobil Kamera Arayüzü: Flutter mobil istemcide kamera ile soru veya el yazısı defter adımı çekme arayüzü (MathScannerView).
- Vision/OCR Pipeline: Görüntüden LaTeX ve cebirsel adım çıkarımı; ham görüntüyü sırayla adımlara bölen segmentasyon.
- Sokratik Hata Teşhisi (Antitezi Photomath): Doğrudan cevabı vermek YASAKTIR.
  1. Soruyu CAS ile parse edip Bilgi Grafı'ndaki ilgili düğüme bağla.
  2. Öğrencinin defterindeki ara adımları analiz edip hangi adımda hata yaptığını ve hangi Buggy Rule'a düştüğünü tespit et.
  3. Öğrenciye: "3. adımda eksi işaretini dağıtırken bir hata yapmışsın, orayı tekrar kontrol etmek ister misin?" şeklinde Sokratik yönlendirme sun.
- Zero-Leakage Kalkanı: Taranan sorunun nihai sonucunun istemciye sızdırılmasını regex/AST seviyesinde engelle.
- Entegrasyon testleri ve sentetik görüntü testleri ile doğrula.
```

---

### 🔹 HEDEF 6: Müfredat Faz D — İntegral ve Alan Hesabı (Kalkülüs II)
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 6 kapsamındaki "İntegral ve Alan Hesabı (Kalkülüs II)" paketini uçtan uca uygula ve doğrula.
- Bilgi Grafı Genişlemesi: N111-N135 (Belirsiz integral, integrasyon sabitinin anlamı, temel integrasyon kuralları, değişken değiştirme [u-substitution], kısmi integrasyon [uv - int v du], Riemann alt/üst toplamları, Belirli İntegral [Kalkülüsün Temel Teoremi], iki eğri arasında kalan alan).
- 10 Yeni Yanılgı Kuralı: BUG-INT-01..05 (İntegrasyon sabiti +C'yi unutma, değişken değiştirmede dx'i du'ya çevirmeden integralleme, belirli integralde F(b)-F(a) yerine ters çıkarma, x ekseninin altında kalan alanda negatif sonucu doğrudan alan kabul etme).
- SymPy CAS İntegral Doğrulayıcı: Hem sembolik integrali hem de adım adım değişken dönüşümlerini AST seviyesinde denetleyen güvenli motor.
- Mobil Riemann Kanvası: Eğrinin altına dikdörtgenler yerleştirerek n sonsuza giderken alanın integrale yakınsamasını görselleştiren RiemannIntegralCanvas.
- 45 yeni test ile tüm kalkülüs paketinin yeşil geçtiğini doğrula.
```

---

### 🔹 HEDEF 7: Analitik Geometri ve Vektörler Motoru
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 7 kapsamındaki "Analitik Geometri ve Vektörler Motoru" paketini uygula ve doğrula.
- Bilgi Grafı Genişlemesi: N136-N160 (Noktanın analitiği, iki nokta arası uzaklık, orta nokta, doğrunun eğimi ve denklemi, paralel ve dik doğruların eğim bağıntıları, noktanın doğruya uzaklığı, çemberin standart denklemi (x-a)^2 + (y-b)^2 = r^2, 2B vektörler ve iç çarpım).
- Yanılgı Katalogları: BUG-ANAG-01..05 (Dik doğrularda m1*m2=-1 kuralını m1=m2 sanma, eğim açısı geniş açı olduğunda eğimi pozitif alma, çember merkez koordinatlarının işaretlerini formülde ters okuma).
- Mobil İnteraktif Koordinat Kanvası (InteractiveCoordinateCanvas): Öğrencinin noktaları sürükleyip doğru denkleminin ve çember yarıçapının gerçek zamanlı değişimini gördüğü dokunmatik kanvas.
- 40 yeni test ile koordinat ve cebir doğrulamasını tamamla.
```

---

### 🔹 HEDEF 8: Yeni Nesil Hikayeli Problemler ve Modelleme Motoru
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 8 kapsamındaki "Yeni Nesil Hikayeli Problemler ve Modelleme Motoru" paketini uygula ve doğrula.
- Kapsam: Yaş, hareket (hız-zaman-yol), yüzde-kâr-zarar, işçi-havuz ve optimizasyon problemleri.
- Modelleme İskelesi: Paragraf halindeki problemi doğrudan çözmek yerine 3 aşamalı Sokratik Modelleme akışı kur:
  1. Değişkenleri Tanımla ("Hangi bilinmeyene x demeliyiz?")
  2. Eşitliği Kur ("Metindeki hangi ifade denklemin sağ tarafını oluşturur?")
  3. CAS ile Adım Adım Çöz.
- Görsel Şematik Modelleme: Hareket problemleri için otomatik zaman-yol çizgisi, karışım/yüzde problemleri için kap şeması üreten dinamik görselleştirici.
- 10 yeni modelleme kavram yanılgısı kuralı (BUG-PROB-01..05) ve 40 test ile doğrula.
```

---

### 🔹 HEDEF 9: Kişisel "Hata Otopsisi" Kasası ve Akıllı Zaaf Avcısı
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 9 kapsamındaki "Kişisel Hata Otopsisi (Mistake Vault) ve Akıllı Zaaf Avcısı" paketini uygula ve doğrula.
- Hata Kasası Veri Modeli: Öğrencinin çözümlerde veya Hedef 5 kamerasında düştüğü tüm bozuk kuralları (BUG-xxxx) zaman damgası, konu düğümü ve tam adım bağlamıyla SQLite/Postgres üzerinde sakla.
- Kendi Kendini Düzeltme Seansı (Self-Correction Session): Öğrencinin geçmişte yaptığı hatalı adımı önüne çıkarıp: "3 gün önce bu adımda bir hata yapmıştın. Kendi hatanı bulup düzeltebilir misin?" diyen üstbilişsel arayüz.
- FSRS-4.5 Zaaf Adaptasyonu: Unutma eğrisi motorunu öğrencinin en sık hata yaptığı bozuk kurallarla eşleştir; haftalık "Boss Battle" tekrar oturumları üret.
- 35 test ve simülasyon doğrulaması ile tamamla.
```

---

### 🔹 HEDEF 10: Bilişsel Tuzaklı Sonsuz Soru Üretim Fabrikası
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 10 kapsamındaki "Bilişsel Tuzaklı Sonsuz Soru Üretim Fabrikası (Dynamic Item Generator & Exam Maker)" paketini uygula ve doğrula.
- CAS Tabanlı Dinamik Üretici: Sadece rastgele sayı üreten değil; öğrencinin zayıf olduğu Buggy Rule'u tetikleyecek özel çeldiricili sorular sentezleyen ters-SymPy jeneratörü.
- Formel Kanıt: Üretilen her sorunun tam sayı köklere sahip olduğunu ve çözüm adımlarının %100 geçerli olduğunu SymPy ile formel olarak kanıtla.
- Deneme Sınavı & PDF Export: Tek tıkla LaTeX kalitesinde temiz, çözümlü PDF çalışma yaprağı ve deneme sınavı üretme motoru.
- 30 test ve 500 sentetik soru üretim testi ile doğrula.
```

---

### 🔹 HEDEF 11: Olasılık, Kombinatorik ve İstatistik Motoru (Ayrık Matematik)
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 11 kapsamındaki "Olasılık, Kombinatorik ve İstatistik Motoru" paketini uygula ve doğrula.
- Bilgi Grafı: Permütasyon, Kombinasyon, Faktöriyel cebiri, Binom açılımı, Basit ve Koşullu Olasılık, Bayes Teoremi, Beklenen Değer.
- Sezgisel Hata Dedektörleri: BUG-COMB-01..05 (Sıralama ile seçmeyi karıştırma, tekrarlı permütasyonda özdeş elemanı bölmeme, bağımsız olay çarpımı hatası).
- Canlı Monte Carlo Doğrulayıcı: Öğrencinin teorik sonucunu anında 100.000 sanal deneyle simüle eden ve ampirik frekansı gösteren simülasyon motoru.
- İnteraktif Sayma Ağacı & Venn Şeması Kanvası.
- 40 test ile doğrula.
```

---

### 🔹 HEDEF 12: Sentetik Öklid Geometrisi ve Akıllı Ek Çizim Motoru
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 12 kapsamındaki "Sentetik Öklid Geometrisi ve Akıllı Ek Çizim Motoru" paketini uygula ve doğrula.
- Kapsam: Üçgende açılar, kenarortay, açıortay, benzerlik teoeremleri (Thales, Kelebek), dik üçgen bağıntıları (Öklid, Pisagor), çemberde açılar ve kirişler.
- Geometrik Kısıt Çözücü: Ekrana çizilen şeklin geometrik tutarlılığını (açı toplamı 180, kenar eşitsizliği) doğrulayan motor.
- Sokratik Ek Çizim İskelesi: Öğrenci tıkandığında çizgiyi doğrudan çekmek yerine: "Bu ikizkenar üçgenin tabanına dik inersek taban nasıl bölünür?" diyerek ek çizimi öğrenciye yaptıran rehber.
- Serbest Dokunmatik Geometri Kanvası (EuclideanCanvas).
- 40 test ile doğrula.
```

---

### 🔹 HEDEF 13: Matematiksel İspat ve Mantık Laboratuvarı ("Nedenini Anla")
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 13 kapsamındaki "Matematiksel İspat ve Mantık Laboratuvarı" paketini uygula ve doğrula.
- Kapsam: Önermeler mantığı, doğruluk tabloları, niceleyiciler, Tümevarım ile ispat, Olmayana Ergi (Çelişki) ile ispat, Karşıt-Ters yöntemi.
- Adım Adım Mantık Denetleyicisi: Öğrencinin bir hipotezden başlayıp adım adım teorem türettiği ve motorun her adımın mantıksal geçerliliğini (Modus Ponens) denetlediği ispat sandbox'ı.
- Temel Teorem İspat Kataloğu: Karekök 2'nin irrasyonelliği, asal sayıların sonsuzluğu, Gauss toplam formülü vb.
- 35 test ile doğrula.
```

---

### 🔹 HEDEF 14: Yaşayan Kişisel Matematik Atlası ve Zihin Haritası Gezgini
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 14 kapsamındaki "Yaşayan Kişisel Matematik Atlası ve Zihin Haritası Gezgini" paketini uygula ve doğrula.
- Bütünleşik Bilgi Grafı (N01 - N160): Tüm lise matematiğinin birbirine bağlandığı organik bir 2B/3B Zihin Ağı (Knowledge Graph Navigator).
- Dinamik Zihinsel Durum: Öğrencinin BKT posterior ustalığına göre yeşil/sarı/kırmızı parıldayan, zayıf önkoşul köprülerini gösteren interaktif harita.
- Konular Arası Köprüler: Parabol tepe noktasından Türev teğetine, Diskriminanttan İkinci Dereceden Kök formülüne uzanan canlı kavramsal bağlantılar.
- Mobil donanım hızlandırmalı graf görselleştiricisi ve 30 test ile doğrula.
```

---
*Bu belge projenin kalıcı ana yol haritasıdır. İhtiyaç duyulduğunda ilgili hedefin /goal bloğu kopyalanıp doğrudan çalıştırılabilir.*
