# 16-TECHNICAL-ARCHITECTURE-OPTIONS.md
# TEKNİK MİMARİ VE SİSTEM TOPOLOJİSİ (TECHNICAL ARCHITECTURE)
## Nöro-Sembolik Teknoloji Yığını, Olay Kaynağı (Event Sourcing), CAS Yürütme Mimarisi ve Veri Tabanı Şemaları

---

## 1. YÜKSEK SEVİYELİ SİSTEM TOPOLOJİSİ (SYSTEM TOPOLOGY)

Sistem mimarisi, deterministik matematiksel doğrulama ile üretken yapay zekayı mikroservis sınırları içinde izole eden **Nöro-Sembolik Çift Katman (Neuro-Symbolic Dual Stack)** prensibiyle tasarlanmıştır:

```text
+─────────────────────────────────────────────────────────────────────────────+
|                         İSTEMCİ KATMANI (CLIENT LAYER)                      |
|  - BİRİNCİL (PRIMARY): Mobil İstemci (Flutter 3.19+ / Dart 3.3+ / Impeller)  |
|    * Dikey Başparmak Ergonomisi ($390 \times 844$), Çift Modlu Tuş Takımı   |
|    * CustomPainter Donanım Hızlandırmalı Karo & Dinamik Parabol             |
|    * Isar / SQLite Çevrimdışı Adım Önbelleği & Yerel AST Sanity             |
|  - İKİNCİL / B PLANI: Masaüstü Web & PWA (Next.js 14 / React 18 / MathLive) |
|    * Geniş ekran analiz panelleri ve masaüstü araştırmacı erişimi           |
+─────────────────────────────────────────────────────────────────────────────+
                                       │  HTTPS / WebSocket / SSE
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
|                     UYGULAMA VE ORKESTRASYON KATMANI                        |
|  - API Gateway & Oturum Yöneticisi (FastAPI / Python 3.11+ / Uvicorn)       |
|  - Pedagojik FSM Karar Motoru (Finite State Machine State Reducer)          |
|  - Adaptif CAT Teşhis Servisi (SciPy / NumPy 2PL IRT Modülü)                |
|  - BKT & FSRS Aralıklı Tekrar Servisi (Asenkron Celery / Redis Queue)       |
+─────────────────────────────────────────────────────────────────────────────+
           │                                                │
           ▼ (Deterministik Doğrulama)                      ▼ (Pedagojik Tercüme)
+──────────────────────────────+               +──────────────────────────────+
|   SEMBOLİK CEBİR SERVİSİ     |               |    AI TUTOR ORKESTRATÖRÜ     |
|   (CAS Core / SymPy Service) |               |  (LLM Inference Pipeline)    |
| - AST Ayrıştırma ve Normaliz.|               | - Katı Sistem Promptu        |
| - Eşdeğerlik Kontrolü        |               | - JSON Şema Filtresi         |
| - Deterministik Hata Eşleme  |               | - Sokratik Yanıt Üretici     |
| - Hard Timeout (500 ms Sandb)|               | - Zero-Leakage Interceptor   |
+──────────────────────────────+               +──────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
|                          VERİ SAKLAMA KATMANI (DATA)                         |
|  - PostgreSQL 15+: Append-Only Event Store, Kullanıcı Master, BKT Ledger    |
|  - In-Memory DAG (NetworkX): 30 Düğümlü Bilgi Grafı topolojisi ve kenarları  |
|  - Redis 7.2+: Aktif oturum durumu, ZPD penceresi, Rate Limiting            |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 2. OLAY GÜDÜMLÜ OLAY KAYNAĞI MİMARİSİ (EVENT-DRIVEN EVENT SOURCING)

Sistemdeki öğrenici durumu (BKT olasılıkları, 5D yetkinlik matrisi, ZPD sınırları), doğrudan veritabanında "üzerine yazılan" (mutable) kayıtlarla değil, değiştirilemez bir **Olay Günlüğü (Append-Only Event Stream)** üzerinden türetilir. Böylece öğrencinin tüm zihinsel evrimi istendiğinde zamanda geriye sarılarak (Event Replay) yeniden oynatılabilir ve analiz edilebilir.

### 2.1. Olay Şemaları (Event Schemas)

#### A. `StepSolved` Olayı
Öğrenci çözüm tahtasında bir adım yazdığında ve bu adım CAS tarafından geçerli/geçersiz olarak doğrulandığında fırlatılır.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "StepSolvedEvent",
  "type": "object",
  "required": [
    "event_id", "event_type", "aggregate_id", "timestamp", "session_id",
    "concept_id", "problem_id", "step_index", "payload"
  ],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "type": "string", "const": "StepSolved" },
    "aggregate_id": { "type": "string", "description": "Öğrenci UUID" },
    "session_id": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "concept_id": { "type": "string", "example": "math.alg.quadratics.factoring" },
    "problem_id": { "type": "string", "example": "prob_quad_042" },
    "step_index": { "type": "integer", "minimum": 1 },
    "payload": {
      "type": "object",
      "required": ["input_latex", "canonical_form", "is_correct", "latency_ms"],
      "properties": {
        "input_latex": { "type": "string", "example": "2x + 3 = 10" },
        "canonical_form": { "type": "string", "example": "2*x + 3 == 10" },
        "is_correct": { "type": "boolean" },
        "error_classification": {
          "type": ["object", "null"],
          "properties": {
            "taxonomy_class": { "type": "string", "example": "PROCEDURAL_DISTRIBUTIVE_SIGN" },
            "root_cause_node": { "type": "string", "example": "math.alg.distributive_property" },
            "severity": { "type": "string", "enum": ["LOW", "MEDIUM", "HIGH"] }
          }
        },
        "latency_ms": { "type": "integer", "description": "Adımın yazılma süresi" },
        "keystroke_count": { "type": "integer" },
        "backspace_count": { "type": "integer" }
      }
    }
  }
}
```

