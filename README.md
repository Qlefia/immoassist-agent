# ImmoAssist AI Agent

KI-gestützter Immobilienberater für Investitionen in deutsche Neubauimmobilien, entwickelt mit Google Agent Development Kit (ADK).

## 🏠 Über ImmoAssist

ImmoAssist ist ein spezialisierter AI-Agent, der Kunden bei Investitionen in deutsche Neubauimmobilien berät. Der Agent bietet:

- **24/7 Beratung** zu Immobilieninvestments
- **Automatische Berechnungen** von Rentabilität und Finanzierung
- **Personalisierte Empfehlungen** basierend auf Kundenprofil
- **Integrierte Wissensdatenbank** mit FAQ und Handbuch
- **Multimodale Kommunikation** (Text, Sprache, Avatar)

## 🚀 Features

### Kernfunktionen

- ✅ Immobiliensuche und -bewertung
- ✅ Investitionsrentabilität-Berechnungen
- ✅ Steuerliche Optimierung (5% Sonder-AfA)
- ✅ Benutzerprofil und Präferenzen-Management
- ✅ Langzeit- und Kurzzeitgedächtnis
- ✅ FAQ und Handbuch-Integration

### Integrationen

- 🔄 **HeyGen**: Avatar-basierte Kommunikation
- 🔊 **ElevenLabs**: Text-zu-Sprache Synthese
- 📅 **Terminbuchung**: Automatische Beratungstermine
- 📧 **Email-Benachrichtigungen**: Berichte und Erinnerungen
- 🏢 **3D-Visualisierung**: Immobilien-Tours

### Technische Features

- 🧠 **Google Gemini 2.5 Pro** als LLM
- 🛠️ **Google ADK Framework**
- 📊 **Vertex AI** für Deployment
- 🔍 **Google Search** Integration
- 💾 **PostgreSQL** für Benutzerdaten
- 🔐 **Google Cloud** Sicherheit

## 📋 Voraussetzungen

- Python 3.11+
- Poetry (für Dependency Management)
- Google Cloud Projekt mit aktivierten APIs
- Optional: PostgreSQL für Produktionsdaten

## 🛠️ Installation

### 1. Repository klonen

