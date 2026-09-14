# 09-MASTERY-AND-ASSESSMENT-MODEL.md
# YETKİNLİK VE ÖLÇME MODELİ (MASTERY & ASSESSMENT MODEL)
## 5 Boyutlu Yetkinlik Kapısı, Karşıt Örnek Testi ve Sahte Öğrenmeyi Engelleme

---

## 1. SUBSYSTEM 10-SORU MATRİSİ

1. **Neden Var?** Bir öğrencinin tek bir soruyu şans eseri veya mekanik ezberle doğru yapmasını "bu konuyu öğrendi" kabul etmenin yıkıcı sonuçlarını engellemek için.
2. **Hangi Problemi Çözer?** "Yetkinlik yanılsamasını" (Illusion of Competence), şık tahminciliğini, sistemin açıklarını kullanarak puan toplamayı (gaming the system) ve yüzeysel anlamayı çözer.
3. **Girdiler:** 5 bilişsel boyuttaki adım bazlı performans kanıtları, çözüm süreleri, ters köşe test sonuçları, transfer görevi çıktıları.
4. **Tuttuğu Durum:** Her düğüm için 5 kapının onaylanma durumu (Gates 1-5 Passed/Pending), hile ve şans eseri tahmin şüphesi skoru.
5. **Aldığı Kararlar:** Düğümün "Mastered" (Usta) statüsüne geçip geçmeyeceği, hangi boyutta ek kanıt toplanması gerektiği, gerileme (demotion) olup olmayacağı.
6. **Çıktılar:** Yetkinlik sertifikasyonu, kognitif zayıflık teşhis raporu, FSRS aralıklı tekrar sıklık katsayısı.
7. **Çalıştığını Nasıl Anlarız?** Sistem tarafından "Mastered" damgası vurulan bir öğrencinin, 14 gün sonra desteksiz ve habersiz yapılan sürpriz bir testte en az %85 başarı göstermesiyle.
8. **Nasıl Çöker?** Kriterlerin aşırı katı tutulup öğrencinin hiçbir zaman konuyu bitiremeyerek tükenmesiyle veya aşırı gevşek tutulup sahte ustalık üretilmesiyle.
9. **MVP Kapsamı:** 5 Boyutlu Kapı Denetimi + Parametrik İzomorfik Soru Üreteci.
10. **Geleceğe Bırakılanlar:** Akran değerlendirmesi (peer instruction) ve öğrencinin başkasına konuyu anlatmasını değerlendiren LLM dinleyicileri.

---

## 2. 5 BOYUTLU YETKİNLİK KAPISI (THE 5-DIMENSIONAL MASTERY GATE)

Bir düğümün graf üzerinde "Yeşil / Mastered" statüsü kazanması için aşağıdaki 5 kapının **sırayla ve bağımsız olarak** açılması şarttır:

