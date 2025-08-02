"""
A2A Telemetry and Monitoring Integration

Provides comprehensive telemetry, metrics collection, and monitoring
for polyhegel A2A agent operations.
"""

import asyncio
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json
from collections import defaultdict, deque
import threading
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics collected"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class EventType(Enum):
    """Types of telemetry events"""

    AGENT_START = "agent_start"
    AGENT_STOP = "agent_stop"
    REQUEST_START = "request_start"
    REQUEST_END = "request_end"
    THEME_GENERATED = "theme_generated"
    STRATEGY_DEVELOPED = "strategy_developed"
    ERROR_OCCURRED = "error_occurred"
    AUTHENTICATION_SUCCESS = "auth_success"
    AUTHENTICATION_FAILURE = "auth_failure"
    RATE_LIMIT_HIT = "rate_limit_hit"


@dataclass
class TelemetryEvent:
    """A single telemetry event"""

    event_type: EventType
    timestamp: float
    agent_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "agent_id": self.agent_id,
            "data": self.data,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class MetricValue:
    """A metric value with metadata"""

    name: str
    value: float
    metric_type: MetricType
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "value": self.value,
            "type": self.metric_type.value,
            "timestamp": self.timestamp,
            "tags": self.tags,
        }


class TelemetryCollector:
    """Collects and manages telemetry data"""

    def __init__(self, agent_id: str, max_events: int = 10000, max_metrics: int = 1000):
        self.agent_id = agent_id
        self.max_events = max_events
        self.max_metrics = max_metrics

        # Storage
        self._events: deque = deque(maxlen=max_events)
        self._metrics: deque = deque(maxlen=max_metrics)
        self._active_timers: Dict[str, float] = {}
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}

        # Thread safety
        self._lock = threading.RLock()

        # Event handlers
        self._event_handlers: List[Callable[[TelemetryEvent], None]] = []
        self._metric_handlers: List[Callable[[MetricValue], None]] = []

    def add_event_handler(self, handler: Callable[[TelemetryEvent], None]):
        """Add event handler for real-time processing"""
        self._event_handlers.append(handler)

    def add_metric_handler(self, handler: Callable[[MetricValue], None]):
        """Add metric handler for real-time processing"""
        self._metric_handlers.append(handler)

    def record_event(
        self,
        event_type: EventType,
        data: Dict[str, Any] = None,
        duration_ms: Optional[float] = None,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """Record a telemetry event"""
        event = TelemetryEvent(
            event_type=event_type,
            timestamp=time.time(),
            agent_id=self.agent_id,
            data=data or {},
            duration_ms=duration_ms,
            success=success,
            error=error,
        )

        with self._lock:
            self._events.append(event)

        # Notify handlers
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}")

    def record_metric(self, name: str, value: float, metric_type: MetricType, tags: Dict[str, str] = None):
        """Record a metric value"""
        metric = MetricValue(name=name, value=value, metric_type=metric_type, timestamp=time.time(), tags=tags or {})

        with self._lock:
            self._metrics.append(metric)

            # Update internal state
            if metric_type == MetricType.COUNTER:
                self._counters[name] += value
            elif metric_type == MetricType.GAUGE:
                self._gauges[name] = value

        # Notify handlers
        for handler in self._metric_handlers:
            try:
                handler(metric)
            except Exception as e:
                logger.error(f"Metric handler error: {e}")

    def increment_counter(self, name: str, value: float = 1.0, tags: Dict[str, str] = None):
        """Increment a counter metric"""
        self.record_metric(name, value, MetricType.COUNTER, tags)

    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric value"""
        self.record_metric(name, value, MetricType.GAUGE, tags)

    def start_timer(self, name: str) -> str:
        """Start a timer and return timer ID"""
        timer_id = f"{name}_{int(time.time() * 1000000)}"
        self._active_timers[timer_id] = time.time()
        return timer_id

    def end_timer(self, timer_id: str, tags: Dict[str, str] = None) -> Optional[float]:
        """End timer and record duration"""
        start_time = self._active_timers.pop(timer_id, None)
        if start_time is None:
            return None

        duration_ms = (time.time() - start_time) * 1000
        # Extract name by removing the timestamp suffix (last underscore and digits)
        name = timer_id.rsplit("_", 1)[0]
        self.record_metric(name, duration_ms, MetricType.TIMER, tags)
        return duration_ms

    @asynccontextmanager
    async def timer(self, name: str, tags: Dict[str, str] = None):
        """Context manager for timing operations"""
        timer_id = self.start_timer(name)
        try:
            yield
        finally:
            self.end_timer(timer_id, tags)

    def get_events(self, limit: int = None, event_type: EventType = None) -> List[TelemetryEvent]:
        """Get recorded events"""
        with self._lock:
            events = list(self._events)

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if limit:
            events = events[-limit:]

        return events

    def get_metrics(self, limit: int = None, metric_name: str = None) -> List[MetricValue]:
        """Get recorded metrics"""
        with self._lock:
            metrics = list(self._metrics)

        if metric_name:
            metrics = [m for m in metrics if m.name == metric_name]

        if limit:
            metrics = metrics[-limit:]

        return metrics

    def get_summary(self) -> Dict[str, Any]:
        """Get telemetry summary"""
        with self._lock:
            recent_events = list(self._events)[-100:]  # Last 100 events

            # Event counts by type
            event_counts: Dict[str, int] = defaultdict(int)
            error_count = 0

            for event in recent_events:
                event_counts[event.event_type.value] += 1
                if not event.success:
                    error_count += 1

            # Current counter and gauge values
            current_counters = dict(self._counters)
            current_gauges = dict(self._gauges)

        return {
            "agent_id": self.agent_id,
            "total_events": len(self._events),
            "total_metrics": len(self._metrics),
            "recent_event_counts": dict(event_counts),
            "error_count": error_count,
            "counters": current_counters,
            "gauges": current_gauges,
            "timestamp": time.time(),
        }


class A2AMonitoringMiddleware:
    """FastAPI middleware for A2A monitoring"""

    def __init__(self, collector: TelemetryCollector):
        self.collector = collector

    async def __call__(self, request, call_next):
        """Process request with monitoring"""
        start_time = time.time()

        # Record request start
        self.collector.record_event(
            EventType.REQUEST_START,
            data={
                "method": request.method,
                "url": str(request.url),
                "client": request.client.host if request.client else None,
            },
        )

        # Increment request counter
        self.collector.increment_counter("http_requests_total", tags={"method": request.method})

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Record successful request
            self.collector.record_event(
                EventType.REQUEST_END,
                data={"method": request.method, "url": str(request.url), "status_code": response.status_code},
                duration_ms=duration_ms,
                success=response.status_code < 400,
            )

            # Record response metrics
            self.collector.record_metric(
                "http_request_duration_ms",
                duration_ms,
                MetricType.HISTOGRAM,
                tags={"method": request.method, "status_code": str(response.status_code)},
            )

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Record error
            self.collector.record_event(
                EventType.ERROR_OCCURRED,
                data={"method": request.method, "url": str(request.url), "error_type": type(e).__name__},
                duration_ms=duration_ms,
                success=False,
                error=str(e),
            )

            # Increment error counter
            self.collector.increment_counter(
                "http_errors_total", tags={"method": request.method, "error_type": type(e).__name__}
            )

            raise


class TelemetryExporter:
    """Exports telemetry data to external systems"""

    def __init__(self, collector: TelemetryCollector):
        self.collector = collector
        self._exporters: List[Callable[[List[TelemetryEvent], List[MetricValue]], None]] = []

    def add_exporter(self, exporter: Callable[[List[TelemetryEvent], List[MetricValue]], None]):
        """Add data exporter"""
        self._exporters.append(exporter)

    def export_to_json_file(self, filepath: str):
        """Export data to JSON file"""
        events = self.collector.get_events()
        metrics = self.collector.get_metrics()

        data = {
            "agent_id": self.collector.agent_id,
            "timestamp": time.time(),
            "events": [e.to_dict() for e in events],
            "metrics": [m.to_dict() for m in metrics],
            "summary": self.collector.get_summary(),
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported telemetry data to {filepath}")

    def export_to_stdout(self):
        """Export summary to stdout"""
        summary = self.collector.get_summary()
        print(f"=== Telemetry Summary for {summary['agent_id']} ===")
        print(f"Total Events: {summary['total_events']}")
        print(f"Total Metrics: {summary['total_metrics']}")
        print(f"Error Count: {summary['error_count']}")
        print(f"Event Counts: {summary['recent_event_counts']}")
        print(f"Counters: {summary['counters']}")
        print(f"Gauges: {summary['gauges']}")
        print("=" * 50)


# Global telemetry collector instances
_collectors: Dict[str, TelemetryCollector] = {}
_collector_lock = threading.Lock()


def get_telemetry_collector(agent_id: str) -> TelemetryCollector:
    """Get or create telemetry collector for agent"""
    with _collector_lock:
        if agent_id not in _collectors:
            _collectors[agent_id] = TelemetryCollector(agent_id)
        return _collectors[agent_id]


def setup_telemetry_for_agent(agent_id: str) -> TelemetryCollector:
    """Setup telemetry collection for an agent"""
    collector = get_telemetry_collector(agent_id)

    # Record agent start
    collector.record_event(EventType.AGENT_START, data={"startup_time": time.time()})

    logger.info(f"Telemetry initialized for agent {agent_id}")
    return collector


# Context manager for operation timing
@asynccontextmanager
async def time_operation(collector: TelemetryCollector, operation_name: str, **tags):
    """Time an operation and record metrics"""
    async with collector.timer(f"{operation_name}_duration_ms", tags):
        yield


# Decorator for automatic method timing
def timed_operation(operation_name: str = None):
    """Decorator to automatically time and record method execution"""

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            # Try to get collector from self if available
            collector = None
            if args and hasattr(args[0], "_telemetry_collector"):
                collector = args[0]._telemetry_collector
            elif args and hasattr(args[0], "agent_id"):
                collector = get_telemetry_collector(args[0].agent_id)

            if collector:
                name = operation_name or func.__name__
                async with time_operation(collector, name):
                    return await func(*args, **kwargs)
            else:
                return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            # For sync functions, just call directly
            return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
