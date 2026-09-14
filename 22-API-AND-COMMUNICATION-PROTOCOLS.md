# 22-API-AND-COMMUNICATION-PROTOCOLS.md
# MOBİL-BACKEND İLETİŞİM PROTOKOLLERİ VE API ŞARTNAMESİ (API & PROTOCOL SPECIFICATION)
## WebSocket Canlı Akış Sözleşmesi, REST Uç Noktaları, JSON Şemaları ve İstemci Ön Doğrulama Kuralları

---

## 1. GENEL BAKIŞ VE İLETİŞİM PRENSİPLERİ

Kişisel Öğrenme Motoru, mobil istemci (Flutter) ile zeki bilişsel çekirdek (FastAPI) arasında iki farklı iletişim kanalı kullanır:

1. **Çözüm Tahtası Canlı Oturumu (WebSocket - `/ws/v1/session`):**
   * Milisaniyelik telemetri, adım doğrulama, haptik tetikleyiciler ve afektif anlık şalter için çift yönlü, kalıcı ve düşük gecikmeli ($P_{95} \le 180\text{ ms}$) kanal.
2. **Yapılandırılmış Durum ve Teşhis API'si (REST / HTTP):**
   * Soğuk başlangıç CAT teşhis oturumu, günlük seans başlatma, geçmiş seans özeti ve analitik veriler için standart HTTPS JSON uç noktaları.

---

## 2. WEBSOCKET OTURUM PROTOKOLÜ (`/ws/v1/session`)

### 2.1. Bağlantı Yaşam Döngüsü (Connection Lifecycle)
```text
Flutter Mobil                              FastAPI Backend
     │                                            │
     │─── [WS Connect: /ws/v1/session?token=...] ─►│
     │◄── [SESSION_READY: state, problem] ────────│
     │                                            │
     │─── [STEP_SUBMIT: latex, latency, mode] ───►│ (CAS + BKT İşleme)
     │◄── [STEP_VALIDATED: status, feedback] ─────│
     │                                            │
     │─── [CONFIDENCE_SUBMIT: prob, time] ───────►│ (Brier Hesaplama)
     │◄── [CONFIDENCE_ACK: score, calibration] ───│
     │                                            │
     │─── [AFFECTIVE_BEACON: pauses, deletes] ───►│ (Markov HMM Analizi)
     │◄── [AFFECTIVE_ALERT: circuit_breaker] ─────│ (Opsiyonel Müdahale)
     │                                            │
```

---

### 2.2. İstemciden Sunucuya Giden Mesaj Şemaları (Client -> Server)

#### A. `STEP_SUBMIT` (Öğrencinin Çözüm Adımı Göndermesi)
```json
{
  "type": "STEP_SUBMIT",
  "client_msg_id": "cmsg_7f8a9b1c-4d2e",
  "session_id": "sess_98234-abcd",
  "problem_id": "prob_quad_015",
  "step_index": 2,
  "payload": {
    "raw_latex": "x^2 + 6x + 9 = 11",
    "previous_canonical": "x^2 + 6x = 2",
    "input_mode": "touchpad", 
    "latency_ms": 4820,
    "hesitation_pauses_count": 1,
    "backspace_count": 0,
    "client_timestamp": "2026-09-14T16:42:00.123Z"
  }
}
```

#### B. `CONFIDENCE_SUBMIT` (Metabilişsel Güven Bildirimi)
```json
{
  "type": "CONFIDENCE_SUBMIT",
  "client_msg_id": "cmsg_11a22b33",
  "session_id": "sess_98234-abcd",
  "step_index": 2,
  "payload": {
    "confidence_level": 0.80,
    "decision_time_ms": 1450,
    "client_timestamp": "2026-09-14T16:42:02.456Z"
  }
}
```

#### C. `HINT_REQUEST` (İskele / İpucu Talebi)
```json
{
  "type": "HINT_REQUEST",
  "client_msg_id": "cmsg_hint_9988",
  "session_id": "sess_98234-abcd",
  "step_index": 2,
  "payload": {
    "current_latex": "x(x+6) = 2",
    "stuck_duration_ms": 12400
  }
}
```

---

### 2.3. Sunucudan İstemciye Gelen Mesaj Şemaları (Server -> Client)

