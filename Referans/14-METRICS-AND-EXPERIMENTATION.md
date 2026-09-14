# 14-METRICS-AND-EXPERIMENTATION.md
# METRİKLER VE DENEYSEL DOĞRULAMA PLANI (METRICS & EXPERIMENTATION)
## Bilişsel Metrikler, A/B Deney Mimarisi, İstatistiksel Güç Analizi ve Nedensel Çıkarım Protokolü

---

## 1. KANTİTATİF METRİK MATRİSİ VE TAM MATEMATİKSEL FORMÜLASYONLAR

Platformun pedagojik etkinliği, bilişsel psikoloji ve psikometri literatüründe kabul görmüş, ampirik olarak doğrulanabilir matematiksel modeller üzerinden ölçülür.

```text
+------------------------------------+-----------------------------------------------------------------------------------------+
| METRİK ADI                         | FORMÜLASYON VE BİLİŞSEL TEMEL                                                           |
+------------------------------------+-----------------------------------------------------------------------------------------+
| 1. R-LGpM                          | R-LGpM = [g * S(t = 14)] / T_active                                                     |
|    (Retention-Discounted Gain/Min) | Normalleştirilmiş öğrenme kazancının 14 günlük kalıcılık sağkalımı ve harcanan aktif   |
|                                    | süreye normalize edilmiş nihai kognitif sermaye verimlilik katsayısı.                   |
+------------------------------------+-----------------------------------------------------------------------------------------+
| 2. Bilişsel Verimlilik (Paas E)    | E = (z_P - z_R) / sqrt(2)                                                               |
|    (Cognitive Efficiency)          | Standartlaştırılmış öğrenme performansı ile harcanan zihinsel çaba arasındaki vektörel |
|                                    | fark. (Paas & Van Merriënboer, 1993).                                                   |
+------------------------------------+-----------------------------------------------------------------------------------------+
| 3. Süre-Doğruluk Pareto Sınırı     | P* = {theta in Theta | not exists theta': A(theta') >= A(theta) ve t(theta') <= t(theta)}|
|    (Speed-Accuracy Pareto Frontier)| Drift-Diffusion Modeli (DDM) tabanlı hız-doğruluk dengesinde dominant strateji tayini.  |
+------------------------------------+-----------------------------------------------------------------------------------------+
| 4. Beklenen Kalibrasyon Hatası     | ECE = sum_{m=1}^M (|acc(B_m) - conf(B_m)| * |B_m| / N)                                  |
|    (Expected Calibration Error)    | Metabilişsel kalibrasyon sapması (Naeini et al., 2015). Hedef: ECE < 0.08.              |
+------------------------------------+-----------------------------------------------------------------------------------------+
| 5. İskele Çekilme Eğimi (beta_hint)| HintCount(p) = alpha + beta_hint * ProblemIndex, beta_hint < 0                          |
|    (Assistance Fading Slope)       | Bir alt kavramda ardışık problemlerde talep edilen yardımın negatif eğimi.             |
+------------------------------------+-----------------------------------------------------------------------------------------+
| 6. Uzak Transfer Oranı (FTR)       | FTR = CorrectUnseenFarTransferTasks / TotalFarTransferTasks                             |
|    (Far Transfer Rate)             | Yüzey yapısı (surface features) farklı, derin şeması (deep structure) izomorfik görev.  |
+------------------------------------+-----------------------------------------------------------------------------------------+
```

---

### 1.1. R-LGpM (Retention-Discounted Learning Gain per Minute) Tam Matematiksel Formülasyonu

Klasik eğitim teknolojileri, öğrencinin platformda geçirdiği süreyi (time-on-platform) maksimize etmeye odaklanır. Oysa kognitif bilim perspektifinden zaman kısıtlı bir zihinsel kaynaktır; ideal bir öğretim motoru **minimum sürede maksimum kalıcı kavramsal kazanım** üretmelidir.

