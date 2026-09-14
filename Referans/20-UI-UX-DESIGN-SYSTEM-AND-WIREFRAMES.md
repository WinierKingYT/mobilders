# 20-UI-UX-DESIGN-SYSTEM-AND-WIREFRAMES.md
# AKILLI TELEFON (PORTRAIT) UI/UX TASARIM SİSTEMİ VE EKRAN ŞEMALARI (WIREFRAMES)
## Bilişsel Yükü Sıfırlayan Minimalist Tasarım, Başparmak Ergonomisi, Çift Modlu Klavye ve 7 Mobil Ekran Şeması

---

## 1. MOBİL TASARIM SİSTEMİ İLKELERİ (MOBILE DESIGN PHILOSOPHY)

Platformun akıllı telefon arayüzü ($390 \times 844$ dikey yönelim) iki temel aksiyoma dayanır:
1. **Düşük Arayüz Sürtünmesi, Yüksek Bilişsel Çaba:** Kullanıcı enerjisini ekranda gezinmeye veya karmaşık menülere değil, problemin derin matematiksel yapısını çözmeye harcar.
2. **Anti-Palyaço İlkesi (No EdTech Gimmicks):** Patlayan konfetiler, yapay elmaslar, can kaybetme stresleri veya dikkat dağıtan maskotlar KESİNLİKLE YOKTUR. Motivasyon, **kendi zihninin bir konuyu gerçekten anladığını görmekten (Öz-Yeterlik / Bandura, 1997)** doğar.
3. **Başparmak Bölgesi (Thumb Zone) Ergonomisi:** Kritik tüm matematiksel etkileşimler ve girdi alanı, tek elle veya iki başparmakla kolayca erişilebilen alt %45'lik ekranda toplanır.

---

## 2. RENK SİSTEMİ, TİPOGRAFİ VE BİLİŞSEL TASARIM BELİRTEÇLERİ (DESIGN TOKENS)

Arayüz varsayılan olarak **Koyu Mod (Dark / Slate)** odaklıdır; OLED ekranlarda pil tasarrufu sağlar ve uzun süreli odaklanmada göz yorgunluğunu en aza indirir. Tüm renk kombinasyonları WCAG 2.1 AAA (en az 7:1 kontrast) standardını karşılar.

### 2.1. Semantik Renk Belirteçleri (Semantic Color Palette)

| Token Adı | HEX Kodu | WCAG Kontrastı | Semantik Anlamı ve Bilişsel İşlevi |
| :--- | :--- | :---: | :--- |
| `bg-canvas` | `#0B0F19` | - | Mobil ana arka plan (Derin Gece / Saf Odak) |
| `surface-card` | `#1E293B` | - | Kart, adım ve modal zeminleri (Slate-800) |
| `surface-input` | `#0F172A` | - | Matematiksel girdi kutusu ve klavye arka planı |
| `primary-accent` | `#3B82F6` | 8.2:1 (bg üzerinde) | Aktif adım, seçili buton, ilerleme çubuğu (Mavi) |
| `math-symbolic` | `#F8FAFC` | 15.8:1 (bg üzerinde) | Yüksek kontrastlı TeX/LaTeX matematik yazı rengi |
| `text-secondary` | `#94A3B8` | 7.1:1 (bg üzerinde) | İpucu, süre ve ikincil açıklamalar (Slate-400) |
| `success-mastery`| `#10B981` | 9.4:1 (bg üzerinde) | Doğrulanmış adım, ustalaşılan düğüm ($P(L) \ge 0.85$) |
| `warning-zpd` | `#F59E0B` | 8.7:1 (bg üzerinde) | Aktif çalışma alanı, ZPD düğümü ($P(L) \approx 0.50$) |
| `error-buggy` | `#EF4444` | 7.5:1 (bg üzerinde) | Bozuk kural (Buggy Rule) veya aritmetik sapma |
| `socratic-coach` | `#A855F7` | 7.8:1 (bg üzerinde) | AI Tutor Sokratik yönlendirme balonu ve parlaması |
| `tile-x2` | `#2563EB` | 8.0:1 (metin beyaz) | Al-Harezmi $x^2$ büyük kare karosu |
| `tile-x` | `#059669` | 7.9:1 (metin beyaz) | Al-Harezmi $x$ dikey/yatay dikdörtgen karosu |
| `tile-unit` | `#D97706` | 7.3:1 (metin beyaz) | Al-Harezmi $1$ birim kare karosu |

