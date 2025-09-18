"""
Analytics Utility for Meeting Minutes Generator.
Day 6 Implementation - Usage tracking, metrics, and insights.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class AnalyticsConfig:
    """Configuration for analytics tracking."""

    ANALYTICS_DIR = Path.home() / ".meeting_minutes_ai" / "analytics"
    USAGE_FILE = ANALYTICS_DIR / "usage.json"

    # Privacy settings
    TRACK_CONTENT = False  # Don't track actual meeting content
    TRACK_PERFORMANCE = True
    TRACK_USAGE_PATTERNS = True

class UsageTracker:
    """Tracks user interactions and system performance."""

    def __init__(self):
        """Initialize usage tracker."""
        self.config = AnalyticsConfig()
        self._ensure_analytics_dir()

    def _ensure_analytics_dir(self):
        """Ensure analytics directory exists."""
        self.config.ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

    def track_event(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Track a usage event."""
        try:
            if not self.config.TRACK_USAGE_PATTERNS:
                return

            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "data": self._anonymize_data(data or {})
            }

            # Load existing events
            events = self._load_usage_data()
            events.append(event)

            # Save updated events
            self._save_usage_data(events)

            logger.debug(f"Tracked event: {event_type}")

        except Exception as e:
            logger.error(f"Failed to track event: {e}")

    def track_session_start(self, session_info: Dict[str, Any] = None) -> str:
        """Track session start and return session ID."""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        session_data = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat()
        }

        self.track_event("session_start", session_data)
        return session_id

    def track_transcript_processing(self, processing_data: Dict[str, Any]) -> None:
        """Track transcript processing event."""
        anonymous_data = {
            "processing_time": processing_data.get("processing_time", 0),
            "transcript_length": processing_data.get("transcript_length", 0),
            "success": processing_data.get("success", False),
            "ai_enhanced": processing_data.get("ai_enhanced", False)
        }

        self.track_event("transcript_processed", anonymous_data)

    def track_export_event(self, export_data: Dict[str, Any]) -> None:
        """Track document export event."""
        anonymous_export = {
            "export_format": export_data.get("format", "Unknown"),
            "success": export_data.get("success", False)
        }

        self.track_event("document_exported", anonymous_export)

    def _anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from tracking data."""
        if not self.config.TRACK_CONTENT:
            sensitive_keys = ["transcript", "content", "text", "minutes", "summary"]
            return {k: v for k, v in data.items() if not any(sens in k.lower() for sens in sensitive_keys)}
        return data

    def _load_usage_data(self) -> List[Dict[str, Any]]:
        """Load existing usage data."""
        try:
            if self.config.USAGE_FILE.exists():
                with open(self.config.USAGE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load usage data: {e}")
        return []

    def _save_usage_data(self, events: List[Dict[str, Any]]) -> None:
        """Save usage data to file."""
        try:
            with open(self.config.USAGE_FILE, 'w') as f:
                json.dump(events, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save usage data: {e}")

class AnalyticsInsights:
    """Generate insights from usage data."""

    def __init__(self):
        self.tracker = UsageTracker()

    def get_usage_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get usage summary for specified period."""
        try:
            events = self.tracker._load_usage_data()

            cutoff_date = datetime.now() - timedelta(days=days)
            recent_events = [
                event for event in events
                if datetime.fromisoformat(event["timestamp"]) > cutoff_date
            ]

            return self._analyze_events(recent_events, days)

        except Exception as e:
            logger.error(f"Failed to generate usage summary: {e}")
            return self._get_empty_summary()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics."""
        try:
            events = self.tracker._load_usage_data()

            processing_events = [
                e for e in events 
                if e["event_type"] == "transcript_processed"
            ]

            if not processing_events:
                return self._get_empty_performance_metrics()

            processing_times = [
                e["data"].get("processing_time", 0) 
                for e in processing_events
                if e["data"].get("processing_time")
            ]

            success_rate = len([
                e for e in processing_events 
                if e["data"].get("success", False)
            ]) / len(processing_events)

            return {
                "total_processed": len(processing_events),
                "avg_processing_time": sum(processing_times) / len(processing_times) if processing_times else 0,
                "success_rate": success_rate * 100
            }

        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return self._get_empty_performance_metrics()

    def _analyze_events(self, events: List[Dict[str, Any]], days: int) -> Dict[str, Any]:
        """Analyze events and generate summary."""
        if not events:
            return self._get_empty_summary()

        event_counts = {}
        for event in events:
            event_type = event["event_type"]
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        return {
            "period_days": days,
            "total_events": len(events),
            "sessions": event_counts.get("session_start", 0),
            "transcripts_processed": event_counts.get("transcript_processed", 0),
            "documents_exported": event_counts.get("document_exported", 0)
        }

    def _get_empty_summary(self) -> Dict[str, Any]:
        """Get empty usage summary."""
        return {
            "period_days": 0,
            "total_events": 0,
            "sessions": 0,
            "transcripts_processed": 0,
            "documents_exported": 0
        }

    def _get_empty_performance_metrics(self) -> Dict[str, Any]:
        """Get empty performance metrics."""
        return {
            "total_processed": 0,
            "avg_processing_time": 0,
            "success_rate": 0
        }

# Global tracker instance
_tracker = None
_insights = None

def get_tracker() -> UsageTracker:
    """Get global usage tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker()
    return _tracker

def get_insights() -> AnalyticsInsights:
    """Get global insights generator instance."""
    global _insights
    if _insights is None:
        _insights = AnalyticsInsights()
    return _insights

def track_usage(event_type: str, data: Dict[str, Any] = None) -> None:
    """Convenience function to track usage events."""
    try:
        tracker = get_tracker()
        tracker.track_event(event_type, data)
    except Exception as e:
        logger.error(f"Failed to track usage: {e}")

def get_usage_stats(days: int = 7) -> Dict[str, Any]:
    """Convenience function to get usage statistics."""
    try:
        insights = get_insights()
        return insights.get_usage_summary(days)
    except Exception as e:
        logger.error(f"Failed to get usage stats: {e}")
        return {}

def test_analytics():
    """Test analytics functionality."""
    logger.info("Testing analytics functionality...")

    try:
        tracker = get_tracker()

        # Track test events
        tracker.track_session_start({"platform": "test"})
        tracker.track_transcript_processing({
            "processing_time": 2.5,
            "transcript_length": 1000,
            "success": True,
            "ai_enhanced": True
        })

        insights = get_insights()
        summary = insights.get_usage_summary(1)

        assert summary["sessions"] >= 1, "Session tracking failed"
        assert summary["transcripts_processed"] >= 1, "Processing tracking failed"

        logger.info("Analytics test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Analytics test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_analytics()
    print(f"Analytics Test: {'✅ PASS' if success else '❌ FAIL'}")
