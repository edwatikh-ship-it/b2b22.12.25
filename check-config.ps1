# Check Configuration Script
# Проверяет правильность настройки портов

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ПРОВЕРКА КОНФИГУРАЦИИ" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allOk = $true

# Check Frontend .env.local
Write-Host "[1] Проверка Frontend .env.local..." -ForegroundColor Yellow
if (Test-Path "frontend\moderator-dashboard-ui\.env.local") {
    $envContent = Get-Content "frontend\moderator-dashboard-ui\.env.local" -Raw
    if ($envContent -match "8001") {
        Write-Host "    [ERROR] .env.local использует НЕПРАВИЛЬНЫЙ порт 8001!" -ForegroundColor Red
        Write-Host "    Исправьте на: NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" -ForegroundColor Yellow
        $allOk = $false
    } elseif ($envContent -match "8000") {
        Write-Host "    [OK] .env.local использует правильный порт 8000" -ForegroundColor Green
    } else {
        Write-Host "    [WARN] NEXT_PUBLIC_API_URL не найден в .env.local" -ForegroundColor Yellow
    }
} else {
    Write-Host "    [OK] .env.local не существует (используется дефолт из кода)" -ForegroundColor Green
}

# Check Frontend lib/api.ts
Write-Host ""
Write-Host "[2] Проверка Frontend lib/api.ts..." -ForegroundColor Yellow
if (Test-Path "frontend\moderator-dashboard-ui\lib\api.ts") {
    $apiContent = Get-Content "frontend\moderator-dashboard-ui\lib\api.ts" -Raw
    if ($apiContent -match '8000') {
        Write-Host "    [OK] api.ts использует правильный порт 8000" -ForegroundColor Green
    } else {
        Write-Host "    [ERROR] api.ts НЕ использует порт 8000!" -ForegroundColor Red
        $allOk = $false
    }
}

# Check Backend start script
Write-Host ""
Write-Host "[3] Проверка Backend start-backend.ps1..." -ForegroundColor Yellow
if (Test-Path "start-backend.ps1") {
    $backendContent = Get-Content "start-backend.ps1" -Raw
    if ($backendContent -match '--port 8000') {
        Write-Host "    [OK] start-backend.ps1 использует порт 8000" -ForegroundColor Green
    } else {
        Write-Host "    [ERROR] start-backend.ps1 НЕ использует порт 8000!" -ForegroundColor Red
        $allOk = $false
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($allOk) {
    Write-Host "ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!" -ForegroundColor Green
} else {
    Write-Host "НАЙДЕНЫ ПРОБЛЕМЫ КОНФИГУРАЦИИ!" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan
