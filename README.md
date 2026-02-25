# GrantsAssistant

Веб-приложение для управления грантами с AI-ассистентом (Claude Sonnet).

## Быстрый старт

### 1. Настройка backend

```bash
cd backend
cp .env.example .env
# Заполните .env: ANTHROPIC_API_KEY, SMTP настройки, TELEGRAM_BOT_TOKEN

pip install -r requirements.txt

# Инициализация БД + заполнение данными из Excel
python scripts/seed_from_excel.py

# Запуск
uvicorn app.main:app --reload
```

API доступен на http://localhost:8000
Документация: http://localhost:8000/docs

### 2. Настройка frontend

```bash
cd frontend
npm install
npm run dev
```

Сайт открывается на http://localhost:5173

### 3. Docker Compose (оба сервиса)

```bash
ANTHROPIC_API_KEY=sk-ant-... docker-compose up
```

## Данные для входа (после seed)

- Email: `admin@grants.local`
- Пароль: `admin123`

## Структура

```
grants-assistant/
├── backend/          # FastAPI + SQLAlchemy + Claude AI
│   ├── app/
│   │   ├── models/   # Grant, User, Application, Notification
│   │   ├── routers/  # auth, grants, applications, ai, documents, notifications, admin
│   │   └── services/ # ai_service, document_service, scraper, notifications, scheduler
│   └── scripts/seed_from_excel.py
├── frontend/         # React + Vite + TypeScript + Tailwind
│   └── src/
│       ├── pages/    # HomePage, Dashboard, GrantDetail, Wizard, Profile, Admin
│       └── components/
└── docker-compose.yml
```

## Деплой на Railway

1. Подключите GitHub репозиторий
2. Создайте 2 сервиса: `grants-backend` (Python) и `grants-frontend` (Node)
3. Добавьте PostgreSQL плагин Railway
4. Укажите env vars: `ANTHROPIC_API_KEY`, `SECRET_KEY`, `SMTP_*`, `TELEGRAM_BOT_TOKEN`
5. Railway автоматически определит `DATABASE_URL` из `PGHOST`, `PGUSER` и т.д.

## Функциональность

- **Каталог грантов** — 10 грантов из Excel с фильтрами
- **Дедлайны** — таймеры обратного отсчёта, сортировка по ближайшему дедлайну
- **Уведомления** — Email, Telegram, Push (за 30/14/7/1 день)
- **AI-ассистент** — подсказки Claude при заполнении заявки
- **Мастер заявки** — 5 шагов с автосохранением
- **Генерация документов** — PDF (reportlab) и DOCX (python-docx)
- **Парсер** — httpx → BeautifulSoup → Playwright → Claude AI
- **APScheduler** — еженедельный парсинг + ежедневные напоминания
