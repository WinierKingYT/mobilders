# 🔹 HEDEF 1: ÜRETİM HAZIRLIĞI, ÇEVRİMDIŞI KALICILIK VE MOBİL E2E SAĞLAMLAŞTIRMA

---

## ⚡ ÇALIŞTIRILABİLİR /goal KOMUTU

```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Hedef 1 kapsamındaki "Üretim Hazırlığı, Çevrimdışı Kalıcılık, Mobil Kalite ve Haptik Sistem" paketini uçtan uca uygula ve doğrula:

1. Mobil Çevrimdışı Kuyruk (OfflineSyncQueue):
   - Ağ koptuğunda çözülen adımları diske yaz; ağ bağlantısı sağlandığında sunucuya idempotent olarak aktar.
2. Haptik Dokunsal Geri Bildirim:
   - Tuş vuruşları (light impact), doğru adımlar (medium impact) ve hata uyarıları için HapticFeedbackService geliştir ve tüm butonlara bağla.
3. Sıfır Arayüz Sıçraması (Zero Layout Shift):
   - Touchpad, Klavye ve Çizim Kanvası geçişlerini AnimatedSwitcher ve yay fiziği ile 60/120 FPS akıcı hale getir.
4. Çökme Direnci & Durum Koruma:
   - Seansı ve yarım kalan girdiyi yerel depolamaya anında kaydet; sıfır veri kaybıyla geri yükle (State Restoration).
5. Erişilebilirlik ve Kanvas Entegrasyonu:
   - VectorInkingCanvas, TunnelFocusMode ve DyscalculiaHelper bileşenlerini seans ekranına bağla.
6. Tüm mobil ve backend testlerinin yeşil geçtiğini doğrula.
```
