# 🔧 Troubleshooting Guide

## Frontend не запускается (ERR_CONNECTION_REFUSED)

### Проблема: `http://localhost:3000` недоступен

### Решение 1: Проверь окно PowerShell для Frontend

После запуска `start-dev.ps1` должно открыться **2 окна PowerShell**:
1. Одно для Backend (порт 8001)
2. Одно для Frontend (порт 3000)

**Проверь окно Frontend:**
- Есть ли ошибки в консоли?
- Видно ли сообщение "Ready" или "Local: http://localhost:3000"?

### Решение 2: Запусти Frontend вручную

```powershell
cd D:\b2b\frontend\moderator-dashboard-ui
npm run dev
```

**Если видишь ошибки:**
- `node_modules not found` → выполни `npm install`
- `Port 3000 is already in use` → останови процесс на порту 3000 или измени порт

### Решение 3: Проверь зависимости

```powershell
cd frontend\moderator-dashboard-ui

# Проверь наличие node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..."
    npm install
}

# Запусти вручную
npm run dev
```

### Решение 4: Проверь порты

```powershell
# Проверь, занят ли порт 3000
netstat -ano | findstr :3000

# Если занят, найди процесс и останови его
# Или измени порт в package.json:
# "dev": "next dev -p 3001"
```

---

## Backend не запускается

### Проверь окно PowerShell для Backend

Должно быть видно:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete.
```

### Запусти Backend вручную

```powershell
cd D:\b2b\backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

---

## Оба сервера не запускаются

### Проверь предпосылки

```powershell
# Python
python --version
# Должно быть Python 3.12+

# Node.js
node --version
# Должно быть Node 20+

# uv
uv --version
# Если нет, установи: pip install uv
```

### Переустанови зависимости

```powershell
# Backend
cd backend
uv sync

# Frontend
cd frontend\moderator-dashboard-ui
npm install
```

---

## Frontend не подключается к Backend

### Проверь .env.local

Файл должен быть: `frontend/moderator-dashboard-ui/.env.local`

Содержимое:
```
NEXT_PUBLIC_API_URL=http://localhost:8001
```

### Проверь CORS в Backend

Backend должен разрешать запросы с `http://localhost:3000`.

Проверь `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    ...
)
```

---

## Быстрая диагностика

```powershell
# 1. Проверь порты
netstat -ano | findstr ":3000 :8001"

# 2. Проверь процессы Node.js
Get-Process node -ErrorAction SilentlyContinue

# 3. Проверь процессы Python
Get-Process python -ErrorAction SilentlyContinue

# 4. Проверь логи в окнах PowerShell
# (должны быть видны ошибки, если есть)
```

---

## Полный перезапуск

```powershell
# 1. Останови все процессы
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Очисти кэши
cd D:\b2b
just clean

# 3. Переустанови зависимости
cd backend
uv sync

cd ..\frontend\moderator-dashboard-ui
npm install

# 4. Запусти заново
cd D:\b2b
.\start-dev.ps1
```