#### B. `HintRequested` Olayı
Öğrenci kendi isteğiyle veya sistem önerisiyle bir ipucu butonuna tıkladığında üretilir.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "HintRequestedEvent",
  "type": "object",
  "required": [
    "event_id", "event_type", "aggregate_id", "timestamp", "session_id",
    "concept_id", "problem_id", "step_index", "payload"
  ],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "type": "string", "const": "HintRequested" },
    "aggregate_id": { "type": "string", "format": "uuid" },
    "session_id": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "concept_id": { "type": "string" },
    "problem_id": { "type": "string" },
    "step_index": { "type": "integer" },
    "payload": {
      "type": "object",
      "required": ["hint_level", "requested_by", "current_fading_level"],
      "properties": {
        "hint_level": { "type": "integer", "minimum": 1, "maximum": 4 },
        "requested_by": { "type": "string", "enum": ["STUDENT_CLICK", "SYSTEM_FREEZE_PROMPT"] },
        "current_fading_level": { "type": "string", "enum": ["WORKED", "FADED", "INDEPENDENT"] },
        "was_imposter_blocked": { "type": "boolean", "description": "İmposter güvence kilidiyle engellendi mi?" }
      }
    }
  }
}
```

#### C. `ConfidenceStated` Olayı
Öğrenci bir adımı veya sonucu göndermeden önce metabilişsel güven derecesini belirlediğinde kaydedilir.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ConfidenceStatedEvent",
  "type": "object",
  "required": [
    "event_id", "event_type", "aggregate_id", "timestamp", "session_id",
    "problem_id", "payload"
  ],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "type": "string", "const": "ConfidenceStated" },
    "aggregate_id": { "type": "string", "format": "uuid" },
    "session_id": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "problem_id": { "type": "string" },
    "payload": {
      "type": "object",
      "required": ["confidence_rating", "elicitation_type"],
      "properties": {
        "confidence_rating": { "type": "number", "minimum": 0.0, "maximum": 1.0, "example": 0.85 },
        "elicitation_type": { "type": "string", "enum": ["PRE_DECISION", "POST_DECISION", "PROBABILISTIC_INTERVAL"] },
        "decision_time_ms": { "type": "integer" }
      }
    }
  }
}
```

