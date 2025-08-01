"""
Tests for A2A telemetry and monitoring system
"""

import pytest
import asyncio
import time
import tempfile
import json
from unittest.mock import MagicMock
from pathlib import Path

from polyhegel.telemetry import (
    MetricType,
    EventType,
    TelemetryEvent,
    MetricValue,
    TelemetryCollector,
    A2AMonitoringMiddleware,
    TelemetryExporter,
    get_telemetry_collector,
    setup_telemetry_for_agent,
    time_operation,
    timed_operation,
)


class TestTelemetryEvent:
    """Test TelemetryEvent data structure"""

    def test_event_creation(self):
        """Test creating telemetry events"""
        event = TelemetryEvent(
            event_type=EventType.THEME_GENERATED,
            timestamp=time.time(),
            agent_id="test-agent",
            data={"theme_count": 3},
            duration_ms=150.5,
            success=True,
        )

        assert event.event_type == EventType.THEME_GENERATED
        assert event.agent_id == "test-agent"
        assert event.data["theme_count"] == 3
        assert event.duration_ms == 150.5
        assert event.success is True
        assert event.error is None

    def test_event_serialization(self):
        """Test event to_dict serialization"""
        event = TelemetryEvent(
            event_type=EventType.REQUEST_START,
            timestamp=1234567890.0,
            agent_id="test-agent",
            data={"operation": "test"},
            success=False,
            error="Test error",
        )

        event_dict = event.to_dict()

        assert event_dict["event_type"] == "request_start"
        assert event_dict["timestamp"] == 1234567890.0
        assert event_dict["agent_id"] == "test-agent"
        assert event_dict["data"]["operation"] == "test"
        assert event_dict["success"] is False
        assert event_dict["error"] == "Test error"


class TestMetricValue:
    """Test MetricValue data structure"""

    def test_metric_creation(self):
        """Test creating metric values"""
        metric = MetricValue(
            name="request_duration_ms",
            value=125.7,
            metric_type=MetricType.HISTOGRAM,
            timestamp=time.time(),
            tags={"method": "POST", "status": "200"},
        )

        assert metric.name == "request_duration_ms"
        assert metric.value == 125.7
        assert metric.metric_type == MetricType.HISTOGRAM
        assert metric.tags["method"] == "POST"

    def test_metric_serialization(self):
        """Test metric to_dict serialization"""
        metric = MetricValue(
            name="test_counter",
            value=42.0,
            metric_type=MetricType.COUNTER,
            timestamp=1234567890.0,
            tags={"env": "test"},
        )

        metric_dict = metric.to_dict()

        assert metric_dict["name"] == "test_counter"
        assert metric_dict["value"] == 42.0
        assert metric_dict["type"] == "counter"
        assert metric_dict["timestamp"] == 1234567890.0
        assert metric_dict["tags"]["env"] == "test"


