# 18-FOUNDATION-GOALS-AND-DEFINITION-OF-DONE.md
# TEMEL HEDEFLER VE BİTİŞ KRİTERLERİ (DEFINITION OF DONE - DoD)
## Projenin Başarı Tanımı, Doğrulama Kapıları ve Nesnel Kabul Kriterleri

---

## 1. NEDEN BU DOKÜMAN VAR? (HEDEF BELİRLEMENİN ÖNEMİ)

Yazılım projelerinin en büyük başarısızlık nedeni "ne zaman bittiğinin" net olarak tanımlanmamasıdır. Açık ve nesnel hedefler konulmadığında:
1. Geliştirme süreci sonsuz bir özellik ekleme (scope creep) döngüsüne girer.
2. Kodun derlenmesi veya çalışıyor gibi görünmesi "özellik bitti" zannedilir (sahte tamamlanma).
3. Pedagojik ve matematiksel hatalar arayüzün arkasına gizlenir.

Bu doküman; **Kişisel Öğrenme Motoru'nun MVP geliştirme sürecinin bittiğini kanıtlayan, tartışmaya ve yoruma kapalı, otomatik olarak test edilebilir 6 Katı Kabul Kapısı'nı (Acceptance Gates)** ve nihai Definition of Done (DoD) kontratını kilitler.

---

## 2. NİHAİ PROJE HEDEFİ (THE NORTH STAR GOAL)

> **"Lise seviyesindeki bir öğrencinin İkinci Dereceden Denklemler konusunu; formül ezberlemeden, pasif video izlemeden, 20 dakikalık günlük seanslarla kavramsal olarak öğrenmesini sağlayan, adımlarını anlık denetleyen ve 14 gün sonraki kalıcılığını kanıtlayan tam otonom bir Nöro-Sembolik Bilişsel Öğrenme Motoru teslim etmek."**

---

## 3. 6 KATI DOĞRULAMA KAPISI (THE 6 ACCEPTANCE GATES)

MVP'nin "TAMAMLANDI" statüsü alabilmesi için aşağıdaki 6 kapının **tamamından sırayla ve %100 başarıyla** geçmesi şarttır:

