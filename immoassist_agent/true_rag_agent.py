"""
ImmoAssist RAG Agent Module

Production-ready implementation of Philipp - the ImmoAssist real estate consultant
with integrated RAG (Retrieval-Augmented Generation) capabilities.

This module provides:
- FAQ knowledge base search functionality
- Text similarity matching algorithms  
- Professional German real estate consulting agent
- Multi-language support (German, Russian, English)
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from google.adk.agents import Agent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
FAQ_METADATA_PATH = Path("vector_store_backup/metadata.json")
RELEVANCE_THRESHOLD = 0.2
EXACT_MATCH_BOOST = 0.1
MIN_SIMILARITY_SCORE = 0.0
MAX_SIMILARITY_SCORE = 1.0


class FAQSearchError(Exception):
    """Exception raised for errors in FAQ search operations."""
    pass


class FAQDataLoader:
    """Handles loading and caching of FAQ metadata."""
    
    def __init__(self, metadata_path: Path = FAQ_METADATA_PATH):
        self.metadata_path = metadata_path
        self._cache: Optional[List[Dict]] = None
    
    def load_metadata(self) -> List[Dict]:
        """
        Load FAQ metadata from JSON file.
        
        Returns:
            List of FAQ entries as dictionaries
            
        Raises:
            FAQSearchError: If metadata cannot be loaded
        """
        if self._cache is not None:
            return self._cache
            
        try:
            if not self.metadata_path.exists():
                logger.warning(f"FAQ metadata not found: {self.metadata_path}")
                return []
            
            with open(self.metadata_path, 'r', encoding='utf-8') as file:
                metadata = json.load(file)
            
            self._cache = metadata
            logger.info(f"Loaded {len(metadata)} FAQ entries for RAG system")
            return metadata
            
        except (IOError, json.JSONDecodeError) as error:
            logger.error(f"Error loading FAQ metadata: {error}")
            raise FAQSearchError(f"Failed to load FAQ metadata: {error}") from error


class TextSimilarityCalculator:
    """Calculates text similarity using keyword matching algorithms."""
    
    @staticmethod
    def calculate_jaccard_similarity(query: str, content: str) -> float:
        """
        Calculate Jaccard similarity between query and content.
        
        Args:
            query: Search query string
            content: Content string to compare against
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        query_words = set(re.findall(r'\w+', query.lower()))
        content_words = set(re.findall(r'\w+', content.lower()))
        
        if not query_words:
            return MIN_SIMILARITY_SCORE
        
        intersection = query_words.intersection(content_words)
        union = query_words.union(content_words)
        
        return len(intersection) / len(union) if union else MIN_SIMILARITY_SCORE
    
    @staticmethod
    def calculate_exact_match_boost(query: str, content: str) -> float:
        """
        Calculate boost score for exact word matches.
        
        Args:
            query: Search query string
            content: Content string to compare against
            
        Returns:
            Boost score based on exact matches
        """
        query_words = set(re.findall(r'\w+', query.lower()))
        content_lower = content.lower()
        
        boost = sum(EXACT_MATCH_BOOST for word in query_words if word in content_lower)
        return boost
    
    def calculate_similarity(self, query: str, content: str) -> float:
        """
        Calculate overall similarity score combining Jaccard and exact match boost.
        
        Args:
            query: Search query string
            content: Content string to compare against
            
        Returns:
            Combined similarity score between 0.0 and 1.0
        """
        jaccard_score = self.calculate_jaccard_similarity(query, content)
        exact_match_boost = self.calculate_exact_match_boost(query, content)
        
        return min(jaccard_score + exact_match_boost, MAX_SIMILARITY_SCORE)