$$\text{R-LGpM} = \frac{g \cdot S(t = 14)}{T_{\text{active}}}$$

Burada:
* $g$: Hake (1998) Normalleştirilmiş Öğrenme Kazancı (Normalized Learning Gain).
* $S(t = 14)$: Kaplan-Meier 14 Günlük Kalıcılık Sağkalım İhtimali (Survival Probability).
* $T_{\text{active}}$: Öğrencinin hedeflenen bilgi bileşenini (KC - Knowledge Component) kazanırken harcadığı toplam aktif seans süresi (dakika cinsinden).

#### A. Hake (1998) Normalize Kazanç ($g$) ve Uç Durum Düzeltmeleri
Öğrencinin ön bilgi seviyesinden bağımsız net kavramsal sıçramasını ölçmek için Hake normalize kazancı kullanılır:

$$g = \frac{\text{PostScore} - \text{PreScore}}{\text{MaxScore} - \text{PreScore}}$$

*Skorlar $[0, 100]$ aralığında normalize edildiğinde $\text{MaxScore} = 100$ alınır:*
$$g = \frac{\text{Post} - \text{Pre}}{100 - \text{Pre}}$$

**Sınır Koşulları ve Düzeltmeler (Marx & Cummings, 2007):**
1. **Tavan Etkisi ($\text{PreScore} = 100$):** Ön testte tam puan alan öğrenci için payda sıfır olur. Bu öğrenciler birincil öğrenme kohortundan çıkarılır; üst düzey zenginleştirme (enrichment / far transfer) kohortuna atanır ($g$ tanımsızdır, tavan analizi yapılır).
2. **Negatif Kazanç ($\text{PostScore} < \text{PreScore}$):** Öğrenci müdahale sonrasında kavram yanılgısına düşmüşse veya tahmin faktörüyle ön testte şans eseri yüksek almışsa $g < 0$ çıkar. Asimetriyi önlemek için Marx & Cummings formülasyonu uygulanır:
   $$\text{Eğer } \text{Post} < \text{Pre} \implies g = \frac{\text{Post} - \text{Pre}}{\text{Pre}}$$
3. **Kategorizasyon Eşikleri (Hake, 1998):**
   * Yüksek Kazanç ($g \ge 0.70$)
   * Orta Kazanç ($0.30 \le g < 0.70$)
   * Düşük Kazanç ($g < 0.30$)

#### B. Kaplan-Meier 14 Günlük Kalıcılık Sağkalım Tahmincisi ($S(t)$)
Öğrenmenin gerçekleşmesi yeterli değildir; edinilen bilginin Ebbinghaus unutma eğrisine direnç göstermesi şarttır. Kalıcılık, sağkalım analizi (Survival Analysis) çerçevesinde modellenir.

Bir kavramın unutulması veya kognitif gerileme yaşaması bir "olay" (event / cognitive lapse) olarak tanımlanır. Bir öğrenci, $t$ anında yapılan aralıklı geri çağırma (retrieval probe) testinde başarı eşiğinin ($\theta_{\text{mastery}} = 0.80$) altına düşerse olay gerçekleşmiş ($d_i = 1$) sayılır. 14 gün boyunca aktif kalıp testi başarıyla geçenler veya çalışmayı bırakmayanlar sağdan sansürlenir (right-censored, $c_i$).

Kaplan-Meier çarpım-limit tahmincisi (Kaplan & Meier, 1958):

$$S(t) = \prod_{t_i \le t} \left(1 - \frac{d_i}{n_i}\right)$$

Burada:
* $t_i$: Kalıcılık yoklama zamanları ($t_1 = 1\text{ gün}, t_2 = 3\text{ gün}, t_3 = 7\text{ gün}, t_4 = 14\text{ gün}$).
* $d_i$: $t_i$ zaman aralığında kalıcılık kriterini kaybeden (başarısız olan) öğrenci sayısı.
* $n_i$: $t_i$ zaman noktası hemen öncesinde risk altındaki (henüz unutmamış ve sansürlenmemiş) aktif öğrenci sayısı.

$S(14)$, öğrencinin müdahaleden sonraki 14. günde bilgiyi zihninde tutma olasılığıdır ($0 \le S(14) \le 1.0$).

#### C. Toplam Aktif Seans Süresi ($T_{\text{active}}$)
Pasif bekleme veya ekran açıkken başka bir sekmeye geçme gibi durumları ayıklamak için aktif süre telemetri kurallarıyla filtrelenir:

$$T_{\text{active}} = \sum_{k=1}^K \min\left(\Delta t_k, \tau_{\text{threshold}}\right) \cdot \mathbb{I}(\text{Event}_k \in \mathcal{E}_{\text{active}})$$

* $\Delta t_k$: İki ardışık telemetri olayı arasındaki geçen süre.
* $\tau_{\text{threshold}} = 120\text{ saniye}$ (2 dakikadan uzun eylemsizlikler "boşta kalma / idle" sayılarak kırpılır).
* $\mathcal{E}_{\text{active}}$: Aktif kognitif etkileşimler (tuş vuruşu, formül düzenleme, adım onaylama, AST hata yanıtı, çizim yapma).
* $T_{\text{active}}$ dakika birimine dönüştürülür: $T_{\text{active}} = \frac{\text{Aktif Saniye}}{60}$.

#### D. Boyut Analizi ve Yorumlama
$$\text{Birim: } [\text{R-LGpM}] = \frac{[\text{Normalize Kazanç}] \cdot [\text{Boyutsuz Olasılık}]}{[\text{Dakika}]} = \text{dk}^{-1}$$
*Örnek Senaryo:*
* Ön-test: %30, Son-test: %86 $\implies g = (86 - 30)/(100 - 30) = 56/70 = 0.80$
* 14. Gün Kalıcılık Olasılığı: $S(14) = 0.85$
* Aktif Öğrenme Süresi: 24 dakika
$$\text{R-LGpM} = \frac{0.80 \times 0.85}{24} = \frac{0.68}{24} = 0.02833\text{ dk}^{-1} \quad (2.83\%\text{ kalıcı kazanım / aktif dakika})$$

---

### 1.2. Bilişsel Verimlilik Metrikleri (Paas & Van Merriënboer Modeli)

Eğitimde yüksek performans, aşırı zihinsel yüklenme pahasına elde ediliyorsa sürdürülebilir değildir (Cognitive Overload). Fred Paas ve Jeroen van Merriënboer (1993) tarafından geliştirilen Bilişsel Verimlilik ($E$) modeli, performans ile harcanan zihinsel çabayı (Mental Effort / Cognitive Load) tek bir normalize metrikte birleştirir.

$$E = \frac{z_P - z_R}{\sqrt{2}}$$

Burada:
* $z_P$: Standartlaştırılmış öğrenme performansı ($z$-score).
  $$z_P = \frac{P - \mu_P}{\sigma_P} \quad (P = \text{PostTest skoru veya } g)$$
* $z_R$: Standartlaştırılmış zihinsel çaba skoru ($z$-score).
  $$z_R = \frac{R - \mu_R}{\sigma_R} \quad (R = \text{9-dereceli Paas Zihinsel Çaba Skoru veya NASA-TLX})$$
* $\sqrt{2}$: $P = R$ referans köşegenine olan dik mesafeyi hesaplayan geometrik normalizasyon katsayısı.

#### Bilişsel Verimlilik Faz Uzayı (Paas 2D Coordinate Space)

```text
              Yüksek Performans (z_P)
                         ▲
                         │
        BÖLGE 2          │          BÖLGE 1
  [YÜKSEK VERİMLİLİK]    │   [AĞIR BİLİŞSEL YÜK]
  Düşük Çaba, Yüksek Başarı│   Yüksek Çaba, Yüksek Başarı
  (Hedef Durum: E > 0)   │   (Zorlayıcı / Sürdürülemez)
                         │
 ────────────────────────┼────────────────────────► Yüksek Zihinsel
                         │                          Çaba (z_R)
        BÖLGE 3          │          BÖLGE 4
     [İLGİSİZLİK]        │     [BİLİŞSEL BOĞULMA]
  Düşük Çaba, Düşük Başarı │   Yüksek Çaba, Düşük Başarı
  (Apatik / Kopma)       │   (Fatal Aşırı Yük: E < 0)
                         │
```

* **Yorum:**
  * $E > 0$: Yüksek Verimlilik (Öğrenci zihinsel kapasitesini gereksiz yüklerle [extraneous load] tüketmeden, germane load ile şema inşası başarmıştır).
  * $E < 0$: Düşük Verimlilik (Öğrenci arayüz karmaşası, kötü iskele veya açıklama eksikliği nedeniyle aşırı çaba sarf etmiş ancak başarı elde edememiştir).
  * Hedef Kriterimiz: Nöro-sembolik motor altındaki grubun bilişsel verimlilik ortalamasının kontrol grubuna kıyasla **$E_{\text{Engine}} - E_{\text{Control}} \ge 0.50\sigma$** düzeyinde pozitif ayrışmasıdır.

---

### 1.3. Süre-Doğruluk Pareto Eğrisi (Speed-Accuracy Pareto Frontier)

Bilişsel görevlerde bireyler doğruluk ile çözüm süresi arasında bir takas (Speed-Accuracy Trade-off - SAT) yaparlar. Bu dinamik, Ratcliff'in Drift-Diffusion Modeli (DDM) çerçevesinde açıklanır:

Bir öğrencinin karar verme ve çözüm süreci, kanıt birikim hızına (drift rate $v$), karar eşiğine (boundary separation $a$) ve motor/algısal gecikmeye ($T_{er}$) bağlı bir stokastik diferansiyel süreçtir:

$$dx(t) = v \cdot dt + s \cdot dW(t)$$

Doğruluk $A(\theta)$ ve ortalama çözüm süresi $t(\theta)$, karar eşiği $a$ genişledikçe artar. Ancak öğretim motorunun amacı, öğrenciyi aynı doğruluk seviyesine daha kısa sürede ulaştırmak veya aynı sürede daha yüksek doğruluğa çıkarmaktır.

#### Pareto Dominansı ve Sınır Formülasyonu
Bir öğretim stratejisi $\theta_1$, diğer bir strateji $\theta_2$'ye göre aşağıdaki koşul sağlandığında **Pareto Dominant** kabul edilir:

$$\theta_1 \succ_{\text{Pareto}} \theta_2 \iff \left[ A(\theta_1) \ge A(\theta_2) \land t(\theta_1) \le t(\theta_2) \right] \land \left[ A(\theta_1) > A(\theta_2) \lor t(\theta_1) < t(\theta_2) \right]$$

Pareto Sınırı ($\mathcal{P}^*$), hiçbir alternatif tarafından domine edilemeyen en verimli öğretim durumlarının kümesidir:

$$\mathcal{P}^* = \left\{ \theta \in \Theta \;\middle|\; \nexists \theta' \in \Theta : \theta' \succ_{\text{Pareto}} \theta \right\}$$

```text
Doğruluk (%)
  100 ▲                ┌──────────────────────── Pareto Sınırı (Bizim Motorumuz)
      │               * (Yüksek Başarı, Kısa Süre)
   80 │             *   
      │           *       ┌ - - - - - - - - - - - Geleneksel EdTech Sınırı
   60 │         *        x (Yavaş İlerleme, Ezberci Doğruluk)
      │       *         
   40 │     *          o (Naive LLM: Hızlı ama Yüzeysel & Düşük Kalıcılık)
      │   *
    0 └──────────────────────────────────────────► Süre (Dakika)
          0           15          30          45
```

