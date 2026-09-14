# 00-PROJECT-VISION.md
# BİLİŞSEL KİŞİSEL ÖĞRENME MOTORU (PERSONAL LEARNING ENGINE)
## Proje Vizyonu, Felsefi Temeller ve Paradigma Değişimi Manifestosu

---

## 1. YÖNETİCİ ÖZETİ VE ÇIKIŞ NOKTASI

Günümüz eğitim teknolojileri (EdTech) pazarı, dijital çağın en büyük yapısal aldatmacalarından birini yaşamaktadır: Pazardaki uygulamaların %99'u öğrencinin zihinsel modelini dönüştürmek yerine **içerik dağıtımını (Content Delivery)** ve **kullanıcı bağlılığını (Engagement / Retention Loop)** maksimize etmek üzere tasarlanmıştır.

* **Video Eğitim Platformları (Coursera, Udemy, vb.):** Pasif izlemeye dayalıdır. Öğrenci videoyu izlerken "anlıyorum" hissine kapılır; ancak bu nörobilişsel düzeyde bir **"Yetkinlik Yanılsamasıdır" (Illusion of Competence - Bjork, 1994)**. Kaynak kapatıldığında bilginin geri çağrılma oranı %10'un altına düşer.
* **Flashcard Uygulamaları (Anki, Quizlet, vb.):** Basit ikili çağrımlarda (kelime ezberi, tıbbi terimler) etkilidir; ancak derin kavramsal kavrayış, prosedürel beceri, strateji seçimi ve transfer kabiliyetini ölçmekten ve inşa etmekten uzaktır.
* **Genel Amaçlı LLM Arayüzleri ve Ödev Çözücüler (ChatGPT, Photomath, vb.):** Öğrencinin yerine düşünerek problemi çözer. Bilişsel yükü (Cognitive Load) sıfırlayarak öğrencinin zihinsel kas yapmasını engeller. Öğrenci problemi çözdüğünü sanır, oysa çözümü sadece tüketmiştir.

Bu projenin nihai amacı, bir **"İçerik Dağıtım Sistemi"** değil, bilimsel temelli bir **"Kişisel Öğrenme Motoru" (Personal Learning Engine)** inşa etmektir.

---

## 2. VİZYONUN FORMÜLASYONU VE PARADİGMA DEĞİŞİMİ

```text
KLASİK EDTECH PARADİGMASI (İÇERİK MERKEZLİ)
[Müfredat/İçerik Havuzu] ─── (İteratif Dağıtım) ───> [Öğrenci] ───> [Soru/Quiz] ───> [Skor / XP]

BİZİM PARADİGMAMIZ (KOGNİTİF KONTROL DÖNGÜSÜ)
                                  +-----------------------+
                                  |     KULLANICI NİYETİ  |
                                  +-----------------------+
                                              │
                                              ▼
                                  +-----------------------+
                                  |   UYARLAMALI TEŞHİS   |
                                  +-----------------------+
                                              │
                                              ▼
+───────────────────────────────────────────────────────────────────────────────────────────+
|                                    ÖĞRENİCİ MODELİ (DEVLET)                               |
|   [Geri Çağrım]  [Kavramsal Şema]  [Prosedürel Beceri]  [Strateji]  [Transfer]  [Bellek]  |
+───────────────────────────────────────────────────────────────────────────────────────────+
       ▲                                                                            │
       │ Bayesian Güncelleme                                                        │ Karar
       │                                                                            ▼
+──────────────────────+                                                 +──────────────────+
|  HATA & KÖK NEDEN    | <─── [AKTİF HAMLE & BİLİŞSEL ÇABA] <─── [KİŞİSELLEŞTİRİLMİŞ|
|     TEŞHİSİ          |       (Minimal İskeleleme)                      MÜDAHALE]          |
+──────────────────────+                                                 +──────────────────+
       │
       ▼
+──────────────────────+
| ÇOK BOYUTLU YETKİNLİK| ───> [GECİKMELİ KALICILIK & TRANSFER] ───> [DÖNGÜYÜ GÜNCELLE]
|     DOĞRULAMASI      |
+──────────────────────+
```

### Temel Vizyon Aforizması:
> **"Sana daha fazla içerik göstermiyoruz. Ne bilmediğini buluyoruz. Neden anlamadığını teşhis ediyoruz. Zihinsel şemana en uygun pedagojik müdahaleyi seçiyoruz. Aktif olarak öğrenmeni sağlıyoruz. Gerçekten öğrenip öğrenmediğini kanıtlıyoruz. Ve unutmana fırsat vermeden bilgiyi en doğru anda yeniden çağırıyoruz."**

