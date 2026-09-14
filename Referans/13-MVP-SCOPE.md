# 13-MVP-SCOPE.md
# MVP KAPSAMI VE ACIMASIZ SINIRLAR (MVP SCOPE & FEATURE FREEZE)
## Sandbox Domain Tercihi, Faz Kapıları, Kapsam Kilitleri ve MVP Alt Kümesi

---

## 1. TEMEL MVP HİPOTEZİ VE BAŞARI KRİTERİ

MVP'nin amacı genel amaçlı bir eğitim platformu yapmak veya kontrolsüz özellik eklemek değildir. Tek bir bilimsel-ürün hipotezini en katı test ortamında doğrulamaktır:

> **MVP Temel Hipotezi:**
> "Kullanıcının ön bilgisini teşhis eden, çok boyutlu zihinsel durumunu modelleyen, öğretim yöntemini ve iskelelemeyi (fading/hinting) adaptif değiştiren ve prosedürel aralıklı tekrar uygulayan bir sistem; sabit lineer içerik sunan (Khan Academy tarzı) veya standart ödev çözücü chatbot'lara (ChatGPT tarzı) kıyasla **gecikmeli kalıcılıkta (7. gün) ve transfer testinde harcanan dakika başına en az %35 daha yüksek performans** sağlar."

---

## 2. İLK ALAN (FIRST DOMAIN) SEÇİMİ: LİSE CEBİRİ VE İKİNCİ DERECEDEN DENKLEMLER

İlk MVP için **Lise Cebiri: İkinci Dereceden Denklemler (Quadratic Equations)** seçilmiştir:

