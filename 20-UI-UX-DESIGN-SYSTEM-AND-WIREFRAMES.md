# 20-UI-UX-DESIGN-SYSTEM-AND-WIREFRAMES.md
# KULLANICI ARAYÜZÜ (UI/UX) TASARIM SİSTEMİ VE EKRAN ŞEMALARI (WIREFRAMES)
## Bilişsel Yükü Sıfırlayan Minimalist Tasarım, Renk Sistemi ve 7 Temel Ekran Şeması

---

## 1. TASARIM SİSTEMİ İLKELERİ (DESIGN PHILOSOPHY)

Platformun görsel kimliği iki temel aksiyoma dayanır:
1. **Düşük Arayüz Sürtünmesi, Yüksek Bilişsel Çaba:** Kullanıcı enerjisini arayüzü anlamaya değil, problemin derin matematiksel yapısını çözmeye harcar.
2. **Anti-Palyaço İlkesi (No EdTech Gimmicks):** Patlayan konfetiler, yapay elmaslar, kalpler veya dikkat dağıtan maskotlar KESİNLİKLE YOKTUR. Motivasyon dışsal ödüllerden değil, **kendi zihninin bir konuyu gerçekten anladığını görmekten (Öz-Yeterlik / Bandura, 1997)** doğar.

---

## 2. RENK SİSTEMİ VE BİLİŞSEL TASARIM BELİRTEÇLERİ (DESIGN TOKENS)

Arayüz varsayılan olarak **Koyu Mod (Dark / Slate)** odaklıdır; uzun süreli matematiksel odaklanmada göz yorgunluğunu en aza indirir.

| Token Adı | HEX Kodu | Semantik Anlamı ve Bilişsel İşlevi |
| :--- | :--- | :--- |
| `bg-canvas` | `#0B0F19` | Ana arka plan (Derin Gece / Minimalist Odak) |
| `surface-card` | `#1E293B` | Kart ve panel zeminleri (Hafif ayrıştırılmış katman) |
| `primary-accent` | `#3B82F6` | Aktif adım, seçili buton, ilerleme çizgisi |
| `math-symbolic` | `#F8FAFC` | Yüksek kontrastlı LaTeX matematik yazı rengi |
| `success-mastery`| `#10B981` | Doğrulanmış adım, usta düğüm ($P(L) \ge 0.85$) |
| `warning-zpd` | `#F59E0B` | Aktif çalışma alanı, ZPD düğümü ($P(L) \approx 0.50$) |
| `error-buggy` | `#EF4444` | Bozuk kural (Buggy Rule) veya aritmetik sapma |
| `socratic-coach` | `#A855F7` | AI Tutor Sokratik yönlendirme balonu ve parlaması |
| `tile-x2` | `#2563EB` | Al-Harezmi $x^2$ büyük kare karosu |
| `tile-x` | `#059669` | Al-Harezmi $x$ dikey/yatay şerit karosu |
| `tile-unit` | `#D97706` | Al-Harezmi $1$ birim kare karosu |

---

## 3. 7 TEMEL EKRAN ŞEMASI VE BİLEŞEN HİYERARŞİSİ (ASCII WIREFRAMES)

---

### EKRAN 1: DİNAMİK TEŞHİS EKRANI (DIAGNOSTIC CAT SCREEN)
* **Amaç:** Öğrencinin başlangıç seviyesini 8 soruda stres yaratmadan belirlemek.

```text
+─────────────────────────────────────────────────────────────────────────────+
| [LOGO] CEBİR MOTORU                       [ Soru 3 / 8 ]   [ İlerleme: 38% ]|
+─────────────────────────────────────────────────────────────────────────────+
|                                                                             |
|                      SEVİYE BELİRLEME SORUSU                                |
|                                                                             |
|            x² - 5x + 6 = 0  denkleminin köklerini bulunuz.                  |
|                                                                             |
+─────────────────────────────────────────────────────────────────────────────+
|  [ ÇÖZÜMÜNÜ YAZ ]:                                                          |
|  +-----------------------------------------------------------------------+  |
|  | x = 2  veya  x = 3                                                    |  |
|  +-----------------------------------------------------------------------+  |
|                                                                             |
|  Bu cevabından ne kadar eminsin?                                            |
|  [   ] %25 (Tahmin)   [   ] %50 (Kısmen)   [ ● ] %75 (Eminim)   [   ] %100   |
|                                                                             |
|  [ EKRAN KLAVYESİ ]:  [ x ]  [ ² ]  [ ± ]  [ √ ]  [ = 0 ]  [ Kesir ]        |
|                                                                             |
|  [ BİLMİYORUM / EMİN DEĞİLİM ]                            [ CEVABI GÖNDER ] |
+─────────────────────────────────────────────────────────────────────────────+
```

---

### EKRAN 2: ÇÖZÜM TAHTASI VE SOKRATİK REHBER (INTERACTIVE SCRATCHPAD)
* **Amaç:** Günlük 20 dakikalık seansın kalbi; adım bazlı doğrulama ve rehberlik.

