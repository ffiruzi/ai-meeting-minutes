"""
AI Agents package for Meeting Minutes Generator.
Contains the four specialized agents for transcript processing.

Day 4 Implementation: All agents are now fully implemented with OpenAI GPT-4o-mini
integration, providing production-ready AI-powered processing capabilities.
"""

from .transcript_processor import process_transcript, test_transcript_processor
from .content_analyzer import analyze_content, test_content_analyzer
from .summary_writer import write_summary, test_summary_writer
from .minutes_formatter import format_minutes, test_minutes_formatter, get_minutes_statistics

__all__ = [
    # Agent functions
    "process_transcript",
    "analyze_content",
    "write_summary",
    "format_minutes",

    # Testing functions
    "test_transcript_processor",
    "test_content_analyzer",
    "test_summary_writer",
    "test_minutes_formatter",

    # Utility functions
    "get_minutes_statistics"
]

# Agent metadata for workflow information - UPDATED for Day 4
AGENT_INFO = {
    "transcript_processor": {
        "name": "Transcript Processor",
        "description": "AI-powered transcript cleaning and speaker identification using OpenAI GPT-4o-mini",
        "input_fields": ["raw_transcript"],
        "output_fields": ["cleaned_transcript", "speaker_identification", "transcript_quality_score", "processing_notes"],
        "status": "ai_enhanced_complete",
        "ai_model": "openai_gpt4o_mini",
        "capabilities": ["filler_word_removal", "error_correction", "speaker_identification", "quality_assessment"]
    },
    "content_analyzer": {
        "name": "Content Analyzer",
        "description": "AI-powered information extraction with context-aware analysis using OpenAI GPT-4o-mini",
        "input_fields": ["cleaned_transcript"],
        "output_fields": ["extracted_info", "action_items", "decisions", "key_points", "attendees", "meeting_type", "topics_discussed", "deadlines_mentioned"],
        "status": "ai_enhanced_complete",
        "ai_model": "openai_gpt4o_mini",
        "capabilities": ["action_item_extraction", "decision_identification", "meeting_type_detection", "deadline_parsing", "context_analysis"]
    },
    "summary_writer": {
        "name": "Summary Writer",
        "description": "AI-powered executive summary generation with strategic business focus using OpenAI GPT-4o-mini",
        "input_fields": ["cleaned_transcript", "extracted_info", "action_items", "decisions", "key_points"],
        "output_fields": ["executive_summary", "meeting_overview", "key_outcomes", "next_steps_summary", "meeting_insights", "stakeholder_impact"],
        "status": "ai_enhanced_complete",
        "ai_model": "openai_gpt4o_mini",
        "capabilities": ["executive_summaries", "strategic_analysis", "stakeholder_impact", "business_insights", "next_steps_planning"]
    },
    "minutes_formatter": {
        "name": "Minutes Formatter",
        "description": "AI-powered professional meeting minutes generation with corporate formatting using OpenAI GPT-4o-mini",
        "input_fields": ["executive_summary", "meeting_overview", "key_outcomes", "action_items", "decisions", "meeting_metadata"],
        "output_fields": ["formatted_minutes", "minutes_sections", "action_items_table", "decisions_list", "attendees_list"],
        "status": "ai_enhanced_complete",
        "ai_model": "openai_gpt4o_mini",
        "capabilities": ["professional_formatting", "markdown_generation", "table_creation", "modular_sections", "executive_ready_output"]
    }
}

def get_agent_info(agent_name: str = None):
    """
    Get information about agents.

    Args:
        agent_name: Specific agent name, or None for all agents

    Returns:
        Agent information dictionary
    """
    if agent_name:
        return AGENT_INFO.get(agent_name, {})
    return AGENT_INFO

def test_all_agents():
    """
    Test all agents with sample data.

    Returns:
        Dictionary with test results for all agents
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.info("🧪 Testing all AI-enhanced agents...")

    results = {}

    # Test each agent with enhanced validation
    test_functions = [
        ("transcript_processor", test_transcript_processor),
        ("content_analyzer", test_content_analyzer),
        ("summary_writer", test_summary_writer),
        ("minutes_formatter", test_minutes_formatter)
    ]

    for agent_name, test_func in test_functions:
        try:
            logger.info(f"Testing AI-enhanced {agent_name}...")
            result = test_func()
            results[agent_name] = result

            # Enhanced status reporting for AI agents
            success = result.get("success", False)
            ai_enhanced = result.get("ai_enhanced", False)

            if success and ai_enhanced:
                status = "✅ PASS (AI Enhanced)"
            elif success:
                status = "⚠️ PASS (Fallback)"
            else:
                status = "❌ FAIL"

            logger.info(f"{status} - {agent_name}")

        except Exception as e:
            results[agent_name] = {"success": False, "ai_enhanced": False, "error": str(e)}
            logger.error(f"❌ FAIL - {agent_name}: {e}")

    # Enhanced summary with AI status
    passed = sum(1 for r in results.values() if r.get("success"))
    ai_enhanced = sum(1 for r in results.values() if r.get("success") and r.get("ai_enhanced"))
    total = len(results)

    logger.info(f"Agent tests completed: {passed}/{total} passed, {ai_enhanced}/{total} AI-enhanced")

    return {
        "results": results,
        "summary": {
            "total_agents": total,
            "passed": passed,
            "failed": total - passed,
            "ai_enhanced": ai_enhanced,
            "success_rate": f"{(passed/total)*100:.1f}%",
            "ai_enhancement_rate": f"{(ai_enhanced/total)*100:.1f}%",
            "production_ready": ai_enhanced == total
        }
    }

def get_system_status():
    """
    Get overall system status and capabilities.

    Returns:
        System status dictionary
    """
    return {
        "system_name": "Meeting Minutes Generator",
        "version": "1.0.0",
        "development_day": "Day 4 Complete",
        "total_agents": 4,
        "ai_enhanced_agents": 4,
        "status": "production_ready",
        "capabilities": [
            "AI-powered transcript cleaning",
            "Context-aware content extraction",
            "Executive-level summary generation",
            "Professional meeting minutes formatting",
            "Multi-format export support",
            "Real-time progress tracking",
            "Error-resilient processing"
        ],
        "ai_models": {
            "primary": "openai_gpt4o_mini",
            "fallback": "pattern_matching"
        },
        "output_quality": "executive_ready",
        "processing_speed": "production_optimized",
        "reliability": "enterprise_grade"
    }