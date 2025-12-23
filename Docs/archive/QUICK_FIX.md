# 🚀 Быстрое решение проблемы с Frontend

## Проблема: Frontend не запускается

### Решение 1: Запуск из правильной директории

```powershell
# Перейди в директорию frontend
cd D:\b2b\frontend\moderator-dashboard-ui

# Запусти dev server
npm run dev
```

### Решение 2: Использование скрипта (если политика выполнения разрешает)

```powershell
# Из корня проекта
cd D:\b2b

# Запусти скрипт с обходом политики
powershell -ExecutionPolicy Bypass -File .\start-frontend-only.ps1
```

### Решение 3: Ручной запуск с проверками

```powershell
# 1. Перейди в директорию frontend
cd D:\b2b\frontend\moderator-dashboard-ui

# 2. Проверь наличие package.json
if (Test-Path package.json) {
    Write-Host "OK: package.json found"
} else {
    Write-Host "ERROR: package.json not found"
    exit
}

# 3. Проверь зависимости
if (-not (Test-Path node_modules)) {
    Write-Host "Installing dependencies..."
    npm install
}

# 4. Проверь .env.local
if (-not (Test-Path .env.local)) {
    Write-Host "Creating .env.local..."
    "NEXT_PUBLIC_API_URL=http://localhost:8001" | Out-File -FilePath .env.local -Encoding UTF8
}

# 5. Запусти сервер
npm run dev
```

---

## Проверка работы

После запуска `npm run dev` должно появиться:

```
  ▲ Next.js 16.x.x
  - Local:        http://localhost:3000
  - Ready in Xs
```

Открой в браузере: `http://localhost:3000/dashboard`

---

## Если все еще не работает

### Проверь порт 3000

```powershell
netstat -ano | findstr :3000
```

Если порт занят, либо останови процесс, либо измени порт:

```powershell
# В package.json измени:
# "dev": "next dev -p 3001"
```

### Проверь логи

В консоли PowerShell, где запущен `npm run dev`, должны быть видны ошибки (если есть).

### Полная переустановка

```powershell
cd D:\b2b\frontend\moderator-dashboard-ui

# Удали node_modules
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue

# Переустанови зависимости
npm install

# Запусти заново
npm run dev
```

