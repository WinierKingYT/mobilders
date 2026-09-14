# 17-OPEN-QUESTIONS-AND-RESEARCH-GAPS.md
# AÇIK TASARIM SORULARI, ARAŞTIRMA BOŞLUKLARI VE ÖN KAYITLI DENEYSEL PROTOKOL
## Bilimsel Sınırlar, Yanıtlanmamış Hipotezler, OSF Ön Kayıt Tasarımı ve Çift Kör Sokratik Kıyaslama

---

## 1. GİRİŞ VE METODOLOJİK DÜRÜSTLÜK

Bilişsel bilim, yapay zeka pedagojisi ve akıllı öğretim sistemleri (Intelligent Tutoring Systems - ITS) hızla evrilen disiplinlerarası alanlardır. Karmaşık insan zihninin şema inşasını tek bir deterministik modele indirgemek veya sistemin her pedagojik kararının mutlak doğruluğunu varsaymak bilimsel ciddiyetle bağdaşmaz. 

Bu doküman;
1. Sistemimizin MVP ve ölçeklenme aşamalarında ampirik olarak test etmesi gereken **10 temel açık araştırma boşluğunu (Research Gaps)** ve bunların formel istatistiksel hipotezlerini ($H_0$ vs $H_1$),
2. Open Science Framework (OSF) standartlarında **Ön Kayıtlı Deney Tasarımını (Pre-registration Study Design)**,
3. Nöro-sembolik Sokratik LLM motorumuzun insan uzman öğretmenlerle kıyaslanacağı **Çift Kör (Double-Blind) Sokratik Pedagoji Doğrulama Protokolünü** içerir.

---

## 2. 10 TEMEL AÇIK ARAŞTIRMA BOŞLUĞU VE BİLİMSEL ÇÖZÜM HİPOTEZLERİ

```text
+----+---------------------------------------------------+---------------------------------------------------+
| NO | ARAŞTIRMA BOŞLUĞU (RESEARCH GAP)                  | TEMEL BİLİŞSEL / ALGORİTMİK ÇATIŞMA               |
+----+---------------------------------------------------+---------------------------------------------------+
| 1  | Metabilişsel Güven Sorusunun Kognitif Maliyeti    | Metacognitive Calibration vs Extraneous Load      |
| 2  | Çoklu Temsil Değişiminde Bandit Dengesi           | Multi-Armed Bandit Exploration vs Split-Attention |
| 3  | Doğal Dil Öz-Açıklama Otomatik Puanlama Bias'ı    | Semantic Understanding vs Academic Jargon Bias    |
| 4  | BKT'den DKT/SAKT Modellerine Dinamik Geçiş Eşiği   | Model Explainability vs Non-Linear Skill Tracking |
| 5  | İskele Çekilme Hızı ve Uzmanlık Tersinme Etkisi   | Scaffolding Fading vs Expertise Reversal Effect   |
| 6  | Verimli Başarısızlık ve Doğrudan Öğretim Zamanı   | Productive Failure (Kapur) vs Early Frustration   |
| 7  | Sembolik AST Doğrulama Gecikmesi ve Diyalog Akışı | Formal Verification Latency vs Conversational Flow|
| 8  | STEM Dışı Yorumlayıcı Alanlara Genişletilebilirlik| Deterministic Proofs vs Ill-Structured Domains    |
| 9  | Pasif Telemetri ile Bilişsel Tükenmişlik Tespiti  | Sensorless Fatigue Inference vs Behavioral Noise  |
| 10 | FSRS Spaced Repetition vs ACT-R Bellek Sentezi    | Empirical Power Laws vs Cognitive Architecture    |
+----+---------------------------------------------------+---------------------------------------------------+
```

---

### 2.1. Metabilişsel Güven Sorgulamasının Kognitif Maliyeti ve Kalibrasyon Kazancı
* **Bağlam ve Mekanizma:** Her çözüm adımından önce öğrenciye *"Bu adımdan ne kadar eminsin? (%20 - %100)"* sorusunu yöneltmek (Elicitation), öğrencinin izleme (monitoring) mekanizmasını tetikleyerek Dunning-Kruger etkisini azaltır. Ancak her adımda bu kararı vermek çalışma belleğinde yabancı kognitif yük (extraneous cognitive load) ve değerlendirme kaygısı yaratabilir.
* **Hipotezler:**
  * $H_0: \text{R-LGpM}_{\text{ExplicitConfidence}} \le \text{R-LGpM}_{\text{PassiveTelemetry}}$
  * $H_1: \text{R-LGpM}_{\text{ExplicitConfidence}} > \text{R-LGpM}_{\text{PassiveTelemetry}}$ ve $\text{ECE}_{\text{Explicit}} < \text{ECE}_{\text{Passive}} - 0.04$