### Neden Bu Domain?
1. **Deterministik Doğrulanabilirlik:** Matematiksel adımlar sembolik olarak (CAS / SymPy) %100 kesinlikle doğrulanabilir; LLM halüsinasyon riski sıfırlanır.
2. **Kavram Yanılgısı Literatürünün Zenginliği:** Booth (2013) ve Ashlock (2010) araştırmaları, cebirdeki hata kalıplarını (Freshman's dream, işaret dağıtma hataları, sıfır çarpım ihmali) eksiksiz sınıflandırmıştır.
3. **Net ve Hiyerarşik Önkoşul Yapısı:** Aritmetik $\rightarrow$ Çarpanlara Ayırma $\rightarrow$ Kuadratik Formül $\rightarrow$ Parabol ilişkisi kristal berraklığında bir DAG sunar.
4. **Çoklu Temsil Zenginliği:** Hem cebirsel formülle hem geometrik alan modeliyle (Al-Harezmi kare tamamlama) hem de grafiksel parabol simülasyonuyla anlatılabilir.

---

## 3. KESİN FAZ KAPILARI (MILESTONE PHASE GATES 0 - 5)

Proje, her biri bağımsız olarak doğrulanabilir 6 ardışık faz kapısına (Phase Gate) bölünmüştür. Bir fazın Çıkış Kriterleri (DoD) %100 sağlanmadan sonraki faza geçilmesi kesinlikle yasaktır.

```text
+─────────────+    +─────────────+    +─────────────+    +─────────────+    +─────────────+    +─────────────+
|   GATE 0    |───>|   GATE 1    |───>|   GATE 2    |───>|   GATE 3    |───>|   GATE 4    |───>|   GATE 5    |
| CAS Core &  |    | CAT & 5D    |    | FSM Engine &|    | Scratchpad  |    | Integrated  |    | Cohort Test |
| DAG Topo    |    | Learner BKT |    | Socratic AI |    | Reactive UI |    | E2E Loop    |    | & Retention |
+─────────────+    +─────────────+    +─────────────+    +─────────────+    +─────────────+    +─────────────+
```

### Faz 0: Temel Sembolik Çekirdek ve Bilgi Ontolojisi (CAS Core & Knowledge DAG)
* **Giriş Kriterleri (Entry Criteria):**
  - İkinci dereceden denklemler matematiksel spesifikasyonunun tamamlanmış olması.
  - Python 3.11+ ve SymPy çalışma ortamının hazırlanması.
* **Teslimat Kalemleri (Deliverables):**
  - Deterministik CAS Doğrulama Modülü (AST ayrıştırıcı, `simplify(user - target) == 0` mantığı, canonical normalizer).
  - 30 Düğümlü Bilgi Grafı (NetworkX / JSON ontoloji modeli) ve önkoşul kenarları.
  - 15 Temel Cebirsel Yanılgı AST Eşleştirici Kütüphanesi.
* **Çıkış Kriterleri (Definition of Done - DoD):**
  - 500 sentetik cebir adımı test setinde %100 doğruluk (0 False Positive, 0 False Negative).
  - CAS adım doğrulama işlem süresinin $\le 150 \text{ ms}$ olması.
  - AST Sandbox güvenlik testlerinin (kod enjeksiyonu, sonsuz döngü) sıfır güvenlik açığı ile geçmesi.

### Faz 1: Adaptif Teşhis ve Öğrenici Modeli (CAT Diagnostic & 5D Learner Engine)
* **Giriş Kriterleri (Entry Criteria):**
  - Faz 0'ın başarıyla kilitlenmesi.
  - Kalibre edilmiş 40 soruluk parametrik 2PL IRT soru bankası veri seti.
* **Teslimat Kalemleri (Deliverables):**
  - Fisher Bilgisi optimizasyonlu 5 soruluk Bilgisayarlı Uyarlamalı Teşhis Testi (CAT Motoru).
  - 5 Boyutlu Yetkinlik Vektörü ($V_L$) ve Bayesian Knowledge Tracing (BKT) durum güncelleyici.
  - Güven Derecelendirmesi ve Brier Skoru kalibrasyon algoritması.
* **Çıkış Kriterleri (Definition of Done - DoD):**
  - Teşhis motorunun sentetik simülasyonlarda (Monte Carlo 10,000 öğrenci) gerçek $\theta$ yetkinliğini 5 soruda $\text{SE}(\theta) \le 0.35$ standart hata ile kestirebilmesi.
  - Brier skoru ve BKT durum geçiş hesaplamasının $\le 30 \text{ ms}$ içinde tamamlanması.

### Faz 2: Pedagojik FSM ve Sokratik AI Orkestratörü (FSM Engine & Socratic LLM)
* **Giriş Kriterleri (Entry Criteria):**
  - Faz 1'in BKT ve yetkinlik güncelleme servislerinin canlı API'de hazır olması.
  - LLM API anahtarları, şablon sözleşmeleri ve çıktı doğrulama boru hattı.
* **Teslimat Kalemleri (Deliverables):**
  - 3 Katmanlı Durum Makinesi (Global Strateji, Düğüm İçi Fading, Adım İçi Onarım FSM).
  - Remediation Sandboxing (Mikro-kum havuzu) ve ZPD Gezinti Protokolü.
  - Sokratik AI Tutor İstem Hattı (Katı negatif kısıtlar, Sıfır Sızıntı / Zero-Leakage regex filtresi, Sezgi Freni).
* **Çıkış Kriterleri (Definition of Done - DoD):**
  - Kırmızı Takım (Red Team) testlerinde 100 farklı adversarial istem enjeksiyonunda (Jailbreak, "cevabı ver", "öğretmen moduna geç") sızıntı oranının %0 (sıfır) olması.
  - FSM durum geçiş testlerinin 50 uç senaryoda (edge case) %100 hatasız sonuçlanması.

### Faz 3: İstemci Arayüzü ve Reaktif Çözüm Tahtası (Web UI & Scratchpad)
* **Giriş Kriterleri (Entry Criteria):**
  - Faz 0, 1 ve 2 servis API uç noktalarının (`/submit-step`, `/diagnostic`, `/fsm-state`) tamamlanması.
* **Teslimat Kalemleri (Deliverables):**
  - Next.js / React / TypeScript tabanlı reaktif web arayüzü.
  - MathLive entegre sanal matematik klavyesi, Akıllı Sembol Tuşları (Smart Chips) ve KaTeX render motoru.
  - Canlı Beyin Haritası görselleştiricisi (D3.js / React Flow tabanlı ZPD ve düğüm renklendirmesi).
  - Mikro-kum havuzu açılır pencere (side-drawer) bileşeni.
* **Çıkış Kriterleri (Definition of Done - DoD):**
  - Mobilde ve masaüstünde First Contentful Paint (FCP) $\le 1.2 \text{ s}$, Time to Interactive (TTI) $\le 2.0 \text{ s}$.
  - Girdi alanından adım gönderimine kadar UI etkileşim gecikmesinin $\le 50 \text{ ms}$ olması.
  - WCAG 2.1 AA erişilebilirlik standartlarına %100 uyum.

### Faz 4: Entegre E2E Öğrenme Döngüsü ve Dahili Pilot (End-to-End Loop & Dogfooding)
* **Giriş Kriterleri (Entry Criteria):**
  - Tüm istemci ve sunucu bileşenlerinin entegre edilmesi.
  - FSRS aralıklı tekrar kuyruğu ve Redis oturum deposunun canlıya bağlanması.
* **Teslimat Kalemleri (Deliverables):**
  - 20 dakikalık günlük öğrenme seansı akışı: 3 dk Isınma (Tekrar) $\rightarrow$ 12 dk Yeni Düğüm / ZPD $\rightarrow$ 5 dk Kapanış Testi.
  - Hata telemetrisi, yanıt süreleri ve kognitif kilitlenme kütükleme sistemi.
  - Dahili ekip (10 kullanıcı) ile 5 günlük dogfooding test çalışması.
* **Çıkış Kriterleri (Definition of Done - DoD):**
  - 10 kullanıcının 5 gün boyunca günde en az 1 tam seans tamamlaması (Sıfır kritik çökme / Zero P0 bug).
  - Adım doğrulama uçtan uca ortalama gecikmesinin $P_{95} \le 850 \text{ ms}$ olması.
  - Öğrenci durum kayıplarının veya oturum kopmalarının %0 olması.

### Faz 5: MVP Lansmanı, Gecikmeli Kalıcılık ve Transfer Deneyi (Cohort Testing & Audit)
* **Giriş Kriterleri (Entry Criteria):**
  - Faz 4'ün başarıyla tamamlanması ve tüm P0/P1 hataların kapatılması.
  - Etik kurul ve kullanıcı aydınlatma onam mekanizmasının hazır olması.
* **Teslimat Kalemleri (Deliverables):**
  - 50 kişilik lise öğrenci kohortu ile 14 günlük canlı deneme (Kontrol grubu vs. Adaptif Sistem).
  - 7. gün gecikmeli kalıcılık testi (Delayed Retention Test).
  - Yapısal transfer testi (Isomorphic & Far Transfer: $x^4 - 5x^2 + 4 = 0$, geometrik problem).
  - Nihai Bilimsel Doğrulama Raporu ve Metrik Analizi.
* **Çıkış Kriterleri (Definition of Done - DoD):**
  - 7. gün kalıcılık ve transfer skorunda kontrol grubuna kıyasla harcanan dakika başına en az %35 performans artışının $p < 0.01$ istatistiksel anlamlılıkla kanıtlanması.
  - Öğrenci ayrılma (drop-off) oranının %20'nin altında kalması.

---

## 4. KATI KAPSAM DIŞI LİSTESİ (NON-GOALS & BOUNDARIES)

Aşağıdaki özellikler, cazip görünseler dahi MVP hipotezini sulandıracağı ve mühendislik karmaşıklığını orantısız artıracağı için **kesinlikle kapsam dışıdır**:

| Kapsam Dışı Özellik | Kapsam Dışı Bırakılma Gerekçesi | Gelecekte Değerlendirme Eşiği |
| :--- | :--- | :--- |
| **1. Serbest El Yazısı Tanıma / Çizim OCR** | Matematiksel el yazısı parse etme (kesir, üs, kök sembolleri) yüksek hata oranına sahiptir. Yanlış tanınan bir karakter öğrencinin moralini bozar ve bilişsel odağı matematikten OCR düzeltmeye kaydırır. | Faz 2 sonrasında, sembolik doğruluk oranı %98'e ulaştığında MyScript / Mathpix SDK ile. |
| **2. Sesli Konuşma Arayüzü (Voice Agent)** | Matematiksel formüllerin sesle dikte edilmesi ("parantez aç iki x artı üç parantez kapa bölü...") kognitif sürtünmeyi katlar. Matematik yüksek derecede görsel-sembolik bir dildir. | İleri erişilebilirlik (özel gereksinimli bireyler) fazında özel ses motoruyla. |
| **3. Çoklu Branş ve Ders Genişlemesi** | Fizik, Kimya veya Biyoloji gibi alanlara yayılmak, bilgi grafı kalitesini düşürür ve deterministik CAS doğrulaması yerine LLM halüsinasyon riskini artırır. | İkinci dereceden denklemler domaininde %35 öğrenme üstünlüğü ispatlanana kadar yasaktır. |
| **4. Derin Öğrenme Tabanlı DKT / Transformer Modelleri** | Derin Bilgi İzleme (Deep Knowledge Tracing) yüz binlerce etkileşim verisi ister, bir kara kutudur ve pedagojik açıklanabilirliği yoktur. BKT ve 5D vektörü az veriyle deterministik ve şeffaf çalışır. | Sistem 500,000+ tekil adım kütüğüne ulaştığında BKT ile hibrit ensemble olarak. |
| **5. Sosyal Özellikler ve Gamification** | Liderlik tabloları (leaderboards), arkadaş ekleme, sanal ligler ve XP puanları; öğrencinin içsel motivasyonunu (SDT) dışsal ödül bağımlılığına çevirir ve kognitif derinliği yok eder. | MVP sonrasında yalnızca bireysel ustalık ve büyüme odaklı rozetlerle sınırlı olarak. |
| **6. Native Mobil Uygulama (iOS Swift / Android Kotlin)** | Çift kod tabanı bakım maliyeti getirir. Modern Next.js PWA, dokunmatik optimizasyon ve MathLive sanal klavye ile mobilde kusursuz çalışmaktadır. | Web PWA aylık 10,000 aktif kullanıcıyı aştığında. |
| **7. Serbest / Açık Uçlu LLM Sohbet Penceresi** | Öğrencinin serbest sohbet kutusuna ödevini yapıştırması veya konu dışına çıkması engellenmelidir. Arayüz adım bazlı Scratchpad olarak kilitlidir. | Hiçbir zaman serbest sohbete dönüştürülmeyecektir; daima Sokratik adım odaklı kalacaktır. |
| **8. Gerçek Zamanlı Çok Oyunculu Akran Öğrenmesi** | Eşzamanlı WebRTC / WebSocket çok kullanıcılı etkileşim mimari karmaşıklığı 10 katına çıkarır ve MVP hipotezi bireysel adaptasyon üzerinedir. | Kurumsal / Okul içi sınıf lisanslama fazında (v2.0). |

---

## 5. MVP SANDBOX: 30 DÜĞÜMLÜ KUADRATİK DENKLEMLER GRAFININ MVP ALT KÜMESİ

`04-KNOWLEDGE-AND-PREREQUISITE-GRAPH.md` dökümanında tanımlanan 30 düğümlü tam ağın pedagojik omurgası incelenmiş; **20 düğüm MVP Sandbox'ta AKTİF**, **10 düğüm ise FAZ 2'ye ERTELENMİŞTİR**.

### 5.1. Düğüm Seçim Kriterleri
1. **Çekirdek Hipotez Uyumu:** İkinci dereceden denklem çözme yetkinliğinin 3 temel ayağı (Çarpanlara Ayırma, Tam Kare, Kuadratik Formül) eksiksiz temsil edilmelidir.
2. **Deterministik Doğrulama Güvenilirliği:** CAS motorunun ara adımları tek anlamlı biçimde basitleştirebildiği düğümlere öncelik verilmiştir.
3. **Kavramsal Derinlik ve Çoklu Temsil:** Hem sembolik hem geometrik alan modelini (Al-Harezmi) içeren düğümler çekirdeğe dahil edilmiştir.

### 5.2. MVP Düğüm Dağılım Matrisi (N01 - N30)

```text
+---------------------------------------------------------------------------------------------------------------+
| DÜĞÜM KODU | DÜĞÜM ADI (CONCEPT NAME)                    | DURUM      | GEREKÇE VE PEDAGOJİK ROLÜ             |
+---------------------------------------------------------------------------------------------------------------+
| SEVİYE 0: TEMEL ARİTMETİK VE CEBİRSEL ÖNKOŞULLAR (MİKRO-KUM HAVUZU İÇİN AÇIK)                                  |
+---------------------------------------------------------------------------------------------------------------+
| [N01]      | Negatif Sayılarla İşlemler (Signed Arith.)  | AKTİF      | Mikro-kum havuzunda işaret hatası tamiri|
| [N02]      | Dağılma Özelliği (Distributive Property)    | AKTİF      | Parantez açma yanılgılarının kök düğümü |
| [N03]      | Benzer Terimleri Birleştirme (Like Terms)   | AKTİF      | Standart forma getirmede zorunlu önkoşul|
| [N04]      | Lineer Denklem Çözme (Linear Solving)       | AKTİF      | Çarpanların köklerini bulmak için şart  |
+---------------------------------------------------------------------------------------------------------------+
| SEVİYE 1: ÇARPANLARA AYIRMA VE ÖZDEŞLİKLER                                                                    |
+---------------------------------------------------------------------------------------------------------------+
| [N05]      | Ortak Çarpan Parantezi (GCF Factoring)      | AKTİF      | Basit kuadratik denklemlerde anahtar    |
| [N06]      | İki Kare Farkı Özdeşliği (a² - b²)          | AKTİF      | Saf kuadratiklerde simetrik çözüm       |
| [N07]      | Tam Kare Özdeşliği ((a ± b)²)               | AKTİF      | Tam kareye tamamlamanın cebirsel temeli |
| [N08]      | Monik Üçterimliler (x² + bx + c)            | AKTİF      | Çarpanlara ayırmanın en yaygın omurgası |
| [N09]      | Monik Olmayan Üçterimliler (ax² + bx + c)   | ERTELENDİ  | Gruplama kuralı arayüz sürtünmesi yüksek;|
|            |                                             | (Faz 2)    | Kuadratik formül (N18) ile ikame edildi.|
+---------------------------------------------------------------------------------------------------------------+
| SEVİYE 2: İKİNCİ DERECEDEN DENKLEM TEMELLERİ                                                                  |
+---------------------------------------------------------------------------------------------------------------+
| [N10]      | Standart Form (ax² + bx + c = 0, a ≠ 0)     | AKTİF      | Tüm çözüm yöntemlerinin başlangıç şartı |
| [N11]      | Sıfır Çarpım İlkesi (Zero Product Property) | AKTİF      | En yaygın kavram yanılgısı kapanı (Trap)|
| [N12]      | Çarpanlara Ayırma Yoluyla Çözüm             | AKTİF      | Seviye 1 özdeşliklerinin birleşik testi |
| [N13]      | Karekök Alma ile Çözüm (Pure Quadratics)    | AKTİF      | ± işaretinin unutulma yanılgısını tarar |
+---------------------------------------------------------------------------------------------------------------+
| SEVİYE 3: TAM KAREYE TAMAMLAMA VE GEOMETRİK MODEL                                                             |
+---------------------------------------------------------------------------------------------------------------+
| [N14]      | Geometrik Alan Modeli ile Tam Kare          | AKTİF      | Al-Harezmi karo modeli (Kavramsal)      |
| [N15]      | Cebirsel Tam Kareye Tamamlama ((b/2)²)      | AKTİF      | Formülün çıkarılışındaki kritik algoritma|
| [N16]      | Tam Kare Metodu ile Kök Bulma               | AKTİF      | Genel çözüme giden mekanik prosedür     |
+---------------------------------------------------------------------------------------------------------------+
| SEVİYE 4: KUADRATİK FORMÜL VE DİSKRİMİNANT                                                                    |
+---------------------------------------------------------------------------------------------------------------+
| [N17]      | Kuadratik Formülün Çıkarılışı (Derivation)  | AKTİF      | Ezberi önleyen derin kavramsal düğüm    |
| [N18]      | Kuadratik Formül Standart Uygulama          | AKTİF      | Evrensel çözüm yöntemi                  |
| [N19]      | Diskriminant Hesaplanışı (Δ = b² - 4ac)     | AKTİF      | Kök yapısını belirleyen çekirdek ölçüt  |
| [N20]      | Diskriminant ve Reel/Karmaşık Kök Türü      | AKTİF      | Kök sayısı ve varlığı kavram analizi    |
| [N21]      | Yöntem Seçim Stratejisi (Strategy Picking)  | AKTİF      | Metabilişsel strateji seçimi            |
+---------------------------------------------------------------------------------------------------------------+
| SEVİYE 5: FONKSİYON, GRAFİK VE PARABOL İLİŞKİSİ                                                               |
+---------------------------------------------------------------------------------------------------------------+
| [N22]      | Parabol Tanımı ve Simetri Ekseni            | AKTİF      | Cebir-geometri köprüsü                  |
| [N23]      | Tepe Noktası (Vertex Form)                  | AKTİF      | Tam kare ile tepe noktası bağı          |
| [N24]      | x-Eksenini Kesen Noktalar ve Kökler         | AKTİF      | Köklerin geometrik izdüşümü             |
| [N25]      | 'a' Katsayısının Parabol Şekline Etkisi     | ERTELENDİ  | İnteraktif simülatör gereksinimi yüksek;|
|            |                                             | (Faz 2)    | MVP'de statik grafikler yeterlidir.    |
+---------------------------------------------------------------------------------------------------------------+
| SEVİYE 6: İLERİ SEVİYE VE TRANSFER UYGULAMALARI                                                               |
+---------------------------------------------------------------------------------------------------------------+
| [N26]      | u-Substitution ile İkinci Dereceye İndirgeme| ERTELENDİ  | İleri manipülasyon; MVP için kritik değil|
| [N27]      | Ters Köşe ve Karşıt Örnek Analizi           | AKTİF      | Sadeleştirip kök kaybetme tuzağı (Aşı) |
| [N28]      | Geometrik Alan Optimizasyonu                | ERTELENDİ  | Kelime problemi parse sürtünmesi yüksek |
| [N29]      | Fizik Yörünge Hareketi Modellemesi          | ERTELENDİ  | Faz 2 uzak transfer (far transfer) testi|
| [N30]      | Doğru ile Parabol Kesişimi Sistemleri       | ERTELENDİ  | İki değişkenli sistemler kapsam dışı    |
+---------------------------------------------------------------------------------------------------------------+
```

### 5.3. MVP Sandbox Graf Özeti
* **Toplam Düğüm Sayısı:** 30
* **MVP Aktif Düğüm:** 20 (%66.7 kapsam oranı - kavramsal omurga tam)
* **Faz 2'ye Ertelenen:** 10 (%33.3 - ileri modelleme ve yüksek sürtünmeli uçlar)
* **Aktif Önkoşul Kenar Sayısı:** 34 katı kenar ($E_{\text{strict}}$), 12 destekleyici kenar ($E_{\text{soft}}$)
* **Mikro-Kum Havuzu İzolasyonu:** N01, N02, N03, N04 düğümleri ana öğrenme rotasında zorunlu ders olarak dayatılmaz; yalnızca üst seviyelerde takılma anında 2 dakikalık mikro-müdahale kum havuzu olarak tetiklenir.

