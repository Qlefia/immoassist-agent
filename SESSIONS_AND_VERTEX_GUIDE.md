## Руководство по интеграции: сессии, БД, Firebase и Vertex AI (ADK)

### Содержание

- Общая модель данных и терминов
- Вариант A (рекомендуется для прод): SQL-БД (SQLite локально, Postgres/MySQL на проде)
- Вариант B: Vertex AI Session Service (облачная персистентность)
- Аутентификация реальных пользователей через Firebase (и привязка userId)
- Изменения по файлам проекта (пошагово)
- ЧаВо и типовые проблемы

---

## Общая модель данных ADK: пользователь → сессии → события

Логическая схема для любого хранилища (БД или Vertex AI):

```mermaid
erDiagram
    USER ||--o{ SESSION : "имеет"
    SESSION ||--o{ EVENT : "включает"

    USER {
      string user_id PK
      string email
      json   profile
      ts     created_at
    }

    SESSION {
      string session_id PK
      string app_name
      string user_id FK
      json   state               "ключ-значение с префиксами (user./app./без префикса)"
      ts     created_at
      ts     last_update_time
      bool   active
    }

    EVENT {
      string event_id PK
      string session_id FK
      string author          "user | agent | tool"
      string role            "user | model"
      ts     timestamp
      json   parts           "текст/функции/ответы"
      json   grounding_metadata
      json   usage_metadata
    }
```

Session:
  - id: str                    # Постоянный ID сессии
  - app_name: str             # Название приложения
  - user_id: str              # ID пользователя
  - state: dict               # Состояние сессии
  - events: list              # История событий/сообщений
  - last_update_time: datetime # Время последнего обновления

Принципы ADK:

- Один `userId` → много `sessionId` (мультисессионность).
- В каждой сессии хранится история `events` и `state`.
- `state` использует умные префиксы:
  - без префикса — состояние конкретной сессии;
  - `user.` — пользовательские настройки (общие для всех сессий пользователя);
  - `app.` — глобальные настройки приложения.

```python
Управление сессиями пользователя:
# 1. Создание новой сессии для пользователя
session = await session_service.create_session(
    app_name="immoassist",
    user_id="user_123",
    session_id=None  # Автогенерируется или можно задать свой
)

# 2. Получение всех сессий пользователя
user_sessions = await session_service.list_sessions(
    app_name="immoassist",
    user_id="user_123"
)

# 3. Восстановление конкретной сессии
existing_session = await session_service.get_session(
    app_name="immoassist",
    user_id="user_123",
    session_id="session_abc123"
)

# 4. Получение истории событий сессии
events = await session_service.list_events(
    app_name="immoassist",
    user_id="user_123",
    session_id="session_abc123"
)
```

Управление состоянием сессии
ADK поддерживает умные префиксы для состояния:

```python
# Состояние сессии (по умолчанию)
session.state['current_step'] = 'property_analysis'

# Состояние пользователя (общее для всех сессий пользователя)
session.state['user:language'] = 'ru'
session.state['user:preferences'] = {'currency': 'EUR'}

# Глобальное состояние приложения
session.state['app:version'] = '1.0'

# Временное состояние (не сохраняется)
session.state['temp:api_response'] = {...}
```
## Как реализовано сейчас

.env:

```
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=29448644777
MODEL_NAME=gemini-2.5-flash
SPECIALIST_MODEL=gemini-2.5-flash
CHAT_MODEL=gemini-2.5-flash
PORT=8000
# GOOGLE_APPLICATION_CREDENTIALS=C:\Users\Coldh\Desktop\immoassist\app\gothic-agility-464209-f4-39095fb8e054copy.json (закомментировано)
RAG_CORPUS=projects/.../ragCorpora/...
PRESENTATION_RAG_CORPUS=projects/.../ragCorpora/...
LEGAL_RAG_CORPUS=projects/.../ragCorpora/...
ELEVENLABS_API_KEY=...
SESSION_SERVICE_URI=vertexai://
SESSION_SERVICE_URI=sqlite:///./sessions.db
```