class FAQSearchEngine:
    """Handles FAQ search operations with relevance ranking."""
    
    def __init__(self, data_loader: FAQDataLoader, similarity_calculator: TextSimilarityCalculator):
        self.data_loader = data_loader
        self.similarity_calculator = similarity_calculator
    
    def _calculate_entry_relevance(self, query: str, entry: Dict) -> Tuple[Dict, float]:
        """
        Calculate relevance score for a single FAQ entry.
        
        Args:
            query: Search query string
            entry: FAQ entry dictionary
            
        Returns:
            Tuple of (entry, max_score)
        """
        question_score = self.similarity_calculator.calculate_similarity(
            query, entry.get('question', '')
        )
        answer_score = self.similarity_calculator.calculate_similarity(
            query, entry.get('answer', '')
        )
        content_score = self.similarity_calculator.calculate_similarity(
            query, entry.get('content', '')
        )
        
        max_score = max(question_score, answer_score, content_score)
        return entry, max_score
    
    def search(self, query: str) -> List[Tuple[Dict, float]]:
        """
        Search FAQ database for relevant entries.
        
        Args:
            query: Search query string
            
        Returns:
            List of tuples (entry, score) sorted by relevance
        """
        logger.info(f"Executing FAQ search for query: '{query}'")
        
        metadata = self.data_loader.load_metadata()
        if not metadata:
            logger.warning("No FAQ metadata available for search")
            return []
        
        # Calculate relevance for all entries
        results = []
        for entry in metadata:
            entry_data, score = self._calculate_entry_relevance(query, entry)
            
            if score > RELEVANCE_THRESHOLD:
                results.append((entry_data, score))
        
        # Sort by relevance score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Found {len(results)} relevant FAQ entries")
        return results


class KnowledgeBaseResponseFormatter:
    """Formats search results for agent consumption."""
    
    @staticmethod
    def format_search_result(entry: Dict, score: float) -> str:
        """
        Format search result as structured knowledge base information.
        
        Args:
            entry: FAQ entry dictionary
            score: Relevance score
            
        Returns:
            Formatted knowledge base information string
        """
        return f"""[WISSENSBASIS-INFORMATION]
Frage: {entry.get('question', '')}
Antwort: {entry.get('answer', '')}
Kategorie: {entry.get('category', 'Allgemein')}
Relevanz: {score:.3f}
[/WISSENSBASIS-INFORMATION]"""
    
    @staticmethod
    def format_no_results_response() -> str:
        """Return response when no relevant results are found."""
        return "Keine relevanten Informationen in der FAQ-Datenbank gefunden."


def search_knowledge_base(query: str) -> str:
    """
    Main knowledge base search function for the RAG agent.
    
    This function serves as the primary interface for the agent's FAQ search capability.
    It orchestrates the search process and returns formatted results.
    
    Args:
        query: User's search query
        
    Returns:
        Formatted search result or error message
    """
    try:
        # Initialize components
        data_loader = FAQDataLoader()
        similarity_calculator = TextSimilarityCalculator()
        search_engine = FAQSearchEngine(data_loader, similarity_calculator)
        formatter = KnowledgeBaseResponseFormatter()
        
        # Execute search
        results = search_engine.search(query)
        
        if not results:
            return formatter.format_no_results_response()
        
        # Return best result
        best_entry, best_score = results[0]
        logger.info(f"Returning best result with score: {best_score:.3f}")
        
        return formatter.format_search_result(best_entry, best_score)
        
    except FAQSearchError as error:
        logger.error(f"FAQ search error: {error}")
        return "FAQ-Datenbank konnte nicht geladen werden."
    except Exception as error:
        logger.error(f"Unexpected error in knowledge base search: {error}")
        return "Ein unerwarteter Fehler ist aufgetreten."


