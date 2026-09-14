# 10-RETENTION-AND-SPACING-ENGINE.md
# KALICILIK VE ARALIKLI TEKRAR MOTORU (RETENTION & SPACING ENGINE)
## ACT-R Bellek Aktivasyonu, FSRS-4.5 DSR Modeli, Parça-Bütün Matris Yayılımı, Sirkadiyen Uyku Bariyeri ve Kodlama Çeşitliliği

---

## 1. SUBSYSTEM 10-SORU MATRİSİ

1. **Neden Var?** Matematiksel yetkinlik bir seanslık "anladım" hissiyatıyla kalıcı hale gelmez. Zaman geçtikçe nöral sinapslardaki aktivasyon zayıflar, prosedürel üretim kuralları aşınır. Tekrar edilmeyen cebirsel kural unutulmaya mahkûmdur.
2. **Hangi Problemi Çözer?** Yığın çalışma (massed practice / cramming) sonucu oluşan sahte kalıcılığı, gereksiz aşırı tekrarın yol açtığı zaman israfını ve alt önkoşulların (ör. doğrusal denklem çözümü) izole şekilde tekrar tekrar sorularak öğrenciyi bezdirmesini önler.
3. **Girdiler:** Öğrencinin problem çözme geçmişi, adım bazlı çözüm süresi (latency), rating notu ($G \in \{1, 2, 3, 4\}$), seans zaman damgaları, uyku konsolidasyonu verisi, problem temsil modalitesi, graf önkoşul topolojisi.
4. **Tuttuğu Durum:** Her Bilgi Bileşeni (KC) için DSR durum vektörü $[D, S, R]^T$, son tekrar zamanı $t_{\text{last}}$, son seans modalitesi $M_{\text{last}}$, hiyerarşik yayılım önbelleği.
5. **Aldığı Kararlar:** Hangi konunun ne zaman tekrar edileceği, sıradaki seans için optimal aralık (ISI), alt önkoşulların örtük (implicit) güncellenme büyüklüğü, aynı gün tekrarlarının stabiliteye etki edip etmeyeceği.
6. **Çıktılar:** Bir sonraki önerilen tekrar tarihi ($t_{\text{next}}$), güncellenmiş kararlılık ($S'$), güncellenmiş zorluk ($D'$), tahmini anlık geri çağrılabilirlik ($R(t)$), alt beceri stabilite vektörü ($\Delta \mathbf{S}$).
7. **Çalıştığını Nasıl Anlarız?** Sistem tarafından hedeflenen hatırlama olasılığı ($R_{\text{target}} = 0.90$) bandında tutulan öğrencilerin, 30 ve 90 gün sonra yapılan habersiz denetim testlerinde $\ge \%88$ başarı göstermesiyle.
8. **Nasıl Çöker?** Uyku bariyeri dikkate alınmadan aynı gün yapılan 50 tekrarla stabilite şişirilirse, parça-bütün yayılımında aşırı iyimser çarpanlarla alt beceriler canlı sanılıp çürümeye terk edilirse.
9. **MVP Kapsamı:** FSRS-4.5 (17 parametre) + Parça-Bütün Matris Yayılımı + Sirkadiyen Uyku Filtresi + Kodlama Çeşitliliği Multiplier'ı.
10. **Geleceğe Bırakılanlar:** Öğrencinin kişisel EEG veya giyilebilir cihaz uyku kalitesi verisiyle FSRS parametrelerinin dinamik Bayesyen kalibrasyonu.

---

## 2. KURAMSAL TEMEL: MATEMATİKSEL HAFIZANIN AŞINMASI

Matematik bir kelime ezberi değildir; birbirini tetikleyen prosedürel üretim kurallarının (production rules) zincirlenmesidir. Bir cebir kuralının hafızadaki durumu John R. Anderson'ın ACT-R (Adaptive Control of Thought-Rational) kognitif mimarisiyle modellenir.

### 2.1. ACT-R Temel Aktivasyon Modeli (Anderson & Schooler, 1991)
Bir $i$ bilgi bileşeninin ($KC_i$) $t$ anındaki taban aktivasyon seviyesi ($A_i$):

$$A_i = \ln \left( \sum_{k=1}^n (t - t_k)^{-d} \right) + \beta_i$$

* $n$: Öğrencinin bu $KC$'yi geçmişte başarıyla çağırdığı pratik sayısı.
* $t_k$: $k$. çağrımın gerçekleştiği zaman damgası.
* $d$: Güç yasası bellek bozunma parametresi (tipik olarak $d \approx 0.5$).
* $\beta_i$: Düğümün kalıcı taban seviye gücü (öğrencinin genel matematik yatkınlığına bağlı bias).

### 2.2. Gecikme (Latency) ve Unutmanın Erken Uyarı Sinyali
Aktivasyon $A_i$ düştükçe, öğrencinin doğru cebirsel adımı belleğinden geri çağırıp tuvale yazması için harcadığı süre üstel olarak patlar:

$$\text{Latency}_i = F \cdot e^{-f \cdot A_i}$$

* $F$: Temel motor/okuma süresi ölçekleyicisi.
* $f$: Aktivasyon duyarlılık katsayısı.