* **Değişkenler:** Bağımsız: Güven sorgulama frekansı (Her adım vs Yalnızca kritik dallanma adımları vs Sıfır sorgulama); Bağımlı: Beklenen Kalibrasyon Hatası (ECE), R-LGpM, Paas Bilişsel Verimlilik ($E$).
* **Yanlışlanabilirlik Eşiği:** Eğer açık güven sorgulama grubu, pasif telemetri grubuna kıyasla kalibrasyon hatasını anlamlı düzeyde düşürmeden ($p > 0.05$) seans tamamlama süresini %15'ten fazla uzatırsa $H_0$ kabul edilir ve doğrudan güven sorma arayüzü terk edilir.

---

### 2.2. Çoklu Temsil Değişiminde Keşif/Kullanım (Exploration/Exploitation) ve Ayrık Dikkat
* **Bağlam ve Mekanizma:** Öğrenci bir denklemde takıldığında, motor temsili cebirselden geometrik alana (Algebra Tiles) veya fiziksel terazi analojisine dönüştürebilir. Bu karar Multi-Armed Bandit (MAB / Thompson Sampling) ile yönetilir. Çok agresif keşif (exploration) öğrencinin dikkatini dağıtır (Split-Attention Effect; Sweller, 2011); aşırı muhafazakar kalmak (exploitation) öğrenciyi çıkmaza hapseder.
* **Hipotezler:**
  * $H_0: \mu_{\text{Transfer}}^{(\text{AdaptiveMAB})} = \mu_{\text{Transfer}}^{(\text{FixedStaticRep})}$
  * $H_1: \mu_{\text{Transfer}}^{(\text{AdaptiveMAB})} > \mu_{\text{Transfer}}^{(\text{FixedStaticRep})} + 0.40\sigma$
* **Değişkenler:** Bağımsız: MAB sıcaklık parametresi ($\tau \in [0.1, 1.5]$); Bağımlı: Temsil değiştirme sonrası ilk adım başarı oranı, kognitif yük (Paas ölçeği), Uzak Transfer Oranı (FTR).
* **Yanlışlanabilirlik Eşiği:** Temsil değişim frekansı $k > 2$ olduğunda öğrencinin reaksiyon süresinde aşırı artış ($>2.5\times$) ve ardışık hata artışı gözlenirse MAB keşif parametresi sıkı bir tavlama (cooling schedule) filtresine bağlanır.

---

### 2.3. Doğal Dil ile Öz-Açıklama (Self-Explanation) Otomatik Puanlamasında LLM Değerlendirme Yanlılığı
* **Bağlam ve Mekanizma:** Chi et al. (1989) öz-açıklamanın derin kavramsal öğrenmeyi tetiklediğini kanıtlamıştır. Öğrenci "Bu çarpanlara ayırma adımını neden seçtin?" sorusuna serbest Türkçe yanıt verdiğinde, LLM anlamsal kavrayış ile akademik jargon kullanımını ayırt etmek zorundadır.
* **Hipotezler:**
  * $H_0: \text{LLM Puanları ile Uzman Eğitici Puanları Arasındaki } \kappa_{\text{Cohen}} < 0.70$ (Jargon yanlılığı $\ge \%20$).
  * $H_1: \text{LLM Puanları ile Uzman Eğitici Puanları Arasındaki } \kappa_{\text{Cohen}} \ge 0.85$ (Few-shot semantik zincirleme ile).
* **Değişkenler:** Bağımsız: Prompt mühendisliği / AST destekli kavramsal bağlam enjeksiyonu; Bağımlı: İki dereceli Cohen's Kappa ($\kappa$), Falsely Penalized Informal Language Rate (Hatalı Ceza Oranı).
* **Yanlışlanabilirlik Eşiği:** Eğer LLM, formel matematiksel terim içermeyen fakat anlamsal olarak doğru olan halk dili açıklamalarını (örn. *"iki tarafı da eşitlemek için fazlalığı karşıya attım"*) %10'dan daha yüksek bir hata payıyla "yanlış/yetersiz" puanlarsa, doğal dil öz-açıklama değerlendirmesi zorunlu adımlardan çıkarılıp opsiyonel ipucuna dönüştürülür.