class TestTelemetryCollector:
    """Test TelemetryCollector functionality"""

    def test_collector_creation(self):
        """Test creating telemetry collector"""
        collector = TelemetryCollector("test-agent", max_events=100, max_metrics=50)

        assert collector.agent_id == "test-agent"
        assert collector.max_events == 100
        assert collector.max_metrics == 50
        assert len(collector._events) == 0
        assert len(collector._metrics) == 0

    def test_record_event(self):
        """Test recording events"""
        collector = TelemetryCollector("test-agent")

        collector.record_event(EventType.THEME_GENERATED, data={"theme_count": 3}, duration_ms=100.0, success=True)

        events = collector.get_events()
        assert len(events) == 1

        event = events[0]
        assert event.event_type == EventType.THEME_GENERATED
        assert event.agent_id == "test-agent"
        assert event.data["theme_count"] == 3
        assert event.duration_ms == 100.0
        assert event.success is True

    def test_record_metric(self):
        """Test recording metrics"""
        collector = TelemetryCollector("test-agent")

        collector.record_metric("test_metric", 42.5, MetricType.GAUGE, tags={"env": "test"})

        metrics = collector.get_metrics()
        assert len(metrics) == 1

        metric = metrics[0]
        assert metric.name == "test_metric"
        assert metric.value == 42.5
        assert metric.metric_type == MetricType.GAUGE
        assert metric.tags["env"] == "test"

    def test_increment_counter(self):
        """Test counter increment functionality"""
        collector = TelemetryCollector("test-agent")

        collector.increment_counter("requests_total", 1.0)
        collector.increment_counter("requests_total", 2.0)
        collector.increment_counter("requests_total", 1.5)

        # Check internal counter state
        summary = collector.get_summary()
        assert summary["counters"]["requests_total"] == 4.5

    def test_set_gauge(self):
        """Test gauge setting functionality"""
        collector = TelemetryCollector("test-agent")

        collector.set_gauge("active_connections", 10.0)
        collector.set_gauge("active_connections", 15.0)
        collector.set_gauge("memory_usage", 75.5)

        # Check internal gauge state
        summary = collector.get_summary()
        assert summary["gauges"]["active_connections"] == 15.0
        assert summary["gauges"]["memory_usage"] == 75.5

    def test_timer_functionality(self):
        """Test timer start/end functionality"""
        collector = TelemetryCollector("test-agent")

        timer_id = collector.start_timer("test_operation")
        assert timer_id.startswith("test_operation_")

        # Simulate some work
        time.sleep(0.01)

        duration = collector.end_timer(timer_id)
        assert duration is not None
        assert duration > 0

        # Check that timer metric was recorded
        metrics = collector.get_metrics(metric_name="test_operation")
        assert len(metrics) == 1
        assert metrics[0].metric_type == MetricType.TIMER

    @pytest.mark.asyncio
    async def test_timer_context_manager(self):
        """Test async timer context manager"""
        collector = TelemetryCollector("test-agent")

        async with collector.timer("async_operation"):
            await asyncio.sleep(0.01)

        # Check that timer metric was recorded
        metrics = collector.get_metrics(metric_name="async_operation")
        assert len(metrics) == 1
        assert metrics[0].metric_type == MetricType.TIMER
        assert metrics[0].value > 0

    def test_event_handlers(self):
        """Test event handler functionality"""
        collector = TelemetryCollector("test-agent")
        handled_events = []

        def event_handler(event):
            handled_events.append(event)

        collector.add_event_handler(event_handler)

        collector.record_event(EventType.REQUEST_START, data={"test": "data"})

        assert len(handled_events) == 1
        assert handled_events[0].event_type == EventType.REQUEST_START
        assert handled_events[0].data["test"] == "data"

    def test_metric_handlers(self):
        """Test metric handler functionality"""
        collector = TelemetryCollector("test-agent")
        handled_metrics = []

        def metric_handler(metric):
            handled_metrics.append(metric)

        collector.add_metric_handler(metric_handler)

        collector.record_metric("test_metric", 100.0, MetricType.COUNTER)

        assert len(handled_metrics) == 1
        assert handled_metrics[0].name == "test_metric"
        assert handled_metrics[0].value == 100.0

    def test_get_summary(self):
        """Test getting telemetry summary"""
        collector = TelemetryCollector("test-agent")

        # Add some data
        collector.record_event(EventType.REQUEST_START, success=True)
        collector.record_event(EventType.REQUEST_END, success=True)
        collector.record_event(EventType.ERROR_OCCURRED, success=False)
        collector.increment_counter("test_counter", 5.0)
        collector.set_gauge("test_gauge", 42.0)

        summary = collector.get_summary()

        assert summary["agent_id"] == "test-agent"
        assert summary["total_events"] == 3
        assert summary["error_count"] == 1
        assert summary["counters"]["test_counter"] == 5.0
        assert summary["gauges"]["test_gauge"] == 42.0
        assert "request_start" in summary["recent_event_counts"]


class TestTelemetryExporter:
    """Test TelemetryExporter functionality"""

    def test_export_to_json_file(self):
        """Test exporting telemetry to JSON file"""
        collector = TelemetryCollector("test-agent")
        exporter = TelemetryExporter(collector)

        # Add some test data
        collector.record_event(EventType.THEME_GENERATED, data={"count": 3})
        collector.record_metric("test_metric", 100.0, MetricType.COUNTER)

        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            exporter.export_to_json_file(temp_path)

            # Read and verify exported data
            with open(temp_path, "r") as f:
                exported_data = json.load(f)

            assert exported_data["agent_id"] == "test-agent"
            assert len(exported_data["events"]) == 1
            assert len(exported_data["metrics"]) == 1
            assert exported_data["events"][0]["event_type"] == "theme_generated"
            assert exported_data["metrics"][0]["name"] == "test_metric"

        finally:
            Path(temp_path).unlink()

    def test_export_to_stdout(self, capsys):
        """Test exporting summary to stdout"""
        collector = TelemetryCollector("test-agent")
        exporter = TelemetryExporter(collector)

        # Add some test data
        collector.record_event(EventType.REQUEST_START)
        collector.increment_counter("requests_total", 1.0)

        exporter.export_to_stdout()

        captured = capsys.readouterr()
        assert "Telemetry Summary for test-agent" in captured.out
        assert "Total Events: 1" in captured.out
        assert "requests_total" in captured.out


