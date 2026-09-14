# 04-KNOWLEDGE-AND-PREREQUISITE-GRAPH.md
# BİLGİ VE ÖNKOŞUL GRAFI (KNOWLEDGE & PREREQUISITE GRAPH)
## Ontolojik Ağ Mimarisi, Graf Gezinme Algoritmaları ve Cebir MVP Grafı

---

## 1. SUBSYSTEM 10-SORU MATRİSİ

1. **Neden Var?** Bilgi parçalı veya rastgele bir liste değildir; hiyerarşik, birbirine bağımlı ve ontolojik bir ağdır. İleri düzey bir becerinin temeli zayıf bir önkoşul üzerine kurulamaz.
2. **Hangi Problemi Çözer?** "Bu konuyu anlamıyorum" diyen bir öğrencinin asıl sorununun o konuda değil, 2-3 adım gerideki bir önkoşulda (prerequisite) olduğunu tespit edememe körlüğünü çözer.
3. **Girdiler:** Hedef konu, öğrenici modelinin güncel yetkinlik vektörleri, graf kenar ağırlıkları.
4. **Tuttuğu Durum:** DAG (Directed Acyclic Graph) topolojisi, düğüm yetkinlik durumları, öğrencinin ZPD (Zone of Proximal Development) sınır kümesi.
5. **Aldığı Kararlar:** Hangi düğümün öğretileceği, bir takılma anında hangi önkoşula geri dönüleceği (backtracking), mikro-kum havuzunun ne zaman açılacağı.
6. **Çıktılar:** Kişiselleştirilmiş öğrenme rotası, önkoşul eksiklik haritası, ZPD aday düğüm listesi.
7. **Çalıştığını Nasıl Anlarız?** Bir önkoşul düzeltildiğinde, öğrencinin takıldığı ileri düzey konuyu desteksiz çözme olasılığının $\ge \%80$ artmasıyla.
8. **Nasıl Çöker?** Grafta döngü (cycle) oluşması, kenar bağımlılıklarının gerçek bilişsel yükü yansıtmaması, öğrencinin sürekli geriye fırlatılarak motivasyonunun kırılması (Prerequisite Hell).
9. **MVP Kapsamı:** İkinci Dereceden Denklemler için 30 düğümlü küratörlü, doğrulanmış statik DAG.
10. **Geleceğe Bırakılanlar:** Öğrenci etkileşim verilerinden kazaen keşfedilen dinamik graf kenarları (Data-driven prerequisite discovery).

---

## 2. GRAF VERİ MODELİ VE KENAR SEMANTİĞİ

Bilgi ağı yönlü ve döngüsüz bir graftır: $G = (V, E)$.
* $V$: Bilgi Bileşenleri (Knowledge Components - KC).
* $E \subseteq V \times V$: Bağımlılık ilişkileri.

### Kenar Türleri:
1. **Katı Önkoşul (Strict Prerequisite - $E_{\text{strict}}$):** $A \rightarrow B$. $A$ düğümünde yetkinlik sağlanmadan ($P(L_A) < 0.70$), $B$ düğümüne geçiş sistemsel olarak kilitlidir. (Örn: Çarpanlara ayırma bilinmeden İkinci Dereceden Denklemler çözülemez).
2. **Yumuşak / Destekleyici Önkoşul (Soft Prerequisite - $E_{\text{soft}}$):** $A \rightarrow B$. $A$ becerisi $B$'yi kolaylaştırır ama şart değildir. (Örn: Geometrik alan modeli, tam kareye tamamlamayı anlamayı hızlandırır).
3. **Transfer Komşuluğu (Transfer Edge - $E_{\text{transfer}}$):** $B \leftrightarrow C$. Aynı derin matematiksel yapıyı paylaşan farklı bağlamlar. (Örn: Parabol tepe noktası ile roket yörüngesinin tepe noktası).

```json
{
  "node_id": "math.alg.quadratics.zero_product_property",
  "name": "Zero Product Property (Sıfır Çarpım Özelliği)",
  "domain": "algebra",
  "strict_prerequisites": [
    "math.alg.linear.single_variable_solve",
    "math.arith.multiplication.properties_of_zero"
  ],
  "soft_prerequisites": [
    "math.alg.factoring.trinomials_monic"
  ],
  "cognitive_thresholds": {
    "min_recall": 0.85,
    "min_concept": 0.80,
    "min_procedure": 0.75
  },
  "misconception_traps": [
    "MISC_NON_ZERO_PRODUCT",
    "MISC_DIVIDE_BY_VARIABLE"
  ]
}
```

---

## 3. GRAF GEZİNME VE "REMEDIATION SANDBOXING" PROTOKOLÜ

