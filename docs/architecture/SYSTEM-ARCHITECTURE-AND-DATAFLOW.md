# SYSTEM ARCHITECTURE AND DATAFLOW SPECIFICATION (SİSTEM MİMARİSİ VE VERİ AKIŞ ŞARTNAMESİ)
## Kişisel Öğrenme Motoru (Personal Learning Engine) — C4 Mimarisi, ER Modelleri ve İletişim Akışları

**Tarih:** 14 Eylül 2026  
**Doküman Kodu:** ARCH-PLE-2026-V1  
**Kapsam:** Flutter Mobil İstemci, Python FastAPI Çekirdek Motor, Nöro-Sembolik CAS, WebSocket Canlı Akış ve Çevrimdışı Senkronizasyon  

---

## 1. MİMARİ GENEL BAKIŞ VE C4 MODELİ

Kişisel Öğrenme Motoru, **"Deterministik Sembolik Hakikat + Kısıtlanmış Sokratik Pedagoji"** (Neuro-Symbolic Architecture) felsefesine dayanan, olay güdümlü (event-driven), çift yönlü ve düşük gecikmeli bir mikro-istemci mimarisidir.

### 1.1. C4 Seviye 1: Sistem Bağlamı (System Context Diagram)

```mermaid
graph TD
    User([Öğrenci / Lise Grubu]) <-->|390x844 Mobil Portre Arayüzü| MobileApp[PLE Flutter Mobil Uygulaması]
    MobileApp <-->|WebSocket: Canlı Telemetri /ws/v1/session| Gateway[FastAPI API Ağ Geçidi]
    MobileApp <-->|HTTPS REST: CAT Teşhis & Durum /api/v1| Gateway
    Gateway <-->|Deterministik Matematik Doğrulama| CAS[SymPy Sembolik CAS & AST Sandbox]
    Gateway <-->|Bayesyen Yetenek & Hafıza| Psychometrics[iBKT + DDM + FSRS-4.5 Motoru]
    Gateway <-->|Pedagojik İskele & Güvenlik| SocraticAI[4-Katmanlı Sokratik AI & Zero-Leakage Kalkanı]
```

---

### 1.2. C4 Seviye 2: Konteyner ve Servis Mimarisi (Container Diagram)

```mermaid
graph TB
    subgraph Mobil Cihaz [İstemci Katmanı - Flutter / Dart]
        Touchpad[MathTouchpad: Çift Modlu Matematik Girişi]
        Canvas[AlKhwarizmiCanvas: x² + bx Geometrik Tuval]
        Scratchpad[ScratchpadOverlay: Serbest Çizim Katmanı]
        Tier1AST[Tier-1 Yerel Dart AST Sözdizim Denetleyici]
        OfflineQueue[In-Memory & Isar Çevrimdışı Olay Kuyruğu]
        WSClient[SessionWebSocketService: Canlı Soket İstemcisi]
    end

    subgraph Backend [Çekirdek Bilişsel Motor - Python 3.11 / FastAPI]
        APIRouter[FastAPI Uç Noktaları & WS Yöneticisi]
        SymEngine[SymbolicEquivalenceEngine: AST Whitelist]
        BugDetector[QuadraticMisconceptionDetector: BUG-QUAD-01..05]
        DAGService[KnowledgeDAG: 20 Çekirdek Düğümlü Topoloji]
        CATService[CATEngine: 2PL-IRT Fisher Bilgi Seçicisi]
        BKTService[IndividualizedBKT & CT-BKT: Kolmogorov Çözücü]
        DDMService[EZDiffusionSolver: Wagenmakers Kapalı Form]
        SPRTService[WaldSPRT: Sıralı Olasılık Karar Vericisi]
        FSRSService[FSRSEngine: 17 Parametre & Sirkadiyen Kilit]
        PropService[PartWholePropagator: Nilpotent Matris (I - 0.8A)⁻¹]
        AffectService[AffectiveStateDetector: 5-Durumlu HMM & Şalter]
        SocrService[SocraticPipeline & ZeroLeakageGuardrail]
    end

    Touchpad --> Tier1AST
    Tier1AST -->|Geçerli Adım| WSClient
    Tier1AST -->|Sözdizim Hatası| Touchpad
    WSClient <-->|WSS TLS 1.3| APIRouter
    WSClient -.->|Ağ Koptuğunda| OfflineQueue
    OfflineQueue -.->|Ağ Geldiğinde Replay| WSClient

    APIRouter --> SymEngine
    APIRouter --> BugDetector
    APIRouter --> DAGService
    APIRouter --> CATService
    APIRouter --> BKTService
    APIRouter --> DDMService
    APIRouter --> SPRTService
    APIRouter --> FSRSService
    APIRouter --> PropService
    APIRouter --> AffectService
    APIRouter --> SocrService
```

