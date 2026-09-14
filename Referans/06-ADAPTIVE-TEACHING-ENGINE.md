# 06-ADAPTIVE-TEACHING-ENGINE.md
# ADAPTİF ÖĞRETİM MOTORU (ADAPTIVE TEACHING ENGINE)
## Pedagojik Karar Ağacı, İskeleleme Politikaları ve Bilişsel Yük Yönetimi

---

## 1. SUBSYSTEM 10-SORU MATRİSİ

1. **Neden Var?** Tek tip (one-size-fits-all) öğretim yaklaşımının iflas etmesi; her öğrencinin o anki zihinsel durumuna, hata türüne ve bilişsel kapasitesine göre farklı bir pedagojik müdahaleye ihtiyaç duyması nedeniyle vardır.
2. **Hangi Problemi Çözer?** Acemiye çok zor problem verip kognitif kilitlenmeye sokma (cognitive overload) veya yetkin öğrenciye gereksiz örnek gösterip sıkma ve yavaşlatma (expertise reversal) problemini çözer.
3. **Girdiler:** Öğrenici modelindeki 5D yetkinlik vektörü, son adımın sembolik doğruluk durumu, hata kategorisi, çözüm latensi, Paas bilişsel verimlilik indeksi ($E$).
4. **Tuttuğu Durum:** Mevcut öğretim modu (Worked / Faded / Active / Interleaved / Concrete), aktif iskele derinliği, ZPD zorluk katsayısı.
5. **Aldığı Kararlar:** Hangi modun seçileceği, zorluğun ne zaman artırılacağı, somuttan soyuta ne zaman geçileceği, araya ne zaman farklı soru tipi sokulacağı.
6. **Çıktılar:** Bir sonraki görev tipi ve parametreleri, AI Tutor ajanına gönderilen pedagojik komut (Pedagogical Directive).
7. **Çalıştığını Nasıl Anlarız?** Öğrencinin problem çözme başarı oranının optimum ZPD aralığında (%65-%80) kalması ve bilişsel verimlilik indeksinin $E > +0.8$ bandına çıkmasıyla.
8. **Nasıl Çöker?** İskelelemeyi çok erken kaldırıp öğrenciyi hüsrana uğratmak veya iskeleyi çok geç kaldırıp bağımlılık yaratmakla.
9. **MVP Kapsamı:** FSM + Geriye Doğru Eksiltme (Backward Fading) + Somutluk Sönümlemesi + Entropi Minimizasyonu ile Soru Seçimi.
10. **Geleceğe Bırakılanlar:** Pekiştirmeli Öğrenme (Reinforcement Learning - RL) tabanlı dinamik pedagojik politika optimizasyonu.

---

## 2. PEDAGOJİK SONLU DURUM MAKİNESİ (INSTRUCTIONAL FSM)

Sistem öğrencinin anlık yetkinlik ($P(L)$) ve hata geçmişine göre durumlar arasında geçiş yapar:

```text
                                  +-----------------------+
                                  |     HEDEF DÜĞÜM       |
                                  +-----------------------+
                                              │
                       ┌──────────────────────┴──────────────────────┐
                       ▼                                             ▼
          [ DURUM 1: ACEMİ REJİMİ ]                     [ DURUM 2: YETKİN REJİMİ ]
               (P(L) < 0.50)                                 (P(L) ≥ 0.50)
                       │                                             │
                       ▼                                             ▼
          +─────────────────────────+                   +─────────────────────────+
          |  SOMUTLUK SÖNÜMLEMESİ   |                   |  PRODUCTIVE FAILURE     |
          |  (Concrete Tiles)       |                   |  GÖREVİ (Sezgisel Deneme|
          +─────────────────────────+                   +─────────────────────────+
                       │                                             │
                       ▼                                             ▼
          +─────────────────────────+                   +─────────────────────────+
          |  GERİYE DOĞRU EKSİLTME  |                   |  BAĞIMSIZ PROBLEM       |
          |  (Backward Fading)      |                   |  ÇÖZÜMÜ                 |
          +─────────────────────────+                   +─────────────────────────+
                       │                                             │
                       └──────────────────────┬──────────────────────┘
                                              │
                                              ▼
                                 [ DURUM 3: HATA / ZORLANMA ]
                                              │
                      ┌───────────────────────┼───────────────────────┐
                      ▼                       ▼                       ▼
            [ Level 1-2 İpucu ]      [ Köprüleme Stratejisi ] [ Mikro-Kum Havuzu ]
            (Metabilişsel / Strateji)(Sözel / Anlamlandırma)  (Önkoşul Tamiri)
                                              │
                                              ▼
                                 [ DURUM 4: USTALIK VE PEKİŞTİRME ]
                                              │
                      ┌───────────────────────┴──────────────────────┐
                      ▼                                               ▼
            [ ARAYA EKLEME ]                                [ UZAK TRANSFER ]
            (Interleaved Discrimination)                    (Yeni Bağlam / Modelleme)
```

