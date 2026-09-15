# KİŞİSEL ÖĞRENME MOTORU (PLE) — MASTER YOL HARİTASI
## Bilişsel Matematik İşletim Sistemi — Sıfırdan Zirveye Tam Pedagoji, Akış ve Müfredat Planı

Bu belge, Kişisel Öğrenme Motoru'nun (Personal Learning Engine - PLE) kuramsal, pedagojik, matematiksel ve yazılımsal mimarisini içeren nihai master yol haritasıdır.

**Temel Tasarım İlkesi (The First-User Dogfooding Invariant):**  
Bu sistemin ilk kullanıcısı, geliştiricisinin bizzat kendisidir. Sistem; hiçbir matematik temeli olmayan veya geçmişte matematikten kopmuş bir öğrenciyi en temel kavramlardan (sayı doğrusu, borç/alacak, değişken ve terazi sezgisi) alıp üniversite hazırlık zirvesine (Kalkülüs, İspat, Analitik Geometri) kadar **pasif anlatım olmaksızın, kendi çözüyormuş gibi** en yüksek hız ve kalitede öğretmek üzere tasarlanmıştır.

---

## 🧭 BÖLÜM 1: BİLİŞSEL ÖĞRETİM MANİFESTOSU VE HIZLI ÖĞRENME İLKELERİ

Geleneksel eğitim platformları (video izletenler veya doğrudan çözümü veren chatbotlar) beyni pasif bir izleyiciye dönüştürür ve "Anlama İllüzyonu" (*Illusion of Competence*) yaratır. PLE bu illüzyonu 6 katı pedagojik ilkeyle yıkar:

1. **Sıfır Pasif Monolog (Zero Passive Lecture):** Sistem asla 5 dakikalık bir video izletmez veya 3 paragraflık bir teorik metin okutmaz. Bilgi, sadece öğrencinin yapacağı bir sonraki eylemin gerekçesi olarak aktarılır.
2. **Aktif Birlikte Çözme (Active Co-Solving):** Konu anlatımı dahi bir problem çözme sürecidir. Sistem soruyu alt hedeflere böler; öğrenci her mikro adımı bizzat klavye veya kanvas üzerinden kendisi yazar.
3. **Bruner E-I-S Modeli (Concreteness Fading):** Her soyut cebirsel kavram 3 aşamalı somutluk sönümlemesinden geçer:
   - *Eylemsel (Enactive):* Sayı doğrusunda yürüme, terazi kefelerine ağırlık koyma, Al-Harezmi karolarını birleştirme.
   - *İkonik (Iconic):* Şematik alan taslakları, kutu modelleri, yönlü oklar.
   - *Sembolik (Symbolic):* Saf cebirsel gösterim ($2x + 3 = 11$).
4. **Anında Mikro-Zafer ve Dopamin Döngüsü (Micro-Triumph Loop):** Öğrenci sistemin desteğiyle bir adımı bulduğu anda, sistem arkasından aynı mantığı taşıyan küçük bir varyant verir ve desteksiz yaptırır. Beyin *"Bunu ben çözdüm"* başarısını tadar.
5. **Akıllı Tereddüt Sensörü (Cognitive Hesitation Sensor):** Öğrenci 8-10 saniye hareketsiz kaldığında (Ratcliff DDM drift hızı sıfırlandığında), sistem öğrenciyi boğmadan hafif bir parıltı veya tek cümlelik bir odaklama fısıltısı (*"Önce parantezin içindeki sayıya bakalım mı?"*) ile kilitlenmeyi çözer.
6. **"Nereden Geldi Bu?" Geri Sarım Düğmesi (Source Unpacker):** Öğrencinin kafası karıştığında tek dokunuşla o sayının veya terimin önceki hangi iki sayının çarpımından/toplamından doğduğunu gösteren mikro-animasyon devreye girer.

---

## 🎯 BÖLÜM 2: TAKILMA ANINDA METOT ANLATIMI (SONUCU DEĞİL, YÖNTEMİ BULDUGURAN AKIŞ)

Öğrenci bir soruda bir ara adımda takıldığında sistem **SONUCU ASLA VERMEZ**. Sonucu söylemek öğrenmeyi öldürür. Sistem **YÖNTEMİN SEZGİSİNİ** minik bir keşifle öğrenciye hissettirir.

### Somut Örnek: Eşitsizlikte Eksi Sayıya Bölme Takılması
**Soru:** $-3x + 5 \le 14$  
Öğrenci 5'i karşıya attı ve $-3x \le 9$ adımına geldi. Burada tıkandı veya yanlışlıkla $x \le -3$ yazdı.

