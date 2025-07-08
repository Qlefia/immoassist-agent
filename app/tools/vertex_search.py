"""
Vertex AI Search integration for ImmoAssist knowledge base.
Provides search and answer capabilities using Google Vertex AI Discovery Engine.
"""

import requests
import os
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from typing import List, Dict, Optional
from dotenv import load_dotenv
import json
from app.config import config

# Load environment variables
load_dotenv()

# Vertex AI Search (Discovery Engine) configuration
PROJECT_ID = config.project_id
ENGINE_ID = config.vertex_ai_engine_id
REGION = config.location
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

# Endpoints
SEARCH_URL = f"https://{REGION}-discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{REGION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search:search"
ANSWER_URL = f"https://{REGION}-discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{REGION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search:answer"


def get_access_token() -> str:
    """Get access token for Google Cloud API authentication."""
    if not SERVICE_ACCOUNT_FILE:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
    
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise ValueError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print(f"[ERROR] Failed to get access token: {e}")
        raise


def search_vertex_ai_search(query: str, page_size: int = 3, use_answer: bool = False, session: Optional[str] = None) -> List[Dict]:
    """
    Search documents in Vertex AI Search (Discovery Engine).
    
    Args:
        query: User's question or search query
        page_size: Number of top results to return
        use_answer: If True, use answer endpoint (generative answer). If False, use search endpoint (document chunks)
        session: Session string for API (optional)
        
    Returns:
        List of relevant document chunks or answers with metadata
    """
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    if use_answer:
        # Answer endpoint for generative responses
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
        return [data]
    else:
        # Search endpoint for document retrieval
        payload = {
            "query": query,
            "pageSize": page_size,
            "queryExpansionSpec": {"condition": "AUTO"},
            "spellCorrectionSpec": {"mode": "AUTO"},
            "userInfo": {"timeZone": "Europe/Berlin"}  # German timezone for real estate context
        }
        if session:
            payload["session"] = session
            
        try:
            response = requests.post(SEARCH_URL, headers=headers, json=payload)
            
            if response.status_code != 200:
                print(f"[ERROR] Vertex AI Search error {response.status_code}: {response.text}")
                response.raise_for_status()
                
            data = response.json()
            
        except requests.exceptions.HTTPError as e:
            print(f"[ERROR] HTTP Error: {e}")
            return []
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            return []
        
        results = []
        for doc in data.get("results", []):
            struct = doc.get("document", {}).get("derivedStructData", {})
            
            # Extract content from multiple sources
            content = ""
            
            # Priority 1: Extractive answers
            extractive_answers = struct.get("extractive_answers", [])
            if extractive_answers:
                content = extractive_answers[0].get("content", "")
            
            # Priority 2: Snippets
            if not content:
                snippets = struct.get("snippets", [])
                if snippets:
                    content = snippets[0].get("snippet", "")
            
            # Priority 3: Full document content
            if not content:
                content = struct.get("content", "")
            
            title = struct.get("title", "")
            link = struct.get("link", "")
            
            if content or title or link:
                results.append({
                    "title": title,
                    "content": content,
                    "page": "",
                    "link": link
                })
        
        print(f"[Vertex AI Search] Found {len(results)} documents")
        return results 