# Скрипт запуска Chrome в режиме отладки для парсера

Write-Host "🔧 Запуск Chrome с режимом отладки..." -ForegroundColor Cyan

# Остановка всех процессов Chrome
Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Путь к Chrome
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"

# Запуск с отладкой (окно PowerShell останется открытым)
& $chromePath --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug

Write-Host "✅ Chrome запущен!" -ForegroundColor Green
Write-Host "⚠ НЕ ЗАКРЫВАЙТЕ это окно PowerShell!" -ForegroundColor Yellow
Write-Host "📌 Для запуска парсера откройте НОВОЕ окно и выполните:" -ForegroundColor Cyan
Write-Host "   cd D:\ProjectVC\search-parser" -ForegroundColor White
Write-Host "   .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   python cli.py кирпич 3 yandex" -ForegroundColor White
