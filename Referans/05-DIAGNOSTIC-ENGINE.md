# 05-DIAGNOSTIC-ENGINE.md
# UYARLAMALI TEŞHİS MOTORU (ADAPTIVE DIAGNOSTIC ENGINE)
## Bilgisayarlı Uyarlamalı Test (CAT), Fisher Bilgi Matrisi ve Hızlı Başlangıç Mimarisi

---

## 1. SUBSYSTEM 10-SORU MATRİSİ

1. **Neden Var?** Yeni bir öğrencinin ne bildiğini ve hangi önkoşullarda eksiği olduğunu 45 dakikalık bir sınavla bezdirmeden, en az sayıda soruyla hızla tespit etmek için.
2. **Hangi Problemi Çözer?** Kullanıcıya zaten bildiği şeyleri baştan anlatan "sıkıcı eğitim" veya temeli olmayan öğrenciyi doğrudan zor konuya sokan "ezici eğitim" açmazını çözer.
3. **Girdiler:** Kullanıcının öğrenme hedefi (Goal), her teşhis sorusuna verilen cevap, işlem süresi, güven beyanı (%25-%100).
4. **Tuttuğu Durum:** Tahmini gizil yetenek ($\hat{\theta}$), tahminin standart hatası ($SE(\hat{\theta})$), test edilmiş düğümler kümesi, aday önkoşul açığı hipotezleri.
5. **Aldığı Kararlar:** Bilgi kazanımını (Information Gain) maksimize edecek sıradaki sorunun seçimi, teşhisin ne zaman sonlandırılacağı (stopping rule), müfredat grafına hangi düğümden girileceği.
6. **Çıktılar:** Başlangıç yetkinlik vektörü $\vec{M}_0$, doğrulanmış önkoşul eksiklikleri listesi, kişisel başlangıç rotası.
7. **Çalıştığını Nasıl Anlarız?** Ortalama 4.2 soruda $SE(\hat{\theta}) < 0.35$ eşiğine ulaşılması ve teşhisin önerdiği başlangıç seviyesinde öğrencinin başarı oranının ZPD (%60-%75) bandına oturmasıyla.
8. **Nasıl Çöker?** Şans eseri doğru yapma (guessing) veya basit bir dalgınlıkla yanlış yapma (slip) durumunda aşırı agresif karar verip rotayı saptırmasıyla.
9. **MVP Kapsamı:** 2PL IRT tabanlı, maksimum 5 soruluk kural tabanlı adaptif CAT motoru.
10. **Geleceğe Bırakılanlar:** Çok boyutlu gizil sınıf analizleri (Multidimensional Cognitive Diagnostic Models - DINA/NIDA).

---

## 2. PSİKOMETRİK TEMEL: MADDE TEPKİ KURAMI (IRT) VE FISHER BİLGİSİ

Teşhis motoru klasik test teorisini (doğru sayısı / toplam soru) reddeder. Her sorunun ayırt ediciliğini ve zorluğunu matematiksel olarak modelleyen **2-Parametreli Lojistik Modeli (2PL IRT)** kullanır:

$$P(Y_j = 1 \mid \theta) = \frac{1}{1 + e^{-a_j(\theta - b_j)}}$$

* $\theta \in [-3.0, +3.0]$: Öğrencinin gizil matematiksel yetenek seviyesi.
* $b_j \in [-3.0, +3.0]$: Sorunun zorluk parametresi (Difficulty).
* $a_j \in [0.5, 2.5]$: Sorunun ayırt edicilik parametresi (Discrimination).

### Fisher Bilgi Fonksiyonu (Fisher Information):
Bir $j$ sorusunun mevcut $\theta$ düzeyinde sisteme sağladığı enformasyon miktarı:

$$I_j(\theta) = a_j^2 \cdot P_j(\theta) \cdot (1 - P_j(\theta))$$

Maksimum bilgi, $P_j(\theta) = 0.50$ olduğunda (yani öğrencinin soruyu doğru yapma ihtimali yazı-tura ile aynı olduğunda) elde edilir.

### Sıradaki Soru Seçim Kuralı:
Sistem havuzdaki henüz sorulmamış sorular arasından, öğrencinin o anki yetenek kestirimi $\hat{\theta}_t$ noktasında Fisher bilgisini maksimize eden soruyu seçer:

