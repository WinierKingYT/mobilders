# 24-SECURITY-PRIVACY-AND-DATA-GOVERNANCE.md
# GÜVENLİK, VERİ GİZLİLİĞİ VE YÖNETİŞİM ŞARTNAMESİ (SECURITY, PRIVACY & GOVERNANCE)
## Sıfır Kişisel Veri (Zero-PII) Mimarisi, LLM İzolasyonu, Kaba Kuvvet Koruması ve KVKK/GDPR Uyumu

---

## 1. TEMEL FELSEFE VE SIFIR KİŞİSEL VERİ (ZERO-PII) İLKESİ

Kişisel Öğrenme Motoru, reşit olmayan öğrencilerin (13-18 yaş lise grubu) bilişsel verilerini işlediği için **gizlilik öncelikli (privacy-by-design)** bir mimariyle inşa edilmiştir:

1. **Sıfır PII (Zero Personally Identifiable Information):** Sistemde kullanıcı adı, e-posta, telefon numarası, okul adı veya gerçek kimlik bilgisi tutulmaz ve talep edilmez.
2. **Cihaz Anahtarlığı (Keychain/Keystore) Tabanlı Anonim Kimlik:** Kullanıcı, cihazındaki güvenli donanım modülünde (iOS Keychain / Android EncryptedSharedPreferences) üretilen rastgele bir kriptografik `UUID v4` ile temsil edilir.
3. **Pedagojik Veri Minimizasyonu:** Sunucuda yalnızca öğrencinin matematiksel adımları, tepki süreleri ve Bayesyen ustalık olasılıkları saklanır.

---

## 2. LLM İZOLASYONU VE VERİ SIZINTISI GÜVENCESİ (LLM PRIVACY GUARD)

Bilişsel diyalog motoru (Google Gemini API vb.) harici bir LLM sağlayıcısına bağlandığında aşağıdaki katı veri izolasyon kuralları işletilir:

```text
[ Öğrenci Çözüm Tahtası ] 
           │
           ▼
[ API Ağ Geçidi & Anonimleştirici Filtre ]
  - Öğrenci UUID'si kaldırılır (İstek başına geçici 'prompt_session_id' atanır).
  - Özel isim, şehir veya okul çağrışımı yapan serbest metinler regex ile temizlenir.
  - LLM'e sadece: { Hata Kodu, Güncel Denklem, Hedef ZPD, İskele Seviyesi } gider.
           │
           ▼
[ Google Gemini / Harici LLM API ]
           │
           ▼
[ Zero-Leakage Regex Sübabı (M4.2) ] ── (Cevap/kök sızıntısı taraması)
           │
           ▼
[ Öğrenci Ekranı ]
```

---

## 3. AĞ GÜVENLİĞİ VE KABA KUVVET KORUMASI (ANTI-ABUSE & RATE LIMITING)

1. **TLS 1.3 ve Certificate Pinning:** Mobil istemci ile backend arasındaki tüm HTTP/WebSocket iletişimi TLS 1.3 üzerinden şifrelenir. Üretim sürümünde SSL Pinning zorunludur.
2. **WebSocket Hız Sınırı (Rate Limiting):**
   * Tek bir oturumdan saniyede en fazla 2 `STEP_SUBMIT` kabul edilir.
   * Aşırı hızlı gönderimler ($<300\text{ ms}$ aralıkla seri gönderimler) bot/komut dosyası saldırısı olarak etiketlenir ve bağlantı 10 saniye askıya alınır.
3. **AST Parser Güvenlik Duvarı:**
   * Python tarafında hiçbir `eval()`, `exec()` veya dinamik derleyici çağrılmaz.
   * Maksimum AST derinliği 15 ile sınırlandırılmıştır; 15'ten derin ifadeler işleme alınmadan `INVALID_EXPRESSION_DEPTH` hatasıyla reddedilir.
   * Sembolik basitleştirme (`simplify`) işlemi için 500 ms multiprocessing donma süresi (hard timeout) uygulanır.

---

## 4. KVKK VE GDPR UYUMLULUĞU

* **Unutulma Hakkı (Right to be Forgotten):** Kullanıcı mobil uygulamadan "Verilerimi Sıfırla" butonuna bastığında, cihazdaki UUID anahtarlık kaydı silinir ve sunucuya anonim bir `PURGE_TELEMETRY` olayı gönderilerek öğrenciye ait tüm BKT geçmişi anonim boşluğa bırakılır.
* **Veri Taşınabilirliği:** Kullanıcı dilerse tüm matematiksel öğrenme geçmişini (Atlas düğüm durumları ve seans sayıları) JSON formatında dışa aktarabilir.
