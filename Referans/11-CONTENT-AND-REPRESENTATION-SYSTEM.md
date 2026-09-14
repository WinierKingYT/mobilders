# 11-CONTENT-AND-REPRESENTATION-SYSTEM.md
# İÇERİK VE ÇOKLU TEMSİL SİSTEMİ (CONTENT & REPRESENTATION SYSTEM)
## 4 Çeyrek Temsil Matrisi, Al-Harezmi Geometrik Karo Modeli, Dinamik Parabolik Morflama ve Bağlantılı Çift Görünüm Protokolü

---

## 1. SUBSYSTEM 10-SORU MATRİSİ

1. **Neden Var?** Matematiksel kavramlar tek bir gösterim biçimine (özellikle yalnızca sembolik formüllere) hapsedildiğinde mekanik ve ezbere dayalı kalır. Kavramsal derinlik ve transfer yeteneği, farklı temsil modaliteleri arasında akıcı geçiş yapabilme yetisine (Bruner ve Lesh çoklu temsil teorisi) dayanır.
2. **Hangi Problemi Çözer?** "Formülü biliyorum ama soruda uygulayamıyorum" veya "$(x+3)^2 = x^2 + 9$" (Freshman's Dream) gibi yaygın kavram yanılgılarını; öğrencinin denklemi hem uzamsal alan, hem fonksiyon eğrisi, hem de gerçek hayat problemi olarak eşzamanlı canlandırmasını sağlayarak çözer.
3. **Girdiler:** Mevcut cebirsel denklem/ifade, öğrencinin aktif etkileşim modu, manipüle edilen parametreler ($a, b, c$ veya $h, k$), tuval üzerindeki sürükle-bırak hareketleri, sembolik editör adım girdileri.
4. **Tuttuğu Durum:** 4 çeyrek temsil durum vektörü $[T_S, T_G, T_P, T_V]$, karo yerleşim koordinat ızgarası, parabol tepe noktası ve kök sapması ($\delta$), çift yönlü senkronizasyon olay veri yolu (event bus) durumu.
5. **Aldığı Kararlar:** Hangi kavram yanılgısında hangi görsel temsilin (mikro-kum havuzu) otomatik tetikleneceği, sembolik adımlarla geometrik animasyonların nasıl eşzamanlanacağı, bölünmüş dikkat etkisinin nasıl sıfırlanacağı.
6. **Çıktılar:** Reaktif SVG/Canvas geometri bileşenleri, 60 FPS dinamik parabol eğrisi ve simetri ekseni göstergeleri, eşzamanlı renk kodlu LaTeX sembolik adımları.
7. **Çalıştığını Nasıl Anlarız?** Sembolik olarak takılan bir öğrencinin geometrik alan karosu veya parabol tepe noktası kaydırma animasyonunu gördükten sonra doğru adımı desteksiz atabilme oranının $\ge \%85$ olmasıyla.
8. **Nasıl Çöker?** Sembolik terimler ile görsel nesneler arasındaki renk ve animasyon eşleşmesi gecikirse ($> 50 \text{ ms}$), ekran aşırı karmaşıklaşarak öğrencinin dışsal bilişsel yükünü (extraneous cognitive load) patlatırsa.
9. **MVP Kapsamı:** İkinci Dereceden Denklemler için 4 Çeyrek Matrisi + Al-Harezmi Karo Sistemi (SVG) + Dinamik Parabol Simetri Ekseni Kontratı + Linked Dual-View Protokolü.
10. **Geleceğe Bırakılanlar:** Öğrencinin el çizimlerini gerçek zamanlı olarak cebirsel karolara ve eğrilere dönüştüren nöral el yazısı ayrıştırıcısı.

---

## 2. 4 ÇEYREK TEMSİL MATRİSİ (THE 4-QUADRANT REPRESENTATION MATRIX)

Matematiksel bir kuadratik ilişki Lesh Çoklu Temsil Modeli (Lesh Translation Model) doğrultusunda 4 ayrık kadranda eşzamanlı var olur:

```text
+─────────────────────────────────────────+─────────────────────────────────────────+
|      [ T_S: SAF SEMBOLİK / CEBİRSEL ]   |      [ T_G: GEOMETRİK ALAN MODELİ ]     |
|   ax² + bx + c = 0                      |   Al-Harezmi Kare ve Şerit Karoları     |
|   Δ = b² - 4ac                          |   Alan = (x + b/2a)²                    |
|   x = (-b ± √Δ) / 2a                    |   Eksik Köşe = (b/2a)²                  |
|   Özellik: Kompakt, algoritmik, soyut   |   Özellik: Uzamsal çapa, somut sezgi    |
+─────────────────────────────────────────+─────────────────────────────────────────+
|      [ T_P: DİNAMİK PARABOLİK GRAFİK ]  |      [ T_V: SÖZEL VE GERÇEK DÜNYA ]     |
|   f(x) = a(x - h)² + k                  |   "Bir roketin fırlatılış yörüngesi..." |
|   Simetri Ekseni: x = h = -b/2a         |   "Gelir = Fiyat × Talep denklemi..."   |
|   Kök Mesafesi: δ = √(-k/a)             |   Özellik: Anlamsal bağlam, fiziksel    |
|   Özellik: Fonksiyonel, sürekli, dinamik|            kısıtlar (zaman > 0, alan > 0)|
+─────────────────────────────────────────+─────────────────────────────────────────+
```

### 2.1. $4 \times 4$ Temsil Geçiş Matrisi ($\mathbf{T}_{\text{quadrant}}$)

Yetkin bir matematiksel zihin, bu 4 temsil arasında sıfır sürtünmeyle çift yönlü geçiş yapabilendir. Sistem, öğrencinin temsil geçişlerini aşağıdaki $4 \times 4$ dönüşüm matrisiyle yönlendirir:

| Başlangıç $\downarrow$ \ Hedef $\to$ | **$T_S$ (Sembolik)** | **$T_G$ (Geometri)** | **$T_P$ (Parabol)** | **$T_V$ (Sözel)** |
| :--- | :--- | :--- | :--- | :--- |
| **$T_S$ (Sembolik)** | *Öz-İndirgeme:* Cebirsel sadeleştirme, ortak paranteze alma. | *Spatialization (Uzamsallaştırma):* Terimleri karo boyutlarına ($x^2, x, 1$) eşleme. Sürtünme: $\mu = 0.25$. | *Fonksiyonelleştirme:* $y = f(x)$ bağıntısına dönüştürüp kökleri $x$-keseni görme. Sürtünme: $\mu = 0.30$. | *Anlamlandırma:* Cebirsel denklemden gerçek dünya senaryosu kurgulama. Sürtünme: $\mu = 0.60$. |
| **$T_G$ (Geometri)** | *Formalization (Formülleştirme):* Karo alan toplamını cebirsel polinom olarak yazma. Sürtünme: $\mu = 0.20$. | *Öz-Tamamlama:* Karoları yeniden düzenleyerek tam kare oluşturma. | *Geometrik-Analitik Köprü:* Alan büyüklüğünü tepe noktası yüksekliğine eşleme. Sürtünme: $\mu = 0.50$. | *Fiziksel Alan:* Arsa, çerçeve, oda genişletme problemlerine bağlama. Sürtünme: $\mu = 0.35$. |
| **$T_P$ (Parabol)** | *Kök Okuma / Çözüm:* Tepe noktası $h$ ve kök sapması $\delta$ ile kökleri $h \pm \delta$ yazma. Sürtünme: $\mu = 0.30$. | *Tepe Noktası - Tam Kare Eşlemesi:* Grafiğin $k$ değerini geometrik eksik köşeye eşleme. Sürtünme: $\mu = 0.55$. | *Parametrik Morflama:* $a, h, k$ sliderları ile eğriyi dinamik bükme. | *Yörünge Yorumlama:* Maksimum yükseklik, tepe noktası zamanı, menzil bulma. Sürtünme: $\mu = 0.25$. |
| **$T_V$ (Sözel)** | *Matematiksel Modelleme:* Problem cümlesinden değişken tanımlayıp denklem kurma. Sürtünme: $\mu = 0.70$. | *Şematik Çizim:* Metindeki boyutları geometrik dikdörtgen/kareye dökme. Sürtünme: $\mu = 0.40$. | *Hareket Grafiği Çizimi:* Zaman-yükseklik eksenlerini tanımlayıp parabol eskizi çıkarma. Sürtünme: $\mu = 0.45$. | *Yeniden İfade Etme:* Problemi farklı kelimelerle özetleme. |

---

## 3. AL-HAREZMİ GEOMETRİK KARO SİSTEMİ (ALGEBRA TILES ARCHITECTURE)

Al-Harezmi'nin MS 820 yılında *"El-Kitabü'l-Muhtasar fi Hisabi'l-Cebri ve'l-Mukabele"* eserinde geliştirdiği geometrik tam kare tamamlama yöntemi, sistemin somut bilişsel çapasını oluşturur.

```text
               x                     b/2
        ┌──────────────────────┬───────────────┐
        │                      │               │
        │                      │               │
     x  │         x²           │    (b/2)x     │
        │      (Ana Kare)      │  (Sağ Kanat)  │
        │                      │               │
        ├──────────────────────┼ - - - - - - - ┤
        │                      │  EKSİK KÖŞE   │
    b/2 │        (b/2)x        │   (b/2)²      │
        │     (Alt Kanat)      │  (Doldurulan) │
        └──────────────────────┴ - - - - - - - ┘
```

### 3.1. 3 Temel Karo Türü ve Boyut Tokenları

SVG ve HTML5 Canvas üzerinde piksel bağımsız ölçekleme için normalize edilmiş baz birim $u = 40\text{ px}$ ve dinamik değişken boyutu $X = 120\text{ px}$ olarak tanımlanır:

| Karo Türü | Sembolik Alan | Boyutlar $(w \times h)$ | Pozitif Renk / Token | Negatif Renk / Tarama |
| :--- | :---: | :---: | :--- | :--- |
| **Büyük Kare** | $x^2$ | $X \times X$ ($120 \times 120\text{ px}$) | Azure Blue (`#2563EB`) | Crimson Red (`#DC2626`) + $45^\circ$ Çapraz Tarama |
| **Dikdörtgen Şerit (Dikey)** | $x$ | $u \times X$ ($40 \times 120\text{ px}$) | Emerald Green (`#059669`) | Coral Red (`#EF4444`) + Kesikli Kenar |
| **Dikdörtgen Şerit (Yatay)** | $x$ | $X \times u$ ($120 \times 40\text{ px}$) | Emerald Green (`#059669`) | Coral Red (`#EF4444`) + Kesikli Kenar |
| **Küçük Birim Kare** | $1$ | $u \times u$ ($40 \times 40\text{ px}$) | Amber Gold (`#D97706`) | Wine Dark Red (`#991B1B`) + Noktalı Dolgu |

### 3.2. Polarite ve Sıfır Çifti (Zero Pair) İptal Mekanizması
* Bir pozitif karo ($+x$ veya $+1$) ile bir negatif karo ($-x$ veya $-1$) tuval üzerinde temas ettirildiğinde veya üst üste sürüklendiğinde, sistem anında bir **Sıfır Çifti (Zero Pair)** algılar.
* Karolar 300 ms içinde şeffaflaşarak (opacity: $1 \to 0$, transform: `scale(0.8)`) sahneden silinir.
* Bu mekanizma, $(x^2 - 4x = 5)$ gibi denklemlerde negatif şeritlerin nasıl konumlanacağını ve sıfırlanacağını somutlaştırır.

### 3.3. Tam Kareye Tamamlama ($x^2 + bx = c$) Yerleşim Şeması

$x^2 + 6x = 16$ denkleminin tam kareye tamamlama adımları:
1. **$x^2$ Konumlandırma:** Sol-alt orijine $(0, 0)$ yerleştirilir. Alan: $x^2$.
2. **Lineer Terimin ($bx$) Simetrik Bölünmesi:** 
   * $b = 6 \implies \frac{b}{2} = 3$.
   * 3 adet dikey $x$-şeridi ana karenin sağına yerleştirilir: Koordinat $(X, 0)$, toplam boyut $3u \times X$.
   * 3 adet yatay $x$-şeridi ana karenin üstüne yerleştirilir: Koordinat $(0, X)$, toplam boyut $X \times 3u$.
3. **Eksik Köşenin (The Missing Corner) Belirlenmesi:**
   * Koordinat: $(X, X)$.
   * Boyut: $3u \times 3u$.
   * Alan: $\left(\frac{b}{2}\right) \times \left(\frac{b}{2}\right) = 3 \times 3 = 9$ birim kare.
   * Bu köşe henüz boştur; kesikli sarı çizgiyle (`stroke: #F59E0B; stroke-dasharray: 6,4;`) yanıp söner (pulsing animation).
4. **Tamamlanma:** Köşeye 9 adet $1 \times 1$ sarı birim kare yerleştirildiğinde büyük birleşik kare oluşur:
   $$\text{Toplam Alan} = \left( x + 3 \right)^2 = x^2 + 6x + 9$$
   Eşitliğin korunması için sağ taraftaki $16$'ya da $+9$ eklenir: $(x + 3)^2 = 25 \implies x + 3 = \pm 5$.

### 3.4. SVG / Canvas Render Modeli ve JSON Veri Kontratı

```json
{
  "canvas_viewbox": "0 0 600 600",
  "unit_size_px": 40,
  "variable_x_px": 120,
  "tiles": [
    {
      "id": "tile_main_x2",
      "type": "X_SQUARE",
      "sign": "POSITIVE",
      "bounds": { "x": 50, "y": 250, "width": 120, "height": 120 },
      "fill": "#2563EB",
      "label": "x²"
    },
    {
      "id": "tile_right_strips",
      "type": "X_RECT_VERTICAL",
      "count": 3,
      "sign": "POSITIVE",
      "bounds": { "x": 170, "y": 250, "width": 120, "height": 120 },
      "fill": "#059669",
      "label": "3x"
    },
    {
      "id": "tile_top_strips",
      "type": "X_RECT_HORIZONTAL",
      "count": 3,
      "sign": "POSITIVE",
      "bounds": { "x": 50, "y": 130, "width": 120, "height": 120 },
      "fill": "#059669",
      "label": "3x"
    },
    {
      "id": "tile_missing_corner",
      "type": "UNIT_SQUARE_GRID",
      "status": "AWAITING_DROP",
      "required_units": 9,
      "bounds": { "x": 170, "y": 130, "width": 120, "height": 120 },
      "stroke": "#F59E0B",
      "stroke_dash": "6,4",
      "label": "Eksik: 3² = 9"
    }
  ]
}
```

---

## 4. DİNAMİK PARABOL MORFLAMA VE SİMETRİ EKSENİ (DYNAMIC PARABOLA MORPHING)

Standart formdaki $y = ax^2 + bx + c$ parabolü, tepe noktası (vertex) formuna dönüştürüldüğünde:

$$f(x) = a(x - h)^2 + k$$

Burada:
$$h = -\frac{b}{2a} \quad (\text{Simetri Ekseni}), \quad k = f(h) = -\frac{\Delta}{4a} = c - \frac{b^2}{4a} \quad (\text{Tepe Değeri})$$

```text
                  y
                  │           x = h (Simetri Ekseni)
                  │             │
                  │             │     *
                  │            *│*   /
                  │           / │ \ /
     ─────────────┼──────────[x₁]───[x₂]───────────► x
                  │         ◄───┼───►
                  │           δ │ δ
                  │             │
                  │           \ │ /
                  │            *│*
                  │             ▼ T(h, k)  (Tepe Noktası)
                  │
```

### 4.1. Köklerin Simetri Ekseninden Sapması ($\delta$ Formülasyonu)
Denklemin kökleri $f(x) = 0$ eşitliğinden türetilir:

$$a(x - h)^2 + k = 0 \implies (x - h)^2 = -\frac{k}{a} = \frac{\Delta}{4a^2}$$

Her iki tarafın karekökü alındığında köklerin simetri eksenine olan **uzaklık sapması ($\delta$)**:

$$\delta = \sqrt{-\frac{k}{a}} = \frac{\sqrt{\Delta}}{2|a|} = \frac{\sqrt{b^2 - 4ac}}{2|a|}$$

Kökler doğrudan simetri ekseni etrafında simetrik iki nokta olarak ortaya çıkar:

$$x_1 = h - \delta, \quad x_2 = h + \delta$$

> [!IMPORTANT]
> **Kavramsal Atılım:** Kuadratik formül $x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$ öğrenciye gökten inmiş sihirli bir ezber gibi öğretilmez; **"Simetri ekseni ($h$) etrafında sağa ve sola $\delta$ kadar adım atma"** eylemidir:
> $$x = \underbrace{-\frac{b}{2a}}_{\text{Merkez Ekseni } h} \pm \underbrace{\frac{\sqrt{\Delta}}{2a}}_{\text{Sapma } \delta}$$

### 4.2. Dinamik Görselleştirme Kontratı ve 3 Rejim

Kullanıcı arayüzünde tepe noktası $T(h, k)$ dikey olarak sürüklendiğinde ($k$ parametresi değiştikçe), grafik tuvalinde şu rejimler dinamik olarak morflanır:

| Rejim / Durum | Matematiksel Koşul | Görsel Parabol Davranışı | $\delta$ Göstergesi ve Kök Rozeti |
| :--- | :---: | :--- | :--- |
| **Rejim A: İki Reel Kök** | $\Delta > 0 \iff -\frac{k}{a} > 0$ | Parabol $x$-eksenini iki farklı noktada keser ($k < 0, a > 0$). | $x = h$ dikey kesikli mavi çizgi. Sağa ve sola iki yeşil ok uzanır ($\delta$). Okların ucunda parlak yeşil kök noktaları: $h \pm \delta$. |
| **Rejim B: Çift Katlı Kök** | $\Delta = 0 \iff k = 0$ | Parabolün tepe noktası tam olarak $x$-eksenine teğettir. | İki ok sıfıra büzülür ($\delta = 0$). İki kök noktası simetri ekseni üzerinde tek bir altın sarısı noktada birleşir: $x_1 = x_2 = h$. |
| **Rejim C: Reel Kök Yok** | $\Delta < 0 \iff -\frac{k}{a} < 0$ | Parabol $x$-ekseninden havaya kalkar ($k > 0, a > 0$). Eksenle hiçbir temas yoktur. | $\delta = i \cdot \sqrt{k/a}$ karmaşık sayıya döner. $x$-eksenindeki reel kök göstergeleri yarı saydam griye (ghost) dönüşür. Ekranda **"Reel Kök Yok ($\Delta < 0$)"** uyarı rozeti belirir. |

---

## 5. BAĞLANTILI ÇİFT GÖRÜNÜM SENKRONİZASYONU (LINKED DUAL-VIEW PROTOCOL)

Öğrencinin bir ekranda sembolik formülü, başka bir sayfada grafiği görmesi Sweller (1988) tarafından tanımlanan **Bölünmüş Dikkat Etkisine (Split-Attention Effect)** yol açarak çalışma belleğini kilitler. Sistem, bu sorunu **Bağlantılı Çift Görünüm (Linked Dual-View)** mimarisiyle çözer.

```text
┌──────────────────────────────────────────┬──────────────────────────────────────────┐
│ PANEL 1: İNTERAKTİF GEOMETRİK TUVAL      │ PANEL 2: ADIM ADIM SEMBOLİK DENKLEM      │
│                                          │                                          │
│           x                  3           │    x² + 6x = 16                          │
│     ┌───────────┬───────────────┐        │                                          │
│   x │   [x²]    │     [3x]      │        │    x² + 2·(3)x + [ 9 ] = 16 + [ 9 ]      │
│     ├───────────┼───────────────┤        │                  ▲               ▲       │
│   3 │   [3x]    │     [ 9 ]     │ ◄──────┼──────────────────┴───────────────┘       │
│     └───────────┴───────────────┘        │    (Sarı vurgulu terim tuvaldeki sarı    │
│           ▲                              │     küçük kareyle anında reaktif parlar) │
│           └──────────────────────────────┼──┐                                       │
│                                          │  ▼                                       │
│                                          │    (x + 3)² = 25                         │
│                                          │    x + 3 = ±5                            │
│                                          │    x₁ = 2,  x₂ = -8                      │
└──────────────────────────────────────────┴──────────────────────────────────────────┘
```

### 5.1. Reaktif Çift Yönlü Veri Yolu (Bidirectional Reactive Bus)

İki panel arasında mesajlaşma sub-50ms gecikmeli bir WebSocket/EventBus protokolü üzerinden yürütülür:

#### Olay 1: Sembolikten Geometriye (`SYMBOLIC_TO_GEOMETRIC`)
1. Öğrenci sağ panelde `x^2 + 6x = 16` adımından sonra "Her iki tarafa da $3^2 = 9$ ekle" adımını yazar veya seçer.
2. Sağ panel `STEP_COMMITTED { action: "ADD_TERM", value: 9, token_id: "corner_sq" }` olayını fırlatır.
3. Sol panel bu olayı yakalar; 9 adet sarı birim kare sağ üstten süzülerek (tween duration: 250ms, ease: `cubic-bezier(0.34, 1.56, 0.64, 1)`) eksik köşeye yerleşir.
4. Eksik köşe kesikli çizgiden sürekli altın sarısı dolguya dönüşür.

#### Olay 2: Geometriden Semboliğe (`GEOMETRIC_TO_SYMBOLIC`)
1. Öğrenci sol paneldeki araç kutusundan sarı $1 \times 1$'lik karoları sürükleyip eksik köşedeki boş ızgaraya bırakır.
2. Izgara 9 birim dolduğu anda sol panel `GEOMETRY_COMPLETED { area: 9, dimension: [3, 3] }` olayını yayınlar.
3. Sağ paneldeki denklem satırında $+9$ terimi altın sarısı renginde (`#F59E0B`) pırıldayarak belirir.
4. AI Tutor sesli/metin ipucu verir: *"Harika! Geometrik kareyi tamamlamak için 9 birim ekledin. Şimdi eşitliği bozmamak için denklemin sağına ne yapmalısın?"*

### 5.2. Renk ve Vurgu Eşleme Tokenları (Design Token Contract)

Görsel ve sembolik bileşenler ortak CSS tasarım değişkenleriyle kilitlenir:
* `--token-math-x2`: `#2563EB` (Azure Mavi) $\leftrightarrow$ Hem $x^2$ terimi hem $x \times x$ ana karesi.
* `--token-math-linear`: `#059669` (Zümrüt Yeşil) $\leftrightarrow$ Hem $bx$ terimi hem yan şeritler.
* `--token-math-corner`: `#D97706` (Amber Altın) $\leftrightarrow$ Hem $(b/2)^2$ sabiti hem eksik köşe dolgusu.
* `--token-math-symmetry`: `#9333EA` (Mor) $\leftrightarrow$ Hem $h = -b/(2a)$ ekseni hem tepe noktası çizgisi.

---

## 6. DİNAMİK TEMSİL DERLEYİCİSİ VE SENKRONİZASYON MOTORU (PYTHON)

Aşağıdaki Python sınıfı; verilen bir kuadratik denklemi sembolik olarak ayrıştırır, 4 temsil kadrandaki tüm parametreleri hesaplar ve çift görünüm senkronizasyon olaylarını üretir:

```python
"""
Representation Compiler & Dual-View Synchronization Engine
SymPy Tabanlı Çoklu Temsil Derleyicisi
"""

import math
import sympy as sp
from typing import Dict, Any, Tuple, Optional

class DualViewRepresentationEngine:
    def __init__(self):
        self.x = sp.Symbol('x')

    def compile_equation(self, eq_str: str) -> Dict[str, Any]:
        """
        'ax^2 + bx + c = 0' veya 'ax^2 + bx = c' ifadesini 4 temsil kadrana derler.
        """
        clean_eq = eq_str.replace(" ", "")
        if "=" in clean_eq:
            lhs_str, rhs_str = clean_eq.split("=")
            expr = sp.parse_expr(lhs_str) - sp.parse_expr(rhs_str)
        else:
            expr = sp.parse_expr(clean_eq)

        poly = sp.Poly(expr, self.x)
        coeffs = poly.all_coeffs()
        
        # Katsayı normalizasyonu (ax^2 + bx + c)
        if len(coeffs) == 3:
            a, b, c = [float(v) for v in coeffs]
        elif len(coeffs) == 2:
            a, b, c = float(coeffs[0]), float(coeffs[1]), 0.0
        elif len(coeffs) == 1:
            a, b, c = float(coeffs[0]), 0.0, 0.0
        else:
            raise ValueError(f"Geçersiz polinom derecesi: {eq_str}")

        # 1. Sembolik Kadran (T_S)
        disc = b**2 - 4*a*c
        h = -b / (2*a)
        k = -disc / (4*a)
        
        # 2. Geometrik Alan Karosu Kadranı (T_G - Monic x^2 + (b/a)x dönüşümü)
        b_norm = b / a
        c_norm = c / a
        half_b = b_norm / 2.0
        corner_area = half_b ** 2
        
        # 3. Parabolik Kadran (T_P - Simetri ve Kök Mesafesi)
        has_real_roots = disc >= 0
        delta_spread = math.sqrt(disc) / (2 * abs(a)) if has_real_roots else None
        
        roots = []
        if has_real_roots:
            roots = [h - delta_spread, h + delta_spread]

        # 4. Sözel / Durumsal Model (T_V)
        verbal_scaffold = self._generate_verbal_context(a, b, c, h, k)

        return {
            "symbolic_quadrant": {
                "equation": eq_str,
                "standard_form": f"{a}x² + {b}x + {c} = 0",
                "coefficients": {"a": a, "b": b, "c": c},
                "discriminant": disc,
                "completing_the_square_identity": f"(x + {half_b:.2f})² = {-c_norm + corner_area:.2f}"
            },
            "geometric_quadrant": {
                "main_square": {"dimension": "x", "area": "x²"},
                "split_rectangles": {"count": 2, "dimension": f"{half_b:.2f} × x", "total_area": f"{b_norm:.2f}x"},
                "missing_corner": {
                    "width": half_b,
                    "height": half_b,
                    "required_area": corner_area,
                    "is_perfect_integer": corner_area.is_integer()
                },
                "total_completed_square_side": f"x + {half_b:.2f}"
            },
            "parabolic_quadrant": {
                "vertex": (h, k),
                "symmetry_axis_x": h,
                "delta_spread": delta_spread,
                "regime": "TWO_REAL_ROOTS" if disc > 0 else ("DOUBLE_ROOT" if disc == 0 else "NO_REAL_ROOTS"),
                "roots": roots,
                "latex_root_formula": f"x = {h:.2f} \\pm {delta_spread:.2f}" if has_real_roots else "x \\notin \\mathbb{R}"
            },
            "verbal_quadrant": verbal_scaffold
        }

    def _generate_verbal_context(self, a: float, b: float, c: float, h: float, k: float) -> Dict[str, str]:
        """Katsayıların işaret ve tepe noktasına göre gerçek dünya bağlamı üretir."""
        if a < 0:
            return {
                "context_type": "PROJECTILE_MOTION",
                "narrative": f"Bir top yerden fırlatılıyor. t={h:.2f}. saniyede maksimum yüksekliği olan {k:.2f} metreye ulaşıyor.",
                "valid_root_constraint": "Zaman t > 0 olmalıdır. Negatif kök fiziksel olarak elenir."
            }
        else:
            return {
                "context_type": "AREA_OPTIMIZATION",
                "narrative": f"Bir kenarı x metre olan kare bir odaya {b:.1f} metre koridor ekleniyor. Toplam alan hedefine ulaşmak için x hesaplanıyor.",
                "valid_root_constraint": "Uzunluk x > 0 olmalıdır. Negatif kök geometrik olarak elenir."
            }

    def handle_sync_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Çift görünüm senkronizasyon olay yönlendiricisi.
        """
        if event_type == "SYMBOLIC_TERM_ADDED":
            term_value = payload.get("value")
            return {
                "target_panel": "GEOMETRIC_CANVAS",
                "animation": "DROP_TILES_INTO_CORNER",
                "payload": {"units": term_value, "color": "#D97706", "duration_ms": 250}
            }
        elif event_type == "GEOMETRIC_CORNER_FILLED":
            filled_units = payload.get("units")
            return {
                "target_panel": "SYMBOLIC_EDITOR",
                "animation": "HIGHLIGHT_EQUATION_TERM",
                "payload": {"term_latex": f"+ {filled_units}", "color": "#D97706", "prompt": "Her iki tarafa da ekleyin"}
            }
        elif event_type == "VERTEX_DRAGGED":
            new_k = payload.get("k")
            return {
                "target_panel": "DUAL_SYNC",
                "animation": "UPDATE_DISCRIMINANT_AND_DELTA",
                "payload": {"new_k": new_k}
            }
        return {"status": "UNKNOWN_EVENT"}
```