---

### 2.4. BKT'den Derin Bilgi Takibine (DKT/SAKT) Dinamik Geçiş Eşiği ve Açıklanabilirlik Takası
* **Bağlam ve Mekanizma:** Klasik Bayesyen Bilgi Takibi (BKT), 4 parametre ($L_0, T, G, S$) ile her beceri için şeffaf ve açıklanabilir olasılıklar üretir. Transformer tabanlı Derin Bilgi Takibi (DKT, SAKT) ise beceriler arası örtük etkileşimleri yakalar ancak kara kutudur (black-box).
* **Hipotezler:**
  * $H_0: \text{AUC}_{\text{DKT}} - \text{AUC}_{\text{BKT}} < 0.03 \quad (\text{Küçük veri kohortunda, } N_{\text{interactions}} < 50.000)$
  * $H_1: \text{AUC}_{\text{DKT}} - \text{AUC}_{\text{BKT}} \ge 0.08 \quad (\text{Büyük veri kohortunda, } N_{\text{interactions}} \ge 200.000)$
* **Değişkenler:** Bağımsız: Toplam kullanıcı etkileşim hacmi ($N$); Bağımlı: Bir sonraki adım başarı tahmin AUC-ROC değeri, SHAP tabanlı pedagojik karar gerekçelendirme kararlılığı.
* **Yanlışlanabilirlik Eşiği:** DKT modelinin AUC skoru BKT'den en az 0.05 puan yüksek değilse ve pedagojik kararlar kural tabanlı iskele motoruna deterministik olarak aktarılamıyorsa BKT omurgası korunur.

---

### 2.5. İskele Sönümleme Hızı ve Uzmanlık Tersinme Etkisi (Expertise Reversal Effect)
* **Bağlam ve Mekanizma:** Kalyuga et al. (2003), acemiler için hayati olan yönlendirici iskelelerin (worked examples, hints), öğrenci uzmanlaştıkça gereksiz bir kognitif yüke dönüşerek performansı düşürdüğünü (Expertise Reversal Effect) göstermiştir. İskelenin hangi türevle ($\frac{d\,\text{Scaffold}}{dt}$) geri çekileceği kritik bir optimizasyon problemidir.
* **Hipotezler:**
  * $H_0: \text{Performans}_{\text{DinamikFading}} \le \text{Performans}_{\text{SabitAdımlıFading}}$
  * $H_1: \text{Performans}_{\text{DinamikFading}} > \text{Performans}_{\text{SabitAdımlıFading}} \quad (\text{Effect size } d \ge 0.45)$
* **Değişkenler:** Bağımsız: Sönümleme algoritması (Sabit problem sayısı kuralı vs Anlık gecikme süresi + hata olasılığı türevli dinamik sönümleme); Bağımlı: Akıcı problem çözme hızı, öğrenci hayal kırıklığı skoru (frustration index).
* **Yanlışlanabilirlik Eşiği:** Dinamik sönümleme, ileri düzey öğrencilerde adım başına harcanan sürede %20'den fazla azalma sağlamazsa basitleştirilmiş lineer sönümleme kuralı uygulanır.

---

### 2.6. Verimli Başarısızlık (Productive Failure) ve Doğrudan Öğretim Zamanlaması
* **Bağlam ve Mekanizma:** Manu Kapur (2008), öğrencilerin bir kavramı öğrenmeden önce o kavramla ilgili çözümsüz veya zor problemlerle boğuşmasının (Productive Failure), doğrudan çözümlü örnek görmeye kıyasla derin şema inşasını artırdığını savunur. Ancak aşırı zorlanma öğrenciyi sistemden koparabilir.
* **Hipotezler:**
  * $H_0: \text{UzakTransfer}_{\text{ProductiveFailure}} \le \text{UzakTransfer}_{\text{DirectInstructionFirst}}$
  * $H_1: \text{UzakTransfer}_{\text{ProductiveFailure}} > \text{UzakTransfer}_{\text{DirectInstructionFirst}} \quad (p < 0.01)$
* **Değişkenler:** Bağımsız: Pedagojik sıra (Önce Keşif/Hata $\rightarrow$ Sonra Çözümlü Örnek vs Önce Çözümlü Örnek $\rightarrow$ Sonra Problem); Bağımlı: Uzak transfer başarı yüzdesi (FTR), terk/drop-out oranı.
* **Yanlışlanabilirlik Eşiği:** Önce keşif yaptıran grupta seansı terk etme oranı (drop-out rate) kontrol grubuna göre %15'ten fazla artarsa, verimli başarısızlık modu varsayılan olmaktan çıkarılıp "yüksek motivasyonlu" profillere sınırlandırılır.

---

### 2.7. Nöro-Sembolik AST Doğrulama Gecikmesi ve Sokratik Diyalog Akıcılığı
* **Bağlam ve Mekanizma:** LLM'in ürettiği her Sokratik yanıtın ve öğrencinin yazdığı cebirsel ifadenin deterministik Python/SymPy AST motorundan geçirilmesi ek bir hesaplama gecikmesi (latency: $800\text{ms} - 2200\text{ms}$) ekler. Bu gecikmenin kognitif akış (flow state) üzerindeki etkisi bilinmemektedir.
* **Hipotezler:**
  * $H_0: \text{Akış Skoru (Flow)}_{\text{DüşükGecikme/Doğrulamasız}} > \text{Akış Skoru}_{\text{YüksekGecikme/ASTDoğrulamalı}}$
  * $H_1: \text{Öğrenme Kazanımı (R-LGpM)}_{\text{ASTDoğrulamalı}} > \text{R-LGpM}_{\text{Doğrulamasız}} \quad (\text{Gecikmeye rağmen matematiksel kesinlik üstündür})$
* **Değişkenler:** Bağımsız: Sistem yanıt süresi ($T_{\text{latency}} < 500\text{ms}$ halüsinasyon riskli vs $T_{\text{latency}} \approx 1800\text{ms}$ tam sembolik denetimli); Bağımlı: Matematiksel işlem hatası toleransı, kullanıcı akış anketi skoru, R-LGpM.
* **Yanlışlanabilirlik Eşiği:** AST denetiminin sağladığı matematiksel sıfır-hata güvencesi, diyalog gecikmesi kaynaklı öğrenci memnuniyetsizliğini telafi edemez ve terk oranını %20 artırırsa asenkron spekülatif doğrulama (speculative decoding) mimarisine geçilir.

---

### 2.8. STEM Dışı ve Yorumlayıcı Alanlarda Doğrulama Katmanının Genişletilebilirliği
* **Bağlam ve Mekanizma:** Cebir ve mantıkta tek bir kanonik doğruluk (AST eşdeğerliği) varken; felsefe, edebiyat analizi veya tarihsel nedensellik gibi alanlarda argümantasyon yapısı (Toulmin argüman modeli) geçerlidir.
* **Hipotezler:**
  * $H_0: \text{Deterministik Graflar Argüman Haritalama Alanında } \kappa < 0.60 \text{ Anlaşma Sağlar.}$
  * $H_1: \text{Toulmin Şeması Entegre Edilmiş Nöro-Sembolik Çözümleyici, İnsan Değerlendiricilerle } \kappa \ge 0.75 \text{ Uyum Gösterir.}$
* **Değişkenler:** Bağımsız: Argüman ayrıştırıcı graf kuralları; Bağımlı: Öğrencinin iddia, veri, gerekçe ve çürütme adımlarını tespit doğruluğu.
* **Yanlışlanabilirlik Eşiği:** Eğer argüman tabanlı sembolik denetleyici, öğrencinin tutarlı felsefi argümanlarını %25'in üzerinde yapısal hata olarak işaretlerse sistem bu alanlarda kural tabanlı doğrulama yerine çoklu model konsensüsüne (Multi-LLM Jury) evrilir.

---

### 2.9. Biyometrik Olmayan Davranışsal Telemetri ile Bilişsel Tükenmişlik Tespiti
* **Bağlam ve Mekanizma:** Göz takip cihazları veya EEG pratik değildir. Tuş vuruş aralıkları (keystroke dynamics), fare gezinme entropisi (mouse trajectory entropy) ve adım onaylama gecikmelerinden kognitif tükenmişlik (burnout / ego depletion) kestirilebilir mi?
* **Hipotezler:**
  * $H_0: \text{Telemetri Öznitelikleri ile NASA-TLX Zihinsel Yorgunluk Korelasyonu } r < 0.30$
  * $H_1: \text{Tuş Vuruş Varyansı + İpucu Tıklama İvmesi } r \ge 0.65 \quad (p < 0.001)$