---

## 2. VARLIK VE BİLİŞSEL VERİ MODELLERİ (ENTITY RELATIONSHIP & DATA MODELS)

Sistemde öğrenci kişisel verisi (PII) tutulmaz. Tüm durum anonim bir `StudentUUID` ve matematiksel bilişsel durum matrisi ile saklanır.

### 2.1. ER Modeli Şeması

```mermaid
erDiagram
    STUDENT_COGNITIVE_STATE ||--o{ NODE_MASTERY : tracks
    STUDENT_COGNITIVE_STATE ||--o{ SESSION_EVENT : logs
    KNOWLEDGE_NODE ||--o{ NODE_PREREQUISITE : defines
    KNOWLEDGE_NODE ||--o{ NODE_MASTERY : references
    SESSION_EVENT ||--o{ STEP_DIAGNOSTIC : includes

    STUDENT_COGNITIVE_STATE {
        string student_uuid PK "Kriptografik Anonim ID"
        float overall_theta "2PL-IRT Latent Yetenek (-3.0 to +3.0)"
        float standard_error "SE(theta)"
        datetime circadian_lock_until "14 Saatlik Uyku Bariyeri Bitişi"
        datetime last_sync_time "Son Eşzamanlama Zamanı"
    }

    KNOWLEDGE_NODE {
        string node_id PK "N01..N20"
        string canonical_code "math.alg.quadratics.complete_square"
        string title "Tam Kareye Tamamlama"
        int level "0: Temel, 1: Orta, 2: İleri"
        float default_difficulty_b "2PL-IRT b parametresi"
        float discrimination_a "2PL-IRT a parametresi"
    }

    NODE_PREREQUISITE {
        string parent_node_id FK
        string prerequisite_node_id FK
        string dependency_type "STRICT | SOFT"
    }

    NODE_MASTERY {
        string student_uuid FK
        string node_id FK
        float p_mastery "BKT Güncel Ustalık P(L)"
        float fsrs_stability "FSRS Bellek Stabilitesi (Gün)"
        float fsrs_difficulty "FSRS Algılanan Zorluk D"
        datetime next_review_date "Aralıklı Tekrar Tarihi"
    }

    SESSION_EVENT {
        string event_id PK "UUID v4"
        string session_id "sess_xxx"
        string student_uuid FK
        string event_type "STEP_SUBMIT | CONFIDENCE_SUBMIT | HINT_REQUEST"
        int step_index "Adım Sırası"
        string raw_latex "Girdi İfadesi"
        float latency_ms "Tepki Süresi"
        datetime client_timestamp "İstemci Zaman Damgası"
    }

    STEP_DIAGNOSTIC {
        string event_id FK
        boolean is_valid "Matematiksel Geçerlilik"
        string detected_bug_id "BUG-QUAD-01..05"
        float ddm_drift_v "Drift Rate"
        float ddm_boundary_a "Boundary Separation"
        string affective_state "FLOW | CONFUSION | FRUSTRATION"
    }
```

---

## 3. VERİ AKIŞLARI VE SIRALI DİYAGRAMLAR (SEQUENCE DIAGRAMS)

---

### 3.1. Canlı Adım Doğrulama ve Sokratik Geri Bildirim Akışı (WebSocket)