Фактическая конфигурация: используется **SQLite** (`sqlite:///./sessions.db`), т.к. строка ниже перекрывает верхнюю. Это персистентное локальное хранилище файла `sessions.db` — при рестарте процесса данные не теряются. В продакшене лучше перейти на Postgres/MySQL (см. «Вариант A»).

Замечание: `vertexai://` как URI для `session_service_uri` ADK **не поддерживает**. Для Vertex Ai Session Service требуется программная инициализация (см. «Вариант B»).

---

## Вариант A: SQL-БД

Идея: оставить маршруты ADK как есть и переключить SessionService на БД. На локали — `SQLite`, на проде — `PostgreSQL`/`MySQL`.

### .env

Локально (оставить):

```
SESSION_SERVICE_URI=sqlite:///./sessions.db
```

Прод (пример для Postgres):

```
SESSION_SERVICE_URI=postgresql://USER:PASSWORD@HOST:5432/DBNAME
```

### Что хранится в БД

- Таблица sessions (id, app_name, user_id, state JSON, created_at, last_update_time, active)
- Таблица events (id, session_id, author/role, timestamp, parts JSON, grounding_metadata JSON, usage_metadata JSON)

ADK `DatabaseSessionService` создаёт и ведёт эти структуры под капотом. Вам важно обеспечить доступность БД и бэкапы.

### Плюсы/минусы

Плюсы: привычная эксплуатация, прозрачность данных, горизонтальное масштабирование сервиса. Минусы: нужно управлять БД.

---

## Вариант B: Vertex AI Session Service

Идея: хранить сессии и события в **управляемом облачном хранилище** Vertex AI. Подходит, если вы уже на GCP и хотите меньше DevOps.

Важно: в ADK выражение `session_service_uri=vertexai://` не поддерживается. Требуется программная инициализация `VertexAiSessionService(project, location)` и передача её в сборку FastAPI-приложения.

### Требования для Vertex

- Включённый Vertex AI в проекте GCP (`GOOGLE_CLOUD_PROJECT`)
- Аутентификация: сервисный аккаунт/ADC
  - Локально — `GOOGLE_APPLICATION_CREDENTIALS=...json`
  - На Cloud Run/GKE — Workload Identity/привязанный SA
- `LOCATION` (например, `us-central1`)
- Для некоторых сценариев ADK app_name должен соответствовать ресурсу Reasoning/Agent Engine ID

### Пример программной инициализации (Python)

```python
# Требуется: pip install google-adk[vertexai]
from google.adk.sessions import VertexAiSessionService

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# ⚠️ ВАЖНО: app_name должен соответствовать Reasoning Engine ID
REASONING_ENGINE_APP_NAME = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/your-engine-id"

vertex_session_service = VertexAiSessionService(project=PROJECT_ID, location=LOCATION)

# При использовании VertexAiSessionService app_name должен быть полным resource name
# session = await vertex_session_service.create_session(
#     app_name=REASONING_ENGINE_APP_NAME,
#     user_id="user123"
# )
```

### Создание Reasoning Engine в Vertex AI

Прежде чем использовать `VertexAiSessionService`, необходимо создать Reasoning Engine:

```bash
# Включить Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Аутентификация
gcloud auth application-default login

# Создать Reasoning Engine (через Console или gcloud CLI)
gcloud ai reasoning-engines create \
  --location=us-central1 \
  --display-name="ImmoAssist-Engine" \
  --project=your-project-id
```

Либо через веб-консоль: Cloud Console → Vertex AI → Reasoning Engines → Create.

### Плюсы/минусы

Плюсы: менеджед-персистентность, меньше DevOps. Минусы: привязка к GCP, квоты, необходима поддержка инъекции SessionService в вашей версии ADK.

---

## Аутентификация реальных пользователей (Firebase) и привязка userId

По умолчанию в проекте использовался тестовый userId (`u_999`). Для продакшена нужно заменить на реальный `uid` из Firebase Auth (или вашего auth сервиса). Схема:

1. Фронтенд логинит пользователя в Firebase (email/password или magic link), получает `idToken` и `uid`.
2. Все вызовы `/apps/{appName}/users/{userId}/...` выполняются с `Authorization: Bearer <idToken>` и `userId=uid`.
3. Бэкенд проверяет токен и запрещает несоответствие `uid` ↔ `userId` в URL.

### .env для Vertex AI

```bash
# Основные переменные для Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Локально - путь к service account JSON
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# На Cloud Run/GKE - используется Workload Identity, переменная не нужна
# GOOGLE_APPLICATION_CREDENTIALS - не устанавливать
```

### .env для Firebase

```bash
FIREBASE_PROJECT_ID=<ваш_project_id>
GOOGLE_APPLICATION_CREDENTIALS=<путь_к_service_account.json_с_Firebase_Admin_правами>
```

### Важные примечания по Vertex AI аутентификации

**Локальная разработка:**

- Устанавливайте `GOOGLE_APPLICATION_CREDENTIALS` на путь к JSON файлу service account
- Service account должен иметь роли: `Vertex AI User`, `Vertex AI Developer`

**Продакшен на GCP (Cloud Run/GKE):**

- Используйте Workload Identity
- НЕ устанавливайте `GOOGLE_APPLICATION_CREDENTIALS`
- Привяжите Kubernetes Service Account к Google Service Account

```bash
# Пример настройки Workload Identity
gcloud iam service-accounts add-iam-policy-binding \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:PROJECT-ID.svc.id.goog[NAMESPACE/KSA-NAME]" \
  GSA-NAME@PROJECT-ID.iam.gserviceaccount.com
```

### app/auth/firebase.py (новый)

```python
import os
import firebase_admin
from firebase_admin import auth, credentials
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

def init_firebase_admin():
    if not firebase_admin._apps:
        cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
        firebase_admin.initialize_app(cred, {"projectId": os.getenv("FIREBASE_PROJECT_ID")})

def verify_bearer_token(auth_header: str) -> str:
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise ValueError("Missing/invalid Authorization header")
    token = auth_header.split(" ", 1)[1].strip()
    decoded = auth.verify_id_token(token)
    return decoded["uid"]

class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        if path.startswith("/apps/") and "/users/" in path:
            try:
                uid = verify_bearer_token(request.headers.get("authorization"))
                parts = path.strip("/").split("/")
                user_idx = parts.index("users") + 1
                path_user = parts[user_idx]
                if path_user != uid:
                    return JSONResponse({"detail": "Forbidden: uid mismatch"}, status_code=403)
                request.state.uid = uid
            except Exception as e:
                return JSONResponse({"detail": f"Unauthorized: {e}"}, status_code=401)
        return await call_next(request)
```

### run_agent.py — подключение SessionService и middleware

**Вариант A (SQL БД):**

```python
import os
from google.adk.apps import get_fast_api_app
from app.auth.firebase import init_firebase_admin, FirebaseAuthMiddleware

def main():
    agents_path = "app"  # путь к агентам

    # Для SQL БД используем session_service_uri
    session_service_uri = os.getenv("SESSION_SERVICE_URI", "sqlite:///./sessions.db")

    app = get_fast_api_app(
        agents_dir=agents_path,
        web=True,
        allow_origins=["*"],
        session_service_uri=session_service_uri
    )

    # Firebase Auth middleware
    init_firebase_admin()
    app.add_middleware(FirebaseAuthMiddleware)

    # Запуск сервера
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
```

**Вариант B (Vertex AI - если поддерживается):**