### 2.2. Tipografi Hiyerarşisi (Typography Hierarchy)
- **Metin ve Arayüz Fontu:** `Inter` (Google Fonts)
  - `Display / Sayaç`: 28sp / Bold (Seans Geri Sayımı)
  - `Title / Problem`: 18sp / Semi-Bold (Aktif Denklem Başlığı)
  - `Body / Sokratik`: 15sp / Regular (AI Tutor İskele Mesajları, 1.4 satır aralığı)
  - `Caption / İpucu`: 12sp / Medium (Tuş altı açıklamaları ve ZPD yüzdesi)
- **Matematik ve Sembol Fontu:** `JetBrains Mono` & `flutter_math_fork` (KaTeX Font Ailesi)
  - Tüm değişkenler ($x, y, t$), sayılar ($0-9$) ve operatörler ($+, -, =, \pm, \sqrt{}$) matematiksel render motoru üzerinden orantılı çizilir.

### 2.3. Bilişsel UI Bileşen Mimarisi (Component Architecture)
1. **`MathStepCard`:** Çözüm tahtasındaki her bir doğrulanan adım; solunda doğrulama rozeti (✓ veya ⚠️), ortasında KaTeX TeX gösterimi, sağında latens göstergesi barındırır.
2. **`TouchpadGrid`:** $48 \times 48\text{ dp}$ minimum dokunmatik hedeflere sahip, çift başparmakla erişilebilir 5 sütunlu matematik klavye modülü.
3. **`SocraticScaffoldBubble`:** `#A855F7` hafif mor parıltılı, asla cevabı vermeyen, öğrenciyi düşündüren kart widget'ı.
4. **`BreathingCircleModal`:** $F_{\text{score}} \ge 0.85$ olduğunda tam ekran açılan, 15 saniyelik de-eskalasyon ve sakinleşme dairesi.

---

## 3. BAŞPARMAK ERGONOMİSİ VE ÇİFT MODLU GİRDİ SİSTEMİ

### A. Steven Hoober Başparmak Alanı Dağılımı ($390 \times 844$ Ekran)
```text
┌───────────────────────────────────────┐ 0px
│ [ ÜST BÖLGE: GÖZLEM ALANI ]           │
│ - Seans Sayacı (14:22)                │
│ - Hedef Problem Tanımı                │ ◄── "Zor Bölge" (Ow Zone)
│ - Sokratik İskele Yönlendirme Kartı   │     Sadece okuma yapılır,
│                                       │     dokunma aranmaz.
├───────────────────────────────────────┤ 420px
│ [ ORTA BÖLGE: ADIM LİSTESİ ]          │
│ - Kaydırılabilir Adım Kartları        │ ◄── "Uzanma Bölgesi" (Stretch Zone)
│   (Önceki Doğrulanmış Adımlar)        │     Kaydırma ve inceleme alanı.
├───────────────────────────────────────┤ 560px
│ [ ALT BÖLGE: DOĞAL DOKUNMA BÖLGESİ ]  │
│ - Giriş Modu Seçici (Touchpad / Klavye│
│ - Aktif Matematik Girdi Satırı        │ ◄── "Kolay Bölge" (Natural Zone)
│ - Özel Matematik Tuş Takımı           │     Başparmakla tek dokunuş
│   veya Sistem Klavyesi                │     (Haptik titreşim destekli).
└───────────────────────────────────────┘ 844px
```

### B. Çift Modlu Giriş Seçici (Input Mode Switcher)
Öğrencinin tercihine göre tek dokunuşla mod değişir:
- **Mod 1 (Touchpad - Özel Tuş Takımı):** Formül parçalarını tek dokunuşla ekler, mobilde parantez/üs açmayı zahmetsiz kılar.
- **Mod 2 (Serbest Klavye):** Sistem klavyesini açar; harici klavye kullanan veya seri yazmak isteyen öğrenciler için tam özgürlük sunar. Akıllı sözdizim düzelticisi `^` işaretini üsse, `x2`yi `x^2`ye dönüştürür.

---

## 4. 7 TEMEL AKILLI TELEFON EKRAN ŞEMASI (ASCII WIREFRAMES)

---

### EKRAN 1: MOBİL DİNAMİK TEŞHİS EKRANI (CAT SCREEN)
* **Amaç:** 8-12 uyarlamalı soruda öğrencinin kuadratik yetenek seviyesini ($\theta$) belirlemek.