```mermaid
sequenceDiagram
    autonumber
    actor Student as Öğrenci (Flutter)
    participant UI as MathTouchpad & Canvas
    participant ClientAST as İstemci Tier-1 AST
    participant WS as WebSocket (/ws/v1/session)
    participant Backend as FastAPI Router
    participant CAS as SymbolicEngine (SymPy)
    participant Bug as MisconceptionDetector
    participant BKT as IndividualizedBKT
    participant DDM as EZDiffusionSolver
    participant Affect as AffectiveDetector
    participant Socr as SocraticPipeline
    participant Guard as ZeroLeakageGuardrail

    Student->>UI: Denklem adımını girer (x + 3 = sqrt(11))
    UI->>ClientAST: validate_parentheses_balance & equality
    ClientAST-->>UI: Geçerli sözdizim (<=2ms)
    UI->>WS: STEP_SUBMIT {raw_latex, latency_ms, thrash_count}
    WS->>Backend: Mesajı ayrıştır
    Backend->>CAS: verify_equivalence(raw_latex, target_eq)
    CAS-->>Backend: is_valid: false, latency: 18ms
    Backend->>Bug: detect(raw_latex, prev_canonical, target_eq)
    Bug-->>Backend: BUG-QUAD-02 (Negatif Kök Kaybı)
    Backend->>BKT: update_mastery(p_l, is_correct=False)
    Backend->>DDM: solve(mrt, vrt, pc=0.15)
    Backend->>Affect: evaluate_telemetry(obs)
    Affect-->>Backend: State: CONFUSION, F_score: 0.42
    Backend->>Socr: process(SocraticRequest)
    Socr->>Guard: intercept_and_filter(raw_prompt)
    Guard-->>Socr: Sızıntısız Sokratik Soru (<=0.1ms)
    Socr-->>Backend: Sokratik İpucu
    Backend->>WS: STEP_VALIDATED {status: BUGGY_RULE_DETECTED, prompt}
    WS-->>UI: Adım üstü çizilir, Sokratik yönlendirme gösterilir
```

---

### 3.2. 2PL-IRT Dinamik CAT Teşhis ve Atlas Tohumlama Akışı (REST)

```mermaid
sequenceDiagram
    autonumber
    actor Student as Öğrenci (Flutter)
    participant DiagUI as DiagnosticScreen
    participant API as EngineApiService
    participant Backend as FastAPI CAT Router
    participant CAT as CATEngine (2PL-IRT)
    participant DAG as KnowledgeDAG

    Student->>DiagUI: Teşhis Seansını Başlat
    DiagUI->>API: getNextCatItem(theta=0.0, history=[])
    API->>Backend: POST /api/v1/diagnostic/next-item
    Backend->>CAT: select_next_item(theta=0.0)
    CAT-->>Backend: Item: CAT-ITEM-01 (N12, b=-1.8, a=2.8)
    Backend-->>DiagUI: CATItemResponse
    DiagUI-->>Student: Soruyu ekranda göster
    Student->>DiagUI: Yanıtı seçer (Doğru)
    DiagUI->>API: submitCatResponse(item_id, is_correct=True)
    API->>Backend: POST /api/v1/diagnostic/submit
    Backend->>CAT: estimate_theta(history) -> theta_hat=0.72, SE=0.48
    Backend->>CAT: is_test_complete() -> False (SE > 0.35)
    Backend->>CAT: select_next_item(theta=0.72)
    CAT-->>Backend: Item: CAT-ITEM-05 (b=0.75, a=2.75)
    Backend-->>DiagUI: next_item döner
    Note over Student,DiagUI: 3-4 soru sonra SE <= 0.35'e düşer
    DiagUI->>API: submitCatResponse(final_item)
    API->>Backend: POST /api/v1/diagnostic/submit
    Backend->>CAT: is_test_complete() -> True (SE <= 0.35)
    Backend->>CAT: seed_knowledge_dag(theta_hat)
    CAT->>DAG: get_zpd_candidates(mastered_set)
    DAG-->>Backend: ZPD: [N15: Tam Kare, N18: Diskriminant]
    Backend-->>DiagUI: is_complete=True, seeded_mastery, zpd_candidates
    DiagUI-->>Student: "Başlangıç Haritan Hazır! Hedef: N15 Tam Kare"
```

---

### 3.3. Çevrimdışı Mod, Yerel Kuyruk ve Çatışmasız Senkronizasyon (Offline Sync)