$$j^* = \arg\max_{j \in \text{Havuz}} I_j(\hat{\theta}_t)$$

---

## 3. DİNAMİK YETENEK KESTİRİMİ VE DURDURMA KURALI (STOPPING RULE)

Her cevaptan sonra yetenek kestirimi **Maksimum Olabilirlik (Maximum Likelihood Estimation - MLE)** veya **Beklenen Sonsal Dağılım (Expected A Posteriori - EAP)** ile güncellenir:

$$\hat{\theta}_{t+1} = \hat{\theta}_t + \frac{\sum_{i=1}^t a_i (y_i - P_i(\hat{\theta}_t))}{\sum_{i=1}^t I_i(\hat{\theta}_t)}$$

Yetenek tahmininin Standart Hatası (Standard Error):
$$SE(\hat{\theta}) = \frac{1}{\sqrt{\sum_{i=1}^t I_i(\hat{\theta})}}$$

### Durdurma Kuralı (Stopping Criteria):
Teşhis testi şu iki şarttan **herhangi biri** sağlandığında derhal sonlandırılır:
1. **Kesinlik Eşiği:** $SE(\hat{\theta}) \le 0.35$ (Yetenek yeterince dar bir güven aralığına sıkıştırıldı).
2. **Tavan Soru Sınırı:** Toplam soru sayısı $= 5$ (Öğrencinin bilişsel enerjisini tüketmemek için test zorla bitirilir; kalan belirsizlik öğrenme sırasında Stealth Assessment ile giderilir).

---

## 4. ÖNKOŞUL GRAFI ÜZERİNDE BİLGİ KAZANIMI DALLANMASI VE 2PL-IRT MADDE HAVUZU

Teşhis motoru, [04-KNOWLEDGE-AND-PREREQUISITE-GRAPH.md](04-KNOWLEDGE-AND-PREREQUISITE-GRAPH.md) dokümanında tanımlanan 30 düğümlü Cebir Ağı üzerinde çalışır. Her soru, graf üzerindeki belirli bir anahtar düğümü (Anchor Node) hedefleyen kalibre edilmiş bir 2PL-IRT maddesidir.

### 4.1. Kalibre Edilmiş Teşhis Maddeleri Havuzu (2PL-IRT Parameter Bank)
Aşağıdaki maddeler, Fisher bilgisini maksimize etmek ve DAG topolojisini minimum soruda taramak üzere optimize edilmiştir:

| Madde Kodu | Hedef Düğüm No ve Adı | Zorluk ($b_j$) | Ayırt Edicilik ($a_j$) | Örnek Teşhis Sorusu | Doğru Yanıt Sonrası Rota | Hatalı Yanıt Sonrası Rota |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CAT-ITEM-01** | `[N12]` Çarpanlara Ayırma ile Çözüm | $0.00$ | $2.10$ | $x^2 - 5x + 6 = 0$ denkleminin köklerini bulunuz. | İleri Test: `CAT-ITEM-02` (`[N20]`) | Geriye İzleme: `CAT-ITEM-03` (`[N06]`) |
| **CAT-ITEM-02** | `[N20]` Diskriminant ve Kök Türü | $+1.50$ | $1.95$ | $2x^2 + 4x - 7 = 0$ denkleminde köklerin reel/farklı olduğunu gösteriniz. | Zirve Transfer: `CAT-ITEM-08` (`[N29]`) | Seviye 3/4 Girişi: `[N15]` veya `[N18]` |
| **CAT-ITEM-03** | `[N06]` İki Kare Farkı Özdeşliği | $-1.20$ | $1.85$ | $x^2 - 9$ ifadesini çarpanlarına ayırınız. | Seviye 1 Onarımı: `CAT-ITEM-05` (`[N08]`) | Temel Aritmetik: `CAT-ITEM-04` (`[N02]`) |
| **CAT-ITEM-04** | `[N02]` Dağılma Özelliği | $-2.00$ | $1.70$ | $-3(2x - 4)$ ifadesini açıp sadeleştiriniz. | Seviye 1 Başlangıcı: `[N05]` | Seviye 0 Başlangıcı: `[N01]` |
| **CAT-ITEM-05** | `[N08]` Monik Üçterimli Çarpanlar | $-0.50$ | $2.00$ | $x^2 + 7x + 12$ ifadesini çarpanlarına ayırınız. | Seviye 2 Başlangıcı: `[N11]` & `[N12]` | Seviye 1 Başlangıcı: `[N06]` & `[N07]` |
| **CAT-ITEM-06** | `[N15]` Cebirsel Tam Kare | $+0.80$ | $1.80$ | $x^2 + 6x$ ifadesini tam kare yapmak için eklenecek sabit nedir? | Seviye 4 Girişi: `[N18]` | Seviye 3 Başlangıcı: `[N14]` & `[N15]` |
| **CAT-ITEM-07** | `[N18]` Kuadratik Formül | $+1.20$ | $1.90$ | $x^2 - 3x + 1 = 0$ denklemini kuadratik formülle çözünüz. | Seviye 5 Girişi: `[N22]` | Seviye 4 Başlangıcı: `[N17]` & `[N18]` |
| **CAT-ITEM-08** | `[N29]` Fizik Yörünge Transferi | $+2.20$ | $1.65$ | $h(t) = -5t^2 + 20t$ atışında roketin yere düştüğü anı bulunuz. | Seviye 6 Başlangıcı: `[N28]`-`[N30]` | Seviye 5 Başlangıcı: `[N22]`-`[N25]` |