```text
┌───────────────────────────────────────┐
│ 9:41 📶 🔋                            │
│ [✕ Çık]       SEVİYE BELİRLEME    3/8 │
│ ■■■■■□□□□□□□ [İlerleme: %38]          │
├───────────────────────────────────────┤
│                                       │
│ SORU:                                 │
│  x² - 5x + 6 = 0                      │
│  denkleminin köklerini bulunuz.       │
│                                       │
│ ÇÖZÜMÜN:                              │
│ ┌───────────────────────────────────┐ │
│ │ x = 2  veya  x = 3                │ │
│ └───────────────────────────────────┘ │
│                                       │
│ Bu cevabından ne kadar eminsin?       │
│ (●) %25  ( ) %50  ( ) %75  ( ) %100   │
│                                       │
├───────────────────────────────────────┤
│ [ 🧮 TUŞ TAKIMI ]   [ ⌨️ SERBEST KLAVYE]│
├─────┬─────┬─────┬─────┬───────────────┤
│  x  │ x²  │  √  │  ±  │      DEL      │
├─────┼─────┼─────┼─────┼───────────────┤
│  7  │  8  │  9  │  (  │       )       │
├─────┼─────┼─────┼─────┼───────────────┤
│  4  │  5  │  6  │  +  │       -       │
├─────┼─────┼─────┼─────┼───────────────┤
│  1  │  2  │  3  │  =  │  BİLMİYORUM   │
├─────┴─────┼─────┼─────┴───────────────┤
│     0     │  /  │   CEVABI GÖNDER     │
└───────────┴─────┴─────────────────────┘
```

---

### EKRAN 2: MOBİL KARALAMA DEFTERİ VE SOKRATİK ÇÖZÜM TAHTASI (SCRATCHPAD)
* **Amaç:** Günlük 20 dakikalık odaklanmış seansın kalbi; adım bazlı gerçek zamanlı doğrulama.

```text
┌───────────────────────────────────────┐
│ 9:41 📶 🔋 🤫[Sessiz] ⏱️ 14:22 Kalan  │
│ 🎯 DÜĞÜM: Tam Kareye Tamamlama (N15) │
├───────────────────────────────────────┤
│ HEDEF DENKLEM:                        │
│   x² + 6x - 2 = 0     [📝 MÜSVEDDE ◄] │
│                                       │
│ [ADIM 1]  x² + 6x = 2         [✓ Doğru│
│ [ADIM 2]  x² + 6x + 9 = 11    [✓ Doğru│
│ [ADIM 3]  (x + 3)² = 11       [✓ Doğru│
│ [ADIM 4]  ~~x + 3 = √11~~     [✕ Hata!│
│  (Kırmızı üzeri çizili - silinmez)    │
│                                       │
│ 💡 SOKRATİK KOÇ (AI TUTOR):           │
│ ┌───────────────────────────────────┐ │
│ │ "Karesi 11 eden tek sayı √11      │ │
│ │  midir? Negatif ikizini hatırla." │ │
│ └───────────────────────────────────┘ │
├───────────────────────────────────────┤
│ AKTİF GİRDİ:          [ 💡 TAKILDIM ] │
│ ┌───────────────────────────────────┐ │
│ │ x + 3 = ±√11                      │ │
│ └───────────────────────────────────┘ │
│ [ 🧮 TUŞ TAKIMI ● ]  [ ⌨️ SERBEST KLAVYE]│

├─────┬─────┬─────┬─────┬───────────────┤
│  x  │ x²  │  √  │  ±  │      DEL      │
├─────┼─────┼─────┼─────┼───────────────┤
│  7  │  8  │  9  │  (  │       )       │
├─────┼─────┼─────┼─────┼───────────────┤
│  4  │  5  │  6  │  +  │       -       │
├─────┼─────┼─────┼─────┼───────────────┤
│  1  │  2  │  3  │  =  │   ADIM EKLE   │
├─────┴─────┼─────┼─────┴───────────────┤
│     0     │  ,  │   ADIMI DOĞRULA 🚀  │
└───────────┴─────┴─────────────────────┘
```


---

### EKRAN 3: MOBİL AL-HAREZMI & PARABOL GÖRSEL TEMSİLİ (DUAL REPRESENTATION)
* **Amaç:** Ekran darlığı nedeniyle sekmeli (Segmented Control) yapıda geometrik karo ile parabolü bağlamak.

