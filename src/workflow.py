

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from utils.state_models import (
    MeetingState,
    create_initial_state,
    update_agent_status,
    add_error,
    add_warning,
    is_processing_complete,
    calculate_progress,
    get_processing_summary
)
from agents.transcript_processor import process_transcript
from agents.content_analyzer import analyze_content
from agents.summary_writer import write_summary
from agents.minutes_formatter import format_minutes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MeetingMinutesWorkflow:
    """
    LangGraph workflow for Meeting Minutes Generator.
    Orchestrates four AI agents to process meeting transcripts.
    """

    def __init__(self):
        """Initialize the workflow with all agents and graph structure."""
        self.graph = None
        self.compiled_workflow = None
        self._setup_workflow()

    def _setup_workflow(self):
        """Set up the LangGraph workflow with all agents and connections."""
        logger.info("Setting up Meeting Minutes LangGraph workflow...")

        # Create the state graph
        self.graph = StateGraph(MeetingState)

        # Add all agent nodes
        self.graph.add_node("transcript_processor", self._transcript_processor_node)
        self.graph.add_node("content_analyzer", self._content_analyzer_node)
        self.graph.add_node("summary_writer", self._summary_writer_node)
        self.graph.add_node("minutes_formatter", self._minutes_formatter_node)

        # Define the workflow edges (sequential processing)
        self.graph.add_edge("transcript_processor", "content_analyzer")
        self.graph.add_edge("content_analyzer", "summary_writer")
        self.graph.add_edge("summary_writer", "minutes_formatter")
        self.graph.add_edge("minutes_formatter", END)

        # Set entry point
        self.graph.set_entry_point("transcript_processor")

        # Compile the workflow
        try:
            self.compiled_workflow = self.graph.compile()
            logger.info("✅ LangGraph workflow compiled successfully")
        except Exception as e:
            logger.error(f"❌ Failed to compile workflow: {e}")
            raise

    def _transcript_processor_node(self, state: MeetingState) -> MeetingState:
        """
        Node wrapper for transcript processor agent.
        Handles logging, timing, and error management.
        """
        agent_name = "transcript_processor"
        logger.info(f"🤖 Starting {agent_name}")

        start_time = time.time()

        try:
            # Update status to processing
            state = update_agent_status(state, agent_name, "processing", 10)

            # Call the actual agent
            result_state = process_transcript(state)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Update status to complete
            result_state = update_agent_status(
                result_state,
                agent_name,
                "complete",
                25,
                processing_time
            )

            logger.info(f"✅ {agent_name} completed in {processing_time:.2f}s")
            return result_state

        except Exception as e:
            logger.error(f"❌ {agent_name} failed: {e}")
            error_state = add_error(
                state,
                agent_name,
                "processing_error",
                str(e),
                recoverable=False
            )
            return error_state

    def _content_analyzer_node(self, state: MeetingState) -> MeetingState:
        """
        Node wrapper for content analyzer agent.
        Handles logging, timing, and error management.
        """
        agent_name = "content_analyzer"
        logger.info(f"🔍 Starting {agent_name}")

        start_time = time.time()

        try:
            # Check if previous step completed successfully
            if not state.get("cleaned_transcript"):
                error_msg = "No cleaned transcript available from previous step"
                logger.error(error_msg)
                return add_error(state, agent_name, "dependency_error", error_msg, False)

            # Update status to processing
            state = update_agent_status(state, agent_name, "processing", 35)

            # Call the actual agent
            result_state = analyze_content(state)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Update status to complete
            result_state = update_agent_status(
                result_state,
                agent_name,
                "complete",
                50,
                processing_time
            )

            logger.info(f"✅ {agent_name} completed in {processing_time:.2f}s")
            return result_state

        except Exception as e:
            logger.error(f"❌ {agent_name} failed: {e}")
            error_state = add_error(
                state,
                agent_name,
                "processing_error",
                str(e),
                recoverable=False
            )
            return error_state

    def _summary_writer_node(self, state: MeetingState) -> MeetingState:
        """
        Node wrapper for summary writer agent.
        Handles logging, timing, and error management.
        """
        agent_name = "summary_writer"
        logger.info(f"📝 Starting {agent_name}")

        start_time = time.time()

        try:
            # Check if previous steps completed successfully
            if not state.get("cleaned_transcript") or not state.get("extracted_info"):
                error_msg = "Missing required data from previous steps"
                logger.error(error_msg)
                return add_error(state, agent_name, "dependency_error", error_msg, False)

            # Update status to processing
            state = update_agent_status(state, agent_name, "processing", 60)

            # Call the actual agent
            result_state = write_summary(state)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Update status to complete
            result_state = update_agent_status(
                result_state,
                agent_name,
                "complete",
                75,
                processing_time
            )

            logger.info(f"✅ {agent_name} completed in {processing_time:.2f}s")
            return result_state

        except Exception as e:
            logger.error(f"❌ {agent_name} failed: {e}")
            error_state = add_error(
                state,
                agent_name,
                "processing_error",
                str(e),
                recoverable=False
            )
            return error_state

    def _minutes_formatter_node(self, state: MeetingState) -> MeetingState:
        """
        Node wrapper for minutes formatter agent.
        Handles logging, timing, and error management.
        """
        agent_name = "minutes_formatter"
        logger.info(f"📋 Starting {agent_name}")

        start_time = time.time()

        try:
            # Check if all previous steps completed successfully
            required_fields = ["cleaned_transcript", "extracted_info", "executive_summary"]
            missing_fields = [field for field in required_fields if not state.get(field)]

            if missing_fields:
                error_msg = f"Missing required data: {missing_fields}"
                logger.error(error_msg)
                return add_error(state, agent_name, "dependency_error", error_msg, False)

            # Update status to processing
            state = update_agent_status(state, agent_name, "processing", 85)

            # Call the actual agent
            result_state = format_minutes(state)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Update status to complete and finalize
            result_state = update_agent_status(
                result_state,
                agent_name,
                "complete",
                100,
                processing_time
            )

            # Mark overall processing as complete
            result_state["processing_status"] = "complete"
            result_state["completion_timestamp"] = datetime.now().isoformat()

            # Calculate total processing time
            if result_state.get("agent_processing_times"):
                total_time = sum(result_state["agent_processing_times"].values())
                result_state["processing_time"] = total_time

            logger.info(f"✅ {agent_name} completed in {processing_time:.2f}s")
            logger.info("🎉 All agents completed successfully!")
            return result_state

        except Exception as e:
            logger.error(f"❌ {agent_name} failed: {e}")
            error_state = add_error(
                state,
                agent_name,
                "processing_error",
                str(e),
                recoverable=False
            )
            return error_state

    def _create_empty_transcript_response(self, transcript: str, metadata: Optional[Dict[str, Any]], input_method: str) -> MeetingState:
        """Create a proper response for empty or insufficient transcripts."""
        logger.info("Creating response for empty/insufficient transcript")

        empty_state = create_initial_state(transcript or "", metadata or {}, input_method)
        empty_state["processing_status"] = "completed_with_warnings"
        empty_state["progress_percentage"] = 100
        empty_state["current_agent"] = "workflow"

        # Set all agent statuses to complete (since we're bypassing them)
        empty_state["agent_statuses"] = {
            "transcript_processor": "skipped",
            "content_analyzer": "skipped",
            "summary_writer": "skipped",
            "minutes_formatter": "complete"
        }

        # Create minimal but proper meeting minutes
        meeting_date = metadata.get("date", datetime.now().strftime("%Y-%m-%d")) if metadata else datetime.now().strftime("%Y-%m-%d")

        empty_state["formatted_minutes"] = f"""# Meeting Minutes

**Date:** {meeting_date}  
**Status:** Insufficient content provided

## Summary

No substantial meeting content was available for processing. Please provide a meeting transcript with actual conversation content to generate comprehensive meeting minutes.

## Action Items

No action items could be identified from the provided content.

## Decisions Made

No decisions could be identified from the provided content.

## Next Steps

1. Provide meeting transcript content with actual conversation
2. Ensure transcript includes speaker names and dialogue
3. Re-run processing for comprehensive meeting minutes

---

*Generated by AI Meeting Assistant on {datetime.now().strftime("%Y-%m-%d at %H:%M")}*
"""

        # Set other required fields
        empty_state["executive_summary"] = "Meeting content insufficient for analysis."
        empty_state["meeting_overview"] = "No substantial content provided for processing."
        empty_state["cleaned_transcript"] = transcript or ""
        empty_state["action_items"] = []
        empty_state["decisions"] = []
        empty_state["key_points"] = []
        empty_state["attendees"] = []
        empty_state["meeting_type"] = "Unspecified"
        empty_state["completion_timestamp"] = datetime.now().isoformat()

        # Add a warning
        empty_state = add_warning(empty_state, "workflow", "Empty or insufficient transcript provided")

        return empty_state

    def process_transcript(
        self,
        transcript: str,
        metadata: Optional[Dict[str, Any]] = None,
        input_method: str = "unknown"
    ) -> MeetingState:
        """
        Process a meeting transcript through the complete workflow.

        Args:
            transcript: Raw meeting transcript text
            metadata: Optional metadata about the meeting
            input_method: How the transcript was provided

        Returns:
            Final state with processed meeting minutes
        """
        logger.info("🚀 Starting meeting transcript processing workflow")

        try:
            # Enhanced input validation with proper empty handling
            if not transcript or not isinstance(transcript, str):
                logger.warning("No transcript provided")
                return self._create_empty_transcript_response("", metadata, input_method)

            transcript_clean = transcript.strip()
            if len(transcript_clean) < 10:
                logger.warning(f"Transcript too short ({len(transcript_clean)} chars), insufficient for processing")
                return self._create_empty_transcript_response(transcript, metadata, input_method)

            # Create initial state with validated input
            initial_state = create_initial_state(transcript_clean, metadata or {}, input_method)

            # Log processing start
            logger.info(f"Processing transcript ({len(transcript_clean)} characters)")
            if metadata:
                logger.info(f"Meeting metadata: {metadata}")

            # Execute the workflow
            final_state = self.compiled_workflow.invoke(initial_state)

            # Log completion
            if is_processing_complete(final_state):
                summary = get_processing_summary(final_state)
                logger.info(f"✅ Workflow completed successfully in {summary['total_time']:.2f}s")
                logger.info(f"📊 Processing summary: {summary}")
            else:
                logger.warning("⚠️ Workflow completed with issues")

            return final_state

        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {e}")
            # Create error response with minimal minutes
            error_state = create_initial_state(transcript or "", metadata or {}, input_method)
            error_state = add_error(error_state, "workflow", "execution_error", str(e), False)
            error_state["formatted_minutes"] = f"""# Meeting Minutes

**Date:** {metadata.get('date', datetime.now().strftime('%Y-%m-%d')) if metadata else datetime.now().strftime('%Y-%m-%d')}  
**Status:** Processing error occurred

## Summary

An error occurred during meeting minutes processing: {str(e)}

## Next Steps

Please try again or contact support if the issue persists.

---

*Generated by AI Meeting Assistant on {datetime.now().strftime('%Y-%m-%d at %H:%M')}*
"""
            return error_state

    def process_sample(self, sample_key: str) -> MeetingState:
        """
        Process a sample transcript from the sample data.

        Args:
            sample_key: Key for the sample transcript

        Returns:
            Final state with processed meeting minutes
        """
        try:
            from sample_data.sample_transcripts import get_sample_transcript

            sample = get_sample_transcript(sample_key)
            if not sample:
                logger.error(f"Sample '{sample_key}' not found")
                error_state = create_initial_state("", {}, "sample")
                return add_error(error_state, "workflow", "sample_error", f"Sample '{sample_key}' not found", False)

            logger.info(f"🎯 Processing sample: {sample.get('title', sample_key)}")

            return self.process_transcript(
                transcript=sample["transcript"],
                metadata=sample.get("metadata", {}),
                input_method=f"sample_{sample_key}"
            )

        except Exception as e:
            logger.error(f"❌ Sample processing failed: {e}")
            error_state = create_initial_state("", {}, "sample")
            return add_error(error_state, "workflow", "sample_error", str(e), False)

    def get_workflow_info(self) -> Dict[str, Any]:
        """
        Get information about the workflow structure.

        Returns:
            Dictionary with workflow information
        """
        return {
            "agents": ["transcript_processor", "content_analyzer", "summary_writer", "minutes_formatter"],
            "workflow_type": "sequential",
            "total_nodes": 4,
            "entry_point": "transcript_processor",
            "compiled": self.compiled_workflow is not None,
            "description": "AI-powered meeting minutes generator using LangGraph orchestration"
        }