* **Değişkenler:** Bağımsız: İki vuruş arası bekleme süreleri (inter-keystroke intervals), silme/düzeltme frekansı, kararsız fare hareketleri; Bağımlı: Seans içi anlık öz-bildirim yorgunluk skoru.
* **Yanlışlanabilirlik Eşiği:** Davranışsal telemetri, kognitif çöküş anlarını rastgele tahmin seviyesinin (AUC $\le 0.60$) üzerine çıkaramazsa sistem içi zorunlu mola (micro-break) uyarıları telemetriye değil sabit süre sayacına (Pomodoro kuralı: her 25 dk) bağlanır.

---

### 2.10. FSRS Aralıklı Tekrar ile ACT-R Bildirimsel Bellek Aktivasyon Sentezi
* **Bağlam ve Mekanizma:** FSRS (Free Spaced Repetition Scheduler) pratik ve ampiriktir. John Anderson'ın ACT-R bilişsel mimarisi ise bellek izi aktivasyonunu ($A_i = \ln \sum t_k^{-d}$) formüle eder. Bu iki yaklaşımın hibritlenmesi tahmin gücünü artırır mı?
* **Hipotezler:**
  * $H_0: \text{RMSE}_{\text{Hybrid(FSRS+ACT-R)}} \ge \text{RMSE}_{\text{StandardFSRS}}$
  * $H_1: \text{RMSE}_{\text{Hybrid(FSRS+ACT-R)}} < \text{RMSE}_{\text{StandardFSRS}} - 0.03$
* **Değişkenler:** Bağımsız: Tekrar zamanlama algoritması; Bağımlı: 14 ve 30 günlük kalıcılık yoklama testlerindeki tahmin hatası (Root Mean Square Error).
* **Yanlışlanabilirlik Eşiği:** Hibrit model 30 günlük kalıcılık tahmininde klasik FSRS'e göre en az %5 hata iyileşmesi sağlamazsa matematiksel sadelik adına standart FSRS korunur.

---

## 3. ÖN KAYITLI DENEY TASARIMI (PRE-REGISTRATION STUDY DESIGN - OSF STANDARDI)

Bu protokol, Open Science Framework (OSF) ve APA Ön Kayıt Kriterlerine harfiyen uyumlu olarak tescil edilmek üzere tasarlanmıştır.

```text
========================================================================================
OSF PRE-REGISTRATION PROTOCOL: NEURO-SYMBOLIC COGNITIVE TUTORING ENGINE RCT (N = 600)
========================================================================================
Tescil Başlığı: Kapalı Çevrim Nöro-Sembolik Sokratik Öğretim Motorunun Matematiksel Kavram
                Edinimi ve Uzun Vadeli Bellek Kalıcılığı Üzerindeki Nedensel Etkisi
Baş Araştırmacı: Kişisel Öğrenme Motoru Araştırma Grubu
Hedef Tescil Platformu: Open Science Framework (osf.io) / AsPredicted.org
========================================================================================
```

### 3.1. Araştırma Soruları ve Hipotezler
1. **Birincil Soru:** Kapalı çevrim nöro-sembolik iskele motoru, geleneksel statik video/soru modeline ve kısıtlanmamış üretken yapay zekaya (ChatGPT-4o) kıyasla 14 günlük kalıcılık düzeltmeli öğrenme kazancını (R-LGpM) istatistiksel olarak anlamlı biçimde artırır mı?
2. **Yönlü Hipotez:** Nöro-sembolik motor altındaki grup, kontrol ve naive AI gruplarına göre $d \ge 0.45$ etki büyüklüğüyle daha yüksek R-LGpM ve $d \ge 0.50$ daha yüksek uzak transfer skoru sergileyecektir.

---

### 3.2. Değişkenlerin Operasyonel Tanımları

#### A. Bağımsız Değişkenler (Independent Variables - IV)
* **IV 1: Pedagojik Dağıtım Motoru (Factor A - 3 Seviye):**
  * *Seviye A1 (Aktif Kontrol):* Geleneksel EdTech Modeli (15 dk video anlatımı + 10 statik çoktan seçmeli/açık uçlu alıştırma + statik tam çözüm metni).
  * *Seviye A2 (Naive Generative AI):* Kısıtlanmamış GPT-4o Arayüzü (Öğrenci serbestçe soru sorabilir, tam çözüm isteyebilir, prompt kısıtlaması yoktur).
  * *Seviye A3 (Deneysel Kol):* Nöro-Sembolik Sokratik Motor (İskele sönümlemesi, sembolik AST hata denetimi, zorunlu adım doğrulama, FSRS aralıklı tekrar).
