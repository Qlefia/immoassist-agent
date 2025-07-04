# ImmoAssist Enterprise Integration Patterns

## Обзор

ImmoAssist построен как enterprise система с четкими границами интеграции для легкой интеграции с существующими системами.

## Структура Проекта

```
app/
├── __init__.py              # Экспорт root_agent для ADK Web
├── agent.py                 # Многоагентная архитектура
├── config.py                # Enterprise конфигурация
├── models/                  # Domain models
├── tools/                   # Инструменты агентов
├── services/               # Бизнес-логика
└── utils/                  # Утилиты
```

## 1. Интеграция с Сайтом

### ADK Web Interface

```bash
http://localhost:8000/dev-ui/?app=app
```

### API Integration

```python
from app import root_agent
from app.services import SessionService

class ImmoAssistAPI:
    def __init__(self):
        self.session_service = SessionService()
        self.agent = root_agent

    async def chat(self, user_id: str, message: str):
        session = self.session_service.get_or_create_session(user_id)
        response = await self.agent.send_message(message, session.session_id)
        return {"response": response.content}
```

## 2. Внешние API

### HeyGen Integration

```python
class HeyGenIntegration:
    async def create_avatar_video(self, message: str):
        # HeyGen API integration
        pass
```

### Property Database Integration

```python
class PropertyService:
    def __init__(self):
        self.apis = {
            "immowelt": ImmoweltAPI(),
            "immoscout": ImmoscoutAPI()
        }
```

## 3. Configuration

```bash
# .env
ENVIRONMENT=production
DATABASE_URL=postgresql://...
HEYGEN_API_KEY=your_key
WEBSITE_API_BASE_URL=https://yoursite.com/api
```

## 4. Deployment

Система готова к production через Docker/Kubernetes с proper monitoring и security.
