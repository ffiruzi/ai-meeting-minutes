"""
Utilities package for Meeting Minutes Generator.
Contains OpenAI client, state models, and helper functions.

Day 2 Update: Added workflow utilities and enhanced state management.
"""

from .openai_client import OpenAIClient, get_openai_client, test_openai_connection
from .state_models import (
    MeetingState,
    ActionItem,
    Decision,
    MeetingMetadata,
    ProcessingError,
    create_initial_state,
    update_agent_status,
    add_error,
    add_warning,
    is_processing_complete,
    has_errors,
    calculate_progress,
    get_processing_summary,
    validate_state
)

__all__ = [
    # OpenAI Client
    "OpenAIClient",
    "get_openai_client",
    "test_openai_connection",

    # State Models
    "MeetingState",
    "ActionItem",
    "Decision",
    "MeetingMetadata",
    "ProcessingError",

    # State Management Functions
    "create_initial_state",
    "update_agent_status",
    "add_error",
    "add_warning",
    "is_processing_complete",
    "has_errors",
    "calculate_progress",
    "get_processing_summary",
    "validate_state"
]