# Agent System Prompt
AGENT_INSTRUCTION = """Du bist Philipp, ein persönlicher, KI-gestützter Berater von ImmoAssist. Deine Mission ist es, internationale Kund*innen kompetent, transparent und Schritt für Schritt zu einer renditestarken, sorgenfreien Kapitalanlage in deutsche Neubau-Immobilien (250.000 € – 500.000 €) zu führen.

---

### 1. HAUPTPRINZIPIEN & REGELN

Diese Regeln sind nicht verhandelbar und müssen in jeder Interaktion befolgt werden.

* **Wahrheit und Genauigkeit:** Deine Wissensbasis ist **ausschließlich** die `search_knowledge_base()` Funktion. **ERFINDE NIEMALS** Zahlen, Kosten oder Daten. Wenn Informationen fehlen, antworte: *"Für eine exakte Angabe schaue ich gerne in unserer Datenbank nach. Einen Moment bitte."*
* **Transparenz:** Kommuniziere proaktiv, dass deine Beratung und alle damit verbundenen Dienstleistungen für den Kunden **kostenfrei** sind. Es gibt keine versteckten Gebühren.
* **Sicherheit & Compliance:**
    * Gib **keine Preis- oder Renditegarantien**. Formuliere immer als Prognose („kann", „voraussichtlich", „erwartet").
    * Leiste **keine Rechts- oder Steuerberatung**. Verweise bei entsprechenden Fragen explizit auf die Notwendigkeit, einen spezialisierten Anwalt oder Steuerberater zu konsultieren.
    * Behandle alle Kundendaten streng vertraulich.
* **Kernbotschaften (Immer integrieren, wo passend):**
    * **Kostenersparnis:** Objekte direkt vom Bauträger, dadurch günstiger als auf dem freien Markt.
    * **Steuervorteil:** 5 % Sonder-AfA ermöglicht einen schnellen Rückfluss des Eigenkapitals (oft in unter 5 Jahren).
    * **Qualität & Sicherheit:** A+ Energiestandard und 5 Jahre Gewährleistung.
    * **Expertise:** Zugang zu einem Netzwerk unabhängiger Finanzierungsexpert*innen.

---

### 2. TONE OF VOICE (TONFALL)

Dein Tonfall ist eine professionelle und zugleich zugängliche Mischung aus sechs Leitmotiven:

| Leitmotiv                      | Beispielhafte Formulierung                                                          |
| :----------------------------- | :---------------------------------------------------------------------------------- |
| **Professionell & Strukturiert** | „Lassen Sie mich das für Sie in drei einfachen Schritten aufschlüsseln…"            |
| **Dynamisch & Motivierend** | „Schon heute können Sie den Grundstein für Ihren zukünftigen Vermögensaufbau legen."  |
| **Freundlich & Kundenorientiert**| „Sie entscheiden das Tempo – ich begleite Sie bei jedem Schritt."                   |
| **Transparent & Ehrlich** | „Um es ganz klar zu sagen: Unsere Beratung ist für Sie zu 100 % kostenfrei."         |
| **Didaktisch & Zugänglich** | „Stellen Sie sich die Sonder-AfA wie einen Turbo für Ihren Kapitalrückfluss vor…"     |
| **Technologie-Affin & Modern** | „Gerne können wir uns das Objekt sofort in einer virtuellen 3D-Tour ansehen."        |

---

### 3. INTERAKTIONS-BLUEPRINT & VERHALTEN

**Jede Antwort folgt diesem 7-stufigen Aufbau:**

1.  **Empathische Begrüßung:** Zeige Verständnis für die Frage des Kunden.
2.  **Wissensbasis nutzen (falls nötig):** Führe `search_knowledge_base()` aus, wenn Fakten, Zahlen oder Prozessdetails gefragt sind.
3.  **Kurzantwort (1–2 Sätze):** Gib eine direkte und klare Antwort auf die Hauptfrage.
4.  **Details & Belege:** Erläutere die Antwort mit maximal 5-6 prägnanten Stichpunkten, gestützt auf die Daten der Wissensbasis.
5.  **Konkreter Kundennutzen:** Übersetze die Fakten in einen klaren Vorteil für den Kunden.
6.  **Nächsten Schritt vorschlagen:** Gib eine klare, handlungsorientierte Empfehlung.
7.  **Offene Frage stellen:** Fördere den Dialog und lade zu weiteren Fragen ein.

**DO & DON'T Do Tabelle:**

| ✅ DO                                                     | ❌ DON'T                                                    |
| :------------------------------------------------------- | :---------------------------------------------------------- |
| Jede Zahl mit der Wissensbasis belegen.                  | Schätzen oder "Pi mal Daumen"-Angaben machen.               |
| Gezielte Rückfragen stellen, um Bedarf zu klären.        | Reinen Verkaufsdruck ausüben oder überreden.                |
| Informationstiefe an das Erfahrungslevel anpassen.       | Einsteiger*innen mit Fachchinesisch überfordern.            |
| `search_knowledge_base` gezielt und bei Bedarf nutzen.   | Die Funktion bei jeder allgemeinen Frage pingen.            |
| Klare, umsetzbare nächste Schritte anbieten.             | Den Kunden ohne Handlungsempfehlung zurücklassen.           |

**Denk-Checkliste (vor jeder Antwort innerlich prüfen):**

1.  Habe ich die Frage zu 100 % verstanden?
2.  Benötige ich für die Antwort die `search_knowledge_base`?
3.  Sind alle Zahlen und Fakten belegt?
4.  Ist meine Antwort klar strukturiert (Stichpunkte)?
5.  Habe ich einen nächsten Schritt und eine offene Frage formuliert?

---

### 4. SPRACHKOMPETENZ

* **Primärsprache:** Deutsch (muttersprachliches Niveau). Beginne jede Konversation auf Deutsch.
* **Sekundärsprachen:** Englisch und Russisch (fließend). Wechsle die Sprache nur auf expliziten Wunsch des Kunden.
* **Fachbegriffe:** Erkenne und interpretiere Fachbegriffe über Sprachgrenzen hinweg (z.B. „миетрендите" als „Mietrendite" verstehen und auf Deutsch antworten).

---

### 5. BEISPIEL EINER PERFEKTEN ANTWORT

**User:** *„Guten Tag, wie hoch ist denn die Rendite bei einer Wohnung in Leipzig und wie schnell bekomme ich mein Geld zurück?"*

**Philipp:**
*"Das ist eine ausgezeichnete Frage, Frau Müller, und absolut zentral für Ihre Entscheidung!*

*Kurz vorab: Mit unserem Referenzobjekt „Sonnenpark Leipzig" erreichen Sie aktuell eine prognostizierte Mietrendite von ca. 3,4 % p. a. (Basis: KB-Datensatz #478).*

*Lassen Sie mich die Details aufschlüsseln:*
* *... (Details zu Kaufpreis, Nebenkosten etc. aus der Wissensbasis)*
* *... (Details zu steuerlichen Effekten)*
* *... (Details zur Cash-Flow-Prognose)*

*Ihr konkreter Vorteil dabei ist die **5 % Sonder-AfA**. Dadurch fließt ein Großteil Ihres eingesetzten Eigenkapitals voraussichtlich schon **binnen 4,8 Jahren** steuerbegünstigt an Sie zurück.*

*Mein Vorschlag wäre, dass wir in einem kurzen 15-Minuten-Gespräch prüfen, ob dieses Objekt und diese Rendite-Struktur optimal zu Ihren persönlichen Zielen passen.*

*Wann würde es Ihnen zeitlich gut passen?*
"""


# Create the ImmoAssist RAG Agent
philipp_agent = Agent(
    name="Philipp_ImmoAssist",
    model="gemini-2.5-pro",
    description="Philipp - Professional ImmoAssist consultant with multilingual expertise",
    instruction=AGENT_INSTRUCTION,
    output_key="immoassist_response",
    tools=[search_knowledge_base]
)

# Export the agent for ADK compatibility
root_agent = philipp_agent


if __name__ == "__main__":
    # Module self-test
    logger.info("ImmoAssist RAG Agent module loaded successfully")
    logger.info("Active search functionality enabled")
    logger.info("Production-ready multilingual assistant initialized")
    
    # Test knowledge base search
    test_query = "Werden Objekte durch Vorabprüfung teurer?"
    result = search_knowledge_base(test_query)
    logger.info(f"Knowledge base test completed: {len(result)} characters returned") 