# 23-OFFLINE-STATE-AND-SYNC-SPECIFICATION.md
# ÇEVRİMDIŞI ÇALIŞMA, YEREL DURUM VE EŞZAMANLAMA ŞARTNAMESİ (OFFLINE STATE & SYNC)
## Isar/SQLite Yerel Veri Modeli, Çevrimdışı Adım Kuyruğu ve Çatışmasız Olay Tekrarı (Event Replay)

---

## 1. GENEL BAKIŞ VE FELSEFE

Kişisel Öğrenme Motoru, mobil cihazlarda metro, uçak veya zayıf internet bağlantısı durumunda öğrencinin 20 dakikalık günlük odak seansının bölünmemesini garanti eder:

1. **"Sıfır Donma, Sıfır Veri Kaybı":** Ağ bağlantısı koptuğunda kullanıcıya hata ekranı gösterilmez; yerel motor adımları kaydeder ve yerel AST ile ön doğrulama yapar.
2. **Olay Kaynağı Tabanlı Çatışmasız Replay (CRDT / Idempotent Replay):** Ağ tekrar sağlandığında, yerelde kuyruğa alınan adımlar sunucuya zaman damgalarıyla sırayla iletilir. Sunucu BKT ve FSRS durumlarını geriye dönük deterministik olarak yeniden hesaplar.

---

## 2. MOBİL YEREL VERİ TABANI ŞEMASI (ISAR SCHEMA - DART)

Mobil istemci, hızlı anahtar-değer ve nesne tabanlı yerel depolama için Flutter ekosisteminde donanım seviyesinde hızlı çalışan **Isar Database** kullanır.

### 2.1. `LocalLearnerState` Koleksiyonu
Öğrencinin 20 düğümlü Cebir Atlası üzerindeki son bilinen durumunu saklar.
```dart
@collection
class LocalLearnerState {
  Id id = Isar.autoIncrement;
  
  late String studentUuid;
  late DateTime lastSyncTimestamp;
  late double overallTheta; // 2PL-IRT yetenek puanı
  
  // Düğüm bazlı Bayesyen ustalık olasılıkları [NodeId -> P(L)]
  late List<NodeMasteryEntry> nodeMasteries;
  
  // 14 Saatlik Sirkadiyen Kilit Durumu
  late DateTime? circadianLockUntil;
}

@embedded
class NodeMasteryEntry {
  late String nodeId;       // Örn: "N15"
  late double pMastery;     // 0.0 - 1.0
  late double fsrsStability; // Gün cinsinden bellek stabilitesi
  late DateTime nextReviewDate;
}
```

### 2.2. `UnsyncedEventQueue` Koleksiyonu
Çevrimdışıyken atılan ve henüz sunucu tarafından doğrulanıp onaylanmamış adımlar.
```dart
@collection
class UnsyncedEvent {
  Id id = Isar.autoIncrement;
  
  @Index(unique: true)
  late String clientEventId; // UUID v4
  
  late String sessionId;
  late String eventType;     // "STEP_SUBMIT", "CONFIDENCE_SUBMIT"
  late String payloadJson;
  late DateTime createdAt;
  
  int retryCount = 0;
  bool isFailedPermanently = false;
}
```

---

## 3. AĞ KOPMASI VE ÇEVRİMDIŞI İCRA PROTOKOLÜ

```text
[ ÇEVRİMİÇİ MOD ] ──────────────── Ağ Koptu ───────────────► [ ÇEVRİMDIŞI SANDBOX ]
- Sunucu CAS & BKT anlık                                     - Tier-1 Yerel Dart AST denetimi
- Haptik hafif onay                                          - Adım Isar Queue'ya yazılır
- Gerçek zamanlı AI Tutor                                    - AI Tutor: "Bağlantı bekleniyor,
                                                               adımlarını kaydettim."
                                                                      │
                                                                 Ağ Geldi
                                                                      ▼
                                                             [ BATCH REPLAY & SYNC ]
                                                             - Idempotent API çağrısı
                                                             - Sunucu CAS doğrulama
                                                             - BKT & FSRS durum güncellemesi
```

---

## 4. ÇATIŞMASIZ SENKRONİZASYON KURALLARI (IDEMPOTENT EVENT REPLAY)

1. **İstemci Zaman Damgası Önceliği:** BKT geçiş olasılıkları hesaplanırken sunucu saati değil, öğrencinin adımı attığı anki `client_timestamp` ve `latency_ms` esas alınır.
2. **İdempotentlik Anahtarı (`client_msg_id`):** Sunucu, aynı `client_msg_id` ile gelen tekrarlı paketleri ikinci kez işlemez; önceden üretilmiş yanıtı döner (`HTTP 200 OK - Cached`).
3. **Kademeli Geri Çekilme (Exponential Backoff):**
   * Ağ koptuktan sonra ilk deneme: 2. saniyede.
   * İkinci deneme: 4. saniyede.
   * Üçüncü deneme: 8. saniyede (Maksimum 30 saniye aralıkla arka plan senkronizasyonu).