```python
import os
from google.adk.apps import get_fast_api_app
from google.adk.sessions import VertexAiSessionService
from app.auth.firebase import init_firebase_admin, FirebaseAuthMiddleware

def main():
    agents_path = "app"

    # ⚠️ ПроверBNM поддержку ADK
    try:
        vertex_session_service = VertexAiSessionService(
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        )

        app = get_fast_api_app(
            agents_dir=agents_path,
            web=True,
            allow_origins=["*"],
            session_service=vertex_session_service  # Прямая передача сервиса
        )
    except TypeError as e:
        # Fallback на SQL БД если session_service не поддерживается
        print(f"VertexAiSessionService не поддерживается: {e}")
        print("Используем SQL БД...")
        app = get_fast_api_app(
            agents_dir=agents_path,
            web=True,
            allow_origins=["*"],
            session_service_uri=os.getenv("SESSION_SERVICE_URI", "sqlite:///./sessions.db")
        )

    init_firebase_admin()
    app.add_middleware(FirebaseAuthMiddleware)

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

if __name__ == "__main__":
    main()
```

### frontend/index.html — Firebase SDK

```html
<script src="https://www.gstatic.com/firebasejs/10.12.1/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.1/firebase-auth-compat.js"></script>
<script>
  window.firebaseConfig = {
    apiKey: '<apiKey>',
    authDomain: '<project>.firebaseapp.com',
    projectId: '<project>',
  };
</script>
```

### frontend/apiClient.js — проброс токена и uid

```js
let authToken = null;
let authUid = null;

export async function initFirebaseAuth() {
  if (!window.firebase?.apps?.length) window.firebase.initializeApp(window.firebaseConfig);
  return new Promise((resolve) => {
    window.firebase.auth().onAuthStateChanged(async (user) => {
      if (user) {
        authUid = user.uid;
        authToken = await user.getIdToken(true);
        resolve(user);
      } else {
        resolve(null);
      }
    });
  });
}

function buildHeaders(extra = {}) {
  const h = { 'Content-Type': 'application/json', ...extra };
  if (authToken) h['Authorization'] = `Bearer ${authToken}`;
  return h;
}

export function getAuthUid() {
  return authUid;
}

export async function createSession(appName = 'app') {
  const userId = getAuthUid();
  const sessionId = generateUUID();
  const r = await fetch(`${API_BASE_URL}/apps/${appName}/users/${userId}/sessions/${sessionId}`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({}),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

export async function listUserSessions(appName = 'app') {
  const userId = getAuthUid();
  const r = await fetch(`${API_BASE_URL}/apps/${appName}/users/${userId}/sessions`, {
    headers: buildHeaders(),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}
```

В `frontend/script.js` в `init()` сначала вызывайте `await initFirebaseAuth()` и только затем создавайте/листайте сессии (так `userId` будет реальным `uid`).

---

## Сводные шаги по файлам проекта

- .env
  - Для БД: `SESSION_SERVICE_URI=postgresql://...` (прод) или `sqlite:///./sessions.db` (локально)
  - Для Vertex: `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GOOGLE_APPLICATION_CREDENTIALS` (локально) — и программная инициализация `VertexAiSessionService`
  - Для Firebase: `FIREBASE_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS` (service account)

- app/auth/firebase.py — добавить (см. код выше)
- run_agent.py — подключить Firebase middleware; `session_service_uri` оставить для варианта A
- frontend/index.html — добавить Firebase SDK и конфиг
- frontend/apiClient.js — инициализация Firebase, проброс токена и использование `uid` вместо `u_999`
- frontend/script.js — дождаться авторизации в `init()`

---

1. Почему `SESSION_SERVICE_URI=vertexai://` не работает?

- В ADK URI-режим предназначен для `DatabaseSessionService` (sqlite/postgres/mysql). Для Vertex нужен `VertexAiSessionService(project, location)` программно. Если ваша версия ADK не поддерживает инъекцию сервиса в `get_fast_api_app`, используйте БД.

2. Сессии не «протухают»?

- В in-memory — да. В SQLite/Postgres/Vertex — нет: это персистентные записи. Хранятся годами, пока вы их не удаляете или не превышаете квоты (Vertex).

3. Где посмотреть данные?

- В БД — обычные таблицы (sessions/events). В Vertex — через API ADK (list/get/listEvents/delete) или консоль Vertex (по мере доступности фич), это менеджед сущности.

4. Что выбрать на прод?