```text
+─────────────────────────────────────────────────────────────────────────────+
|                     5 BOYUTLU YETKİNLİK DOĞRULAMA KAPILARI                  |
+─────────────────────────────────────────────────────────────────────────────+
| [ KAPI 1: ÇAĞRIM AKICILIĞI (Recall Fluency) ]                               |
| Görev: Formülü veya temel kuralı hiçbir seçenek olmadan boş alana yaz.       |
| Örnek: "Kuadratik formülü yazınız."                                         |
| Kriter: Sıfır ipucu, < 20 saniye, %100 sembolik doğruluk.                   |
+─────────────────────────────────────────────────────────────────────────────+
| [ KAPI 2: RUTİN PROSEDÜREL YÜRÜTME (Procedural Execution) ]                 |
| Görev: 3 ardışık standart parametrik problemi sıfır yardımla çöz.           |
| Örnek: "x² - 7x + 12 = 0 denkleminin köklerini bulunuz."                    |
| Kriter: 3/3 başarı, ara adımlarda sıfır kural ihlali.                       |
+─────────────────────────────────────────────────────────────────────────────+
| [ KAPI 3: YÖNTEM SEÇİMİ VE AYRIŞTIRMA (Strategy Selection) ]                |
| Görev: Karışık 4 farklı denklem içinden bu yöntemin hangisine en uygun      |
| olduğunu seç ve nedenini açıkla.                                            |
| Örnek: "x² + 6x - 2 = 0 denklemini çözmek için neden çarpanlara ayırma      |
| yerine tam kareye tamamlama veya formül tercih edilmelidir?"                 |
| Kriter: Doğru yöntem tespiti + geçerli gerekçe seçimi.                      |
+─────────────────────────────────────────────────────────────────────────────+
| [ KAPI 4: TERS KÖŞE VE KARŞIT ÖRNEK (Counterexample Discrimination) ]       |
| Görev: Kuralın geçersiz olduğu veya tuzak barındıran problemi yakala.       |
| Örnek: "(x - 4)(x + 2) = 7 denkleminde x - 4 = 7 yazan öğrencinin hatası ne?"|
| Kriter: Kavramsal sınır ihlalini doğru tespit etme.                         |
+─────────────────────────────────────────────────────────────────────────────+
| [ KAPI 5: UZAK TRANSFER VE MODELLEME (Far Transfer & Application) ]         |
| Görev: Yüzey özellikleri tamamen farklı bir problemde denklemi kur ve çöz.  |
| Örnek: "Bir roketin fırlatıldıktan t saniye sonraki yüksekliği h(t) = -5t²  |
| + 40t + 10 metredir. Roket kaçıncı saniyede yere çarpar?"                   |
| Kriter: Sözel/fiziksel problemden standart ax² + bx + c formunu çıkarma ve  |
| kökleri fiziksel bağlama göre yorumlama (negatif zamanı eleme).             |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 3. SİSTEMİ KANDIRMAYI (GAMING THE SYSTEM) ENGELLEME MEKANİZMALARI

Öğrenciler genellikle öğrenmek yerine sistemin algoritmik açıklarını bularak "görevi tamamlandı" göstermeye çalışırlar (Baker et al., 2004). Platform, hedef kitle personalarının ([00-PROJECT-VISION.md](00-PROJECT-VISION.md)) zaaflarını da gözeterek bu hileleri aktif olarak engeller:

1. **Hızlı Tahmin Avcısı (Rapid Guessing Filter - Persona B Koruması):**
   * Eğer kullanıcı bir soruyu asgari okuma süresinin altında ($< 3.5$ saniye) cevaplarsa, sonuç doğru olsa dahi yetkinlik modeline pozitif katkı verilmez (İlke 1: Doğruluk > Hız - [02-PRODUCT-PRINCIPLES.md](02-PRODUCT-PRINCIPLES.md)). Sistem ardışık hızlı tahminlerde kullanıcıya zorunlu ara adım (scratchpad) girişi dayatır.
2. **İpucu Tüketme Hilesi ve Güvence Kilidi (Bottom-Out Hint Abuse & Reassurance Weaning - Persona A ve C Koruması):**
   * Kullanıcı soruyu çözmek yerine sürekli "İpucu Ver" butonuna basarak son adımdaki çözümü tüketirse (Persona A), sistem soru tipini değiştirir ve o düğümdeki $P(L)$ değerine ceza katsayısı uygular.
   * Doğru yapmasına rağmen sürekli güvence arayan İmposter öğrencilerde (Persona C) ise sistem "İpucu Ver" butonunu geçici olarak kilitler (*Reassurance Weaning* - [03-LEARNER-MODEL.md](03-LEARNER-MODEL.md), [07-AI-TUTOR-BEHAVIOR-SPEC.md](07-AI-TUTOR-BEHAVIOR-SPEC.md)).
3. **Parametrik İzomorfik Problem Üreteci (Zero-Memorization Engine):**
   * Bir sorunun rakamları asla statik değildir. SymPy tabanlı şablon motoru her denemede aynı derin matematiksel yapıya sahip, ancak sayısal kökleri ve katsayıları farklı rastgele problemler üretir:
$$ax^2 + bx + c = 0 \quad \text{burada } b^2 - 4ac > 0 \land a,b,c \in \mathbb{Z}$$
Kullanıcı çözümü ezberleyemez; algoritmayı işletmek zorundadır.

---

## 4. GİZLİ DEĞERLENDİRME (STEALTH ASSESSMENT) PROTOKOLÜ

Geleneksel eğitimdeki yüksek stresli, tek seferlik sınavlar özellikle yüksek kaygılı öğrencilerin (Persona A) gerçek yetkinliğini yansıtmaz (Test Anxiety - Ashcraft & Krause, 2007).

Bunun yerine sistem, **Valerie Shute'un Gizli Değerlendirme (Stealth Assessment)** ilkelerini uygular:
* Öğrenci test edildiğini bilmez; sadece bir sonraki ilgi çekici problemi çözer.
* Öğrencinin çözüm tahtasındaki imleç hareketleri, silgi kullanımı, adım aralarındaki bekleme süreleri (latens) arka plandaki Bayesian ağını ([03-LEARNER-MODEL.md](03-LEARNER-MODEL.md)) besler.
* Yetkinlik bir "sınav notu" değil, öğrencinin doğal problem çözme akışının matematiksel bir türevidir.
* Teşhis motorundan ([05-DIAGNOSTIC-ENGINE.md](05-DIAGNOSTIC-ENGINE.md)) gelen ilk $\hat{\theta}$ tahmininden sonra tüm kalıcı değerlendirmeler bu örtük telemetri hattı üzerinden yürütülür.

---

## 5. KEŞİF KUM HAVUZU VE ÖLÇME KARANTİNASI (EXPLORATORY SANDBOX QUARANTINE)

Üretici Başarısızlık (Productive Failure - PF) oturumlarında yapılan denemeler standart psikometrik modellerden tamamen izole edilir:

```text
[ SERBEST KEŞİF / PF DENEMESİ ] ────► [ PSİKOMETRİK KARANTİNA FİLTRESİ ]
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
    [ BKT P(L) VE CAT θ GÜNCELLEMESİ ]                           [ KEŞİF VE METABİLİŞSEL SKORLAR ]
    - Dondurulur (Freeze).                                       - Fikir Çeşitliliği İndeksi (D_ideas)
    - Hatalar "Slip" veya "Yetersizlik"                          - Bilişsel Sebat (Persistence Score)
      olarak cezalandırılmaz.                                    - Keşif Çabası (Effort Bonus)
```

1. **Psikometrik Ceza Muafiyeti:** Öğrenci henüz kanonik yöntem öğretilmeden önce zor bir denklemle ($x^2 + 6x - 2 = 0$) boğuşurken yaptığı yanlışlar, iBKT veya 2PL-IRT modellerinde slip/hata olarak işlenmez. Aksi halde öğrenci cezalandırılma korkusuyla risk almaktan ve sezgisel üretim yapmaktan kaçınır.
2. **Temsil Çeşitliliği Metriği ($D_{\text{ideas}}$):**
$$D_{\text{ideas}} = \sum_{k \in \{\text{Aritmetik, Cebirsel, Geometrik, Grafik}\}} \mathbb{I}(\text{Temsil } k \text{ denendi})$$
Sistem, doğru cevabı bulamasa bile en az iki farklı temsil düzleminde çözüm arayan öğrenciye **Bilişsel Keşif Primi (Exploratory Bonus)** tanımlar.
3. **Resmi Yetkinlik Başlangıç Koşulu:** 5 Boyutlu Yetkinlik Kapıları (Gates 1-5), yalnızca konsolidasyon tamamlanıp bağımsız pratik rejimi başladığında kayıt almaya başlar.
