# 27-TELEMETRY-LOGGING-AND-ERROR-TAXONOMY.md
# HATA SÖZLÜĞÜ, LOGLAMA VE TELEMETRİ ŞARTNAMESİ (TELEMETRY & ERROR TAXONOMY)
## Standart Sistem Hata Kodları, Bilişsel Telemetri Paketleri ve Yapılandırılmış Log Şemaları

---

## 1. GENEL BAKIŞ

Kişisel Öğrenme Motoru, hata ayıklama (debugging), performans izleme ve bilişsel model kalibrasyonu için standartlaştırılmış bir hata taksonomisi ve olay günlüğü mimarisi kullanır:

1. **Benzersiz Hata Kodları:** Her istisnai durum (`ERR_...`), tekil bir alfasayısal kod ve makine tarafından okunabilir bir hata yükü ile temsil edilir.
2. **Yapılandırılmış JSON Loglama:** Sunucu logları düz metin değil; OpenTelemetry ve ELK uyumlu yapılandırılmış JSON biçimindedir.
3. **Bilişsel Telemetri:** Öğrencinin tereddütleri, tuş vuruşu aralıkları ve silme davranışları afektif durumun (HMM) canlı beslemesi olarak kaydedilir.

---

## 2. STANDART SİSTEM HATA KODLARI KATALOĞU (ERROR CODE TAXONOMY)

### 2.1. Sembolik Matematik ve CAS Hataları (`1000 - 1999`)
* `ERR_CAS_PARSE_FAILED (1001)`: LaTeX veya metin girdisi geçerli bir AST ağacına dönüştürülemedi.
* `ERR_CAS_DEPTH_EXCEEDED (1002)`: İfade karmaşıklığı maksimum AST derinlik sınırını ($15$) aştı.
* `ERR_CAS_TIMEOUT (1003)`: `simplify()` veya denklem eşdeğerliği kontrolü $500\text{ ms}$ sınırında zaman aşımına uğradı.
* `ERR_CAS_DIVISION_BY_ZERO (1004)`: Cebirsel adımda tanımsız sıfıra bölme işlemi tespit edildi.
* `ERR_CAS_INVALID_CHARACTERS (1005)`: Matematiksel alfabede tanımlanmayan yabancı semboller tespit edildi.

### 2.2. Bilgi Grafı ve DAG Hataları (`2000 - 2999`)
* `ERR_DAG_NODE_NOT_FOUND (2001)`: İstenen kavram düğümü (`[N01]..[N30]`) ontolojik ağda mevcut değil.
* `ERR_DAG_CYCLE_DETECTED (2002)`: Graf kenar güncellemesi topolojide döngüsel bağımlılık yarattı.
* `ERR_DAG_PREREQUISITE_LOCKED (2003)`: Katı önkoşul ($E_{\text{strict}}$) sağlanmadan kilitli düğüme geçilmeye çalışıldı.

### 2.3. Bilişsel Model ve Psikometri Hataları (`3000 - 3999`)
* `ERR_BKT_CONVERGENCE_FAILED (3001)`: iBKT lojistik link fonksiyonu optimize edilemedi.
* `ERR_DDM_DEGENERATE_DATA (3002)`: EZ-Diffusion için sıfır varyans veya aşırı uç latens değeri ($MRT < 100\text{ ms}$).
* `ERR_CAT_ITEM_EXHAUSTED (3003)`: Belirlenen yetenek aralığında kalibre edilmiş soru kalmadı.

### 2.4. Güvenlik, LLM ve Sokratik Hatalar (`4000 - 4999`)
* `ERR_SEC_ZERO_LEAK_TRIGGERED (4001)`: LLM çıktısında çözüm kümesi veya kök sızıntısı yakalandı ve bloke edildi.
* `ERR_SEC_RATE_LIMIT_EXCEEDED (4002)`: Oturum başına izin verilen saniyelik adım gönderim sınırı aşıldı.
* `ERR_SEC_UNAUTHORIZED_TOKEN (4003)`: WebSocket oturum token'ı geçersiz veya süresi dolmuş.

---

## 3. BİLİŞSEL TELEMETRİ OLAYI ŞEMASI (`CognitiveTelemetryEvent`)

Öğrencinin çözüm tahtasındaki mikro-etkileşimleri zihinsel yük ve afektif durum tespiti için kaydedilir:

```json
{
  "event_type": "COGNITIVE_TELEMETRY",
  "session_id": "sess_98234-abcd",
  "problem_id": "prob_quad_015",
  "timestamp": "2026-09-14T16:48:00.000Z",
  "telemetry_payload": {
    "total_thinking_time_ms": 14200,
    "first_keystroke_latency_ms": 6100,
    "inter_keystroke_mean_ms": 320,
    "inter_keystroke_variance_ms": 14500,
    "total_backspaces": 3,
    "cursor_idle_intervals_above_3s": 2,
    "mode_switches_count": 1,
    "input_mode_used": "touchpad",
    "screen_orientation": "portrait"
  }
}
```

---

## 4. YAPILANDIRILMIŞ SUNUCU LOG ŞEMASI (STRUCTURED LOGGING)

FastAPI ve Celery logları standart JSON formatında Elasticsearch/CloudWatch'a basılır:

```json
{
  "timestamp": "2026-09-14T16:48:01.234Z",
  "level": "INFO",
  "logger": "services.core_engine.cas_evaluator",
  "message": "Step verified successfully",
  "trace_id": "trc_4f5a6b",
  "span_id": "spn_8899aa",
  "student_uuid": "anon_u_9a8b7c",
  "problem_id": "prob_quad_015",
  "duration_ms": 42.6,
  "result": {
    "is_correct": true,
    "bug_detected": null,
    "ast_depth": 4
  }
}
```