---

### 4.2. Topolojik Bilgi Kazanımı ve Dallanma Algoritması
Teşhis testi daima tam orta noktadaki Kök Testi (`CAT-ITEM-01` $\to$ `[N12]`, $b = 0.0$) ile başlar. Her adımdan sonra öğrencinin $\hat{\theta}$ değeri güncellenir ve DAG önkoşul kısıtları altında Fisher bilgisini maksimize eden madde çağrılır:

```text
[ TEŞHİS ADIMI 1: KÖK TESTİ - Düğüm [N12] (b = 0.0, a = 2.10) ]
Soru: "x² - 5x + 6 = 0 denkleminin köklerini bulunuz."
├── DOĞRU CEVAP (θ̂ ≈ +0.85):
│     │
│     ▼
│   [ TEŞHİS ADIMI 2A: İLERİ SEVİYE & DİSKRİMİNANT - Düğüm [N20] (b = +1.5, a = 1.95) ]
│   Soru: "2x² + 4x - 7 = 0 denkleminde kök türünü diskriminant ile belirleyin."
│   ├── DOĞRU CEVAP (θ̂ ≈ +1.95):
│   │     │
│   │     ▼
│   │   [ TEŞHİS ADIMI 3A: UZAK TRANSFER - Düğüm [N29] (b = +2.2, a = 1.65) ]
│   │   ├── DOĞRU ──> SEVİYE 6'DAN BAŞLA ([N26]-[N30] İleri Düğümler)
│   │   └── YANLIŞ ──> SEVİYE 5'TEN BAŞLA ([N22]-[N25] Parabol & Fonksiyon)
│   │
│   └── YANLIŞ CEVAP (θ̂ ≈ +0.90):
│         │
│         ▼
│       [ ADIM 3B: TAM KARE & FORMÜL PROBU - Düğüm [N15] / [N18] (b = +0.8) ]
│       ├── DOĞRU ──> SEVİYE 4'TEN BAŞLA ([N17]-[N21] Formül & Strateji)
│       └── YANLIŞ ──> SEVİYE 3'TEN BAŞLA ([N14]-[N16] Geometrik & Cebirsel Tam Kare)
│
└── YANLIŞ CEVAP (θ̂ ≈ -0.85):
      │
      ▼
    [ TEŞHİS ADIMI 2B: ÖNKOŞUL GERİYE İZLEME - Düğüm [N06] (b = -1.2, a = 1.85) ]
    Soru: "x² - 9 ifadesini çarpanlarına ayırınız."
    ├── DOĞRU CEVAP (θ̂ ≈ -0.40):
    │     │
    │     ▼
    │   [ ADIM 3C: ÜÇTERİMLİ ÇARPANLARA AYIRMA - Düğüm [N08] (b = -0.5, a = 2.00) ]
    │   ├── DOĞRU ──> SEVİYE 2'DEN BAŞLA ([N10]-[N13] İkinci Dereceden Denklem Temelleri)
    │   └── YANLIŞ ──> SEVİYE 1'DEN BAŞLA ([N07]-[N09] Çarpanlara Ayırma Özelleşmesi)
    │
    └── YANLIŞ CEVAP (θ̂ ≈ -1.75):
          │
          ▼
        [ ADIM 3D: TEMEL DAĞILMA & İŞARET - Düğüm [N02] (b = -2.0, a = 1.70) ]
        Soru: "-3(2x - 4) ifadesini açıp sadeleştiriniz."
        ├── DOĞRU ──> SEVİYE 1'DEN BAŞLA ([N05]-[N06] Ortak Çarpan & İki Kare Farkı)
        └── YANLIŞ ──> SEVİYE 0'DAN BAŞLA ([N01]-[N04] Negatif Sayılar & Doğrusal Çözüm)
```