class TestA2AMonitoringMiddleware:
    """Test A2A monitoring middleware"""

    @pytest.mark.asyncio
    async def test_middleware_successful_request(self):
        """Test middleware for successful request"""
        collector = TelemetryCollector("test-agent")
        middleware = A2AMonitoringMiddleware(collector)

        # Mock request and response
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url = "http://test.com/api"
        mock_request.client.host = "127.0.0.1"

        mock_response = MagicMock()
        mock_response.status_code = 200

        async def mock_call_next(request):
            await asyncio.sleep(0.01)  # Simulate processing time
            return mock_response

        # Process request through middleware
        response = await middleware(mock_request, mock_call_next)

        assert response.status_code == 200

        # Check recorded events
        events = collector.get_events()
        assert len(events) == 2  # START and END

        start_event = events[0]
        assert start_event.event_type == EventType.REQUEST_START
        assert start_event.data["method"] == "GET"

        end_event = events[1]
        assert end_event.event_type == EventType.REQUEST_END
        assert end_event.success is True
        assert end_event.duration_ms > 0

    @pytest.mark.asyncio
    async def test_middleware_error_request(self):
        """Test middleware for error request"""
        collector = TelemetryCollector("test-agent")
        middleware = A2AMonitoringMiddleware(collector)

        # Mock request
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url = "http://test.com/api"
        mock_request.client.host = "127.0.0.1"

        async def mock_call_next_error(request):
            await asyncio.sleep(0.01)
            raise ValueError("Test error")

        # Process request through middleware
        with pytest.raises(ValueError):
            await middleware(mock_request, mock_call_next_error)

        # Check recorded events
        events = collector.get_events()
        assert len(events) == 2  # START and ERROR

        error_event = events[1]
        assert error_event.event_type == EventType.ERROR_OCCURRED
        assert error_event.success is False
        assert error_event.error == "Test error"


class TestTelemetryHelpers:
    """Test telemetry helper functions"""

    def test_get_telemetry_collector(self):
        """Test getting telemetry collector"""
        collector1 = get_telemetry_collector("agent-1")
        collector2 = get_telemetry_collector("agent-2")
        collector1_again = get_telemetry_collector("agent-1")

        assert collector1.agent_id == "agent-1"
        assert collector2.agent_id == "agent-2"
        assert collector1 is collector1_again  # Same instance
        assert collector1 is not collector2  # Different instances

    def test_setup_telemetry_for_agent(self):
        """Test setting up telemetry for agent"""
        collector = setup_telemetry_for_agent("test-agent")

        assert collector.agent_id == "test-agent"

        # Check that agent start event was recorded
        events = collector.get_events()
        assert len(events) == 1
        assert events[0].event_type == EventType.AGENT_START

    @pytest.mark.asyncio
    async def test_time_operation_context_manager(self):
        """Test time_operation context manager"""
        collector = TelemetryCollector("test-agent")

        async with time_operation(collector, "test_operation", env="test"):
            await asyncio.sleep(0.01)

        # Check that timer metric was recorded
        metrics = collector.get_metrics(metric_name="test_operation_duration_ms")
        assert len(metrics) == 1
        assert metrics[0].metric_type == MetricType.TIMER
        assert metrics[0].tags["env"] == "test"

    @pytest.mark.asyncio
    async def test_timed_operation_decorator(self):
        """Test timed_operation decorator"""
        collector = TelemetryCollector("test-agent")

        @timed_operation("decorated_operation")
        async def test_function(self):
            await asyncio.sleep(0.01)
            return "result"

        # Mock object with telemetry collector
        mock_obj = MagicMock()
        mock_obj._telemetry_collector = collector

        result = await test_function(mock_obj)
        assert result == "result"

        # Check that timer metric was recorded
        metrics = collector.get_metrics(metric_name="decorated_operation_duration_ms")
        assert len(metrics) == 1
        assert metrics[0].metric_type == MetricType.TIMER


if __name__ == "__main__":
    pytest.main([__file__])