```text
[ DURUM: ÖĞRENCİ TIKANDI / "NASIL YAPILIR?" BUTONUNA BASTI ]
                             │
                             ▼
[ 1. AŞAMA: CEVAP YOK, MANTIK SEZGİSİ VAR ]
AI Tutor: "Harika geldin, sona çok yaklaştın! 
Şimdi x'i yalnız bırakmak için her iki tarafı (-3)'e böleceğiz. 
Ama dur! Eşitsizliklerde negatif bir sayıya böldüğümüzde sihirli bir kural vardı..."
                             │
                             ▼
[ 2. AŞAMA: MİNİK BİR SEZGİ ÖRNEĞİ (GROUNDING) ]
AI Tutor: "Düşün bakalım: 2 sayısı 5'ten küçüktür (2 < 5). 
İki tarafı da (-1) ile çarparsak -2 ve -5 olur. 
Sayı doğrusunda -2 mi daha büyüktür, -5 mi?"
                             │
                             ▼
[ ÖĞRENCİ CEVAPLAR ]: "-2 daha büyüktür."
                             │
                             ▼
[ 3. AŞAMA: KURALI ÖĞRENCİYE KENDİSİNE BULDURMA ]
AI Tutor: "Gördün mü! Sayılar negatife dönünce küçüktür işareti BÜYÜKTÜR'e döndü. 
Yani negatif bir sayıya böldüğümüzde eşitsizlik işareti daima YÖN DEĞİŞTİRİR. 
Şimdi kendi soruna dön: Her iki tarafı -3'e böldüğünde ≤ işareti neye dönüşmeli?"
                             │
                             ▼
[ ÖĞRENCİ ADIMI KENDİSİ YAZAR ]: "x >= -3" (DOĞRULANDI ✓)
```

---

## 📚 BÖLÜM 3: GERİYE DOĞRU ZİNCİRLENMİŞ YAŞAYAN DERS NOTLARI
*(Explorable Prerequisite Notes — "Bunu Çözmek İçin Bu Lazım")*

Öğrenci soru çözerken takıldığında veya doğrudan konuyu sıfırdan öğrenmek istediğinde ekranda beliren yaşayan, tıklanabilir ders kartlarıdır. Statik PDF değildir; her not bir **"Önkoşul Merdiveni" (Prerequisite Chain)** barındırır:

```text
┌─────────────────────────────────────────────────────────────┐
│ 📖 DERS NOTU: 2. Dereceden Denklemler Nasıl Çözülür?        │
├─────────────────────────────────────────────────────────────┤
│ 💡 TEMEL FİKİR (1 Cümle):                                   │
│ "İçinde x² olan bir denklemin amacı, onu çarpanlarına        │
│  ayırarak İKİ TANE BASİT (1. Dereceden) denkleme bölmektir."│
│                                                             │
│ ⚠️ DİKKAT! BU KONUYU ANLAMAK İÇİN ŞUNLAR LAZIM:             │
│                                                             │
│ 🔗 1. Önkoşul: [ 1. Dereceden Denklem Nasıl Çözülür? ➔ ]   │
│    "x'i yalnız bırakmayı bilmiyorsan, x²'yi hiç çözemezsin. │
│     Durumun nasıl? [Emin Değilim, Buna Bak] [Biliyorum]"   │
│                                                             │
│ 🔗 2. Önkoşul: [ Çarpanlara Ayırma & Sıfır Çarpım ➔ ]       │
│    "İki sayının çarpımı 0 ise biri kesinlikle 0'dır."       │
│                                                             │
│ ─────────── 2. DERECEDEN DENKLEM ÇÖZÜM REÇETESİ ────────────│
│                                                             │
│ 1. ADIM: Eşitliğin sağını daima 0 yap (Terimleri sola topla)│
│    Örnek: x² + 5x = 6  ──►  x² + 5x - 6 = 0                 │
│                                                             │
│ 2. ADIM: Çarpanlarına ayır (İki parantez yap)              │
│    (x + 6)(x - 1) = 0                                       │
│                                                             │
│ 3. ADIM: Her parantezi AYRI AYRI 1. Dereceden denklem yap! │
│    x + 6 = 0  ──►  x = -6                                   │
│    x - 1 = 0  ──►  x = 1                                    │
│                                                             │
│ [ 🎮 10 Saniyelik Mini Alıştırma: Bir Tane Kendin Dene! ]   │
└─────────────────────────────────────────────────────────────┘
```

### 🔄 Geriye Doğru Temele İniş Örneği:
Öğrenci yukarıdaki notta *"1. Önkoşul: 1. Dereceden Denklem"* bağlantısına dokunduğunda:
1. Ekran 1. Dereceden denklemin **Terazi Modeline** iner.
2. Notun altında: *"Bunu yapabilmek için Negatif Sayılarda İşaretler lazım"* uyarısı çıkar.
3. Öğrenci oradan da **Negatif Sayılar** kartına inebilir.
4. Temeli anladığında **[ ⬅️ Anladım, Kaldığım Soruya Geri Dön ]** butonuna basarak adım adım lise sorusuna geri döner.

---

## 🌳 BÖLÜM 4: KÖK MATEMATİK ONTOLOJİSİ (SEVİYE -3'TEN SEVİYE 0'A KADAR TAM AĞ)

Lise konularında takılan bir öğrencinin sorunu %85 oranında lise matematiği değil, Seviye 0'ın altındaki bu 16 temel bilgi bileşenindeki (Knowledge Component - KC) görünmez deliklerdir:

```text
[ SEVİYE -3: SAYI HİSSİ, YÖN VE İŞARET SEZGİSİ ]
├── N_ROOT_01: Sayı Doğrusu ve Yön Sezgisi (Sıfırın sağı pozitif/kazanç, solu negatif/kayıp)
├── N_ROOT_02: Borç / Alacak ve Sıcaklık Modeli (-6 - 5 = -11; borcun büyümesi sezgisi)
├── N_ROOT_03: Zıt İşaretlerin Toplanması (-8 + 5 = -3; büyük olanın işaretinin baskınlığı)
└── N_ROOT_04: Çarpma ve Bölmede İşaret Kuralları ((+)·(-) = (-), (-)·(-) = (+); yön değiştirme kuralı)

[ SEVİYE -2.5: KESİRLER VE RASYONEL SEZGİ (ORAN-ORANTI TOHUMLARI) ]
├── N_ROOT_05: Kesir Bir Bölmedir (Pasta/Pizza dilimi, 1/4'ün 1 bütünün 4'e bölünmesi olduğu)
├── N_ROOT_06: Denk Kesirler ve Sadeleştirme (2/4 = 1/2 mantığı; pay ve paydayı aynı sayıyla ölçekleme)
└── N_ROOT_07: Ortak Payda Mantığı (Farklı büyüklükteki dilimler doğrudan toplanamaz: 1/2 + 1/3)

[ SEVİYE -2: İŞLEM ÖNCELİĞİ VE PARANTEZ SEZGİSİ ]
├── N_ROOT_08: Çarpmanın Önceliği Sezgisi (3 + 2 · 4 = 11; 2 tane 4'lük paket + 3 tek)
├── N_ROOT_09: Parantezin Koruyucu Kalkanı (Parantez içi tek bir sayı gibi işlem görür)
└── N_ROOT_10: Hediye Paketi Dağılma Özelliği (2(x + 4) = 2x + 8; paketteki her şeye 2 katı)

[ SEVİYE -1.5: ÜSLÜ VE KÖKLÜ SAYI TOHUMLARI ]
├── N_ROOT_11: Üs Bir Çarpma Sayacıdır (2³ = 2·2·2 = 8; asla 2·3 = 6 DEĞİLDİR)
└── N_ROOT_12: Karekök Alan Sezgisi (√25 = "Alanı 25 olan karenin bir kenarı kaçtır?")

[ SEVİYE -1: DEĞİŞKEN, EŞİTLİK VE TERAZİ SEZGİSİ (CEBİRİN DOĞUŞU) ]
├── N_ROOT_13: x Bir Harf Değil "Gizli Sayı Kutusu"dur (Kutunun içinde tek bir doğru sayı saklı)
├── N_ROOT_14: Örtük Çarpma (3x ifadesi "3 tane x" ya da 3 · x demektir, 30 küsur değildir)
├── N_ROOT_15: Terazi Modeli ile Denklem Çözme (Sol kefeden 5 alırsan, sağ kefeden de 5 almalısın)
└── N_ROOT_16: Fonksiyon Sezgisi (Girdi -> Kural Fabrikası -> Çıktı Modeli)
```

---

## ⚠️ BÖLÜM 5: 15 TEMEL KÖK YANILGI KATALOĞU (`BUG-FOUND-01..15`)

Sistem, öğrencinin adımlarını incelerken aşağıdaki 15 kök yanılgıyı deterministik olarak yakalar ve öğrencinin **Bilişsel Zaaf Defterine** işler:

| Kod | Yanılgı Adı | Öğrencinin Yaptığı Hata | Doğru Zihinsel Model |
| :--- | :--- | :--- | :--- |
| `BUG-FOUND-01` | **Çift Eksi Tuzağı** | $-(-4) = -4$ sanma | İki ters yön birbirini pozitife çevirir: $-(-4) = +4$. |
| `BUG-FOUND-02` | **İşlem Önceliği Körlüğü** | $3 + 4 \cdot 2 = 14$ bulma | Çarpma paket oluşturur; önce $4 \cdot 2 = 8$, sonra $3 + 8 = 11$. |
| `BUG-FOUND-03` | **Kuvvet ile İşaret Çelişkisi** | $-3^2 = 9$ yazma | Parantez yoksa üs sadece sayıya aittir: $-3^2 = -(3\cdot 3) = -9$. |
| `BUG-FOUND-04` | **Kesir Düz Toplama Hatası**| $\frac{1}{2} + \frac{1}{3} = \frac{2}{5}$ yazma | Farklı boyutlu dilimler toplanamaz; payda eşitlenmelidir ($5/6$). |
| `BUG-FOUND-05` | **Yarım Dağılma Hatası** | $2(x + 3) = 2x + 3$ yazma | Parantezdeki her eleman 2 ile çarpılmalıdır ($2x + 6$). |
| `BUG-FOUND-06` | **Toplama/Çarpma Karışıklığı** | $x + x = x^2$ sanma | $x+x = 2x$ (iki tane x); $x \cdot x = x^2$. |
| `BUG-FOUND-07` | **Katsayıyı Çıkarma Sanma** | $3x = 12 \implies x = 12 - 3 = 9$ | 3 ile x çarpım durumundadır; karşıya bölme geçer ($x = 12/3 = 4$). |
| `BUG-FOUND-08` | **Elma ile Armudu Toplama**| $2x + 3 = 5x$ yazma | Sabit sayı ile değişkenli terim toplanamaz; $2x + 3$ en sade haldedir. |
| `BUG-FOUND-09` | **Üs ile Tabanı Çarpma** | $2^3 = 6$ yazma | Üs kaç defa çarpılacağını söyler: $2 \cdot 2 \cdot 2 = 8$. |
| `BUG-FOUND-10` | **Negatif Sıralama Yanılgısı**| $-8 > -3$ sanma (8 büyük diye) | Sayı doğrusunda sola gidildikçe değer küçülür: $-8 < -3$. |
| `BUG-FOUND-11` | **Sıfıra Bölme Hatası** | $\frac{5}{0} = 0$ veya $5$ yazma | Sıfıra bölme tanımsızdır; $\frac{0}{5} = 0$'dır. |
| `BUG-FOUND-12` | **Eksi Parantez Dağılma** | $-(x - 4) = -x - 4$ yazma | Eksi içeri dağılırken tüm işaretleri ters çevirir: $-x + 4$. |
| `BUG-FOUND-13` | **Fonksiyonu Sayı Sanma** | $f(x) = 2x$ için $f(3) = 23$ yazma | 2 ile x çarpım durumundadır; $2 \cdot 3 = 6$'dır. |
| `BUG-FOUND-14` | **Eşitsizlikte Yön Unutma** | $-2x < 6 \implies x < -3$ yazma | Negatife bölerken eşitsizlik yön değiştirir: $x > -3$. |
| `BUG-FOUND-15` | **Tek Taraflı Terazi Hatası**| $x + 4 = 10 \implies x + 4 - 4 = 10$ | Terazi dengesi için her iki taraftan da 4 çıkarılmalıdır ($x = 6$). |