#### A. `STEP_VALIDATED` (Adım Doğrulama ve Bilişsel Geri Bildirim)
*Geçerli Adım:*
```json
{
  "type": "STEP_VALIDATED",
  "client_msg_id": "cmsg_7f8a9b1c-4d2e",
  "status": "VALID",
  "payload": {
    "is_correct": true,
    "is_terminal_step": false,
    "canonical_latex": "x^2 + 6x + 9 = 11",
    "buggy_rule": null,
    "haptic_feedback": "light_impact",
    "learner_delta": {
      "concept_id": "math.alg.quadratics.complete_square",
      "p_mastery_prior": 0.52,
      "p_mastery_posterior": 0.61
    },
    "socratic_prompt": null
  }
}
```

*Hatalı Adım (Bozuk Kural Yakalandığında):*
```json
{
  "type": "STEP_VALIDATED",
  "client_msg_id": "cmsg_7f8a9b1c-4d2e",
  "status": "BUGGY_RULE_DETECTED",
  "payload": {
    "is_correct": false,
    "is_terminal_step": false,
    "canonical_latex": "x = 2 \\lor x + 6 = 2",
    "buggy_rule": {
      "rule_id": "BUG-QUAD-01",
      "name": "NonZeroZeroProduct",
      "description": "Sıfır olmayan sayıya sıfır-çarpım kuralı uygulama yanılgısı"
    },
    "haptic_feedback": "heavy_error",
    "socratic_prompt": {
      "agent_role": "socratic_coach",
      "message": "Sol tarafı çarpım haline getirdin. Peki çarpımları 2 olan iki sayının biri mutlaka 2 olmak zorunda mıdır? (Örneğin 1 ve 2, ya da 4 ve 0.5 olabilir mi?)",
      "scaffold_level": 2
    }
  }
}
```

#### B. `AFFECTIVE_ALERT` (Duygudurumsal Şalter Müdahalesi)
```json
{
  "type": "AFFECTIVE_ALERT",
  "payload": {
    "circuit_breaker_triggered": true,
    "action": "TRIGGER_BREATHE_MODAL",
    "f_score": 0.88,
    "pause_duration_seconds": 15,
    "support_message": "Bu adım oldukça derin bir bilişsel yük gerektiriyor. Bir an durup derin bir nefes alalım, ardından karolar üzerinden görsel olarak yaklaşalım."
  }
}
```

---

## 3. REST API UÇ NOKTALARI (HTTP REST ENDPOINTS)

### 3.1. Teşhis ve Seviye Belirleme (CAT Endpoints)
* `POST /api/v1/cat/start`: Yeni bir uyarlamalı test oturumu başlatır.
* `POST /api/v1/cat/submit-item`: Çözülen CAT maddesini iletir, güncel $\hat{\theta}$ ve bir sonraki maddeyi döner.
* `GET /api/v1/cat/result/{cat_session_id}`: CAT sonucunda oluşan 20 düğümlü Cebir Atlası Bayesian başlangıç olasılık dağılımını döner.

### 3.2. Günlük Seans ve İlerleme (Session & Atlas Endpoints)
* `POST /api/v1/session/start-daily`: Günlük 20 dakikalık oturumu başlatır (FSRS-4.5 ısınma soruları + ZPD hedefi).
* `GET /api/v1/atlas/state`: Öğrencinin güncel 20 düğümlü Cebir Atlası durumunu (Usta, ZPD, Kilitli) döner.
* `POST /api/v1/session/conclude`: Günlük seansı sonlandırır, 14 saatlik sirkadiyen kilidi aktifleştirir.

---

## 4. İSTEMCİ TARAFI YEREL AST VE SÖZDİZİM ÖN KONTROLÜ (TIER-1 CLIENT SANITY)

Mobil istemci, öğrencinin geçersiz veya yarım kalan denklemlerle sunucu kotasını ve ağ süresini tüketmesini önlemek için Dart seviyesinde milisaniyelik ön filtreler uygular:

1. **Parantez Dengesi Denetimi (`validate_parentheses_balance`):**
   * `(` ve `)` adetleri eşit değilse "Kontrol Et" butonu deaktiftir (`disabled`).
2. **Eşitlik İşareti Kuralı (`validate_single_equality`):**
   * Bir denklem adımında tam olarak 1 adet `=` olmalıdır; birden fazla veya sıfır eşitlik işareti varsa kullanıcıya anında yerel uyarı gösterilir.
3. **Geçersiz Karakter ve Enjeksiyon Koruması (`sanitize_input_symbols`):**
   * Yalnızca geçerli matematiksel karakter kümesine (`[0-9xX+\-*/^=().,\s]`) izin verilir; alfasayısal komutlar (`eval`, `script` vb.) istemcide filtrelenir.
4. **Gecikme Hedefi:** İstemci tarafı ön kontrol gecikmesi $\le 5\text{ ms}$ olmalıdır.