- На практике быстрее всего Postgres (Cloud SQL) + Firebase Auth. Если вы уже глубоко в Vertex AI и хотите меньше управлять БД — переходите на VertexAiSessionService, как только ваша версия ADK позволит инъекцию SessionService.

5. **Почему `list_sessions()` не содержит полных событий (events)?**

- **По документации ADK**: метод `list_sessions(*, app_name, user_id)` возвращает **только метаданные сессий** (`ListSessionsResponse`) БЕЗ полного содержимого `events`. Это сделано для производительности при получении списка.
- **Для получения событий** (сообщений диалога) нужно использовать:
  - `get_session(*, app_name, user_id, session_id)` — возвращает полную сессию включая `events[]`
  - `list_events(*, app_name, user_id, session_id)` — возвращает только события конкретной сессии (`ListEventsResponse`)

6. **Структура ответов ADK API:**

```python
# list_sessions() возвращает:
ListSessionsResponse = {
  "sessions": [
    {
      "id": "session_123",
      "app_name": "app",
      "user_id": "u_999",
      "state": {"key": "value"},  # JSON состояние
      "last_update_time": 1643617719.123,
      "events": []  # ПУСТОЙ массив! События НЕ включены
    }
  ]
}

# get_session() возвращает:
Session = {
  "id": "session_123",
  "app_name": "app",
  "user_id": "u_999",
  "state": {"key": "value"},
  "last_update_time": 1643617719.123,
  "events": [  # ПОЛНЫЙ массив событий
    {
      "id": "event_1",
      "author": "user",
      "content": {"parts": [{"text": "Привет"}]},
      "timestamp": 1643617719.100
    },
    {
      "id": "event_2",
      "author": "AgentName",
      "content": {"parts": [{"text": "Здравствуйте!"}]},
      "grounding_metadata": {...},  # RAG источники
      "timestamp": 1643617719.200
    }
  ]
}

# list_events() возвращает:
ListEventsResponse = {
  "events": [
    // ... те же объекты Event как в get_session().events
  ]
}
```

7. **Структура событий (Events) в ADK:**

```python
Event = {
  "id": "event_123",
  "author": "user",           # "user" | имя агента
  "invocation_id": "e-xyz...", # ID всего вызова
  "timestamp": 1643617719.100,
  "content": {                # Основное содержимое
    "role": "user",           # "user" | "model"
    "parts": [                # Массив частей сообщения
      {
        "text": "Привет, как дела?"  # Текст сообщения
      }
    ]
  },
  "grounding_metadata": {     # RAG источники (если есть)
    "grounding_supports": [...]
  },
  "usage_metadata": {...},   # Метаданные использования
  "actions": {               # Действия агента
    "state_delta": {...}     # Изменения состояния
  },
  "partial": false,          # Частичное сообщение?
  "turn_complete": true      # Завершён ли ход?
}
```

8. **Как найти первое сообщение пользователя:**

```javascript
// В events ищем первое событие где:
const userEvent = events.find(
  (event) =>
    event.content?.parts?.[0]?.text && // Есть текст
    (event.content.role === 'user' || // role = "user" ИЛИ
      event.author === 'user') // author = "user"
);

if (userEvent) {
  const userText = userEvent.content.parts[0].text.trim();
  const title = userText.length > 40 ? userText.substring(0, 40) + '...' : userText;
}
```

9. **Практическое решение для UI списка сессий:**

- Используйте `list_sessions()` для быстрого отображения карточек сессий
- Для получения **названия сессии** (первое сообщение пользователя) — вызывайте `get_session()` или `list_events()` асинхронно для каждой сессии
- Кэшируйте названия в `localStorage` для избежания повторных запросов
- В нашем проекте: функция `getTitleForSession()` в `frontend/script.js` делает именно это

10. **Альтернативы для названий сессий:**

- Если в проекте используется `state.message_history` (кастомная логика) — сначала проверяйте `session.state.message_history[0].user_input`
- Если нет — ищите в `session.events` первый Event с `author="user"` или `content.role="user"`
- Fallback: используйте timestamp сессии для генерации названия типа "Диалог от 12.01.2024"

