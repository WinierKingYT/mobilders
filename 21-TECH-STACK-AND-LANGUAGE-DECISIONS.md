# 21-TECH-STACK-AND-LANGUAGE-DECISIONS.md
# TEKNOLOJİ YIĞINI VE PROGRAMLAMA DİLİ KARARLARI (TECH STACK & LANGUAGE DECISIONS)
## Karşılaştırmalı Dil Analizi, Mimari Katmanlar, Kütüphane Bağımlılıkları ve Dizin Yapısı

---

## 1. MİMARİ KARAR GEREKÇESİ (ARCHITECTURE DECISION RECORD - ADR-001)

### Karar Başlığı:
**Kişisel Öğrenme Motoru İçin Hibrit Nöro-Sembolik Teknoloji Yığını Seçimi**

### Bağlam:
Sistem üç farklı doğadaki görevi eşzamanlı olarak yerine getirmek zorundadır:
1. **Deterministik Sembolik Matematik ve Psikometri:** Cebirsel adımların AST analizi, DDM diferansiyel denklemleri, 2PL-IRT matris işlemleri.
2. **Yüksek Performanslı ve Düşük Gecikmeli Web API:** Kullanıcının her adımını $<180\text{ ms}$ sürede doğrulayan olay güdümlü backend.
3. **Zengin ve Düşük Sürtünmeli İstemci Arayüzü:** Matematiksel klavye (MathLive), dinamik SVG alan karoları, parabol animasyonları ve interaktif graf ağları.

---

## 2. PROGRAMLAMA DİLLERİ KARŞILAŞTIRMA VE SEÇİM MATRİSİ

### A. Backend & Matematiksel CAS Katmanı Seçimi

| Kriter | Python 3.11+ (FastAPI) | Go (Golang) | Node.js (TypeScript) | Rust |
| :--- | :---: | :---: | :---: | :---: |
| **Sembolik Matematik (CAS)** | ⭐⭐⭐⭐⭐ (SymPy / Dünya Standardı) | ⭐ (Yetersiz / Kütüphane Yok) | ⭐⭐ (Math.js zayıf / eksik) | ⭐⭐ (Sembolik ekosistem ham) |
| **Psikometri & İstatistik** | ⭐⭐⭐⭐⭐ (NumPy, SciPy, PyMC) | ⭐⭐ (Temel istatistik) | ⭐ (Ciddi kütüphane yok) | ⭐⭐⭐ (Gelişmekte) |
| **Tip Güvenliği & Şema** | ⭐⭐⭐⭐ (Pydantic v2 / Rust Tabanlı) | ⭐⭐⭐⭐⭐ (Statik tip) | ⭐⭐⭐⭐ (TypeScript / Zod) | ⭐⭐⭐⭐⭐ (Mükemmel) |
| **Gecikme & Eşzamanlılık** | ⭐⭐⭐⭐ (AsyncIO / >15k req/s) | ⭐⭐⭐⭐⭐ (Goroutines) | ⭐⭐⭐⭐ (Event Loop) | ⭐⭐⭐⭐⭐ (Sıfır maliyet) |
| **LLM & AI Entegrasyonu** | ⭐⭐⭐⭐⭐ (Resmi google-genai SDK) | ⭐⭐⭐ (İkincil SDK) | ⭐⭐⭐⭐ (JS SDK) | ⭐⭐ (Topluluk sarmalayıcıları) |
| **NİHAİ KARAR** | **SEÇİLDİ (KAZANAN) ✅** | Elendi (CAS desteği yok) | Elendi (Sembolik CAS yok) | Elendi (Gereksiz karmaşıklık) |

> **Karar:** Backend çekirdeği **Python 3.11+ ve FastAPI** olarak kilitlenmiştir. SymPy olmadan cebirsel eşdeğerliği ve bozuk kuralları deterministik analiz etmek imkansızdır. Pydantic v2'nin Rust tabanlı serileştirmesiyle milisaniye altı veri doğrulama sağlanır.

