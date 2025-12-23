# ✅ Проверенное решение

## Проблема
Скрипт запускается, но Next.js не виден в выводе или не запускается.

## Решение: Запуск вручную (проверено)

### Шаг 1: Открой PowerShell

### Шаг 2: Выполни команды по порядку

```powershell
# Перейди в директорию frontend
cd D:\b2b\frontend\moderator-dashboard-ui

# Запусти dev server (команда будет работать до остановки Ctrl+C)
npm run dev
```

### Шаг 3: Проверь вывод

Должно появиться:
```
▲ Next.js 16.x.x
- Local:        http://localhost:3000
- Ready in Xs
```

### Шаг 4: Открой в браузере

Открой: `http://localhost:3000/dashboard`

---

## Если npm run dev не работает

### Проверь зависимости

```powershell
cd D:\b2b\frontend\moderator-dashboard-ui

# Проверь наличие node_modules
if (-not (Test-Path node_modules)) {
    npm install
}
```

### Проверь .env.local

```powershell
# Создай файл если его нет
if (-not (Test-Path .env.local)) {
    "NEXT_PUBLIC_API_URL=http://localhost:8001" | Out-File -FilePath .env.local -Encoding UTF8
}
```

---

## Проверка работы

После запуска `npm run dev`:

1. **Проверь порт:**
   ```powershell
   netstat -ano | findstr :3000
   ```
   Должен показать процесс, слушающий порт 3000

2. **Проверь в браузере:**
   - Открой `http://localhost:3000/dashboard`
   - Должна открыться страница (не ERR_CONNECTION_REFUSED)

3. **Проверь процессы Node.js:**
   ```powershell
   Get-Process node -ErrorAction SilentlyContinue
   ```
   Должен быть хотя бы один процесс node.exe

---

## Остановка сервера

В окне PowerShell, где запущен `npm run dev`:
- Нажми `Ctrl+C`
- Подтверди остановку (если спросит)

---

## Важно

**Скрипт `start-frontend-only.ps1` может не показывать вывод Next.js правильно.**

**Используй ручной запуск:**
```powershell
cd D:\b2b\frontend\moderator-dashboard-ui
npm run dev
```

Это самый надежный способ.