11. **Как проверить поддержку VertexAiSessionService в вашей версии ADK?**

```python
from google.adk.apps import get_fast_api_app
from google.adk.sessions import VertexAiSessionService
import inspect

# Проверить поддержку session_service параметра
sig = inspect.signature(get_fast_api_app)
supports_session_service = 'session_service' in sig.parameters

print(f"get_fast_api_app поддерживает session_service: {supports_session_service}")

if supports_session_service:
    print("Можно использовать VertexAiSessionService программно")
else:
    print("Используйте session_service_uri с SQL БД")
```

12. **Зависимости для различных компонентов:**

```bash
# Базовая установка ADK
pip install google-adk

# Для Vertex AI Session Service
pip install google-adk[vertexai]

# Для SQL БД (PostgreSQL)
pip install google-adk[postgresql]  # или psycopg2-binary

# Для SQL БД (MySQL)
pip install google-adk[mysql]  # или PyMySQL

# Для Firebase Admin (бэкенд аутентификация)
pip install firebase-admin

# Для полной интеграции
pip install google-adk[vertexai] firebase-admin psycopg2-binary
```

13. **Диагностика и отладка:**

```python
# Проверка подключения к Vertex AI
from google.adk.sessions import VertexAiSessionService

try:
    service = VertexAiSessionService(
        project="your-project",
        location="us-central1"
    )
    print("✅ VertexAiSessionService инициализирован")
except Exception as e:
    print(f"❌ Ошибка VertexAI: {e}")

# Проверка SQL БД подключения
from google.adk.sessions import DatabaseSessionService

try:
    db_service = DatabaseSessionService("sqlite:///./test.db")
    print("✅ DatabaseSessionService инициализирован")
except Exception as e:
    print(f"❌ Ошибка БД: {e}")

# Проверка переменных окружения
import os
required_vars = [
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
    "GOOGLE_GENAI_USE_VERTEXAI"
]
for var in required_vars:
    value = os.getenv(var)
    print(f"{var}: {'✅' if value else '❌'} {value}")
```

14. **Типичные ошибки и решения:**

| Ошибка                                                        | Причина                                    | Решение                                               |
| ------------------------------------------------------------- | ------------------------------------------ | ----------------------------------------------------- |
| `Invalid database URL format 'vertexai://'`                   | ADK не поддерживает URI для Vertex         | Используйте программную инициализацию                 |
| `get_fast_api_app() got unexpected keyword 'session_service'` | Версия ADK не поддерживает прямую передачу | Fallback на `session_service_uri`                     |
| `403 Forbidden` при вызове Vertex API                         | Недостаточно прав у service account        | Добавьте роли `Vertex AI User`, `Vertex AI Developer` |
| `Firebase token verification failed`                          | Неправильный токен/проект                  | Проверьте `FIREBASE_PROJECT_ID` и токен               |
| Events не сохраняются в сессии                                | Используете `InMemorySessionService`       | Переключитесь на персистентный сервис                 |

---

## Итог

- Базовая архитектура: пользователь (uid) → множество сессий (sessionId) → события (история сообщений).
- Текущий проект хранит сессии в SQLite; фронт уже поддерживает мультисессионность и восстановление RAG-источников.
- Для прод: переключитесь на Postgres/MySQL (простой и надёжный путь) или используйте Vertex Ai Session Service при поддерживаемой версии ADK.
- Для реальных пользователей — включайте Firebase Auth, пробрасывайте `idToken` и используйте `uid` вместо тестового `u_999`.

---

## Примечания и физическая схема БД (практика)

В ADK объект `Session` уже содержит поле `events` (список), а `state` — словарь. В `DatabaseSessionService` данные в БД обычно хранятся агрегированно (таблицы сессий и событий) или в JSON-колонках.

Для простоты и скорости можно хранить `state` целиком JSON в `SESSION.state`. Если требуется аналитика/поиск по ключам, вынесите отдельные ключи состояния в таблицу `STATE_KV`.

