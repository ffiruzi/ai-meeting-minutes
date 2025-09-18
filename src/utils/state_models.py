"""
Enhanced State models for the Meeting Minutes Generator LangGraph workflow.
Expanded for Day 2 with complete agent orchestration support.
"""

from typing import TypedDict, Optional, List, Dict, Any, Union
from datetime import datetime
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

class MeetingState(TypedDict):
    """
    Enhanced state object that flows through the LangGraph workflow.
    Each agent reads from and writes to this state object.
    """

    # ================================
    # INPUT DATA
    # ================================
    raw_transcript: str                           # Original, unprocessed meeting transcript
    meeting_metadata: Optional[Dict[str, Any]]    # Date, attendees, duration, type, etc.

    # ================================
    # AGENT 1: TRANSCRIPT PROCESSOR OUTPUTS
    # ================================
    cleaned_transcript: Optional[str]             # Cleaned and structured transcript
    speaker_identification: Optional[Dict[str, List[str]]]  # Identified speakers and their contributions
    processing_notes: Optional[str]               # Notes from the cleaning process
    transcript_quality_score: Optional[float]     # Quality assessment (0-1)

    # ================================
    # AGENT 2: CONTENT ANALYZER OUTPUTS
    # ================================
    extracted_info: Optional[Dict[str, Any]]      # Complete structured data (JSON format)
    action_items: Optional[List[Dict[str, str]]]  # Extracted action items with details
    decisions: Optional[List[Dict[str, str]]]     # Decisions made in meeting
    key_points: Optional[List[str]]               # Important discussion points
    attendees: Optional[List[str]]                # Identified attendees
    meeting_type: Optional[str]                   # Type of meeting detected
    topics_discussed: Optional[List[str]]         # Main topics covered
    deadlines_mentioned: Optional[List[Dict[str, str]]]  # Time-sensitive items

    # ================================
    # AGENT 3: SUMMARY WRITER OUTPUTS
    # ================================
    executive_summary: Optional[str]              # High-level meeting summary
    meeting_overview: Optional[str]               # Purpose and context
    key_outcomes: Optional[str]                   # Main results and decisions
    next_steps_summary: Optional[str]             # Overview of what happens next
    meeting_insights: Optional[List[str]]         # Important insights or concerns
    stakeholder_impact: Optional[Dict[str, str]]  # Impact on different stakeholders

    # ================================
    # AGENT 4: MINUTES FORMATTER OUTPUTS
    # ================================
    formatted_minutes: Optional[str]              # Final formatted meeting minutes (Markdown)
    minutes_sections: Optional[Dict[str, str]]    # Individual sections for flexibility
    action_items_table: Optional[str]             # Formatted action items table
    decisions_list: Optional[str]                 # Formatted decisions list
    attendees_list: Optional[str]                 # Formatted attendees information

    # ================================
    # WORKFLOW METADATA AND CONTROL
    # ================================
    processing_status: Optional[str]              # Current workflow status
    current_agent: Optional[str]                  # Which agent is currently processing
    agent_statuses: Optional[Dict[str, str]]      # Status of each agent
    progress_percentage: Optional[int]            # Progress indicator (0-100)

    # ================================
    # ERROR HANDLING AND LOGGING
    # ================================
    errors: Optional[List[Dict[str, str]]]        # Errors with agent and message
    warnings: Optional[List[Dict[str, str]]]      # Warnings from processing
    processing_log: Optional[List[Dict[str, Any]]]  # Detailed processing log

    # ================================
    # PERFORMANCE AND TIMING
    # ================================
    processing_time: Optional[float]              # Total time taken for processing
    agent_processing_times: Optional[Dict[str, float]]  # Time per agent
    timestamp: Optional[str]                      # When processing started
    completion_timestamp: Optional[str]           # When processing completed

    # ================================
    # ADDITIONAL METADATA FOR UI/UX
    # ================================
    input_method: Optional[str]                   # How input was provided (upload, paste, sample)
    input_filename: Optional[str]                 # Original filename if uploaded
    word_count: Optional[int]                     # Word count of original transcript
    estimated_duration: Optional[str]             # Estimated meeting duration

class ActionItem(TypedDict):
    """Enhanced structure for individual action items."""
    task: str
    assignee: str
    deadline: str
    priority: Optional[str]              # high, medium, low
    status: Optional[str]                # pending, in_progress, completed
    context: Optional[str]               # Context from the meeting
    dependencies: Optional[List[str]]    # Other action items this depends on