```text
+─────────────────────────────────────────────────────────────────────────────+
|                     MVP DOĞRULAMA VE KABUL KAPILARI                         |
+─────────────────────────────────────────────────────────────────────────────+
| [ KAPI 1: SEMBOLİK CAS VE MATEMATİKSEL DOĞRULUK KAPISI ]                    |
| - 500 sentetik cebirsel adım testi (doğru adımlar, hatalı adımlar, tuzaklar)|
| - Başarı Kriteri: %100 Doğruluk (0 False Positive, 0 False Negative)        |
| - Hız Kriteri: Adım başına P95 analiz süresi <= 120 ms                      |
| - Güvenlik: Sıfır eval/exec, maksimum AST derinliği 15                      |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
| [ KAPI 2: PSİKOMETRİK KESTİRİM VE CAT TEŞHİS KAPISI ]                       |
| - 10,000 sentetik öğrenci Monte Carlo simülasyonu                           |
| - Başarı Kriteri: 2PL-IRT CAT motorunun en fazla 5 soruda SE(θ) <= 0.35     |
|   hassasiyetle öğrenciyi doğru DAG düğümüne yerleştirmesi                   |
| - Wald SPRT Kriteri: Sahte ustalık (Tip-1 hata α) <= 0.05, Tip-2 hata <= 0.10|
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
| [ KAPI 3: SOKRATİK AI VE SIFIR SIZINTI (ZERO-LEAKAGE) KAPISI ]              |
| - 100 farklı adversarial jailbreak ve prompt injection saldırısı            |
| - Başarı Kriteri: %0 Cevap Sızıntısı (Zero-Leakage Regex Guardrail geçişi)  |
| - Pedagojik Kriter: Sokratik Soru / Açıklama Oranı >= 2.0                   |
| - LLM Yanıt Süresi: P95 <= 800 ms                                           |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
| [ KAPI 4: PERFORMANS VE GECİKME BÜTÇESİ (SLA) KAPISI ]                      |
| - İstemci yerel sözdizim kontrolü: <= 15 ms                                 |
| - LLM'siz toplam adım doğrulama (Ağ + CAS + BKT): <= 180 ms                 |
| - LLM Sokratik yönlendirmeli toplam döngü: <= 850 ms                        |
| - İstemci FCP <= 1.2 s, TTI <= 2.0 s, UI tuş tepkisi <= 50 ms               |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
| [ KAPI 5: UÇTAN UCA KULLANICI DENEYİMİ VE AKIŞ KAPISI ]                     |
| - Gerçek bir kullanıcının:                                                  |
|   1. Sisteme sıfır sürtünmeyle girmesi                                      |
|   2. 8 soruluk CAT teşhisini tamamlaması                                    |
|   3. 20 dakikalık günlük seansı (Isınma -> ZPD -> Çözüm -> Kapanış)         |
|      hiçbir arayüz çökmesi veya çıkmaz sokak olmadan bitirmesi              |
|   4. Beyin Haritası'nda ilerlemesini görmesi                                |
| - Başarı Kriteri: 10 kullanıcı x 5 gün dahili testte 0 P0/P1 hata           |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
| [ KAPI 6: BİLİŞSEL KALICILIK VE ÖĞRENME KAZANCI (R-LGpM) KAPISI ]           |
| - 50 kişilik kohort (veya simüle edilmiş öğrenci grubu) pilot denemesi      |
| - Başarı Kriteri: Geleneksel EdTech (video + pasif soru) kontrol grubuna     |
|   kıyasla 14. gün kalıcılık testinde harcanan aktif dakika başına net       |
|   kazançta (R-LGpM) en az %35 istatistiksel üstünlük (p < 0.01, ANCOVA)     |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 4. KAPSAM İÇİ VE KAPSAM DIŞI SINIRLARI (SCOPE BOUNDARIES)

| Alan | MVP'de Kesinlikle VAR (In-Scope) | MVP'de Kesinlikle YOK (Out-of-Scope / Non-Goals) |
| :--- | :--- | :--- |
| **Matematik Konusu** | İkinci Dereceden Denklemler (20 Çekirdek Düğüm) | Trigonometri, Türev, Çok Değişkenli Sistemler |
| **Girdi Yöntemi** | MathLive Klavye + Akıllı Sembol Tuşları | Serbest El Yazısı OCR, Sesli Konuşma |
| **Doğrulama** | Deterministik SymPy AST (Sunucu Tarafı) | LLM'in tek başına matematiği puanlaması |
| **Öğretici** | Sokratik Metin Diyaloğu + Çözüm Tahtası | Sesli Konuşan 3D Avatar, Video Anlatımı |
| **Platform** | Responsive Web (Mobile PWA & Desktop) | Native iOS / Android Uygulamaları |
| **Motivasyon** | Beyin Haritası, Kalibrasyon Skoru, ZPD | Konfeti patlaması, XP, Lig/Liderlik Tablosu |

---

## 5. ÇIKIŞ KONTROL LİSTESİ (THE COMPREHENSIVE DEFINITION OF DONE CHECKLIST)

Geliştirme tamamlandığında aşağıdaki onay kutularının tamamı işaretlenmiş olmalıdır:

### 1. Kodlama ve Mimari Tamamlanma:
- [ ] Python 3.11 FastAPI backend servisi ayakta ve OpenAPI dokümantasyonu erişilebilir.
- [ ] Next.js 14 frontend arayüzü hatasız derleniyor (TypeScript strict mode, 0 lint error).
- [ ] PostgreSQL 15 Event Store şeması ve Redis 7.2 ZPD önbellek katmanı çalışıyor.
- [ ] SymPy AST doğrulayıcı sandbox kısıtlamaları (500ms timeout, memory limit) devrede.

### 2. Algoritmik ve Bilişsel Doğrulama:
- [ ] 5 Bozuk Kural (`BUG-QUAD-01..05`) AST tarafından hatasız tanınıyor.
- [ ] iBKT, CT-BKT ve Ratcliff DDM motoru adım adım canlı telemetriyle güncelleniyor.
- [ ] Wald SPRT algoritması erken durdurma ve ustalık kapılarını doğru açıyor/kapatıyor.
- [ ] FSRS-4.5 aralıklı tekrar çizelgeleyicisi 14 saatlik uyku bariyerini uyguluyor.
- [ ] Afektif dedektör öfke tıklamasında "Bir Nefes Verelim" modalını tetikliyor.

### 3. Test ve Kalite Güvencesi:
- [ ] Birim test kapsama oranı (Code Coverage) $\ge \%85$.
- [ ] 500 sentetik cebir test senaryosunun tamamı yeşil.
- [ ] 100 adversarial jailbreak güvenlik testinin tamamı yeşil.
- [ ] Uçtan uca Playwright E2E testleri (Teşhis $\to$ Seans $\to$ Kapanış) yeşil.
