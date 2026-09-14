# 02-PRODUCT-PRINCIPLES.md
# ÜRÜN PRENSİPLERİ VE PEDAGOJİK ANAYASA
## Tasarım Dogmaları, Anti-Pattern'ler ve Değerleme Hiyerarşisi

---

## 1. TEMEL ÜRÜN PRENSİBİ VE DEĞERLEME HİYERARŞİSİ

Bu platform tek bir varoluş amacıyla tasarlanmıştır:
> **"Kullanıcıya azami miktarda içerik tüketici yaptırmak değil; minimum zamanda maksimum kalıcı, aktarılabilir ve bağımsız bilişsel yetkinlik kazandırmaktır."**

### Kırılmaz Değerleme Hiyerarşisi:
Herhangi bir ürün, UX veya algoritma çatışmasında aşağıdaki sıralama katı biçimde geçerlidir:

```text
[ 1. Bilimsel Kalıcılık & Doğruluk (Retention & Correctness) ]
                     ▼
[ 2. Ölçülmüş Yetkinlik Bütünlüğü (Mastery Integrity) ]
                     ▼
[ 3. Bilişsel Bağımsızlık & Minimal Müdahale ]
                     ▼
[ 4. Kullanıcı Akıcılığı & Deneyim Kolaylığı ]
                     ▼
[ 5. Yüzeysel Etkileşim & Eğlence (Gamification / Time Spent) ]
```

---

## 2. 12 SARSILMAZ ÜRÜN VE PEDAGOJİK PRENSİP (THE 12 IMMUTABLE PRINCIPLES)

Sistem, eğitim bilimleri ve ileri psikometri literatüründeki 7 temel araştırma ekseninin ampirik bulgularına dayanan 12 anayasal ilke ile yönetilir:

### İlke 1: Doğruluk ve Kavrayış Derinliği > Hız (Correctness & Schema Depth Over Speed)
* **İlgili Eksen:** **Eksen 2 (İleri Psikometri & Çok Boyutlu Ölçme)** ve **Eksen 6 (Metabilişsel Kalibrasyon)**.
* **Bilişsel Mekanizma:** Hızlı yanıtlar genellikle yüzeysel tanıdıklığın (familiarity) ve Sistem 1 dürtüselliğinin ürünüdür. Ratcliff Drift-Diffusion Modelinde (DDM) zihinsel bilgi birikim hızı (drift rate $v$) ve karar sınırı ($a$) birlikte analiz edilir. Hızlı ama hatalı tahminler derin kavramsal şemanın yokluğunu gösterir.
* **Sistemik Kural:** Hızlı yanıtlar ödüllendirilmez; 3.5 saniyenin altındaki dürtüsel tıklamalar (Rapid Guessing) yetkinlik modelinde dikkate alınmaz ([09-MASTERY-AND-ASSESSMENT-MODEL.md](09-MASTERY-AND-ASSESSMENT-MODEL.md)). Zihinsel çaba harcanarak ve ara adımlar doğrulanarak ulaşılan çözümler en yüksek ağırlığı alır.

### İlke 2: Sıfır Cevap Sızdırma ve Sokratik Zorunluluk (Zero-Leakage & Socratic Imperative)
* **İlgili Eksen:** **Eksen 3 (Sokratik Diyalog & Zeki Öğretici Sistemler - ITS)**.
* **Bilişsel Mekanizma:** Öğrenciye cevabı veya bir sonraki işlem adımını doğrudan sunmak, çalışma belleğindeki üretici yükü (germane load) sıfırlar; zihinsel kas inşasını imkansız kılar (The Assistance Dilemma - Koedinger & Aleven, 2007).
* **Sistemik Kural:** AI Tutor hiçbir koşulda, öğrenci yalvarsa dahi nihai cevabı veya hazır cebirsel adımı açık etmez. 4 katmanlı iç monolog hattı ve deterministik **Zero-Leakage Regex Guardrail** (`rf"(x\s*=\s*{root}|kök\s*{root})"`), cevabın modele sızmasını %100 engeller ([07-AI-TUTOR-BEHAVIOR-SPEC.md](07-AI-TUTOR-BEHAVIOR-SPEC.md)). Tutor yalnızca soruyu soruyla açar.