---

## 3. SOMUTLUK SÖNÜMLEMESİ PROTOKOLÜ (CONCRETENESS FADING PROTOCOL)

1. **Aşama 1 (Eylemsel / Somut):** Öğrenci sanal cebir karolarıyla (Algebra Tiles) $x^2 + 6x$ alanını kurar.
2. **Aşama 2 (İkonik / Şematik):** Fiziksel karolar kaldırılır; kenar uzunlukları $x$ ve $3$ olan geometrik taslak çizdirilir.
3. **Aşama 3 (Saf Sembolik):** Şekil tamamen kaldırılır; $(x + 3)^2 = x^2 + 6x + 9$ cebirsel adımı desteksiz yazdırılır.

---

## 4. KOGNİTİF VERİMLİLİK İNDEKSİ ($E$) İLE ADAPTİF REGÜLASYON

Paas & Van Merriënboer (1993) formülüyle öğrencinin çalışma belleği yükü izlenir:

$$E = \frac{z_P - z_R}{\sqrt{2}}$$

* **Eğer $E < -1.0$ (Kognitif Boğulma):** Başarı düşük, harcanan efor/latens aşırı yüksek. Sistem mevcut karmaşık temsili derhal kapatır ve köprüleme stratejisiyle sözel modele döner.
* **Eğer $E > +1.0$ (Yüksek Verim / Otomatikleşme):** Başarı yüksek, harcanan efor minimum. İskele tamamen çekilir, araya farklı konular sokulur (Interleaving).

---

## 5. BİLGİ-TEORİK AKTİF GÖREV SEÇİMİ (MUTUAL INFORMATION MAXIMIZATION)

Sıradaki problem rastgele seçilmez; öğrenici modelinin Shannon Entropisini ($H(L)$) en hızlı düşüren problem seçilir:

$$j^* = \arg\max_{j \in \text{Havuz}} \sum_{k \in \text{DAG}} w_k \cdot IG(j; L_k) - \lambda \cdot \text{Cost}(j)$$

$$IG(j; L_k) = H(L_k) - \mathbb{E}_{y \in \{0, 1\}} \left[ H(L_k \mid Y_j = y) \right]$$

Bu sayede öğrenciye gereksiz tek bir soru dahi sorulmaz; her soru maksimum bilişsel ayırt edicilik sağlar.

---

## 6. ÜRETİCİ BAŞARISIZLIK MOTORU (PRODUCTIVE FAILURE ENGINE)

Sistem, yeni ve derin bir kavramsal yapıya (örn. Tam Kareye Tamamlama veya Kuadratik Formül) geçmeden önce öğrenciye doğrudan formül sunmaz (Direct Instruction reddi). Bunun yerine **Manu Kapur 2-Aşamalı Üretici Başarısızlık (PF)** protokolünü işletir.

```text
+─────────────────────────────────────────────────────────────────────────────+
|               ÜRETİCİ BAŞARISIZLIK (PF) YAŞAM DÖNGÜSÜ                       |
+─────────────────────────────────────────────────────────────────────────────+
| [ AŞAMA 1: KEŞİF VE ÜRETİM (Exploration & Generation Sandbox) ]              |
| - Biçimsel algoritma verilmez.                                              |
| - Hedef: Çoklu sezgisel çözüm temsili üretme (Divergent SGR).               |
| - Kural: Hatalar BKT/IRT'de cezalandırılmaz (Karantina Sandbox).            |
| - Çıktı: Öğrenci bilgi açığını (gap awareness) somut olarak deneyimler.     |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼ (Konsolidasyon Tetikleyicisi)
+─────────────────────────────────────────────────────────────────────────────+
| [ AŞAMA 2: KONSOLİDASYON VE KANONİK İNŞA (Consolidation & Assembly) ]       |
| - Öğrencinin ürettiği temsiller (SGR) masaya yatırılır.                     |
| - Karşılaştırmalı Örnekler (Contrasting Cases) ile sınır sınırları gösterilir|
| - Kanonik yöntem (Tam Kare / Formül), öğrencinin sezgisi üzerine kurulur.   |
+─────────────────────────────────────────────────────────────────────────────+
```

