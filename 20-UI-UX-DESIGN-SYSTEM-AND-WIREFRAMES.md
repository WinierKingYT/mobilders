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

## 2. RENK SİSTEMİ VE BİLİŞSEL TASARIM BELİRTEÇLERİ (DESIGN TOKENS)

Arayüz varsayılan olarak **Koyu Mod (Dark / Slate)** odaklıdır; OLED ekranlarda pil tasarrufu sağlar ve uzun süreli odaklanmada göz yorgunluğunu en aza indirir.

| Token Adı | HEX Kodu | Semantik Anlamı ve Bilişsel İşlevi |
| :--- | :--- | :--- |
| `bg-canvas` | `#0B0F19` | Mobil ana arka plan (Derin Gece / Saf Odak) |
| `surface-card` | `#1E293B` | Kart, adım ve modal zeminleri (Slate-800) |
| `surface-input` | `#0F172A` | Matematiksel girdi kutusu ve klavye arka planı |
| `primary-accent` | `#3B82F6` | Aktif adım, seçili buton, ilerleme çubuğu |
| `math-symbolic` | `#F8FAFC` | Yüksek kontrastlı TeX/LaTeX matematik yazı rengi |
| `success-mastery`| `#10B981` | Doğrulanmış adım, ustalaşılan düğüm ($P(L) \ge 0.85$) |
| `warning-zpd` | `#F59E0B` | Aktif çalışma alanı, ZPD düğümü ($P(L) \approx 0.50$) |
| `error-buggy` | `#EF4444` | Bozuk kural (Buggy Rule) veya aritmetik sapma |
| `socratic-coach` | `#A855F7` | AI Tutor Sokratik yönlendirme balonu ve parlaması |
| `tile-x2` | `#2563EB` | Al-Harezmi $x^2$ büyük kare karosu |
| `tile-x` | `#059669` | Al-Harezmi $x$ dikey/yatay dikdörtgen karosu |
| `tile-unit` | `#D97706` | Al-Harezmi $1$ birim kare karosu |

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
│ 9:41 📶 🔋       ⏱️ 14:22 Kalan       │
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
│ AKTİF ADIM GİRİŞİ:                    │
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
