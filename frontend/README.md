# PythoNyashka — фронтенд

Клиентская часть PythoNyashka: React 19, Vite 7, TypeScript, Tailwind CSS 4, React Router, TanStack Query.

## Требования

- Node.js 20.19+ или 22.12+ (проверялось на 26.x)
- npm

## Установка и запуск

### Локально (без Docker)

```powershell
cd frontend
npm install
npm run dev
```

Сервер поднимается на http://localhost:5173 в mock-режиме (см. ниже).

### Через Docker (вместе со всем стеком)

Из корня репозитория:

```powershell
docker compose -f .docker/docker-compose-dev.yaml up -d
```

Поднимает весь бэкенд-стек (postgres, minio, kafka, auth, profile, media, notification, bff) и этот фронтенд. В compose фронт работает в dev-режиме: исходники проброшены bind-mount'ом, HMR работает как при локальном запуске. Режим по умолчанию в compose — `hybrid`.

Внимание: контейнер и локальный dev-сервер занимают один и тот же порт (5173) — одновременно запущено должно быть что-то одно.

## Режимы работы API

Переключаются переменной `VITE_USE_MOCKS`:

| Значение | Что происходит |
|---|---|
| `true` | Полностью автономный режим на встроенных моках: демо-автологин, сидированные данные, бэкенд не нужен. Значение по умолчанию при локальном запуске. |
| `hybrid` | Аккаунт, анкета, медиа и уведомления ходят на реальный BFF; лента, мэтчи и чаты остаются на моках — это демо-режим. Значение по умолчанию в docker-compose. |
| `false` | Всё на реальный BFF. Мэтчи и чаты работают вживую, свайпы пишутся в реальный match-сервис. Ограничение: BFF пока не отдаёт чужие анкеты (нет `GET /profiles/{id}`), поэтому карточки ленты и собеседники в чатах показываются плейсхолдерами «Анкета/Чат» без имён и фото. |

PowerShell:

```powershell
$env:VITE_USE_MOCKS='hybrid'; npm run dev
```

Git Bash:

```bash
VITE_USE_MOCKS=hybrid npm run dev
```

Переменную можно зафиксировать в файле `.env` (пример разметки — в `.env.example`) либо задать перед `docker compose up` для контейнерного запуска.

## Прокси до бэкенда

Vite-прокси заворачивает все запросы `/api/*` на BFF. По умолчанию таргет — `http://localhost:8003`. Если фронтенд живёт внутри docker-сети, таргет перекрывается переменной `VITE_PROXY_TARGET` (в compose она уже задана как `http://bff:8000`).

## Скрипты

| Команда | Что делает |
|---|---|
| `npm run dev` | dev-сервер с HMR |
| `npm run build` | typecheck + прод-сборка в `dist/` |
| `npm run preview` | локальный предпросмотр прод-сборки |
| `npm run typecheck` | только проверка типов |

## Обновление зависимостей (Docker-вариант)

Node-модули живут в именованном volume, поэтому при изменении `package.json` одной пересборкой не обойтись:

```powershell
docker compose -f .docker/docker-compose-dev.yaml stop frontend
docker volume rm pytonyashka_frontend_modules
docker compose -f .docker/docker-compose-dev.yaml build frontend
docker compose -f .docker/docker-compose-dev.yaml up -d frontend
```

Если менялись только исходники — ничего пересобирать не нужно, bind-mount и HMR подхватят изменения сами.