### 6.1. Kuadratik Denklemlerde PF Görevi: "Kareleme Çıkmazı"
* **Verilen Problem:** 
$$x^2 + 6x - 2 = 0$$
*(Not: Tam sayılarla çarpanlarına ayrılamaz: $\Delta = 36 - 4(1)(-2) = 44$, $\sqrt{44} \notin \mathbb{Z}$).*
* **Sistem Yönergesi:** 
  > *"Bu denklemi henüz öğrenmediğin bir yolla çözmen beklenmiyor. Senden ricamız, $x$'in değerini bulmak veya tahmin etmek için aklına gelen en az 2 farklı sezgisel yolu (tahmin, şekil çizme, cebirsel deneme) denemen. Yanılmaktan hiç çekinme!"*

### 6.2. Öğrenci Tarafından Üretilen Temsillerin (SGR) Otomatik Sınıflandırılması
SymPy AST ve örüntü tanıyıcı, öğrencinin serbest deneme tahtasındaki girdilerini 4 kategoriden birine eşler:

| Temsil Kategorisi | Öğrencinin Giriş Eylemi | Bilişsel Teşhis (Cognitive Diagnosis) | Konsolidasyon Hamlesi |
| :--- | :--- | :--- | :--- |
| **Kategori A: Kaba Kuvvet Aritmetik** | $x=0 \implies -2$, $x=1 \implies 5$, $x \approx 0.3$ | Sayısal sezgi var; analitik genelleme yok. | Aritmetik yaklaşımın hassasiyet sınırını göster; analitik ihtiyacı vurgula. |
| **Kategori B: Hatalı Sıfır-Çarpım Genellemesi** | $x(x+6) = 2 \implies x=2 \lor x+6=2$ | Buggy Rule: Sıfır-çarpım özelliğini 2'ye aktarma. | $2 \times 1 = 2$, $(-1) \times (-2) = 2$ sonsuz ihtimalini göstererek çürüt. |
| **Kategori C: Eksik Geometrik Kare** | $x^2$ karosu yanına iki adet $3x$ şeridi koyup duraklama | **Altın Sezgi:** Kare yapmaya çalıştı ama köşe boş kaldı ($3 \times 3 = 9$). | Bu çizimi ekrana getir: *"Harika bir yere geldin! O köşeyi tamamlamak için ne eksik?"* |
| **Kategori D: Parabolik Kök Sıkıştırma** | Grafiği çizip $x$-eksenini kestiği yeri işaretleme | Fonksiyonel/geometrik kavrayış yüksek. | Parabolün tepe noktasından simetri eksenine ($x=-3$) bağla. |

### 6.3. Konsolidasyon Aşaması ve Karşılaştırmalı Vakalar (Contrasting Cases)
AI Tutor, öğrencinin denemesini aldıktan sonra kanonik yöntemi doğrudan dikte etmez:
1. **Adım 1 (Yansıtma):** Öğrencinin denediği Kategori B'yi ekrana yansıtır: *"Önce $x(x+6)=2$ yolunu denedin. Bu çok yaratıcı bir hamleydi. Ama çarpımları 2 olan sadece 2 ve 1 mi vardır? Ya $4 \times 0.5$? Bu yüzden sağ taraf sıfır olmadan bu kural çalışmaz."*
2. **Adım 2 (Kavramsal Köprü):** Kategori C'yi devreye sokar: *"Peki bir kare yapmayı düşünsek? $x^2 + 6x$ ifadesini $x$ ve 3 kenarlı parçalara bölersek, tam bir kare olması için $3^2 = 9$ birim kareye ihtiyacımız var!"*
3. **Adım 3 (Kanonik İnşa):**
$$x^2 + 6x + 9 = 2 + 9 \implies (x + 3)^2 = 11 \implies x + 3 = \pm\sqrt{11} \implies x = -3 \pm\sqrt{11}$$
Bu sayede öğrenci formülü ezberlemez; **kendi hissettiği geometrik boşluğun matematiksel çözümü** olarak kavrar.