Geleneksel eğitim yazılımlarının en ölümcül hatası şudur: Öğrenci lise cebirinde takıldığında sistemi durdurup onu ilkokul kesirler dersine sürgün ederler. Bu, yetişkin veya lise çağındaki öğrencinin motivasyonunu yok eder.

### Çözüm: Mikro-Kum Havuzu Protokolü (Remediation Sandboxing)

```text
[ HEDEF PROBLEM ÇÖZÜLÜYOR: 2x² + 5x - 3 = 0 ]
                     │
                     ▼
[ HATA TESPİTİ: Öğrenci (-3) ile 2'yi çarparken -6 yerine +6 yazdı ]
                     │
                     ▼
[ KÖK NEDEN ANALİZİ: Düğüm = math.arith.negative_numbers.multiplication ]
                     │
                     ▼
+─────────────────────────────────────────────────────────────+
|           MİKRO-KUM HAVUZU (REMEDIATION SANDBOX)            |
| - Ekranın sağ köşesinde 2 dakikalık mini panel açılır.      |
| - Ana problem arka planda dondurulur (kaybolmaz).           |
| - 1 adet görselleştirilmiş kural hatırlatması:              |
|   "Zıt işaretlerin çarpımı daima negatiftir: (+) · (-) = (-)|
| - 2 adet 10 saniyelik hızlı mikro-doğrulama testi.          |
+─────────────────────────────────────────────────────────────+
                     │
                     ▼
[ EKSİK KAPATILDI: Kum havuzu kapanır, ana denklemdeki o adıma dönülür ]
```

---

## 4. MVP MATEMATİK GRAFI (30 DÜĞÜMLÜ İKİNCİ DERECEDEN DENKLEMLER AĞI)

Aşağıdaki liste, sistemin MVP kapsamındaki 30 Bilgi Bileşenini (Knowledge Component - KC) ve hiyerarşik seviye mimarisini tanımlar:

```text
SEVİYE 0: TEMEL ARİTMETİK VE CEBİRSEL ÖNKOŞULLAR
├── [N01] Negatif Sayılarla İşlemler (Signed Arithmetic)
├── [N02] Dağılma Özelliği (Distributive Property)
├── [N03] Benzer Terimleri Birleştirme (Combining Like Terms)
└── [N04] Birinci Dereceden Lineer Denklem Çözme (Linear Solving)

SEVİYE 1: ÇARPANLARA AYIRMA VE ÖZDEŞLİKLER
├── [N05] Ortak Çarpan Parantezine Alma (GCF Factoring)
├── [N06] İki Kare Farkı Özdeşliği (Difference of Squares: a² - b²)
├── [N07] Tam Kare Özdeşliği (Perfect Square Trinomials: (a ± b)²)
├── [N08] Başkatsayısı 1 Olan Üçterimlileri Çarpanlara Ayırma (x² + bx + c)
└── [N09] Başkatsayısı 1'den Farklı Üçterimlileri Ayırma (ax² + bx + c, Gruplama Metodu)

SEVİYE 2: İKİNCİ DERECEDEN DENKLEM TEMELLERİ
├── [N10] İkinci Dereceden Denklem Standart Formu (ax² + bx + c = 0, a ≠ 0 Tanımı)
├── [N11] Sıfır Çarpım İlkesi (Zero Product Property: AB = 0 => A=0 veya B=0)
├── [N12] Çarpanlara Ayırma Yoluyla Denklem Çözme (Solving by Factoring)
└── [N13] Karekök Alma Yoluyla Çözüm (Pure Quadratics: ax² = c)

SEVİYE 3: TAM KAREYE TAMAMLAMA VE GEOMETRİK MODEL
├── [N14] Geometrik Alan Modeli ile Tam Kare İnşası (Geometric Completing the Square)
├── [N15] Cebirsel Tam Kareye Tamamlama (Algebraic Completing the Square: (b/2)²)
└── [N16] Tam Kare Metodu ile Kök Bulma (Solving by Completing the Square)

SEVİYE 4: KUADRATİK FORMÜL VE DİSKRİMİNANT
├── [N17] Kuadratik Formülün Çıkarılışı (Derivation of Quadratic Formula)
├── [N18] Kuadratik Formülün Standart Uygulanışı (Direct Application)
├── [N19] Diskriminant Tanımı ve Hesaplanışı (Δ = b² - 4ac)
├── [N20] Diskriminant ve Kök Sayısı/Türü İlişkisi (Δ > 0, Δ = 0, Δ < 0 / Reel ve Karmaşık Kökler)
└── [N21] Yöntem Seçim Stratejisi (Çarpanlara Ayırma mı, Formül mü, Tam Kare mi?)

SEVİYE 5: FONKSİYON, GRAFİK VE PARABOL İLİŞKİSİ
├── [N22] Parabol Tanımı ve Simetri Ekseni (x = -b / 2a)
├── [N23] Tepe Noktası (Vertex Form: y = a(x - h)² + k)
├── [N24] x-Eksenini Kesen Noktalar ve Köklerin Geometrik Anlamı
└── [N25] a Katsayısının Parabolün Yönüne ve Genişliğine Etkisi

SEVİYE 6: İLERİ SEVİYE VE TRANSFER UYGULAMALARI
├── [N26] Değişken Değiştirme ile İkinci Dereceye İndirgeme (u-substitution, Örn: x⁴ - 5x² + 4 = 0)
├── [N27] Ters Köşe ve Karşıt Örnek Analizi (a=0 tuzağı, değişkeni sadeleştirip kök kaybetme hatası)
├── [N28] Geometrik Alan Optimizasyonu Problemleri (Maksimum Dikdörtgen Alanı)
├── [N29] Fizik Yörünge Hareketi Modellemesi (h(t) = -gt² + v₀t + h₀)
└── [N30] İki Değişkenli Denklem Sistemlerinde Kesişim (Doğru ile Parabol Kesişimi)
```

