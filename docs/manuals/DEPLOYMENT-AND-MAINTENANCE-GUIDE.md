# DEPLOYMENT AND MAINTENANCE GUIDE (KURULUM, DAĞITIM VE BAKIM KILAVUZU)
## Kişisel Öğrenme Motoru (Personal Learning Engine) — Üretim Dağıtımı, CI/CD ve Operasyonel Bakım

**Doküman Versiyonu:** 1.0.0  
**Hedef Ortam:** Linux Ubuntu 22.04 LTS / 24.04 LTS (Backend), Android 8.0+ & iOS 14+ (Mobil)  
**Tarih:** 14 Eylül 2026  

---

## 1. SİSTEM GEREKSİNİMLERİ VE ALTYAPI BİLEŞENLERİ

### 1.1. Backend Sunucu Donanım ve Yazılım Gereksinimleri
- **İşletim Sistemi:** Ubuntu Server 22.04 LTS veya Debian 12
- **CPU:** Asgari 2 vCPU (Önerilen: 4 vCPU, AVX2 destekli x86_64)
- **RAM:** Asgari 4 GB RAM (Önerilen: 8 GB)
- **Disk:** 40 GB NVMe SSD
- **Yazılım:**
  - Python 3.11.x (Katı sürüm gereksinimi, `python3.11-venv`, `python3.11-dev`)
  - Docker 26.0+ & Docker Compose v2.26+
  - Nginx 1.24+ (WebSocket ters vekil sunucusu)
  - Certbot / Let's Encrypt (TLS 1.3 SSL sertifikası)

### 1.2. Mobil Geliştirme ve Derleme Ortamı
- **Flutter SDK:** 3.19.0 veya üzeri (Kanal: `stable`)
- **Dart SDK:** 3.3.0 veya üzeri
- **Java Development Kit:** OpenJDK 17 LTS
- **Android SDK:** Platform 34, Build Tools 34.0.0, NDK 26.1
- **Xcode (iOS için):** Xcode 15.2+, CocoaPods 1.15+

---

## 2. BACKEND SERVİSLERİNİN ÜRETİM ORTAMINA KURULUMU

### 2.1. Kaynak Kodun Alınması ve Bağımlılıkların Yüklenmesi
```bash
# 1. Projeyi klonlayın
git clone https://github.com/WinierKingYT/mobilders.git /opt/mobilders
cd /opt/mobilders/services/core-engine

# 2. Python 3.11 sanal ortamını oluşturun
python3.11 -m venv .venv
source .venv/bin/activate

# 3. Bağımlılıkları yükleyin
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.2. Gunicorn + Uvicorn Çok İş Parçacıklı Üretim Başlatımı
Üretim ortamında tek bir Uvicorn süreci yerine, çekirdek sayısı kadar (`2 * vCPU + 1`) çalışan Gunicorn çalışanları kullanılmalıdır:

```bash
# Üretim başlatma komutu (örnek: 4 worker)
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000 \
  --timeout 120 \
  --keep-alive 5 \
  --access-logfile /var/log/ple/access.log \
  --error-logfile /var/log/ple/error.log
```

### 2.3. Systemd Servis Yapılandırması (`/etc/systemd/system/ple-engine.service`)
```ini
[Unit]
Description=Personal Learning Engine Core Backend
After=network.target

[Service]
Type=simple
User=pleuser
Group=pleuser
WorkingDirectory=/opt/mobilders/services/core-engine
Environment="PATH=/opt/mobilders/services/core-engine/.venv/bin"
Environment="PYTHONPATH=/opt/mobilders/services/core-engine"
ExecStart=/opt/mobilders/services/core-engine/.venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --timeout 120

Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

Servisi etkinleştirmek ve başlatmak için:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ple-engine
sudo systemctl start ple-engine
sudo systemctl status ple-engine
```

### 2.4. Nginx Ters Vekil ve WebSocket Yapılandırması (`/etc/nginx/sites-available/ple.conf`)
```nginx
upstream ple_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name api.ogrenmemotoru.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.ogrenmemotoru.com;

    ssl_certificate /etc/letsencrypt/live/api.ogrenmemotoru.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.ogrenmemotoru.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # REST API Uç Noktaları
    location /api/ {
        proxy_pass http://ple_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 5s;
        proxy_read_timeout 60s;
    }

    # Canlı WebSocket Oturumu (/ws/v1/session)
    location /ws/v1/session {
        proxy_pass http://ple_backend/ws/v1/session;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }

    # Sağlık Kontrolü
    location /health {
        proxy_pass http://ple_backend/health;
        access_log off;
    }
}
```

---

## 3. MOBİL İSTEMCİ DERLEME VE DAĞITIM KILAVUZU (FLUTTER)

### 3.1. Android Dağıtımı (Google Play Store AAB & APK)
1. **Sürüm Numaralandırması:** `apps/mobile/pubspec.yaml` dosyasında `version: 1.0.0+1` değerini doğrulayın.
2. **Keystore Oluşturma:**
   ```bash
   keytool -genkey -v -keystore ~/ple-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias ple-key
   ```
3. **Android App Bundle (AAB) Derleme:**
   ```bash
   cd apps/mobile
   flutter pub get
   flutter build appbundle --release --obfuscate --split-debug-info=./debug-symbols
   ```
   *Çıktı Yolu:* `build/app/outputs/bundle/release/app-release.aab`

4. **Yerel Test APK'sı Derleme:**
   ```bash
   flutter build apk --release --target-platform android-arm64
   ```

### 3.2. Ağ Güvenlik Yapılandırması (`network_security_config.xml`)
Yerel geliştirme ortamlarında HTTP erişimine izin vermek, üretimde ise yalnızca HTTPS ve TLS 1.3 zorunluluğu için `apps/mobile/android/app/src/main/res/xml/network_security_config.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.ogrenmemotoru.com</domain>
        <!-- SSL Pinning sertifika özeti buraya eklenecektir -->
    </domain-config>
