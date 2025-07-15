"""
Knowledge management tools for ImmoAssist.
"""
import os

from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

from app.config import config


search_knowledge_rag = VertexAiRagRetrieval(
    name="search_knowledge_rag",
    description=(
        "Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,"
    ),
    rag_resources=[
        rag.RagResource(
            rag_corpus=config.rag_corpus,
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
) 