```mermaid
sequenceDiagram
    autonumber
    actor Student as Öğrenci (Metro/Tünel)
    participant Touchpad as MathTouchpad
    participant LocalAST as Tier-1 Dart AST
    participant Queue as UnsyncedEventQueue (Isar/Memory)
    participant Network as Ağ İzleyicisi (Connectivity)
    participant Backend as FastAPI Gateway
    participant EventStore as Olay Kaynağı / Veritabanı

    Note over Student,Network: İnternet Bağlantısı Koptu (Offline)
    Student->>Touchpad: Adım yazar: x² + 6x + 9 = 11
    Touchpad->>LocalAST: Ön doğrulama yap (Parantez, Eşitlik)
    LocalAST-->>Touchpad: Geçerli biçim
    Touchpad->>Queue: Olayı kaydet (client_msg_id, payload, timestamp)
    Touchpad-->>Student: "Çevrimdışı kaydedildi ✓"
    Note over Student,Network: İnternet Bağlantısı Yeniden Sağlandı
    Network->>Queue: 'online' sinyali tetiklendi
    Queue->>Backend: POST /api/v1/session/replay-batch [Event1, Event2, ...]
    Backend->>Backend: Idempotency Denetimi (client_msg_id kontrolü)
    loop Her Bir Adım İçin
        Backend->>Backend: CAS doğrulama & BKT durum güncellemesi
    end
    Backend->>EventStore: Olayları kalıcı kaydet
    Backend-->>Queue: HTTP 200 OK (Senkronizasyon Başarılı)
    Queue->>Queue: Kuyruktaki olayları temizle
```

---

### 3.4. Afektif Kriz ve Şalter Müdahalesi (Circuit Breaker Interruption)

```mermaid
sequenceDiagram
    autonumber
    actor Student as Öğrenci
    participant UI as Flutter SessionScreen
    participant WS as WebSocket Channel
    participant Backend as Core Engine
    participant Affect as AffectiveStateDetector

    Student->>UI: 4 saniye içinde 5 kez üst üste silme/hatalı deneme (Rage Clicks)
    UI->>WS: STEP_SUBMIT {latency_ms: 800, thrash_count: 5}
    WS->>Backend: Telemetriyi ilet
    Backend->>Affect: evaluate_telemetry(obs)
    Affect->>Affect: Frustration Skoru = 0.91 (>= 0.85 Eşiği Aşıldı)
    Affect-->>Backend: is_circuit_breaker_tripped = True
    Backend->>WS: AFFECTIVE_ALERT {action: TRIGGER_BREATHE_MODAL, pause: 15s}
    WS-->>UI: Ekran anında kilitlenir
    UI-->>Student: "Bir Nefes Verelim" animasyonlu solunum modalı açılır
    Note over Student,UI: 15 saniye zorunlu bilişsel mola (Öğrenci cezalandırılmaz)
    UI-->>Student: Çözümlü Örnek (Worked Example) kartına yönlendirilir
```

---

## 4. İLETİŞİM SÖZLEŞMELERİ VE PAYLOAD ŞEMALARI

### 4.1. WebSocket Mesaj Formatı (`/ws/v1/session`)
Tüm WebSocket mesajları aşağıdaki temel zarf (envelope) yapısını paylaşır:
```json
{
  "type": "STRING (STEP_SUBMIT | STEP_VALIDATED | CONFIDENCE_SUBMIT | AFFECTIVE_ALERT | HINT_REQUEST | PING)",
  "client_msg_id": "STRING (cmsg_uuid)",
  "session_id": "STRING (sess_uuid)",
  "timestamp": 1726328400.123,
  "payload": { ... }
}
```

### 4.2. REST Uç Noktaları Sözleşmesi
- **Adım Doğrulama:** `POST /api/v1/session/step/verify` $\to$ `StepVerificationResponse` (Gecikme $P_{95} \le 180\text{ ms}$)
- **Dinamik Teşhis Soru Talebi:** `POST /api/v1/diagnostic/next-item` $\to$ `CATItemResponse` (Gecikme $P_{95} \le 25\text{ ms}$)
- **Teşhis Cevap Gönderimi:** `POST /api/v1/diagnostic/submit` $\to$ `CATSubmitResponse`
- **Sokratik Diyalog Rehberi:** `POST /api/v1/socratic/respond` $\to$ `InnerMonologueLog` (Gecikme $P_{95} \le 10\text{ ms}$ yerel)
- **Günlük Seans Başlatma:** `POST /api/v1/session/start-daily`
- **Atlas Durumu:** `GET /api/v1/atlas/state`
- **Seans Kapanışı (14h Kilit):** `POST /api/v1/session/conclude`

Bu mimari; milisaniyelik deterministik matematiksel güvenceyi, insan bilişsel kapasitesine duyarlı koruyucu sınırları ve kesintisiz mobil deneyimi temin eder.
