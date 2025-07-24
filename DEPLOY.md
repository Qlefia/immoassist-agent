# Деплой ImmoAssist на Google Cloud Run

## Автоматический деплой

### Windows (PowerShell)

```powershell
.\deploy.ps1
```

### Linux/macOS (Bash)

```bash
./deploy.sh
```

## Ручной деплой

### 1. Сборка Docker образа

```bash
docker build -t gcr.io/gothic-agility-464209-f4/immoassist:latest .
```

### 2. Отправка образа в Google Container Registry

```bash
docker push gcr.io/gothic-agility-464209-f4/immoassist:latest
```

### 3. Деплой на Cloud Run

```bash
gcloud run deploy immoassist \
    --image gcr.io/gothic-agility-464209-f4/immoassist:latest \
    --platform managed \
    --region europe-central2 \
    --allow-unauthenticated \
    --port 8000 \
    --memory 2Gi \
    --cpu 1 \
    --max-instances 10 \
    --project gothic-agility-464209-f4
```

## После деплоя

После успешного деплоя ваше приложение будет доступно по следующим адресам:

- **Чат интерфейс (основной)**: `https://your-service-url/chat/`
- **ADK интерфейс**: `https://your-service-url/`
- **TTS API**: `https://your-service-url/tts`

### Важные моменты

1. **Чат доступен по `/chat/`** - это основной интерфейс для пользователей
2. **Автоматический редирект** - переход с корневого URL на чат
3. **TTS функционал** - работает с ElevenLabs API
4. **Все статические файлы** фронтенда включены в контейнер

## Требования

- Docker Desktop
- Google Cloud SDK (gcloud CLI)
- Аутентификация в Google Cloud
- Права на проект `gothic-agility-464209-f4`

## Переменные окружения

Убедитесь что в Cloud Run настроены следующие переменные:

- `GOOGLE_CLOUD_PROJECT=gothic-agility-464209-f4`
- `GOOGLE_CLOUD_LOCATION=europe-west3`
- `ELEVENLABS_API_KEY=your-key`
- `GOOGLE_APPLICATION_CREDENTIALS=/usr/src/app/app/gothic-agility-464209-f4-39095fb8e054copy.json`

## Диагностика

Если что-то не работает:

1. Проверьте логи Cloud Run
2. Убедитесь что все файлы скопированы в контейнер
3. Проверьте переменные окружения
4. Убедитесь что порт 8000 открыт

## Структура URL

```
https://your-service-url/
├── /                    → редирект на /chat/
├── /chat/              → чат интерфейс (HTML)
├── /chat/style.css     → стили чата
├── /chat/script.js     → логика чата
├── /tts                → TTS API
├── /run_sse            → SSE API для чата
└── /apps/app/...       → ADK API endpoints
```
