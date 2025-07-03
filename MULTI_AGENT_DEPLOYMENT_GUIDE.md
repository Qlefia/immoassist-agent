# ImmoAssist Multi-Agent System - Deployment Guide

Comprehensive deployment and operations guide for the production-ready ImmoAssist multi-agent architecture based on Google ADK and Vertex AI.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Agent Deployment](#agent-deployment)
5. [System Testing](#system-testing)
6. [A2A Integration](#a2a-integration)
7. [Production Deployment](#production-deployment)
8. [Monitoring and Analytics](#monitoring-and-analytics)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

---

## Architecture Overview

### ImmoAssist Multi-Agent System

```
Root Agent (Philipp)
├── Knowledge Agent (FAQ + Handbooks)
├── Property Agent (Real Estate Search)
├── Calculator Agent (Financial Calculations)
└── Analytics Agent (Market Analytics)
```

### Key Components

- **Root Agent**: Coordinator and main consultant Philipp
- **Sub-Agents**: Specialized agents via AgentTool pattern
- **Session Management**: VertexAiSessionService for state management
- **RAG Integration**: Vertex AI RAG for knowledge retrieval
- **A2A Support**: Inter-agent communication protocol

---

## Prerequisites

### Google Cloud Setup

```bash
# 1. Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
source ~/.bashrc

# 2. Authentication
gcloud auth login
gcloud auth application-default login

# 3. Project configuration
gcloud config set project YOUR_PROJECT_ID

# 4. Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudstorage.googleapis.com
gcloud services enable firestore.googleapis.com
```

### Python Environment

```bash
# Python 3.11+ required
python --version  # >= 3.11

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install google-adk>=1.5.0
pip install google-cloud-aiplatform[adk]>=1.93.0
pip install python-dotenv>=1.0.1
```

---

## Environment Setup

### 1. Environment Variables Configuration

```bash
# Copy template
cp environment.config.template .env

# Edit configuration
nano .env
```

**Required Settings:**

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=europe-west1
GOOGLE_GENAI_USE_VERTEXAI=True

# Models
MODEL_NAME=gemini-2.5-pro
EMBEDDING_MODEL=text-embedding-005

# ADK Configuration
ADK_PORT=8000
ADK_HOST=localhost
```

### 2. Vertex AI RAG Setup (Optional)

```bash
# Create RAG corpus
gcloud alpha vertex-ai rag-corpora create \
  --location=europe-west1 \
  --display-name="ImmoAssist Knowledge Base" \
  --description="FAQ and handbooks for ImmoAssist"

# Get corpus ID
gcloud alpha vertex-ai rag-corpora list --location=europe-west1

# Add to .env
RAG_CORPUS=projects/YOUR_PROJECT/locations/europe-west1/ragCorpora/CORPUS_ID
```

### 3. Knowledge Base Preparation

```bash
# Knowledge structure is ready
ls -la data/FAQ/
ls -la data/Handbücher/

# Vector database backup available
ls -la vector_store/metadata.json
```

---

## Agent Deployment

### 1. Multi-Agent System Startup

```bash
# Navigate to project directory
cd immoassist

# Verify configuration
python -c "from immoassist_agent.multi_agent_architecture import root_agent; print('Multi-Agent system loaded successfully')"

# Start ADK Web UI
adk web --port 8000
```

### 2. Agent Verification

Open browser: `http://localhost:8000/dev-ui/?app=immoassist_agent`

**Expected Console Output:**

```
INFO - ImmoAssist Multi-Agent System initialized successfully
INFO - Root Agent: Philipp_ImmoAssist_Coordinator (Main Coordinator)
INFO - Knowledge Agent: knowledge_specialist (FAQ & Handbooks)
INFO - Property Agent: property_specialist (Search & Analysis)
INFO - Calculator Agent: calculator_specialist (Financial Calculations)
INFO - Analytics Agent: analytics_specialist (Market Analysis)
```

### 3. Test Queries

```bash
# Knowledge test
"What is Erbbaurecht?"

# Calculation test
"Calculate the yield for a 350,000 EUR apartment in Munich"

# Property search test
"Find new construction properties in Berlin under 400,000 EUR"

# Analytics test
"How are real estate prices developing in Hamburg?"
```

---

## System Testing

### 1. Agent Functionality Tests

**Knowledge Agent:**

- FAQ query handling
- Handbook information retrieval
- Multi-language responses

**Property Agent:**

- Property search execution
- Market analysis integration
- Location assessment

**Calculator Agent:**

- ROI calculations
- Cash flow projections
- Tax optimization scenarios

**Analytics Agent:**

- Market trend analysis
- Risk assessment
- Investment recommendations

### 2. Integration Tests

```bash
# Multi-agent coordination
"Compare properties in Leipzig and Dresden with full financial analysis"

# Cross-domain queries
"Find a property in Munich, calculate ROI, and analyze market trends"

# Multi-language testing
"ты работаешь?" → Russian response
"Was ist Tilgung?" → German response with knowledge specialist
```

### 3. Performance Testing

```bash
# Load testing
ab -n 100 -c 10 http://localhost:8000/

# Memory usage monitoring
ps aux | grep python

# Response time analysis
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/
```

---

## A2A Integration

### 1. Agent Card Generation

```bash
# Generate A2A Agent Card
python immoassist_agent/a2a_agent_card.py

# Verify agent card
cat .well-known/agent.json
```

### 2. Agent Discovery Endpoint

Agent Card available at:

```
http://localhost:8000/.well-known/agent.json
```

### 3. A2A Communication (Future)

```python
# Example usage
from immoassist_agent.a2a_agent_card import ImmoAssistAgentCard

# Create agent card
card = ImmoAssistAgentCard.create_card()
print(card.to_json())

# Discovery endpoint
discovery = ImmoAssistAgentCard.create_agent_discovery_endpoint()
```

---

## Production Deployment

### 1. Google Cloud Run Deployment

```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Deploy to Cloud Run
gcloud run deploy immoassist-multi-agent \
  --source . \
  --port=8080 \
  --allow-unauthenticated \
  --region=europe-west1 \
  --memory=2Gi \
  --cpu=2 \
  --min-instances=1 \
  --max-instances=10 \
  --timeout=3600
```

### 2. Production Environment Configuration

```bash
# Production .env
GOOGLE_CLOUD_PROJECT=your-production-project
GOOGLE_GENAI_USE_VERTEXAI=True
MODEL_NAME=gemini-2.5-pro
ADK_PORT=8080
ADK_HOST=0.0.0.0
DEVELOPMENT_MODE=false
LOG_LEVEL=INFO
```

### 3. Security Configuration

```bash
# IAM roles
gcloud projects add-iam-policy-binding YOUR_PROJECT \
  --member="serviceAccount:immoassist-sa@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding YOUR_PROJECT \
  --member="serviceAccount:immoassist-sa@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# VPC configuration for enhanced security
gcloud compute networks create immoassist-vpc --subnet-mode=custom
```

### 4. Load Balancing and CDN

```bash
# Create load balancer
gcloud compute url-maps create immoassist-lb \
  --default-service=immoassist-backend-service

# Configure SSL
gcloud compute ssl-certificates create immoassist-ssl \
  --domains=api.immoassist.de
```

---

## Monitoring and Analytics

### 1. Logging Configuration

```python
# Production logging setup
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/immoassist/agent.log')
    ]
)
```

### 2. Session Metrics

The system automatically tracks:

- Session duration and user engagement
- Question volume and agent utilization
- Topic distribution and conversation flow
- Performance metrics and error rates

### 3. Cloud Monitoring Integration

```bash
# View logs in Cloud Logging
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=immoassist-multi-agent"

# Set up alerting
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring-policy.yaml
```

### 4. Performance Metrics

```python
# Session state metrics
{
  "analytics": {
    "session_duration_seconds": 1200,
    "total_questions_asked": 15,
    "agents_consulted": ["knowledge_specialist", "calculator_specialist"],
    "topics_discussed": ["property_search", "financial_analysis"],
    "user_satisfaction_indicators": ["positive_feedback", "continued_engagement"]
  }
}
```

---

## Troubleshooting

### Common Issues

#### 1. RAG Not Working

```bash
# Check corpus configuration
gcloud alpha vertex-ai rag-corpora describe CORPUS_ID --location=europe-west1

# Verify fallback search
python -c "from immoassist_agent.true_rag_agent import search_knowledge_base; print('Fallback OK')"
```

#### 2. Agent Initialization Failures

```bash
# Check imports
python -c "from immoassist_agent import root_agent; print('Import OK')"

# Verify environment
python -c "import os; print('Project:', os.getenv('GOOGLE_CLOUD_PROJECT'))"

# Check authentication
gcloud auth application-default print-access-token
```

#### 3. Session Management Issues

```bash
# Clear session cache
rm -rf ~/.adk/sessions/

# Restart ADK with clean state
adk web --port 8000 --reset
```

#### 4. Memory and Performance Issues

```bash
# Monitor resource usage
top -p $(pgrep -f "adk web")

# Check memory leaks
python -m memory_profiler agent_script.py

# Optimize garbage collection
export PYTHONOPTIMIZE=1
```

---

## Maintenance

### Regular Maintenance Tasks

#### 1. Dependency Updates

```bash
# Update ADK and dependencies
pip install --upgrade google-adk google-cloud-aiplatform

# Check for security updates
pip audit

# Update lockfile
poetry update
```

#### 2. Model Performance Monitoring

```bash
# Monitor model performance
gcloud ai models list --region=europe-west1

# Check token usage
gcloud billing budgets list

# Performance benchmarks
python scripts/benchmark_agents.py
```

#### 3. Knowledge Base Updates

```bash
# Update FAQ content
git pull origin main

# Refresh vector embeddings
python scripts/update_embeddings.py

# Validate knowledge consistency
pytest tests/knowledge_validation.py
```

#### 4. Security Audits

```bash
# Audit dependencies
safety check

# Security scan
bandit -r immoassist_agent/

# Access review
gcloud projects get-iam-policy YOUR_PROJECT
```

### Backup and Recovery

#### 1. Configuration Backup

```bash
# Backup configuration
cp .env .env.backup.$(date +%Y%m%d)
tar -czf config-backup-$(date +%Y%m%d).tar.gz .env pyproject.toml
```

#### 2. Session Data Backup

```bash
# Export session data
python scripts/export_sessions.py --output=sessions-backup.json

# Backup vector store
tar -czf vector-store-backup-$(date +%Y%m%d).tar.gz vector_store/
```

#### 3. Disaster Recovery

```bash
# Restore from backup
tar -xzf config-backup-20250103.tar.gz
cp .env.backup.20250103 .env

# Rebuild system
python scripts/rebuild_system.py --config=.env
```

---

## Production Checklist

### Pre-Deployment

- [ ] All environment variables configured
- [ ] Google Cloud authentication working
- [ ] All agents initialize successfully
- [ ] Knowledge base accessible
- [ ] Session management functional
- [ ] Security settings configured

### Post-Deployment

- [ ] Health checks passing
- [ ] Monitoring and alerting active
- [ ] Load balancing configured
- [ ] SSL certificates valid
- [ ] Backup procedures tested
- [ ] Documentation updated

### Ongoing Operations

- [ ] Regular dependency updates
- [ ] Performance monitoring
- [ ] Security audit schedule
- [ ] Knowledge base maintenance
- [ ] User feedback integration
- [ ] Capacity planning review

---

## Support and Resources

### Documentation Links

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [A2A Protocol Specification](https://github.com/a2aproject/a2a-samples)

### Support Channels

- **GitHub Issues**: Technical issues and feature requests
- **Google Cloud Support**: Infrastructure and platform issues
- **Community Forum**: General questions and discussions

### Emergency Contacts

- **Production Issues**: ops@immoassist.de
- **Security Incidents**: security@immoassist.de
- **Business Critical**: emergency@immoassist.de

---

**Production Ready!** Your ImmoAssist multi-agent system is ready for enterprise deployment with full Vertex AI integration, A2A protocol support, and enterprise-grade architecture.

Built for Scale | Secured by Design | Ready for International Teams
