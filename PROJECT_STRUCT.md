```text
employee-rating/
├── backend/                  # Backend приложение (FastAPI)
├── frontend/                 # Frontend приложение (React/Vite)
├── nginx/                    # (опционально) nginx конфиги/прокси
├── docker-compose.yml        # запуск всего стека
├── .env                      # переменные окружения
├── USE_CASES.md              # сценарии использования
├── API_SPECIFICATION.md      # спецификация API
├── TECHNOLOGY_JUSTIFICATION.md
├── ENTITIES.md               # сущности системы
└── ER_DIAGRAM.md             # ER диаграмма

backend/
├── app/
│   ├── main.py                        # создание FastAPI app + router + health
│   ├── config.py                      # настройки (env → Settings)
│   │
│   ├── api/                           # API слой
│   │   ├── deps.py                    # зависимости (db session, cache)
│   │   └── v1/
│   │       ├── router.py              # агрегатор роутеров
│   │       ├── employees.py           # endpoints сотрудников
│   │       ├── departments.py         # endpoints отделов
│   │       ├── ratings.py             # endpoints рейтингов/снапшотов/импорта
│   │       └── reports.py             # endpoints отчётов (заглушка/основа)
│   │
│   ├── core/                          # Domain слой
│   │   ├── exceptions.py              # доменные ошибки
│   │   └── services/
│   │       ├── import_service.py      # разбор/валидация CSV
│   │       ├── rating_calculator.py   # валидация и вычисление дельт
│   │       └── snapshot_service.py    # построение снимка рейтинга
│   │
│   ├── infrastructure/                # Infrastructure слой
│   │   ├── database/
│   │   │   ├── base.py                # Base + TimestampMixin
│   │   │   ├── session.py             # engine + session factory
│   │   │   └── models/
│   │   │       ├── department.py
│   │   │       ├── employee.py
│   │   │       ├── rating.py          # RatingEntry/Metric/Snapshot + enum
│   │   │       └── __init__.py
│   │   ├── cache/
│   │   │   ├── redis_client.py        # клиент redis (async)
│   │   │   └── rating_cache.py        # кэш снимков
│   │   └── tasks/
│   │       ├── celery_app.py          # Celery (если включаем фоновые задачи)
│   │       └── report_tasks.py
│   │
│   └── schemas/                       # Pydantic схемы API
│       ├── employee.py
│       ├── department.py
│       ├── rating.py
│       └── common.py
│
├── alembic/                            # миграции БД
│   ├── env.py
│   ├── versions/
│   └── script.py.mako
│
└── tests/                              # unit + integration тесты
    ├── conftest.py
    ├── unit/
    └── integration/

frontend/
├── index.html
├── vite.config.ts
├── package.json
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── api/
    │   └── client.ts              # axios client + типы + методы
    ├── pages/
    │   └── Dashboard.tsx          # основная страница (таблица + график)
    ├── components/
    │   ├── tables/RatingTable.tsx
    │   └── charts/RatingTrendChart.tsx
    └── hooks/
        └── useRatingData.ts       # react-query хуки

