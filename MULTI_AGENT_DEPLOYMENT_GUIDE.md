# 🏗️ ImmoAssist Multi-Agent System - Deployment Guide

Комплексное руководство по развертыванию и использованию профессиональной multi-agent архитектуры ImmoAssist на базе Google ADK и Vertex AI.

## 📋 Содержание

1. [Архитектурный обзор](#архитектурный-обзор)
2. [Предварительные требования](#предварительные-требования)
3. [Настройка среды](#настройка-среды)
4. [Развертывание агентов](#развертывание-агентов)
5. [Тестирование системы](#тестирование-системы)
6. [A2A интеграция](#a2a-интеграция)
7. [Производственное развертывание](#производственное-развертывание)
8. [Мониторинг и аналитика](#мониторинг-и-аналитика)

---

## 🏛️ Архитектурный обзор

### Multi-Agent система ImmoAssist

```
🧠 Root Agent (Philipp)
├── 📚 Knowledge Agent (FAQ + Handbücher)
├── 🏠 Property Agent (Поиск недвижимости)
├── 💰 Calculator Agent (Финансовые расчеты)
└── 📊 Analytics Agent (Рыночная аналитика)
```

### Ключевые компоненты

- **Root Agent**: Координатор и главный консультант Philipp
- **Sub-Agents**: Специализированные агенты через AgentTool
- **Session Management**: VertexAiSessionService для состояния
- **RAG Integration**: Vertex AI RAG для знаний
- **A2A Support**: Межагентная коммуникация

---

## ⚙️ Предварительные требования

### Google Cloud Setup

```bash
# 1. Установка Google Cloud CLI
curl https://sdk.cloud.google.com | bash
source ~/.bashrc

# 2. Аутентификация
gcloud auth login
gcloud auth application-default login

# 3. Настройка проекта
gcloud config set project YOUR_PROJECT_ID

# 4. Включение API
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudstorage.googleapis.com
gcloud services enable firestore.googleapis.com
```

### Python Environment

```bash
# Python 3.11+ требуется
python --version  # >= 3.11

# Виртуальная среда
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Зависимости
pip install google-adk
pip install google-cloud-aiplatform
pip install google-cloud-storage
pip install python-dotenv
```

---

## 🔧 Настройка среды

### 1. Конфигурация Environment Variables

```bash
# Скопируйте шаблон
cp environment.config.template .env

# Отредактируйте .env файл
nano .env
```

**Обязательные настройки:**

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True

# Модели
MODEL_NAME=gemini-2.5-pro
EMBEDDING_MODEL=text-embedding-005

# ADK
ADK_PORT=8001
ADK_HOST=localhost
```

### 2. Настройка Vertex AI RAG (Опционально)

```bash
# Создание RAG корпуса
gcloud alpha vertex-ai rag-corpora create \
  --location=us-central1 \
  --display-name="ImmoAssist Knowledge Base" \
  --description="FAQ and handbooks for ImmoAssist"

# Получение корпуса ID
gcloud alpha vertex-ai rag-corpora list --location=us-central1

# Добавление в .env
RAG_CORPUS=projects/YOUR_PROJECT/locations/us-central1/ragCorpora/CORPUS_ID
```

### 3. Подготовка знаний

```bash
# Структура знаний уже готова
ls -la "for embedings/FAQ/"
ls -la "for embedings/Handbücher/"

# Векторная база данных
ls -la vector_store_backup/metadata.json
```

---

## 🚀 Развертывание агентов

### 1. Запуск Multi-Agent системы

```bash
# Переход в директорию проекта
cd immoassist

# Проверка конфигурации
python -c "from immoassist_agent.multi_agent_architecture import root_agent; print('✅ Multi-Agent система загружена')"

# Запуск ADK Web UI
adk web
```

### 2. Проверка агентов

Откройте браузер: `http://localhost:8001/dev-ui/?app=immoassist_agent`

**Ожидаемый вывод в консоли:**

```
INFO - ImmoAssist Multi-Agent System initialized successfully
INFO - ✓ Root Agent: Philipp (Coordinator)
INFO - ✓ Knowledge Agent: FAQ & Handbooks
INFO - ✓ Property Agent: Search & Analysis
INFO - ✓ Calculator Agent: Financial Calculations
INFO - ✓ Analytics Agent: Market Analysis
```

### 3. Тестовые запросы

```bash
# Тест знаний
"Was ist das Erbbaurecht?"

# Тест расчетов
"Berechne die Rendite für eine 350.000€ Wohnung in München"

# Тест поиска
"Finde Neubau-Immobilien in Berlin unter 400.000€"

# Тест аналитики
"Wie entwickeln sich die Immobilienpreise in Hamburg?"
```

---

## 🔗 A2A интеграция

### 1. Генерация Agent Card

```bash
# Создание A2A Agent Card
python immoassist_agent/a2a_agent_card.py

# Проверка файла
cat .well-known/agent.json
```

### 2. Agent Discovery Endpoint

Agent Card будет доступен по адресу:

```
http://localhost:8001/.well-known/agent.json
```

### 3. A2A Communication (Будущее)

```python
# Пример использования
from immoassist_agent.a2a_agent_card import ImmoAssistAgentCard

# Создание карты агента
card = ImmoAssistAgentCard.create_card()
print(card.to_json())

# Discovery endpoint
discovery = ImmoAssistAgentCard.create_agent_discovery_endpoint()
```

---

## 🏭 Производственное развертывание

### 1. Cloud Run Deployment

```bash
# Создание Dockerfile
cat > Dockerfile << EOF
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Создание requirements.txt
pip freeze > requirements.txt

# Развертывание
gcloud run deploy immoassist-multi-agent \
  --source . \
  --port=8080 \
  --allow-unauthenticated \
  --region=us-central1 \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=10
```

### 2. Environment для Production

```bash
# Production .env
GOOGLE_CLOUD_PROJECT=your-production-project
GOOGLE_GENAI_USE_VERTEXAI=True
MODEL_NAME=gemini-2.5-pro
ADK_PORT=8080
ADK_HOST=0.0.0.0
DEVELOPMENT_MODE=false
LOG_LEVEL=WARNING
```

### 3. Security настройки

```bash
# IAM роли
gcloud projects add-iam-policy-binding YOUR_PROJECT \
  --member="serviceAccount:immoassist-sa@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding YOUR_PROJECT \
  --member="serviceAccount:immoassist-sa@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

---

## 📊 Мониторинг и аналитика

### 1. Логирование

```python
# Проверка логов
import logging
logging.basicConfig(level=logging.INFO)

# В Cloud Run
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=immoassist-multi-agent"
```

### 2. Session Tracking

Система автоматически отслеживает:

- Время сессии
- Количество вопросов
- Использованные агенты
- Темы обсуждения

### 3. Metrics для Production

```python
# Метрики в session state
{
  "analytics": {
    "session_duration": 0,
    "questions_asked": 0,
    "agents_consulted": [],
    "topics_discussed": []
  }
}
```

---

## 🔧 Troubleshooting

### Распространенные проблемы

1. **RAG не работает**

   ```bash
   # Проверка корпуса
   gcloud alpha vertex-ai rag-corpora describe CORPUS_ID --location=us-central1

   # Fallback на локальный поиск автоматически включится
   ```

2. **Агенты не отвечают**

   ```bash
   # Проверка импортов
   python -c "from immoassist_agent import root_agent; print('OK')"

   # Проверка environment
   python -c "import os; print(os.getenv('GOOGLE_CLOUD_PROJECT'))"
   ```

3. **Session проблемы**

   ```bash
   # Очистка session
   rm -rf ~/.adk/sessions/

   # Рестарт ADK
   adk web --reset
   ```

---

## 🎯 Следующие шаги

### Краткосрочные (1-2 недели)

- [ ] Тестирование всех агентов
- [ ] Настройка production среды
- [ ] Интеграция с реальной базой объектов

### Среднесрочные (1-2 месяца)

- [ ] A2A коммуникация с внешними агентами
- [ ] Расширенная аналитика
- [ ] Мобильное приложение

### Долгосрочные (3-6 месяцев)

- [ ] Multi-modal поддержка (голос, изображения)
- [ ] Автоматическое ML-обучение на пользовательских данных
- [ ] Enterprise интеграции (CRM, ERP)

---

## 🆘 Поддержка

### Контакты для помощи

- **GitHub Issues**: Создавайте issue в репозитории
- **Google Cloud Support**: Для вопросов по Vertex AI
- **ADK Documentation**: https://google.github.io/adk-docs/

### Полезные ссылки

- [ADK Quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit/quickstart)
- [A2A Protocol](https://github.com/a2aproject/a2a-samples)
- [Vertex AI RAG](https://cloud.google.com/vertex-ai/generative-ai/docs/retrieval-augmented-generation/overview)

---

**✅ Готово к продакшену!** Ваша multi-agent система ImmoAssist готова для профессионального использования с полной поддержкой Vertex AI, A2A протокола, и enterprise-grade архитектуры.
