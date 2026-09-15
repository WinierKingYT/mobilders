# 💎 BÖLÜM 6: UYGULAMA KALİTESİ, HAPTİK VE AKICILIK STANDARTLARI (MOBILE CRAFTSMANSHIP)

Bu goal, Apple Design Award ve Linear standartlarında dokunsal zanaatkarlık, sıfır arayüz sıçraması, çökme direnci, <5ms istemci doğrulaması ve Zen odak modunu kapsar.

---

## ⚡ ÇALIŞTIRILABİLİR /goal KOMUTU

```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Bölüm 6 "Mobil Zanaatkarlık, Haptik Geri Bildirim, Sıfır Gecikme ve Çökme Direnci (UX & Performance Polish)" paketini uçtan uca uygula ve doğrula:

1. Haptik Dokunsal Geri Bildirim:
   - Tuş vuruşları (light impact), doğru adımlar (medium impact / zafer titreşimi) ve hatalar/uyarılar (heavy impact) için HapticFeedbackService geliştir ve tüm butonlara bağla.
2. Sıfır Arayüz Sıçraması (Zero Layout Shift - ZLS):
   - Touchpad, Klavye ve Vector Inking Canvas geçişlerindeki zıplamaları AnimatedSwitcher ve yay fiziği (spring curves: Cubic(0.175, 0.885, 0.32, 1.25)) ile akıcı (60/120 FPS) hale getir.
3. Çökme Direnci & Durum Koruma (State Restoration):
   - Uygulama arka plana atıldığında, kapandığında veya telefon çaldığında aktif seansı, çözüm adımlarını ve yarım kalan formül girdisini yerel depolamaya anında kaydet; açılışta sıfır veri kaybıyla geri yükle.
4. İstemci Tarafı Anlık Sanity (<5ms):
   - Yazım anında parantez eşleştirme (6 seviyeli Rainbow Brackets), çift operatör engelleme ve ikinci ondalık nokta filtresini cihazda anında (<1ms) doğrula.
5. Görsel Mükemmellik & Zen Modu:
   - KaTeX ve Unicode matematik tipografisini piksel düzeyinde optimize et; dikkat dağıtmayan derin obsidian Zen odak modu ekle.
6. En az 25 yeni UI/Widget ve donma/performans testi ile doğrula.
```

---

## 📋 Beklenen Teslimatlar
- `apps/mobile/lib/core/services/haptic_feedback_service.dart`
- `apps/mobile/lib/ui/features/touchpad/zero_layout_shift_dock.dart`
- `apps/mobile/lib/ui/features/touchpad/instant_math_sanitizer.dart`
- `apps/mobile/lib/data/services/session_restoration_manager.dart`
- `apps/mobile/lib/ui/features/session/views/zen_focus_overlay.dart`
