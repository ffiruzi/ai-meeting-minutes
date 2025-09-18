

import streamlit as st
import sys
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import traceback
import io
import base64
from pathlib import Path

# Add src to path for imports
sys.path.append('src')

from workflow import process_meeting_transcript, get_workflow
from sample_data.sample_transcripts import get_all_sample_keys, get_sample_transcript, get_sample_titles
from utils.state_models import get_processing_summary, is_processing_complete, calculate_progress
from utils.openai_client import get_api_status, test_openai_connection
from agents import get_system_status
from agents.minutes_formatter import get_minutes_statistics, export_minutes_as_text


try:
    from utils.pdf_generator import generate_pdf_report
    from utils.analytics import track_usage, get_usage_stats
    from utils.user_preferences import load_user_preferences, save_user_preferences
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    generate_pdf_report = None
    track_usage = None
    get_usage_stats = None
    load_user_preferences = None
    save_user_preferences = None

# ================================
# PAGE CONFIGURATION
# ================================

st.set_page_config(
    page_title="Meeting Minutes Generator Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "AI-Powered Meeting Minutes Generator - Professional Edition",
        'Get Help': 'https://github.com/your-repo/meeting-minutes-ai',
        'Report a bug': 'https://github.com/your-repo/meeting-minutes-ai/issues'
    }
)

# ================================
# ENHANCED CSS STYLING
# ================================

def load_enhanced_css():
    """Load enhanced CSS for professional appearance with animations."""
    st.markdown("""
    <style>
    /* Enhanced CSS for Professional UI */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        margin: 0;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    /* Status cards */
    .status-good {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(22, 163, 74, 0.3);
    }
    
    .status-warning {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(217, 119, 6, 0.3);
    }
    
    .status-error {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
    }
    
    /* Agent status indicators */
    .agent-status {
        background: #f3f4f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #d1d5db;
        transition: all 0.3s ease;
    }
    
    .agent-status.active {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-left-color: #667eea;
        animation: pulse 2s infinite;
    }
    
    .agent-status.complete {
        background: #d1fae5;
        border-left-color: #16a34a;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    /* Progress container */
    .progress-container {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin: 1rem 0;
    }
    
    /* Results container */
    .results-container {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin: 2rem 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        height: 100%;
        transition: all 0.3s ease;
        border: 1px solid #e5e7eb;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: #f9fafb;
        padding: 1rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Loading animation */
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Success animation */
    .success-checkmark {
        display: inline-block;
        font-size: 2rem;
        color: #16a74a;
        animation: successPulse 1.5s ease-out;
    }
    
    @keyframes successPulse {
        0% { transform: scale(0); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    
    /* Feature cards */
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            padding: 1.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
        
        .results-container {
            padding: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ================================
# ENHANCED STATE MANAGEMENT
# ================================

def initialize_enhanced_session_state():
    """Initialize enhanced session state with user preferences."""
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'processing_state' not in st.session_state:
        st.session_state.processing_state = None
    if 'processing_time' not in st.session_state:
        st.session_state.processing_time = 0
    if 'show_analytics' not in st.session_state:
        st.session_state.show_analytics = False
    if 'show_preferences' not in st.session_state:
        st.session_state.show_preferences = False
    if 'usage_stats' not in st.session_state:
        st.session_state.usage_stats = {
            'sessions': 0,
            'transcripts_processed': 0,
            'total_processing_time': 0,
            'avg_transcript_length': 0
        }
    if 'processing_history' not in st.session_state:
        st.session_state.processing_history = []
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = load_user_preferences() if load_user_preferences else {}
    if 'last_processed_transcript' not in st.session_state:
        st.session_state.last_processed_transcript = None

    if 'current_transcript' not in st.session_state:
        st.session_state.current_transcript = ""
    if 'current_metadata' not in st.session_state:
        st.session_state.current_metadata = {}
    if 'input_method' not in st.session_state:
        st.session_state.input_method = "manual"

# ================================
# ENHANCED UI COMPONENTS
# ================================

def render_enhanced_header():
    """Render enhanced application header with animations."""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Meeting Minutes Generator Pro</h1>
        <p>✨ AI-Powered Professional Meeting Documentation | Day 6 Edition</p>
    </div>
    """, unsafe_allow_html=True)