Bizim nöro-sembolik motorumuz, iskele sönümlemesi (faded scaffolding) ve anlık AST denetimi sayesinde öğrencinin hata arama çıkmazlarında (dead-end state search) kaybolmasını engelleyerek **Pareto Eğrisini dışa doğru (outward frontier shift)** öteler.

---

## 2. A/B TEST MİMARİSİ VE İSTATİSTİKSEL GÜÇ ANALİZİ (STATISTICAL POWER ANALYSIS)

Deneysel tasarımımızın rastgele dalgalanmalardan arındırılmış, tip I ve tip II hatalara karşı dayanıklı olmasını garanti etmek için standart Neyman-Pearson hipotez testi protokolü işletilir.

### 2.1. Örneklem Büyüklüğü ($N$) Analitik Hesabı

#### Hipotez Parametreleri:
* **Anlamlılık Düzeyi ($\alpha$):** 0.05 (İki yönlü tip I hata payı; $Z_{1 - \alpha/2} = 1.96$)
* **İstatistiksel Güç ($1 - \beta$):** 0.80 (Tip II hata payı $\beta = 0.20$; $Z_{1 - \beta} = 0.8416$)
* **Asgari Saptanabilir Etki Büyüklüğü (MDE - Minimum Detectable Effect):** Cohen's $d = 0.35$ (Orta-düşük etki büyüklüğü; eğitim müdahalelerinde pratik açıdan anlamlı eşik).

İki bağımsız grup arasındaki fark için temel örneklem büyüklüğü formülü:

$$n_{\text{raw}} = \frac{2 \cdot \left(Z_{1 - \alpha/2} + Z_{1 - \beta}\right)^2}{d^2}$$

Sayısal yerine koyma:

$$n_{\text{raw}} = \frac{2 \cdot (1.96 + 0.8416)^2}{0.35^2} = \frac{2 \cdot (2.8016)^2}{0.1225} = \frac{2 \cdot 7.8490}{0.1225} = \frac{15.6979}{0.1225} \approx 128.15$$

Grup başına tam sayı tavan değeri: **$n = 129$ öğrenci**.

---

### 2.2. Çoklu Grup (3 Kol), Çoklu Karşılaştırma ve Yıpranma Düzeltmesi

Deneyimiz 3 kollu (Kontrol, Naive AI, Bizim Motorumuz) bir tasarıma sahiptir:
1. **Çoklu Karşılaştırma Düzeltmesi:** Üç grup arasında ikili post-hoc karşılaştırmalar (Tukey HSD) yapılacağından, ANOVA omnibüs $F$-testi için Cohen's $f$ parametresi hesaplanır:
   $$f = \frac{d}{2} = \frac{0.35}{2} = 0.175$$
   $\alpha = 0.05$, $k = 3$ grup ve Power $= 0.80$ için ANOVA güç hesabında grup başına gereken asgari örneklem $n \approx 125$ öğrencidir.

2. **Boylamsal Yıpranma ve Terk (Attrition / Drop-out) Düzeltmesi:**
   14 ve 30 günlük çok aşamalı takip süreçlerinde, çevrimiçi eğitim platformlarında ortalama yıpranma oranı literatürde $\%30 - \%40$ bandındadır. Muhafazakar bir yaklaşımla terk oranı $R_{\text{attrition}} = 0.35$ (%35) olarak modellenir:

   $$n_{\text{adjusted}} = \frac{n_{\text{raw}}}{1 - R_{\text{attrition}}} = \frac{129}{1 - 0.35} = \frac{129}{0.65} \approx 198.46 \implies \mathbf{200 \text{ öğrenci / kol}}$$

3. **Toplam Örneklem Büyüklüğü:**
   $$N_{\text{total}} = 3 \times 200 = \mathbf{600 \text{ Katılımcı}}$$

---

### 2.3. ANCOVA Kovaryat Verimliliği

