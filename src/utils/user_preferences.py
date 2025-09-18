"""
User Preferences Utility for Meeting Minutes Generator.
Day 6 Implementation - User customization and settings management.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class PreferencesConfig:
    """Configuration for user preferences."""

    PREFERENCES_DIR = Path.home() / ".meeting_minutes_ai" / "preferences"
    PREFERENCES_FILE = PREFERENCES_DIR / "user_preferences.json"

    DEFAULT_PREFERENCES = {
        "theme": "Professional",
        "default_export_format": "Markdown",
        "analytics_enabled": True,
        "auto_save_results": True,
        "show_advanced_options": False,
        "processing_timeout": 300,
        "quality_threshold": 0.6,
        "preferences_version": "1.0",
        "last_updated": None
    }

class UserPreferencesManager:
    """Manages user preferences and customization settings."""

    def __init__(self):
        self.config = PreferencesConfig()
        self._ensure_preferences_dir()
        self._current_preferences = None

    def _ensure_preferences_dir(self):
        """Ensure preferences directory exists."""
        self.config.PREFERENCES_DIR.mkdir(parents=True, exist_ok=True)

    def load_preferences(self) -> Dict[str, Any]:
        """Load user preferences from storage."""
        try:
            if self.config.PREFERENCES_FILE.exists():
                with open(self.config.PREFERENCES_FILE, 'r') as f:
                    stored_prefs = json.load(f)

                preferences = self.config.DEFAULT_PREFERENCES.copy()
                preferences.update(stored_prefs)
                preferences = self._validate_preferences(preferences)

                self._current_preferences = preferences
                logger.debug("User preferences loaded successfully")
                return preferences

        except Exception as e:
            logger.error(f"Failed to load user preferences: {e}")

        default_prefs = self.config.DEFAULT_PREFERENCES.copy()
        default_prefs["last_updated"] = datetime.now().isoformat()

        self._current_preferences = default_prefs
        return default_prefs

    def save_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Save user preferences to storage."""
        try:
            validated_prefs = self._validate_preferences(preferences)
            validated_prefs["last_updated"] = datetime.now().isoformat()

            with open(self.config.PREFERENCES_FILE, 'w') as f:
                json.dump(validated_prefs, f, indent=2)

            self._current_preferences = validated_prefs
            logger.info("User preferences saved successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to save user preferences: {e}")
            return False

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a specific preference value."""
        if self._current_preferences is None:
            self._current_preferences = self.load_preferences()

        try:
            if '.' in key:
                keys = key.split('.')
                value = self._current_preferences
                for k in keys:
                    value = value.get(k, {})
                return value if value != {} else default
            else:
                return self._current_preferences.get(key, default)

        except Exception as e:
            logger.error(f"Failed to get preference {key}: {e}")
            return default

    def set_preference(self, key: str, value: Any, save_immediately: bool = True) -> bool:
        """Set a specific preference value."""
        try:
            if self._current_preferences is None:
                self._current_preferences = self.load_preferences()

            if '.' in key:
                keys = key.split('.')
                target = self._current_preferences
                for k in keys[:-1]:
                    if k not in target:
                        target[k] = {}
                    target = target[k]
                target[keys[-1]] = value
            else:
                self._current_preferences[key] = value

            if save_immediately:
                return self.save_preferences(self._current_preferences)

            return True

        except Exception as e:
            logger.error(f"Failed to set preference {key}: {e}")
            return False

    def _validate_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize preferences."""
        validated = preferences.copy()

        # Validate theme options
        valid_themes = ["Professional", "Modern", "Classic", "Dark", "Light"]
        if validated.get("theme") not in valid_themes:
            validated["theme"] = "Professional"

        # Validate export formats
        valid_formats = ["Markdown", "PDF", "Plain Text", "JSON", "HTML"]
        if validated.get("default_export_format") not in valid_formats:
            validated["default_export_format"] = "Markdown"

        # Validate numeric ranges
        if "processing_timeout" in validated:
            try:
                value = float(validated["processing_timeout"])
                validated["processing_timeout"] = max(30, min(600, value))
            except (ValueError, TypeError):
                validated["processing_timeout"] = 300

        if "quality_threshold" in validated:
            try:
                value = float(validated["quality_threshold"])
                validated["quality_threshold"] = max(0.0, min(1.0, value))
            except (ValueError, TypeError):
                validated["quality_threshold"] = 0.6

        # Validate boolean settings
        boolean_keys = ["analytics_enabled", "auto_save_results", "show_advanced_options"]
        for key in boolean_keys:
            if key in validated:
                validated[key] = bool(validated[key])

        return validated