> [!IMPORTANT]
> **Erken Teşhis Kuralı:** Öğrenci bir denklem adımını henüz yanlış yapmamış olsa bile, çözüm latensi medyan sürenin 2 katını aşıyorsa ($Latency > 2.0 \times \overline{Latency}$), aktivasyon kritik eşiğe inmiştir. Sistem bu durumu beklenen açık bir hata (lapse) gibi önceliklendirir.

---

## 3. FSRS-4.5 DSR MATEMATİKSEL MODELİ VE 17-PARAMETRE ANALİZİ

Sistem, geleneksel SM-2 veya HL-Leitner yerine Jarrett Ye tarafından geliştirilen modern **FSRS-4.5 (Free Spaced Repetition Scheduler)** modelini cebirsel ve prosedürel öğrenmeye uyarlayarak kullanır.

### 3.1. DSR Durum Uzayı
FSRS-4.5 her beceriyi 3 boyutlu bir durumda modeller:
1. **Difficulty ($D \in [1, 10]$):** Becerinin içsel bilişsel karmaşıklığı. Cebirde çok adımlı, negatif işaret tuzaklı işlemler yüksek $D$ değerine sahiptir.
2. **Stability ($S > 0$, gün):** Becerinin unutulmaya karşı direnci. Geri çağrılabilirliğin $\%90$'dan $\%81.8$'e düşmesi için gereken gün sayısı.
3. **Retrievability ($R \in [0, 1]$):** Aradan geçen $t$ gün sonra öğrencinin bu kuralı doğru uygulama olasılığı.

### 3.2. Değerlendirme Derecesi ($G \in \{1, 2, 3, 4\}$)
Öğrencinin problem adımındaki performansı 4 seviyeli bir nota dönüştürülür:
* **$G = 1$ (Again / Başarısız):** Kural ihlali, yanlış formül seçimi, işaret hatası veya kavramsal kilitlenme.
* **$G = 2$ (Hard / Zor):** Ağır duraksama ($Latency > 2.0 \times \overline{Latency}$), tereddütlü adım, ancak yardımsız doğru tamamlama.
* **$G = 3$ (Good / İyi):** Beklenen sürede, hatasız, standart prosedürel icra.
* **$G = 4$ (Easy / Kolay):** Akıcı, doğrudan, medyan sürenin yarısından kısa sürede kusursuz çözüm ($Latency < 0.5 \times \overline{Latency}$).

---

### 3.3. FSRS-4.5 Çekirdek Formülleri

#### A. İlk Kararlılık (Initial Stability)
Yeni bir $KC$ ile ilk karşılaşmada verilen nota göre ilk kararlılık atanır:
$$S_0(G) = w_{G-1} \quad \text{yani} \quad S_0 \in \{w_0, w_1, w_2, w_3\}$$

#### B. İlk Zorluk (Initial Difficulty)
$$D_0(G) = w_4 - e^{w_5 \cdot (G - 1)} + 1$$
Değer $[1, 10]$ aralığına kırpılır: $D_0 \leftarrow \min(\max(D_0, 1), 10)$.

#### C. Zorluk Güncellemesi (Difficulty Update)
$$\Delta D = -w_6 \cdot (G - 3)$$
Ortalama zorluğa çekilme (Mean Reversion) mekanizması ile:
$$D' = w_7 \cdot D_0(3) + (1 - w_7) \cdot (D + \Delta D)$$
$$D' \leftarrow \min(\max(D', 1), 10)$$

#### D. Geri Çağrılabilirlik Güç Yasası (Retrievability)
Son başarılı çalışmanın üzerinden $t$ gün geçtikten sonra anlık geri çağrılabilirlik:
$$R(t, S) = \left( 1 + \text{FACTOR} \cdot \frac{t}{S} \right)^{-0.5}$$
FSRS-4.5 standart uygulamasında $R(S) = 0.90$ eşleşmesi için $\text{FACTOR} = \frac{1}{0.9^2} - 1 = \frac{19}{81} \approx 0.23457$:
$$R(t, S) = \left( 1 + \frac{19}{81} \cdot \frac{t}{S} \right)^{-0.5}$$

#### E. Başarılı Hatırlama Sonrası Kararlılık Artışı ($G \ge 2$)
$$S'_r(D, S, R, G) = S \cdot \left( 1 + e^{w_8} \cdot (11 - D) \cdot S^{-w_9} \cdot \left( e^{w_{10}(1 - R)} - 1 \right) \cdot K(G) \right)$$
Burada derecelendirme düzeltme çarpanı $K(G)$:
$$K(G) = \begin{cases} w_{15}, & G = 2 \text{ (Hard)} \\ 1.0, & G = 3 \text{ (Good)} \\ w_{16}, & G = 4 \text{ (Easy)} \end{cases}$$

#### F. Unutma / Hata Sonrası Kararlılık Düşüşü ($G = 1$)
$$S'_f(D, S, R) = w_{11} \cdot D^{-w_{12}} \cdot \left( (S + 1)^{w_{13}} - 1 \right) \cdot e^{w_{14}(1 - R)}$$
Hafıza sıfırlanmaz; eski stabilite $(S+1)^{w_{13}}$ kuvvetinde kısmi bir tortu bırakır (Savings Effect - Ebbinghaus).

---

### 3.4. 17-Parametre Ağırlık Vektörü $\mathbf{w}$ ve Cebirsel Yorumları

