# Запуск Chrome с вашим основным профилем

Write-Host "🔧 Остановка всех Chrome..." -ForegroundColor Cyan
Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 3

Write-Host "🚀 Запуск Chrome с основным профилем..." -ForegroundColor Yellow

# Используем ваш обычный профиль (где вы уже авторизованы)
$userProfile = "$env:LOCALAPPDATA\Google\Chrome\User Data"

# ВАЖНО: Запускаем в фоне, чтобы окно PowerShell не блокировалось
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& 'C:\Program Files\Google\Chrome\Application\chrome.exe' --remote-debugging-port=9222 --user-data-dir='$userProfile'"

Write-Host "
✅ Chrome запускается с вашим профилем" -ForegroundColor Green
Write-Host "⏳ Подождите 10 секунд..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "
🎯 Теперь можно запускать парсер!" -ForegroundColor Green
