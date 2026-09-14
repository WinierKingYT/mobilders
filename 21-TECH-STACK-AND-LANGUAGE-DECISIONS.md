# 21-TECH-STACK-AND-LANGUAGE-DECISIONS.md
# TEKNOLOJİ YIĞINI VE PROGRAMLAMA DİLİ KARARLARI (TECH STACK & LANGUAGE DECISIONS)
## Karşılaştırmalı Mobil Dil Analizi, Hibrit Mimari Katmanları, Kütüphaneler ve Dizin Yapısı

---

## 1. MİMARİ KARAR GEREKÇESİ (ARCHITECTURE DECISION RECORD - ADR-001)

### Karar Başlığı:
**Kişisel Öğrenme Motoru İçin Mobil Öncelikli (Flutter + Python Çekirdek) Nöro-Sembolik Teknoloji Yığını**

### Bağlam:
Sistem, akıllı telefon form faktöründe ($390 \times 844$ dikey yönelim) üç farklı doğadaki görevi eşzamanlı olarak yerine getirmek zorundadır:
1. **Yüksek Performanslı Mobil İstemci (Flutter):** 60/120 FPS akıcı kanvas çizimi (Al-Harezmi alan karoları ve dinamik paraboller), çift modlu matematiksel girdi (Özel Dokunmatik Tuş Takımı / Serbest Klavye geçişi) ve düşük sürtünmeli dikey ergonomi.
2. **Deterministik Sembolik Matematik ve Bilişsel Backend (Python 3.11):** Cebirsel adımların SymPy AST analizi, bozuk kural (Buggy Rules) tespiti, DDM diferansiyel denklemleri ve 2PL-IRT CAT seviye tayini.
3. **Düşük Gecikmeli Mobil API İletişimi:** Her matematiksel adımın mobilden sunucuya iletilip $<180\text{ ms}$ sürede doğrulanarak dokunsal (haptik) geri bildirimle ekrana yansıtılması.

---

## 2. MOBİL PROGRAMLAMA DİLLERİ KARŞILAŞTIRMA VE SEÇİM MATRİSİ

### A. Mobil İstemci Çerçevesi (Mobile Client Framework) Seçimi

| Kriter | Flutter (Dart 3.x) | React Native (TypeScript) | Saf Yerel (Swift & Kotlin) | Web / PWA |
| :--- | :---: | :---: | :---: | :---: |
| **Grafik & Kanvas Performansı** | ⭐⭐⭐⭐⭐ (Impeller Motoru / 120 FPS) | ⭐⭐⭐ (Bridge / Fabric gecikmesi) | ⭐⭐⭐⭐⭐ (Metal / Vulkan) | ⭐⭐ (Mobil tarayıcı kısıtları) |
| **Özel Matematik Klavyesi (Touchpad)** | ⭐⭐⭐⭐⭐ (Hafif ve tam özelleştirilebilir) | ⭐⭐⭐⭐ (Third-party bağımlılığı) | ⭐⭐⭐⭐⭐ (Tam yerel kontrol) | ⭐⭐⭐ (Sanal klavye çakışmaları) |
| **Girdi Modu Değiştirme (Çift Mod)** | ⭐⭐⭐⭐⭐ (Anlık ve titreşimsiz geçiş) | ⭐⭐⭐ (Layout shift riski) | ⭐⭐⭐⭐⭐ (Mükemmel) | ⭐⭐ (Viewport kayma sorunu) |
| **Geliştirme Hızı & Tek Kod Tabanı** | ⭐⭐⭐⭐⭐ (iOS & Android %100 ortak) | ⭐⭐⭐⭐⭐ (Ortak JS kod tabanı) | ⭐ (İki ayrı ekip ve kod tabanı) | ⭐⭐⭐⭐⭐ (Tek web kodu) |
| **Dokunsal Geri Bildirim (Haptics)** | ⭐⭐⭐⭐⭐ (`HapticFeedback` yerel API) | ⭐⭐⭐⭐ (Modül bağımlılığı) | ⭐⭐⭐⭐⭐ (CoreHaptics) | ⭐ (Mobil webde zayıf/desteksiz) |
| **Çevrimdışı Çalışma & Yerel Önbellek** | ⭐⭐⭐⭐⭐ (Isar / Hive / SQLite) | ⭐⭐⭐⭐ (WatermelonDB / MMKV) | ⭐⭐⭐⭐⭐ (CoreData / Room) | ⭐⭐⭐ (IndexedDB kısıtları) |
| **NİHAİ KARAR** | **SEÇİLDİ (KAZANAN) ✅** | Elendi (Kanvas/animasyon sürtünmesi) | Elendi (İki kat maliyet) | Elendi (Mobil deneyim yetersiz) |

