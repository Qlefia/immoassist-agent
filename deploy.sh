#!/bin/bash

# Конфигурация для деплоя
PROJECT_ID="gothic-agility-464209-f4"
IMAGE_NAME="immoassist"
REGION="europe-central2"
SERVICE_NAME="immoassist"

# Проверяем переменные окружения
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Ошибка: PROJECT_ID не установлен"
    exit 1
fi

echo "🚀 Начинаем деплой ImmoAssist на Cloud Run..."
echo "   Проект: $PROJECT_ID"
echo "   Регион: $REGION"
echo "   Сервис: $SERVICE_NAME"
echo ""

# Шаг 1: Сборка Docker образа
echo "📦 Сборка Docker образа..."
docker build -f Dockerfile.simple -t gcr.io/$PROJECT_ID/$IMAGE_NAME:latest .

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при сборке Docker образа"
    exit 1
fi

echo "✅ Docker образ собран успешно"
echo ""

# Шаг 2: Пуш образа в Google Container Registry
echo "📤 Отправка образа в Google Container Registry..."
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:latest

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при отправке образа"
    exit 1
fi

echo "✅ Образ отправлен в GCR"
echo ""

# Шаг 3: Деплой на Cloud Run
echo "🚀 Деплой на Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$IMAGE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8000 \
    --memory 2Gi \
    --cpu 1 \
    --max-instances 10 \
    --project $PROJECT_ID

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при деплое на Cloud Run"
    exit 1
fi

echo ""
echo "🎉 Деплой завершен успешно!"
echo ""
echo "📱 Ваше приложение доступно по адресу:"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
echo "   Основной URL: $SERVICE_URL"
echo "   Чат интерфейс: $SERVICE_URL/chat/"
echo ""
echo "💡 Важно: Чат будет доступен по адресу $SERVICE_URL/chat/" 