class ThemeManager:
    """Manages UI themes and customization."""

    def __init__(self, preferences_manager: UserPreferencesManager):
        self.prefs = preferences_manager
        self.themes = self._load_default_themes()

    def _load_default_themes(self) -> Dict[str, Dict[str, Any]]:
        """Load default theme configurations."""
        return {
            "Professional": {
                "primary_color": "#1e40af",
                "secondary_color": "#3b82f6",
                "background_color": "#ffffff",
                "text_color": "#1f2937"
            },
            "Modern": {
                "primary_color": "#7c3aed", 
                "secondary_color": "#8b5cf6",
                "background_color": "#fafafa",
                "text_color": "#111827"
            },
            "Classic": {
                "primary_color": "#1f2937",
                "secondary_color": "#374151", 
                "background_color": "#f9fafb",
                "text_color": "#111827"
            },
            "Dark": {
                "primary_color": "#3b82f6",
                "secondary_color": "#1e40af",
                "background_color": "#111827", 
                "text_color": "#f9fafb"
            }
        }

    def get_current_theme(self) -> Dict[str, Any]:
        """Get current theme configuration."""
        theme_name = self.prefs.get_preference("theme", "Professional")
        return self.themes.get(theme_name, self.themes["Professional"])

# Global preferences manager instance
_preferences_manager = None

def get_preferences_manager() -> UserPreferencesManager:
    """Get global preferences manager instance."""
    global _preferences_manager
    if _preferences_manager is None:
        _preferences_manager = UserPreferencesManager()
    return _preferences_manager

def load_user_preferences() -> Dict[str, Any]:
    """Convenience function to load user preferences."""
    try:
        manager = get_preferences_manager()
        return manager.load_preferences()
    except Exception as e:
        logger.error(f"Failed to load preferences: {e}")
        return PreferencesConfig.DEFAULT_PREFERENCES.copy()

def save_user_preferences(preferences: Dict[str, Any]) -> bool:
    """Convenience function to save user preferences."""
    try:
        manager = get_preferences_manager()
        return manager.save_preferences(preferences)
    except Exception as e:
        logger.error(f"Failed to save preferences: {e}")
        return False

def get_user_preference(key: str, default: Any = None) -> Any:
    """Convenience function to get a specific preference."""
    try:
        manager = get_preferences_manager()
        return manager.get_preference(key, default)
    except Exception as e:
        logger.error(f"Failed to get preference: {e}")
        return default

def set_user_preference(key: str, value: Any) -> bool:
    """Convenience function to set a specific preference."""
    try:
        manager = get_preferences_manager()
        return manager.set_preference(key, value)
    except Exception as e:
        logger.error(f"Failed to set preference: {e}")
        return False

def test_preferences():
    """Test preferences functionality."""
    logger.info("Testing preferences functionality...")

    try:
        manager = UserPreferencesManager()

        # Test loading defaults
        prefs = manager.load_preferences()
        assert "theme" in prefs, "Theme preference missing"
        assert "default_export_format" in prefs, "Export format preference missing"

        # Test setting preference
        success = manager.set_preference("theme", "Modern")
        assert success, "Failed to set preference"

        # Test getting preference
        theme = manager.get_preference("theme")
        assert theme == "Modern", "Failed to get updated preference"

        # Test theme manager
        theme_manager = ThemeManager(manager)
        current_theme = theme_manager.get_current_theme()
        assert "primary_color" in current_theme, "Theme missing primary color"

        logger.info("Preferences test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Preferences test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_preferences()
    print(f"Preferences Test: {'✅ PASS' if success else '❌ FAIL'}")