---

## 3. CAS YÜRÜTME MİMARİSİ: İSTEMCİ (WASM/PYODIDE) VS. SUNUCU TARAFI PYTHON CAS

Sembolik Cebir Sisteminin (CAS) nerede çalışacağı, kullanıcı gecikmesi (<200ms hedefi), ağ trafiği, sunucu maliyeti ve hile güvenliği açısından kritik bir mimari ayrımdır:

### 3.1. Karşılaştırma Matrisi

| Değerlendirme Kriteri | İstemci Tarafı WASM (Pyodide / SymPy WASM) | Sunucu Tarafı Python CAS (FastAPI / Worker) |
| :--- | :--- | :--- |
| **Gecikme (Latency)** | **Sıfır Ağ Gecikmesi:** Yerel tarayıcıda yürütme ($\sim 30-60\text{ ms}$). | **Ağ + İşlem:** RTT ($\sim 40\text{ ms}$) + SymPy ($\sim 50\text{ ms}$) = **$\sim 90-140\text{ ms}$**. |
| **İlk İndirme Boyutu (Initial Payload)** | **Çok Yüksek:** Pyodide runtime + Python stdlib + SymPy paketi **$\approx 18 - 25\text{ MB}$** WASM/JS indirmesi. | **Sıfır İndirme:** Web istemcisi yalnızca standart React/MathLive paketini indirir ($\approx 350\text{ KB}$). |
| **Soğuk Başlatma (Cold Boot)** | **Yavaş:** Tarayıcıda WASM derleme ve SymPy modül yükleme **$2.5 - 5.0\text{ saniye}$** sürer. | **Anında:** Sunucudaki worker havuzu zaten bellekte sıcaktır ($< 5\text{ ms}$). |
| **Cihaz Uyumluluğu / CPU Yükü** | Düşük segment mobil telefonlarda tarayıcıyı yavaşlatır, batarya tüketir. | Tüm hesaplama yükü buluttadır; telefon yalnızca hafif JSON alır/verir. |
| **Güvenlik ve Hile Koruması (Tamper Proof)** | **Zayıf:** Çözüm mantığı ve doğrulamalar istemcidedir; DevTools ile manipüle edilebilir. | **Yüksek:** Yetkili (Authoritative) hakem sunucudur; BKT durumu güvenle saklanır. |
| **Geliştirme / Debug Kolaylığı** | WASM içinde CPython kütüphanesi hata ayıklaması zordur. | Standart Python unit test, profiling ve izleme araçları tam çalışır. |

### 3.2. Hibrit Mimari Kararı (Tiered CAS Architecture)
Katı gecikme bütçesi ($\le 200\text{ ms}$) ve güvenilirlik için **İki Kademeli Hibrit Model (Tiered Model)** seçilmiştir:

```text
[Kullanıcı MathLive Girişi]
           │
           ├──> [Tier-1: İstemci İçi Anlık Sözdizimi Kontrolü (Client JS/Parser)]
           │    - Süre: < 10 ms
           │    - Kapsam: Parantez dengesi, geçerli LaTeX, boş girdi engeli.
           │    - Sonuç: Buton aktifleşir, anlık görsel geribildirim.
           │
           └──> [Tier-2: Sunucu Tarafı Yetkili CAS Servisi (FastAPI / SymPy Sandboxed)]
                - Süre: ~80-120 ms (Ağ dahil, bütçe < 200 ms)
                - Kapsam: AST Eşdeğerlik, Hata Sınıflandırma, BKT Güncellemesi.
                - Sonuç: Hakiki pedagojik durum geçişi.
```

---

## 4. DURUM YÖNETİMİ VE VERİ TABANI ŞEMALARI (REDIS & POSTGRESQL)

### 4.1. Redis Bellek Ön Belleği (In-Memory Session & Cache Schema)

Redis 7.2+, oturum içi hızlı durum takibi, hız sınırlama ve FSM durumu için kullanılır.

