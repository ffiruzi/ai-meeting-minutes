"""
Streamlit utility functions for Meeting Minutes Generator.
Provides UI helpers, caching, formatting, and user experience enhancements.
"""

import streamlit as st
import time
import json
import base64
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from io import StringIO
import logging

logger = logging.getLogger(__name__)


# ================================
# CACHING AND PERFORMANCE
# ================================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_sample_data():
    """Load sample data with caching for performance."""
    try:
        from sample_data.sample_transcripts import get_all_sample_keys, get_sample_titles, get_sample_transcript

        sample_keys = get_all_sample_keys()
        sample_titles = get_sample_titles()
        samples = {}

        for key in sample_keys:
            samples[key] = get_sample_transcript(key)

        return {
            "keys": sample_keys,
            "titles": sample_titles,
            "samples": samples
        }
    except Exception as e:
        logger.error(f"Failed to load sample data: {e}")
        return {"keys": [], "titles": {}, "samples": {}}


@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_system_status_cached():
    """Get system status with caching."""
    try:
        from utils.openai_client import get_api_status
        from agents import get_system_status

        return {
            "api_status": get_api_status(),
            "system_status": get_system_status(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return {
            "api_status": {"status": "error", "production_ready": False},
            "system_status": {"status": "error", "ai_enhanced_agents": 0, "total_agents": 4},
            "timestamp": datetime.now().isoformat()
        }


# ================================
# UI HELPERS
# ================================

def create_download_link(data: str, filename: str, mime_type: str = "text/plain", label: str = "Download") -> str:
    """Create a download link for data."""
    b64_data = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:{mime_type};base64,{b64_data}" download="{filename}">{label}</a>'
    return href


def format_processing_time(seconds: float) -> str:
    """Format processing time for display."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"


def create_metric_card(title: str, value: str, delta: Optional[str] = None, help_text: Optional[str] = None):
    """Create a styled metric card."""
    delta_html = ""
    if delta:
        delta_color = "#16a34a" if not delta.startswith("-") else "#dc2626"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.8rem; margin-top: 0.25rem;">{delta}</div>'

    help_html = ""
    if help_text:
        help_html = f'<div style="color: #64748b; font-size: 0.75rem; margin-top: 0.5rem;">{help_text}</div>'

    card_html = f"""
    <div style="
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    ">
        <div style="font-size: 0.9rem; color: #64748b; margin-bottom: 0.5rem;">{title}</div>
        <div style="font-size: 2rem; font-weight: bold; color: #1e40af;">{value}</div>
        {delta_html}
        {help_html}
    </div>
    """

    return card_html


def show_processing_animation(message: str = "Processing..."):
    """Show an animated processing indicator."""
    placeholder = st.empty()

    animation_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    for i in range(20):  # Show animation for 2 seconds
        char = animation_chars[i % len(animation_chars)]
        placeholder.markdown(f"**{char} {message}**")
        time.sleep(0.1)

    placeholder.empty()


def create_status_badge(status: str, label: str = "") -> str:
    """Create a colored status badge."""
    colors = {
        "success": "#16a34a",
        "warning": "#d97706",
        "error": "#dc2626",
        "info": "#3b82f6",
        "processing": "#7c3aed"
    }

    color = colors.get(status, "#64748b")

    badge_html = f"""
    <span style="
        background-color: {color};
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
    ">
        {label}
    </span>
    """

    return badge_html


# ================================
# DATA FORMATTING
# ================================

def format_action_items_table(action_items: List[Dict[str, Any]]) -> str:
    """Format action items as an HTML table."""
    if not action_items:
        return "<p><em>No action items identified</em></p>"

    table_html = """
    <table style="width: 100%; border-collapse: collapse; margin: 1rem 0;">
        <thead>
            <tr style="background-color: #f8fafc;">
                <th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid #e2e8f0;">Task</th>
                <th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid #e2e8f0;">Assignee</th>
                <th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid #e2e8f0;">Deadline</th>
                <th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid #e2e8f0;">Priority</th>
            </tr>
        </thead>
        <tbody>
    """

    for item in action_items:
        priority = item.get("priority", "medium").lower()
        priority_color = {
            "high": "#fca5a5",
            "medium": "#fed7aa",
            "low": "#d1fae5"
        }.get(priority, "#f3f4f6")

        table_html += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 0.75rem; vertical-align: top;">
                    <strong>{item.get('task', 'Unknown task')}</strong>
                    {f'<br><small style="color: #64748b;">{item.get("context", "")}</small>' if item.get('context') else ''}
                </td>
                <td style="padding: 0.75rem;">{item.get('assignee', 'Unassigned')}</td>
                <td style="padding: 0.75rem;">{item.get('deadline', 'Not specified')}</td>
                <td style="padding: 0.75rem;">
                    <span style="
                        background-color: {priority_color};
                        padding: 0.25rem 0.5rem;
                        border-radius: 4px;
                        font-size: 0.75rem;
                        font-weight: 500;
                    ">
                        {priority.title()}
                    </span>
                </td>
            </tr>
        """

    table_html += """
        </tbody>
    </table>
    """

    return table_html


def format_decisions_list(decisions: List[Dict[str, Any]]) -> str:
    """Format decisions as a styled list."""
    if not decisions:
        return "<p><em>No decisions recorded</em></p>"

    list_html = "<div style='margin: 1rem 0;'>"

    for i, decision in enumerate(decisions, 1):
        context = decision.get('context', '')
        rationale = decision.get('rationale', '')

        list_html += f"""
        <div style="
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: #f8fafc;
        ">
            <h4 style="margin: 0 0 0.5rem 0; color: #1e40af;">Decision {i}</h4>
            <p style="margin: 0 0 0.5rem 0; font-weight: 500;">{decision.get('decision', 'Unknown decision')}</p>

            {f'<p style="margin: 0.25rem 0; color: #64748b; font-size: 0.9rem;"><strong>Context:</strong> {context}</p>' if context else ''}
            {f'<p style="margin: 0.25rem 0; color: #64748b; font-size: 0.9rem;"><strong>Rationale:</strong> {rationale}</p>' if rationale and rationale != 'not specified' else ''}
        </div>
        """

    list_html += "</div>"
    return list_html


def format_file_size(bytes_size: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


# ================================
# VALIDATION AND SANITIZATION
# ================================

def validate_transcript(transcript: str) -> Tuple[bool, str]:
    """Validate transcript content and return (is_valid, message)."""
    if not transcript:
        return False, "Transcript is empty"

    if len(transcript.strip()) < 10:
        return False, "Transcript too short (minimum 10 characters)"

    if len(transcript) > 50000:  # 50KB limit
        return False, "Transcript too long (maximum 50,000 characters)"

    # Check if it looks like a real transcript
    if ":" not in transcript:
        return False, "Transcript should include speaker names (format: 'Name: message')"

    # Check for minimum word count
    words = transcript.split()
    if len(words) < 5:
        return False, "Transcript should contain at least 5 words"

    return True, "Transcript looks good"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe downloads."""
    import re

    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    filename = filename.strip('._')

    # Ensure reasonable length
    if len(filename) > 100:
        name_part = filename[:90]
        extension = filename[90:] if '.' in filename[90:] else ''
        filename = name_part + extension

    return filename


def validate_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean metadata."""
    cleaned = {}

    # Date validation
    if 'date' in metadata:
        date_str = str(metadata['date']).strip()
        if date_str and date_str != 'None':
            cleaned['date'] = date_str

    # Meeting type validation
    if 'meeting_type' in metadata:
        meeting_type = str(metadata['meeting_type']).strip()
        if meeting_type and meeting_type != 'None':
            cleaned['meeting_type'] = meeting_type

    # Duration validation
    if 'duration' in metadata:
        duration = str(metadata['duration']).strip()
        if duration and duration != 'None':
            cleaned['duration'] = duration

    # Attendees validation
    if 'attendees' in metadata and isinstance(metadata['attendees'], list):
        attendees = [str(name).strip() for name in metadata['attendees'] if str(name).strip()]
        if attendees:
            cleaned['attendees'] = attendees

    # Filename validation
    if 'filename' in metadata:
        filename = str(metadata['filename']).strip()
        if filename and filename != 'None':
            cleaned['filename'] = sanitize_filename(filename)

    return cleaned


# ================================
# ERROR HANDLING
# ================================

def display_error_details(error: Exception, context: str = ""):
    """Display error details in a user-friendly format."""
    error_type = type(error).__name__
    error_message = str(error)

    st.error(f"❌ **{error_type}**: {error_message}")

    if context:
        st.info(f"**Context**: {context}")

    # Show expandable details for debugging
    with st.expander("🔍 Technical Details"):
        st.code(f"""
Error Type: {error_type}
Error Message: {error_message}
Context: {context}
Timestamp: {datetime.now().isoformat()}
        """)


def safe_execute(func, *args, default_return=None, error_message="Operation failed", **kwargs):
    """Safely execute a function with error handling."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"{error_message}: {e}")
        display_error_details(e, error_message)
        return default_return


# ================================
# SESSION STATE HELPERS
# ================================

def init_session_state(defaults: Dict[str, Any]):
    """Initialize session state with default values."""
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_session_value(key: str, default=None):
    """Get value from session state with default."""
    return st.session_state.get(key, default)


def set_session_value(key: str, value: Any):
    """Set value in session state."""
    st.session_state[key] = value


def clear_session_state():
    """Clear all session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]


# ================================
# EXPORT UTILITIES
# ================================

def create_export_package(state: Dict[str, Any], format_type: str = "json") -> str:
    """Create comprehensive export package."""
    export_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "generator": "Meeting Minutes Generator v1.0.0",
            "format_version": "1.0",
            "export_type": format_type
        },
        "meeting_info": {
            "date": state.get("meeting_metadata", {}).get("date"),
            "type": state.get("meeting_type"),
            "attendees": state.get("attendees", []),
            "duration": state.get("meeting_metadata", {}).get("duration"),
            "quality_score": state.get("transcript_quality_score")
        },
        "content": {
            "executive_summary": state.get("executive_summary"),
            "meeting_overview": state.get("meeting_overview"),
            "key_outcomes": state.get("key_outcomes"),
            "next_steps": state.get("next_steps_summary")
        },
        "structured_data": {
            "action_items": state.get("action_items", []),
            "decisions": state.get("decisions", []),
            "key_points": state.get("key_points", []),
            "topics_discussed": state.get("topics_discussed", []),
            "meeting_insights": state.get("meeting_insights", [])
        },
        "output": {
            "formatted_minutes": state.get("formatted_minutes"),
            "minutes_sections": state.get("minutes_sections", {}),
            "processing_stats": get_processing_stats(state)
        }
    }

    if format_type == "json":
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    else:
        # Future: could add other formats like XML, YAML, etc.
        return json.dumps(export_data, indent=2, ensure_ascii=False)


