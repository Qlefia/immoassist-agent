"""
Knowledge base management tools for ImmoAssist.

This module contains tools for searching FAQ and handbook databases,
retrieving knowledge categories, and adding new knowledge entries.
"""

from typing import List, Optional
from google.adk.tools import FunctionTool
import json

# Temporary knowledge base (will be replaced with vector database later)
FAQ_DATABASE = [
    {
        "id": "faq_001",
        "question": "Wie funktioniert der Immobilienkauf ohne Makler?",
        "answer": "Bei ImmoAssist arbeiten wir direkt mit Projektentwicklern zusammen. Dadurch entfallen die Maklergebühren (meist 3-7% des Kaufpreises), und wir können Ihnen die Immobilien unter dem öffentlichen Prospektpreis anbieten. Sie sparen so mehrere tausend Euro beim Kauf.",
        "category": "kaufprozess",
        "tags": ["makler", "kosten", "sparen"]
    },
    {
        "id": "faq_002", 
        "question": "Was ist die 5% Sonder-AfA und wie funktioniert sie?",
        "answer": "Die Sonder-AfA (Sonderabschreibung für Abnutzung) ermöglicht es bei Neubauimmobilien, 5% des Kaufpreises jährlich über 4 Jahre von der Steuer abzusetzen. Bei einer 300.000€ Immobilie sind das 15.000€ pro Jahr. Mit einem Steuersatz von 42% erhalten Sie 6.300€ jährlich zurück - insgesamt 25.200€ über 4 Jahre.",
        "category": "steuern",
        "tags": ["sonder-afa", "steuervorteile", "abschreibung"]
    },
    {
        "id": "faq_003",
        "question": "Wie sicher ist die Erstvermietungsgarantie?",
        "answer": "Die Erstvermietungsgarantie wird direkt vom Projektentwickler für 12 Monate gewährleistet. Das bedeutet, Sie erhalten die vereinbarte Miete unabhängig davon, ob die Wohnung vermietet ist oder nicht. Dies bietet Ihnen Planungssicherheit für das erste Jahr.",
        "category": "garantien",
        "tags": ["erstvermietung", "garantie", "sicherheit"]
    },
    {
        "id": "faq_004",
        "question": "Warum nur Energieeffizienzklasse A+?",
        "answer": "Energieeffizienzklasse A+ bedeutet minimale Nebenkosten für Ihre Mieter und damit eine höhere Attraktivität der Immobilie. Zudem gibt es staatliche Förderungen für energieeffiziente Neubauten. Die niedrigen Betriebskosten sichern langfristig stabile Mieteinnahmen.",
        "category": "energieeffizienz",
        "tags": ["energieeffizienz", "nebenkosten", "förderung"]
    },
    {
        "id": "faq_005",
        "question": "Wie viel Eigenkapital benötige ich mindestens?",
        "answer": "In der Regel benötigen Sie mindestens 5-10% des Kaufpreises als Eigenkapital plus Nebenkosten (ca. 10-12% des Kaufpreises). Bei einer 300.000€ Immobilie sind das etwa 45.000-66.000€. Durch unsere günstigen Konditionen oft weniger als bei herkömmlichen Käufen.",
        "category": "finanzierung",
        "tags": ["eigenkapital", "finanzierung", "nebenkosten"]
    }
]

HANDBOOK_DATABASE = [
    {
        "id": "handbook_001",
        "title": "Grundlagen der Immobilieninvestition",
        "content": "Immobilieninvestitionen gelten als eine der sichersten Anlageformen. Besonders Neubauimmobilien bieten durch moderne Energiestandards und Garantien zusätzliche Sicherheit. Wichtige Faktoren sind Lage, Ausstattung, Energieeffizienz und Finanzierungskonditionen.",
        "category": "grundlagen",
        "tags": ["investment", "sicherheit", "neubau"]
    },
    {
        "id": "handbook_002",
        "title": "Steuerliche Optimierung bei Immobilieninvestments",
        "content": "Neben der normalen Abschreibung (2% p.a. über 50 Jahre) können Sie bei Neubauimmobilien die 5% Sonder-AfA nutzen. Zusätzlich sind Renovierungskosten, Verwaltungskosten und Kreditzinsen steuerlich absetzbar. Eine optimale Steuerplanung kann die Rendite erheblich steigern.",
        "category": "steuern",
        "tags": ["steueroptimierung", "abschreibung", "rendite"]
    },
    {
        "id": "handbook_003",
        "title": "Finanzierungsstrategien für Kapitalanleger",
        "content": "Für Kapitalanleger gelten andere Finanzierungsbedingungen als für Eigennutzer. Wichtig sind: niedriger Tilgungsanteil (1-2%), lange Zinsbindung für Planungssicherheit, und die Berücksichtigung von Mieteinnahmen bei der Finanzierung. Durch geschickte Strukturierung kann die monatliche Belastung unter 200€ gehalten werden.",
        "category": "finanzierung", 
        "tags": ["finanzierungsstrategie", "tilgung", "zinsbindung"]
    },
    {
        "id": "handbook_004",
        "title": "Standortanalyse und Markteinschätzung",
        "content": "Bei der Standortanalyse sind folgende Faktoren entscheidend: Bevölkerungsentwicklung, Arbeitsplätze, Infrastruktur, Bildungseinrichtungen und geplante Entwicklungen. Großstädte und deren Speckgürtel bieten meist die beste Wertentwicklung und Vermietbarkeit.",
        "category": "standort",
        "tags": ["standortanalyse", "markteinschätzung", "wertentwicklung"]
    }
]