---

## 3. PROJE SINIRLARI: NE DEĞİLİZ?

Projenin sınırlarını kesinleştirmek, kapsam kaymasını (scope creep) engellemenin ilk şartıdır:

| Biz Ne Değiliz? | Neden Değiliz? | Biz Neyiz? |
| :--- | :--- | :--- |
| **Bir Chatbot Değiliz** | Serbest sohbet botları öğrencinin yönlendirmesine kapılır, konudan sapar ve cevabı açık eder. | **Kural Tabanlı & Sokratik Bir Pedagojik FSM (Sonlu Durum Makinesi)** |
| **Bir Video Kurs Değiliz** | Video izlemek pasif bir eylemdir; beyin minimum glikoz tüketir. | **Etkileşimli Problem Çözme ve Çözümlü Örnek İskeleleme Motoru** |
| **Bir Ödev Çözücü Değiliz** | Öğrenciye sonucu vermek onun yerine düşünmektir. | **Öğrencinin Kendi Kendine Bulmasını Sağlayan Minimal İpucu Sistemi** |
| **Bir Soru Bankası Değiliz** | Rastgele binlerce soru çözmek ayrıştırma becerisi kazandırmaz. | **Maksimum Bilgi Kazanımı (Fisher Info) Sağlayan Adaptif Görev Seçici** |
| **Bir Gamification Oyunu Değiliz** | Streak ve rozetler sahte ödül kimyası (dopamin) yaratır; yetkinlik sağlamaz. | **Gerçek, Kanıtlanmış Bilişsel Yetkinlik ve Metabilişsel Doğruluk Takipçisi** |

---

## 4. TEMEL BAŞARI KRİTERİ: RETENTION-DISCOUNTED LEARNING GAIN PER MINUTE (R-LGpM)

Endüstrideki sahte etkileşim metrikleri (DAU, oturum süresi, tamamlanan kart sayısı) reddedilmiştir. Başarı, **zaman birimi başına uzun vadeli net kognitif kazanım** ile ölçülür.

### Standart Yanılgı:
Anlık oturumda "Learning Gain Per Minute" (LGpM) ölçülürse:
$$\text{Naive LGpM} = \frac{\text{PostTest}_{\text{immediate}} - \text{PreTest}}{\text{Dakika}}$$
Bu formül sistemi hile yapmaya iter: Öğrenciye aşırı ipucu verilir, sorular blok halinde çözdürülür, anlık puan yüksek çıkar ama 7 gün sonra unutulur.

### Bizim Metriğimiz: R-LGpM
$$\text{R-LGpM} = \frac{\mathbb{E}[\text{Delayed Performance (t = 7d)}] - \text{PreTest Baseline}}{\text{Toplam Harcanan Süre (Teşhis + Öğrenme + Düzeltme + Tekrar)}}$$

Bu metrik, sistemi **"Arzu Edilen Zorlukları" (Desirable Difficulties)** uygulamaya zorlar. Anlık oturumda hızı düşürmek pahasına uzun vadeli kalıcılığı maksimize eden pedagojik müdahaleler (Interleaving, Faded Scaffolding, Productive Failure) ancak bu metrikle ödüllendirilir.

---

## 5. UZUN VADELİ ETKİ VE HEDEF KİTLE

### 5.1. Uzun Vadeli Etki ve Nihai Kazanımlar
1. **Bilişsel Bağımsızlık:** Sistemin nihai amacı öğrenciyi kendine bağımlı kılmak değil; öğrenciye kendi metabilişsel kalibrasyonunu kazandırmak ve zamanla iskeleyi tamamen çekmektir ([02-PRODUCT-PRINCIPLES.md](02-PRODUCT-PRINCIPLES.md), [03-LEARNER-MODEL.md](03-LEARNER-MODEL.md)).
2. **Kavramsal Sağlamlık:** Öğrenci bir üst konuya (örneğin Kalkülüs) geçtiğinde, alt konudaki (Cebir) kırılganlıklar nedeniyle duvara toslamamalıdır. Sistem temel şemaların sarsılmazlığını garanti eder ([04-KNOWLEDGE-AND-PREREQUISITE-GRAPH.md](04-KNOWLEDGE-AND-PREREQUISITE-GRAPH.md)).
3. **Zaman Tasarrufu:** Aynı konuyu 40 saatlik video serilerinde gezinerek yarım yamalak öğrenmek yerine, hedefe yönelik 3-4 saatlik yüksek yoğunluklu aktif bilişsel etkileşimle kalıcı ustalığa ulaştırır ([12-UX-AND-CORE-LEARNING-LOOP.md](12-UX-AND-CORE-LEARNING-LOOP.md)).