def get_processing_stats(state: Dict[str, Any]) -> Dict[str, Any]:
    """Get processing statistics from state."""
    from utils.state_models import get_processing_summary
    from agents.minutes_formatter import get_minutes_statistics

    try:
        processing_summary = get_processing_summary(state)
        minutes_stats = get_minutes_statistics(state)

        return {
            "processing_time": processing_summary.get("total_time", 0),
            "agent_times": processing_summary.get("agent_times", {}),
            "word_count": minutes_stats.get("total_words", 0),
            "character_count": minutes_stats.get("total_characters", 0),
            "action_items_count": minutes_stats.get("action_items_count", 0),
            "decisions_count": minutes_stats.get("decisions_count", 0),
            "success_rate": "100%" if processing_summary.get("completed") else "Partial"
        }
    except Exception as e:
        logger.error(f"Failed to get processing stats: {e}")
        return {"error": str(e)}


# ================================
# UI ANIMATIONS AND FEEDBACK
# ================================

def show_success_animation(message: str):
    """Show success animation with message."""
    placeholder = st.empty()

    # Show animated success
    placeholder.success(f"🎉 {message}")
    time.sleep(2)

    # Fade to normal success
    placeholder.success(message)


def show_progress_bar(progress: float, message: str = ""):
    """Show progress bar with message."""
    progress_bar = st.progress(progress)
    if message:
        st.write(message)
    return progress_bar