Cebir ve prosedürel matematik öğrenme izleri için kalibre edilmiş FSRS-4.5 ağırlık vektörü:

$$\mathbf{w} = [0.4072, 1.1827, 3.1262, 15.4722, 7.2102, 0.5316, 1.0651, 0.0234, 1.6160, 0.1544, 1.0819, 1.9813, 0.0953, 0.2975, 0.2242, 0.2407, 2.9466]$$

| Parametre | Değer | Matematiksel Rolü | Cebirsel ve Prosedürel Anlamı |
| :--- | :---: | :--- | :--- |
| **$w_0$** | `0.4072` | $S_0(G=1)$ İlk Başarısızlık Stabilitesi | Öğrenci ilk denemede işaret veya parantez hatası yaparsa, bu becerinin kararlılığı yaklaşık **9.7 saat** ($0.407$ gün) sonra tekrar test edilmelidir. |
| **$w_1$** | `1.1827` | $S_0(G=2)$ İlk Zorlanma Stabilitesi | Tereddütle çözülen yeni bir cebirsel kural (ör. diskriminant formülü) **1.18 gün** sonra unutulma eşiğine yaklaşır. |
| **$w_2$** | `3.1262` | $S_0(G=3)$ İlk Başarı Stabilitesi | İlk denemede temiz çözülen standart kuadratik denklem **3.12 gün** boyunca güvenli bölgede kalır. |
| **$w_3$** | `15.4722` | $S_0(G=4)$ İlk Kolaylık Stabilitesi | Önceden aşina olunan temel bir kural (ör. $x \cdot 0 = 0$) ilk seferde akıcıysa **15.47 gün** tekrar gerektirmez. |
| **$w_4$** | `7.2102` | $D_0$ Taban Zorluk Çapası | Cebir konularının taban zorluk ekseni. Matematik soyutlaması $1-10$ skalasında $7.21$ taban zorluğuyla başlatılır. |
| **$w_5$** | `0.5316` | İlk Notun Zorluğa Etkisi | İlk derecenin ($G$) zorluk skoru üzerindeki diferansiyel eğimi. |
| **$w_6$** | `1.0651` | Zorluk Değişim Adımı | Her $G \ne 3$ durumunda $D$'nin ne kadar sert güncelleneceğini belirler. Hata yapıldığında zorluk $1.065$ puan sıçrar. |
| **$w_7$** | `0.0234` | Ortalama Zorluğa Çekilme (Mean Reversion) | Aşırı uçlardaki zorlukların zamanla konunun genel ortalama zorluğuna ($D_0(3)$) yavaşça dönme katsayısı. |
| **$w_8$** | `1.6160` | Stabilite Artış Katsayısı ($\ln$) | Hatırlama anındaki genel stabilite patlamasının taban çarpanı ($e^{1.616} \approx 5.03$). Başarılı tekrar kararlılığı katlar. |
| **$w_9$** | `0.1544` | Stabilite Azalan Getirisi ($S^{-w_9}$) | Bir cebir kuralı zaten çok kararlıysa ($S = 100$ gün), yeni bir tekrarın sağladığı ek stabilite yüzdesi düşer. |
| **$w_{10}$** | `1.0819` | İstenen Zorluk Katsayısı ($e^{w_{10}(1-R)}$) | **Desirable Difficulty:** Öğrenci kuralı tam unutmak üzereyken ($R \to 0.1$) zorlanarak hatırlarsa, kazandığı stabilite artışı tavan yapar. |
| **$w_{11}$** | `1.9813` | Lapse Sonrası Taban Stabilite | Bir kural unutulduğunda ($G=1$) yeni kararlılığın taban ölçeği. |
| **$w_{12}$** | `0.0953` | Lapse Zorluk Cezası ($D^{-w_{12}}$) | Karmaşık, yüksek $D$'li konularda unutma yaşandığında stabilitenin daha sert düşmesini sağlar. |
| **$w_{13}$** | `0.2975` | Geçmiş Stabilite Kurtarma Payı | Kural daha önce ne kadar sağlamsa ($S$), unutulsa dahi nöral iz tamamen silinmez; $S^{0.2975}$ oranında hızlı toparlanır. |
| **$w_{14}$** | `0.2242` | Beklenmedik Unutma Cezası | $R$ yüksekken (öğrencinin bilmesi beklenirken) yapılan sürpriz hatalarda stabilite düşüşünü derinleştirir. |
| **$w_{15}$** | `0.2407` | Zorluk Cezası Çarpanı ($G=2$) | Öğrenci adımı tereddütle ($Hard$) tamamlarsa, $Good$ başarısına kıyasla stabilite artışı $\%75.9$ oranında budanır ($0.2407$). |
| **$w_{16}$** | `2.9466` | Kolaylık Bonusu Çarpanı ($G=4$) | Adım otomatikleşmiş bir akıcılıkla atılırsa ($Easy$), kararlılık standart artışın **$2.95$ katı** hızla büyür. |

---

## 4. HİYERARŞİK PARÇA-BÜTÜN BELLEK YAYILIMI (PART-WHOLE PROPAGATION)

Geleneksel aralıklı tekrar algoritmaları (Anki, SuperMemo) kartları birbirinden tamamen bağımsız kabul eder. Ancak matematik **hiyerarşik bir yönlü döngüsüz graftır (DAG)**. 

