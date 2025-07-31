#!/usr/bin/env python3
# Copyright 2025 ImmoAssist


"""
ImmoAssist Agent Runner.

Provides a web interface for the ImmoAssist multi-agent system using
Google ADK's FastAPI integration with additional endpoints for TTS
and frontend serving.
"""

import os
import sys
import logging
from pathlib import Path
from typing import AsyncGenerator
from datetime import datetime

import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
import httpx

# Import health checks and observability
from app.health_checks import health_checker
from app.observability import metrics_collector, track_user_interaction

# Environment variables are loaded in app.config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Verify critical environment variables
REQUIRED_ENV_VARS = [
    "GOOGLE_CLOUD_PROJECT",
    "MODEL_NAME",
    "SPECIALIST_MODEL",
    "CHAT_MODEL"
]

for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        logger.warning(f"Environment variable {var} not set")

# Set default values for optional variables
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "europe-west3")


class TTSRequest(BaseModel):
    """Text-to-speech request model."""
    text: str
    voice_id: str = "pNInz6obpgDQGcFmaJgB"  # Adam - multilingual voice
    model_id: str = "eleven_flash_v2_5"  # Optimized for low latency


class VoiceChatRequest(BaseModel):
    """Voice chat request model."""
    text: str
    voice_id: str = "pNInz6obpgDQGcFmaJgB"
    app_name: str
    user_id: str
    session_id: str


async def stream_tts_audio(text: str, voice_id: str, model_id: str) -> AsyncGenerator[bytes, None]:
    """
    Stream text-to-speech audio from ElevenLabs API.
    
    Args:
        text: Text to convert to speech
        voice_id: ElevenLabs voice identifier
        model_id: ElevenLabs model identifier
        
    Yields:
        Audio chunks as bytes
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        logger.error("ElevenLabs API key not configured")
        yield b""
        return
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        },
        "output_format": "mp3_22050_32"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", 
                url, 
                json=data, 
                headers=headers,
                timeout=30.0
            ) as response:
                if response.status_code == 200:
                    async for chunk in response.aiter_bytes(chunk_size=1024):
                        yield chunk
                else:
                    logger.error(f"ElevenLabs API error: {response.status_code}")
                    yield b""
    except Exception as e:
        logger.error(f"TTS streaming error: {str(e)}")
        yield b""


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI app instance
    """
    # Get project root directory
    script_dir = Path(__file__).resolve().parent
    
    logger.info("Starting ImmoAssist Agent...")
    logger.info(f"Project directory: {script_dir}")
    
    # Create FastAPI app with ADK
    # Convert the Path object to a string and explicitly point to the "agents" directory.
    # get_fast_api_app expects a string path and internally performs string operations
    # (e.g., rstrip), which will fail if a pathlib.Path object is supplied.
    # The ADK expects the directory that *contains* individual agent packages.
    # In this repository, that is the project root directory (script_dir), not
    # the nested "agents" folder.
    agents_path = str(script_dir)
    app = get_fast_api_app(
        agents_dir=agents_path,
        web=True,  # Enable web interface
        allow_origins=["*"],  # Allow all origins for development
    )
    
    # Add TTS streaming endpoint
    @app.post("/tts-stream")
    async def generate_tts_stream(request: TTSRequest):
        """Stream text-to-speech audio."""
        try:
            return StreamingResponse(
                stream_tts_audio(request.text, request.voice_id, request.model_id),
                media_type="audio/mpeg",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Connection": "keep-alive"
                }
            )
        except Exception as e:
            logger.error(f"TTS streaming failed: {str(e)}")
            raise HTTPException(status_code=500, detail="TTS generation failed")
    
    # Add CORS preflight handler for TTS
    @app.options("/tts-stream")
    async def tts_stream_options():
        """Handle CORS preflight requests."""
        from fastapi.responses import Response
        return Response(
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "3600"
            }
        )
    
    # Add comprehensive health check endpoint
    @app.get("/health")
    async def health_check():
        """Comprehensive health check for all system components."""
        try:
            health_status = await health_checker.check_all()
            
            # Return appropriate HTTP status based on health
            if health_status["status"] == "unhealthy":
                return JSONResponse(
                    status_code=503,
                    content=health_status
                )
            elif health_status["status"] == "degraded":
                return JSONResponse(
                    status_code=200,
                    content=health_status
                )
            else:
                return JSONResponse(
                    status_code=200,
                    content=health_status
                )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": "unavailable"
                }
            )
    
    # Add metrics endpoint for monitoring
    @app.get("/metrics")
    async def get_metrics():
        """Get application metrics for monitoring."""
        try:
            return JSONResponse(
                status_code=200,
                content={
                    "metrics_summary": metrics_collector.get_metrics_summary(),
                    "cloud_monitoring_format": metrics_collector.export_metrics_for_cloud_monitoring()
                }
            )
        except Exception as e:
            logger.error(f"Metrics endpoint failed: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": str(e)}
            )
    
    # Add readiness probe endpoint  
    @app.get("/ready")
    async def readiness_check():
        """Simple readiness check for Kubernetes/Cloud Run."""
        try:
            # Quick check of essential services
            vertex_ai_check = await health_checker.check_vertex_ai()
            
            if vertex_ai_check.status == "unhealthy":
                return JSONResponse(
                    status_code=503,
                    content={"ready": False, "reason": vertex_ai_check.message}
                )
            
            return JSONResponse(
                status_code=200,
                content={"ready": True, "timestamp": vertex_ai_check.timestamp}
            )
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={"ready": False, "error": str(e)}
            )
    
    # Add liveness probe endpoint
    @app.get("/alive")
    async def liveness_check():
        """Simple liveness check for Kubernetes/Cloud Run."""
        return JSONResponse(
            status_code=200,
            content={
                "alive": True,
                "timestamp": str(datetime.utcnow()),
                "application": "immoassist"
            }
        )
    
    # Mount frontend static files
    frontend_path = script_dir / "frontend"
    if frontend_path.exists():
        app.mount("/chat", StaticFiles(directory=str(frontend_path), html=True), name="chat")
        
        # Redirect root to chat interface
        @app.get("/")
        async def redirect_to_chat():
            """Redirect root URL to chat interface."""
            return RedirectResponse(url="/chat/", status_code=302)
    else:
        logger.warning(f"Frontend directory not found: {frontend_path}")
    
    return app


def main():
    """Run the ImmoAssist agent server."""
    try:
        # Create the application
        app = create_app()
        
        # Get port from environment (Cloud Run compatibility)
        port = int(os.environ.get("PORT", 8000))
        host = os.environ.get("HOST", "0.0.0.0")
        
        logger.info(f"Starting server on {host}:{port}")
        logger.info(f"Web interface available at: http://localhost:{port}")
        logger.info(f"ADK Development UI available at: http://localhost:{port}/adk")
        
        # Run the server
        uvicorn.run(
            app, 
            host=host, 
            port=port, 
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start agent: {str(e)}")
        logger.info("Please ensure:")
        logger.info("  - Google Cloud authentication is configured")
        logger.info("  - Required environment variables are set")
        logger.info("  - Vertex AI API is enabled in your project")
        sys.exit(1)


if __name__ == "__main__":
    main()
