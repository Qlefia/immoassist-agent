"""
Knowledge management tools for ImmoAssist.

Provides RAG-based knowledge retrieval for German real estate investment information.
"""

import os
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag
from app.config import config

# Main knowledge base search tool
search_knowledge_base = VertexAiRagRetrieval(
    name="search_knowledge_base",
    description=(
        "Search the ImmoAssist knowledge base for German real estate investment information, "
        "including financing strategies, tax benefits, depreciation rules, and best practices."
    ),
    rag_resources=[
        rag.RagResource(
            rag_corpus=config.rag_corpus,
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)

# Export the tool
__all__ = ["search_knowledge_base"]