* **Oturum Durumu Anahtarı:** `session:{session_id}:state` (Hash)
  ```text
  HSET session:sess_849204:state
    user_id          "usr_3fa85f64-5717-4562-b3fc-2c963f66afa6"
    current_node     "math.alg.quadratics.factoring"
    fsm_state        "FADED_STEP_2"
    consecutive_err  "1"
    freeze_timer     "1726304520"
    current_problem  "prob_quad_042"
    ttl              "3600"
  ```
* **Kullanıcı ZPD Kümesi:** `user:{user_id}:zpd_nodes` (Set)
  ```text
  SADD user:usr_3fa85f64:zpd_nodes "math.alg.quadratics.factoring" "math.alg.quadratics.zero_product"
  ```
* **Hız Sınırlama (Rate Limiting):** `ratelimit:{user_id}:submit_step` (String / Sliding Window)
  - Limit: Dakikada maksimum 30 adım gönderimi.

---

### 4.2. PostgreSQL 15+ Kalıcı Veri Tabanı DDL Şeması

```sql
-- 1. KULLANICI MASTER TABLOSU (ANONİM KİMLİK)
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pseudonym VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    math_anxiety_level VARCHAR(16) DEFAULT 'NORMAL', -- 'LOW', 'NORMAL', 'HIGH'
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 2. DEĞİŞTİRİLEMEZ OLAY GÜNLÜĞÜ (IMMUTABLE EVENT STORE)
CREATE TABLE learning_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    session_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    sequence_number BIGSERIAL,
    concept_id VARCHAR(128) NOT NULL,
    problem_id VARCHAR(64),
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_learning_events_user_time ON learning_events (aggregate_id, created_at DESC);
CREATE INDEX idx_learning_events_concept ON learning_events (concept_id);
CREATE INDEX idx_learning_events_payload ON learning_events USING GIN (payload);

-- 3. ÖĞRENİCİ USTALIK DEFTERİ (BKT & 5D COMPETENCY LEDGER - DERIVED READ MODEL)
CREATE TABLE learner_mastery_ledger (
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    concept_id VARCHAR(128) NOT NULL,
    p_l NUMERIC(5, 4) NOT NULL DEFAULT 0.1000, -- BKT P(L) Ustalık olasılığı
    uncertainty NUMERIC(5, 4) NOT NULL DEFAULT 0.5000,
    -- 5 Boyutlu Yetkinlik Vektörü
    c_recall NUMERIC(5, 4) NOT NULL DEFAULT 0.1000,
    c_concept NUMERIC(5, 4) NOT NULL DEFAULT 0.1000,
    c_procedure NUMERIC(5, 4) NOT NULL DEFAULT 0.1000,
    c_transfer NUMERIC(5, 4) NOT NULL DEFAULT 0.0500,
    c_metacog NUMERIC(5, 4) NOT NULL DEFAULT 0.5000,
    -- Kalibrasyon ve Tekrar Durumu
    brier_score NUMERIC(5, 4) DEFAULT NULL,
    fsrs_stability NUMERIC(7, 2) NOT NULL DEFAULT 1.00,
    fsrs_difficulty NUMERIC(5, 2) NOT NULL DEFAULT 5.00,
    next_review_at TIMESTAMPTZ DEFAULT NULL,
    mastery_status VARCHAR(24) NOT NULL DEFAULT 'UNTOUCHED', -- 'UNTOUCHED', 'IN_PROGRESS', 'PROVISIONAL', 'MASTERED'
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, concept_id)
);

CREATE INDEX idx_mastery_next_review ON learner_mastery_ledger (user_id, next_review_at) 
WHERE next_review_at IS NOT NULL;

-- 4. BİLGİ GRAFI STATİK ÖNKOŞUL TABLOSU
CREATE TABLE prerequisite_edges (
    source_node VARCHAR(128) NOT NULL,
    target_node VARCHAR(128) NOT NULL,
    edge_type VARCHAR(24) NOT NULL, -- 'STRICT', 'SOFT', 'TRANSFER'
    weight NUMERIC(3, 2) NOT NULL DEFAULT 1.0,
    PRIMARY KEY (source_node, target_node)
);

-- 5. KAVRAM YANILGILARI TELEMETRİ KÜTÜĞÜ
CREATE TABLE misconception_log (
    log_id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    concept_id VARCHAR(128) NOT NULL,
    taxonomy_class VARCHAR(64) NOT NULL,
    expression_latex TEXT NOT NULL,
    remediated BOOLEAN NOT NULL DEFAULT FALSE,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_misconception_user_class ON misconception_log (user_id, taxonomy_class);
```