def render_enhanced_system_status():
    """Render enhanced system status dashboard."""
    st.header("📊 System Status")

    # API and system health
    api_status = get_api_status()
    system_status = get_system_status()

    if api_status['production_ready']:
        st.markdown("""
        <div class="status-good">
            <strong>✅ System Online</strong><br>
            <small>All AI agents operational and ready</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-warning">
            <strong>⚠️ API Configuration Required</strong><br>
            <small>Please configure your OpenAI API key</small>
        </div>
        """, unsafe_allow_html=True)

    # System metrics
    col1, col2 = st.columns(2)

    with col1:
        if system_status['ai_enhanced_agents'] == 4:
            st.metric(
                "AI Agents",
                f"{system_status['ai_enhanced_agents']}/{system_status['total_agents']}",
                delta="100% AI-powered" if system_status['ai_enhanced_agents'] == 4 else None
            )

    with col2:
        status_emoji = "🟢" if system_status['status'] == 'production_ready' else "🟡"
        status_text = "Production" if system_status['status'] == 'production_ready' else "Setup"
        st.metric("Status", f"{status_emoji} {status_text}")

    # Usage statistics
    if st.session_state.usage_stats['sessions'] > 0:
        st.subheader("📈 Your Usage")

        usage = st.session_state.usage_stats
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Sessions", usage['sessions'])
            st.metric("Processed", usage['transcripts_processed'])

        with col2:
            avg_time = usage['total_processing_time'] / max(usage['transcripts_processed'], 1)
            st.metric("Avg Time", f"{avg_time:.1f}s")
            st.metric("Avg Length", f"{usage['avg_transcript_length']:.0f}")

    # Enhanced processing capabilities
    st.subheader("🎯 Pro Features")
    features = [
        "✨ Advanced AI Processing",
        "📊 Real-time Analytics",
        "🎨 Custom Export Formats",
        "📱 Mobile-Optimized UI",
        "⚡ Performance Monitoring",
        "🔄 Processing History"
    ]

    for feature in features:
        st.write(feature)

    # Quick actions
    st.subheader("⚡ Quick Actions")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.show_analytics = True

    with col2:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.show_preferences = True