### 4.1. 30 Düğümlü Topolojik Önkoşul ve Bağımlılık Matrisi
Graf üzerinde hiçbir düğüm izole veya sahipsiz bırakılmamıştır. Tüm kenarlar katı önkoşul ($E_{\text{strict}}$), destekleyici önkoşul ($E_{\text{soft}}$) ve transfer bağı ($E_{\text{transfer}}$) olarak kodlanmıştır:

| Düğüm No | Düğüm Kodu (Canonical ID) | Katı Önkoşul ($E_{\text{strict}}$) | Destekleyici ($E_{\text{soft}}$) | Transfer ($E_{\text{transfer}}$) | CAT Teşhis Probu ([05-DIAGNOSTIC-ENGINE.md](05-DIAGNOSTIC-ENGINE.md)) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **N01** | `math.arith.signed_ops` | - | - | - | Probe Yedek (b = -2.5) |
| **N02** | `math.alg.distributive` | N01 | - | - | CAT-ITEM-04 (b = -2.0) |
| **N03** | `math.alg.like_terms` | N01 | N02 | - | - |
| **N04** | `math.alg.linear_solve` | N02, N03 | N01 | - | Probe Önkoşul (b = -1.6) |
| **N05** | `math.alg.factoring.gcf` | N02 | N04 | - | Probe Seviye 1 |
| **N06** | `math.alg.factoring.diff_squares`| N01, N05 | N02 | - | CAT-ITEM-03 (b = -1.2) |
| **N07** | `math.alg.factoring.perfect_sq`| N02, N05 | N06 | N14 | - |
| **N08** | `math.alg.factoring.trinomial_monic` | N01, N03, N05 | N07 | - | CAT-ITEM-05 (b = -0.5) |
| **N09** | `math.alg.factoring.trinomial_nonmonic`| N08 | N05 | - | - |
| **N10** | `math.alg.quad.standard_form` | N03, N04 | N02 | N27 | - |
| **N11** | `math.alg.quad.zero_product` | N04 | N01 | N27 | Teşhis Temeli |
| **N12** | `math.alg.quad.solve_factoring` | N08, N11 | N06, N09 | - | **CAT-ITEM-01 (Kök Testi, b = 0.0)** |
| **N13** | `math.alg.quad.pure_quadratics` | N01, N04 | N06 | N16 | - |
| **N14** | `math.alg.quad.geom_complete_sq` | N02, N07 | - | N28 | - |
| **N15** | `math.alg.quad.alg_complete_sq` | N07, N14 | N08 | N23 | CAT-ITEM-06 (b = +0.8) |
| **N16** | `math.alg.quad.solve_complete_sq` | N13, N15 | N14 | - | - |
| **N17** | `math.alg.quad.formula_derivation` | N15, N16 | N10 | - | - |
| **N18** | `math.alg.quad.formula_application`| N01, N10 | N17 | - | CAT-ITEM-07 (b = +1.2) |
| **N19** | `math.alg.quad.discriminant_calc` | N01, N10 | N18 | - | - |
| **N20** | `math.alg.quad.discriminant_roots`| N19 | N20 | N24 | **CAT-ITEM-02 (b = +1.5)** |
| **N21** | `math.alg.quad.strategy_selection` | N12, N16, N18, N20| - | N27 | Seviye 4 Kapı Testi |
| **N22** | `math.func.parabola.vertex_axis` | N10, N20 | N04 | N23 | - |
| **N23** | `math.func.parabola.vertex_form` | N15, N22 | N14 | N28 | - |
| **N24** | `math.func.parabola.x_intercepts` | N12, N20, N22 | N18 | N30 | - |
| **N25** | `math.func.parabola.coefficient_a`| N10, N22 | N24 | N29 | - |
| **N26** | `math.alg.quad.u_substitution` | N12, N18 | N10 | - | - |
| **N27** | `math.alg.quad.counterexamples` | N11, N21 | N10 | - | - |
| **N28** | `math.app.quad.geom_optimization` | N23, N24 | N14 | N29 | Transfer Probu (b = +2.0) |
| **N29** | `math.app.quad.physics_trajectory` | N18, N23 | N24 | N28 | **CAT-ITEM-08 (Transfer, b = +2.2)** |
| **N30** | `math.app.quad.line_parabola_sys` | N04, N18, N24 | N22 | - | Seviye 6 Zirve Düğümü |

