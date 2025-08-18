"""
Production observability system for ImmoAssist multi-agent system.

Implements comprehensive monitoring, metrics collection, error tracking,
and performance monitoring following ADK Observability patterns and
Google Cloud Monitoring best practices.
"""

import time
import functools
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import asyncio

from .logging_config import get_logger

logger = get_logger("observability")


class MetricType(Enum):
    """Types of metrics to collect."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Represents a metric measurement."""

    name: str
    value: float
    labels: Dict[str, str]
    timestamp: datetime
    metric_type: MetricType

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary for serialization."""
        return {
            "name": self.name,
            "value": self.value,
            "labels": self.labels,
            "timestamp": self.timestamp.isoformat(),
            "type": self.metric_type.value,
        }


@dataclass
class PerformanceMetric:
    """Performance measurement for agent operations."""

    operation: str
    agent_name: str
    duration_ms: float
    success: bool
    error_type: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


@dataclass
class UserInteraction:
    """User interaction tracking data."""

    user_id: str
    session_id: str
    interaction_type: str
    agent_name: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost_estimate: Optional[float] = None
    satisfaction_score: Optional[float] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


@dataclass
class ErrorEvent:
    """Error event tracking."""

    error_type: str
    error_message: str
    agent_name: Optional[str]
    operation: str
    stack_trace: Optional[str]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    severity: AlertSeverity = AlertSeverity.ERROR
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class MetricsCollector:
    """Collects and aggregates metrics for Cloud Monitoring."""

    def __init__(self):
        self._metrics: List[Metric] = []
        self._performance_metrics: List[PerformanceMetric] = []
        self._user_interactions: List[UserInteraction] = []
        self._error_events: List[ErrorEvent] = []
        self._lock = threading.Lock()

        # Performance counters
        self._operation_counts: Dict[str, int] = {}
        self._operation_durations: Dict[str, List[float]] = {}
        self._error_counts: Dict[str, int] = {}

    def record_metric(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        metric_type: MetricType = MetricType.GAUGE,
    ) -> None:
        """Record a custom metric."""
        metric = Metric(
            name=name,
            value=value,
            labels=labels or {},
            timestamp=datetime.now(timezone.utc),
            metric_type=metric_type,
        )

        with self._lock:
            self._metrics.append(metric)

        logger.debug(f"Recorded metric: {name}={value}, labels={labels}")

    def record_performance(self, performance_metric: PerformanceMetric) -> None:
        """Record performance measurement."""
        with self._lock:
            self._performance_metrics.append(performance_metric)

            # Update counters
            key = f"{performance_metric.agent_name}.{performance_metric.operation}"
            self._operation_counts[key] = self._operation_counts.get(key, 0) + 1

            if key not in self._operation_durations:
                self._operation_durations[key] = []
            self._operation_durations[key].append(performance_metric.duration_ms)

            if not performance_metric.success:
                error_key = f"{key}.{performance_metric.error_type or 'unknown'}"
                self._error_counts[error_key] = self._error_counts.get(error_key, 0) + 1

        logger.info(
            f"Performance: {performance_metric.agent_name}.{performance_metric.operation} "
            f"took {performance_metric.duration_ms:.2f}ms, success={performance_metric.success}"
        )

    def record_user_interaction(self, interaction: UserInteraction) -> None:
        """Record user interaction for analytics."""
        with self._lock:
            self._user_interactions.append(interaction)

        # Record as metric for Cloud Monitoring
        self.record_metric(
            "user_interactions_total",
            1,
            labels={
                "interaction_type": interaction.interaction_type,
                "agent_name": interaction.agent_name,
            },
            metric_type=MetricType.COUNTER,
        )

        if interaction.input_tokens:
            self.record_metric(
                "input_tokens_total",
                interaction.input_tokens,
                labels={"agent_name": interaction.agent_name},
                metric_type=MetricType.COUNTER,
            )

        if interaction.output_tokens:
            self.record_metric(
                "output_tokens_total",
                interaction.output_tokens,
                labels={"agent_name": interaction.agent_name},
                metric_type=MetricType.COUNTER,
            )

        logger.info(
            f"User interaction recorded: {interaction.interaction_type} with {interaction.agent_name}"
        )

    def record_error(self, error_event: ErrorEvent) -> None:
        """Record error event for tracking and alerting."""
        with self._lock:
            self._error_events.append(error_event)

        # Record as metric
        self.record_metric(
            "errors_total",
            1,
            labels={
                "error_type": error_event.error_type,
                "agent_name": error_event.agent_name or "unknown",
                "severity": error_event.severity.value,
            },
            metric_type=MetricType.COUNTER,
        )

        # Log based on severity
        if error_event.severity == AlertSeverity.CRITICAL:
            logger.critical(
                f"CRITICAL ERROR: {error_event.error_message}",
                extra={
                    "agent_name": error_event.agent_name,
                    "operation": error_event.operation,
                    "error_type": error_event.error_type,
                    "stack_trace": error_event.stack_trace,
                },
            )
        elif error_event.severity == AlertSeverity.ERROR:
            logger.error(
                f"ERROR: {error_event.error_message}",
                extra={
                    "agent_name": error_event.agent_name,
                    "operation": error_event.operation,
                    "error_type": error_event.error_type,
                },
            )
        else:
            logger.warning(f"Warning: {error_event.error_message}")

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        with self._lock:
            return {
                "total_metrics": len(self._metrics),
                "total_performance_records": len(self._performance_metrics),
                "total_user_interactions": len(self._user_interactions),
                "total_errors": len(self._error_events),
                "operation_counts": dict(self._operation_counts),
                "error_counts": dict(self._error_counts),
                "avg_operation_durations": {
                    op: sum(durations) / len(durations)
                    for op, durations in self._operation_durations.items()
                },
            }

    def export_metrics_for_cloud_monitoring(self) -> List[Dict[str, Any]]:
        """Export metrics in Cloud Monitoring format."""
        with self._lock:
            return [
                metric.to_dict() for metric in self._metrics[-100:]
            ]  # Last 100 metrics

    def clear_old_metrics(self, max_age_hours: int = 24) -> None:
        """Clear metrics older than specified hours."""
        cutoff = datetime.now(timezone.utc).timestamp() - (max_age_hours * 3600)

        with self._lock:
            self._metrics = [
                m for m in self._metrics if m.timestamp.timestamp() > cutoff
            ]
            self._performance_metrics = [
                m for m in self._performance_metrics if m.timestamp.timestamp() > cutoff
            ]
            self._user_interactions = [
                m for m in self._user_interactions if m.timestamp.timestamp() > cutoff
            ]
            self._error_events = [
                m for m in self._error_events if m.timestamp.timestamp() > cutoff
            ]


class ObservabilityDecorator:
    """Decorator for monitoring agent operations."""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector

    def monitor_agent_operation(
        self, agent_name: str, operation_name: Optional[str] = None
    ):
        """Decorator to monitor agent operation performance."""

        def decorator(func: Callable) -> Callable:
            op_name = operation_name or func.__name__

            if asyncio.iscoroutinefunction(func):

                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    start_time = time.time()
                    success = False
                    error_type = None

                    try:
                        result = await func(*args, **kwargs)
                        success = True
                        return result
                    except Exception as e:
                        error_type = type(e).__name__

                        # Record error event
                        self.collector.record_error(
                            ErrorEvent(
                                error_type=error_type,
                                error_message=str(e),
                                agent_name=agent_name,
                                operation=op_name,
                                stack_trace=traceback.format_exc(),
                                severity=AlertSeverity.ERROR,
                            )
                        )
                        raise
                    finally:
                        duration_ms = (time.time() - start_time) * 1000

                        # Record performance
                        self.collector.record_performance(
                            PerformanceMetric(
                                operation=op_name,
                                agent_name=agent_name,
                                duration_ms=duration_ms,
                                success=success,
                                error_type=error_type,
                            )
                        )

                return async_wrapper
            else:

                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    start_time = time.time()
                    success = False
                    error_type = None

                    try:
                        result = func(*args, **kwargs)
                        success = True
                        return result
                    except Exception as e:
                        error_type = type(e).__name__

                        # Record error event
                        self.collector.record_error(
                            ErrorEvent(
                                error_type=error_type,
                                error_message=str(e),
                                agent_name=agent_name,
                                operation=op_name,
                                stack_trace=traceback.format_exc(),
                                severity=AlertSeverity.ERROR,
                            )
                        )
                        raise
                    finally:
                        duration_ms = (time.time() - start_time) * 1000

                        # Record performance
                        self.collector.record_performance(
                            PerformanceMetric(
                                operation=op_name,
                                agent_name=agent_name,
                                duration_ms=duration_ms,
                                success=success,
                                error_type=error_type,
                            )
                        )

                return sync_wrapper

        return decorator


class AlertManager:
    """Manages alerts and notifications for production issues."""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.alert_thresholds = {
            "error_rate_threshold": 0.05,  # 5% error rate
            "response_time_threshold": 10000,  # 10 seconds
            "memory_threshold": 0.8,  # 80% memory usage
        }

    def check_error_rate_alert(
        self, time_window_minutes: int = 5
    ) -> Optional[Dict[str, Any]]:
        """Check if error rate exceeds threshold."""
        # Implementation would check recent error rate
        # For now, return None (no alert)
        return None

    def check_performance_alert(
        self, time_window_minutes: int = 5
    ) -> Optional[Dict[str, Any]]:
        """Check for performance degradation."""
        # Implementation would check recent response times
        return None

    def should_trigger_alert(self, metric_name: str, value: float) -> bool:
        """Determine if metric value should trigger an alert."""
        if (
            metric_name == "error_rate"
            and value > self.alert_thresholds["error_rate_threshold"]
        ):
            return True
        if (
            metric_name == "response_time_ms"
            and value > self.alert_thresholds["response_time_threshold"]
        ):
            return True
        if (
            metric_name == "memory_usage"
            and value > self.alert_thresholds["memory_threshold"]
        ):
            return True
        return False


# Global observability instances
metrics_collector = MetricsCollector()
observability_decorator = ObservabilityDecorator(metrics_collector)
alert_manager = AlertManager(metrics_collector)

# Convenience decorators
monitor_agent = observability_decorator.monitor_agent_operation


def track_user_interaction(
    user_id: str, session_id: str, interaction_type: str, agent_name: str, **kwargs
) -> None:
    """Convenience function to track user interactions."""
    interaction = UserInteraction(
        user_id=user_id,
        session_id=session_id,
        interaction_type=interaction_type,
        agent_name=agent_name,
        **kwargs,
    )
    metrics_collector.record_user_interaction(interaction)


def track_error(
    error: Exception,
    agent_name: str,
    operation: str,
    severity: AlertSeverity = AlertSeverity.ERROR,
    **kwargs,
) -> None:
    """Convenience function to track errors."""
    error_event = ErrorEvent(
        error_type=type(error).__name__,
        error_message=str(error),
        agent_name=agent_name,
        operation=operation,
        stack_trace=traceback.format_exc(),
        severity=severity,
        **kwargs,
    )
    metrics_collector.record_error(error_event)