# ================================
# GLOBAL WORKFLOW INSTANCE
# ================================

# Create global workflow instance
_workflow_instance = None

def get_workflow() -> MeetingMinutesWorkflow:
    """
    Get or create the global workflow instance.

    Returns:
        MeetingMinutesWorkflow instance
    """
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = MeetingMinutesWorkflow()
    return _workflow_instance

def process_meeting_transcript(
    transcript: str,
    metadata: Optional[Dict[str, Any]] = None,
    input_method: str = "api"
) -> MeetingState:
    """
    Convenience function to process a meeting transcript.

    Args:
        transcript: Raw meeting transcript
        metadata: Optional meeting metadata
        input_method: How the transcript was provided

    Returns:
        Final processing state
    """
    workflow = get_workflow()
    return workflow.process_transcript(transcript, metadata, input_method)

def process_sample_transcript(sample_key: str) -> MeetingState:
    """
    Convenience function to process a sample transcript.

    Args:
        sample_key: Key for sample transcript

    Returns:
        Final processing state
    """
    workflow = get_workflow()
    return workflow.process_sample(sample_key)

# ================================
# TESTING AND DEBUGGING
# ================================

def test_workflow_compilation():
    """Test that the workflow compiles without errors."""
    try:
        workflow = MeetingMinutesWorkflow()
        info = workflow.get_workflow_info()
        logger.info(f"✅ Workflow compilation test passed: {info}")
        return True
    except Exception as e:
        logger.error(f"❌ Workflow compilation test failed: {e}")
        return False

