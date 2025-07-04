"""Knowledge tools for ImmoAssist enterprise system."""

import json
import os
from typing import List, Optional
from google.adk.tools import FunctionTool
from ..config import config


@FunctionTool
def search_faq(query: str, category: Optional[str] = None) -> str:
    """Search ImmoAssist FAQ database."""
    
    # TODO: Implement real search with vector database
    # For now, return sample FAQ results
    
    sample_faqs = [
        {
            "question": "Was genau macht ImmoDev?",
            "answer": "ImmoDev ist eine Plattform für deutsche Immobilieninvestitionen mit Fokus auf Neubau-Objekte mit A+ Energiestandard im Preisbereich 250.000-500.000 EUR.",
            "category": "Allgemein"
        },
        {
            "question": "Welche Dienstleistungen bietet ImmoDev an?",
            "answer": "Wir bieten Immobiliensuche, Finanzierungsberatung, Renditeberechnung und Investmentanalyse für deutsche Neubau-Immobilien.",
            "category": "Erste Schritte"
        },
        {
            "question": "Was sind die Vorteile der 5% Sonder-AfA?",
            "answer": "Bei Neubau-Immobilien können Sie 4 Jahre lang 5% des Kaufpreises zusätzlich abschreiben, was zu erheblichen Steuervorteilen führt.",
            "category": "Steuervorteile"
        }
    ]
    
    # Filter by category if specified
    if category:
        filtered = [faq for faq in sample_faqs if faq["category"].lower() == category.lower()]
    else:
        filtered = sample_faqs
    
    # Simple text search
    if query:
        filtered = [
            faq for faq in filtered 
            if query.lower() in faq["question"].lower() or query.lower() in faq["answer"].lower()
        ]
    
    return json.dumps({"faqs": filtered}, ensure_ascii=False)


@FunctionTool
def search_handbook(topic: str) -> str:
    """Search ImmoAssist handbook for detailed information."""
    
    # TODO: Implement real handbook search
    sample_handbook = {
        "grunderwerbsteuer": {
            "title": "Was ist die Grunderwerbsteuer?",
            "content": "Die Grunderwerbsteuer ist eine einmalige Steuer beim Immobilienkauf. Sie beträgt je nach Bundesland 3,5% bis 6,5% des Kaufpreises.",
            "details": [
                "Bayern: 3,5%",
                "Sachsen: 3,5%", 
                "Berlin: 6,0%",
                "Nordrhein-Westfalen: 6,5%"
            ]
        },
        "energieeffizienz": {
            "title": "Energieeffizienzklassen bei Immobilien",
            "content": "Die Energieeffizienzklasse gibt an, wie energiesparend eine Immobilie ist. A+ ist die beste Klasse.",
            "details": [
                "A+: Sehr niedriger Energieverbrauch",
                "A: Niedriger Energieverbrauch",
                "B: Mittlerer Energieverbrauch"
            ]
        }
    }
    
    topic_lower = topic.lower()
    result = None
    
    for key, content in sample_handbook.items():
        if key in topic_lower or topic_lower in content["title"].lower():
            result = content
            break
    
    if result:
        return json.dumps(result, ensure_ascii=False)
    else:
        return json.dumps({"error": "Topic not found in handbook"}, ensure_ascii=False)


@FunctionTool
def get_process_guide(process_name: str) -> str:
    """Get step-by-step process guide."""
    
    processes = {
        "immobilienkauf": {
            "title": "Immobilienkauf-Prozess",
            "steps": [
                "1. Finanzierung klären und Bestätigung einholen",
                "2. Objektbesichtigung und Prüfung",
                "3. Kaufvertrag prüfen lassen",
                "4. Notartermin vereinbaren",
                "5. Kaufvertrag beim Notar unterschreiben",
                "6. Eigentumsumschreibung im Grundbuch",
                "7. Schlüsselübergabe"
            ],
            "duration": "4-8 Wochen",
            "important_notes": [
                "Immer Finanzierung vor Vertragsunterzeichnung sichern",
                "Bauträgervertrag durch Rechtsanwalt prüfen lassen",
                "Gewährleistungsfristen beachten"
            ]
        },
        "steuervorteile": {
            "title": "Steuervorteile bei Neubau-Immobilien",
            "steps": [
                "1. 5% Sonder-AfA für 4 Jahre beantragen",
                "2. 2% reguläre AfA für 50 Jahre",
                "3. Werbungskosten geltend machen",
                "4. Steuerliche Beratung in Anspruch nehmen"
            ],
            "benefits": [
                "Bis zu 42% Steuerersparnis auf Abschreibungen",
                "Schnelle Kapitalrückgewinnung",
                "Planbare Steuervorteile"
            ]
        }
    }
    
    if process_name.lower() in processes:
        return json.dumps(processes[process_name.lower()], ensure_ascii=False)
    else:
        return json.dumps({"error": "Process guide not found"}, ensure_ascii=False) 