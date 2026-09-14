# EMPIRICAL VALIDATION PROTOCOL (AMPİRİK DOĞRULAMA VE PİLOT DENEY PROTOKOLÜ)
## 50 Kişilik Lise Kohortu Pilot Testi, R-LGpM Etki Ölçümü ve Ön-Kayıtlı Bilimsel Araştırma Protokolü

**Protokol Kodu:** EXP-PLE-2026-COHORT-50  
**Ön Kayıt Platformu:** Open Science Framework (OSF Pre-Registration)  
**Hedef Kitle:** 9. ve 10. Sınıf Lise Öğrencileri ($N = 50$)  
**Çalışma Süresi:** 4 Hafta (14 Günlük Aktif Seans + 14 Günlük Gecikmeli Kalıcılık Ölçümü)  
**Tarih:** 14 Eylül 2026  

---

## 1. ARAŞTIRMA PROBLEMİ VE BİLİMSEL HİPOTEZLER

Geleneksel EdTech uygulamaları (Duolingo tarzı gamification, pasif video çözümleri ve doğrudan cevap veren LLM sohbet botları); anlık başarı hissi ("Illusion of Competence") yaratarak öğrencilerin bilişsel çaba göstermesini engellemekte ve uzun vadeli kalıcılığı düşürmektedir. 

Bu araştırma, Kişisel Öğrenme Motoru'nun (PLE) 7 Bilişsel Eksenine dayanan pedagojik mimarisini ampirik olarak test etmeyi amaçlar.