```text
┌───────────────────────────────────────┐
│ 9:41 📶 🔋              [✕ Kapat]    │
│ 📐 ÇOKLU TEMSİL KÖPRÜSÜ               │
├───────────────────────────────────────┤
│ [ ● 📐 AL-HAREZMI ]  [ 📈 PARABOL ]    │
├───────────────────────────────────────┤
│                                       │
│  Geometrik Alan Karosu Modeli:        │
│                                       │
│         x             3               │
│     ┌───────┐       ┌───┐             │
│   x │  x²   │     x │3x │             │
│     └───────┘       └───┘             │
│     ┌───────┐       ┌───┐             │
│   3 │  3x   │     3 │ ? │ ◄── [BOŞLUK]│
│     └───────┘       └───┘  (Parıldar) │
│                                       │
│ 💡 Sezgisel Soru:                     │
│ "Şekli tam bir büyük kare yapmak      │
│  için sağ alt köşeye kaç birimlik     │
│  karo eklemelisin?"                   │
│                                       │
│ [ +9 BİRİM EKLE (ALANI TAMAMLA) ]     │
├───────────────────────────────────────┤
│ [ Parabol Sekmesine Geç ──► ]         │
└───────────────────────────────────────┘
```

---

### EKRAN 4: MOBİL ÜRETİCİ BAŞARISIZLIK (PF CONTRASTING CASES)
* **Amaç:** Öğrencinin serbest denemesi ile kanonik matematiksel çözümü dikey kartlarla kıyaslamak.

```text
┌───────────────────────────────────────┐
│ 9:41 📶 🔋              🛡️ KEŞİF MODU │
│ PUAN CEZASI YOKTUR - ZİHNİNİ ÖZGÜR TUT│
├───────────────────────────────────────┤
│ PROBLEM: x² + 6x - 2 = 0              │
│                                       │
│ ┌─ ❌ SENİN DENEMEN ────────────────┐ │
│ │ x(x + 6) = 2                      │ │
│ │ x = 2  veya  x + 6 = 2            │ │
│ │                                   │ │
│ │ Teşhis: Sağ taraf 0 olmadığı için │ │
│ │ çarpanlar 2'ye eşitlenemez.       │ │
│ └───────────────────────────────────┘ │
│                                       │
│ ┌─ 💡 KANONİK YOL (TAM KARE) ───────┐ │
│ │ x² + 6x + 9 = 2 + 9               │ │
│ │ (x + 3)² = 11                     │ │
│ │                                   │ │
│ │ Fark: Eşitliğin her iki tarafına  │ │
│ │ 9 ekleyerek sol tarafı tam kare   │ │
│ │ yaptık!                           │ │
│ └───────────────────────────────────┘ │
│                                       │
│ [ ANLADIM, ŞİMDİ KENDİM DENEYEYİM ]   │
└───────────────────────────────────────┘
```

---

### EKRAN 5: MOBİL CEBİR ATLASI (LIVING BRAIN MAP)
* **Amaç:** 20 düğümlü kuadratik bilgi grafını dikey kaydırılabilir düğüm ağacı olarak sunmak.

```text
┌───────────────────────────────────────┐
│ 9:41 📶 🔋              [⚙️ Ayarlar]  │
│ 🧠 CEBİR ATLASI (Gelişim Haritan)     │
│ Usta Düğümler: 12 / 20    Güç: %68    │
├───────────────────────────────────────┤
│                                       │
│   [✓ N01: Tam Sayılar] (%99)          │
│            │                          │
│            ▼                          │
│   [✓ N02: Doğrusal Denklemler] (%95)  │
│            │                          │
│     ┌──────┴──────┐                   │
│     ▼             ▼                   │
│   [✓ N06]       [✓ N07] (%90)         │
│     │             │                   │
│     └──────┬──────┘                   │
│            ▼                          │
│   [✓ N12: Çarpanlara Ayırma] (%85)    │
│            │                          │
│            ▼                          │
│  ⭐ [● N15: TAM KAREYE TAMAMLAMA]      │
│     [ Aktif Öğrenme Düğümü - %62 ]    │
│            │                          │
│            ▼                          │
│   [🔒 N18: Kuadratik Formül]          │
│            │                          │
│            ▼                          │
│   [🔒 N22: Parabol Geometrisi]        │
│                                       │
│ [ SEANSA BAŞLA (N15 ÇALIŞ) 🚀 ]       │
└───────────────────────────────────────┘
```

---

### EKRAN 6: MOBİL AFEKTİF GÜVENLİK ŞALTERİ (CIRCUIT BREAKER)
* **Amaç:** 3 ardışık başarısızlık veya yüksek kaygıda arayüzü dondurup duygusal şefkat sağlamak.