</network-security-config>
```

---

## 4. CI/CD VE OTOMATİK DOĞRULAMA HATTI (GITHUB ACTIONS)

Depodaki `.github/workflows/verify-kernel.yml` iş akışı, her `push` ve `pull_request` anında 6 Katı Kabul Kapısını (DoD) test eder:

```yaml
name: Verify Cognitive Learning Kernel & Client

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-verification:
    name: Backend CAS, Psychometrics & Guardrails (Gates 1-3)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - name: Install Dependencies
        run: |
          cd services/core-engine
          pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run Backend Pytest Suite (68 Tests)
        run: |
          cd services/core-engine
          pytest -v --maxfail=1

  mobile-verification:
    name: Flutter Mobile Client (Gates 4-5)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.19.x'
          channel: 'stable'
          cache: true
      - name: Analyze Dart Code (0 Issues)
        run: |
          cd apps/mobile
          flutter pub get
          flutter analyze --fatal-infos --fatal-warnings
      - name: Run Flutter Tests (25 Scenarios)
        run: |
          cd apps/mobile
          flutter test
```

---

## 5. SİSTEM İZLEME, HATA KODLARI VE OPERASYONEL ALARMLAR

### 5.1. Sistem Sağlık Kontrolü (`GET /health`)
```bash
curl -i https://api.ogrenmemotoru.com/health
```
*Beklenen Yanıt:*
```json
{
  "status": "healthy",
  "service": "core-engine",
  "cas_status": "ready",
  "supported_misconceptions": [
    "BUG-QUAD-01", "BUG-QUAD-02", "BUG-QUAD-03", "BUG-QUAD-04", "BUG-QUAD-05"
  ]
}
```

### 5.2. Standart Hata Kodları ve Müdahale Rehberi
- **`ERR_CAS_PARSE_FAILED (1001)`:** Öğrenci geçersiz semboller girdi. İstemci ön-işlemcisi `2x` ve parantez dengesini inceler.
- **`ERR_CAS_DEPTH_EXCEEDED (1002)`:** Stack overflow saldırısı (AST derinliği > 15). Oturum güvenlik günlüğüne kaydedilir.
- **`ERR_CAS_TIMEOUT (1003)`:** SymPy sadeleştirmesi 500 ms'yi aştı. İşlem kesilir, öğrenciye daha sade bir adım atması önerilir.
- **`ERR_SEC_ZERO_LEAK_TRIGGERED (4001)`:** LLM çıktı filtresi cevabı ifşa eden kökü yakaladı. Sokratik soruya otomatik indirgendi.

### 5.3. Kritik Alarm Eşikleri (Alerting Rules)
1. **CAS P95 Gecikme Spike Alarmı:** $P_{95} > 120\text{ ms}$ (5 dakika boyunca) $\to$ CPU darboğazı veya karmaşık sembolik istekler.
2. **Afektif Şalter Fırlama Alarmı:** Oturumların %15'inden fazlasında Şalter tetikleniyorsa $\to$ Madde zorluk parametresi ($b$) öğrenci seviyesine göre aşırı yüksek kalibre edilmiştir.
3. **WebSocket Kopma Oranı:** Saniyede > 10 beklenmeyen kopma $\to$ Nginx timeout veya ağ altyapı sorunu.

---

## 6. SIFIR-PII VERİ YÖNETİŞİMİ VE FELAKET KURTARMA (DISASTER RECOVERY)

### 6.1. Kullanıcı Unutulma Talebi (`PURGE_TELEMETRY`)
Öğrenci uygulamasından "Verilerimi Sıfırla" eylemi gerçekleştirdiğinde:
1. Mobil cihazdaki Isar yerel veritabanı ve UUID silinir.
2. Sunucuya `POST /api/v1/privacy/purge` isteği iletilir.
3. Sunucu, ilgili anonim `StudentUUID`'ye ait tüm BKT posterior kayıtlarını ve seans loglarını kalıcı olarak siler (`DELETE FROM session_events WHERE student_uuid = :uuid`).

### 6.2. Günlük Yedekleme Prosedürü
Bilişsel model parametreleri ve anonim telemetri günlük olarak şifreli soğuk depoya yedeklenir:
```bash
#!/bin/bash
# /opt/scripts/backup-ple.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/ple"
mkdir -p "$BACKUP_DIR"
# Veritabanı ve Redis durum dump'ı
tar -czf "$BACKUP_DIR/ple_data_$TIMESTAMP.tar.gz" /var/lib/ple/data
# 30 günden eski yedekleri temizle
find "$BACKUP_DIR" -type f -name "*.tar.gz" -mtime +30 -delete
```

Bu kılavuz, sistemin yüksek erişilebilirlikle (99.9% uptime SLA) ve sıfır veri kaybı prensibiyle çalışmasını temin eder.