---

### 5.2. Hedef Kitle Personaları (Primary Target Personas)

Sistem, homojen bir öğrenci kitlesi varsayımını reddeder. Bilişsel mimari, öğrenme bilimleri literatüründe tanımlanan 3 kritik öğrenici arketipi üzerine kalibre edilmiştir:

#### Persona A: Ezberci Yüksek Kaygılı (The Anxious Rote-Memorizer)
* **Demografik & Psikolojik Profil:** Lise veya üniversiteye giriş sınavlarına (YKS, LGS, SAT) hazırlanan, yüksek başarı hedefleyen ancak yoğun **Matematik Kaygısı (Math Anxiety - Ashcraft & Krause, 2007)** yaşayan öğrenci.
* **Bilişsel Model & Tipik Davranış:**
  * Formülleri ve algoritmaları anlamını sorgulamadan mekanik olarak ezberler.
  * Standart şablon soruları yüksek doğrulukla çözer; ancak sorunun yüzey özellikleri değiştiğinde veya ters köşe bir kavramsal tuzakla karşılaştığında duvara toslar.
  * Hata yapmaktan aşırı korkar; hata yaptığında bunu bir öğrenme fırsatı değil, kendi zekasının yetersizliği olarak yorumlar (Sabit Zihin Yapısı - Dweck, 2006).
* **Telemetri & Zihinsel İzler:**
  * Aşırı uzun başlangıç latensi ($RT > 45$ saniye; adım atmaktan çekinme / donma).
  * İlk zorlanmada seri biçimde ipucu butonuna basma (Bottom-Out Hint Abuse eğilimi).
  * Düşük bilişsel verimlilik skoru ($E < -1.0$; aşırı kognitif yüklenme).
  * Çözüm tahtasında sık silgi kullanımı ve geri adımlar.
* **Sistemin Pedagojik Reçetesi:**
  * **Somutluk Sönümlemesi (Eksen 4):** Doğrudan soyut cebir yerine Al-Harezmi Alan Modeli ve Cebir Karoları ile somut başlangıç ([11-CONTENT-AND-REPRESENTATION-SYSTEM.md](11-CONTENT-AND-REPRESENTATION-SYSTEM.md)).
  * **Karantina Sandbox'ı (Eksen 7):** Üretici Başarısızlık (PF) modunda hataların puanı düşürmediğinin görsel olarak güvenceye alınması ([09-MASTERY-AND-ASSESSMENT-MODEL.md](09-MASTERY-AND-ASSESSMENT-MODEL.md)).
  * **Afektif Şalter ve Şefkatli Müdahale (Eksen 7):** Hüsran skoru $F_{\text{score}} \ge 0.85$ olduğunda sistemi dondurup tarihsel normalizasyon ve nefes molası sağlama ([06-ADAPTIVE-TEACHING-ENGINE.md](06-ADAPTIVE-TEACHING-ENGINE.md), [07-AI-TUTOR-BEHAVIOR-SPEC.md](07-AI-TUTOR-BEHAVIOR-SPEC.md)).
  * **Kademeli Eksiltme (Faded Scaffolding):** Tam çözümlü örneklerden adım adım bağımsızlığa yumuşak geçiş.
* **Hedeflenen Bilişsel Dönüşüm:** Formül ezberine dayalı kırılgan performanstan, derin kavramsal şemalara ve hata yapmaktan korkmayan bilişsel öz-yeterliğe geçiş.

#### Persona B: Hızlı Tahminci / Dürtüsel (The Impulsive Rapid Guesser)
* **Demografik & Psikolojik Profil:** Dikkat süresi kısa, video oyunları ve sosyal medya formatlarına alışkın, hızlı sonuç isteyen, bilişsel çaba harcamaktan kaçınan öğrenci.
* **Bilişsel Model & Tipik Davranış:**
  * Problemin derin yapısını analiz etmek yerine **Sistem 1 (Hızlı, Otomatik, Sezgisel - Kahneman, 2011)** dürtüleriyle hareket eder.
  * Soruyu okumadan gözüne çarpan ilk sayılarla dört işlem yapar; şık veya kutu varsa rastgele sayılar dener (Brute-force / Trial & Error).
  * Aşırı Özgüven Yanılgısı (Overconfidence Bias) sergiler; yanlış yaptığında bunu "dikkatsizlik" sanarak hızını kesmez.