```text
┌───────────────────────────────────────┐
│ 9:41 📶 🔋                            │
│                                       │
│                                       │
│               🌿                      │
│        BİR DERİN NEFES AL             │
│                                       │
│             (  O  )                   │
│    ◄──[Nefes Animasyonu Genişler]──►  │
│                                       │
│   Bu problem gerçekten zorlu bir      │
│   kavram içeriyor. Yalnız değilsin;   │
│   Al-Harezmi de bu denklem tipi       │
│   üzerinde yıllarca düşündü.          │
│                                       │
│   3 cesur deneme yaptın. Puan kaybı   │
│   veya ceza kesinlikle yok.           │
│                                       │
│ ┌───────────────────────────────────┐ │
│ │ [ 🤝 BİRLİKTE ADIM ADIM ÇÖZELİM ] │ │
│ └───────────────────────────────────┘ │
│ ┌───────────────────────────────────┐ │
│ │ [ ☕ 5 DAKİKA DİNLENME MOLASI VER] │ │
│ └───────────────────────────────────┘ │
└───────────────────────────────────────┘
```

---

### EKRAN 7: GÜN SONU KAZANIM KARTI VE SİRKADİYEN KİLİT
* **Amaç:** 20 dakikalık süreyi tamamlayıp bilişsel kazancı mühürlemek ve uyku kilidini koymak.

```text
┌───────────────────────────────────────┐
│ 9:41 📶 🔋                            │
│                                       │
│       ✨ 20 DAKİKALIK SEANS BİTTİ     │
│                                       │
│ ┌─ 📊 BUGÜNKÜ ZİHİNSEL KAZANIMIN ───┐ │
│ │ ⏱️ Net Düşünme: 19 Dakika 40 Sn   │ │
│ │ 🧠 Yeni Ustalık: N15 Tam Kareleme │ │
│ │ 🎯 Güven Uyumu:  %86 Kalibrasyon  │ │
│ │ ⚡ Tamir Edilen: Negatif Kök Kural│ │
│ └───────────────────────────────────┘ │
│                                       │
│ 🌙 SİRKADİYEN UYKU KİLİDİ AKTİF:      │
│ Beyninin bu yeni kuralları kalıcı     │
│ hafızaya yazması için uykuya ihtiyacı │
│ var. Bugün daha fazla soru çözmek     │
│ öğrenmeye katkı sağlamaz.             │
│                                       │
│ Sonraki Açılış: YARIN 08:00           │
│                                       │
│ ┌───────────────────────────────────┐ │
│ │ [ 🚪 UYGULAMADAN ÇIK VE DİNLEN ]   │ │
│ └───────────────────────────────────┘ │
└───────────────────────────────────────┘
```

---

## 5. DOKUNMATİK HEDEF STANDARTLARI (TOUCH ERGONOMICS)

1. **Minimum Dokunma Alanı (Touch Target):** Tüm tuş takımı butonları en az $48 \times 48\text{ dp}$ boyutundadır (Material 3 & Apple HIG yönergeleri).
2. **Dokunsal Geri Bildirim (Haptic Feedback):**
   - Tuşa basma: `HapticFeedback.selectionClick()` (Hafif mekanik tıklama hissi).
   - Doğrulanmış geçerli adım: `HapticFeedback.lightImpact()` (Başarı hissi).
   - Bozuk Kural / Hata: `HapticFeedback.heavyImpact()` (Farkındalık yaratan hafif tok titreşim).
3. **Klavye Yüksekliği:** Ekranın alt %40'ını aşmaz; adım kartlarının ve hedef problemin görünürlüğünü asla engellemez.

---

## 6. ERİŞİLEBİLİRLİK (A11Y) VE KAPSAYICI TASARIM STANDARTLARI

1. **Dinamik Tip Boyutu (Dynamic Type Support):**
   * Kullanıcı sistem fontunu büyüttüğünde matematiksel semboller ve kart metinleri taşma (RenderFlex overflow) yapmadan esnek dikey kaydırmaya geçer.
2. **Ekran Okuyucu ve Matematik Seslendirme (TalkBack / VoiceOver):**
   * Her adım kartı için `Semantics` widget'ı üzerinden semantik metin tanımlanır:
   * Örneğin $x^2 + 6x = 2$ ifadesi ekran okuyucuya *"x kare artı altı x eşittir iki"* olarak seslendirilir; ham LaTeX string'i (`x\^2 + 6x = 2`) asla okunmaz.
3. **Renk Körlüğü Paleti ve Biçimsel Ayıraçlar (Non-Color Reliance):**
   * Bilgi durumu yalnızca renklerle (yeşil/kırmızı) aktarılmaz:
     - Geçerli adım: Yeşil renk + Onay İkonu (✓) + Hafif Haptik Titreşim.
     - Hatalı/Bozuk Kural adımı: Kırmızı/Turuncu renk + Ünlem İkonu (⚠️) + Çift Tok Haptik Titreşim.
   * Karolar desen dokularıyla (çizgili, noktalı, düz) ayırt edilebilir durumdadır.