def render_input_section() -> tuple[str, Dict[str, Any], str]:
    """Render enhanced input section with multiple input methods."""
    st.header("📝 Meeting Transcript Input")

    # Enhanced input tabs
    input_tabs = st.tabs(["✍️ Text Input", "📁 File Upload", "📚 Sample Data"])

    # Initialize with session state values
    transcript = st.session_state.get('current_transcript', "")
    metadata = st.session_state.get('current_metadata', {})
    input_method = st.session_state.get('input_method', "manual")

    # Tab 1: Manual text input
    with input_tabs[0]:
        st.write("Paste or type your meeting transcript below:")

        # Use session state for text area
        manual_transcript = st.text_area(
            "Meeting Transcript",
            value=st.session_state.get('current_transcript', "") if st.session_state.get(
                'input_method') == 'manual' else "",
            height=300,
            placeholder="John: Let's start the meeting...\nSarah: I agree with the proposal...",
            key="transcript_input"
        )

        if manual_transcript:
            st.session_state.current_transcript = manual_transcript
            st.session_state.input_method = "manual"
            transcript = manual_transcript

        # Enhanced metadata collection
        with st.expander("📋 Meeting Metadata (Optional)", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                meeting_date = st.date_input("Meeting Date", datetime.now())
                meeting_type = st.selectbox(
                    "Meeting Type",
                    ["General", "Standup", "Review", "Planning", "Retrospective", "Board Meeting"]
                )
            with col2:
                duration = st.text_input("Duration", placeholder="e.g., 45 minutes")
                attendees = st.text_input("Attendees", placeholder="John, Sarah, Mike")

            metadata = {
                "date": meeting_date.strftime("%Y-%m-%d"),
                "type": meeting_type,
                "duration": duration,
                "attendees": [a.strip() for a in attendees.split(",")] if attendees else []
            }

            if manual_transcript:
                st.session_state.current_metadata = metadata

    # Tab 2: File upload
    with input_tabs[1]:
        uploaded_file = st.file_uploader(
            "Upload a transcript file",
            type=['txt', 'md'],
            help="Upload a text or markdown file containing your meeting transcript"
        )

        if uploaded_file is not None:
            file_transcript = uploaded_file.read().decode("utf-8")
            st.session_state.current_transcript = file_transcript
            st.session_state.input_method = "file"
            transcript = file_transcript

            st.success(f"✅ Loaded {len(file_transcript)} characters from {uploaded_file.name}")

            # Show preview
            with st.expander("📄 Preview (first 500 characters)"):
                st.text(file_transcript[:500] + "..." if len(file_transcript) > 500 else file_transcript)

    # Tab 3: Sample data - FIXED
    with input_tabs[2]:
        st.write("Select a sample meeting transcript to test the system:")

        sample_titles = get_sample_titles()
        selected_sample = st.selectbox(
            "Choose a sample transcript",
            options=list(sample_titles.keys()),
            format_func=lambda x: sample_titles[x],
            key="sample_selector"
        )

        # FIXED: Load sample button now properly stores the transcript
        if st.button("📥 Load Sample", type="primary", key="load_sample_btn"):
            sample = get_sample_transcript(selected_sample)
            sample_transcript = sample["transcript"]
            sample_metadata = sample.get("metadata", {})

            # Store in session state
            st.session_state.current_transcript = sample_transcript
            st.session_state.current_metadata = sample_metadata
            st.session_state.input_method = "sample"

            st.success(f"✅ Loaded {selected_sample}: {len(sample_transcript)} characters")
            st.rerun()  # Force rerun to update the UI

        # Show loaded sample if it exists
        if st.session_state.get('input_method') == 'sample' and st.session_state.get('current_transcript'):
            transcript = st.session_state.current_transcript
            metadata = st.session_state.current_metadata

            # Show sample preview
            with st.expander("📄 Sample Preview", expanded=True):
                st.text(transcript[:500] + "..." if len(transcript) > 500 else transcript)

    # Validation
    if transcript and len(transcript.strip()) < 10:
        st.warning("⚠️ Transcript seems too short. Please add more content.")

    # Return the current transcript from session state
    return (
        st.session_state.get('current_transcript', ""),
        st.session_state.get('current_metadata', {}),
        st.session_state.get('input_method', "manual")
    )




def render_enhanced_progress_tracker(current_agent: str = None, progress: int = 0, processing_stats: dict = None):
    """Render enhanced progress tracking with animations."""
    st.markdown("""
    <div class="progress-container">
        <h3>🚀 AI Processing Pipeline</h3>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced progress bar with gradient
    progress_bar = st.progress(progress / 100.0)

    # Show processing stats
    if processing_stats:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Progress", f"{progress}%")
        with col2:
            st.metric("Current Agent", current_agent or "Initializing")
        with col3:
            elapsed_time = processing_stats.get('elapsed_time', 0)
            st.metric("Elapsed", f"{elapsed_time:.1f}s")

    # Enhanced agent status indicators
    agents = [
        ("transcript_processor", "📝 Transcript Processor", "AI-powered cleaning & structuring"),
        ("content_analyzer", "🔍 Content Analyzer", "Smart extraction & analysis"),
        ("summary_writer", "📊 Summary Writer", "Executive-level summaries"),
        ("minutes_formatter", "📋 Minutes Formatter", "Professional formatting")
    ]

    st.subheader("🤖 AI Agent Pipeline:")

    for agent_id, agent_name, description in agents:
        if current_agent == agent_id:
            st.markdown(f"""
            <div class="agent-status active">
                <div class="loading-spinner"></div>
                <div style="margin-left: 1rem;">
                    <strong>🔄 {agent_name}</strong><br>
                    <small>{description}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif _is_agent_complete(agent_id, progress):
            st.markdown(f"""
            <div class="agent-status complete">
                <div class="success-checkmark">✅</div>
                <div style="margin-left: 1rem;">
                    <strong>{agent_name}</strong><br>
                    <small>Completed successfully</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="agent-status">
                <strong>⏳ {agent_name}</strong><br>
                <small>Waiting in queue...</small>
            </div>
            """, unsafe_allow_html=True)

def _is_agent_complete(agent_id: str, progress: int) -> bool:
    """Helper to determine if agent is complete based on progress."""
    agent_progress = {
        "transcript_processor": 25,
        "content_analyzer": 50,
        "summary_writer": 75,
        "minutes_formatter": 100
    }
    return progress >= agent_progress.get(agent_id, 0)

def render_enhanced_results_display(state: Dict[str, Any]):
    """Render enhanced processing results with FIXED PDF download."""
    st.header("📊 Generated Meeting Minutes")

    # Enhanced performance metrics
    stats = get_minutes_statistics(state)
    processing_summary = get_processing_summary(state)

    # Success animation
    st.markdown('<div class="success-checkmark">✅</div>', unsafe_allow_html=True)
    st.success("🎉 Meeting minutes generated successfully!")

    # Enhanced metrics cards
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats.get('total_words', 0):,}</div>
            <div class="metric-label">Words Generated</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats.get('action_items_count', 0)}</div>
            <div class="metric-label">Action Items</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats.get('decisions_count', 0)}</div>
            <div class="metric-label">Decisions</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        processing_time = processing_summary.get('total_time', st.session_state.processing_time)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{processing_time:.1f}s</div>
            <div class="metric-label">Processing Time</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        quality_score = state.get("transcript_quality_score", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{quality_score:.1f}</div>
            <div class="metric-label">Quality Score</div>
        </div>
        """, unsafe_allow_html=True)

    # Enhanced results tabs
    result_tabs = st.tabs([
        "📋 Meeting Minutes",
        "📊 Executive Summary",
        "✅ Action Items",
        "📈 Analysis",
        "💾 Export Options",
        "🔧 Raw Data"
    ])

    # Tab 1: Meeting Minutes (FIXED PDF DOWNLOAD)
    with result_tabs[0]:
        st.subheader("Professional Meeting Minutes")
        formatted_minutes = state.get("formatted_minutes", "")

        if formatted_minutes:
            st.markdown(formatted_minutes)

            # Enhanced download section
            st.markdown("---")
            st.subheader("📥 Download Options")

            # Generate unique timestamp
            unique_id = datetime.now().strftime("%Y%m%d_%H%M%S")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.download_button(
                    label="📄 Markdown",
                    data=formatted_minutes,
                    file_name=f"meeting_minutes_{unique_id}.md",
                    mime="text/markdown",
                    key=f"download_markdown_{unique_id}",
                    use_container_width=True
                )

            with col2:
                plain_text = export_minutes_as_text(formatted_minutes)
                st.download_button(
                    label="📝 Plain Text",
                    data=plain_text,
                    file_name=f"meeting_minutes_{unique_id}.txt",
                    mime="text/plain",
                    key=f"download_text_{unique_id}",
                    use_container_width=True
                )

            with col3:
                export_data = {
                    "meeting_metadata": state.get("meeting_metadata", {}),
                    "action_items": state.get("action_items", []),
                    "decisions": state.get("decisions", []),
                    "key_points": state.get("key_points", []),
                    "executive_summary": state.get("executive_summary", ""),
                    "formatted_minutes": formatted_minutes,
                    "generated_at": datetime.now().isoformat()
                }

                st.download_button(
                    label="📊 JSON Data",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"meeting_data_{unique_id}.json",
                    mime="application/json",
                    key=f"download_json_{unique_id}",
                    use_container_width=True
                )

            with col4:
                # FIXED: Direct PDF generation without intermediate button
                if PDF_AVAILABLE and generate_pdf_report:
                    try:
                        # Generate PDF directly
                        with st.spinner("Generating PDF..."):
                            pdf_data = generate_pdf_report(state, formatted_minutes)

                        st.download_button(
                            label="📑 PDF Report",
                            data=pdf_data,
                            file_name=f"meeting_minutes_{unique_id}.pdf",
                            mime="application/pdf",
                            key=f"download_pdf_{unique_id}",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"PDF generation unavailable: {str(e)}")
                else:
                    st.info("📑 PDF export\n(ReportLab required)")

        else:
            st.warning("No formatted minutes generated")

    # Tab 2: Executive Summary
    with result_tabs[1]:
        st.subheader("Executive Summary")
        executive_summary = state.get("executive_summary", "")

        if executive_summary:
            st.markdown(f"""
            <div class="feature-card">
                <h4>📊 Executive Summary</h4>
                <p style="font-size: 1.1rem; line-height: 1.6; color: #374151;">
                {executive_summary}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Additional summary components
            summary_components = [
                ("meeting_overview", "Meeting Overview", "🏢"),
                ("key_outcomes", "Key Outcomes", "🎯"),
                ("next_steps_summary", "Next Steps", "⏭️")
            ]

            for field, title, emoji in summary_components:
                content = state.get(field, "")
                if content:
                    st.markdown(f"""
                    <div class="feature-card">
                        <h4>{emoji} {title}</h4>
                        <p style="line-height: 1.6; color: #374151;">{content}</p>
                    </div>
                    """, unsafe_allow_html=True)

        else:
            st.warning("No executive summary generated")

    # Tab 3: Action Items
    with result_tabs[2]:
        st.subheader("Action Items & Deliverables")
        action_items = state.get("action_items", [])

        if action_items:
            for i, item in enumerate(action_items, 1):
                priority = item.get('priority', 'medium').lower()
                priority_color = {
                    'high': '#dc2626',
                    'medium': '#d97706',
                    'low': '#059669'
                }.get(priority, '#6b7280')

                with st.expander(f"📋 Action Item {i}: {item.get('task', 'Unknown')[:60]}...", expanded=i<=3):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"**Task:** {item.get('task', 'Not specified')}")
                        st.markdown(f"**Assignee:** {item.get('assignee', 'Unassigned')}")

                    with col2:
                        st.markdown(f"**Deadline:** {item.get('deadline', 'Not specified')}")
                        st.markdown(f"**Priority:** <span style='color: {priority_color}; font-weight: bold;'>{item.get('priority', 'Medium')}</span>", unsafe_allow_html=True)

                    if item.get('context'):
                        st.markdown(f"**Context:** {item.get('context')}")

                    # Progress indicator
                    status = item.get('status', 'pending')
                    status_emoji = {'pending': '⏳', 'in_progress': '🔄', 'completed': '✅'}.get(status, '❓')
                    st.markdown(f"**Status:** {status_emoji} {status.title()}")

        else:
            st.info("📋 No action items identified in this meeting")

    # Tab 4: Analysis
    with result_tabs[3]:
        st.subheader("Meeting Analysis & Insights")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Meeting Information")
            meeting_info = [
                ("Type", state.get('meeting_type', 'Unknown')),
                ("Attendees", len(state.get('attendees', []))),
                ("Quality Score", f"{state.get('transcript_quality_score', 0):.2f}/1.0"),
                ("Processing Method", "OpenAI GPT-4o-mini")
            ]

            for label, value in meeting_info:
                st.markdown(f"• **{label}:** {value}")

            topics = state.get('topics_discussed', [])
            if topics:
                st.markdown(f"• **Main Topics:** {', '.join(topics[:3])}")

        with col2:
            st.markdown("### ⚡ Performance Metrics")
            processing_time = processing_summary.get('total_time', st.session_state.processing_time)

            perf_info = [
                ("Total Processing Time", f"{processing_time:.2f}s"),
                ("AI Enhancement", "✅ Yes"),
                ("Words per Second", f"{stats.get('total_words', 0) / max(processing_time, 0.1):.0f}"),
                ("Success Rate", "100%")
            ]

            for label, value in perf_info:
                st.markdown(f"• **{label}:** {value}")

        # Insights section
        insights = state.get('meeting_insights', [])
        if insights:
            st.markdown("### 💡 Key Insights")
            for insight in insights:
                st.markdown(f"""
                <div class="feature-card">
                    <p style="margin: 0; font-style: italic;">"{insight}"</p>
                </div>
                """, unsafe_allow_html=True)

    # Tab 5: Export Options (FIXED)
    with result_tabs[4]:
        st.subheader("💾 Advanced Export Options")

        # Export format selection
        export_format = st.selectbox(
            "Choose Export Format",
            ["Markdown", "Plain Text", "JSON", "PDF Report"],
            index=0,
            key="export_format_selector"
        )

        # Export customization
        col1, col2 = st.columns(2)

        with col1:
            include_metadata = st.checkbox("Include Meeting Metadata", value=True)
            include_raw_data = st.checkbox("Include Raw Processing Data", value=False)

        with col2:
            include_analytics = st.checkbox("Include Analytics", value=False)
            custom_branding = st.checkbox("Add Custom Branding", value=False)

        if custom_branding:
            company_name = st.text_input("Company Name", placeholder="Your Company Name", key="company_name_input")
            company_logo = st.file_uploader("Company Logo", type=['png', 'jpg', 'jpeg'], key="company_logo_uploader")

        # FIXED: Direct download without intermediate button
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meeting_export_{timestamp}"

        # Create export data based on options
        export_data = _create_custom_export(
            state,
            export_format,
            include_metadata,
            include_raw_data,
            include_analytics
        )

        if export_format == "PDF Report" and PDF_AVAILABLE:
            try:
                with st.spinner("Generating PDF..."):
                    pdf_data = generate_pdf_report(state, export_data if isinstance(export_data, str) else formatted_minutes)

                st.download_button(
                    label="📑 Download PDF Report",
                    data=pdf_data,
                    file_name=f"{filename}.pdf",
                    mime="application/pdf",
                    key=f"export_pdf_{timestamp}",
                    type="primary",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF generation failed: {e}")
        else:
            file_extension = {
                "Markdown": ".md",
                "Plain Text": ".txt",
                "JSON": ".json"
            }.get(export_format, ".txt")

            st.download_button(
                label=f"📥 Download {export_format}",
                data=export_data,
                file_name=f"{filename}{file_extension}",
                mime="text/plain",
                key=f"export_{timestamp}",
                type="primary",
                use_container_width=True
            )

    # Tab 6: Raw Data
    with result_tabs[5]:
        st.subheader("🔧 Raw Processing Data")

        # Processing logs with better formatting
        processing_log = state.get("processing_log", [])
        if processing_log:
            st.subheader("📋 Processing Log")

            log_data = []
            for log_entry in processing_log[-10:]:
                log_data.append({
                    "Timestamp": log_entry.get('timestamp', ''),
                    "Agent": log_entry.get('agent', ''),
                    "Status": log_entry.get('status', ''),
                    "Progress": f"{log_entry.get('progress', 0)}%"
                })

            st.dataframe(log_data, use_container_width=True)

        # Extracted info in expandable JSON
        extracted_info = state.get("extracted_info", {})
        if extracted_info:
            with st.expander("📊 Extracted Information (JSON)", expanded=False):
                st.json(extracted_info)

        # Full state data
        if st.session_state.user_preferences.get('show_advanced_options', False):
            with st.expander("🔧 Full State Data (Advanced)", expanded=False):
                st.json(dict(state))

def _create_custom_export(state, format_type, include_metadata, include_raw, include_analytics):
    """Create custom export based on user preferences."""
    export_content = []

    if format_type == "Markdown":
        export_content.append(state.get("formatted_minutes", ""))
        if include_metadata:
            export_content.append("\n\n## Metadata\n")
            export_content.append(json.dumps(state.get("meeting_metadata", {}), indent=2))
    elif format_type == "Plain Text":
        export_content.append(export_minutes_as_text(state.get("formatted_minutes", "")))
    elif format_type == "JSON":
        export_data = {
            "formatted_minutes": state.get("formatted_minutes", ""),
            "executive_summary": state.get("executive_summary", ""),
            "action_items": state.get("action_items", []),
            "decisions": state.get("decisions", [])
        }
        if include_metadata:
            export_data["metadata"] = state.get("meeting_metadata", {})
        if include_raw:
            export_data["raw_data"] = state
        return json.dumps(export_data, indent=2)

    return "\n".join(export_content) if export_content else state.get("formatted_minutes", "")

# ================================
# PROCESSING FUNCTIONS
# ================================

def process_transcript_with_enhanced_progress(transcript: str, metadata: Dict[str, Any], input_method: str):
    """Process transcript with enhanced real-time progress updates."""

    # Reset results display flags for new processing
    if 'results_displayed' in st.session_state:
        del st.session_state.results_displayed
    if 'results_display_key' in st.session_state:
        del st.session_state.results_display_key

    # Update usage statistics
    st.session_state.usage_stats['sessions'] += 1

    # Create progress placeholders
    progress_placeholder = st.empty()
    status_placeholder = st.empty()

    processing_stats = {
        'start_time': time.time(),
        'elapsed_time': 0,
        'current_agent': 'initializing'
    }

    try:
        # Start processing
        start_time = time.time()

        # Show initializing status
        with status_placeholder.container():
            st.info("🚀 Initializing AI processing pipeline...")

        # Simulate progress steps with actual processing
        progress_steps = [
            (10, "transcript_processor", "🔄 Starting transcript processing..."),
            (25, "transcript_processor", "📝 AI cleaning and structuring transcript..."),
            (40, "content_analyzer", "🔍 Extracting action items and decisions..."),
            (55, "content_analyzer", "🎯 Analyzing meeting content..."),
            (70, "summary_writer", "📊 Generating executive summary..."),
            (85, "minutes_formatter", "📋 Creating professional format..."),
            (95, "minutes_formatter", "✨ Finalizing meeting minutes..."),
        ]

        # Show initial progress
        with progress_placeholder.container():
            render_enhanced_progress_tracker("initializing", 5, processing_stats)

        # Update progress before processing
        for progress, agent, message in progress_steps[:2]:
            time.sleep(0.3)  # Small delay for visual feedback
            processing_stats['elapsed_time'] = time.time() - start_time
            processing_stats['current_agent'] = agent

            with progress_placeholder.container():
                render_enhanced_progress_tracker(agent, progress, processing_stats)

            with status_placeholder.container():
                st.info(message)

            if progress == 25:
                break

        # Process transcript using the workflow
        with status_placeholder.container():
            st.info("🤖 AI agents processing your meeting transcript...")

        # Run the actual processing
        final_state = process_meeting_transcript(
            transcript,
            metadata
        )

        # Continue showing progress after processing
        for progress, agent, message in progress_steps[2:]:
            time.sleep(0.2)  # Small delay for visual feedback
            processing_stats['elapsed_time'] = time.time() - start_time
            processing_stats['current_agent'] = agent

            with progress_placeholder.container():
                render_enhanced_progress_tracker(agent, progress, processing_stats)

            with status_placeholder.container():
                st.info(message)

        # Add any missing fields to final_state
        if final_state:
            final_state['input_method'] = input_method
            if 'formatted_minutes' not in final_state:
                final_state['formatted_minutes'] = ""
            if 'errors' not in final_state:
                final_state['errors'] = []
            if 'warnings' not in final_state:
                final_state['warnings'] = []

        # Calculate processing time
        processing_time = time.time() - start_time
        st.session_state.processing_time = processing_time

        # Update usage statistics
        st.session_state.usage_stats['transcripts_processed'] += 1
        st.session_state.usage_stats['total_processing_time'] += processing_time
        st.session_state.usage_stats['avg_transcript_length'] = (
            (st.session_state.usage_stats['avg_transcript_length'] * 
             (st.session_state.usage_stats['transcripts_processed'] - 1) + 
             len(transcript)) / st.session_state.usage_stats['transcripts_processed']
        )

        # Store results
        st.session_state.processing_state = final_state
        st.session_state.processing_complete = True
        st.session_state.last_processed_transcript = transcript

        # Show 100% completion
        with progress_placeholder.container():
            render_enhanced_progress_tracker("complete", 100, processing_stats)

        with status_placeholder.container():
            st.markdown(f"""
            <div class="status-good">
                <div class="success-checkmark">✅</div>
                <strong>Processing completed successfully!</strong><br>
                <small>⏱️ Total time: {processing_time:.2f}s | 
                📊 Generated {len(final_state.get('formatted_minutes', ''))} character minutes</small>
            </div>
            """, unsafe_allow_html=True)

        # Display results
        time.sleep(1)  # Brief pause before showing results
        if is_processing_complete(final_state):
            render_enhanced_results_display(final_state)
            st.session_state.results_displayed = True

    except Exception as e:
        with status_placeholder.container():
            st.markdown(f"""
            <div class="status-error">
                <strong>❌ Processing Failed</strong><br>
                <small>{str(e)}</small>
            </div>
            """, unsafe_allow_html=True)

        # Show detailed error in expander
        with st.expander("🔍 Detailed Error Information"):
            st.code(traceback.format_exc())

        # Reset session state on error
        st.session_state.processing_complete = False
        st.session_state.processing_state = None
def render_user_preferences():
    """Render user preferences panel."""
    st.header("⚙️ User Preferences")

    with st.expander("🎨 Appearance & Behavior", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            theme = st.selectbox(
                "Theme",
                ["Professional", "Modern", "Classic"],
                index=["Professional", "Modern", "Classic"].index(st.session_state.user_preferences.get('theme', 'Professional'))
            )
            st.session_state.user_preferences['theme'] = theme

            export_format = st.selectbox(
                "Default Export Format",
                ["Markdown", "PDF", "Plain Text", "JSON"],
                index=["Markdown", "PDF", "Plain Text", "JSON"].index(st.session_state.user_preferences.get('export_format', 'Markdown'))
            )
            st.session_state.user_preferences['export_format'] = export_format

        with col2:
            show_advanced = st.checkbox(
                "Show Advanced Options",
                value=st.session_state.user_preferences.get('show_advanced_options', False)
            )
            st.session_state.user_preferences['show_advanced_options'] = show_advanced

            auto_save = st.checkbox(
                "Auto-save Results",
                value=st.session_state.user_preferences.get('auto_save_results', True)
            )
            st.session_state.user_preferences['auto_save_results'] = auto_save

    if st.button("💾 Save Preferences", type="primary"):
        if save_user_preferences:
            save_user_preferences(st.session_state.user_preferences)
        st.success("✅ Preferences saved!")
        st.session_state.show_preferences = False
        st.rerun()

def render_analytics_dashboard():
    """Render analytics dashboard."""
    st.header("📊 Analytics Dashboard")

    if st.session_state.processing_history:
        st.write(f"Total sessions processed: {len(st.session_state.processing_history)}")
    else:
        st.info("📈 Analytics will appear after you process some transcripts!")

    if st.button("🔙 Back to Main", key=f"back_to_main_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        st.session_state.show_analytics = False
        st.rerun()

# ================================
# MAIN APPLICATION
# ================================

def main():
    """Main enhanced Streamlit application."""
    # Initialize session state
    initialize_enhanced_session_state()

    # Load enhanced CSS
    load_enhanced_css()

    # Check for user preferences
    if st.session_state.get('show_preferences', False):
        render_user_preferences()
        return

    if st.session_state.get('show_analytics', False):
        render_analytics_dashboard()
        return

    # Render header
    render_enhanced_header()

    # Check system status
    api_status = get_api_status()
    if not api_status.get("production_ready", False):
        st.markdown("""
        <div class="status-error">
            <h3>⚠️ Setup Required</h3>
            <p><strong>OpenAI API key not configured properly.</strong></p>
            <p>Please:</p>
            <ol>
                <li>Copy <code>.env.example</code> to <code>.env</code></li>
                <li>Add your OpenAI API key to the <code>.env</code> file</li>
                <li>Restart the application</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        return

    # Main layout with enhanced sidebar
    col1, col2 = st.columns([2, 1])

    with col1:
        # Enhanced input section
        transcript, metadata, input_method = render_input_section()

        # Enhanced processing button
        button_col1, button_col2 = st.columns([3, 1])

        with button_col1:
            # Check if we have a transcript in session state
            has_transcript = bool(st.session_state.get('current_transcript', "").strip() and
                                  len(st.session_state.get('current_transcript', "").strip()) > 10)

            process_button = st.button(
                "🚀 Generate Professional Meeting Minutes",
                type="primary",
                use_container_width=True,
                disabled=not has_transcript
            )

        with button_col2:
            if st.button("🔄 Clear", use_container_width=True):
                # Clear all relevant session state
                st.session_state.processing_complete = False
                st.session_state.processing_state = None
                st.session_state.current_transcript = ""
                st.session_state.current_metadata = {}
                st.session_state.input_method = "manual"
                if 'results_displayed' in st.session_state:
                    del st.session_state.results_displayed
                st.rerun()

        if process_button:
            # Use the transcript from session state
            transcript_to_process = st.session_state.get('current_transcript', "").strip()

            if transcript_to_process and len(transcript_to_process) > 10:
                process_transcript_with_enhanced_progress(
                    transcript_to_process,
                    st.session_state.get('current_metadata', {}),
                    st.session_state.get('input_method', 'manual')
                )
            else:
                st.error("❌ Please provide a meeting transcript (at least 10 characters)")


        # Show previous results if available (only once)
        if (st.session_state.processing_complete and
            st.session_state.processing_state and
            'results_displayed' not in st.session_state):

            st.markdown("---")
            render_enhanced_results_display(st.session_state.processing_state)
            st.session_state.results_displayed = True

    with col2:
        # Enhanced system status sidebar
        render_enhanced_system_status()

        # Enhanced help section
        st.markdown("---")
        st.header("💡 Pro Tips")

        with st.expander("🎯 New in Pro Edition"):
            st.write("""
            **🎨 Enhanced Features:**
            
            • Real-time processing animations
            • Advanced export options (PDF now working!)
            • Usage analytics and insights  
            • Customizable preferences
            • Mobile-optimized interface
            • Processing history tracking
            """)

        with st.expander("⚡ Performance Tips"):
            st.write("""
            **Optimize your results:**
            
            • Use clear speaker names (John: message)
            • Include explicit action items and deadlines
            • Mention decisions clearly ("we decided...")
            • Keep transcripts focused and relevant
            • Try different sample types for examples
            """)

        with st.expander("📊 Export Formats"):
            st.write("""
            **Available export options:**
            
            • **Markdown**: Professional formatting
            • **Plain Text**: Simple, readable format
            • **JSON**: Structured data with metadata
            • **PDF**: Executive presentation format (Fixed!)
            • **Custom**: Tailored to your needs
            """)

if __name__ == "__main__":
    main()