# ImmoAssist - Быстрый деплой в Cloud Run
# Проверенный рабочий скрипт после 5-часового дебага 🎉

Write-Host "🚀 Начинаем деплой ImmoAssist..." -ForegroundColor Green

# 1. Сборка Docker image
Write-Host "📦 Собираем Docker image..." -ForegroundColor Yellow
docker build -f Dockerfile.simple -t gcr.io/gothic-agility-464209-f4/immoassist:latest .

if ($LASTEXITCODE -ne 0) {
  Write-Host "❌ Ошибка сборки Docker image" -ForegroundColor Red
  exit 1
}

# 2. Загрузка в Container Registry
Write-Host "⬆️ Загружаем в Google Container Registry..." -ForegroundColor Yellow
docker push gcr.io/gothic-agility-464209-f4/immoassist:latest

if ($LASTEXITCODE -ne 0) {
  Write-Host "❌ Ошибка загрузки image" -ForegroundColor Red
  exit 1
}

# 3. Деплой в Cloud Run с правильными переменными
Write-Host "🌐 Деплоим в Cloud Run..." -ForegroundColor Yellow
gcloud run deploy immoassist `
  --image gcr.io/gothic-agility-464209-f4/immoassist:latest `
  --platform managed `
  --region europe-central2 `
  --allow-unauthenticated `
  --port 8000 `
  --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=gothic-agility-464209-f4,GOOGLE_CLOUD_LOCATION=europe-west1,MODEL_NAME=gemini-2.5-flash,SPECIALIST_MODEL=gemini-2.5-flash,CHAT_MODEL=gemini-2.5-flash,RAG_CORPUS=projects/gothic-agility-464209-f4/locations/europe-west3/ragCorpora/2305843009213693952,PRESENTATION_RAG_CORPUS=projects/gothic-agility-464209-f4/locations/europe-west3/ragCorpora/3379951520341557248,LEGAL_RAG_CORPUS=projects/gothic-agility-464209-f4/locations/europe-west3/ragCorpora/6917529027641081856,ELEVENLABS_API_KEY=sk_4b3175a717b5a47c53d65abdfd3cf64ce1f7b27d56d15094,ENABLE_VOICE_SYNTHESIS=true"

if ($LASTEXITCODE -eq 0) {
  Write-Host "✅ Деплой успешно завершен!" -ForegroundColor Green
  Write-Host "🌐 Сервис доступен: https://immoassist-29448644777.europe-central2.run.app/chat/" -ForegroundColor Cyan
    
  # Проверяем работу
  Write-Host "🔍 Проверяем работу сервиса..." -ForegroundColor Yellow
  try {
    $response = Invoke-WebRequest -Uri "https://immoassist-29448644777.europe-central2.run.app/chat/" -Method GET -UseBasicParsing
    if ($response.StatusCode -eq 200) {
      Write-Host "✅ Сервис работает корректно!" -ForegroundColor Green
    }
  }
  catch {
    Write-Host "⚠️ Проверьте сервис вручную" -ForegroundColor Yellow
  }
}
else {
  Write-Host "❌ Ошибка деплоя" -ForegroundColor Red
  exit 1
}

Write-Host "`n🎉 Готово! Можно тестировать агентов и фронтенд." -ForegroundColor Green 