### 4.3. DAG Önkoşul Kısıtlı Fisher Bilgisi (DAG-Constrained CAT)
Standart CAT rastgele bir soru havuzundan seçim yaparken, sistemimiz DAG bağımlılık matrisini hesaba katar:
$$j^* = \arg\max_{j \in \text{Aday}} I_j(\hat{\theta}_t) \quad \text{koşul:} \quad \forall p \in \text{Anc}(N_j), \; P(L_p) \ge 0.40$$
Bir öğrenci `[N06]` İki Kare Farkı sorusunu yanlış yaptıysa, sistem `[N12]` veya `[N20]` gibi üst düzey düğümleri asla sormaz; arama uzayını derhal kök önkoşullara daraltır.

---

## 5. SOĞUK BAŞLANGIÇ KULLANICI DENEYİMİ (UX) VE RAPORLAMA

Öğrenciye asla bir sınav karnesi gibi "Başarısız oldun, puanın 40" denilmez. Rapor, [04-KNOWLEDGE-AND-PREREQUISITE-GRAPH.md](04-KNOWLEDGE-AND-PREREQUISITE-GRAPH.md) üzerindeki düğüm statülerini gösteren şeffaf ve güçlendirici bir zihinsel harita sunar:

```text
+-----------------------------------------------------------------------------+
|                     ZİHİNSEL HARİTANIZ HAZIRLANDI (3.5 Dk)                  |
+-----------------------------------------------------------------------------+
| Hedef: İkinci Dereceden Denklemler Ustalığı (Seviye 0 - Seviye 6)            |
| Tahmini Yetenek: θ̂ = -0.32 (Standart Hata SE = 0.31 ≤ 0.35 - TEST TAMAMLANDI)|
|                                                                             |
| SAĞLAM VE ONAYLANAN TEMELLERİNİZ:                                           |
|   ✓ [N01] Negatif Sayılarla İşlemler (%95 Usta)                             |
|   ✓ [N02] Dağılma Özelliği (%90 Usta)                                       |
|   ✓ [N04] Birinci Dereceden Lineer Denklem Çözme (%92 Usta)                 |
|   ✓ [N06] İki Kare Farkı Özdeşliği (%88 Usta)                               |
|                                                                             |
| TESPİT EDİLEN ZPD GELİŞİM ALANI (YAKINSAK HEDEF):                           |
|   ! [N08] Başkatsayısı 1 Olan Üçterimlileri Çarpanlara Ayırma (x² + bx + c) |
|   ! [N11] Sıfır Çarpım İlkesi (AB = 0 => A=0 ∨ B=0)                         |
|                                                                             |
| BAŞLANGIÇ ROTAMIZ:                                                          |
|   Zaten bildiğiniz temel konularla sizi oyalamayacağız.                     |
|   Doğrudan [N08] ve [N11] düğümlerini mühürleyerek Seviye 2'ye adım atıyoruz!|
|                                                                             |
|   [ ÖĞRENMEYE BAŞLA (18 Dk Kalan Günlük Seans) ]                            |
+-----------------------------------------------------------------------------+
```

Bu rapor ile öğrencinin yetkinliği somut düğümlerle tescillenir, gereksiz içerik tekrarı engellenir ve öğrencinin motivasyonu korunur.
