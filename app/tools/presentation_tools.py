"""
Presentation tools for ImmoAssist.

Provides RAG-based knowledge retrieval for real estate investment course content.
"""

from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag
from app.config import config

# Presentation knowledge base search tool
search_presentation_rag = VertexAiRagRetrieval(
    name="search_presentation_rag",
    description=(
        "Search the ImmoAssist presentation knowledge base for real estate investment course content, "
        "including the 3.5% rule, apartment selection criteria, yield calculations, and course materials."
    ),
    rag_resources=[
        rag.RagResource(
            rag_corpus=config.presentation_rag_corpus,
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)

# Export the tool
__all__ = ["search_presentation_rag"]
