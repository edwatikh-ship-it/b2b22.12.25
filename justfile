# B2B Platform - Task Runner

default: dev
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# Запустить backend + frontend параллельно
dev:
    powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd D:\b2b\backend; uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload' -WindowStyle Minimized"
    powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd D:\b2b\frontend\moderator-dashboard-ui; npm run dev' -WindowStyle Minimized"

# Backend только
backend:
    cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Frontend только
frontend:
    cd frontend/moderator-dashboard-ui && npm run dev

# Тесты + линтер
test:
    pre-commit run --all-files || true
    cd backend && uv run pytest

# Очистка кэшей и временных файлов
clean:
    powershell -Command "Get-ChildItem -Path backend -Recurse -Include __pycache__,*.pyc,.pytest_cache,.ruff_cache -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
    powershell -Command "Get-ChildItem -Path frontend/moderator-dashboard-ui -Recurse -Include node_modules,.next -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
    powershell -Command "if (Test-Path 'D:\b2bplatform.tmp') { Remove-Item -Path 'D:\b2bplatform.tmp' -Recurse -Force -ErrorAction SilentlyContinue }"

# Утилиты для работы с API
list-endpoints:
    powershell ./tools/list-endpoints.ps1

endpoint-status PATH:
    powershell ./tools/endpoint-status.ps1 {{PATH}}

stub-endpoint PATH:
    powershell ./tools/stub-endpoint.ps1 {{PATH}}