### İlke 3: Mantıksal Bozuk Kuralların Deterministik Teşhisi (Buggy Rule Discrimination)
* **İlgili Eksen:** **Eksen 1 (Bilişsel Hata Anatomisi & Buggy Rules)**.
* **Bilişsel Mekanizma:** Öğrenciler matematikte rastgele hata yapmazlar; zihinlerinde mantıksal olarak tutarlı fakat yanlış çalışan "Bozuk Kurallar" (Buggy Rules - Brown & Burton, 1978; VanLehn, 1990) türetirler.
* **Sistemik Kural:** Hatalar basit bir "yanlış" etiketiyle geçiştirilemez. Sembolik Cebir Motoru (SymPy AST), kullanıcının yazdığı her ara adımı ayrıştırır. Sıfır-çarpım yanılgısını ($(x-3)(x+2)=10 \implies x-3=10$), lineer aşırı-genellemeyi ($(x+4)^2 = x^2 + 16$) veya değişken yok etmeyi ($x^2 = 6x \implies x=6$) anında yakalar ve öğrencinin karşısına o kuralın sınır ihlalini koyar ([08-ERROR-AND-MISCONCEPTION-ENGINE.md](08-ERROR-AND-MISCONCEPTION-ENGINE.md)).

### İlke 4: ZPD Termostatı ile Dinamik Zorluk Dengesi (ZPD Thermostat Balance)
* **İlgili Eksen:** **Eksen 4 (Temsili Akıcılık ve Bilişsel Yük Yönetimi)** ve **Eksen 7 (Dinamik İskeleleme)**.
* **Bilişsel Mekanizma:** Öğrenme, Vygotsky'nin Yakınsak Gelişim Alanında (ZPD) gerçekleşir. Görev çok kolaysa can sıkıntısı (boredom), çok zorsa kognitif aşırı yüklenme ve donma (cognitive freeze) oluşur. Paas & Van Merriënboer (1993) Bilişsel Verimlilik İndeksi ($E = \frac{z_P - z_R}{\sqrt{2}}$) ile zihinsel efor ve başarı eşzamanlı izlenir.
* **Sistemik Kural:** Sistem bir **ZPD Termostatı** gibi çalışır. $E < -1.0$ (kognitif boğulma) durumunda görev zorluğu derhal düşürülür ve iskele seviyesi ($S$) artırılır; $E > +1.0$ (otomatikleşme) durumunda iskele derhal buharlaştırılır ve araya ekleme (interleaving) başlatılır ([06-ADAPTIVE-TEACHING-ENGINE.md](06-ADAPTIVE-TEACHING-ENGINE.md)).

