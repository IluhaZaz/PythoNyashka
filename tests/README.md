# Автотесты PythoNyashka

## Единая команда и отчёт

Из корня репозитория запусти `poetry run poe check <набор>`. Выбрать можно один из следующих наборов.

| Набор | Что запускается |
| --- | --- |
| `auth`, `bff`, `profile`, `match`, `chat`, `media`, `notification` | Тесты выбранного API. Для Auth и Notification также запускаются связанные проверки фоновых операций. |
| `frontend` | Vitest для React и API-клиента. |
| `security` | Проверки JWT, прав доступа, TLS и топологии production Compose. |
| `backend` | Весь обычный набор pytest, включая проверки безопасности. |
| `e2e` | Сквозной сценарий на отдельном Compose-стенде. |
| `regression` | `backend`, `frontend` и `e2e` по очереди. Падение одного набора не отменяет остальные. |

```powershell
poetry run poe check chat
poetry run poe check security
poetry run poe check regression
poetry run poe check e2e --report-dir D:/test-results
```

Для фронтенда и полного регресса один раз установи Node.js и выполни `npm ci` внутри `frontend`. Для E2E также нужен OpenSSL. Если Python-окружение уже установлено, ту же команду можно запустить без Poetry, например `.\.venv\Scripts\python.exe scripts/run_tests.py chat`.

Во время каждого запуска создаётся новая папка в `test-reports/` или в каталоге, указанном через `--report-dir`. Открой `summary.txt`, чтобы увидеть статус каждого теста и краткую причину падения. Полный вывод лежит в `*.log`, отчёт для CI в формате JUnit — в `*.xml`. Общий код выхода равен `0` при успешном прогоне и `1` при падении теста, ошибке запуска или отсутствии отчёта. Ожидаемые падения (`XFAIL`) отмечаются отдельно.

## Прямой запуск pytest

Для полного прогона нужны Python 3.11, Poetry и запущенный Docker. Команды выполняются из корня репозитория.

```powershell
poetry install --no-root
poetry run pytest -rxX
```

Наборы можно запускать отдельно.

```powershell
poetry run pytest tests/bff tests/workers
poetry run pytest tests/services
poetry run pytest --cov=src --cov-branch --cov-report=term-missing -rxX
```

| Набор | Что проверяет |
| --- | --- |
| [BFF](bff/) | 17 публичных операций. Проверяет FastAPI, JWT, реальные сгенерированные клиенты, исходящие запросы и преобразование ответов. Ответы внутренних API задаются через HTTPX MockTransport. |
| [Внутренние API](services/) | 21 операция Auth, Profile, Media, Chat, Match и Notification через FastAPI, use cases и реальные SQLAlchemy-репозитории. Прогон поднимает отдельный PostgreSQL 16 на случайном порту loopback и применяет `alembic upgrade head`. Каждая проверка откатывает свои изменения, контейнер удаляется после прогона. |
| [Фоновые операции](workers/) | Проверяет обработку событий Kafka, повторы при сбоях, подтверждение смещений и составление писем. Брокер, SMTP и S3 заменяются тестовыми объектами. Сохранение уведомлений воркером проверяется в PostgreSQL в [test_notification_worker.py](services/test_notification_worker.py). |

Автосгенерированные страницы Swagger UI и ReDoc в подсчёт операций не входят. Тесты используют синтетические данные. Файлы `.docker/.env` и `.docker/.env.prod` для прогона не нужны.

## Ожидаемые падения

- Повторная регистрация напрямую в Auth приводит к необработанному `IntegrityError`. В контракте указан HTTP 400.
- При отсутствии поля `file` Media возвращает HTTP 422. В контракте указан HTTP 400.
- Отрицательные `limit` и `offset` в Notification передаются в PostgreSQL и приводят к ошибке запроса. Проверки ожидают HTTP 422.

Ошибки 413 и 415 от Media проверены на уровне BFF. В Media пока отсутствуют проверка допустимых типов и отдельный порог размера загрузки, по которым эти ответы мог бы вернуть сам сервис.

Сквозной прогон с реальным обменом между сервисами запускается отдельно командой `poetry run pytest tests/e2e -m e2e`. Утверждённые шаги и условия стенда описаны в [сценарии](E2E.md).

Проверки безопасности можно запустить командой `poetry run pytest -m security`. В этот набор входят проверки JWT, изоляции refresh-сессий, доступа к профилям, чатам, матчам и уведомлениям, настройки TLS для SMTP и сетевая схема production Compose. Проверка Compose анализирует локальную конфигурацию без подстановки значений из файлов сервисов.
