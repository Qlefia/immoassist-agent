"""
Knowledge tools for ImmoAssist enterprise system.
Provides RAG (Retrieval-Augmented Generation) capabilities using Vertex AI Search.
"""

import json
from typing import List
from google.adk.tools import FunctionTool
from app.models.output_schemas import RagResponse, RagSource
from .vertex_search import search_vertex_ai_search


@FunctionTool
def search_knowledge_rag(query: str, top_k: int = 3) -> RagResponse:
    """
    Search knowledge documents in Vertex AI Search and return structured response with sources.
    """
    print(f"[RAG] Processing query: {query}")
    answer_text = None
    sources = []
    # Try Answer endpoint first for generative responses
    try:
        print("[RAG] Trying Answer endpoint...")
        answer_results = search_vertex_ai_search(query, page_size=top_k, use_answer=True)
        if answer_results and len(answer_results) > 0:
            answer_data = answer_results[0]
            if "answer" in answer_data:
                answer_obj = answer_data["answer"]
                answer_text = answer_obj.get("answerText", "")
                citations = answer_obj.get("citations", [])
                references = answer_obj.get("references", [])
                # Process references first (prefer those with links)
                for ref in references:
                    title = ref.get("title", "Document")
                    uri = ref.get("uri", "")
                    if uri and title:
                        sources.append(RagSource(title=title, link=uri))
                # Fallback to citations if no references
                if not sources:
                    for citation in citations:
                        citation_sources = citation.get("sources", [])
                        for source in citation_sources:
                            title = source.get("title", "Document")
                            uri = source.get("uri", "")
                            if uri and title:
                                sources.append(RagSource(title=title, link=uri))
                # Try alternative URI fields if still no sources
                if not sources:
                    for citation in citations:
                        citation_sources = citation.get("sources", [])
                        for source in citation_sources:
                            uri = (
                                source.get("uri", "") or 
                                source.get("link", "") or 
                                source.get("url", "") or
                                source.get("document", {}).get("uri", "")
                            )
                            title = (
                                source.get("title", "") or 
                                source.get("displayName", "") or
                                "Document"
                            )
                            if uri and title:
                                sources.append(RagSource(title=title, link=uri))
                # If still no sources with links, but there are titles, add them with empty link
                if not sources:
                    # Try references first
                    for ref in references:
                        title = ref.get("title", "Document")
                        if title:
                            sources.append(RagSource(title=title, link=""))
                    # Then try citations
                    if not sources:
                        for citation in citations:
                            citation_sources = citation.get("sources", [])
                            for source in citation_sources:
                                title = (
                                    source.get("title", "") or 
                                    source.get("displayName", "") or
                                    "Document"
                                )
                                if title:
                                    sources.append(RagSource(title=title, link=""))
    except Exception as e:
        print(f"[RAG] Answer endpoint failed: {e}")
    # Fallback to Search endpoint
    if not answer_text or len(answer_text) < 10:
        print("[RAG] Falling back to Search endpoint...")
        try:
            results = search_vertex_ai_search(query, page_size=top_k, use_answer=False)
            for doc in results:
                # Add with link if available, otherwise with just title
                if doc.get("title"):
                    sources.append(RagSource(title=doc["title"], link=doc.get("link", "")))
            # Collect content for response
            content_parts = []
            for doc in results:
                if doc.get("content"):
                    content_parts.append(f"Document: {doc['title']}\n{doc['content']}")
            if content_parts:
                answer_text = content_parts[0].split('\n', 1)[1] if len(content_parts[0].split('\n', 1)) > 1 else content_parts[0]
            else:
                if sources:
                    answer_text = "Relevant documents found in knowledge base, but content is temporarily unavailable. Please contact our specialists for personalized consultation."
                else:
                    answer_text = "No relevant information found in knowledge base for your query. Please contact our specialists for personalized consultation."
        except Exception as e:
            print(f"[RAG] Search endpoint failed: {e}")
            answer_text = "Technical error occurred during search. Please contact our specialists."
    
    # Return structured RagResponse object
    return RagResponse(
        answer=answer_text.strip() if answer_text else "No answer found.",
        sources=sources
    ) 