class Decision(TypedDict):
    """Enhanced structure for meeting decisions."""
    decision: str
    context: str
    rationale: Optional[str]             # Why this decision was made
    impact: Optional[str]                # Expected impact
    stakeholders: Optional[List[str]]    # People affected by this decision
    implementation_date: Optional[str]   # When decision takes effect
    review_date: Optional[str]           # When to review this decision

class MeetingMetadata(TypedDict):
    """Enhanced structure for meeting metadata."""
    date: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    duration: Optional[str]
    attendees: Optional[List[str]]
    meeting_type: Optional[str]          # standup, planning, client, board, etc.
    location: Optional[str]              # physical or virtual location
    organizer: Optional[str]
    agenda_items: Optional[List[str]]    # Pre-planned agenda
    meeting_series: Optional[str]        # If part of recurring series

class ProcessingError(TypedDict):
    """Structure for processing errors."""
    agent: str
    error_type: str
    message: str
    timestamp: str
    recoverable: bool

# ================================
# STATE MANAGEMENT FUNCTIONS
# ================================

def create_initial_state(
    transcript: str,
    metadata: Optional[Dict[str, Any]] = None,
    input_method: str = "unknown"
) -> MeetingState:
    """
    Create initial state object for the workflow.

    Args:
        transcript: Raw meeting transcript
        metadata: Optional meeting metadata
        input_method: How the input was provided

    Returns:
        Initial MeetingState object with all fields initialized
    """
    current_time = datetime.now().isoformat()

    return MeetingState(
        # Input
        raw_transcript=transcript,
        meeting_metadata=metadata or {},

        # Initialize all agent outputs as None
        cleaned_transcript=None,
        speaker_identification=None,
        processing_notes=None,
        transcript_quality_score=None,

        extracted_info=None,
        action_items=None,
        decisions=None,
        key_points=None,
        attendees=None,
        meeting_type=None,
        topics_discussed=None,
        deadlines_mentioned=None,

        executive_summary=None,
        meeting_overview=None,
        key_outcomes=None,
        next_steps_summary=None,
        meeting_insights=None,
        stakeholder_impact=None,

        formatted_minutes=None,
        minutes_sections=None,
        action_items_table=None,
        decisions_list=None,
        attendees_list=None,

        # Workflow metadata
        processing_status="initialized",
        current_agent="transcript_processor",
        agent_statuses={
            "transcript_processor": "pending",
            "content_analyzer": "waiting",
            "summary_writer": "waiting",
            "minutes_formatter": "waiting"
        },
        progress_percentage=0,

        # Error handling
        errors=[],
        warnings=[],
        processing_log=[],

        # Performance
        processing_time=None,
        agent_processing_times={},
        timestamp=current_time,
        completion_timestamp=None,

        # Additional metadata
        input_method=input_method,
        input_filename=None,
        word_count=len(transcript.split()) if transcript else 0,
        estimated_duration=None
    )

def update_agent_status(
    state: MeetingState,
    agent_name: str,
    status: str,
    progress: Optional[int] = None,
    processing_time: Optional[float] = None
) -> MeetingState:
    """
    Update the status of a specific agent in the workflow.

    Args:
        state: Current state object
        agent_name: Name of the agent to update
        status: New status (pending, processing, complete, error)
        progress: Optional progress percentage
        processing_time: Time taken by this agent

    Returns:
        Updated state object
    """
    new_state = state.copy()

    # Update agent status
    if new_state["agent_statuses"]:
        new_state["agent_statuses"][agent_name] = status

    new_state["current_agent"] = agent_name

    # Update progress
    if progress is not None:
        new_state["progress_percentage"] = progress
    else:
        new_state["progress_percentage"] = calculate_progress(new_state)

    # Update processing time
    if processing_time is not None:
        if new_state["agent_processing_times"] is None:
            new_state["agent_processing_times"] = {}
        new_state["agent_processing_times"][agent_name] = processing_time

    # Log the status change
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "status": status,
        "progress": new_state["progress_percentage"]
    }

    if new_state["processing_log"] is None:
        new_state["processing_log"] = []
    new_state["processing_log"].append(log_entry)

    logger.info(f"Agent {agent_name} status updated to {status} ({new_state['progress_percentage']}%)")

    return new_state

