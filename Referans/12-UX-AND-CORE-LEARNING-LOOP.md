# 12-UX-AND-CORE-LEARNING-LOOP.md
# KULLANICI DENEYİMİ VE ÇEKİRDEK ÖĞRENME AKIŞI (UX & CORE LEARNING LOOP)
## Arayüz Felsefesi, 20 Dakikalık Günlük Seans Tasarımı ve Zihin Haritası

---

## 1. KULLANICI DENEYİMİ FELSEFESİ (UX PHILOSOPHY)

Geleneksel EdTech arayüzleri iki aşırı uç arasında savrulur: Ya karmaşık, sıkıcı ve akademik bir form yığınıdır ya da dikkati sürekli dağıtan emojiler, patlayan konfetiler ve yapay seslerle dolu bir oyun salonudur (Gamification overload).

### Temel Tasarım İlkemiz:
> **"Düşük Arayüz Sürtünmesi, Yüksek Bilişsel Çaba (Low Interface Friction, High Cognitive Effort)."**

Kullanıcı arayüzü anlamakla değil, problemin matematiği üzerinde düşünmekle meşgul olmalıdır. Bilişsel kapasitenin %100'ü sorunun derin yapısına yönlendirilir.

---

## 2. 20 DAKİKALIK OPTİMİZE GÜNLÜK ÖĞRENME SEANSI (DAILY FLOW)

Sistem kullanıcının oturum süresini gereksiz uzatmaz. Bilişsel dikkat eğrisine (ultradian rhythm) uygun olarak tasarlanmış **20 dakikalık 4 fazlı akış**:

```text
+─────────────────────────────────────────────────────────────────────────────+
|               20 DAKİKALIK GÜNLÜK BİLİŞSEL GELİŞİM AKIŞI                    |
+─────────────────────────────────────────────────────────────────────────────+
|                                                                             |
|  FAZ 1: ZİHNİ GÜÇLENDİRME & ARALIKLI ÇAĞRIM (3-4 Dakika)                    |
|  - Hedef: Unutulma riski (%10) eşiğine gelen eski düğümleri kurtarma.       |
|  - Görev: 2 adet hızlı prosedürel tekrar sorusu (farklı katsayılarla).      |
|                                                                             |
|  FAZ 2: YENİ KAVRAM EDİNİMİ & ÇÖZÜMLÜ ÖRNEKLER (7-8 Dakika)                 |
|  - Hedef: Graf üzerindeki yeni ZPD düğümünü açma.                           |
|  - Görev: 1 Productive Failure sezgisel denemesi + 1 Geriye Eksiltilmiş     |
|    (Faded) çözümlü örnek.                                                   |
|                                                                             |
|  FAZ 3: DERİN PROBLEM ÇÖZME & HATA ONARIMI (5-6 Dakika)                     |
|  - Hedef: Kavramsal şemayı bağımsız yürütmeye dönüştürme.                   |
|  - Görev: 2 bağımsız problem + Adım bazlı hata tespiti ve Sokratik yönlendirme|
|                                                                             |
|  FAZ 4: ARAYA EKLEME & UZAK TRANSFER (2-3 Dakika)                           |
|  - Hedef: Yöntem ayrıştırma ve şablon ezberini kırma.                       |
|  - Görev: 1 karma soru (Önceki konularla harmanlanmış strateji seçimi).     |
|                                                                             |
+─────────────────────────────────────────────────────────────────────────────+
| SEANS SONU BİLİŞSEL KAZANIM KARTI (30 Saniye):                              |
| "Bugün: 2 eski hafıza güçlendirildi, 'Sıfır Çarpım İlkesi' kilidi açıldı,  |
|  Kalibrasyon doğruluğunuz %88'e yükseldi. Yarın görüşmek üzere!"            |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 3. PROBLEM ÇÖZÜM TAHTASI (THE INTERACTIVE SCRATCHPAD)

Mobilde ve webde matematik yazma sürtünmesini (LaTeX bariyeri) ortadan kaldıran özel **Adım Bazlı Çözüm Tahtası**:

```text
+-----------------------------------------------------------------------------+
| PROBLEM:  2x² + 5x - 3 = 0  denkleminin köklerini bulunuz.                  |
|                                                                             |
| Bu sorudan ne kadar eminsin?  [ %25 ]  [ %50 ]  [● %75 ]  [ %100 ]          |
+-----------------------------------------------------------------------------+
| [ADIM 1]  (2x - 1)(x + 3) = 0                               [ ✓ Doğrulandı ]|
|                                                                             |
| [ADIM 2]  2x - 1 = 0  VEYA  x + 3 = 0                       [ ✓ Doğrulandı ]|
|                                                                             |
| [ADIM 3]  x = 1/2     VEYA  x = 3                           [ ✕ HATA!      ]|
+-----------------------------------------------------------------------------+
| AI TUTOR YÖNLENDİRMESİ:                                                     |
| "x + 3 = 0 denkleminde 3'ü eşitliğin sağ tarafına geçirirken işaretine      |
|  dikkat ettin mi? Her iki taraftan 3 çıkardığında sağda ne kalır?"         |
|                                                                             |
| [ Hızlı Sembol Girişi ]:  [ x ]  [ ² ]  [ ± ]  [ √ ]  [ = 0 ]  [ Kesir ]    |
| [ ADIMI DÜZELT ]: [ x = -3                                        ] [GÖNDER]|
+-----------------------------------------------------------------------------+
```

---

## 4. BEYİN HARİTASI (THE LIVING BRAIN MAP)

Kullanıcı öğrenme durumunu XP veya altın puanlar şeklinde değil; [04-KNOWLEDGE-AND-PREREQUISITE-GRAPH.md](04-KNOWLEDGE-AND-PREREQUISITE-GRAPH.md) üzerindeki 30 düğümlü gerçek zihinsel ustalık grafı olarak görür:

```text
CEBİR ATLASI (30 DÜĞÜMLÜ YAŞAYAN ŞEMA)
│
├── [✓] Seviye 0: Temel Önkoşullar
│   ├── [✓] [N01] Negatif Sayılarla İşlemler (%98 Usta)
│   └── [✓] [N04] Birinci Dereceden Lineer Denklem Çözme (%96 Usta)
│
├── [●] Seviye 2: İkinci Dereceden Denklem Temelleri (%74 - İnşa Halinde)
│   ├── [✓] [N08] Monik Üçterimlileri Çarpanlara Ayırma (%90 Usta)
│   ├── [✓] [N11] Sıfır Çarpım Kuralı (%88 Usta)
│   ├── [✓] [N12] Çarpanlara Ayırma ile Çözüm (%85 Usta)
│   └── [!] [N18] Kuadratik Formül Standart Uygulaması (%62 - Geliştirilmeli)
│           ├── Kapı 1 (Çağrım): %95  | Kapı 2 (Prosedür): %70
│           └── Kapı 3 (Strateji Ayrıştırma): %42 (Zayıf Nokta!)
│
└── [ ] Seviye 3: Tam Kareye Tamamlama (Kilitli - Önkoşul [N14] Bekleniyor)

Mevcut Bilişsel Odak & Yönlendirme:
"Kuadratik formülü ezberden doğru yazıyorsun (Kapı 1); ancak hangi denklemde formül,
 hangi denklemde çarpanlara ayırma kullanman gerektiğini ayrıştırmakta (Kapı 3) zorlanıyorsun."