### 6.4. Sinha & Kapur (2021) Meta-Analitik Koşulları ve Dozaj Optimizasyonu
53 bağımsız çalışmayı inceleyen kapsamlı meta-analiz bulgularına göre Üretici Başarısızlık her durumda sihirli bir değnek değildir; başarısı katı pedagojik sınırlara bağlıdır:
1. **Kavramsal Anlama vs Prosedürel Hız:** PF, derin kavramsal anlamada ($g = 0.36$) ve uzak transferde ($g = 0.28$) Doğrudan Öğretimden (DI) üstündür; ancak konsolidasyon adımı zayıf tutulursa saf prosedürel yürütme hızında geriye düşebilir ($g = -0.05$). Bu nedenle konsolidasyon aşamasında kanonik adımların prosedürel akıcılığı mutlaka mühürlenmelidir.
2. **Optimum Dozaj Aralığı ($T_{\text{dosage}}$):**
   * $T_{\text{exp}} < 8$ dakika: Yetersiz aktivasyon. Öğrenci problemin çetinliğini ve zihinsel açığını kavrayamaz.
   * $8 \le T_{\text{exp}} \le 18$ dakika: **Optimum Bilişsel Pencere.** Öğrenci en az 2 farklı temsil dener, sınırları hisseder, konsolidasyona en açık hale gelir.
   * $T_{\text{exp}} > 25$ dakika: Kognitif tükenmişlik ve motivasyon erozyonu.
3. **Dolaylı Başarısızlık (Vicarious Failure):** Çalışma belleği aşırı düşük ($WM < \mu - 1.5\sigma$) olan acemi öğrencilerde kendi başına sıfırdan üretim yapmak boğulmaya yol açarsa, sistem **"Başka bir öğrencinin başarısız denemesini analiz etme"** (Vicarious Failure Analysis) moduna geçerek bilişsel yükü hafifletir.

---

## 7. DİNAMİK İSKELELEME VE SÖNÜMLEME MİMARİSİ (DYNAMIC SCAFFOLDING & FADING)

İskeleleme statik bir ipucu butonu değil, Van de Pol et al. (2010) ilkelerine göre dinamik olarak açılıp kapanan bir regülatördür.

### 7.1. 4-Seviyeli İskele Hiyerarşisi
```text
[ SEVİYE 4: KAVRAMSAL İSKELE (Conceptual Scaffold) ]
-> Geometrik karo modeli, parabol görseli veya sözel analoji sunar.
                               ▲
                               │ (Yetkinlik Arttıkça Sönümlenir)
                               ▼
[ SEVİYE 3: METABİLİŞSEL İSKELE (Metacognitive Scaffold) ]
-> "Şu an hangi aşamadasın?", "Bu adım sana denklemi tam kareye yaklaştırdı mı?" yönlendirmesi.
                               ▲
                               │
                               ▼
[ SEVİYE 2: STRATEJİK İSKELE (Strategic Scaffold) ]
-> "Burada her iki tarafa katsayının yarısının karesini eklemek sence işe yarar mı?"
                               ▲
                               │
                               ▼
[ SEVİYE 1: PROSEDÜREL İSKELE (Procedural Step Scaffold) ]
-> Adım adım girdi kutuları açma: "[   ]² = 11".
                               ▲
                               │
                               ▼
[ SEVİYE 0: SIFIR İSKELE (Independent Mastery) ]
-> Boş konsol; tüm çözüm öğrenciye ait.
```

### 7.2. "ZPD Termostatı" Algoritması (Gerçek Zamanlı İskele Regülasyonu)
Sistem her adımda iskele seviyesini ($S \in \{0, 1, 2, 3, 4\}$) dinamik olarak günceller:

```python
def update_scaffold_level(current_S: int, consecutive_success: int, consecutive_errors: int, cognitive_efficiency_E: float) -> int:
    """
    ZPD Termostatı: Öğrencinin bilişsel yüküne ve başarı zincirine göre iskeleyi ayarlar.
    """
    # İskele Sönümleme (Fading): Öğrenci rahat ve başarılıysa iskeleyi çek
    if consecutive_success >= 2 and cognitive_efficiency_E > 0.5:
        return max(0, current_S - 1)
        
    # İskele Artırma (Scaffolding): Öğrenci bocalıyorsa veya aşırı kognitif yük altındaysa
    if consecutive_errors >= 2 or cognitive_efficiency_E < -1.0:
        return min(4, current_S + 1)
        
    return current_S
```

### 7.3. Sürekli Zamanlı İskeleleme ve Sönümleme Dinamiği (Continuous Scaffolding Equation)
Ayrık seviyelerin arkasında, öğrencinin destek ihtiyacını $S_t \in [0, 1]$ sürekli aralığında modelleyen diferansiyel sönümleme denklemi çalışır:

$$S_{t+1} = S_t \cdot \exp\left(-\alpha \cdot \max(0, P(L_t) - P_{\text{target}}) \cdot \max(0, E_t)\right) + \beta \cdot \mathbb{I}(e_t \in \mathcal{E}_{\text{kavramsal}})$$

* $P(L_t)$: iBKT anlık kavrama olasılığı.
* $E_t$: Paas bilişsel verimlilik skoru ($E = \frac{z_P - z_R}{\sqrt{2}}$).
* $\alpha$: Sönümleme hızı katsayısı ($\alpha > 0$).
* $\beta$: Kavramsal bir yanılgı (misconception) saptandığında iskeleyi anında tekrar devreye sokan **Zıplama Katsayısı (Scaffold Re-inflation)**.
* Bu formül sayesinde öğrenci yetkinleştikçe ($P(L_t) > P_{\text{target}}$) ve rahatladıkça ($E_t > 0$) iskele pürüzsüzce buharlaşır; ancak derin bir yanılgı baş gösterdiği anda sistem derhal koruyucu iskeleyi yeniden örer.

### 7.4. Wood, Bruner & Ross (1976) 6 İskeleleme Fonksiyonunun Algoritmik Karşılığı
1. **İşe Dahil Etme (Recruitment):** Görevi kuru sembolik denklem yerine otantik bir kriz ("Al-Harezmi'nin Tarla Bölme Krizi") olarak sunma.
2. **Serbestlik Derecesini Azaltma (Reduction in Degrees of Freedom):** Karmaşık katsayıları sabitleme ($a=1$ tutarak sadece $b$ ve $c$ ile odak sağlama).
3. **Yönü Korumak (Direction Maintenance):** Alt-hedef etiketleme (Sub-goal Labelling: *"Şu an sadece sol tarafı tam kare yapmaya odaklanıyoruz"*).
4. **Kritik Özellikleri İşaretleme (Marking Critical Features):** Geometrik karolarda eksik kalan köşeyi yanıp sönen bir renkle vurgulama ($3 \times 3 = 9$ açığı).
5. **Hüsran Kontrolü (Frustration Control):** Duygudurumsal şalter (Affective Circuit Breaker) ile öğrenilmiş çaresizliği engelleme.
6. **Modelleme / Gösterme (Demonstration):** Çözümlü örnekler üzerinden ideal düşünme adımlarını sesli düşündürme (Thinking Aloud).

### 7.5. Bilişsel Çıraklık Süreci (Collins, Brown & Newman, 1989)
Sistem öğrenciyi şu aşamalar boyunca taşır:
$$\text{Modelleme (Tutor Çözer)} \longrightarrow \text{Koçluk (Tutor Gözler \& Yönlendirir)} \longrightarrow \text{İskeleleme (Adım Adım Eksiltme)} \longrightarrow \text{İfade Etme (Öğrenci Açıklar)} \longrightarrow \text{Yansıtma (Temsil Kıyaslama)} \longrightarrow \text{Serbest Keşif}$$

---

## 8. YIKICI BAŞARISIZLIĞA KARŞI KORUMA: DUYGUDURUMSAL ŞALTER (AFFECTIVE CIRCUIT BREAKER)