```text
+─────────────────────────────────────────────────────────────────────────────+
| [SEANS: 14:22 Kalan]  [DÜĞÜM: Tam Kareye Tamamlama]  [İSKELE: Seviye 2]     |
+─────────────────────────────────────────────────────────────────────────────+
| HEDEF PROBLEM:  x² + 6x - 2 = 0  denklemini tam kareye tamamlayarak çözün.  |
+─────────────────────────────────────────────────────────────────────────────+
|                                                                             |
| [ADIM 1]  x² + 6x = 2                                       [ ✓ DOĞRULANDI ]|
|                                                                             |
| [ADIM 2]  x² + 6x + 9 = 2 + 9                               [ ✓ DOĞRULANDI ]|
|                                                                             |
| [ADIM 3]  (x + 3)² = 11                                     [ ✓ DOĞRULANDI ]|
|                                                                             |
| [ADIM 4]  x + 3 = √11                                       [ ✕ EKSİK KÖK! ]|
|                                                                             |
+─────────────────────────────────────────────────────────────────────────────+
| 💡 AI TUTOR SOKRATİK YÖNLENDİRMESİ:                                         |
| "Sol tarafın karesi 11 ise, karesi 11 eden sadece pozitif √11 midir?       |
|  Negatif bir ikizi olabilir mi? İşareti gözden geçir."                      |
|                                                                             |
| [ YENİ ADIM YAZ ]:                                                          |
| +---------------------------------------------------------+ +-------------+ |
| | x + 3 = ±√11                                            | | [ GÖNDER ]  | |
| +---------------------------------------------------------+ +-------------+ |
| [ Hızlı Tuşlar ]:  [ x ]  [ ² ]  [ ± ]  [ √ ]  [ = ]  [ ( ]  [ ) ]  [ Geri ]|
+─────────────────────────────────────────────────────────────────────────────+
```

---

### EKRAN 3: AL-HAREZMI VE DİNAMİK PARABOL ÇİFT GÖRÜNÜMÜ (DUAL VIEW CANVAS)
* **Amaç:** Sembolik denklem ile geometrik/fonksiyonel temsili aynı anda bağlamak.

```text
+───────────────────────────────────────┬─────────────────────────────────────+
| SOL PANEL: AL-HAREZMI ALAN KAROLARI   │ SAĞ PANEL: DİNAMİK PARABOL GRAFİĞİ  |
+───────────────────────────────────────┼─────────────────────────────────────+
|                                       │           y                         |
|         x             3               │           │         f(x)=(x+3)²-11  |
|     +-------+       +---+             │           │   \                 /   |
|   x |  x²   |     x |3x |             │           │    \   Tepe        /    |
|     +-------+       +---+             │     ──────┼─────●─────────────┼─► x |
|                                       │          -3 │  (-3,-11)             |
|     +-------+       +---+             │             │                       |
|   3 |  3x   |     3 | 9 | ◄──[EKSİK]  │ Simetri Ekseni: x = -3              |
|     +-------+       +---+    (Parıldar│ Kök Mesafesi: δ = √11 ≈ 3.31        |
|                                       │ Kökler: x = -3 ± √11                |
+───────────────────────────────────────┴─────────────────────────────────────+
| [ CANLI ETKİLEŞİM ]: Sol panelde 9'luk karo eklendiğinde sağdaki parabolün  |
| tepe noktası otomatik olarak y-ekseninde yerine oturur.                     |
+─────────────────────────────────────────────────────────────────────────────+
```

---

### EKRAN 4: ÜRETİCİ BAŞARISIZLIK ÇİFT PANELİ (PF CONTRASTING CASES)
* **Amaç:** Serbest keşif adımlarını kanonik kuralla karşılaştırarak derin kavrayış sağlamak.

```text
+─────────────────────────────────────────────────────────────────────────────+
| [ROZET: 🛡️ KEŞİF MODU - PUAN CEZASI YOKTUR - SEZGİLERİNİ TEST ET]           |
| GÖREV: x² + 6x - 2 = 0 denklemini çözmek için aklına gelen 2 yolu dene.     |
+───────────────────────────────────────┬─────────────────────────────────────+
| SOL PANEL: SENİN DENEMELERİN (SGR)    │ SAĞ PANEL: KANONİK BİRLEŞTİRME      |
+───────────────────────────────────────┼─────────────────────────────────────+
| ❌ 1. Denemen: x(x + 6) = 2           │ 💡 AI Tutor Sentezi:                |
|    Buradan x = 2 dedin.               │ "Çarpımı 2 olan sonsuz reel sayı    |
|    Teşhis: Çarpım kuralı sadece       │  vardır. Ama geometrik denemende    |
|    sağ taraf 0 iken çalışır.          │  harika bir şey yakaladın:          |
|                                       │                                     |
| ⭐ 2. Denemen: Geometrik Karo Taslağı │  x² + 6x ifadesini tam bir kare     |
|    Köşede 9 birimlik bir boşluk       │  yapmak için köşeye 9 eklemeliyiz!  |
|    kaldığını fark ettin!              │                                     |
|                                       │     x² + 6x + 9 = 2 + 9             |
|                                       │     (x + 3)² = 11                   |
+───────────────────────────────────────┴─────────────────────────────────────+
| [ ANLADIM, ŞİMDİ BU YÖNTEMLE ADIM AT ]                                       |
+─────────────────────────────────────────────────────────────────────────────+
```