def add_error(
    state: MeetingState,
    agent_name: str,
    error_type: str,
    error_message: str,
    recoverable: bool = True
) -> MeetingState:
    """
    Add an error message to the state.

    Args:
        state: Current state object
        agent_name: Agent that encountered the error
        error_type: Type of error
        error_message: Error message
        recoverable: Whether the error can be recovered from

    Returns:
        Updated state object with error
    """
    new_state = state.copy()

    error_entry = ProcessingError(
        agent=agent_name,
        error_type=error_type,
        message=error_message,
        timestamp=datetime.now().isoformat(),
        recoverable=recoverable
    )

    if new_state["errors"] is None:
        new_state["errors"] = []
    new_state["errors"].append(error_entry)

    if not recoverable:
        new_state["processing_status"] = "error"
        new_state["agent_statuses"][agent_name] = "error"

    logger.error(f"Error in {agent_name}: {error_message}")

    return new_state

def add_warning(
    state: MeetingState,
    agent_name: str,
    warning_message: str
) -> MeetingState:
    """
    Add a warning message to the state.

    Args:
        state: Current state object
        agent_name: Agent that generated the warning
        warning_message: Warning message

    Returns:
        Updated state object with warning
    """
    new_state = state.copy()

    warning_entry = {
        "agent": agent_name,
        "message": warning_message,
        "timestamp": datetime.now().isoformat()
    }

    if new_state["warnings"] is None:
        new_state["warnings"] = []
    new_state["warnings"].append(warning_entry)

    logger.warning(f"Warning from {agent_name}: {warning_message}")

    return new_state

def calculate_progress(state: MeetingState) -> int:
    """
    Calculate overall processing progress based on agent statuses.

    Args:
        state: Current state object

    Returns:
        Progress percentage (0-100)
    """
    if not state.get("agent_statuses"):
        return 0

    statuses = state["agent_statuses"]
    total_agents = len(statuses)

    # Weight each agent status
    status_weights = {
        "waiting": 0,
        "pending": 0,
        "processing": 0.5,
        "complete": 1.0,
        "error": 0
    }

    total_weight = sum(status_weights.get(status, 0) for status in statuses.values())
    progress = int((total_weight / total_agents) * 100)

    return min(progress, 100)

def is_processing_complete(state: MeetingState) -> bool:
    """
    Check if all agents have completed processing successfully.

    Args:
        state: Current state object

    Returns:
        True if processing is complete, False otherwise
    """
    return (
        state.get("formatted_minutes") is not None and
        state.get("processing_status") not in ["error", "cancelled"] and
        calculate_progress(state) == 100
    )

def has_errors(state: MeetingState) -> bool:
    """
    Check if there are any non-recoverable errors.

    Args:
        state: Current state object

    Returns:
        True if there are blocking errors
    """
    if not state.get("errors"):
        return False

    return any(not error.get("recoverable", True) for error in state["errors"])

def get_processing_summary(state: MeetingState) -> Dict[str, Any]:
    """
    Get a summary of processing status and performance.

    Args:
        state: Current state object

    Returns:
        Dictionary with processing summary
    """
    return {
        "status": state.get("processing_status", "unknown"),
        "progress": calculate_progress(state),
        "current_agent": state.get("current_agent", "unknown"),
        "total_time": state.get("processing_time", 0),
        "agent_times": state.get("agent_processing_times", {}),
        "error_count": len(state.get("errors", [])),
        "warning_count": len(state.get("warnings", [])),
        "word_count": state.get("word_count", 0),
        "completed": is_processing_complete(state)
    }

def validate_state(state: MeetingState) -> List[str]:
    """
    Validate state object for completeness and consistency.

    Args:
        state: State object to validate

    Returns:
        List of validation error messages
    """
    errors = []

    # Check required fields
    if not state.get("raw_transcript"):
        errors.append("Raw transcript is required")

    if not state.get("agent_statuses"):
        errors.append("Agent statuses not initialized")

    # Check consistency
    if state.get("progress_percentage", 0) > 100:
        errors.append("Progress percentage cannot exceed 100")

    if state.get("processing_status") == "complete" and not is_processing_complete(state):
        errors.append("Status marked complete but processing not finished")

    return errors