Üretici başarısızlık kontrollü bir zorlanmadır (desirable difficulty); ancak sınır aşıldığında **öğrenilmiş çaresizlik ve afektif çöküşe (affective shutdown)** neden olur (D'Mello & Graesser, 2012).

### 8.1. Hüsran Eşiği ve Çok-Modlu Dedektör
Sistem arka planda aşağıdaki 4 metriği sürekli izler:
1. **Latens Donması (Latency Freezing):** $RT > 3.0 \times \mu_{\text{baseline}}$ (Öğrenci ekranda hiçbir işlem yapmadan dondu).
2. **Öfke Tıklaması ve Çırpınma (Thrashing / Rage Clicks):** 5 saniye içinde $>4$ anlamsız tıklama, silme veya rastgele karakter girişi.
3. **Yardım İstismarı (Help-Seeking Despair):** Çözüm üretmeden ardı ardına 3 kez yardım butonuna basılması.
4. **Duygudurumsal İpuçları (Affective NLP Triggers):** Chat veya serbest metin alanına girilen *"anlamıyorum"*, *"yapamıyorum"*, *"saçmalık"*, *"bırakıyorum"* gibi çaresizlik belirteçleri.

### 8.2. Koruyucu Şalter Protokolü (Circuit Breaker Interventions)
Dedektör hüsran indeksini $F_{\text{score}} \ge 0.85$ olarak hesapladığı anda sistem **Şalteri İndirir**:

```text
[ TETİKLEYİCİ: F_score >= 0.85 (Yıkıcı Hüsran Riski) ]
                       │
                       ▼
    +─────────────────────────────────────────────────────────+
    |           1. GÖREVİ DERHAL DURDUR VE NEFES ALDIR       |
    | "Dur bir saniye! Bu soru gerçekten çok çetin bir soru.  |
    |  Tarihte matematikçiler de bu noktada tam 400 yıl      |
    |  çözümsüz kalmıştı. Yalnız değilsin!"                  |
    +─────────────────────────────────────────────────────────+
                       │
                       ▼
    +─────────────────────────────────────────────────────────+
    |           2. DÜŞÜK YÜKLÜ ÇÖZÜMLÜ ÖRNEĞE PİVOT ET        |
    | Görev tipini anında 'Worked Example with Self-          |
    | Explanation' moduna düşür. Öğrenciye hesaplama          |
    | yaptırma; sadece önceden çözülmüş bir adımın mantığını  |
    | onaylat ("Burada neden her iki tarafa 9 ekledik?").    |
    +─────────────────────────────────────────────────────────+
                       │
                       ▼
    +─────────────────────────────────────────────────────────+
    |           3. ÖĞRENME MODELİNDEN CEZA MUAFİYETİ          |
    | Bu oturumdaki zorlanma BKT P(L) veya CAT yetenek θ     |
    | puanını düşürmez (Affective Safety Quarantine).         |
    +─────────────────────────────────────────────────────────+
```

### 8.3. Saklı Markov Modeli ile Duygudurum Çözümleme (Affective State HMM)
Öğrencinin gizil afektif durumu $S_t \in \{\text{Flow}, \text{Confusion}, \text{Frustration}, \text{Boredom}, \text{Delight}\}$ 5-durumlu bir Markov zinciri ile modellenir (D'Mello & Graesser, 2012):

$$\mathbf{A} = \begin{pmatrix} 
P(\text{Flow} \to \text{Flow}) & P(\text{Flow} \to \text{Confusion}) & \dots \\
P(\text{Confusion} \to \text{Delight}) & P(\text{Confusion} \to \text{Frustration}) & \dots \\
\vdots & \vdots & \ddots
\end{pmatrix}$$

Gözlemlenen davranış vektörü $\mathbf{o}_t = [z_{RT}, v_{\text{thrash}}, r_{\text{hint}}, sentiment]$ kullanılarak Viterbi algoritması ile öğrencinin anlık duygusal durumu saniyelik olarak deşifre edilir. $P(\text{Frustration} \mid \mathbf{o}_{1:t}) > 0.85$ olduğunda kognitif güvenlik sübabı tavizsiz devreye girer.

Bu sayede öğrencinin öz-yeterlik inancı (self-efficacy) korunur ve kognitif tükenmişlik (burnout) engellenir.
