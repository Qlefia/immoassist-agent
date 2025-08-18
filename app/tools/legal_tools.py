"""
Legal tools for ImmoAssist.

Provides RAG-based knowledge retrieval for German real estate law information.
"""

import os
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag
from app.config import config

# Legal knowledge base search tool
search_legal_rag = VertexAiRagRetrieval(
    name="search_legal_rag",
    description=(
        "Search the ImmoAssist legal knowledge base for German real estate law information, "
        "including regulations, contracts, legal procedures, and compliance requirements."
    ),
    rag_resources=[
        rag.RagResource(
            rag_corpus=config.legal_rag_corpus,
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)

# Export the tool
__all__ = ["search_legal_rag"]