Что кладём в БД практически:

- Таблица `sessions`: `id (session_id)`, `app_name`, `user_id`, `state (JSON)`, `created_at`, `last_update_time`, `active`
- Таблица `events`: `id (event_id)`, `session_id`, `author/role`, `timestamp`, `content (JSON)` или `parts (JSON)`, `grounding_metadata (JSON)`, `usage_metadata (JSON)`
- Дополнительно (опционально): отдельная таблица `event_parts` (если нужно эффективно фильтровать/стримить части), либо хранить `parts` массивом JSON прямо в `events.content/parts`
- Рекомендуемые индексы: `(user_id, app_name)`, `(session_id, timestamp)`

В ADK:

- `DatabaseSessionService` создаёт и ведёт эти структуры «под капотом»
- `VertexAiSessionService` — хранит аналогичную структуру как менеджед сущности в Vertex; таблиц не видно, но API `list/get/delete/listEvents` аналогичен

Идентификаторы и связи:

- `userId` — стабилен, приходит из вашей авторизации (Firebase/ваш auth)
- `sessionId` — генерируется на клиенте или сервере (UUID). У каждого диалога свой `sessionId`
- `eventId` — генерируется при добавлении сообщения

Итого:

- Пользователь → множество Сессий (диалогов)
- Сессия → упорядоченный список Событий (сообщений и действий)
- `state` хранит параметры диалога/пользователя:
  - без префикса — только для этой сессии
  - `user.` — пользовательские настройки (общие для всех сессий пользователя)
  - `app.` — глобальные настройки приложения

Эта модель уже используется в проекте: фронт вызывает `/apps/{appName}/users/{userId}/sessions/...`, а персистентность обеспечивает выбранный `SessionService` (сейчас SQLite, на проде — Postgres/Vertex).

---

## Карта файлов проекта и точки интеграции (где смотреть и что менять)

Ниже перечислены ключевые файлы приложения и как они связаны с темой сессий/персистентности:

- Корень репозитория
  - `run_agent.py` — точка входа FastAPI/ADK.
    - Создаёт приложение через `get_fast_api_app(...)`.
    - Читает `SESSION_SERVICE_URI` (Вариант A: SQLite/Postgres/MySQL).
    - Сюда же добавляем Firebase middleware: `init_firebase_admin()` и `app.add_middleware(FirebaseAuthMiddleware)`.
    - Если в вашей версии ADK появится возможность инъекции готового сервиса — здесь программно инициализируйте `VertexAiSessionService(project, location)` (Вариант B).

- Папка `app/`
  - `app/config.py` — общая конфигурация приложения (переменные окружения, логирование, флаги). Сессионный транспорт (SessionService) берётся из `run_agent.py`.
  - `app/agent.py` — сборка агентов/моделей/промптов; к конфигурации транспортного SessionService напрямую не привязан.
  - `app/health_checks.py` — health-чеки, без прямой связи с сессиями.
  - `app/observability.py` — наблюдаемость/трассировка; полезно для продовой среды, но транспорт SessionService не настраивает.
  - `app/exceptions.py`, `app/logging_config.py` — обработчики ошибок/логирование.
  - `app/services/session_service.py` — вспомогательный сервис для работы с `callback_context.state` внутри агентов (это **не** транспортный `SessionService` ADK для REST). Тут логика состояния на уровне диалога; персистентностью сессий занимается `DatabaseSessionService/VertexAiSessionService` на уровне ADK.

- Папка `frontend/`
  - `frontend/index.html` — подключение Firebase SDK и объявление `window.firebaseConfig`.
  - `frontend/apiClient.js` — инициализация Firebase Auth, получение `idToken` и `uid`, проброс `Authorization: Bearer` и подстановка `userId=uid` в запросы `createSession/listUserSessions/getSessionDetails`.
  - `frontend/script.js` — в `init()` первым вызовом `await initFirebaseAuth()`; после авторизации создаём/читаем сессии. UI бургер-истории и карточки сессий уже поддерживают мультисессионность и восстановление RAG-источников.
