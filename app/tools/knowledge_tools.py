"""Knowledge tools for ImmoAssist enterprise system."""

import json
import os
from typing import List, Optional
from google.adk.tools import FunctionTool
from .vertex_search import search_vertex_ai_search
from google.generativeai import GenerativeModel


def generate_expert_answer(user_question: str, search_results: List[dict]) -> str:
    """
    Generates an expert answer based on search results using Gemini.
    
    Args:
        user_question (str): The user's original question
        search_results (List[dict]): List of search results with title, content, and link
        
    Returns:
        str: Expert answer generated from the search results
    """
    # Build the prompt with sources
    sources = []
    for i, doc in enumerate(search_results, 1):
        sources.append(f"{i}. {doc['title']}: {doc['content'] or '[see source]'} (link: {doc['link']})")
    sources_text = "\n".join(sources)
    prompt = f"""
User Question: {user_question}
Found Sources:
{sources_text}
---
You are a professional real estate consultant. Use the found documents to answer the user's question. Write completely in the language in which the question was asked, even if the sources are in another language. Do not insert original phrases in another language, but paraphrase their meaning in the user's language. Style - expert, structured, clear. Be sure to reference sources (title, link).
"""
    # Auto-language detection - Gemini will handle this automatically if the prompt is in the target language
    model = GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip() if hasattr(response, 'text') else str(response)


@FunctionTool
def search_knowledge_rag(query: str, top_k: int = 3) -> str:
    """
    Search all knowledge documents (FAQ, handbooks, guides, etc.) in Vertex AI Search (Discovery Engine),
    then generate an expert answer in the user's language.
    
    Args:
        query (str): The user's question or search query.
        top_k (int): Number of top results to return.
        
    Returns:
        str: JSON string with 'answer' field (expert answer) and 'sources' field (list of sources).
    """
    results = search_vertex_ai_search(query, page_size=top_k)
    answer = generate_expert_answer(query, results)
    return json.dumps({"answer": answer, "sources": results}, ensure_ascii=False) 