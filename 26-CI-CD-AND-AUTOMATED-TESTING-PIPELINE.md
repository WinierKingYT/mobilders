# 26-CI-CD-AND-AUTOMATED-TESTING-PIPELINE.md
# CI/CD VE OTOMATİK DOĞRULAMA HATTI ŞARTNAMESİ (CI/CD & AUTOMATED VERIFICATION)
## GitHub Actions İş Akışı, 6 Katı Kabul Kapısı (DoD) Test Komutları ve Kalite Eşikleri

---

## 1. GENEL BAKIŞ VE "SIFIR İLLÜZYON" İLKESİ

Kişisel Öğrenme Motoru geliştirme sürecinde hiçbir kod parçası, otomatik testlerden geçmeden ana dala (`main`) birleştirilemez. Yazılım doğrulaması iki katmandan oluşur:

1. **Çekirdek Matematik & Bilişsel Doğrulama (Python / PyTest):**
   - CAS eşdeğerliği, 8 Buggy Rule tespiti, 2PL-IRT simülasyonu ve Wald SPRT sahte ustalık denetimi.
2. **Mobil İstemci Doğrulama (Flutter / Dart Test):**
   - Statik kod analizi (`flutter analyze`), birim testler, widget testleri ve altın ekran (Golden UI) testleri.

---

## 2. GİTHUB ACTIONS İŞ AKIŞI (`.github/workflows/verify-kernel.yml`)

```yaml
name: Verify Cognitive Learning Kernel & Client

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-kernel-verification:
    name: Backend CAS & Psychometrics (Gates 1-3)
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Dependencies
        run: |
          cd services/core-engine
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov pytest-benchmark

      - name: Run Gate 1 - CAS & Buggy Rules (500 Falsification Tests)
        run: |
          cd services/core-engine
          pytest tests/test_cas_falsification.py -v --maxfail=1

      - name: Run Gate 2 - IRT & Psychometrics (Monte Carlo Simulation)
        run: |
          cd services/core-engine
          pytest tests/test_psychometrics_monte_carlo.py -v

      - name: Run Gate 3 - Zero-Leakage & Socratic Guardrails
        run: |
          cd services/core-engine
          pytest tests/test_zero_leakage_guardrail.py -v

  mobile-client-verification:
    name: Flutter Mobile Client (Gates 4-5)
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - name: Set up Flutter 3.19+
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.19.x'
          channel: 'stable'
          cache: true

      - name: Install Flutter Dependencies
        run: |
          if [ -d "apps/mobile" ]; then
            cd apps/mobile
            flutter pub get
          fi

      - name: Run Dart Static Analysis (0 Errors, 0 Warnings)
        run: |
          if [ -d "apps/mobile" ]; then
            cd apps/mobile
            flutter analyze --fatal-infos --fatal-warnings
          fi

      - name: Run Mobile Unit & Widget Tests
        run: |
          if [ -d "apps/mobile" ]; then
            cd apps/mobile
            flutter test --coverage
          fi
```

---

## 3. KATI DOĞRULAMA KAPILARI TEST KOMUTLARI VE EŞİK DEĞERLERİ

| Kabul Kapısı | Test Kapsamı | Çalıştırılacak Komut | Katı Başarı Eşiği |
| :--- | :--- | :--- | :--- |
| **Kapı 1: CAS & Hata** | 500 Sentetik Cebir Adımı | `pytest tests/test_cas_falsification.py` | %100 Doğruluk (0 FP, 0 FN), $P_{95} \le 120\text{ ms}$ |
| **Kapı 2: Psikometri** | 10.000 Sentetik Öğrenci | `pytest tests/test_psychometrics_monte_carlo.py` | $\text{SE}(\theta) \le 0.35$ ($\le 5$ adım), $\alpha \le 0.05$ |
| **Kapı 3: Güvenlik** | 100 Adversarial Jailbreak | `pytest tests/test_zero_leakage_guardrail.py` | %0 Cevap Sızıntısı, Soru/Açıklama $\ge 2.0$ |
| **Kapı 4: Mobil Kod** | Dart Analiz & Null Safety | `flutter analyze` | 0 Error, 0 Warning, 0 Info |
| **Kapı 5: Mobil UI** | Çift Modlu Tuş & Kanvas | `flutter test test/widget/` | 60 FPS kanvas testi, sıfır RenderFlex taşması |