* **IV 2: Metabilişsel Kalibrasyon İskelesi (Factor B - 2 Seviye - İçiçe Tasarım):**
  * *Seviye B1:* Her adım öncesi açık güven derecelendirmesi (%20-%100).
  * *Seviye B2:* Güven derecelendirmesi yok (yalnızca arka plan telemetrisi).

#### B. Bağımlı Değişkenler (Dependent Variables - DV)
* **Birincil Çıktı (Primary Endpoint):**
  * **R-LGpM:** $T_{\text{active}}$ süresine normalize edilmiş 14 günlük Hake kazanç sağkalım skoru ($[g \cdot S(14)] / T_{\text{active}}$).
* **İkincil Çıktılar (Secondary Endpoints):**
  * **14. Gün Kalıcılık Puanı:** $T = 14\text{d}$ gecikmeli izomorfik test başarı yüzdesi.
  * **Uzak Transfer Başarısı (FTR):** Yüzey özellikleri farklı, derin kavramsal yapısı izomorfik 5 adet transfer probleminin çözüm yüzdesi.
  * **Bilişsel Verimlilik İndeksi ($E$):** Paas & Van Merriënboer formülü ($[z_P - z_R]/\sqrt{2}$).
  * **Beklenen Kalibrasyon Hatası (ECE):** Öğrenci güveni ile gerçek adım doğruluğu arasındaki mutlak sapma.
  * **İskele Çekilme Eğimi ($\beta_{\text{hint}}$):** İpucu talep sıklığının zamana göre regresyon katsayısı.

#### C. Manipülasyon Kontrolleri (Manipulation Checks)
1. **Zihinsel Çaba Kontrolü:** Her seans bitiminde 9-dereceli Paas Zihinsel Çaba Skoru ve NASA-TLX zihinsel talep alt boyutu uygulanarak kognitif yük farkı tescil edilir.
2. **Müdahale Sadakati (Treatment Fidelity):** Telemetri loglarında Seviye A3 öğrencilerinin çözümü doğrudan kopyalamadığı, her adımda AST doğrulaması aldığı doğrulanır. Seviye A2 loglarında ise LLM'in tam çözüm üretme sıklığı kaydedilir.
3. **Dikkat ve Sahtekarlık Kontrolü (Catch Trials):** Test maddeleri arasına açık talimat içeren kontrol soruları (örn. *"Bu soruyu okuduysanız lütfen 'B' şıkkını işaretleyiniz"*) yerleştirilir. Başarısız olanlar veri setinden ayıklanır.

---

### 3.3. Katılımcı Hariç Tutma (Exclusion) Kriterleri
Ön kayıt kapsamında aşağıdaki veriler analize dahil edilmeden elenecektir:
1. **Hız Yapanlar (Speeders):** Adım başına medyan okuma ve çözüm süresi 4 saniyenin altında olan oturumlar (bot veya rastgele tıklama).
2. **Eksik Seans Tamamlama:** Ön-testi tamamlayıp ana müdahalenin %50'sinden fazlasını bitirmeden platformu terk edenler (bu veriler ITT analizinde korunur, Per-Protocol analizinden çıkarılır).
3. **Ön-Test Tavan Etkisi:** Ön-test skoru $\ge \%90$ olan öğrenciler (kazanım alanı kalmadığından birincil etki analizine dahil edilmez).
4. **Çoklu Hesap / Hile:** Aynı IP veya parmak iziyle birden fazla grupta hesap açtığı tespit edilen kullanıcılar.

---

### 3.4. Doğrulayıcı Veri Analizi Planı (Confirmatory Analysis Plan)

1. **Birincil Analiz:** R-LGpM çıktısı üzerinde Tedavi Grupları (A, B, C) faktörü için Ön-test skorunu kovaryat olarak içeren **Tek Yönlü Kovaryans Analizi (ANCOVA)** yürütülecektir:
   $$\text{R-LGpM}_{i} = \beta_0 + \beta_1 \mathbb{I}(\text{Group}_B) + \beta_2 \mathbb{I}(\text{Group}_C) + \gamma \text{PreScore}_i + \varepsilon_i$$