def debug_workflow_state(state: MeetingState) -> Dict[str, Any]:
    """
    Get debug information about a workflow state.

    Args:
        state: Workflow state to debug

    Returns:
        Debug information dictionary
    """
    return {
        "processing_status": state.get("processing_status"),
        "current_agent": state.get("current_agent"),
        "progress": calculate_progress(state),
        "agent_statuses": state.get("agent_statuses"),
        "error_count": len(state.get("errors", [])),
        "warning_count": len(state.get("warnings", [])),
        "has_transcript": bool(state.get("raw_transcript")),
        "has_cleaned": bool(state.get("cleaned_transcript")),
        "has_extracted": bool(state.get("extracted_info")),
        "has_summary": bool(state.get("executive_summary")),
        "has_minutes": bool(state.get("formatted_minutes")),
        "is_complete": is_processing_complete(state)
    }

def test_empty_transcript_handling():
    """Test empty transcript handling specifically."""
    try:
        logger.info("Testing empty transcript handling...")

        # Test completely empty
        result1 = process_meeting_transcript("", {}, "test")
        assert result1.get("formatted_minutes"), "Empty transcript should still produce minutes"

        # Test whitespace only
        result2 = process_meeting_transcript("   \n  \t  ", {}, "test")
        assert result2.get("formatted_minutes"), "Whitespace transcript should still produce minutes"

        # Test very short
        result3 = process_meeting_transcript("Hi.", {}, "test")
        assert result3.get("formatted_minutes"), "Short transcript should still produce minutes"

        logger.info("✅ Empty transcript handling tests passed")
        return True

    except Exception as e:
        logger.error(f"❌ Empty transcript handling test failed: {e}")
        return False

if __name__ == "__main__":
    # Test the workflow
    print("Testing workflow compilation...")
    if test_workflow_compilation():
        print("✅ Workflow compilation successful")

        print("Testing empty transcript handling...")
        if test_empty_transcript_handling():
            print("✅ Empty transcript handling successful")
        else:
            print("❌ Empty transcript handling failed")
    else:
        print("❌ Workflow compilation failed")