### 1.1. Araştırma Soruları (Research Questions)
- **RQ1 (Bellek & Sirkadiyen Kilit):** Günde azami 20 dakika ile sınırlandırılmış ve 14 saatlik sirkadiyen uyku bariyeri içeren FSRS-4.5 aralıklı tekrar seansları, geleneksel serbest süreli yığın çalışmaya göre 14 günlük gecikmeli kalıcılıkta istatistiksel olarak anlamlı bir üstünlük sağlar mı?
- **RQ2 (Sokratik Hat & Sıfır Sızıntı):** Doğrudan cevabı ifşa etmeyen, yanlışı bozuk kural (Buggy Rule) üzerinden Sokratik ipuçlarıyla düşündüren AI iskelelemesi, doğrudan çözümlü video/cevap gösteren sisteme göre transfer performansını artırır mı?
- **RQ3 (Çift Temsil & Geometrik Karolar):** Al-Harezmi alan karoları ($x^2 + bx$) ile sembolik ifadenin senkronize edilmesi, ezberci sembolik manipülasyona kıyasla derin kavramsal anlama ($d' \ge 0.80$) sağlar mı?

### 1.2. Formel İstatistiksel Hipotezler
$$H_0^{(1)}: \mu_{\text{R-LGpM}}^{(\text{PLE})} \le \mu_{\text{R-LGpM}}^{(\text{Kontrol})} \quad \text{vs.} \quad H_1^{(1)}: \mu_{\text{R-LGpM}}^{(\text{PLE})} > \mu_{\text{R-LGpM}}^{(\text{Kontrol})}$$
$$H_0^{(2)}: \text{ECE}^{(\text{PLE})} \ge \text{ECE}^{(\text{Kontrol})} \quad \text{vs.} \quad H_1^{(2)}: \text{ECE}^{(\text{PLE})} < \text{ECE}^{(\text{Kontrol})} \quad (\text{Üstbilişsel Doğruluk})$$

---

## 2. METRİKLER VE MATEMATİKSEL FORMÜLASYONLAR

### 2.1. Birincil Çıktı Metriği: R-LGpM (Retention-Discounted Learning Gain per Minute)
Geleneksel öğrenme kazancı (Hake, 1998), harcanan zamanı ve bilginin kalıcılığını hesaba katmaz. Bu protokolde **Zaman-Kalıcılık İndirimli Öğrenme Kazancı (R-LGpM)** birincil metrik olarak tanımlanmıştır:

$$\text{R-LGpM} = \frac{g \cdot S(14)}{T_{\text{active}}}$$

Burada:
1. **$g$ (Normalize Öğrenme Kazancı - Hake Gain):**
   $$g = \frac{\text{PostTest} - \text{PreTest}}{1.0 - \text{PreTest}}$$
   ($\text{PreTest} = 1.0$ olan öğrenciler için tavan etkisi düzeltmesi uygulanır).
2. **$S(14)$ (14 Günlük Sağkalım / Hatırlama Olasılığı):**
   Öğrencinin son seansından 14 gün sonra (Gün 28) uygulanan habersiz gecikmeli kalıcılık testinde kavramları hatırlama oranı (Kaplan-Meier sağkalım fonksiyonu).
3. **$T_{\text{active}}$ (Toplam Aktif Bilişsel Seans Süresi - Dakika):**
   Öğrencinin 14 gün boyunca sistemde fiilen matematiksel işlem yaparken geçirdiği toplam süre (15 saniyeyi aşan dalgınlık süreleri hariç).

### 2.2. İkincil Bilişsel Metrikler
1. **Beklenen Kalibrasyon Hatası (Expected Calibration Error - ECE):**
   Öğrencinin güven beyanı ($c_i$) ile gerçek doğruluk ($y_i$) arasındaki 10 kutulu sapma:
   $$\text{ECE} = \sum_{m=1}^{10} \frac{|B_m|}{N} \left| \overline{\text{acc}}(B_m) - \overline{\text{conf}}(B_m) \right|$$
2. **Fred Paas Bilişsel Verimlilik Skoru ($E$):**
   Standartlaştırılmış performans ($z_P$) ve zihinsel çaba ($z_R$):
   $$E = \frac{z_P - z_R}{\sqrt{2}}$$
   Yüksek $E$ skoru, düşük zihinsel yük ile yüksek doğru çözüm üretildiğini gösterir.
3. **Afektif Şalter Tetiklenme Oranı:**
   Öğrencinin çaresizlik ve öfke krizi yaşamadan akışta (Flow) kalma yüzdesi.

---

## 3. DENEYSEL TASARIM VE KATILIMCI KOHORTU

### 3.1. Katılımcı Profili ve Örneklem
- **Örneklem Büyüklüğü:** $N = 50$ (Lise 9. ve 10. sınıf öğrencileri).
- **Katılım Kriteri:** İkinci dereceden denklemler konusunu henüz okulda işlememiş veya başlangıç seviyesinde olan öğrenciler.
- **Dışlama Kriteri:** İleri düzey matematik olimpiyat eğitimi almış öğrenciler (tavan etkisini önlemek için).

### 3.2. Tabakalı Rastgele Atama (Stratified Randomization)
Öğrenciler ön-testte belirlenen matematik kaygısı (MAS skoru) ve başlangıç CAT latent yeteneğine ($\theta_{\text{pre}}$) göre çiftlenerek iki eşit gruba atanır:

```text
                                  50 Katılımcı
                                       │
                    [Ön Değerlendirme: CAT Teşhis + MAS Anketi]
                                       │
              ┌────────────────────────┴────────────────────────┐
              ▼                                                 ▼
      DENEY GRUBU (N = 25)                            KONTROL GRUBU (N = 25)
  - PLE Flutter Mobil Uygulaması                  - Geleneksel Dijital Çalışma
  - Al-Harezmi Geometrik Karoları                - Doğrudan Adım Çözümleri & Video
  - Sokratik Sıfır Sızıntı AI                    - Açıklamalı Yanıt Gösterimi
  - Günde 20 Dk + 14h Sirkadiyen Kilit           - Serbest Zamanlı Yığın Pratik
```

---

## 4. ÇALIŞMA PROTOKOLÜ VE ZAMAN ÇİZELGESİ

```text
GÜN 0           GÜN 1 - 14 (MÜDAHALE FAZI)              GÜN 14          GÜN 28
  │                         │                              │               │
  ├─ Ön-Test (CAT)          ├─ Deney: Günde 20 dk seans    ├─ Son-Test     ├─ Gecikmeli Kalıcılık
  ├─ MAS Kaygı Ölçeği       │  - 5 dk Isınma (FSRS)        │  (Post-Test)  │  Testi (S(14))
  └─ Bilgilendirilmiş Onay   │  - 10 dk ZPD Problem Tahtası └─ ECE Ölçümü   └─ R-LGpM Hesabı
                            │  - 5 dk Üstbiliş & Kilit
                            └─ Kontrol: Serbest modül
```

### 4.1. Günlük 20 Dakikalık Seans Akışı (Deney Grubu)
1. **00:00 - 05:00 (FSRS-4.5 Isınma):** Parça-bütün yayılımından gelen 3 adet kalıcılık tazeleme sorusu.
2. **05:00 - 15:00 (ZPD Kuadratik Çözüm Tahtası):** 
   - $x^2 + bx = c$ problemleri.
   - `MathTouchpad` ve `AlKhwarizmiCanvas` ile çift görünüm.
   - `ScratchpadOverlay` ile serbest çizim.
   - `BUG-QUAD-01..05` yakalandığında Sokratik iskele.
3. **15:00 - 20:00 (Üstbilişsel Kapanış & Proper Scoring):** 2 soru üzerinde güven beyanı ve kalibrasyon.
4. **20:00 (Sirkadiyen Kilit):** Ekran kilitlenir: *"Bugünkü 20 dakikalık derin odak seansın tamamlandı. Beyninin sinapsları konsolide etmesi için 14 saat mola veriyoruz."*

---

## 5. İSTATİSTİKSEL GÜÇ VE VERİ ANALİZ PLANI

### 5.1. Güç Analizi (Statistical Power Analysis)
- **Yazılım:** G*Power 3.1.9.7
- **Test Türü:** ANCOVA (Analiz Kovaryatı: Ön-test $\theta_{\text{pre}}$ ve MAS kaygı puanı)
- **Parametreler:**
  - Anlamlılık Düzeyi: $\alpha = 0.05$ (Tek yönlü)
  - İstatistiksel Güç ($1 - \beta$): $0.80$
  - Asgari Tespit Edilebilir Etki Büyüklüğü: Cohen's $d = 0.40$ (Orta-Yüksek etki)
  - Gerekli Toplam Örneklem: $N = 48$ (Çalışmamız $N = 50$ ile %82.4 güce sahiptir).

### 5.2. İstatistiksel Testler
1. **Birincil Analiz (R-LGpM Üstünlüğü):** Deney ve kontrol grupları arasında Bağımsız Örneklem $t$-testi ve ANCOVA ($F$-testi, $p < 0.05$).
2. **Sağkalım Analizi (Kalıcılık Eğrisi):** Kaplan-Meier sağkalım eğrisi ve Log-Rank (Mantel-Cox) testi ile Gün 28 hatırlama farkı.
3. **Üstbilişsel Kalibrasyon:** Deney ve Kontrol grupları için ECE farkının Wilcoxon işaretli sıra testi ile kıyaslanması.

---

## 6. ETİK ONAY, GİZLİLİK VE VERİ YÖNETİŞİMİ

1. **Reşit Olmayan Katılımcı Koruması:** Katılımcılar 18 yaşından küçük lise öğrencileri olduğu için velilerinden yazılı **"Aydınlatılmış Veli Onam Formu"** (Parental Informed Consent) ve öğrencilerden **"Bilgilendirilmiş Çocuk Rıza Formu"** (Child Assent) alınır.
2. **Sıfır Kişisel Veri Güvencesi:** Öğrenci isimleri veritabanına asla işlenmez; her öğrenci `STU-001` .. `STU-050` şeklinde anonimleştirilmiş araştırma kodlarıyla temsil edilir.
3. **Açık Bilim ve Tekrarlanabilirlik:** Deney başlamadan önce bu protokol OSF üzerinde zaman damgasıyla ön-kayıt (Pre-registration) altına alınacaktır. Anonimleştirilmiş telemetri veri seti ve R analiz betikleri kamuya açık paylaşılacaktır.

---

## 7. BAŞARI KRİTERLERİ VE PİLOT KABUL EŞİKLERİ

Pilot çalışmanın başarıyla tamamlanmış ve hipotezlerin doğrulanmış sayılması için aşağıdaki 3 eşik şart koşulmuştur:
1. **$\text{R-LGpM}$ Etki Büyüklüğü:** Deney grubunun R-LGpM ortalaması, kontrol grubundan en az **$d \ge 0.35$** standart sapma daha yüksek olmalıdır ($p < 0.05$).
2. **ECE İyileşmesi:** Deney grubunun beklenen kalibrasyon hatası $\text{ECE} \le 0.10$ seviyesine inmelidir (Kontrol grubundan anlamlı derecede düşük).
3. **Afektif Şalter Güvenliği:** 14 günlük seanslarda hiçbir öğrenci kalıcı matematik kaygısı veya yıkıcı hüsran krizine sürüklenmemelidir (Şalter tetiklenme oranı $< %8$).