---

## 💎 BÖLÜM 6: UYGULAMA KALİTESİ, HAPTİK VE AKICILIK STANDARTLARI (MOBILE CRAFTSMANSHIP)

Uygulamanın zanaatkarlık kalitesi, Apple Design Award ve Linear standartlarında katı mühendislik ilkelerine dayanır:

1. **Haptik Dokunsal Geri Bildirim:** Tuş vuruşlarında hafif mekanik tık (`lightImpact`), doğru adımlarda çift vuruşlu zafer darbesi (`mediumImpact`), bozuk kuralda yumuşak ikaz titreşimi (`heavyImpact`).
2. **Sıfır Arayüz Sıçraması (Zero Layout Shift):** Touchpad, Klavye ve Çizim Kanvası geçişlerinde ekran zıplamaz; yay fiziği (`spring physics`) ile 60/120 FPS akıcı geçiş yapar.
3. **Sıfır Gecikmeli Yerel Denetim (<5ms):** Kullanıcı yazarken parantez eşleştirmeleri (Rainbow Brackets) ve geçersiz operatör kontrolleri sunucuyu beklemeden cihazda anında doğrulanır.
4. **Çökme Direnci & Durum Koruma (State Restoration):** Telefon çaldığında veya uygulama kapatıldığında seans, çözülen adımlar ve yarım kalan girdi tek bir harf dahi kaybolmadan geri yüklenir.
5. **Zen Odak Modu & KaTeX Mükemmelliği:** Dikkat dağıtan tüm menüleri gizleyen saf çalışma alanı; kesir çizgileri ve sembol oranları piksel düzeyinde optimize edilmiş TeX tipografisi.

---

## 🗺️ BÖLÜM 7: MASTER YOL HARİTASI 16 AŞAMALI GENEL BAKIŞ

```text
========================================================================================
[ FAZ 0: KÖK PEDAGOJİ, TEMEL MATEMATİK VE ÇÖZDÜREREK ÖĞRETME ÇEKİRDEĞİ ] (1. ÖNCELİK)
========================================================================================
  ├── HEDEF 1: Üretim Hazırlığı, Çevrimdışı Kalıcılık ve Mobil E2E Sağlamlaştırma (Kalite Paketi)
  ├── HEDEF 2: Temel Matematik Sezgisi ve Kök Önkoşul Ağı (Seviye -3..-1: Sıfırdan Başlayan Öğrenci)
  └── HEDEF 3: Aktif Birlikte Çözme (Active Co-Solving), Zaaf Defteri ve Yaşayan Ders Notları

========================================================================================
[ FAZ I: TAM LİSE MATEMATİK MÜFREDATI (CEBİR & ANALİZ) ]
========================================================================================
  ├── HEDEF 4: Müfredat Faz A — Paraboller, 2. Dereceden Fonksiyonlar ve Polinomlar (Cebir II)
  ├── HEDEF 5: Müfredat Faz B — Trigonometri, Logaritma ve Üstel Fonksiyonlar (İleri Fonksiyonlar)
  ├── HEDEF 6: Müfredat Faz C — Limit, Süreklilik ve Türev (Kalkülüs I / Diferansiyel Analiz)
  └── HEDEF 7: Müfredat Faz D — İntegral ve Alan Hesabı (Kalkülüs II / Tam Analiz)

========================================================================================
[ FAZ II: MULTIMODAL ETKİLEŞİM VE DIŞ DÜNYA BAĞLANTISI ]
========================================================================================
  ├── HEDEF 8: Defterden/Kitaptan Soru Fotoğraflama ve Sokratik Hata Teşhis Kamerası (OCR Scanner)
  └── HEDEF 9: Yeni Nesil Hikayeli Problemler ve Modelleme Motoru (Word Problems & Modeling)

========================================================================================
[ FAZ III: GEOMETRİ VE ŞEKİLSEL DÜŞÜNME ]
========================================================================================
  ├── HEDEF 10: Analitik Geometri ve Vektörler Motoru (Koordinat Geometrisi)
  └── HEDEF 11: Sentetik Öklid Geometrisi ve Akıllı Ek Çizim Motoru (Visual Geometry)

========================================================================================
[ FAZ IV: BİLİŞSEL DERİNLİK, İSPAT VE İÇERİK FABRİKASI ]
========================================================================================
  ├── HEDEF 12: Kişisel "Hata Otopsisi" Kasası ve Akıllı Zaaf Avcısı (Cognitive Mistake Vault)
  ├── HEDEF 13: Bilişsel Tuzaklı Sonsuz Soru Üretim Fabrikası (Dynamic Item Generator)
  ├── HEDEF 14: Olasılık, Kombinatorik ve İstatistik Motoru (Ayrık Matematik & Monte Carlo)
  ├── HEDEF 15: Matematiksel İspat ve Mantık Laboratuvarı ("Nedenini Anla" - Proof Engine)
  └── HEDEF 16: Yaşayan Kişisel Matematik Atlası ve Zihin Haritası Gezgini (Interactive Knowledge Navigator)
```