\`\`\`bash
git clone https://github.com/your-org/immoassist-agent.git
cd immoassist-agent
\`\`\`

### 2. Dependencies installieren

\`\`\`bash

# Poetry installieren falls nicht vorhanden

pip install poetry

# Virtual Environment erstellen und Dependencies installieren

poetry install
\`\`\`

### 3. Umgebung konfigurieren

\`\`\`bash

# .env Datei erstellen

cp .env.example .env

# Konfiguration anpassen

nano .env
\`\`\`

### 4. Google Cloud Setup

\`\`\`bash

# Google Cloud CLI authentifizieren

gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID

# Erforderliche APIs aktivieren

gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
\`\`\`

## 🏃‍♂️ Agent starten

### Lokaler Start mit CLI

\`\`\`bash

# Virtual Environment aktivieren

poetry shell

# Agent im CLI-Modus starten

adk run immoassist_agent
\`\`\`

### Web Interface

\`\`\`bash

# Web-Interface starten

adk web
\`\`\`

Dann öffnen Sie http://localhost:8080 und wählen Sie "immoassist_agent" aus dem Dropdown.

## 💬 Beispiel-Interaktionen

### Immobiliensuche

\`\`\`
Benutzer: "Ich suche eine 2-Zimmer-Wohnung in München für maximal 300.000 Euro"

Agent: "Gerne helfe ich Ihnen bei der Suche! Ich habe eine passende 2-Zimmer-Wohnung in München-Schwabing gefunden:

🏠 **Moderne 2-Zimmer-Wohnung in München**
📍 Leopoldstraße 125, 80809 München
💰 285.000 € (unter Prospektpreis!)
📐 65 qm, Energieklasse A+
🏗️ Fertigstellung 2024
✅ 12 Monate Erstvermietungsgarantie
✅ 5 Jahre Bauträger-Gewährleistung

Monatliche Kosten nach Steuervorteilen: nur 180 €
Soll ich eine detaillierte Rentabilitätsberechnung erstellen?"
\`\`\`

### Investitionsberechnung

\`\`\`
Benutzer: "Ja, bitte berechne die Rentabilität für diese Wohnung"

Agent: [Verwendet calculate_investment_return Tool]

"📊 **Detaillierte Investitionsanalyse**

**Einmalige Kosten:**

- Kaufpreis: 285.000 €
- Eigenkapital (min.): 15.000 €
- Nebenkosten: 28.500 €

**Monatliche Bilanz:**

- Mieteinnahmen: 1.200 €
- Darlehensrate: -950 €
- Nebenkosten: -200 €
- **Steuerersparnis (5% Sonder-AfA): +498 €**
- **Monatliches Plus: +548 €**

**Langfristige Prognose:**
✅ Eigenkapital-Rückholung in 4 Jahren
✅ 10-Jahres-Gewinn: ca. 130.000 €
✅ Jährliche Rendite: 15,8%"
\`\`\`

## 🏗️ Architektur

\`\`\`
ImmoAssist Agent
├── Main Agent (LlmAgent)
│ ├── Gemini 2.5 Pro Model
│ └── System Prompt (German)
├── Tools
│ ├── Property Tools
│ │ ├── search_properties()
│ │ ├── get_property_details()
│ │ └── calculate_investment_return()
│ ├── User Tools
│ │ ├── get_user_profile()
│ │ ├── save_user_calculation()
│ │ └── get_user_history()
│ ├── Knowledge Tools
│ │ ├── search_faq()
│ │ └── search_handbook()
│ └── Integration Tools
│ ├── send_heygen_avatar_message()
│ ├── generate_elevenlabs_audio()
│ └── create_appointment_link()
└── External Services
├── Google Cloud (Vertex AI, Storage)
├── HeyGen API (Avatar)
├── ElevenLabs API (TTS)
└── PostgreSQL (User Data)
\`\`\`

## 📊 Deployment

### Google Agent Engine

\`\`\`bash

# Wheel-Datei erstellen

poetry build --format=wheel --output=deployment

# Zu Agent Engine deployen

cd deployment
python deploy.py
\`\`\`

### Cloud Run

\`\`\`bash

# Docker Image erstellen

docker build -t gcr.io/YOUR_PROJECT/immoassist-agent .

# Zu Cloud Run deployen

gcloud run deploy immoassist-agent \\
--image gcr.io/YOUR_PROJECT/immoassist-agent \\
--platform managed \\
--region us-central1
\`\`\`

## 🧪 Testing

\`\`\`bash

# Unit Tests

pytest tests/unit

# Integration Tests

pytest tests/integration

# Evaluation Tests

pytest eval
\`\`\`

## 📝 Nächste Schritte

### Sofort verfügbar:

- [x] Grundlegende Chat-Funktionalität
- [x] Immobiliensuche und -berechnungen
- [x] FAQ und Wissensdatenbank
- [x] Benutzerprofil-Management

### In Entwicklung:

- [ ] Echte Datenbank-Integration
- [ ] HeyGen Avatar-Integration
- [ ] ElevenLabs Sprachsynthese
- [ ] 3D-Immobilien-Visualisierung
- [ ] Automatisches FAQ-Update vom Website

### Geplant:

- [ ] Multi-Agent Workflow (Finanzierung, Rechtliches)
- [ ] Vektordatenbank für semantische Suche
- [ ] Real-time Property Data Feed
- [ ] Mobile App Integration
- [ ] CRM-System Integration

## 🤝 Beitragen

1. Fork das Repository
2. Feature Branch erstellen (\`git checkout -b feature/AmazingFeature\`)
3. Commit Changes (\`git commit -m 'Add some AmazingFeature'\`)
4. Branch pushen (\`git push origin feature/AmazingFeature\`)
5. Pull Request öffnen

## 📄 Lizenz

Dieses Projekt ist unter der Apache 2.0 Lizenz lizenziert - siehe [LICENSE](LICENSE) für Details.

## 📞 Support

Bei Fragen oder Problemen:

- 📧 Email: support@immoassist.de
- 💬 Issues: [GitHub Issues](https://github.com/your-org/immoassist-agent/issues)
- 📚 Dokumentation: [Wiki](https://github.com/your-org/immoassist-agent/wiki)

---

**ImmoAssist** - Ihr intelligenter Partner für Immobilieninvestments 🏠✨