Bir öğrenci $ax^2 + bx + c = 0$ denklemini kuadratik formülle çözerken:
1. $b^2 - 4ac$ diskriminantını hesaplar (Dört işlem, kare alma, işaret kuralı).
2. $\sqrt{\Delta}$ kökünü basitleştirir (Karekök alma kuralı).
3. $-b \pm \sqrt{\Delta}$ payını hesaplar (Negatif sayı aritmetiği).
4. $2a$'ya böler (Kesir sadeleştirme, doğrusal denklem mantığı).

Bu üst düzey bileşik görevi ($W$) başarıyla icra eden bir öğrenciye, ertesi gün gidip izole olarak " $-3 \times -4$ kaçtır?" veya "$2x = 8$ ise $x$ nedir?" diye sormak kognitif bir hatadır.

```text
               [ KC_4: Kuadratik Formül Çözümü ]  (Aktif Çalışılan Düğüm)
                               │
               ┌───────────────┴───────────────┐
               ▼ (γ = 0.80)                    ▼ (γ = 0.80)
      [ KC_3: Diskriminant ]          [ KC_2: Karekök Alma ]
               │
               ▼ (γ² = 0.64)
      [ KC_1: Doğrusal Denklem / İşaret Aritmetiği ]
```

### 4.1. Matematiksel Kanıt ve Formülasyon

Önkoşul grafı $N$ adet bilgi bileşeninden oluşsun: $\mathcal{V} = \{KC_1, KC_2, \dots, KC_N\}$.
Grafın yönlü bağımlılık matrisi $\mathbf{A} \in \mathbb{R}^{N \times N}$ olsun:

$$A_{ij} = \begin{cases} \omega_{ij}, & \text{eğer } KC_i \text{ düğümü, } KC_j \text{ düğümünün doğrudan önkoşulu ise} \\ 0, & \text{aksi halde} \end{cases}$$

Burada $\omega_{ij} \in (0, 1]$ katsayısı, $KC_j$ icra edilirken $KC_i$ alt bileşeninin bilişsel kullanım oranını (bilişsel ağırlığını) temsil eder ve her sütun için $\sum_{i} A_{ij} \le 1$ olacak şekilde normalize edilir.

Graf bir DAG (Directed Acyclic Graph) olduğundan, $\mathbf{A}$ matrisi uygun topolojik sıralamayla kesin üst üçgensel (strictly upper triangular) hale getirilebilir. Dolayısıyla:

$$\exists \, k \le N \quad \text{öyle ki} \quad \mathbf{A}^k = \mathbf{0} \quad (\mathbf{A} \text{ nilpotenttir})$$

### 4.2. Derinlik Bozunma Çarpanı ($\gamma = 0.80^{\text{depth}}$)
Bileşik bir görev çalıştığında, alt düğümlere yayılan kognitif aktivasyon mesafenin üstel bir fonksiyonu olarak sönümlenir. $d$ adım gerideki bir önkoşula ulaşan etki:

$$\text{Decay}(d) = \gamma^d = (0.80)^d$$

Toplam yayılım operatörü matrisi $\mathbf{P} \in \mathbb{R}^{N \times N}$:

$$\mathbf{P} = \mathbf{I} + \gamma \mathbf{A} + \gamma^2 \mathbf{A}^2 + \gamma^3 \mathbf{A}^3 + \dots = \sum_{d=0}^{D_{\max}} \gamma^d \mathbf{A}^d$$

$\mathbf{A}$ nilpotent olduğundan bu seri sonludur ve tam olarak şu ters matrise eşittir:

$$\mathbf{P} = (\mathbf{I} - \gamma \mathbf{A})^{-1}$$

### 4.3. Kararlılık Vektörü Güncellemesi
Öğrenci $j$ düğümünde bir problem çözdüğünde, doğrudan kararlılık artışı $\Delta S_j$ hesaplanır. Doğrudan dürtü vektörü $\mathbf{u} = [0, \dots, \Delta S_j, \dots, 0]^T$ olmak üzere, tüm graf üzerindeki kararlılık artış vektörü:

$$\Delta \mathbf{S} = \mathbf{P} \cdot \mathbf{u}$$

Her bir $KC_i$ için güncellenmiş kararlılık:
$$S'_i = S_i + \Delta S_i = S_i + P_{ij} \cdot \Delta S_j$$

### 4.4. Somut Cebir Örneği ve Matris Hesabı

4 düğümlü bir cebir alt grafı ele alalım:
* $KC_1$: Tek değişkenli doğrusal denklem çözümü ($ax = b$).
* $KC_2$: Karekök sadeleştirme ($\sqrt{48} = 4\sqrt{3}$).
* $KC_3$: Diskriminant hesabı ($b^2 - 4ac$).
* $KC_4$: Kuadratik formülle tam çözüm ($x = \frac{-b \pm \sqrt{\Delta}}{2a}$).

Bağımlılıklar:
* $KC_4 \to KC_3$ (ağırlık: $1.0$), $KC_4 \to KC_2$ (ağırlık: $0.8$)
* $KC_3 \to KC_1$ (ağırlık: $0.9$), $KC_2 \to KC_1$ (ağırlık: $0.4$)

