# ====================================================================
# Kişisel Öğrenme Motoru (Personal Learning Engine) Windows Servis Başlatıcı
# Non-Docker Yerel Üretim Servisi (Uvicorn / NSSM / PowerShell Background Job)
# ====================================================================

param (
    [string]$Action = "start",
    [int]$Port = 8000,
    [string]$HostIP = "127.0.0.1"
)

$RootDir = Resolve-Path "$PSScriptRoot\.."
$EngineDir = "$RootDir\services\core-engine"
$VenvPython = "$EngineDir\.venv\Scripts\python.exe"
$EnvFile = "$EngineDir\.env"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " PLE Core Engine Production Service Runner (Non-Docker)" -ForegroundColor Cyan
Write-Host " Root Directory:   $RootDir" -ForegroundColor Gray
Write-Host " Engine Directory: $EngineDir" -ForegroundColor Gray
Write-Host " Python Binary:    $VenvPython" -ForegroundColor Gray
Write-Host " Action:           $Action" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

if (-not (Test-Path $VenvPython)) {
    Write-Error "Python sanal ortamı bulunamadı: $VenvPython"
    exit 1
}

if (-not (Test-Path $EnvFile)) {
    Write-Warning ".env dosyası bulunamadı, varsayılan yapılandırma kullanılacak."
} else {
    Write-Host ".env yapılandırma dosyası doğrulandı: $EnvFile" -ForegroundColor Green
}

switch ($Action.ToLower()) {
    "start" {
        Write-Host "FastAPI servisi arka planda başlatılıyor (Host: $HostIP, Port: $Port)..." -ForegroundColor Green
        
        $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
        $ProcessInfo.FileName = $VenvPython
        $ProcessInfo.Arguments = "-m uvicorn app.main:app --host $HostIP --port $Port --no-access-log"
        $ProcessInfo.WorkingDirectory = $EngineDir
        $ProcessInfo.RedirectStandardOutput = $false
        $ProcessInfo.RedirectStandardError = $false
        $ProcessInfo.UseShellExecute = $true
        $ProcessInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
        
        $Process = [System.Diagnostics.Process]::Start($ProcessInfo)
        
        Start-Sleep -Seconds 2
        
        # Test connection
        try {
            $Health = Invoke-RestMethod -Uri "http://${HostIP}:${Port}/health" -TimeoutSec 5
            if ($Health.status -eq "healthy") {
                Write-Host "FastAPI Servisi Başarıyla Başlatıldı! PID: $($Process.Id)" -ForegroundColor Green
                Write-Host "Health Check Yanıtı: $($Health | ConvertTo-Json -Compress)" -ForegroundColor Green
            } else {
                Write-Warning "Servis yanıt verdi ancak durum 'healthy' değil: $($Health.status)"
            }
        } catch {
            Write-Warning "Sağlık kontrolü henüz yanıt vermedi. Servis başlatılıyor olabilir: $_"
        }
    }
    "status" {
        try {
            $Health = Invoke-RestMethod -Uri "http://${HostIP}:${Port}/health" -TimeoutSec 5
            Write-Host "PLE Core Engine Durumu: ÇALIŞIYOR (HEALTHY)" -ForegroundColor Green
            Write-Host ($Health | ConvertTo-Json) -ForegroundColor Cyan
        } catch {
            Write-Host "PLE Core Engine Durumu: KAPALI veya ERİŞİLEMİYOR" -ForegroundColor Red
        }
    }
    "stop" {
        Write-Host "FastAPI (uvicorn) süreçleri sonlandırılıyor..." -ForegroundColor Yellow
        Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
            $_.CommandLine -like "*uvicorn app.main:app*"
        } | Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Host "Servis durduruldu." -ForegroundColor Green
    }
    default {
        Write-Host "Kullanım: .\run_production_service.ps1 -Action [start|status|stop] -Port 8000" -ForegroundColor Yellow
    }
}