---

### EKRAN 5: BEYİN HARİTASI (LIVING BRAIN MAP / DAG VIEW)
* **Amaç:** Öğrencinin zihinsel yetkinlik ağını şeffaf bir atlas olarak sunmak.

```text
+─────────────────────────────────────────────────────────────────────────────+
| [CEBİR ATLASI]  Toplam Yetkinlik: %74   Usta Düğümler: 14 / 20              |
+─────────────────────────────────────────────────────────────────────────────+
|                                                                             |
|      [N01: Tam Sayılar] (✓ %98)                                             |
|              │                                                              |
|              ▼                                                              |
|      [N02: Doğrusal Denklemler] (✓ %94)                                     |
|              │                                                              |
|              ├──────────────────────────────────┐                           |
|              ▼                                  ▼                           |
|      [N06: Ortak Parantez] (✓ %90)      [N07: İki Kare Farkı] (✓ %88)       |
|              │                                  │                           |
|              └─────────────────┬────────────────┘                           |
|                                ▼                                            |
|                    [N12: Çarpanlara Ayırma] (✓ %85)                         |
|                                │                                            |
|                                ▼                                            |
|               ●───►[N15: TAM KAREYE TAMAMLAMA] (ŞU ANKİ HEDEF - %62)        |
|                    [ Yanıp Sönen Sarı Halka ]                               |
|                                │                                            |
|                                ▼                                            |
|                    [N18: Kuadratik Formül] (🔒 Kilitli)                     |
|                                │                                            |
|                                ▼                                            |
|                    [N22: Parabol Geometrisi] (🔒 Kilitli)                   |
|                                                                             |
+─────────────────────────────────────────────────────────────────────────────+
```

---

### EKRAN 6: AFEKTİF GÜVENLİK ŞALTERİ MODALI (AFFECTIVE CIRCUIT BREAKER)
* **Amaç:** Bilişsel boğulma anında ekranı dondurup öğrenilmiş çaresizliği engellemek.

```text
+─────────────────────────────────────────────────────────────────────────────+
|                                                                             |
|                          🌿 BİR DERİN NEFES ALALIM                          |
|                                                                             |
|                             ( O )  ◄──[Nefes Dairesi Yavaşça Genişler]      |
|                                                                             |
|     Bu soru gerçekten çok çetin bir düğüm içeriyor. Yalnız değilsin;        |
|     M.S. 820'de Al-Harezmi ve 16. yüzyılda İtalyan matematikçiler de        |
|     bu noktada yüzlerce yıl zorlandı.                                       |
|                                                                             |
|     Sen çok cesurca 3 farklı deneme yaptın. Puan kaybın kesinlikle yok.     |
|                                                                             |
|     [ BİRLİKTE ÇÖZELİM (Çözümlü Örnek) ]           [ 5 DAKİKA MOLA VER ]    |
|                                                                             |
+─────────────────────────────────────────────────────────────────────────────+
```

---

### EKRAN 7: BİLİŞSEL KAZANIM KARTI (SESSION WRAP-UP CARD)
* **Amaç:** 20 dakikanın sonunda zihinsel kazanımı somutlaştırıp uyku kilidini koymak.

```text
+─────────────────────────────────────────────────────────────────────────────+
|                          🎉 GÜNLÜK SEANS TAMAMLANDI                         |
+─────────────────────────────────────────────────────────────────────────────+
|  ⏱️ Aktif Düşünme Süresi:  19 Dakika 45 Saniye                              |
|  🧠 Kazanılan Ustalık:     "Tam Kareye Tamamlama" (%78 Seviyesine Çıktı)    |
|  🎯 Metabilişsel Uyum:     %88 Kalibrasyon Doğruluğu                        |
|  ⚡ Hata Onarımı:          "Negatif Kök Kaybı" kuralı başarıyla tamir edildi|
+─────────────────────────────────────────────────────────────────────────────+
|  🌙 SİRKADİYEN HAFIZA KONSOLİDASYONU KİLİDİ:                                |
|  Bugün öğrendiğin prosedürel kuralların nöral olarak mühürlenmesi için      |
|  beyninin NREM ve REM uykusuna ihtiyacı var.                                |
|                                                                             |
|  Bir sonraki çalışma seansı:  YARIN 09:00                                   |
|                                                                             |
|  [ GÜNÜ TAMAMLA VE ÇIK ]                                                    |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 4. MOBİL DOKUNMATİK ERGONOMİSİ (TOUCH TARGETS)

* **Başparmak Bölgesi (Thumb Zone):** MathLive akıllı sembol tuşları ekranın alt %35'lik alanına sabitlenir.
* **Minimum Dokunma Alanı:** Her buton minimum $48 \times 48\text{ px}$ boyutundadır (WCAG 2.1 AA standardı).
* **Geri Bildirim:** Her geçerli adım girişinde hafif haptik titreşim (mobil destekliyorsa 10ms haptic feedback).
