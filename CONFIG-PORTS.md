# Конфигурация портов

## Важно! Все сервисы должны использовать следующие порты:

| Сервис | Порт | URL |
|--------|------|-----|
| Chrome CDP | 9222 | http://127.0.0.1:9222 |
| Parser Service | 9003 | http://127.0.0.1:9003 |
| Backend | 8000 | http://127.0.0.1:8000 |
| Frontend | 3000 | http://localhost:3000 |

---

## ⚠️ Частая ошибка: неправильный порт Backend (8001 вместо 8000)

### Как проверить:

Запустите: `check-config.bat` или `.\check-config.ps1`

### Где может быть неправильный порт:

#### 1. Frontend `.env.local` (самая частая ошибка)

**Файл**: `frontend/moderator-dashboard-ui/.env.local`

**❌ Неправильно:**
```
NEXT_PUBLIC_API_URL=http://localhost:8001
```

**✅ Правильно:**
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

**Решение:**
1. Исправьте файл
2. Удалите кеш: `Remove-Item -Recurse -Force frontend/moderator-dashboard-ui/.next`
3. Перезапустите Frontend
4. В браузере: Ctrl+Shift+R (жесткая перезагрузка)

#### 2. Frontend `lib/api.ts`

**Файл**: `frontend/moderator-dashboard-ui/lib/api.ts`

**✅ Правильно:**
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
```

#### 3. Backend скрипт запуска

**Файл**: `start-backend.ps1`

**✅ Правильно:**
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Почему возникает проблема?

1. **`.env.local` переопределяет дефолтные значения** из кода
2. Next.js кеширует переменные окружения в `.next` директории
3. Браузер кеширует JavaScript файлы

---

## Как избежать проблемы?

### При первом запуске:

1. **НЕ создавайте** `.env.local` файл вручную
2. Если нужно переопределить URL, используйте `.env.example` как шаблон
3. Запустите `check-config.bat` для проверки

### После изменения конфигурации:

1. Остановите Frontend (Ctrl+C)
2. Удалите кеш: `Remove-Item -Recurse -Force frontend/moderator-dashboard-ui/.next`
3. Перезапустите Frontend: `4-start-frontend.bat`
4. В браузере: Ctrl+Shift+R (жесткая перезагрузка)

### Регулярная проверка:

Запускайте `check-config.bat` после:
- Клонирования репозитория
- Обновления из Git
- Изменения конфигурации
- Появления ошибок подключения

---

## Что делать, если порты заняты?

### Проверить, какой процесс использует порт:

```powershell
# Windows PowerShell
netstat -ano | findstr ":<PORT>"
```

### Остановить процесс:

```powershell
# Остановить все сервисы проекта
Get-Process -Name "chrome", "python*", "node*" | Stop-Process -Force
```

---

## Автоматическая проверка

Скрипт `check-config.ps1` автоматически проверяет:

- ✅ Frontend `.env.local` использует порт 8000
- ✅ Frontend `lib/api.ts` использует порт 8000
- ✅ Backend `start-backend.ps1` использует порт 8000

**Запуск:**
```powershell
# Windows
.\check-config.bat

# PowerShell
.\check-config.ps1
```

---

**Дата последнего обновления**: 24 декабря 2025