> **Karar:** Mobil istemci **Flutter (Dart 3.x)** olarak kilitlenmiştir. Flutter'ın donanım hızlandırmalı Impeller grafik motoru; cebirsel alan karolarını birleştiren animasyonlar, dinamik parabol morflamaları ve çift modlu matematik giriş takımı için benzersiz bir akıcılık sağlar.

---

### B. Backend & Matematiksel CAS Katmanı Seçimi

| Kriter | Python 3.11+ (FastAPI) | Go (Golang) | Node.js (TypeScript) | Rust |
| :--- | :---: | :---: | :---: | :---: |
| **Sembolik Matematik (CAS)** | ⭐⭐⭐⭐⭐ (SymPy / Dünya Standardı) | ⭐ (Yetersiz / Kütüphane Yok) | ⭐⭐ (Math.js zayıf / eksik) | ⭐⭐ (Sembolik ekosistem ham) |
| **Psikometri & İstatistik** | ⭐⭐⭐⭐⭐ (NumPy, SciPy, PyMC) | ⭐⭐ (Temel istatistik) | ⭐ (Ciddi kütüphane yok) | ⭐⭐⭐ (Gelişmekte) |
| **Tip Güvenliği & Şema** | ⭐⭐⭐⭐ (Pydantic v2 / Rust Tabanlı) | ⭐⭐⭐⭐⭐ (Statik tip) | ⭐⭐⭐⭐ (TypeScript / Zod) | ⭐⭐⭐⭐⭐ (Mükemmel) |
| **Gecikme & Eşzamanlılık** | ⭐⭐⭐⭐ (AsyncIO / >15k req/s) | ⭐⭐⭐⭐⭐ (Goroutines) | ⭐⭐⭐⭐ (Event Loop) | ⭐⭐⭐⭐⭐ (Sıfır maliyet) |
| **LLM & AI Entegrasyonu** | ⭐⭐⭐⭐⭐ (Resmi google-genai SDK) | ⭐⭐⭐ (İkincil SDK) | ⭐⭐⭐⭐ (JS SDK) | ⭐⭐ (Topluluk sarmalayıcıları) |
| **NİHAİ KARAR** | **SEÇİLDİ (KAZANAN) ✅** | Elendi (CAS desteği yok) | Elendi (Sembolik CAS yok) | Elendi (Gereksiz karmaşıklık) |

> **Karar:** Backend çekirdeği **Python 3.11+ ve FastAPI** olarak kilitlenmiştir. SymPy motoru ile cebirsel adımların matematiksel eşdeğerliği ve bozuk kurallar deterministik olarak analiz edilir.

---

## 3. SEÇİLEN TEKNOLOJİ YIĞINI BİLEŞENLERİ (THE MOBILE FULL-STACK SPEC)