* **Telemetri & Zihinsel İzler:**
  * Anormal kısa reaksiyon süresi ($RT < 3.5$ saniye - Rapid Guessing anomalisi).
  * Yüksek güven beyanı ($c = 1.0$) ile birlikte yüksek hata oranı ($y = 0$).
  * Ratcliff Drift-Diffusion Modelinde (DDM) dağınık ve yönelimsiz drift hızı ($v$).
  * Karakteristik Buggy Rule işletimi (Örn: Non-Zero Product Bug, Freshman's Dream - [08-ERROR-AND-MISCONCEPTION-ENGINE.md](08-ERROR-AND-MISCONCEPTION-ENGINE.md)).
* **Sistemin Pedagojik Reçetesi:**
  * **Hızlı Tahmin Avcısı (Rapid Guessing Filter - Eksen 6):** 3.5 saniye altındaki yanıtlara doğru olsa bile yetkinlik ve ilerleme kredisi vermeme ([09-MASTERY-AND-ASSESSMENT-MODEL.md](09-MASTERY-AND-ASSESSMENT-MODEL.md)).
  * **Brier Proper Scoring Kuralı (Eksen 6):** Aşırı özgüvenli yanlışlarda katı ceza puanı ($10 - 20(1 - 0)^2 = -10$ puan) ile kalibrasyon şoku yaşatma ([03-LEARNER-MODEL.md](03-LEARNER-MODEL.md)).
  * **Sezgi Freni Protokolü (CRT Probing - Eksen 3):** Sistem 1'in dürtüsel cevabını zorla 3 saniye dondurup Sistem 2'yi devreye sokan Sokratik fren ([07-AI-TUTOR-BEHAVIOR-SPEC.md](07-AI-TUTOR-BEHAVIOR-SPEC.md)).
  * **Zorunlu Ara Adım Doğrulaması:** Çözüm tahtasında adım yazmadan nihai sonuca atlamayı engelleyen AST kapısı ([12-UX-AND-CORE-LEARNING-LOOP.md](12-UX-AND-CORE-LEARNING-LOOP.md)).
* **Hedeflenen Bilişsel Dönüşüm:** Dürtüsel ve yüzeysel tahmincilikten, deliberatif strateji seçimi yapabilen, kendi düşüncesini denetleyen (metabilişsel) olgun bir problem çözücüye dönüşüm.

#### Persona C: İmposter Başarılı (The Imposter Achiever / Low Self-Efficacy)
* **Demografik & Psikolojik Profil:** Sınıfında veya okulunda başarılı, ödevlerini aksatmayan ancak içsel olarak "Ben aslında matematikten anlamıyorum, sadece şans eseri yapıyorum" duygusu (İmposter Sendromu - Clance & Imes, 1978) yaşayan öğrenci.
* **Bilişsel Model & Tipik Davranış:**
  * Zihinsel şeması ve matematiksel temeli sağlamdır; adımları doğru işletir.
  * Ancak sürekli dışsal bir onaya ihtiyaç duyar. Kendi muhakemesine güvenmediği için her adımda ipucu veya teyit arar.
  * Tip-2 Sinyal Tespit Kuramı (SDT) analizinde aşırı muhafazakar karar kriterine ($c_2 > +0.3$) ve asimetrik kalibrasyona sahiptir.
* **Telemetri & Zihinsel İzler:**
  * Yüksek sembolik doğruluk oranı ($P(Y=1) \ge 0.90$).
  * Doğru çözümlere rağmen sürekli en düşük güven düzeylerini ($c \in \{0.25, 0.50\}$) işaretleme.
  * Yüksek Tip-2 duyarlılık ($d'_2 > 1.8$) ile çelişen yüksek Beklenen Kalibrasyon Hatası ($ECE$).
  * İpucu butonuna tıklayıp yardım metnini okumadan doğru cevabı yazma (onay bağımlılığı).
* **Sistemin Pedagojik Reçetesi:**
  * **Güvence Kesintisi ve İpucu Kilidi (Reassurance Weaning - Eksen 6 & Eksen 3):** Doğru adımlar atan öğrencinin ipucu butonunu kasten kilitleme ve "Buna ihtiyacın yok, kendine güven!" müdahalesi ([03-LEARNER-MODEL.md](03-LEARNER-MODEL.md), [07-AI-TUTOR-BEHAVIOR-SPEC.md](07-AI-TUTOR-BEHAVIOR-SPEC.md)).
  * **Gizli Değerlendirme (Stealth Assessment - Eksen 2):** Öğrenciye sınav stresi yaşatmadan arka planda örtük telemetriyle yetkinliğini tescilleme ([09-MASTERY-AND-ASSESSMENT-MODEL.md](09-MASTERY-AND-ASSESSMENT-MODEL.md)).
  * **Metabilişsel Güvenilirlik Aynası:** Öğrencinin yüzüne ampirik veriyi koyma: *"Doğruluk oranın %94 ama güven beyanın %35; beynin düşündüğünden çok daha yetkin!"*
  * **Metabilişsel İskelenin Hızla Buharlaşması:** Seviye 3'e hızla geçirilerek ekrandaki tüm güven ve onay kutucuklarının temizlenmesi.
* **Hedeflenen Bilişsel Dönüşüm:** Dışsal onay bağımlılığından, ampirik verilerle kanıtlanmış sarsılmaz içsel öz-yeterlik ve bilişsel özerkliğe geçiş.

---

### 5.3. Anti-Personalar (Sistem Kimler İçin Kesinlikle Değildir?)

Kapsam kaymasını (Scope Creep) ve yanlış ürün kararlarını önlemek amacıyla sistemin **kesinlikle hizmet etmeyeceği** 3 anti-persona belirlenmiştir:

#### Anti-Persona 1: Ödev Çözdürücüler ve Hızlı Kopyacılar (The Homework-Dodger / Copy-Paster)
* **Kullanıcı Beklentisi:** Telefonun kamerasını açıp soru fotoğrafını yüklemek, tek tıkla tam çözümü ve sonucu alıp ödev defterine kopyalamak; düşünmeden sınıfı geçmek.
* **Sistemin Tavrı & Reddi:** Sistem bir "Ödev Çözücü" değildir. Zero-Leakage Guardrail ([07-AI-TUTOR-BEHAVIOR-SPEC.md](07-AI-TUTOR-BEHAVIOR-SPEC.md)) nedeniyle sistem cevabı asla doğrudan vermez. Kullanıcıyı aktif ara adımlar yazmaya zorlar. Bu kullanıcı sistemi "yavaş, zor ve kullanışsız" bulacaktır ve platform bu kaybı bilinçli olarak göze almıştır.

#### Anti-Persona 2: Rozet ve Sahte Streak Avcıları (The Casual Gamification Junkie)
* **Kullanıcı Beklentisi:** Günde 45 saniye uygulamayı açıp iki kelime eşleştirerek 400 günlük "streak" (seri) sürdürmek, XP ve elmas kazanıp liglerde yükselmek; sahte bir "çalışıyorum" tatmini yaşamak.
* **Sistemin Tavrı & Reddi:** Sistem sahte ödül kimyasıyla (Dopamine Trap) bağlılık üretmez. Günlük 20 dakikalık yüksek bilişsel çaba (Desirable Difficulties) gerektirir. Sırf streak bozulmasın diye tasarlanmış anlamsız 1 dakikalık görevler sisteme giremez ([02-PRODUCT-PRINCIPLES.md](02-PRODUCT-PRINCIPLES.md)).

#### Anti-Persona 3: Pasif Video Tüketicileri (The Binge-Watching Couch Learner)
* **Kullanıcı Beklentisi:** Yatakta uzanarak 6 saat kesintisiz "Tüm Cebir Konu Anlatımı" videosu izlemek ve "öğrendim" hissine sığınarak bilişsel rahatlık yaşamak.
* **Sistemin Tavrı & Reddi:** Sistemde pasif olarak izlenebilecek tek bir uzun video dahi yoktur. Öğrenme; Productive Failure, interaktif simülasyon, somutluk sönümlemesi ve çözüm tahtasındaki aktif sembolik eylemlerle gerçekleşir ([11-CONTENT-AND-REPRESENTATION-SYSTEM.md](11-CONTENT-AND-REPRESENTATION-SYSTEM.md), [12-UX-AND-CORE-LEARNING-LOOP.md](12-UX-AND-CORE-LEARNING-LOOP.md)). Sürekli pasif kalmak isteyen kullanıcı elenecektir.