```

---

## 5. ÜRETİCİ BAŞARISIZLIK VE ÇİFT PANELLİ KONSOLİDASYON ARAYÜZÜ (PF DUAL CANVAS UX)

Üretici Başarısızlık aşamasında arayüz, standart soru-cevap modundan çıkarak özel bir **Keşif ve Karşılaştırma Laboratuvarı'na** dönüşür:

### 5.1. Keşif Modu Arayüzü (Exploration Mode)
```text
+-----------------------------------------------------------------------------+
| [ROZET: 🛡️ KEŞİF MODU - PUAN CEZASI YOKTUR - SERBEST DENEYİNİZ]              |
| GÖREV: x² + 6x - 2 = 0 denklemini çözmek için en az 2 farklı yöntem üretin. |
+-----------------------------------------------------------------------------+
| [SEKME 1: Cebir Karoları]   [SEKME 2: Grafik/Parabol]   [SEKME 3: Serbest Çözüm]
|                                                                             |
| +-------------------------+ +---------------------------------------------+ |
| |        x           3    | | [Öğrencinin Çözüm Girişi]                   | |
| |    +-------+     +---+  | |                                             | |
| |  x |  x²   |   x |3x |  | |  1. Denemem: x(x + 6) = 2                   | |
| |    +-------+     +---+  | |     Buradan x = 2 olabilir.                 | |
| |                         | |                                             | |
| |    +-------+     +---+  | |  2. Denemem: Karolarla kare yapmaya        | |
| |  3 |  3x   |   3 | ? |  | |     çalıştım ama köşesi boş kaldı!          | |
| |    +-------+     +---+  | |                                             | |
| +-------------------------+ +---------------------------------------------+ |
| [ + YENİ BİR FİKİR EKLE ]                   [ FİKİRLERİMİ AI TUTOR'A SUN ]  |
+-----------------------------------------------------------------------------+
```

### 5.2. Konsolidasyon Çift Paneli (Contrasting Cases Dual View)
Konsolidasyon aşamasına geçildiğinde ekran ikiye bölünür (Split Screen):

```text
+───────────────────────────────────────┬─────────────────────────────────────+
| SOL PANEL: SENİN DENEMELERİN (SGR)    │ SAĞ PANEL: KANONİK BİRLEŞTİRME      |
+───────────────────────────────────────┼─────────────────────────────────────+
| ❌ Fikir 1: x(x+6) = 2                │ 💡 AI Tutor Sentezi:                |
|    "Çarpımları 2 olan sonsuz reel sayı│ "Geometrik denemende gördüğün gibi: |
|     vardır. Sağ taraf 0 olmadan       │  x² + 6x ifadesini tam bir kare     |
|     çarpanlar ayrılamaz."             │  yapmak için köşeye 9 eklemeliyiz!  |
|                                       │                                     |
| ⭐ Fikir 2: Eksik Geometrik Köşe       │     x² + 6x + 9 = 2 + 9             |
|    "x² yanına iki adet 3x koydun.     │     (x + 3)² = 11                   |
|     Köşedeki 3x3 = 9 boşluğunu        │                                     |
|     doğru fark ettin!"                │  Eksik parçayı ekleyerek denklemi   |
|                                       │  kareye tamamladık!"                |
+───────────────────────────────────────┴─────────────────────────────────────+
```

### 5.3. Afektif Güvenlik Modalı (Anti-Thrashing / Circuit Breaker Overlay)
Öğrenci öfke tıklaması ($F_{\text{score}} \ge 0.85$) sergilediğinde arayüz ekranı karartır ve yumuşak, animasyonlu bir nefes dairesi ile şu modalı açar:

```text
+-----------------------------------------------------------------------------+
|                             🌿 BİR NEFES VERELİM                             |
|                                                                             |
|      Bu soru gerçekten çok çetin bir düğüm içeriyor. Yalnız değilsin;       |
|      tarihte matematikçiler de bu noktada yüzlerce yıl zorlandı.            |
|                                                                             |
|      Senin çaban ve 2 farklı denemen sistemimiz tarafından takdir edildi.   |
|      Hiçbir puan kaybın yok.                                                |
|                                                                             |
|      [ Birlikte Çözelim (Çözümlü Örnek) ]        [ 5 Dakika Mola Ver ]      |
+-----------------------------------------------------------------------------+
```