---

## 5. TEŞHİS MOTORU (2PL-IRT CAT) İLE GRAF ENTEGRASYONU VE SEEDING PROTOKOLÜ

[05-DIAGNOSTIC-ENGINE.md](05-DIAGNOSTIC-ENGINE.md) dokümanında işletilen Bilgisayarlı Uyarlamalı Test (CAT) motoru, graf üzerindeki düğüm durumlarını körlemesine tahmin etmez; DAG topolojisiyle doğrudan senkronize çalışır.

### 5.1. Teşhis Çıktısı $\hat{\theta}$ Değerinin Graf Giriş Seviyesine İzdüşümü
CAT motoru maksimum 5 soruda durduğunda elde edilen yetenek kestirimi $\hat{\theta} \in [-3.0, +3.0]$, öğrencinin grafa hangi seviyeden gireceğini belirler:

| CAT Yetenek Kestirimi ($\hat{\theta}$) | Giriş Seviyesi | Giriş Düğümü Adayı (ZPD Odak Düğümü) | Önkoşul Statüsü ($P(L_k)$ Seeding) |
| :--- | :--- | :--- | :--- |
| $\hat{\theta} < -1.5$ | **Seviye 0** | `[N01]` Negatif Sayılar & `[N02]` Dağılma | Tüm $k \in \text{DAG}$ için $P(L_k) = 0.10$ |
| $-1.5 \le \hat{\theta} < -0.5$ | **Seviye 1** | `[N08]` Üçterimlileri Çarpanlara Ayırma | $N01..N04 \implies P(L) = 0.85$; $N08 \implies P(L) = 0.50$ |
| $-0.5 \le \hat{\theta} < +0.5$ | **Seviye 2** | `[N11]` Sıfır Çarpım & `[N12]` Çözüm | $N01..N09 \implies P(L) = 0.85$; $N11,N12 \implies P(L) = 0.50$ |
| $+0.5 \le \hat{\theta} < +1.2$ | **Seviye 3** | `[N15]` Cebirsel Tam Kareye Tamamlama | $N01..N13 \implies P(L) = 0.85$; $N15 \implies P(L) = 0.50$ |
| $+1.2 \le \hat{\theta} < +1.8$ | **Seviye 4** | `[N18]` Kuadratik Formül & `[N20]` Diskriminant | $N01..N16 \implies P(L) = 0.85$; $N18,N20 \implies P(L) = 0.50$ |
| $\hat{\theta} \ge +1.8$ | **Seviye 5-6** | `[N22]` Parabol Grafiği veya `[N29]` Yörünge | $N01..N21 \implies P(L) = 0.85$; $N22+ \implies P(L) = 0.50$ |

### 5.2. Graf Durum Başlatma (Bayesian Seeding Kuralı)
1. **Atasal Düğümler (Strict Ancestors):** Giriş seviyesinin altındaki tüm doğrudan ve dolaylı katı önkoşul düğümlerine $P(L_k) = 0.85$ başlangıç olasılığı atanır (Geçici Ustalık Hipotezi).
2. **Hedef ZPD Düğümü (Entry Node):** Giriş düğümüne $P(L_k) = 0.50$ atanarak öğrencinin anlık yakınsak gelişim alanı olarak işaretlenir.
3. **Ardıl Düğümler (Descendants):** Giriş düğümünün üzerindeki tüm ileri düzey düğümler $P(L_k) = 0.10$ seviyesinde kilitli tutulur.
4. **Teşhis Sırasında Başarısız Olunan Düğümler (Flagged Probes):** Eğer CAT testi sırasında geriye izleme yapılarak bir önkoşul düğümünde hata saptandıysa (örn: `N06` veya `N02`), o düğümün $P(L)$ değeri derhal $0.25$'e çekilir ve sistem öğrenciyi ana hedefe sokmadan önce 2 dakikalık **Mikro-Kum Havuzu (Remediation Sandbox)** ile bu eksikliği onarır.