---

### B. Frontend ve Arayüz Katmanı Seçimi

| Kriter | TypeScript / Next.js 14 | TypeScript / Vite + React | SvelteKit | Flutter Web |
| :--- | :---: | :---: | :---: | :---: |
| **Matematiksel Klavye (MathLive)** | ⭐⭐⭐⭐⭐ (Mükemmel Web Component) | ⭐⭐⭐⭐⭐ (İyi) | ⭐⭐⭐ (Entegrasyon pürüzlü) | ⭐ (Web'de DOM/Canvas sorunu) |
| **İnteraktif Graf (React Flow)** | ⭐⭐⭐⭐⭐ (Endüstri standardı) | ⭐⭐⭐⭐⭐ (İyi) | ⭐⭐ (Svelte Flow zayıf) | ⭐ (Hazır kütüphane yok) |
| **İlk Yükleme Hızı (FCP / TTI)** | ⭐⭐⭐⭐⭐ (SSR/SSG ile <1.2s) | ⭐⭐⭐ (SPA gecikmesi) | ⭐⭐⭐⭐⭐ (Hızlı) | ⭐ (Canvas yüklemesi >4s) |
| **PWA & Dokunmatik Ergonomi** | ⭐⭐⭐⭐⭐ (Tam uyumlu) | ⭐⭐⭐⭐ (İyi) | ⭐⭐⭐⭐ (İyi) | ⭐⭐⭐ (Ağır paket) |
| **NİHAİ KARAR** | **SEÇİLDİ (KAZANAN) ✅** | Elendi (SSR avantajı yok) | Elendi (Ekosistem darlığı) | Elendi (Web performansı zayıf) |

> **Karar:** Frontend **TypeScript ve Next.js 14 (App Router)** olarak kilitlenmiştir. Tailwind CSS, shadcn/ui bileşenleri, MathLive ve React Flow ile tam entegre çalışır.

---

## 3. SEÇİLEN TEKNOLOJİ YIĞINI BİLEŞENLERİ (THE FULL STACK SPEC)

```text
+─────────────────────────────────────────────────────────────────────────────+
|                                TEKNOLOJİ YIĞINI                             |
+─────────────────────────────────────────────────────────────────────────────+
| [ İSTEMCİ / FRONTEND ]                                                      |
| - Dil: TypeScript 5.4+                                                      |
| - Çerçeve: Next.js 14 (App Router, Server Components, PWA)                 |
| - Stil: Tailwind CSS 3.4+ & shadcn/ui (Radix UI tabanlı)                    |
| - Matematik Girişi: MathLive (LaTeX Sanal Klavye & Web Component)          |
| - Matematik Render: KaTeX (Yüksek hızlı LaTeX render)                       |
| - Görsel Temsiller: Lucide Icons, SVG Canvas, Dinamik Parabol Çizici        |
| - Bilgi Grafı: React Flow 11+ (Cebir Atlası DAG Görselleştirici)            |
+─────────────────────────────────────────────────────────────────────────────+
                                       │ (REST API & WebSockets / JSON)
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
| [ SUNUCU / BACKEND CORE ]                                                   |
| - Dil: Python 3.11+                                                         |
| - Web Çerçevesi: FastAPI (Uvicorn / Starlette / AsyncIO)                    |
| - Şema Doğrulama: Pydantic v2 (Rust motorlu yüksek hızlı tip denetimi)      |
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
| - Hızlı Önbellek & Durum: Redis 7.2+ (ZPD düğüm kümeleri, Rate Limiter)     |
| - ORM / Veri Erişimi: SQLAlchemy 2.0 (Async) + Alembic                      |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
| [ TEST VE KALİTE GÜVENCESİ (QA) ]                                           |
| - Backend Test: PyTest 8.0+, pytest-asyncio, Hypothesis (Property Testing)  |
| - Frontend Test: Vitest, React Testing Library, Playwright (E2E)            |
| - Statik Analiz: Ruff (Python linter/formatter), ESLint, Prettier           |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 4. PROJE DİZİN VE MODÜL MİMARİSİ (MONOREPO / CLEAN ARCHITECTURE)

Proje, bağımlılıkları temiz tutan modüler bir mimaride organize edilir:

```text
uyugulama1/
├── README.md                                # Ana proje indeksi ve genel mimari
├── ROADMAP.md                               # Geliştirme fazları ve DoD kapıları
├── 00-PROJECT-VISION.md ... 17-GAPS.md      # 18 Referans Şartname Dokümanı
├── 18-FOUNDATION-GOALS-AND-DOD.md           # Bitiş kriterleri ve kabul kapıları
├── 19-APPLICATION-FLOW-AND-USER-JOURNEY.md  # Oturum durum makinesi ve kullanıcı akışı
├── 20-UI-UX-DESIGN-SYSTEM-AND-WIREFRAMES.md # Ekran şemaları ve tasarım sistemi
├── 21-TECH-STACK-AND-LANGUAGE-DECISIONS.md  # Teknoloji yığını ve dil şartnamesi
│
├── apps/
│   └── web/                                 # Next.js 14 İstemci Uygulaması
│       ├── app/                             # App Router sayfaları (teşhis, seans, atlas)
│       ├── components/
│       │   ├── scratchpad/                  # MathLive çözüm tahtası ve adım kartları
│       │   ├── canvas/                      # Al-Harezmi SVG karoları ve dinamik parabol
│       │   ├── brain-map/                   # React Flow Cebir Atlası
│       │   └── circuit-breaker/             # Şefkatli Mola modalı
│       └── lib/                             # API istemcisi, WebSocket köprüsü
│
└── services/
    └── core-engine/                         # Python 3.11 FastAPI Backend
        ├── app/
        │   ├── api/                         # FastAPI router endpointleri
        │   ├── cas/                         # SymPy AST eşdeğerlik ve sandbox
        │   ├── misconceptions/              # 5 Buggy Rule dedektörleri (BUG-QUAD-01..05)
        │   ├── psychometrics/               # iBKT, CT-BKT, Ratcliff DDM, Wald SPRT
        │   ├── adaptive/                    # FSM, ZPD Termostatı, Kapur PF motoru
        │   ├── tutor/                       # 4 Katmanlı Sokratik AI ve Zero-Leak Regex
        │   └── models/                      # Pydantic v2 veri şemaları ve DDL
        └── tests/
            ├── cas/                         # 500 Sentetik cebirsel doğrulama testleri
            ├── misconceptions/              # Bozuk kural yakalama testleri
            ├── psychometrics/               # Monte Carlo CAT ve BKT testleri
            └── security/                    # 100 Adversarial jailbreak testleri
```

---

## 5. API İLETİŞİM PROTOKOLÜ VE VERİ KONTRATI (CONTRACTS)

### Adım Doğrulama İsteği (`POST /api/v1/session/step/verify`)
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "node_id": "N15",
  "step_number": 3,
  "raw_latex": "(x + 3)^2 = 11",
  "elapsed_ms": 14200,
  "keystroke_entropy": 0.42,
  "confidence_rating": 0.75
}
```

### Adım Doğrulama Yanıtı (Gecikme $\le 120\text{ ms}$)
```json
{
  "is_valid": true,
  "is_target_reached": false,
  "detected_bug": null,
  "canonical_form": "(x + 3)**2 - 11",
  "bkt_p_learned": 0.68,
  "ddm_drift_rate": 1.45,
  "scaffold_directive": {
    "current_level": 1,
    "next_prompt": "Şimdi her iki tarafın karekökünü alabilir misin?",
    "highlight_token": "ROOT_EXTRACTION"
  }
}
```