def create_collapsible_section(title: str, content: str, expanded: bool = False):
    """Create a collapsible section with content."""
    with st.expander(title, expanded=expanded):
        if isinstance(content, str):
            st.markdown(content)
        else:
            st.write(content)


# ================================
# DEBUGGING AND DEVELOPMENT
# ================================

def debug_state(state: Dict[str, Any], show_in_sidebar: bool = True):
    """Show debug information about the state."""
    if not st.checkbox("🐛 Debug Mode", key="debug_mode"):
        return

    debug_container = st.sidebar if show_in_sidebar else st

    with debug_container:
        st.header("🔧 Debug Information")

        # Basic state info
        st.subheader("State Overview")
        st.json({
            "processing_status": state.get("processing_status"),
            "current_agent": state.get("current_agent"),
            "progress": state.get("progress_percentage"),
            "errors": len(state.get("errors", [])),
            "warnings": len(state.get("warnings", []))
        })

        # Detailed state
        with st.expander("Full State"):
            st.json(state)


def performance_monitor(func):
    """Decorator to monitor function performance."""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        if st.checkbox(f"⚡ Show {func.__name__} performance", key=f"perf_{func.__name__}"):
            st.info(f"Function `{func.__name__}` took {end_time - start_time:.3f}s")

        return result

    return wrapper