```text
+─────────────────────────────────────────────────────────────────────────────+
|                        MOBİL TEKNOLOJİ YIĞINI                               |
+─────────────────────────────────────────────────────────────────────────────+
| [ MOBİL İSTEMCİ / FLUTTER ]                                                 |
| - Dil: Dart 3.3+ (Sound Null Safety)                                        |
| - Çerçeve: Flutter 3.19+ (iOS & Android Native)                              |
| - Durum Yönetimi: flutter_riverpod (Reaktif, test edilebilir ve güvenli)    |
| - Matematik Render: flutter_math_fork (Yüksek hızlı TeX/LaTeX render)        |
| - Girdi Mimarisi (Çift Modlu Giriş):                                        |
|     * Mod A: Özel Dokunmatik Tuş Takımı (Math Touchpad - Grid Layout)       |
|     * Mod B: Serbest Sistem Klavyesi (ASCII / LaTeX Sözdizim Dönüştürücü)   |
| - Vektör & Kanvas Çizim: CustomPainter + RepaintBoundary (Alan Karoları)   |
| - Yerel Önbellek & Olay Kuyruğu: Isar Database / SQLite (Çevrimdışı adım)   |
| - Dokunsal Geri Bildirim: HapticFeedback (Doğru adımda hafif, hatada tok)   |
+─────────────────────────────────────────────────────────────────────────────+
                                       │ (REST API & WebSockets / JSON)
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
| [ SUNUCU / BACKEND CORE ]                                                   |
| - Dil: Python 3.11+                                                         |
| - Web Çerçevesi: FastAPI (Uvicorn / AsyncIO)                                |
| - Şema Doğrulama: Pydantic v2 (Rust tabanlı yüksek hızlı tip denetimi)       |
| - Sembolik CAS: SymPy 1.13+ (AST Ziyaretçisi, Bozuk Kural Dedektörü)        |
| - İstatistik & Psikometri: NumPy 1.26+, SciPy 1.12+ (DDM, IRT, BKT)         |
| - Çoklu İşlem Sandbox'ı: Python `multiprocessing` (500ms timeout / memlimit)|
| - Yapay Zeka SDK: Resmi Google GenAI Python SDK (`google-genai`)            |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
| [ VERİ TABANI VE DURUM KATMANI ]                                            |
| - Olay Deposu (Event Store): PostgreSQL 15+ (Append-Only Events, JSONB)     |
| - Hızlı Önbellek & Durum: Redis 7.2+ (ZPD düğüm kümeleri, Seans TTL)        |
| - ORM / Veri Erişimi: SQLAlchemy 2.0 (Async) + Alembic                      |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
| [ TEST VE KALİTE GÜVENCESİ (QA) ]                                           |
| - Mobil Test: Flutter Driver, flutter_test (Widget & Unit), ARTEMIS MCP     |
| - Backend Test: PyTest 8.0+, pytest-asyncio, Hypothesis (Property Testing)  |
| - Statik Analiz: `dart analyze`, Ruff (Python linter/formatter)             |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 4. MOBİL ÇİFT MODLU GİRDİ (DUAL-MODE INPUT) MİMARİSİ

Öğrencinin bilişsel stiline ve anlık tercihine göre giriş modunu değiştirebilmesi için ayrık iki arayüz katmanı tanımlanmıştır:

```text
+───────────────────────────────────────────────────────────────────+
|                  GİRDİ ALANI SEÇİCİ KONTROLÜ                      |
|       [ 🧮 Matematik Tuş Takımı ]   |   [ ⌨️ Serbest Klavye ]      |
+───────────────────────────────────────────────────────────────────+

  [ MOD A: ÖZEL MATEMATİK TUŞ TAKIMI (TOUCHPAD) ]
  ┌─────┬─────┬─────┬─────┬─────────┐
  │  x  │ x²  │  √  │  ±  │   DEL   │
  ├─────┼─────┼─────┼─────┼─────────┤
  │  7  │  8  │  9  │  (  │    )    │
  ├─────┼─────┼─────┼─────┼─────────┤
  │  4  │  5  │  6  │  +  │    -    │
  ├─────┼─────┼─────┼─────┼─────────┤
  │  1  │  2  │  3  │  =  │ ADIM AT │
  ├─────┴─────┼─────┼─────┴─────────┤
  │     0     │  /  │    GÖNDER     │
  └───────────┴─────┴───────────────┘
  * Avantajı: Tek dokunuşla formül inşası, sözdizimi hatası sıfıra yakın.

  [ MOD B: SERBEST SİSTEM KLAVYESİ ]
  ┌─────────────────────────────────────────────────────────────────┐
  │ [ Girdi Kutusu: x^2 + 6x = 2                                  ] │
  │ ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐                     │
  │ │ q │ w │ e │ r │ t │ y │ u │ i │ o │ p │  (Standart iOS/       │
  │ └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘   Android Klavyesi)  │
  └─────────────────────────────────────────────────────────────────┘
  * Avantajı: Hızlı klavye kullanan veya harici klavye bağlayanlar için özgürlük.
  * Parser: `^` işaretini otomatik `**` üs işlemine, `x2` yazımını `x^2`ye tamamlar.
