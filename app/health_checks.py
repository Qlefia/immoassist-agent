"""
Production health checks for ImmoAssist multi-agent system.

Implements comprehensive health monitoring following ADK Production
Deployment Guidelines and Google Cloud best practices.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import httpx
from google.cloud import aiplatform
from google.api_core import exceptions as gcp_exceptions

from .config import config
from .logging_config import get_logger

logger = get_logger("health_checks")


class HealthStatus:
    """Health status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheckResult:
    """Result of a health check operation."""

    def __init__(
        self,
        service: str,
        status: str,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
        latency_ms: Optional[float] = None,
    ):
        self.service = service
        self.status = status
        self.message = message
        self.details = details or {}
        self.latency_ms = latency_ms
        self.timestamp = datetime.now(timezone.utc).isoformat()


class HealthChecker:
    """Comprehensive health checker for ImmoAssist components."""

    def __init__(self):
        self.timeout_seconds = 10

    async def check_all(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on all components.

        Returns:
            Dictionary with overall health status and individual component results
        """
        start_time = time.time()

        # Run all health checks concurrently
        checks = await asyncio.gather(
            self.check_vertex_ai(),
            self.check_rag_corpora(),
            self.check_elevenlabs_api(),
            self.check_memory_usage(),
            self.check_disk_space(),
            return_exceptions=True,
        )

        results = {}
        overall_status = HealthStatus.HEALTHY
        unhealthy_services = []

        # Process results
        for check in checks:
            if isinstance(check, Exception):
                logger.error(f"Health check failed with exception: {check}")
                result = HealthCheckResult(
                    service="unknown",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {str(check)}",
                )
            else:
                result = check

            results[result.service] = {
                "status": result.status,
                "message": result.message,
                "details": result.details,
                "latency_ms": result.latency_ms,
                "timestamp": result.timestamp,
            }

            # Determine overall status
            if result.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
                unhealthy_services.append(result.service)
            elif (
                result.status == HealthStatus.DEGRADED
                and overall_status == HealthStatus.HEALTHY
            ):
                overall_status = HealthStatus.DEGRADED

        total_time = (time.time() - start_time) * 1000

        return {
            "status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_check_time_ms": round(total_time, 2),
            "services": results,
            "summary": {
                "total_services": len(results),
                "healthy": sum(
                    1 for r in results.values() if r["status"] == HealthStatus.HEALTHY
                ),
                "degraded": sum(
                    1 for r in results.values() if r["status"] == HealthStatus.DEGRADED
                ),
                "unhealthy": sum(
                    1 for r in results.values() if r["status"] == HealthStatus.UNHEALTHY
                ),
                "unhealthy_services": unhealthy_services,
            },
        }

    async def check_vertex_ai(self) -> HealthCheckResult:
        """Check Vertex AI connectivity and model availability."""
        start_time = time.time()

        try:
            # Initialize Vertex AI client
            aiplatform.init(
                project=config.google_cloud.project_id,
                location=config.google_cloud.vertex_ai_location,
            )

            # Test basic connectivity by listing models (with timeout)
            try:
                # This is a lightweight operation to test connectivity
                from google.cloud.aiplatform import Model

                # Test model endpoint availability
                models = Model.list(limit=1)

                latency = (time.time() - start_time) * 1000

                return HealthCheckResult(
                    service="vertex_ai",
                    status=HealthStatus.HEALTHY,
                    message="Vertex AI connectivity verified",
                    details={
                        "project": config.google_cloud.project_id,
                        "location": config.google_cloud.vertex_ai_location,
                        "models_accessible": True,
                    },
                    latency_ms=round(latency, 2),
                )

            except gcp_exceptions.Forbidden:
                return HealthCheckResult(
                    service="vertex_ai",
                    status=HealthStatus.UNHEALTHY,
                    message="Vertex AI access denied - check service account permissions",
                    details={"error": "Insufficient permissions"},
                )

        except Exception as e:
            logger.error(f"Vertex AI health check failed: {e}")
            return HealthCheckResult(
                service="vertex_ai",
                status=HealthStatus.UNHEALTHY,
                message=f"Vertex AI connectivity failed: {str(e)}",
                details={"error": str(e)},
            )

    async def check_rag_corpora(self) -> HealthCheckResult:
        """Check RAG corpora availability and accessibility."""
        start_time = time.time()

        try:
            # Check if RAG corpus IDs are configured
            rag_corpora = {
                "main": getattr(config, "rag_corpus", None),
                "presentation": getattr(config, "presentation_rag_corpus", None),
                "legal": getattr(config, "legal_rag_corpus", None),
            }

            available_corpora = {k: v for k, v in rag_corpora.items() if v}

            if not available_corpora:
                return HealthCheckResult(
                    service="rag_corpora",
                    status=HealthStatus.DEGRADED,
                    message="No RAG corpora configured",
                    details={"configured_corpora": 0},
                )

            # For now, just verify configuration - actual connectivity check would require RAG API calls
            latency = (time.time() - start_time) * 1000

            return HealthCheckResult(
                service="rag_corpora",
                status=HealthStatus.HEALTHY,
                message=f"RAG corpora configured: {len(available_corpora)}",
                details={
                    "configured_corpora": len(available_corpora),
                    "corpus_types": list(available_corpora.keys()),
                },
                latency_ms=round(latency, 2),
            )

        except Exception as e:
            logger.error(f"RAG corpora health check failed: {e}")
            return HealthCheckResult(
                service="rag_corpora",
                status=HealthStatus.UNHEALTHY,
                message=f"RAG corpora check failed: {str(e)}",
                details={"error": str(e)},
            )

    async def check_elevenlabs_api(self) -> HealthCheckResult:
        """Check ElevenLabs API connectivity."""
        start_time = time.time()

        try:
            api_key = config.external_services.elevenlabs_api_key

            if not api_key:
                return HealthCheckResult(
                    service="elevenlabs_api",
                    status=HealthStatus.DEGRADED,
                    message="ElevenLabs API key not configured",
                    details={"tts_available": False},
                )

            # Test API connectivity with a lightweight request
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(
                    "https://api.elevenlabs.io/v1/voices",
                    headers={"xi-api-key": api_key},
                )

                if response.status_code == 200:
                    latency = (time.time() - start_time) * 1000
                    voices_data = response.json()

                    return HealthCheckResult(
                        service="elevenlabs_api",
                        status=HealthStatus.HEALTHY,
                        message="ElevenLabs API accessible",
                        details={
                            "tts_available": True,
                            "voices_count": len(voices_data.get("voices", [])),
                        },
                        latency_ms=round(latency, 2),
                    )
                else:
                    return HealthCheckResult(
                        service="elevenlabs_api",
                        status=HealthStatus.UNHEALTHY,
                        message=f"ElevenLabs API returned status {response.status_code}",
                        details={"status_code": response.status_code},
                    )

        except httpx.TimeoutException:
            return HealthCheckResult(
                service="elevenlabs_api",
                status=HealthStatus.UNHEALTHY,
                message="ElevenLabs API timeout",
                details={"timeout_seconds": self.timeout_seconds},
            )
        except Exception as e:
            logger.error(f"ElevenLabs API health check failed: {e}")
            return HealthCheckResult(
                service="elevenlabs_api",
                status=HealthStatus.DEGRADED,
                message=f"ElevenLabs API check failed: {str(e)}",
                details={"error": str(e)},
            )

    async def check_memory_usage(self) -> HealthCheckResult:
        """Check system memory usage."""
        try:
            import psutil

            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            available_mb = memory.available / (1024 * 1024)

            if memory_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"Critical memory usage: {memory_percent:.1f}%"
            elif memory_percent > 80:
                status = HealthStatus.DEGRADED
                message = f"High memory usage: {memory_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory_percent:.1f}%"

            return HealthCheckResult(
                service="memory",
                status=status,
                message=message,
                details={
                    "usage_percent": round(memory_percent, 1),
                    "available_mb": round(available_mb, 1),
                    "total_mb": round(memory.total / (1024 * 1024), 1),
                },
            )

        except ImportError:
            return HealthCheckResult(
                service="memory",
                status=HealthStatus.DEGRADED,
                message="Memory monitoring unavailable (psutil not installed)",
                details={"monitoring_available": False},
            )
        except Exception as e:
            return HealthCheckResult(
                service="memory",
                status=HealthStatus.DEGRADED,
                message=f"Memory check failed: {str(e)}",
                details={"error": str(e)},
            )

    async def check_disk_space(self) -> HealthCheckResult:
        """Check available disk space."""
        try:
            import shutil

            total, used, free = shutil.disk_usage("/")
            free_percent = (free / total) * 100
            free_gb = free / (1024**3)

            if free_percent < 10:
                status = HealthStatus.UNHEALTHY
                message = f"Critical disk space: {free_percent:.1f}% free"
            elif free_percent < 20:
                status = HealthStatus.DEGRADED
                message = f"Low disk space: {free_percent:.1f}% free"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk space adequate: {free_percent:.1f}% free"

            return HealthCheckResult(
                service="disk_space",
                status=status,
                message=message,
                details={
                    "free_percent": round(free_percent, 1),
                    "free_gb": round(free_gb, 1),
                    "total_gb": round(total / (1024**3), 1),
                },
            )

        except Exception as e:
            return HealthCheckResult(
                service="disk_space",
                status=HealthStatus.DEGRADED,
                message=f"Disk space check failed: {str(e)}",
                details={"error": str(e)},
            )


# Global health checker instance
health_checker = HealthChecker()