### İlke 5: Duygudurumsal Güvenlik ve Afektif Şalter (Affective Safety & Circuit Breaker)
* **İlgili Eksen:** **Eksen 7 (Duygudurumsal Dinamikler & Üretici Başarısızlık)**.
* **Bilişsel Mekanizma:** Bilişsel kafa karışıklığı (confusion), öğrenmeyi tetikleyen yararlı bir motordur; ancak 120-180 saniyeyi aşan ve çözümsüz kalan kafa karışıklığı doğrudan **Yıkıcı Hüsrana (Destructive Frustration)** ve **Öğrenilmiş Çaresizliğe** evrilir (D'Mello & Graesser, 2012).
* **Sistemik Kural:** Sistem öğrencinin latens donmasını, öfke tıklamalarını (rage clicks) ve çaresizlik ifadelerini HMM ile izler. Hüsran skoru $F_{\text{score}} \ge 0.85$ olduğunda **Afektif Şalter (Circuit Breaker)** derhal iner: Oturum durdurulur, ekran karartılır, tarihsel normalizasyon ("Al-Harezmi de burada takılmıştı") ile nefes aldırılır ve düşük yüklü çözümlü örneğe pivot edilir; o seanstaki zorlanma psikometrik ceza olarak işlenmez ([06-ADAPTIVE-TEACHING-ENGINE.md](06-ADAPTIVE-TEACHING-ENGINE.md), [12-UX-AND-CORE-LEARNING-LOOP.md](12-UX-AND-CORE-LEARNING-LOOP.md)).

### İlke 6: Brier Proper Scoring ile Metabilişsel Dürüstlük (Metacognitive Proper Scoring Rule)
* **İlgili Eksen:** **Eksen 6 (Metabilişsel Kalibrasyon & Aşırı Güven Terapisi)**.
* **Bilişsel Mekanizma:** Ne bildiğini bilmek yetmez; neyi bilmediğini bilmek ve kendi bilgisine dair gerçekçi bir güven kalibrasyonuna sahip olmak (Nelson & Narens, 1990) uzmanlığın önkoşuludur. Tip-2 Sinyal Tespit Kuramı ($d'_2, c_2$) zihinsel izleme hassasiyetini gösterir.
* **Sistemik Kural:** Sistem Brier tabanlı **Proper Scoring Rule** uygular: $\text{Puan} = 10 - 20(c_i - y_i)^2$. Yanlış cevaba %100 güvenen öğrenci -10 ceza puanı alırken, bilmediğini dürüstçe itiraf eden öğrenci ($c=0.5 \land y=0$) +5 puanla korunur. Sahte özgüven ampirik olarak törpülenir ([03-LEARNER-MODEL.md](03-LEARNER-MODEL.md)).

### İlke 7: Üretici Başarısızlık ve Ölçme Karantinası (Productive Failure Sandbox Quarantine)
* **İlgili Eksen:** **Eksen 7 (Üretici Başarısızlık ve Keşif Dinamikleri - Manu Kapur, 2016)**.
* **Bilişsel Mekanizma:** Doğrudan kanonik formülü vermek öğrencinin zihinsel şema ihtiyacını hissetmesini engeller. Öğrenci önce biçimsel formülü bilmeden kendi sezgisel temsillerini üretmeli (Divergent SGR), sınırları keşfetmeli ve başarısız olmalıdır.
* **Sistemik Kural:** PF Keşif Aşaması (Exploration Sandbox) psikometrik ölçmeden tamamen karantinaya alınır. Bu fazda öğrencinin yaptığı hatalar iBKT veya 2PL-IRT CAT modellerinde slip veya ceza olarak işlenmez ($P(L)$ ve $\hat{\theta}$ dondurulur). Öğrenci cezalandırılma korkusu olmadan serbestçe hipotez üretir ([06-ADAPTIVE-TEACHING-ENGINE.md](06-ADAPTIVE-TEACHING-ENGINE.md), [09-MASTERY-AND-ASSESSMENT-MODEL.md](09-MASTERY-AND-ASSESSMENT-MODEL.md)).

### İlke 8: Somutluk Sönümlemesi ve Temsili Esneklik (Concreteness Fading)
* **İlgili Eksen:** **Eksen 4 (Temsili Akıcılık ve Bilişsel Yük Yönetimi - Fyfe et al., 2014)**.
* **Bilişsel Mekanizma:** Doğrudan soyut sembollerle başlamak kognitif boğulma yaratır; sadece somut nesnelerle kalmak ise soyutlama ve transfer kabiliyetini sınırlar (Bruner, 1966).
* **Sistemik Kural:** Her temel cebirsel kavram 3 aşamalı katı sönümleme protokolünden geçer: **Eylemsel / Somut (Cebir Karoları)** $\longrightarrow$ **İkonik / Şematik (Al-Harezmi Alan Taslağı)** $\longrightarrow$ **Saf Sembolik Denklem**. Somut aşamada yeterlik sağlanmadan soyut formül ekranına geçilemez ([11-CONTENT-AND-REPRESENTATION-SYSTEM.md](11-CONTENT-AND-REPRESENTATION-SYSTEM.md)).

### İlke 9: Dinamik İskeleleme ve Kademeli Eksiltme (Faded Scaffolding & Dynamic Fading)
* **İlgili Eksen:** **Eksen 3 (ITS Mimarisi)** ve **Eksen 4 (Bilişsel Yük Teorisi - Sweller, 1988; Kalyuga, 2003)**.
* **Bilişsel Mekanizma:** Acemiler tam çözümlü örneklere ihtiyaç duyarken, uzmanlaşan öğrenciler için bu iskeleler kognitif parazite (redundancy effect) dönüşür (Uzmanlık Tersinirliği Etkisi).
* **Sistemik Kural:** İskele kalıcı bir protez değildir. Renkl & Atkinson (2002) modeline göre geriye doğru eksiltilir: **Tam Çözümlü Örnek** $\longrightarrow$ **Son Adımı Eksik Örnek** $\longrightarrow$ **Yarı Çözümlü Örnek** $\longrightarrow$ **Tamamen Bağımsız Problem**. Öğrenci bağımsız adım atabildiği anda tüm ipuçları buharlaştırılır ([06-ADAPTIVE-TEACHING-ENGINE.md](06-ADAPTIVE-TEACHING-ENGINE.md)).

### İlke 10: Ayrıştırıcı Araya Ekleme ve Karıştırma (Discriminative Interleaving)
* **İlgili Eksen:** **Eksen 5 (Prosedürel Bellek ve Dinamik Aralıklandırma - Rohrer & Taylor, 2007)**.
* **Bilişsel Mekanizma:** Bloklanmış pratik ($AAAA \rightarrow BBBB$) sırasında öğrenci soruyu çözmek için hangi yöntemi seçeceğini düşünmez; sadece aynı algoritmayı mekanik işletir. Araya ekleme ($ABACDBC$) beyni problemin derin yapısını ayırt etmeye ve strateji seçimi yapmaya zorlar.
* **Sistemik Kural:** Bir düğümde temel prosedür tamamlanır tamamlanmaz sistem asla arka arkaya aynı şablonda soru sormaz. Önceki seviyelerden sorular (Doğrusal Denklemler, İki Kare Farkı, Tam Kare) harmanlanarak araya sokulur. Yöntem ayrıştırma doğrulanmadan yetkinlik onayı verilmez ([10-RETENTION-AND-SPACING-ENGINE.md](10-RETENTION-AND-SPACING-ENGINE.md)).

### İlke 11: Biyolojik Konsolidasyon ve Aralıklı Dağıtık Bellek (Distributed Spacing & Sleep Barrier)
* **İlgili Eksen:** **Eksen 5 (Prosedürel Bellek & ACT-R - Anderson, 1993; FSRS-4.5; Walker & Stickgold, 2006)**.
* **Bilişsel Mekanizma:** Prosedürel becerilerin sinaptik konsolidasyonu NREM ve REM uykusuna bağımlıdır. Aynı gün içinde 100 soru çözmek stabilite sağlamaz; aralıklı pratik bellek izini katlar.
* **Sistemik Kural:** Sistem günlük seansı 20 dakika ile sınırlar. Bir düğümün "Gecikmeli Kalıcılık" (Retention) kapısı, öğrenci araya en az 14 saatlik (gece uykusu içeren) süre koyup sürpriz bir çağrım testini başarıyla tamamlamadan açılamaz ([10-RETENTION-AND-SPACING-ENGINE.md](10-RETENTION-AND-SPACING-ENGINE.md), [12-UX-AND-CORE-LEARNING-LOOP.md](12-UX-AND-CORE-LEARNING-LOOP.md)).

### İlke 12: 5-Boyutlu Bağımsız Yetkinlik Bütünlüğü (5-Dimensional Mastery Integrity)
* **İlgili Eksen:** **Eksen 2 (İleri Psikometri)**, **Eksen 6 (Metabiliş)** ve **Eksen 7 (Transfer)**.
* **Bilişsel Mekanizma:** Bir öğrencinin tek bir soruyu doğru yapması veya şıklardan doğruyu tanıması yetkinliğin kanıtı olamaz (Yetkinlik Yanılsaması). Gerçek yetkinlik çok boyutlu ve aktarılabilirdir.
* **Sistemik Kural:** Bir bilgi düğümü ancak 5 bağımsız kapıyı eksiksiz geçtiğinde "Mastered" kabul edilir: **1. Çağrım Akıcılığı**, **2. Rutin Prosedürel Yürütme**, **3. Yöntem Seçimi ve Ayrıştırma**, **4. Ters Köşe ve Karşıt Örnek Yakalama**, **5. Uzak Transfer ve Modelleme** ([09-MASTERY-AND-ASSESSMENT-MODEL.md](09-MASTERY-AND-ASSESSMENT-MODEL.md)).

---

## 3. EKSEN 1-7 VE 12 İLKE ÇAPRAZ EŞLEŞTİRME MATRİSİ

Aşağıdaki matris, 12 Ürün İlkesi ile platformun 7 Bilişsel Araştırma Ekseni arasındaki ontolojik bağı ve sistemik yaptırımları özetler:

| İlke No ve Adı | İlgili Bilişsel Eksen | Kuramsal / Psikometrik Temel | Telemetri & Tetikleyici Gösterge | Sistemik Yaptırım / Gardiyan |
| :--- | :--- | :--- | :--- | :--- |
| **İlke 1: Doğruluk > Hız** | Eksen 2 & Eksen 6 | Ratcliff DDM ($v$), Tip-2 SDT ($d'_2$) | $RT < 3.5s$ (Rapid Guessing) | Yetkinlik puanı verilmez, AST adımı zorunlu tutulur. |
| **İlke 2: Sıfır Cevap Sızdırma** | Eksen 3 (ITS) | AutoTutor 5-Adım, Assistance Dilemma | Chatbot diyalog çıktısı ve regex taraması | Zero-Leakage Regex Guardrail ile cevap %100 sansürlenir. |
| **İlke 3: Bozuk Kural Teşhisi** | Eksen 1 (Hata) | VanLehn Mind Bugs, Brown & Burton | Sembolik ara adım eşitsizliği | SymPy AST ile spesifik yanılgı yakalanır, karşıt örnek açılır. |
| **İlke 4: ZPD Termostatı** | Eksen 4 & Eksen 7 | Paas Bilişsel Verimlilik ($E$), Vygotsky | $E < -1.0$ (aşırı yük) veya $E > +1.0$ | İskele seviyesi dinamik ayarlanır ($S \in \{0,..,4\}$), temsil değişir. |
| **İlke 5: Afektif Şalter** | Eksen 7 (Duygudurum) | D'Mello & Graesser HMM, Pekrun | $F_{\text{score}} \ge 0.85$, öfke tıklaması | Oturum dondurulur, şefkatli nefes modalı açılır, ceza dondurulur. |
| **İlke 6: Proper Scoring** | Eksen 6 (Metabiliş) | Nelson-Narens, Brier Scoring Rule | $c_i \in [0.25, 1.0]$ güven beyanı | $10 - 20(c-y)^2$ kuralıyla aşırı özgüvene -10 ceza verilir. |
| **İlke 7: PF Karantinası** | Eksen 7 (PF) | Manu Kapur Productive Failure | Keşif sandbox'ında üretilen SGR girdileri | iBKT $P(L)$ ve CAT $\hat{\theta}$ dondurulur; sıfır psikometrik ceza. |
| **İlke 8: Somutluk Sönümlemesi**| Eksen 4 (Yük) | Fyfe & Goldstone Concreteness Fading | Geometrik alan kavrayış doğruluğu | Somuttan ikonik ve semboliğe 3 aşamalı zorunlu geçiş rotası. |
| **İlke 9: Kademeli Eksiltme** | Eksen 3 & Eksen 4 | Sweller CLT, Kalyuga Expertise Reversal | Ardışık adım başarı serisi | Faded çözümlü örneklerden iskele otomatik buharlaştırılır. |
| **İlke 10: Ayrıştırıcı Araya Ekleme**| Eksen 5 (Bellek) | Rohrer & Taylor Interleaving, Underwood | Benzer şablon tekrarlama sayısı | Farklı düğümlerden izomorfik olmayan sorular çapraz enjekte edilir. |
| **İlke 11: Biyolojik Konsolidasyon** | Eksen 5 (Bellek) | ACT-R Aktivasyonu, Walker & Stickgold | Seanslar arası geçen biyolojik süre | Retention testi için $\ge 14$ saatlik uyku bariyeri şart koşulur. |
| **İlke 12: 5-Boyutlu Kapı** | Eksen 2 & Eksen 6/7 | Shute Stealth Assessment, Wald SPRT | 5 kapıdaki bağımsız başarı kanıtları | Tüm 5 kapı onaylanmadan düğüme "Mastered" statüsü verilmez. |

---

## 4. GERÇEK ÖĞRENMENİN DERECELENDİRİLMESİ (TAXONOMY OF TRUE LEARNING)

Bir kullanıcının "Anladım" demesi veya doğru bir şıkkı işaretlemesi öğrenmenin kanıtı değildir. Sistem 8 kademeli bir bilişsel kanıt piramidi uygular:

```text
                                [ 8. GECİKMELİ RETENTION ]
                                 (Haftalar sonra çağırabilme)
                                            ▲
                                [ 7. UZAK TRANSFER (Far Transfer) ]
                                 (Farklı bağlamdaki probleme uyarlama)
                                            ▲
                                [ 6. STRATEJİ VE AYRIŞTIRMA ]
                                 (Hangi yöntemi seçeceğine karar verme)
                                            ▲
                                [ 5. UYGULAMA (Routine Application) ]
                                 (Standart problemi desteksiz çözme)
                                            ▲
                                [ 4. PROSEDÜREL YÜRÜTME ]
                                 (Adım adım algoritmik sadakat)
                                            ▲
                                [ 3. KAVRAMSAL ANLAMA ]
                                 (Neden çalıştığını ve karşıt örnekleri bilme)
                                            ▲
                                [ 2. AKTİF GERİ ÇAĞIRMA (Recall) ]
                                 (Zihinden formülü/tanımı üretebilme)
                                            ▲
                                [ 1. TANIMA (Recognition) ]
                                 (Şıklarda görünce hatırlama - YETKİNLİK SAYILMAZ)
```

1. **Tanıma (Recognition):** En zayıf bellek izi. Şıklı sorularda doğru cevabı tanımak yetkinlik kabul edilmez.
2. **Geri Çağırma (Recall):** İpucu olmadan kuralı veya formülü zihinden boş ekrana yazabilme (Kapı 1).
3. **Kavramsal Anlama (Conceptual Understanding):** Kuralın sınırlarını bilme; kuralın geçerli olmadığı durumları (counterexamples) ayırt edebilme (Kapı 4).
4. **Prosedürel Yürütme (Procedural Execution):** Karmaşık bir işlemi ara adımlarda hata yapmadan sembolik olarak işletebilme (Kapı 2).
5. **Rutin Uygulama (Application):** Standart bir soruyu sıfır ipucuyla baştan sona çözebilme.
6. **Strateji Seçimi ve Ayrıştırma (Strategy Selection & Discrimination):** Karışık sorular arasında bu yöntemin hangisine uygulanacağını seçebilme (Kapı 3).
7. **Uzak Transfer (Far Transfer):** Yüzey özellikleri tamamen farklı bir problemde (fizik problemi, geometrik model) alt yapıyı tanıyıp yöntemi uygulayabilme (Kapı 5).
8. **Gecikmeli Kalıcılık (Retention):** 7 gün, 30 gün ve 90 gün sonra bu performansı aralıklı çağrımla tekrarlayabilme.

---

## 5. ÜRÜN ANTİ-PATTERN'LERİ (NELERİ KESİNLİKLE YAPMIYORUZ?)

### Anti-Pattern 1: Sahte Bağlılık Döngüleri (The Duolingo Trap)
* **Ret:** Öğrenciyi sırf uygulamayı açsın diye her gün anlamsız 1 dakikalık basit görevlerle meşgul edip 500 günlük "streak" yaptırmak.
* **Kabul Edilen:** Gerçek kalıcılık riski yoksa öğrenciyi rahat bırakmak. Bildirimi yalnızca bir kavram unutulma eşiğine (%10 Retrievability çöküşü) geldiğinde atmak.

### Anti-Pattern 2: Pasif Tüketim İllüzyonu (The Khan Academy Trap)
* **Ret:** 15 dakikalık video izletip ardından videodaki örneğin birebir aynısı olan 3 tane çoktan seçmeli soru çözdürmek.
* **Kabul Edilen:** Problem odaklı başlangıç (Productive Failure), çözümlü örneklerin kademeli eksiltilmesi (fading) ve aktif ara adım girdisi.

### Anti-Pattern 3: Tembelleştirici Yapay Zeka (The Chegg / Photomath Trap)
* **Ret:** Kullanıcı soruyu yapıştırır, AI adımları döker ve cevabı verir. Öğrenci "Hah anladım" der.
* **Kabul Edilen:** Minimal Gerekli İskeleleme (Minimal Necessary Scaffolding). AI asla sonraki adımı yazmaz; öğrenciye o adımı düşündürecek en küçük soruyu sorar.

### Anti-Pattern 4: Sabit Öğrenme Stili Etiketlemesi (The VAK Trap)
* **Ret:** Kullanıcıya profilinde "Sen görsel öğrenicisin" yazıp cebiri resimlerle, tarihi sesle anlatmaya çalışmak.
* **Kabul Edilen:** Konunun ontolojik yapısına uygun çoklu temsiller üretmek ve hangi temsilin öğrencinin bir sonraki performansını artırdığını ampirik olarak gözlemlemek.

---

## 6. TEMEL OPERASYONEL MÜHENDİSLİK PRENSİPLERİ

### 6.1. Deterministik Otorite Prensibi (Deterministic Authority)
* Matematik, mantık ve fen bilimlerinde hiçbir LLM nihai doğruluk otoritesi olamaz.
* Kullanıcının adımı **Sembolik Cebir Motoru (CAS / SymPy / AST)** tarafından doğrulanır.
* LLM yalnızca pedagojik niyetin insani bir dille öğrenciye aktarılmasından sorumludur ([16-TECHNICAL-ARCHITECTURE-OPTIONS.md](16-TECHNICAL-ARCHITECTURE-OPTIONS.md)).

### 6.2. İskelenin Geri Çekilmesi (Fading Principle)
* Verilen her ipucu, yardım ve açıklama geçicidir.
* Sistem bir iskele verdiğinde, öğrenici modelindeki "bağımsızlık skoru" düşer.
* Bir kavram ancak **hiçbir harici yardım almadan** çözüldüğünde yetkinlik kapısına yaklaşır ([06-ADAPTIVE-TEACHING-ENGINE.md](06-ADAPTIVE-TEACHING-ENGINE.md)).

### 6.3. Zihinsel Çabanın Korunması (Desirable Difficulty Principle)
* Kullanıcı zorlanıyorsa, sistem panikleyip cevabı vermez.
* Zorlanma (struggle), bilişsel şemanın yeniden inşa edildiği andır (Bjork, 1994).
* Sistem yalnızca "çaresizlik / kognitif kilitlenme" ($F_{\text{score}} \ge 0.85$) anında en küçük yönlendirmeyi yapar veya Afektif Şalteri indirir ([07-AI-TUTOR-BEHAVIOR-SPEC.md](07-AI-TUTOR-BEHAVIOR-SPEC.md)).