---

## 5. API SÖZLEŞMELERİ VE GECİKME BÜTÇESİ (PERFORMANCE BUDGET)

### 5.1. Uç Nokta Sözleşmesi: `POST /api/v1/learning/submit-step`

#### İstek (Request)
```json
{
  "session_id": "sess_849204",
  "concept_id": "math.alg.quadratics.factoring",
  "problem_id": "prob_quad_042",
  "step_index": 2,
  "confidence_rating": 0.75,
  "user_input_latex": "2x + 3 = 10",
  "latency_ms": 14200
}
```

#### Yanıt (Response `200 OK`)
```json
{
  "is_valid": false,
  "error_classification": {
    "taxonomy_class": "PROCEDURAL_DISTRIBUTIVE_SIGN",
    "root_cause_node": "math.alg.distributive_property",
    "severity": "MEDIUM"
  },
  "pedagogical_action": {
    "action_type": "SOCRATIC_PROMPT",
    "hint_level": 1,
    "tutor_message": "İlk terim olan 2x'i başarıyla çarptın. Parantez içindeki +3 terimi dıştaki 2 ile çarpıldığında neye dönüşür?",
    "highlight_target": "input_box_step_2"
  },
  "learner_model_update": {
    "concept_id": "math.alg.quadratics.factoring",
    "new_p_l": 0.76,
    "delta_uncertainty": -0.04
  },
  "performance_metrics": {
    "cas_duration_ms": 48,
    "fsm_duration_ms": 12,
    "total_server_time_ms": 65
  }
}
```

### 5.2. Gecikme Bütçesi Dağılımı (Latency Budget Breakdown)

| Alt Sistem Bileşeni | Hedef Gecikme ($P_{50}$) | Maksimum İzin Verilen ($P_{95}$) | Açıklama |
| :--- | :--- | :--- | :--- |
| **Tier-1 İstemci Sözdizim Kontrolü** | $5 \text{ ms}$ | $15 \text{ ms}$ | Tarayıcıda yerel MathLive AST kontrolü |
| **Ağ Taşıma (Network Roundtrip)** | $35 \text{ ms}$ | $80 \text{ ms}$ | HTTPS / HTTP2 bağlantısı |
| **Sembolik Doğrulama (CAS / SymPy)** | $45 \text{ ms}$ | $150 \text{ ms}$ | Güvenli AST sandbox ve eşdeğerlik sadeleştirme |
| **FSM Durum Geçişi ve BKT Güncelleme** | $15 \text{ ms}$ | $30 \text{ ms}$ | Bellekteki Bayesian Knowledge Tracing hesabı |
| **Redis Oturum Güncellemesi** | $3 \text{ ms}$ | $10 \text{ ms}$ | `HSET` ve TTL yenileme |
| **PostgreSQL Olay Kütükleme (Asenkron)** | $0 \text{ ms}$ | $0 \text{ ms}$ | Arka plan worker'a bırakılır (Fire-and-forget / Queue) |
| **AI Tutor Sokratik Yanıt (Varsa)** | $400 \text{ ms}$ | $900 \text{ ms}$ | SSE (Server-Sent Events) ile ilk token akışı |
| **TOPLAM ADIM DOĞRULAMA (LLM'siz)** | **$\approx 100 \text{ ms}$** | **$\le 200 \text{ ms}$** | Yeşil/Kırmızı anlık gösterge yanar |
| **TOPLAM UÇTAN UCA (LLM Yanıtlı)** | **$\approx 550 \text{ ms}$** | **$\le 1200 \text{ ms}$** | Sokratik mesaj kutusu açılır |