Bağımlılık matrisi $\mathbf{A}$:

$$\mathbf{A} = \begin{pmatrix} 
0 & 0.4 & 0.9 & 0 \\ 
0 & 0 & 0 & 0.8 \\ 
0 & 0 & 0 & 1.0 \\ 
0 & 0 & 0 & 0 
\end{pmatrix}$$

Derinlik katsayısı $\gamma = 0.80$. $\gamma \mathbf{A}$ ve $(\gamma \mathbf{A})^2$ hesaplanır:

$$\gamma \mathbf{A} = \begin{pmatrix} 
0 & 0.32 & 0.72 & 0 \\ 
0 & 0 & 0 & 0.64 \\ 
0 & 0 & 0 & 0.80 \\ 
0 & 0 & 0 & 0 
\end{pmatrix}$$

$$(\gamma \mathbf{A})^2 = \begin{pmatrix} 
0 & 0 & 0 & (0.32 \times 0.64) + (0.72 \times 0.80) \\ 
0 & 0 & 0 & 0 \\ 
0 & 0 & 0 & 0 \\ 
0 & 0 & 0 & 0 
\end{pmatrix} = \begin{pmatrix} 
0 & 0 & 0 & 0.2048 + 0.5760 \\ 
0 & 0 & 0 & 0 \\ 
0 & 0 & 0 & 0 \\ 
0 & 0 & 0 & 0 
\end{pmatrix} = \begin{pmatrix} 
0 & 0 & 0 & 0.7808 \\ 
0 & 0 & 0 & 0 \\ 
0 & 0 & 0 & 0 \\ 
0 & 0 & 0 & 0 
\end{pmatrix}$$

$(\gamma \mathbf{A})^3 = \mathbf{0}$. Toplam yayılım matrisi $\mathbf{P} = \mathbf{I} + \gamma \mathbf{A} + (\gamma \mathbf{A})^2$:

$$\mathbf{P} = \begin{pmatrix} 
1.0000 & 0.3200 & 0.7200 & 0.7808 \\ 
0 & 1.0000 & 0 & 0.6400 \\ 
0 & 0 & 1.0000 & 0.8000 \\ 
0 & 0 & 0 & 1.0000 
\end{pmatrix}$$

**Sonuç:** Öğrenci $KC_4$'te kuadratik bir problem çözüp $\Delta S_4 = 10.0\text{ gün}$ doğrudan kararlılık artışı kazandığında:
* $KC_4$ (Kuadratik Formül): $\Delta S_4 = 10.0 \text{ gün}$
* $KC_3$ (Diskriminant): $\Delta S_3 = 0.8000 \times 10.0 = \mathbf{8.0 \text{ gün}}$
* $KC_2$ (Karekök): $\Delta S_2 = 0.6400 \times 10.0 = \mathbf{6.4 \text{ gün}}$
* $KC_1$ (Doğrusal Denklem): $\Delta S_1 = 0.7808 \times 10.0 = \mathbf{7.81 \text{ gün}}$

> [!TIP]
> **Öğrenci Deneyimi Kazancı:** Öğrenci ileri düzey problemleri çözdükçe, ilköğretim seviyesindeki $KC_1$ düğümü sıfır izole soruyla arka planda sürekli canlı ve yeşil kalır.

---

## 5. SİRKADİYEN UYKU KONSOLİDASYONU BARİYERİ (WALKER & STICKGOLD)

Bellek araştırmaları (Walker & Stickgold 2004, 2006; Diekelmann & Born 2010), öğrenilen prosedürel ve deklaratif bilginin kalıcı uzun süreli hafızaya (neokortikal ağlara) aktarılmasının **iki aşamalı bir biyolojik süreç** olduğunu kanıtlamıştır.

```text
[ Gündüz Seansı: Hipokampal Kayıt ] ──(Uyanık Tekrar)──► [ Sinaptik Doygunluk (Plato) ]
                     │
             [ NREM / REM Uykusu ]  (Uyku İğcikleri & Keskin Dalga Dalgalanmaları)
                     │
                     ▼
[ Gece Konsolidasyonu: Neokortikal Entegrasyon ] ──► [ Gerçek Kararlılık (S) Artışı ]
```

### 5.1. Nörobiyolojik Mekanizma
* **Gündüz / Çalışma Anı:** Bilgi geçici olarak hipokampusta kodlanır. Aynı gün içinde peş peşe yapılan tekrarlar sinaptik güçlenmeyi bir noktada doyurur (Synaptic Saturation).
* **NREM Uykusu (Yavaş Dalga Uykusu - SWS):** Hipokampustan neokortekse bilgi transferi gerçekleşir (Sharp-Wave Ripples).
* **REM Uykusu:** Prosedürel kurallar şema ağlarıyla bütünleştirilir (Schema Integration).

### 5.2. Gün İçi Yığın Tekrar Bariyeri Formülü
Eğer bir $KC$ aynı gün içinde birden fazla kez çalışılırsa, iki çalışma arasındaki süre $\Delta t < 14\text{ saat}$ ise ve arada bir uyku epizodu doğrulanmamışsa, **uzun süreli stabiliteye katkı sıfırdır**:

$$\Delta S_{\text{session}} = \begin{cases} 
0, & \text{eğer } \Delta t < 14 \text{ saat ve } \text{SleepLogged} = \text{False} \\ 
\Delta S_{\text{FSRS}}, & \text{eğer } \Delta t \ge 14 \text{ saat veya } \text{SleepLogged} = \text{True} 
\end{cases}$$

### 5.3. Çalışma Belleği Geçici Retrievability Güncellemesi
Aynı gün yapılan tekrarlar uzun süreli $S$'yi artırmasa da, anlık seans içi akıcılığı ($R_{\text{temp}}$) yükseltir:

$$R_{\text{temp}} = 1.0, \quad S' = S \quad (\text{Stabilite Dondurulur})$$

Bu mekanizma, öğrencinin sınav öncesi gece sabaha kadar 200 soru çözerek sistemi "kandırmasını" (gaming the retention score) imkânsız kılar. Sistem o gece uyunmadıkça öğrenciyi asla "Mastered / Kalıcı" seviyesine yükseltmez.

---

## 6. KODLAMA ÇEŞİTLİLİĞİ (ENCODING VARIABILITY: MARTIN 1968, BOWER 1972)

Tek bir bağlamda veya tek tip formatta öğrenilen cebirsel kural, aşırı özelleşmiş ve kırılgan bir nöral iz bırakır. Örneğin, öğrenci daima $x^2 - 5x + 6 = 0$ şeklinde standart sembolik formatta pratik yaparsa, soru sözel bir probleme veya geometrik bir alana dönüştüğünde kuralı geri çağıramaz (Context-Dependent Retrieval Failure).

### 6.1. Temsil Modaliteleri Kümesi ($\mathcal{M}$)
Sistem her $KC$ için 4 temel modalite tanımlar:
1. $\text{SYM}$ (Saf Sembolik / Cebirsel): Formül manipülasyonu, standart denklem.
2. $\text{GEO}$ (Geometrik Alan Karosu): Al-Harezmi karo yerleşimi, tam kare tamamlama.
3. $\text{PAR}$ (Fonksiyonel / Dinamik Parabol): Kartezyen tepe noktası, simetri ekseni, kök aralığı.
4. $\text{WRD}$ (Sözel / Gerçek Hayat Modellemesi): Roket yörüngesi, alan optimizasyonu, sözel metin.

### 6.2. Kodlama Çeşitliliği Çarpanı ($\Phi_{\text{diversity}}$)
Tekrar seansında kullanılan modalite ($M_t$) ile son $k$ seansta kullanılan modalitelerin çeşitliliği ölçülür. Seans stabilite artışına şu çarpan uygulanır:

$$\Delta S_{\text{effective}} = \Delta S_{\text{FSRS}} \cdot \Phi_{\text{diversity}}$$

$$\Phi_{\text{diversity}} = 1.0 + \lambda_{\text{mod}} \cdot \left( 1 - \text{CosineSimilarity}(\mathbf{v}_t, \overline{\mathbf{v}}_{t-k}) \right)$$

Pratik ayrık formülasyon:

$$\Phi_{\text{diversity}} = 1.0 + \sum_{m \in \mathcal{M}} \beta_m \cdot \mathbb{I}(M_t = m \land M_t \ne M_{t-1}) + \delta_{\text{cross}} \cdot \mathbb{I}(\text{Modalite Çifti Arası Transfer})$$

