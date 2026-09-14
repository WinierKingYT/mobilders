# Kişisel Öğrenme Motoru - Mobil İstemci (Flutter)

Bu modül, ikinci dereceden denklemler için geliştirilen **Kişisel Öğrenme Motoru**'nun akıllı telefon odaklı ($390 \times 844$ dikey portre ergonomisine optimize edilmiş) Flutter istemcisidir.

---

## 1. Mimari Tasarım ve Katmanlar (MVVM + Repository)

- **`lib/domain/models/`**: Temiz veri modelleri (`SolutionStep`, `DiagnosticBug`, `StepPsychometricsModel`).
- **`lib/data/services/`**: Python FastAPI çekirdek motoru (`/api/v1/session/step/verify`) ile konuşan HTTP API istemcisi (`EngineApiService`).
- **`lib/ui/core/`**: Deep Slate (`#0F172A`) odaklanma teması, tipografi ve tasarım sistemi sabitleri (`AppTheme`, `AppColors`, `AppConstants`).
- **`lib/ui/features/touchpad/`**:
  - **Matematiksel Touchpad (`MathTouchpad`):** Değişkenler ($x, x^2, \sqrt{\dots}, \pm$), operatörler ve tek dokunuşla ekleme.
  - **Serbest Sanal Klavye:** Sistem klavyesine geçiş ve çift yönlü mod kontrolü.
- **`lib/ui/features/session/`**:
  - `SessionViewModel`: Çözüm adımları, BKT ustalık güncellemesi, dal budama (rollback) ve hedef denklem kontrolü.
  - `SessionScreen`: Çözüm tahtası, yeşil/kırmızı adım kartları, **Zihinsel Karşıtlık (Mental Contrast)** üstü çizili yanılgı kartları (`BUG-QUAD-01..05`), Sokratik ipucu butonu (`💡 Takıldım`).

---

## 2. Çalıştırma Talimatları

### Bağımlılıkları İndirme:
```bash
flutter pub get
```

### Testleri Koşturma:
```bash
flutter test
```

### Emülatörde veya Cihazda Başlatma:
```bash
# Arka plan Python FastAPI çekirdeği çalışırken:
flutter run
```
