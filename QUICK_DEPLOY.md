# ImmoAssist - Быстрый деплой в Cloud Run

## Экспресс-деплой

### 1. Сборка и загрузка Docker image

```bash
docker build -f Dockerfile.simple -t gcr.io/gothic-agility-464209-f4/immoassist:latest .
docker push gcr.io/gothic-agility-464209-f4/immoassist:latest
```

### 2. Деплой в Cloud Run с переменными

```bash
gcloud run deploy immoassist \
  --image gcr.io/gothic-agility-464209-f4/immoassist:latest \
  --platform managed \
  --region europe-central2 \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=gothic-agility-464209-f4,GOOGLE_CLOUD_LOCATION=europe-west1,MODEL_NAME=gemini-2.5-flash,SPECIALIST_MODEL=gemini-2.5-flash,CHAT_MODEL=gemini-2.5-flash,RAG_CORPUS=projects/gothic-agility-464209-f4/locations/europe-west3/ragCorpora/2305843009213693952,PRESENTATION_RAG_CORPUS=projects/gothic-agility-464209-f4/locations/europe-west3/ragCorpora/3379951520341557248,LEGAL_RAG_CORPUS=projects/gothic-agility-464209-f4/locations/europe-west3/ragCorpora/6917529027641081856,ELEVENLABS_API_KEY=sk_4b3175a717b5a47c53d65abdfd3cf64ce1f7b27d56d15094,ENABLE_VOICE_SYNTHESIS=true"
```

## Результат

**URL:** https://immoassist-29448644777.europe-central2.run.app/chat/

## Критически важные моменты

1. **РЕГИОН для моделей:** `GOOGLE_CLOUD_LOCATION=europe-west1` (НЕ west3!)
2. **Dockerfile:** Использовать `Dockerfile.simple` (НЕ обычный Dockerfile с Poetry)
3. **Requirements:** БЕЗ ограничений версий - только названия пакетов
4. **PORT:** НЕ добавлять в env vars (зарезервировано Cloud Run)
5. **Agents:** Папка исключена в `.dockerignore`

## 🔄 Проверка работы

```bash
curl -I https://immoassist-29448644777.europe-central2.run.app/chat/
# Ожидаем: HTTP/1.1 200 OK
```