```

### 4.1 Örtük Çarpma ve Mobil Ayrıştırma Motoru (Implicit Multiplication Engine)
Mobil cihazda çarpı (`*`) işaretine sürekli basmak yüksek arayüz sürtünmesi yarattığından, Flutter istemcisi ve FastAPI sunucusu giriş metnini AST'ye sokmadan önce şu regex/token kurallarını deterministik uygular:
1. **Katsayı ve Değişken Eşlemesi:** `([0-9]+)([a-zA-Z])` $\implies$ `$1*$2` (Ör: `2x` $\to$ `2*x`, `6x` $\to$ `6*x`).
2. **Parantez Çarpımları:** `(\))(\()|([0-9a-zA-Z])(\()|(\))([0-9a-zA-Z])` $\implies$ `$1*$2` (Ör: `(x+3)(x-2)` $\to$ `(x+3)*(x-2)`, `3(x+1)` $\to$ `3*(x+1)`).
3. **Çoklu Değişken Terimleri:** `4ac` $\implies$ `4*a*c` (Kuadratik formül diskriminant girdilerinde).
4. **Boşluksuz Üs Dönüşümü:** `x2` veya `x^2` $\implies$ `x**2`.
Bu sayede öğrenci telefonda kağıda yazar gibi doğal cebirsel notasyon kullanır; sistem hiçbir sembolik anlam kaybı olmadan adımı SymPy uyumlu kanonik hale getirir.


---

## 5. PROJE DİZİN VE MODÜL MİMARİSİ (FLUTTER + FASTAPI)

```text
uyugulama1/
├── README.md                                # Ana proje indeksi ve genel mimari
├── ROADMAP.md                               # Geliştirme fazları ve DoD kapıları
├── Referans/                                # 18 Referans Şartname Dokümanı
│   ├── 00-PROJECT-VISION.md ... 17-GAPS.md
├── 18-FOUNDATION-GOALS-AND-DEFINITION-OF-DONE.md # Bitiş kriterleri ve kabul kapıları
├── 19-APPLICATION-FLOW-AND-USER-JOURNEY.md  # Mobil oturum durum makinesi
├── 20-UI-UX-DESIGN-SYSTEM-AND-WIREFRAMES.md # Akıllı telefon dikey wireframeleri
├── 21-TECH-STACK-AND-LANGUAGE-DECISIONS.md  # Bu doküman (Mobil teknoloji yığını)
│
├── apps/
│   └── mobile/                              # Flutter Mobil Uygulaması (iOS & Android)
│       ├── lib/
│       │   ├── core/                        # Tema, renkler, haptik servis, ağ istemcisi
│       │   ├── features/
│       │   │   ├── diagnostic/              # 2PL-IRT CAT seviye tespit ekranı
│       │   │   ├── session/                 # 20 dakikalık günlük seans FSM
│       │   │   ├── scratchpad/              # Karalama defteri & kanvas çizici
│       │   │   ├── keypad/                  # Çift modlu giriş (Touchpad / Serbest klavye)
│       │   │   ├── visual_models/           # Al-Harezmi alan karoları & dinamik parabol
│       │   │   └── summary/                 # Gün sonu bilişsel özet ve sirkadiyen kilit
│       │   └── main.dart                    # Uygulama giriş noktası
│       └── test/                            # Flutter widget ve unit testleri
│
└── services/
    └── core-engine/                         # Python 3.11 FastAPI Backend
        ├── app/
        │   ├── api/                         # FastAPI router endpointleri
        │   ├── cas/                         # SymPy AST eşdeğerlik ve sandbox
        │   ├── misconceptions/              # 5 Bozuk Kural dedektörü (BUG-QUAD-01..05)
        │   ├── psychometrics/               # iBKT, CT-BKT, Ratcliff DDM, Wald SPRT
        │   ├── adaptive/                    # FSM, ZPD Termostatı, Kapur PF motoru
        │   ├── tutor/                       # 4 Katmanlı Sokratik AI ve Sıfır-Sızıntı denetimi
        │   └── models/                      # Pydantic v2 veri şemaları
        └── tests/                           # PyTest test paketi (17 test %100 yeşil)
```

---

## 6. MOBİL VERİ VE ETKİLEŞİM KONTRATI

### Mobil Adım Gönderme İsteği (`POST /api/v1/session/step/verify`)
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "node_id": "N15",
  "step_number": 3,
  "user_expression": "(x + 3)^2 = 11",
  "target_equation": "x^2 + 6*x - 2 = 0",
  "previous_step": "x^2 + 6*x + 9 = 11",
  "input_mode": "TOUCHPAD",
  "elapsed_ms": 14200,
  "confidence_rating": 0.75
}
```

### Mobil Yanıt ve Dokunsal Tetikleyici (Gecikme $\le 120\text{ ms}$)
```json
{
  "is_valid": true,
  "is_target_reached": false,
  "detected_bug": null,
  "canonical_expression": "(x + 3)**2 - 11",
  "haptic_feedback": "LIGHT_IMPACT",
  "analysis_latency_ms": 8.4,
  "socratic_scaffold": {
    "scaffold_level": 1,
    "hint_text": "Harika bir tam kare oluşturdun. Şimdi her iki tarafın karekökünü almayı deneyebilir misin?"
  }
}
```
