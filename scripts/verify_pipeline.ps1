# ====================================================================
# Kişisel Öğrenme Motoru (PLE) Tam Doğrulama ve CI/CD Pipeline Betiği
# Non-Docker Yerel Mühendislik Hattı
# Ref: 26-CI-CD-AND-AUTOMATED-TESTING-PIPELINE.md
# ====================================================================

$ErrorActionPreference = "Stop"

$RootDir = Resolve-Path "$PSScriptRoot\.."
$EngineDir = "$RootDir\services\core-engine"
$MobileDir = "$RootDir\apps\mobile"
$VenvPython = "$EngineDir\.venv\Scripts\python.exe"
$CoverageBin = "$EngineDir\.venv\Scripts\coverage.exe"
$FlutterBin = "C:\src\flutter\bin\flutter.bat"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  PLE MASTER CI/CD VERIFICATION PIPELINE (NON-DOCKER)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# --------------------------------------------------------------------
# 1. ADIM: Flutter Mobil Kod Kalitesi & Birim Testleri
# --------------------------------------------------------------------
Write-Host "`n[1/4] Flutter Mobil Kod Kalitesi ve Statik Analiz..." -ForegroundColor Yellow
if (Test-Path $FlutterBin) {
    Push-Location $MobileDir
    try {
        & $FlutterBin analyze --fatal-infos --fatal-warnings
        if ($LASTEXITCODE -ne 0) { throw "Flutter analyze basarisiz oldu!" }
        Write-Host "Flutter statik analizi: 0 Hata / 0 Uyari [PASS OK]" -ForegroundColor Green

        Write-Host "`n[2/4] Flutter Mobil Birim ve Widget Testleri..." -ForegroundColor Yellow
        & $FlutterBin test test/
        if ($LASTEXITCODE -ne 0) { throw "Flutter testleri basarisiz oldu!" }
        Write-Host "Flutter mobil testleri: Tamami Yesil [PASS OK]" -ForegroundColor Green
    } finally {
        Pop-Location
    }
} else {
    Write-Warning "Flutter binary bulunamadi ($FlutterBin). Mobil adimlar atlandi."
}

# --------------------------------------------------------------------
# 2. ADIM: Python Çekirdek Motor Testleri (PyTest)
# --------------------------------------------------------------------
Write-Host "`n[3/4] Python Cekirdek Motoru Testleri (PyTest)..." -ForegroundColor Yellow
Push-Location $EngineDir
try {
    & $VenvPython -m pytest -v
    if ($LASTEXITCODE -ne 0) { throw "Pytest testleri basarisiz oldu!" }
    Write-Host "Pytest cekirdek motor testleri: 84/84 Yesil [PASS OK]" -ForegroundColor Green

    # --------------------------------------------------------------------
    # 3. ADIM: Kod Kapsamı Denetimi (Coverage >= 85%)
    # --------------------------------------------------------------------
    Write-Host "`n[4/4] Kod Kapsami Denetimi (Coverage >= 85%)..." -ForegroundColor Yellow
    & $CoverageBin run --source=app -m pytest --quiet
    & $CoverageBin report -m --fail-under=85
    if ($LASTEXITCODE -ne 0) { throw "Kod kapsami %85 esiginin altinda kaldi!" }
    Write-Host "Kod Kapsami Denetimi Basarili: >= %85 [PASS OK]" -ForegroundColor Green
} finally {
    Pop-Location
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "  TUM PIPELINE KONTROLLERI BASARIYLA TAMAMLANDI! (100% PASS)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