| Modalite Geçişi ($M_{t-1} \to M_t$) | Çeşitlilik Bonusu ($\Phi_{\text{diversity}}$) | Kognitif Gerekçe |
| :--- | :---: | :--- |
| $\text{SYM} \to \text{SYM}$ | **$1.00$** (Bonus yok) | Aynı sembolik bağlam; ek nöral yolak açılmaz. |
| $\text{SYM} \to \text{GEO}$ | **$1.25$** ($+\%25$) | Cebirsel terim uzamsal alana eşlenir; çift kodlama (Paivio Dual-Coding). |
| $\text{SYM} \to \text{WRD}$ | **$1.35$** ($+\%35$) | Formül semantik bağlama bürünür; anlamsal derinlik artar (Craik & Lockhart). |
| $\text{GEO} \to \text{PAR}$ | **$1.40$** ($+\%40$) | Statik alandan dinamik fonksiyon eğrisine kavramsal sıçrama. |
| $\text{WRD} \to \text{SYM} \to \text{GEO}$ (3'lü Döngü) | **$1.45$** ($+\%45$) | Tam kavramsal esneklik; transfer testi garantisi. |

---

## 7. REJİM-UYARLAMALI ÇİZELGELEME VE YORGUNLUK İNDİRİMİ

### 7.1. The Spacing Paradox Çözümü (Vlach & Sandhofer, 2012)
Geleneksel aralıklı tekrar modelleri kararlılığı düşük yeni öğrenilmiş konulara genişleyen aralık uyguladığında bellek çöküşü yaşanır.
* **Kırılgan Rejim ($S < 2.5 \text{ Gün}$):** Sıkışık / Daralan Aralık. Gün $0 \to$ Gün $1 \to$ Gün $2$. Amaç bellek izini pekiştirmektir.
* **Kararlı Rejim ($S \ge 2.5 \text{ Gün}$):** FSRS-4.5 Genişleyen Aralık. Gün $2 \to$ Gün $7 \to$ Gün $21 \to$ Gün $60$.

### 7.2. Mackworth Uyanıklık Düşüşü ve Bilişsel Yorgunluk İndirimi
Mackworth (1948) araştırmalarına göre, yoğun problem çözme oturumunun 15. dakikasından sonra hata oranı zihinsel glikoz tükenmesi nedeniyle artar.
* Eğer oturum süresi $> 15.0 \text{ dakika}$ ve öğrenci bir hata yaparsa ($G=1$), bu durum konunun unutulduğu anlamına gelmez.
* **Prosedür:** Stabilite tabana sıfırlanmaz ($S' \ne 0.40$). Mevcut stabilite yalnızca $\%15$ kırpılır:
  $$S' = \max(S \times 0.85, 1.0)$$
* Sistem anında bir `FATIGUE_BREAK_TRIGGERED` sinyali üreterek seansı sonlandırır.

---

## 8. EKSİKSİZ ÜRETİM MOTORU: `RetentionAndSpacingEngine`

Aşağıdaki Python sınıfı; 17 parametreli FSRS-4.5 çekirdeğini, $\mathbf{P} = (\mathbf{I} - \gamma \mathbf{A})^{-1}$ parça-bütün yayılımını, 14 saatlik sirkadiyen uyku filtresini ve kodlama çeşitliliği çarpanını eksiksiz olarak yürütür:

```python
"""
Retention and Spacing Engine (FSRS-4.5 + Part-Whole + Sleep Gate + Encoding Variability)
"""

import math
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

class RetentionAndSpacingEngine:
    # Cebirsel ve Prosedürel Öğrenme İçin Kalibre Edilmiş 17 FSRS-4.5 Ağırlığı
    W = np.array([
        0.4072,  # w0: S0(G=1)
        1.1827,  # w1: S0(G=2)
        3.1262,  # w2: S0(G=3)
        15.4722, # w3: S0(G=4)
        7.2102,  # w4: D0 base
        0.5316,  # w5: D0 slope
        1.0651,  # w6: Delta D step
        0.0234,  # w7: Mean reversion
        1.6160,  # w8: S increase base
        0.1544,  # w9: S power diminishing return
        1.0819,  # w10: Desirable difficulty exponent
        1.9813,  # w11: Post-lapse S base
        0.0953,  # w12: Post-lapse D penalty
        0.2975,  # w13: Post-lapse S recovery
        0.2242,  # w14: Post-lapse R penalty
        0.2407,  # w15: Hard rating penalty
        2.9466   # w16: Easy rating bonus
    ], dtype=np.float64)

    GAMMA_DECAY = 0.80  # Parça-bütün derinlik sönümleme katsayısı
    CIRCADIAN_SLEEP_HOURS = 14.0  # Sirkadiyen uyku konsolidasyon bariyeri (saat)
    DESIRED_RETENTION = 0.90  # Hedeflenen hatırlama eşiği

    def __init__(self, kc_ids: List[str], adjacency_matrix: np.ndarray):
        """
        :param kc_ids: Graf üzerindeki tüm KC kimlikleri (topolojik sıralı)
        :param adjacency_matrix: NxN boyutlu yönlü önkoşul ağırlık matrisi A
        """
        self.kc_ids = kc_ids
        self.n = len(kc_ids)
        self.kc_to_idx = {k: i for i, k in enumerate(kc_ids)}
        self.A = adjacency_matrix.astype(np.float64)
        
        # P = (I - gamma * A)^(-1) Parça-Bütün Yayılım Matrisinin Hesaplanması
        I = np.eye(self.n, dtype=np.float64)
        self.P = np.linalg.inv(I - self.GAMMA_DECAY * self.A)

    def calculate_retrievability(self, delta_t_days: float, stability: float) -> float:
        """FSRS-4.5 Geri Çağrılabilirlik Güç Yasası"""
        if stability <= 0:
            return 0.0
        # R(S) = 0.90 olacak şekilde normalize edilmiş FSRS güç yasası
        factor = (1.0 / (self.DESIRED_RETENTION ** 2) - 1.0) # ~ 0.23456
        return float((1.0 + factor * (delta_t_days / stability)) ** -0.5)

    def calculate_interval(self, stability: float) -> float:
        """Hedeflenen retrievability'ye (0.90) ulaşılacak gün sayısı"""
        # R(t) = (1 + factor * t/S)^(-0.5) = 0.90 => t = S
        return max(stability, 0.1)

    def calculate_encoding_diversity(self, current_mode: str, last_mode: Optional[str]) -> float:
        """Kodlama Çeşitliliği Çarpanı (Encoding Variability Multiplier)"""
        if not last_mode or current_mode == last_mode:
            return 1.00
        
        transitions = {
            ("SYM", "GEO"): 1.25,
            ("GEO", "SYM"): 1.25,
            ("SYM", "WRD"): 1.35,
            ("WRD", "SYM"): 1.35,
            ("GEO", "PAR"): 1.40,
            ("PAR", "GEO"): 1.40,
            ("WRD", "PAR"): 1.45,
            ("PAR", "WRD"): 1.45,
        }
        return transitions.get((last_mode, current_mode), 1.20)

    def review_kc(
        self,
        kc_id: str,
        grade: int,  # 1: Again, 2: Hard, 3: Good, 4: Easy
        current_time: datetime,
        last_review_time: Optional[datetime],
        current_stability: Optional[float],
        current_difficulty: Optional[float],
        session_duration_minutes: float,
        current_mode: str = "SYM",
        last_mode: Optional[str] = None,
        sleep_confirmed: bool = False
    ) -> Dict[str, Any]:
        """
        Tek bir KC için tam FSRS-4.5 döngüsü, uyku kontrolü ve yayılım hesabı.
        """
        w = self.W
        idx = self.kc_to_idx[kc_id]
        
        # 1. Mackworth Bilişsel Yorgunluk Kontrolü
        if grade == 1 and session_duration_minutes > 15.0:
            safe_s = max((current_stability or 1.0) * 0.85, 1.0)
            return {
                "kc_id": kc_id,
                "new_stability": safe_s,
                "new_difficulty": current_difficulty or 5.0,
                "regime": "FATIGUE_TOLERATED",
                "propagation_vector": {},
                "message": "15+ dk yorgunluğu: Lapse sayılmadı, stabilite korundu. Seans durdurulmalı."
            }

        # 2. İlk Karşılaşma (Initial Review)
        if current_stability is None or current_difficulty is None or last_review_time is None:
            init_s = float(w[grade - 1])
            init_d = float(w[4] - math.exp(w[5] * (grade - 1)) + 1.0)
            init_d = min(max(init_d, 1.0), 10.0)
            
            # Kodlama çeşitliliği bonusu
            div_mult = self.calculate_encoding_diversity(current_mode, last_mode)
            init_s *= div_mult

            return {
                "kc_id": kc_id,
                "new_stability": init_s,
                "new_difficulty": init_d,
                "regime": "INITIAL",
                "next_interval_days": self.calculate_interval(init_s),
                "propagation_vector": self._propagate_stability(idx, init_s)
            }

        # 3. Sirkadiyen Uyku Konsolidasyonu Kontrolü
        delta_hours = (current_time - last_review_time).total_seconds() / 3600.0
        delta_days = delta_hours / 24.0
        
        if delta_hours < self.CIRCADIAN_SLEEP_HOURS and not sleep_confirmed:
            # Aynı gün yığın tekrar: Stabilite dondurulur, delta_S = 0
            return {
                "kc_id": kc_id,
                "new_stability": current_stability,
                "new_difficulty": current_difficulty,
                "regime": "SAME_DAY_CONSOLIDATION_BLOCKED",
                "next_interval_days": self.calculate_interval(current_stability),
                "propagation_vector": {},
                "message": f"Sirkadiyen bariyer: {delta_hours:.1f} sa < 14 sa (Uyku yok). delta_S = 0."
            }

        # 4. Standart FSRS-4.5 Hesaplaması
        r = self.calculate_retrievability(delta_days, current_stability)
        
        # Zorluk Güncellemesi
        delta_d = -w[6] * (grade - 3)
        d_prime = w[7] * (w[4] - math.exp(w[5] * 2) + 1.0) + (1.0 - w[7]) * (current_difficulty + delta_d)
        d_prime = min(max(d_prime, 1.0), 10.0)

        # Stabilite Güncellemesi
        if grade == 1:
            # Lapse / Başarısızlık
            s_prime = w[11] * (d_prime ** -w[12]) * (((current_stability + 1.0) ** w[13]) - 1.0) * math.exp(w[14] * (1.0 - r))
            regime = "RELEARNING"
        else:
            # Başarılı Hatırlama (Grade 2, 3, 4)
            hard_penalty = w[15] if grade == 2 else 1.0
            easy_bonus = w[16] if grade == 4 else 1.0
            
            s_inc = math.exp(w[8]) * (11.0 - d_prime) * (current_stability ** -w[9]) * (math.exp(w[10] * (1.0 - r)) - 1.0) * hard_penalty * easy_bonus
            s_prime = current_stability * (1.0 + s_inc)
            
            # Rejim Kontrolü (Spacing Paradox)
            regime = "FRAGILE_CONTRACTED" if s_prime < 2.5 else "STABLE_EXPANDING"

        # Kodlama Çeşitliliği Bonusu
        div_mult = self.calculate_encoding_diversity(current_mode, last_mode)
        s_prime *= div_mult

        delta_s = max(s_prime - current_stability, 0.0)
        
        # 5. Parça-Bütün Matris Yayılımı
        prop_updates = self._propagate_stability(idx, delta_s)

        return {
            "kc_id": kc_id,
            "new_stability": s_prime,
            "new_difficulty": d_prime,
            "retrievability_at_review": r,
            "regime": regime,
            "next_interval_days": self.calculate_interval(s_prime),
            "encoding_multiplier": div_mult,
            "propagation_vector": prop_updates
        }

    def _propagate_stability(self, source_idx: int, delta_s: float) -> Dict[str, float]:
        """
        Delta S artışını P = (I - gamma * A)^(-1) matrisi üzerinden alt önkoşullara dağıtır.
        """
        u = np.zeros(self.n, dtype=np.float64)
        u[source_idx] = delta_s
        delta_vector = self.P @ u
        
        updates = {}
        for i, val in enumerate(delta_vector):
            if i != source_idx and val > 0.01:
                updates[self.kc_ids[i]] = float(round(val, 4))
        return updates
```