Ön-test skorları ($Pre$) son-test ($Post$) üzerinde güçlü bir açıklayıcı kovaryattır. Ön-test ile son-test arasındaki korelasyon $\rho \approx 0.60$ kabul edildiğinde, ANCOVA analizi hata varyansını $(1 - \rho^2)$ oranında azaltır:

$$\text{Varyans Azaltma Çarpanı} = 1 - 0.60^2 = 1 - 0.36 = 0.64$$

Bu durum, efektif istatistiksel gücümüzü nominal $1 - \beta = 0.80$'dan **$> 0.94$'e çıkararak** Cohen's $d = 0.28$ seviyesindeki daha küçük farkları dahi tespit edilebilir kılar.

---

### 2.4. Sıralı Analiz (Sequential Testing) ve Erken Durdurma Sınırları

A/B testinin gereksiz yere uzamasını veya belirgin bir pedagojik üstünlük/hasar durumunda etik ihlalleri önlemek için **Lan-DeMets alfa harcama fonksiyonu (O'Brien-Fleming sınırları)** kullanılır:

$$\alpha(t^*) = 2 - 2\Phi\left(\frac{Z_{1 - \alpha/2}}{\sqrt{t^*}}\right)$$

* $t^*$: Tamamlanan örneklem oranı ($t^* \in \{0.33, 0.66, 1.0\}$).
* Ara Analiz 1 ($N = 200$): $p < 0.0001$ ise deney erken durdurulur.
* Ara Analiz 2 ($N = 400$): $p < 0.0072$ ise deney erken durdurulur.
* Nihai Analiz ($N = 600$): $p < 0.0421$ anlamlılık eşiği kabul edilir (Nominal aile-bazı tip I hata $\alpha = 0.05$ korunur).

---

## 3. ENSTRÜMANTAL DEĞİŞKENLER (IV) VE KONTROL GRUPLARI İLE NEDENSEL ÇIKARIM

Eğitim deneylerinde en büyük metodolojik tehdit, öğrencilerin atandıkları gruptaki görevleri eksik yapmaları (non-compliance) veya zorlandıklarında sistemi terk etmeleridir (selective attrition). Sıradan En Küçük Kareler (OLS) regresyonu bu durumda içsellik (endogeneity) ve seçilim yanlılığı nedeniyle hatalı katsayılar üretir.

```text
                                [ RASTGELE ATAMA (Z_i) ]
                                   (Instrument / Araç)
                                      │             ╲
                         Birinci Aşama│              ╲ Dışlanma Kısıtı
                         (Relevance)  │               ╲ (Exclusion: Z -> Y SADECE
                                      ▼                ▼ D üzerinden akar!)
                         [ PEDAGOJİK DOZ (D_i) ] ───► [ KALICI KAZANIM (Y_i) ]
                            (Aktif Seans, Adım)      ▲      (R-LGpM / 14d)
                                                     │
                                             [ GÖZLENMEYEN ]
                                            (Yetenek, Motivasyon, U_i)
```

---

### 3.1. Üç Kollu Karşılaştırma Protokolü

Deney, kognitif içerik açısından bütünüyle izomorfik olan 3 paralel kolda yürütülür:

```text
+---------------------+-------------------------------+-------------------------------+-------------------------------+
| PARAMETRE           | GRUP A: GELENEKSEL EDTECH     | GRUP B: NAIVE AI (CHATGPT-4o) | GRUP C: NÖRO-SEMBOLİK MOTOR   |
+---------------------+-------------------------------+-------------------------------+-------------------------------+
| Öğretim Metodu      | Pasif Video (15 dk) +         | Serbest prompt arayüzü,       | Adaptif teşhis, sönümlenen    |
|                     | 10 Statik Soru + Çözüm Metni  | adım kısıtı yok, açık sohbet  | çözümlü örnekler (faded steps)|
| Hata Müdahalesi     | Statik Açıklama Okuma         | Doğrudan tam cevabı üretme    | Sembolik AST hata teşhisi,    |
|                     |                               | (LLM cevabı ifşa eder)        | yönlendirici Sokratik ipucu   |
| Aralıklı Tekrar     | Yok (Öğrenci inisiyatifi)     | Yok                           | FSRS Algoritmasıyla 14 gün    |
| Bilişsel Kısıt      | Sabit süre, aktif kontrol yok | Kognitif bypass riski yüksek  | Germane yük odaklı scaffolding|
+---------------------+-------------------------------+-------------------------------+-------------------------------+
```

---

### 3.2. İki Aşamalı En Küçük Kareler (2SLS / Instrumental Variables) Modeli

Öğrencinin platformda fiilen tamamladığı kognitif döngü sayısının ($D_i$) nihai başarı ($Y_i$) üzerindeki nedensel etkisini (Causal Effect) arındırmak için İki Aşamalı En Küçük Kareler (Two-Stage Least Squares - 2SLS) formüle edilir:

#### Aşama 1: Doz-Atama Regresyonu (First Stage)
$$D_i = \gamma_0 + \gamma_1 Z_i + \mathbf{X}_i' \boldsymbol{\gamma}_2 + \nu_i$$

* $Z_i \in \{0, 1, 2\}$: Rastgele atanan deney kolu (Enstrümantal Değişken - IV).
* $\mathbf{X}_i$: Ön-test skoru, yaş, genel akademik not ortalaması kovaryat vektörü.
* $D_i$: Öğrencinin tamamladığı interaktif problem çözme adımı sayısı veya aktif dakika.
* **Araç Geçerlilik Şartı (Instrument Relevance):** Birinci aşama $F$-istatistiği mutlaka 10'dan büyük olmalıdır ($F > 10$; Stock-Yogo zayıf araç eşiği).

#### Aşama 2: Nedensel Çıktı Regresyonu (Second Stage)
$$Y_i = \beta_0 + \beta_{\text{LATE}} \widehat{D}_i + \mathbf{X}_i' \boldsymbol{\beta}_2 + \varepsilon_i$$

* $\widehat{D}_i$: Birinci aşamadan elde edilen yansız, tahmin edilen pedagojik doz.
* $\beta_{\text{LATE}}$: Yerel Ortalama Tedavi Etkisi (Local Average Treatment Effect). Rastgele atamaya sadık kalan (complier) öğrenciler için motorun ürettiği net kognitif etki.

#### Dışlanma Kısıtı (Exclusion Restriction):
Rastgele grup atamasının ($Z_i$), öğrencinin 14. gün kalıcılık skoru ($Y_i$) üzerindeki yegane etkisi, öğrencinin deneyimlediği öğretim mimarisi ve tamamladığı etkileşim adımları ($D_i$) üzerinden gerçekleşir ($\text{Cov}(Z_i, \varepsilon_i) = 0$). Deney arayüzlerinin görsel estetiği, yazı tipi boyutu ve oturum süreleri standartlaştırılarak doğrudan yan etki kanalları kapatılır.

---

### 3.3. İzomorfik Test Maddesi Üretimi ve Çapraz Eşleme

Değerlendirme testlerinin (Ön-test, T=0 Anlık Son-Test, T=7d Gecikmeli Test, T=14d Kalıcılık Testi) birbirini tekrar etmemesi ve test aşinalığı (test-retest bias) yaratmaması için **Parametrik İzomorfik Madde Üreteci** kullanılır.

Örnek İzomorfizm Kuralı:
* Şablon: $ax^2 + bx + c = 0$ denkleminde $b^2 - 4ac > 0$ tam kare koşulu.
* Form A (Ön-test): $x^2 - 5x + 6 = 0 \implies (x-2)(x-3)=0$
* Form B (Anlık Test): $x^2 - 7x + 12 = 0 \implies (x-3)(x-4)=0$
* Form C (14. Gün Kalıcılık): $x^2 - 9x + 20 = 0 \implies (x-4)(x-5)=0$
* Form D (Uzak Transfer): $2y^4 - 10y^2 + 8 = 0$ (Değişken değiştirme ile 2. dereceye indirgeme).

Maddelerin psikometrik zorluk parametreleri ($\beta_j$) ve ayırt edicilikleri ($\alpha_j$), 2-Parametreli Lojistik Madde Tepki Kuramı (2PL-IRT) ile kalibre edilir:

$$P(Y_{ij} = 1 \mid \theta_i) = \frac{1}{1 + e^{-\alpha_j(\theta_i - \beta_j)}}$$

---

## 4. İSTATİSTİKSEL HİPOTEZLER, BAŞARI EŞİKLERİ VE HAKEMLİ YAYIN STANDARDI

### 4.1. Formal İstatistiksel Hipotezler

* **Birincil Hipotez (R-LGpM Üstünlüğü):**
  * $H_0: \mu_{\text{R-LGpM}}^{(C)} = \mu_{\text{R-LGpM}}^{(A)} = \mu_{\text{R-LGpM}}^{(B)}$
  * $H_1: \mu_{\text{R-LGpM}}^{(C)} > \max\left(\mu_{\text{R-LGpM}}^{(A)}, \mu_{\text{R-LGpM}}^{(B)}\right)$
* **İkincil Hipotez 1 (14 Günlük Kalıcılık Sağkalımı):**
  * $H_0: S_C(14) \le S_B(14)$
  * $H_1: S_C(14) > S_B(14)$ (Log-Rank Testi ile $p < 0.01$)
* **İkincil Hipotez 2 (Bilişsel Verimlilik):**
  * $H_0: E_C \le E_A$
  * $H_1: E_C > E_A + 0.50$ (Standart sapma cinsinden üstünlük)

---

### 4.2. Başarı Kriterleri Karar Matrisi

```text
+------------------------------------+--------------------------+-----------------------+------------------------+
| GÖSTERGE                           | KABUL EDİLEBİLİR SEVİYE  | HEDEF MÜKEMMELLİK     | BAŞARISIZLIK ALARMI    |
+------------------------------------+--------------------------+-----------------------+------------------------+
| R-LGpM Üstünlüğü                   | Grup C > Grup A (%25 fark)| Grup C > Grup A (%50+) | Grup C <= Grup A       |
| Cohen's d Etki Büyüklüğü           | d >= 0.45                | d >= 0.65 (Büyük Etki)| d < 0.30               |
| 14. Gün Kalıcılık Düşüş Oranı     | Kayıp < %25              | Kayıp < %12           | Kayıp >= %35           |
| Aktif Zaman Tasarrufu (Hedefe)     | %25 daha az süre         | %40+ daha az süre     | Grup C daha yavaş      |
| Bilişsel Verimlilik (Paas E)       | E_C > +0.30              | E_C > +0.60           | E_C <= 0               |
| Beklenen Kalibrasyon Hatası (ECE)  | ECE < 0.10               | ECE < 0.05            | ECE >= 0.15            |
+------------------------------------+--------------------------+-----------------------+------------------------+
```

### 4.3. Hakemli Yayın Raporlama Protokolü (CONSORT Uyumluluğu)
Tüm A/B test bulguları, eğitim bilimleri ve yapay zeka alanının en üst düzey hakemli yayın standartlarına (Computers & Education, Journal of Educational Psychology, AIED, EDM) uygun şekilde **CONSORT (Consolidated Standards of Reporting Trials)** yönergelerine göre raporlanacaktır:
1. Katılımcı akış şeması (Flow diagram: Kayıt, Tahsis, Takip, Analiz).
2. Kayıp veri analizi (Missing Data: Little's MCAR testi ve Full Information Maximum Likelihood - FIML).
3. Etki büyüklüğü güven aralıkları (%95 CI) ve bootstrapping (10.000 iterasyon).