2. **Post-Hoc Karşılaştırmalar:** Tukey HSD testi ile aile-bazı tip I hata oranı $\alpha = 0.05$ seviyesinde korunacaktır.
3. **Boylamsal ve Hiyerarşik Yapı:** Öğrencilerin zaman içindeki kalıcılık değişimleri ($T=0, 7\text{d}, 14\text{d}, 30\text{d}$) **Doğrusal Karma Modeller (Linear Mixed-Effects Models - LMM)** ile incelenecektir (Rastgele kesim noktaları [random intercepts] öğrenci bazında tanımlanacaktır).
4. **Kayıp Veri Protokolü:** Takip testlerine katılmayan öğrenciler için **Full Information Maximum Likelihood (FIML)** kullanılacak, ayrıca çoklu atama (Multiple Imputation by Chained Equations - MICE, $m = 20$) ile duyarlılık analizi yapılacaktır.

---

## 4. LLM SOKRATİK PEDAGOJİSİNİN İNSAN ÖĞRETMENLERLE ÇİFT KÖR (DOUBLE-BLIND) KARŞILAŞTIRMA PROTOKOLÜ

Yapay zekanın eğitimdeki nihai rüştü, birebir insan öğretmen (1:1 Human Tutoring) kalitesiyle ölçülür (Bloom'un 2-Sigma Problemi; Bloom, 1984). Bu protokol, nöro-sembolik motorumuzu uzman insan eğitimcilerle bilimsel hakem heyeti önünde yarıştırır.

```text
               ┌─────────────────────────────────────────────────────────┐
               │         ÖĞRENCİ HAVUZU (N = 150 Lise Öğrencisi)         │
               └────────────────────────────┬────────────────────────────┘
                                            │
                             Çift Kör Rastgele Dağıtım
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               ▼                            ▼                            ▼
     [ KOL 1: İNSAN UZMAN ]       [ KOL 2: NÖRO-SEMBOLİK AI ]   [ KOL 3: NAIVE LLM ]
           (N = 50)                     (N = 50)                     (N = 50)
      Deneyimli Matematik          Bizim Kapalı Çevrim          Kısıtlanmamış
      Öğretmeni (1:1 Chat)         Sokratik Motorumuz           GPT-4o Chatbot
               │                            │                            │
               └────────────────────────────┼────────────────────────────┘
                                            │
                                            ▼
               ┌─────────────────────────────────────────────────────────┐
               │    STANDARTLAŞTIRILMIŞ WEB TERMİNALİ ARAYÜZÜ (BLIND)    │
               │  - Öğrenci muhatabının insan mı yapay zeka mı olduğunu  │
               │    asla bilmez (Tipografi, gecikme simülatörü eşit).     │
               └────────────────────────────┬────────────────────────────┘
                                            │
                                            ▼
               ┌─────────────────────────────────────────────────────────┐
               │     BAĞIMSIZ KÖR DEĞERLENDİRİCİLER (BLIND RATERS)       │
               │  - 3 Bağımsız Kıdemli Eğitim Bilimci ve Matematikçi      │
               │  - Anonim diyalog dökümlerini Sokratik Rubrikle puanlar  │
               └─────────────────────────────────────────────────────────┘
```

---

### 4.1. Çift Kör Arayüz ve Gecikme Standartlaştırması (Latency Matcher)
İnsan ile yapay zekanın arayüzde ayırt edilmesini engellemek için teknik önlemler:
1. **Ortak Terminal:** Tüm iletişim aynı web tabanlı sohbet arayüzü üzerinden gerçekleşir (LaTeX matematik editörü ve çizim tuvali ortaktır).
2. **Yapay Zeka Yazma Gecikmesi Simülatörü:** LLM yanıtları milisaniyeler içinde hazır olsa dahi, insan öğretmen yazma hızını simüle eden bir gecikme fonksiyonuyla parça parça (typing effect) akıtılır:
   $$T_{\text{stream\_delay}} = \text{KelimeSayısı} \times (180\text{ms} \pm 40\text{ms}) + T_{\text{düşünme\_gecikmesi}}$$
3. **İnsan Öğretmen Kısıtı:** Öğretmenler öğrencilerin kimlik bilgilerine veya deney kolu detaylarına erişemez; yalnızca saf pedagojik rehberlik verirler.

---

### 4.2. Sokratik Sadakat ve Pedagojik Kalite Rubriği (Socratic Fidelity Scoring Rubric)

Bağımsız kör değerlendiriciler, anonimleştirilmiş seans loglarını aşağıdaki 5 eksende $[1 - 5]$ Likert skalasında bağımsız olarak puanlar:

```text
+------------------------------------+-------------------------------------------------------------------------+
| BOYUT                              | OPERASYONEL KRİTER VE PUANLAMA STANDARDI                                |
+------------------------------------+-------------------------------------------------------------------------+
| 1. Soru / Açıklama Oranı           | Öğretici/Ajan doğrudan bilgi aktarmak yerine soru soruyor mu?           |
|    (Question-to-Explanation Ratio) | 5 Puan: Yanıtların en az %75'i yönlendirici soru niteliğindedir.        |
|                                    | 1 Puan: Didaktik düz anlatım, soru sorulmuyor.                          |
+------------------------------------+-------------------------------------------------------------------------+
| 2. Sıfır Cevap İfşası              | Öğrenci tıkandığında nihai adım veya nihai cevap açıkça söyleniyor mu?  |
|    (Zero Answer Leakage)           | 5 Puan: Asla cevap söylenmez; adım adım alt sorulara parçalanır.        |
|                                    | 1 Puan: Doğrudan formül veya sonuç öğrenciye teslim edilir.             |
+------------------------------------+-------------------------------------------------------------------------+
| 3. ZPD Hizalaması                  | Verilen ipucu öğrencinin Yakınsak Gelişim Alanına uygun mu?             |
|    (Zone of Proximal Development)  | 5 Puan: İpucu öğrencinin anlık hata yaptığı tam bilişsel eşiğe oturur.  |
|                                    | 1 Puan: Ya aşırı bariz (tribial) ya da tamamen anlaşılamaz derecede zor.|
+------------------------------------+-------------------------------------------------------------------------+
| 4. Kavram Yanılgısı Teşhisi        | Öğrencinin sembolik hatasının altındaki kognitif kök neden bulundu mu?  |
|    (Misconception Diagnosis)       | 5 Puan: Kök yanılgı adlandırılır ve yüzleştirici karşı-örnek sunulur.   |
|                                    | 1 Puan: Sadece "yanlış yaptın, tekrar dene" denir.                      |
+------------------------------------+-------------------------------------------------------------------------+
| 5. Bilişsel Sahiplik Aktarımı      | Çözümün sahibi öğrenci mi hissettirildi?                                |
|    (Epistemic Agency Transfer)     | 5 Puan: Başarı bütünüyle öğrencinin zihinsel keşfi olarak tescillendi.  |
|                                    | 1 Puan: Öğretici baskın figür olarak kaldı.                             |
+------------------------------------+-------------------------------------------------------------------------+
```

---

### 4.3. Eşdeğerlik Testi (TOST - Two One-Sided Tests) ile İnsan Öğretmene Non-Inferiority İspatı

Amacımız yapay zekanın insan öğretmenle eşdeğer olduğunu veya en azından kabul edilemez derecede geri kalmadığını (**Non-Inferiority**) ispatlamaktır. Klasik hipotez testinde $p > 0.05$ çıkması eşdeğerlik kanıtı sayılamaz (absence of evidence is not evidence of absence). Bu nedenle **Schuirmann'ın İki Tek Yönlü Test (TOST)** metodolojisi işletilir.

#### Formel Hipotezler:
Eşdeğerlik marjı (Equivalence Margin) eğitim bilimleri literatüründeki klinik anlamlılık standardına göre $\Delta = 0.20 \cdot \sigma$ (Cohen's $d = 0.20$) olarak kilitlenir:

$$H_{01}: \mu_{\text{AI}} - \mu_{\text{Human}} \le -\Delta \quad (\text{Yapay zeka insandan kabul edilemez düzeyde kötüdür})$$
$$H_{02}: \mu_{\text{AI}} - \mu_{\text{Human}} \ge +\Delta \quad (\text{Yapay zeka insandan aşırı farklıdır})$$
$$H_1: -\Delta < \mu_{\text{AI}} - \mu_{\text{Human}} < +\Delta \quad (\text{Yapay zeka ve insan öğretmen istatistiksel olarak eşdeğerdir})$$

#### Test İstatistiği:
$$t_1 = \frac{(\bar{X}_{\text{AI}} - \bar{X}_{\text{Human}}) - (-\Delta)}{SE_{\text{diff}}}$$
$$t_2 = \frac{(\bar{X}_{\text{AI}} - \bar{X}_{\text{Human}}) - (+\Delta)}{SE_{\text{diff}}}$$

Hem $t_1 > t_{crit}$ hem de $t_2 < -t_{crit}$ ($p < 0.05$) olduğunda $H_0$ reddedilir ve **Nöro-Sembolik Sokratik Motorumuzun, 1:1 uzman insan öğretmenle pedagojik olarak eşdeğer olduğu ampirik ve matematiksel olarak tescil edilir.**