@FunctionTool
def search_faq(query: str, category: Optional[str] = None) -> str:
    """
    Search FAQ database by query.
    
    Args:
        query: Search query
        category: Category for filtering (optional)
        
    Returns:
        Relevant FAQ entries in JSON format
    """
    query_lower = query.lower()
    results = []
    
    for faq in FAQ_DATABASE:
        # Simple text search (will be semantic search in production)
        if (query_lower in faq["question"].lower() or 
            query_lower in faq["answer"].lower() or
            any(tag in query_lower for tag in faq["tags"])):
            
            if category is None or faq["category"] == category:
                results.append(faq)
    
    # Sort by relevance (simple heuristic)
    results.sort(key=lambda x: (
        query_lower in x["question"].lower(),
        len([tag for tag in x["tags"] if tag in query_lower])
    ), reverse=True)
    
    return json.dumps({
        "query": query,
        "category_filter": category,
        "results_count": len(results),
        "results": results[:5]  # Top 5 results
    }, ensure_ascii=False, indent=2)


@FunctionTool
def search_handbook(query: str, category: Optional[str] = None) -> str:
    """
    Search handbook database by query.
    
    Args:
        query: Search query
        category: Category for filtering (optional)
        
    Returns:
        Relevant handbook entries in JSON format
    """
    query_lower = query.lower()
    results = []
    
    for handbook in HANDBOOK_DATABASE:
        # Simple text search
        if (query_lower in handbook["title"].lower() or 
            query_lower in handbook["content"].lower() or
            any(tag in query_lower for tag in handbook["tags"])):
            
            if category is None or handbook["category"] == category:
                results.append(handbook)
    
    # Sort by relevance
    results.sort(key=lambda x: (
        query_lower in x["title"].lower(),
        len([tag for tag in x["tags"] if tag in query_lower])
    ), reverse=True)
    
    return json.dumps({
        "query": query,
        "category_filter": category,
        "results_count": len(results),
        "results": results[:3]  # Top 3 results for handbook
    }, ensure_ascii=False, indent=2)


@FunctionTool
def get_knowledge_categories() -> str:
    """
    Get list of available categories in knowledge base.
    
    Returns:
        List of categories in JSON format
    """
    faq_categories = list(set(faq["category"] for faq in FAQ_DATABASE))
    handbook_categories = list(set(handbook["category"] for handbook in HANDBOOK_DATABASE))
    
    return json.dumps({
        "faq_categories": faq_categories,
        "handbook_categories": handbook_categories,
        "all_categories": list(set(faq_categories + handbook_categories))
    }, ensure_ascii=False, indent=2)


@FunctionTool
def add_knowledge_entry(
    entry_type: str,  # "faq" or "handbook"
    title: str,
    content: str,
    category: str,
    tags: List[str]
) -> str:
    """
    Add new entry to knowledge base.
    
    Args:
        entry_type: Entry type ("faq" or "handbook")
        title: Title/question
        content: Content/answer
        category: Category
        tags: List of tags
        
    Returns:
        Addition confirmation
    """
    if entry_type == "faq":
        new_id = f"faq_{len(FAQ_DATABASE) + 1:03d}"
        new_entry = {
            "id": new_id,
            "question": title,
            "answer": content,
            "category": category,
            "tags": tags
        }
        FAQ_DATABASE.append(new_entry)
        
    elif entry_type == "handbook":
        new_id = f"handbook_{len(HANDBOOK_DATABASE) + 1:03d}"
        new_entry = {
            "id": new_id,
            "title": title,
            "content": content,
            "category": category,
            "tags": tags
        }
        HANDBOOK_DATABASE.append(new_entry)
    else:
        return json.dumps({
            "status": "error",
            "message": "Invalid entry type. Use 'faq' or 'handbook'"
        }, ensure_ascii=False)
    
    return json.dumps({
        "status": "success",
        "message": f"New entry added to {entry_type}",
        "entry_id": new_id,
        "entry": new_entry
    }, ensure_ascii=False, indent=2) 