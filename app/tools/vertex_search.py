import requests
import os
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Vertex AI Search (Discovery Engine) configuration
PROJECT_ID = "29448644777"
ENGINE_ID = "doc-ai-search_1751880000612"
REGION = "eu"
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")  # Path to your service account JSON
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

# Endpoints
SEARCH_URL = f"https://{REGION}-discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{REGION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search:search"
ANSWER_URL = f"https://{REGION}-discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{REGION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search:answer"

# Note: The load_dotenv() call has been removed. Environment variables are now expected 
# to be loaded by the parent script or execution environment.

def get_access_token() -> str:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    credentials.refresh(Request())
    return credentials.token


def search_vertex_ai_search(query: str, page_size: int = 3, use_answer: bool = False, session: Optional[str] = None) -> List[Dict]:
    """
    Search all documents in Vertex AI Search (Discovery Engine) using the new endpoint and parameters.
    Args:
        query (str): The user's question or search query.
        page_size (int): Number of top results to return.
        use_answer (bool): If True, use the answer endpoint (generative answer). If False, use search endpoint (document chunks).
        session (str, optional): Session string for the API (optional).
    Returns:
        List[Dict]: List of relevant document chunks or answers (with metadata).
    """
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    if use_answer:
        # (answer endpoint)
        payload = {
            "query": {
                "text": query,
                "queryId": ""
            },
            "session": session or "",
            "relatedQuestionsSpec": {"enable": True},
            "answerGenerationSpec": {
                "ignoreAdversarialQuery": True,
                "ignoreNonAnswerSeekingQuery": False,
                "ignoreLowRelevantContent": True,
                "multimodalSpec": {},
                "includeCitations": True,
                "modelSpec": {"modelVersion": "stable"}
            }
        }
        response = requests.post(ANSWER_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        # Вернуть весь ответ для гибкости
        return [data]
    else:
        # Поиск документов (search endpoint)
        payload = {
            "query": query,
            "pageSize": page_size,
            "queryExpansionSpec": {"condition": "AUTO"},
            "spellCorrectionSpec": {"mode": "AUTO"},
            # languageCode убран для автоопределения
            "userInfo": {"timeZone": "Europe/Kaliningrad"}
        }
        if session:
            payload["session"] = session
        response = requests.post(SEARCH_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        results = []
        for doc in data.get("results", []):
            struct = doc.get("document", {}).get("derivedStructData", {})
            snippet = struct.get("extractive_answers", [])
            title = struct.get("title", "")
            link = struct.get("link", "")
            if snippet:
                for answer in snippet:
                    results.append({
                        "title": title,
                        "content": answer.get("content", ""),
                        "page": answer.get("pageNumber", ""),
                        "link": link
                    })
            else:
                if title or link:
                    results.append({
                        "title": title,
                        "content": "",
                        "page": "",
                        "link": link
                    })
        # Логируем найденные документы
        print("\n[Vertex AI Search] Найдено документов:", len(results))
        for i, doc in enumerate(results, 1):
            print(f"{i}. Title: {doc['title']}")
            print(f"   Link: {doc['link']}")
            print(f"   Content: {doc['content'][:200]}{'...' if len(doc['content']) > 200 else ''}")
        if not results:
            print("\n[DEBUG] Полный ответ от Vertex AI Search:")
            print(response.text)
        return results 