---

## 📋 BÖLÜM 8: TÜM HEDEFLER İÇİN ÇALIŞTIRILABİLİR /goal ŞABLONLARI

Dilediğiniz an ilgili bloğu kopyalayıp sohbete `/goal <İÇERİK>` şeklinde göndererek geliştirme sürecini başlatabilirsiniz.

---

### 🔹 HEDEF 1: Üretim Hazırlığı, Çevrimdışı Kalıcılık, Mobil Kalite ve Haptik Sistem
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 1 kapsamındaki "Üretim Hazırlığı, Çevrimdışı Kalıcılık, Mobil Kalite ve Haptik Sistem" paketini uçtan uca uygula ve doğrula.
- Working tree temizliği (Inking, LTI, Ses, Erişilebilirlik ve testlerini mantıksal bir git commit'i ile kaydet).
- 23-OFFLINE-STATE-AND-SYNC uyarınca mobil tarafta kalıcı yerel kuyruk (OfflineSyncQueue) oluştur; ağ koptuğunda adımları diske yaz, ağ gelince idempotent aktar.
- Haptik Dokunsal Geri Bildirim: Tuş vuruşları (light impact), doğru adımlar (medium impact) ve hata uyarıları için HapticFeedbackService geliştir ve tüm butonlara bağla.
- Sıfır Arayüz Sıçraması (Zero Layout Shift): Touchpad, Klavye ve Çizim Kanvası geçişlerini AnimatedSwitcher ve yay fiziği ile 60/120 FPS akıcı hale getir.
- Çökme Direnci: Seansı ve yarım kalan girdiyi SQLite/Isar'a anında kaydet; sıfır veri kaybıyla geri yükle (State Restoration).
- VectorInkingCanvas, TunnelFocusMode ve DyscalculiaHelper bileşenlerini DailyJourneyScreen ve ayarlar çekmecesine bağla.
- Tüm mobil ve backend testlerinin %90+ coverage ile yeşil geçtiğini doğrula.
```

---

### 🔹 HEDEF 2: Temel Matematik Sezgisi ve Kök Önkoşul Ağı (Sıfırdan Başlayan Öğrenci Patikası)
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 2 kapsamındaki "Temel Matematik Sezgisi ve Kök Önkoşul Ağı (Seviye -3..-1)" paketini uçtan uca uygula ve doğrula.
- Kapsam: Hiçbir matematik temeli olmayan bir öğrenciyi sıfırdan lise cebirine hazırlayan kök DAG mimarisi.
- Kök Bilgi Grafı (DAG N_ROOT_01 .. N_ROOT_16):
  * Seviye -3 (Sayı Doğrusu & İşaret Mantığı): Borç/alacak modeli ile negatif sayılarda toplama-çıkarma (-6 - 5 = -11), çarpma/bölmede işaret kuralı ((+) * (-) = (-), (-) * (-) = (+)).
  * Seviye -2.5 (Kesir & Rasyonel Sezgi): Pasta/dilim modeli, denk kesirler, sadeleştirme ve ortak payda mantığı.
  * Seviye -2 (İşlem Önceliği & Parantez Sezgisi): PEMDAS / İşlem sırası (önce parantez içi, sonra çarpma/bölme, sonra toplama/çıkarma), dağılma özelliği (2(x+3) = 2x+6).
  * Seviye -1.5 (Üslü & Köklü Sezgi): 2^3 = 8 (asla 6 değil), karekök alan sezgisi (√25 = 5).
  * Seviye -1 (Değişken & Eşitlik Sezgisi): x bir kutudur / bilinmeyendir mantığı, terazi metaforu ile denklem çözme (her iki taraftan aynı şeyi çıkarma), örtük çarpma (2x = 2 * x).
- BUG-FOUND-01..15 temel yanılgı dedektörlerini detector.py'a ekle.
- Sıfır Tabanlı Bilişsel Sezgi Testi (Zero-Baseline Diagnostic): Uygulamaya ilk giren öğrencinin 3 soruda temel aritmetik seviyesini tespit edip gerekirse doğrudan bu temel patikadan başlatma.
- İnteraktif Görsel Kanvas: Dokunmatik Sayı Doğrusu, Pasta Kesir ve Terazi Kanvası (NumberLineBalanceCanvas).
- 40 yeni test ile 0 False Positive ve %90+ coverage sağla.
```

---

### 🔹 HEDEF 3: Aktif Birlikte Çözme, Sokratik Metot Anlatımı ve Yaşayan Ders Notları
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 3 kapsamındaki "Aktif Birlikte Çözme, Sokratik Metot Anlatımı ve Yaşayan Ders Notları" paketini uçtan uca uygula ve doğrula.
- 1. Sokratik Metot Anlatımı (Sonucu Değil, Yöntemi Anlatan Akış):
  * Öğrenci bir adımda takıldığında cevabı vermek KESİNLİKLE YASAKTIR.
  * Eşitsizliklerde negatif bölme yön değişimi gibi adımlarda 3 aşamalı keşif uygula: Sezgi Sorusu -> Öğrenci Yanıtı -> Kuralı Kendisinin Bulması.
- 2. Yaşayan Bağlantılı Ders Notları (Explorable Prerequisite Notes):
  * "2. Dereceden Denklem Nasıl Çözülür?" kartından 1. Dereceden Denkleme, oradan Terazi Modeline ve Negatif Sayılara geriye doğru inen tıklanabilir önkoşul merdiveni kur ("Bunu çözmek için bu lazım, ona da bu lazım").
  * Her kart: 1 Cümlelik Sezgi -> Tıklanabilir Önkoşul Linkleri -> Adım Adım Reçete -> 10 Saniyelik Mini-Alıştırma Widget'ı.
- 3. Bilişsel Zaaf Defteri (CognitiveWeaknessLedger):
  * Öğrencinin yaptığı hatanın seviyesini belirle (Aritmetik, Kavram Yanılgısı, Kök Önkoşul Eksikliği) ve SQLite/Postgres'e kalıcı zaaf olarak işle.
- 4. Mikro-Kum Havuzu (In-Situ Remediation):
  * Lise sorusu çözerken temelde takılan öğrenci için ana soruyu dondur; 45 saniyelik görsel kum havuzunda kuralı kavratıp soruya geri döndür.
- 45 yeni test ile pedagojik FSM durum geçişlerini ve sıfır sızıntıyı doğrula.
```

---

### 🔹 HEDEF 4: Müfredat Faz A — Paraboller, 2. Dereceden Fonksiyonlar ve Polinomlar
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 4 kapsamındaki "Paraboller, İkinci Dereceden Fonksiyonlar ve Polinomlar" müfredat genişlemesini uygula ve doğrula.
- Bilgi Grafı Genişlemesi: N27-N38 (Parabol tepe noktası, simetri ekseni, kök geometrisi) ve N39-N50 (Polinom bölmesi, kalan teoremi, katsayılar toplamı).
- 10 Yeni Yanılgı Kuralı: BUG-PARAB-01..05 (-b/2a formülü eksi işareti, simetri ekseni yanılgısı) ve BUG-POLY-01..05 (bölümde sahte kök, derece karışıklığı).
- SymPy CAS motorunda fonksiyon dönüşümleri ve polinom sadeleştirmelerini güvenli AST sandbox içinde destekle.
- 40 yeni birim testi yazarak 0 False Positive ve %90+ coverage sağla.
```

---

### 🔹 HEDEF 5: Müfredat Faz B — Trigonometri, Üstel ve Logaritmik Fonksiyonlar
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 5 kapsamındaki "Trigonometri, Logaritma ve Üstel Fonksiyonlar" genişlemesini uçtan uca uygula ve doğrula.
- Bilgi Grafı Genişlemesi: N51-N65 (Birim çember, oranlar, özdeşlikler, indirgeme, trigonometrik denklemler) ve N66-N80 (Üstel model, logaritma kuralları, taban değiştirme, logaritmik denklemler).
- 10 Yeni Yanılgı Kuralı: BUG-TRIG-01..05 (Lineerlik tuzağı sin(a+b)=sin a+sin b, isim sadeleştirme, periyot/kök kaybı) ve BUG-LOG-01..05 (Dağılma tuzağı, kuvvet kuralı hatası, negatif tanım kümesi ihmali).
- SymPy CAS'a sin, cos, tan, log, ln, exp operasyonlarını güvenli ekle; tanım kümesi denetleyicisi (evaluate_domain_constraints) yaz.
- Mobil tarafta Al-Harezmi karolarının yanına interaktif Birim Çember Kanvası (UnitCircleCanvas) ekle.
- 50 yeni test ile 170+ toplam yeşil test ve %90+ coverage sağla.
```

---

### 🔹 HEDEF 6: Müfredat Faz C — Limit, Süreklilik ve Türev (Kalkülüs I)
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 6 kapsamındaki "Limit, Süreklilik ve Türev (Kalkülüs I)" paketini uçtan uca uygula ve doğrula.
- Bilgi Grafı Genişlemesi: N81-N110 (Limit sezgisel tanımı, sağ-sol limit, 0/0 belirsizliği, çarpanlara ayırma ve L'Hôpital, süreklilik, türevin limit tanımı, türev alma kuralları [çarpım, bölüm, zincir kuralı], teğet denklemi ve yerel ekstremumlar).
- 10 Yeni Yanılgı Kuralı: BUG-CALC-01..05 (Zincir kuralında iç türevi unutma [d/dx f(g(x)) = f'(g(x))], bölüm türevinde eksi işareti ve payda karesi hatası, 0/0 belirsizliğini "tanımsız" deyip bırakma, türevin sıfır olduğu her noktayı mutlak ekstremum sanma).
- CAS Genişlemesi: SymPy Limit ve Derivative nesnelerini güvenli AST sandbox'a bağla; adım adım türev alma kurallarını doğrula.
- Mobil Görsel Kanvas: Ekranda fonksiyon grafiği üzerinde h/delta_x sıfıra yaklaşırken teğetin oluşumunu gösteren Dinamik Teğet Eğimi Kanvası (DynamicTangentCanvas) geliştir.
- 50 yeni birim testi koşturarak sıfır hata ve %90+ coverage sağla.
```

---

### 🔹 HEDEF 7: Müfredat Faz D — İntegral ve Alan Hesabı (Kalkülüs II)
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 7 kapsamındaki "İntegral ve Alan Hesabı (Kalkülüs II)" paketini uçtan uca uygula ve doğrula.
- Bilgi Grafı Genişlemesi: N111-N135 (Belirsiz integral, integrasyon sabitinin anlamı, temel integrasyon kuralları, değişken değiştirme [u-substitution], kısmi integrasyon [uv - int v du], Riemann alt/üst toplamları, Belirli İntegral [Kalkülüsün Temel Teoremi], iki eğri arasında kalan alan).
- 10 Yeni Yanılgı Kuralı: BUG-INT-01..05 (İntegrasyon sabiti +C'yi unutma, değişken değiştirmede dx'i du'ya çevirmeden integralleme, belirli integralde F(b)-F(a) yerine ters çıkarma, x ekseninin altında kalan alanda negatif sonucu doğrudan alan kabul etme).
- SymPy CAS İntegral Doğrulayıcı: Hem sembolik integrali hem de adım adım değişken dönüşümlerini AST seviyesinde denetleyen güvenli motor.
- Mobil Riemann Kanvası: Eğrinin altına dikdörtgenler yerleştirerek n sonsuza giderken alanın integrale yakınsamasını görselleştiren RiemannIntegralCanvas.
- 45 yeni test ile tüm kalkülüs paketinin yeşil geçtiğini doğrula.
```

---

### 🔹 HEDEF 8: Defterden/Kitaptan Soru Fotoğraflama ve Sokratik Hata Teşhis Kamerası
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 8 kapsamındaki "Defterden/Kitaptan Soru Fotoğraflama ve Sokratik Hata Teşhis Kamerası" paketini uygula ve doğrula.
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

### 🔹 HEDEF 9: Yeni Nesil Hikayeli Problemler ve Modelleme Motoru
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 9 kapsamındaki "Yeni Nesil Hikayeli Problemler ve Modelleme Motoru" paketini uygula ve doğrula.
- Kapsam: Yaş, hareket (hız-zaman-yol), yüzde-kâr-zarar, işçi-havuz ve optimizasyon problemleri.
- Modelleme İskelesi: Paragraf halindeki problemi doğrudan çözmek yerine 3 aşamalı Sokratik Modelleme akışı kur:
  1. Değişkenleri Tanımla ("Hangi bilinmeyene x demeliyiz?")
  2. Eşitliği Kur ("Metindeki hangi ifade denklemin sağ tarafını oluşturur?")
  3. CAS ile Adım Adım Çöz.
- Görsel Şematik Modelleme: Hareket problemleri için otomatik zaman-yol çizgisi, karışım/yüzde problemleri için kap şeması üreten dinamik görselleştirici.
- 10 yeni modelleme kavram yanılgısı kuralı (BUG-PROB-01..05) ve 40 test ile doğrula.
```

---

### 🔹 HEDEF 10: Analitik Geometri ve Vektörler Motoru
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 10 kapsamındaki "Analitik Geometri ve Vektörler Motoru" paketini uygula ve doğrula.
- Bilgi Grafı Genişlemesi: N136-N160 (Noktanın analitiği, iki nokta arası uzaklık, orta nokta, doğrunun eğimi ve denklemi, paralel ve dik doğruların eğim bağıntıları, noktanın doğruya uzaklığı, çemberin standart denklemi (x-a)^2 + (y-b)^2 = r^2, 2B vektörler ve iç çarpım).
- Yanılgı Katalogları: BUG-ANAG-01..05 (Dik doğrularda m1*m2=-1 kuralını m1=m2 sanma, eğim açısı geniş açı olduğunda eğimi pozitif alma, çember merkez koordinatlarının işaretlerini formülde ters okuma).
- Mobil İnteraktif Koordinat Kanvası (InteractiveCoordinateCanvas): Öğrencinin noktaları sürükleyip doğru denkleminin ve çember yarıçapının gerçek zamanlı değişimini gördüğü dokunmatik kanvas.
- 40 yeni test ile koordinat ve cebir doğrulamasını tamamla.
```

---

### 🔹 HEDEF 11: Sentetik Öklid Geometrisi ve Akıllı Ek Çizim Motoru
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 11 kapsamındaki "Sentetik Öklid Geometrisi ve Akıllı Ek Çizim Motoru" paketini uygula ve doğrula.
- Kapsam: Üçgende açılar, kenarortay, açıortay, benzerlik teoeremleri (Thales, Kelebek), dik üçgen bağıntıları (Öklid, Pisagor), çemberde açılar ve kirişler.
- Geometrik Kısıt Çözücü: Ekrana çizilen şeklin geometrik tutarlılığını (açı toplamı 180, kenar eşitsizliği) doğrulayan motor.
- Sokratik Ek Çizim İskelesi: Öğrenci tıkandığında çizgiyi doğrudan çekmek yerine: "Bu ikizkenar üçgenin tabanına dik inersek taban nasıl bölünür?" diyerek ek çizimi öğrenciye yaptıran rehber.
- Serbest Dokunmatik Geometri Kanvası (EuclideanCanvas).
- 40 test ile doğrula.
```

---

### 🔹 HEDEF 12: Kişisel "Hata Otopsisi" Kasası ve Akıllı Zaaf Avcısı
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 12 kapsamındaki "Kişisel Hata Otopsisi (Mistake Vault) ve Akıllı Zaaf Avcısı" paketini uygula ve doğrula.
- Hata Kasası Veri Modeli: Öğrencinin çözümlerde veya Hedef 8 kamerasında düştüğü tüm bozuk kuralları (BUG-xxxx) zaman damgası, konu düğümü ve tam adım bağlamıyla SQLite/Postgres üzerinde sakla.
- Kendi Kendini Düzeltme Seansı (Self-Correction Session): Öğrencinin geçmişte yaptığı hatalı adımı önüne çıkarıp: "3 gün önce bu adımda bir hata yapmıştın. Kendi hatanı bulup düzeltebilir misin?" diyen üstbilişsel arayüz.
- FSRS-4.5 Zaaf Adaptasyonu: Unutma eğrisi motorunu öğrencinin en sık hata yaptığı bozuk kurallarla eşleştir; haftalık "Boss Battle" tekrar oturumları üret.
- 35 test ve simülasyon doğrulaması ile tamamla.
```

---

### 🔹 HEDEF 13: Bilişsel Tuzaklı Sonsuz Soru Üretim Fabrikası
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 13 kapsamındaki "Bilişsel Tuzaklı Sonsuz Soru Üretim Fabrikası (Dynamic Item Generator & Exam Maker)" paketini uygula ve doğrula.
- CAS Tabanlı Dinamik Üretici: Sadece rastgele sayı üreten değil; öğrencinin zayıf olduğu Buggy Rule'u tetikleyecek özel çeldiricili sorular sentezleyen ters-SymPy jeneratörü.
- Formel Kanıt: Üretilen her sorunun tam sayı köklere sahip olduğunu ve çözüm adımlarının %100 geçerli olduğunu SymPy ile formel olarak kanıtla.
- Deneme Sınavı & PDF Export: Tek tıkla LaTeX kalitesinde temiz, çözümlü PDF çalışma yaprağı ve deneme sınavı üretme motoru.
- 30 test ve 500 sentetik soru üretim testi ile doğrula.
```

---

### 🔹 HEDEF 14: Olasılık, Kombinatorik ve İstatistik Motoru (Ayrık Matematik)
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 14 kapsamındaki "Olasılık, Kombinatorik ve İstatistik Motoru" paketini uygula ve doğrula.
- Bilgi Grafı: Permütasyon, Kombinasyon, Faktöriyel cebiri, Binom açılımı, Basit ve Koşullu Olasılık, Bayes Teoremi, Beklenen Değer.
- Sezgisel Hata Dedektörleri: BUG-COMB-01..05 (Sıralama ile seçmeyi karıştırma, tekrarlı permütasyonda özdeş elemanı bölmeme, bağımsız olay çarpımı hatası).
- Canlı Monte Carlo Doğrulayıcı: Öğrencinin teorik sonucunu anında 100.000 sanal deneyle simüle eden ve ampirik frekansı gösteren simülasyon motoru.
- İnteraktif Sayma Ağacı & Venn Şeması Kanvası.
- 40 test ile doğrula.
```

---

### 🔹 HEDEF 15: Matematiksel İspat ve Mantık Laboratuvarı ("Nedenini Anla")
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 15 kapsamındaki "Matematiksel İspat ve Mantık Laboratuvarı" paketini uygula ve doğrula.
- Kapsam: Önermeler mantığı, doğruluk tabloları, niceleyiciler, Tümevarım ile ispat, Olmayana Ergi (Çelişki) ile ispat, Karşıt-Ters yöntemi.
- Adım Adım Mantık Denetleyicisi: Öğrencinin bir hipotezden başlayıp adım adım teorem türettiği ve motorun her adımın mantıksal geçerliliğini (Modus Ponens) denetlediği ispat sandbox'ı.
- Temel Teorem İspat Kataloğu: Karekök 2'nin irrasyonelliği, asal sayıların sonsuzluğu, Gauss toplam formülü vb.
- 35 test ile doğrula.
```

---

### 🔹 HEDEF 16: Yaşayan Kişisel Matematik Atlası ve Zihin Haritası Gezgini
```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 16 kapsamındaki "Yaşayan Kişisel Matematik Atlası ve Zihin Haritası Gezgini" paketini uygula ve doğrula.
- Bütünleşik Bilgi Grafı (N_ROOT_01 - N160): Temel sayı doğrusundan en ileri Kalkülüs ve İspata kadar tüm matematiğin birbirine bağlandığı organik bir 2B/3B Zihin Ağı (Knowledge Graph Navigator).
- Dinamik Zihinsel Durum: Öğrencinin BKT posterior ustalığına göre yeşil/sarı/kırmızı parıldayan, zayıf önkoşul köprülerini gösteren interaktif harita.
- Konular Arası Köprüler: Sayı doğrusundaki eksi sayı modelinden Parabol köklerine, oradan Türev ve İntegrale uzanan canlı kavramsal bağlantılar.
- Mobil donanım hızlandırmalı graf görselleştiricisi ve 30 test ile doğrula.
```

---
*Bu belge projenin kalıcı master şartnamesidir. İlk kullanıcının sıfırdan zirveye eksiksiz, akıcı ve en yüksek pedagojik kalitede öğrenmesi için optimize edilmiştir.*
