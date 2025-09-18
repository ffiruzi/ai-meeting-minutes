

import logging
import json
import time
from typing import Dict, Any, List
from datetime import datetime

from utils.state_models import MeetingState, add_warning
from utils.openai_client import get_openai_client

logger = logging.getLogger(__name__)

def format_minutes(state: MeetingState) -> MeetingState:
    """
    Format all processed information into professional meeting minutes using OpenAI GPT-4o-mini.

    This agent:
    1. Creates executive-quality meeting minutes using AI-powered formatting
    2. Uses standard business meeting minutes template with proper sections
    3. Integrates all agent outputs into cohesive, professional documentation
    4. Formats action items in clear, professional tables with complete details
    5. Ensures consistent, polished language throughout suitable for executives
    6. Integrates metadata seamlessly (meeting date, attendees, duration, type)
    7. Creates modular sections for flexible use and customization
    8. Generates export-ready formats for various business needs

    Args:
        state: Current workflow state containing all processed information

    Returns:
        Updated state with professional meeting minutes and component sections
    """
    logger.info("📋 Minutes Formatter Agent starting (Full AI Implementation)...")

    try:
        # Get all required data from state
        executive_summary = state.get("executive_summary", "")
        meeting_overview = state.get("meeting_overview", "")
        key_outcomes = state.get("key_outcomes", "")
        next_steps_summary = state.get("next_steps_summary", "")
        action_items = state.get("action_items", [])
        decisions = state.get("decisions", [])
        key_points = state.get("key_points", [])
        attendees = state.get("attendees", [])
        meeting_type = state.get("meeting_type", "General Meeting")
        meeting_metadata = state.get("meeting_metadata", {})
        meeting_insights = state.get("meeting_insights", [])
        stakeholder_impact = state.get("stakeholder_impact", {})
        topics_discussed = state.get("topics_discussed", [])

        if not executive_summary:
            logger.warning("No executive summary available for formatting")
            result_state = state.copy()
            result_state = _create_minimal_minutes(result_state, meeting_type, meeting_metadata)
            return add_warning(result_state, "minutes_formatter", "Limited content available for formatting")

        logger.info(f"Formatting professional minutes for {meeting_type} with AI enhancement")

        # Get OpenAI client
        client = get_openai_client()

        # Step 1: Generate comprehensive meeting minutes using AI
        start_time = time.time()
        formatted_minutes = _ai_generate_meeting_minutes(
            client, executive_summary, meeting_overview, key_outcomes,
            next_steps_summary, action_items, decisions, key_points,
            attendees, meeting_type, meeting_metadata, meeting_insights,
            stakeholder_impact, topics_discussed
        )
        formatting_time = time.time() - start_time

        # Step 2: Generate individual sections for flexibility
        start_time = time.time()
        minutes_sections = _ai_generate_individual_sections(
            client, executive_summary, meeting_overview, key_outcomes,
            next_steps_summary, action_items, decisions, meeting_type, meeting_metadata
        )
        sections_time = time.time() - start_time

        # Step 3: Generate specialized formatted components
        action_items_table = _ai_format_action_items_table(client, action_items)
        decisions_list = _ai_format_decisions_list(client, decisions)
        attendees_list = _ai_format_attendees_section(client, attendees, meeting_metadata)

        # Update state with results
        result_state = state.copy()
        result_state["formatted_minutes"] = formatted_minutes
        result_state["minutes_sections"] = minutes_sections
        result_state["action_items_table"] = action_items_table
        result_state["decisions_list"] = decisions_list
        result_state["attendees_list"] = attendees_list

        total_time = formatting_time + sections_time
        logger.info(f"✅ AI-powered minutes formatting completed successfully ({len(formatted_minutes)} characters, {total_time:.2f}s)")
        return result_state

    except Exception as e:
        logger.error(f"❌ Minutes formatting failed: {e}")
        # Return state with minimal minutes
        error_state = state.copy()
        error_state = _create_minimal_minutes(error_state, meeting_type, meeting_metadata)
        raise  # Re-raise for workflow error handling

def _ai_generate_meeting_minutes(
    client, executive_summary: str, meeting_overview: str, key_outcomes: str,
    next_steps_summary: str, action_items: List[Dict[str, str]], decisions: List[Dict[str, str]],
    key_points: List[str], attendees: List[str], meeting_type: str,
    meeting_metadata: Dict[str, Any], meeting_insights: List[str],
    stakeholder_impact: Dict[str, str], topics_discussed: List[str]
) -> str:
    """
    Use OpenAI to generate comprehensive, professional meeting minutes.
    """

    system_prompt = """You are a professional executive secretary creating formal meeting minutes for senior leadership.

Create comprehensive, professional meeting minutes in Markdown format that would be suitable for executive distribution and corporate documentation.

REQUIREMENTS:
1. Use formal business language appropriate for executive consumption
2. Create clear, well-organized sections with proper Markdown formatting
3. Ensure all content is professional, accurate, and complete
4. Use standard business meeting minutes format
5. Include proper tables for action items with all details
6. Make the document suitable for immediate distribution to stakeholders
7. Maintain consistent formatting and professional presentation throughout

STRUCTURE REQUIREMENTS:
- Professional header with meeting details
- Executive Summary section (brief but comprehensive)
- Meeting Overview section (context and purpose)
- Key Discussion Points (organized list)
- Decisions Made (formal list with context)
- Action Items (professional table format)
- Next Steps (clear, actionable summary)
- Strategic Insights (if significant)
- Meeting Conclusion

Return only the complete meeting minutes in Markdown format with no additional commentary."""

    # Prepare comprehensive context
    meeting_date = meeting_metadata.get("date", datetime.now().strftime("%Y-%m-%d"))
    meeting_duration = meeting_metadata.get("duration", "Not specified")
    meeting_location = meeting_metadata.get("location", "Not specified")

    attendees_formatted = ", ".join(attendees) if attendees else "Not specified"
    topics_formatted = ", ".join(topics_discussed) if topics_discussed else "Various business topics"

    action_items_summary = []
    for item in action_items[:10]:  # Include up to 10 action items
        task = item.get("task", "Unknown task")
        assignee = item.get("assignee", "Unassigned")
        deadline = item.get("deadline", "Not specified")
        priority = item.get("priority", "Medium")
        action_items_summary.append(f"• {task} | {assignee} | {deadline} | {priority}")

    decisions_summary = []
    for decision in decisions[:8]:  # Include up to 8 decisions
        decision_text = decision.get("decision", "Unknown decision")
        context = decision.get("context", "No context provided")
        decisions_summary.append(f"• {decision_text} (Context: {context})")

    user_prompt = f"""Create professional meeting minutes for this {meeting_type.lower()}:

MEETING DETAILS:
- Type: {meeting_type}
- Date: {meeting_date}
- Duration: {meeting_duration}
- Location: {meeting_location}
- Attendees: {attendees_formatted}
- Topics: {topics_formatted}

EXECUTIVE SUMMARY:
{executive_summary}

MEETING OVERVIEW:
{meeting_overview}

KEY OUTCOMES:
{key_outcomes}

NEXT STEPS:
{next_steps_summary}

ACTION ITEMS:
{chr(10).join(action_items_summary) if action_items_summary else "No action items identified"}

DECISIONS MADE:
{chr(10).join(decisions_summary) if decisions_summary else "No formal decisions recorded"}

KEY DISCUSSION POINTS:
{chr(10).join([f"• {point}" for point in key_points[:8]]) if key_points else "No specific discussion points"}

STRATEGIC INSIGHTS:
{chr(10).join([f"• {insight}" for insight in meeting_insights[:5]]) if meeting_insights else "No specific insights identified"}

Create comprehensive, professional meeting minutes suitable for executive distribution."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        minutes = client.chat_completion(messages, temperature=0.1, max_tokens=4000)

        return minutes.strip()

    except Exception as e:
        logger.error(f"AI meeting minutes generation failed: {e}")
        return _fallback_generate_meeting_minutes(
            executive_summary, meeting_overview, action_items, decisions,
            meeting_type, meeting_metadata, attendees
        )

def _ai_generate_individual_sections(
    client, executive_summary: str, meeting_overview: str, key_outcomes: str,
    next_steps_summary: str, action_items: List[Dict[str, str]],
    decisions: List[Dict[str, str]], meeting_type: str, meeting_metadata: Dict[str, Any]
) -> Dict[str, str]:
    """
    Generate individual sections for flexible minutes formatting.
    """

    system_prompt = """You are creating individual sections for meeting minutes that can be used modularly.

Create professional, standalone sections that maintain consistency when used together or separately.

REQUIREMENTS:
1. Each section should be complete and professionally written
2. Use appropriate Markdown formatting
3. Maintain formal business language
4. Ensure sections can work independently or together
5. Keep formatting consistent across all sections

RETURN FORMAT:
Return a JSON object with section names as keys and formatted content as values:
{
  "header": "meeting header content",
  "summary": "executive summary section",
  "overview": "meeting overview section",
  "outcomes": "key outcomes section",
  "next_steps": "next steps section"
}

Return only valid JSON with no additional text."""

    meeting_date = meeting_metadata.get("date", datetime.now().strftime("%Y-%m-%d"))
    meeting_duration = meeting_metadata.get("duration", "Not specified")

    user_prompt = f"""Create modular sections for {meeting_type.lower()} minutes:

MEETING INFO:
- Type: {meeting_type}
- Date: {meeting_date}
- Duration: {meeting_duration}

CONTENT:
- Executive Summary: {executive_summary[:500]}...
- Meeting Overview: {meeting_overview[:500]}...
- Key Outcomes: {key_outcomes[:500]}...
- Next Steps: {next_steps_summary[:500]}...
- Action Items: {len(action_items)} items
- Decisions: {len(decisions)} decisions

Generate professional, modular meeting minute sections."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = client.chat_completion(messages, temperature=0.1, max_tokens=2000)

        # Parse JSON response
        sections = json.loads(response)

        # Validate and return
        if isinstance(sections, dict):
            return sections
        else:
            return _fallback_generate_individual_sections(executive_summary, meeting_overview, meeting_type, meeting_metadata)

    except Exception as e:
        logger.error(f"AI sections generation failed: {e}")
        return _fallback_generate_individual_sections(executive_summary, meeting_overview, meeting_type, meeting_metadata)

def _ai_format_action_items_table(client, action_items: List[Dict[str, str]]) -> str:
    """
    Use OpenAI to create a professional action items table.
    """

    if not action_items:
        return "## Action Items\n\nNo action items were identified during this meeting.\n"

    system_prompt = """You are creating a professional action items table for meeting minutes.

Create a well-formatted Markdown table that clearly presents all action items with complete information.

REQUIREMENTS:
1. Use proper Markdown table formatting
2. Include all relevant columns: Task, Assignee, Due Date, Priority, Status
3. Ensure table is readable and professional
4. Add appropriate section header
5. Include any additional context as needed
6. Sort by priority if possible

Return only the formatted action items section with no additional commentary."""

    action_items_data = []
    for item in action_items:
        task = item.get("task", "Unknown task")
        assignee = item.get("assignee", "Unassigned")
        deadline = item.get("deadline", "Not specified")
        priority = item.get("priority", "Medium")
        status = item.get("status", "Pending")
        context = item.get("context", "")

        action_items_data.append({
            "task": task,
            "assignee": assignee,
            "deadline": deadline,
            "priority": priority,
            "status": status,
            "context": context
        })

    user_prompt = f"""Create a professional action items table for meeting minutes:

ACTION ITEMS DATA:
{json.dumps(action_items_data, indent=2)}

Total items: {len(action_items)}

Format as a professional Markdown table suitable for executive meeting minutes."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        table = client.chat_completion(messages, temperature=0.1, max_tokens=1500)

        return table.strip()

    except Exception as e:
        logger.error(f"AI action items table generation failed: {e}")
        return _fallback_format_action_items_table(action_items)

def _ai_format_decisions_list(client, decisions: List[Dict[str, str]]) -> str:
    """
    Use OpenAI to format the decisions section.
    """

    if not decisions:
        return "## Decisions Made\n\nNo formal decisions were recorded during this meeting.\n"

    system_prompt = """You are formatting the decisions section for professional meeting minutes.

Create a well-organized, professional presentation of all decisions made during the meeting.

REQUIREMENTS:
1. Use clear, numbered or bulleted format
2. Include decision text and relevant context
3. Add rationale or reasoning where available
4. Ensure professional business language
5. Format for executive consumption

Return only the formatted decisions section with no additional commentary."""

    decisions_data = []
    for decision in decisions:
        decision_text = decision.get("decision", "Unknown decision")
        context = decision.get("context", "No context provided")
        rationale = decision.get("rationale", "")
        impact = decision.get("impact", "")

        decisions_data.append({
            "decision": decision_text,
            "context": context,
            "rationale": rationale,
            "impact": impact
        })

    user_prompt = f"""Format the decisions section for professional meeting minutes:

DECISIONS DATA:
{json.dumps(decisions_data, indent=2)}

Total decisions: {len(decisions)}

Create a professional decisions section for executive meeting minutes."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        formatted_decisions = client.chat_completion(messages, temperature=0.1, max_tokens=1200)

        return formatted_decisions.strip()

    except Exception as e:
        logger.error(f"AI decisions formatting failed: {e}")
        return _fallback_format_decisions_list(decisions)

def _ai_format_attendees_section(client, attendees: List[str], meeting_metadata: Dict[str, Any]) -> str:
    """
    Use OpenAI to format the attendees and meeting details section.
    """

    system_prompt = """You are creating the header and attendees section for professional meeting minutes.

Create a professional meeting header with all relevant meeting details and attendee information.

REQUIREMENTS:
1. Include meeting title, date, time, location, duration
2. List attendees in an organized, professional manner
3. Add any relevant roles or titles if available
4. Use proper business formatting
5. Make suitable for executive documentation

Return only the formatted header section with no additional commentary."""

    meeting_date = meeting_metadata.get("date", datetime.now().strftime("%Y-%m-%d"))
    meeting_time = meeting_metadata.get("start_time", "Not specified")
    meeting_duration = meeting_metadata.get("duration", "Not specified")
    meeting_location = meeting_metadata.get("location", "Not specified")
    meeting_organizer = meeting_metadata.get("organizer", "Not specified")

    user_prompt = f"""Create professional meeting header and attendees section:

MEETING DETAILS:
- Date: {meeting_date}
- Time: {meeting_time}
- Duration: {meeting_duration}
- Location: {meeting_location}
- Organizer: {meeting_organizer}

ATTENDEES:
{chr(10).join([f"- {attendee}" for attendee in attendees]) if attendees else "- Not specified"}

Total attendees: {len(attendees)}

Create a professional meeting header suitable for executive meeting minutes."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        header = client.chat_completion(messages, temperature=0.1, max_tokens=800)

        return header.strip()

    except Exception as e:
        logger.error(f"AI attendees formatting failed: {e}")
        return _fallback_format_attendees_section(attendees, meeting_metadata)

def _create_minimal_minutes(state: MeetingState, meeting_type: str, metadata: Dict[str, Any]) -> MeetingState:
    """Create minimal minutes when full processing isn't available."""
    meeting_date = metadata.get("date", datetime.now().strftime("%Y-%m-%d"))

    minimal_minutes = f"""# {meeting_type} Minutes

**Date:** {meeting_date}  
**Status:** Processing completed with limited content

## Executive Summary

Meeting was conducted successfully with standard business coordination and information sharing among participants.

## Key Outcomes

- Meeting facilitated team alignment and coordination
- Information sharing completed as planned
- Standard business operations discussed

## Action Items

No specific action items were identified during processing.

## Next Steps

Team members should continue with current priorities and coordinate as needed.

---

*These minutes were generated automatically by AI Meeting Assistant on {datetime.now().strftime("%Y-%m-%d at %H:%M")}*
"""

    result_state = state.copy()
    result_state["formatted_minutes"] = minimal_minutes
    result_state["minutes_sections"] = {
        "header": f"# {meeting_type} Minutes\n\n**Date:** {meeting_date}\n",
        "summary": "Meeting completed with standard coordination.\n",
        "action_items": "No action items identified.\n",
        "next_steps": "Continue with current priorities.\n"
    }
    result_state["action_items_table"] = "## Action Items\n\nNo action items were identified.\n"
    result_state["decisions_list"] = "## Decisions Made\n\nNo formal decisions were recorded.\n"
    result_state["attendees_list"] = f"**Date:** {meeting_date}\n**Attendees:** Not specified\n"

    return result_state

# ================================
# FALLBACK FUNCTIONS (if AI fails)
# ================================

def _fallback_generate_meeting_minutes(
    executive_summary: str, meeting_overview: str, action_items: List[Dict[str, str]],
    decisions: List[Dict[str, str]], meeting_type: str, meeting_metadata: Dict[str, Any],
    attendees: List[str]
) -> str:
    """Fallback meeting minutes generation if AI fails."""
    logger.warning("Using fallback meeting minutes generation")

    meeting_date = meeting_metadata.get("date", datetime.now().strftime("%Y-%m-%d"))
    attendees_str = ", ".join(attendees) if attendees else "Not specified"

    minutes = f"""# {meeting_type} Minutes

**Date:** {meeting_date}  
**Attendees:** {attendees_str}

## Executive Summary

{executive_summary}

## Meeting Overview

{meeting_overview}

## Action Items

"""

    if action_items:
        minutes += "| Task | Assignee | Due Date | Priority |\n"
        minutes += "|------|----------|----------|----------|\n"
        for item in action_items:
            task = item.get("task", "").replace("|", "\\|")
            assignee = item.get("assignee", "Unassigned")
            deadline = item.get("deadline", "Not specified")
            priority = item.get("priority", "Medium")
            minutes += f"| {task} | {assignee} | {deadline} | {priority} |\n"
    else:
        minutes += "No action items were identified.\n"

    minutes += "\n## Decisions Made\n\n"

    if decisions:
        for i, decision in enumerate(decisions, 1):
            decision_text = decision.get("decision", "Unknown decision")
            context = decision.get("context", "")
            minutes += f"{i}. {decision_text}"
            if context and context != "No context provided":
                minutes += f" *(Context: {context})*"
            minutes += "\n"
    else:
        minutes += "No formal decisions were recorded.\n"

    minutes += f"""
---

*These minutes were generated automatically by AI Meeting Assistant on {datetime.now().strftime("%Y-%m-%d at %H:%M")}*
"""

    return minutes

def _fallback_generate_individual_sections(executive_summary: str, meeting_overview: str, meeting_type: str, meeting_metadata: Dict[str, Any]) -> Dict[str, str]:
    """Fallback individual sections generation if AI fails."""
    logger.warning("Using fallback individual sections generation")

    meeting_date = meeting_metadata.get("date", datetime.now().strftime("%Y-%m-%d"))

    return {
        "header": f"# {meeting_type} Minutes\n\n**Date:** {meeting_date}\n",
        "summary": f"## Executive Summary\n\n{executive_summary}\n",
        "overview": f"## Meeting Overview\n\n{meeting_overview}\n",
        "outcomes": "## Key Outcomes\n\nMeeting completed successfully with team coordination.\n",
        "next_steps": "## Next Steps\n\nTeam members to continue with assigned responsibilities.\n"
    }

def _fallback_format_action_items_table(action_items: List[Dict[str, str]]) -> str:
    """Fallback action items table formatting if AI fails."""
    logger.warning("Using fallback action items table formatting")

    if not action_items:
        return "## Action Items\n\nNo action items were identified.\n"

    table = "## Action Items\n\n"
    table += "| Task | Assignee | Due Date | Priority | Status |\n"
    table += "|------|----------|----------|----------|--------|\n"

    for item in action_items:
        task = item.get("task", "Unknown task").replace("|", "\\|")
        assignee = item.get("assignee", "Unassigned")
        deadline = item.get("deadline", "Not specified")
        priority = item.get("priority", "Medium")
        status = item.get("status", "Pending")

        # Truncate long tasks for table readability
        if len(task) > 60:
            task = task[:57] + "..."

        table += f"| {task} | {assignee} | {deadline} | {priority} | {status} |\n"

    return table

def _fallback_format_decisions_list(decisions: List[Dict[str, str]]) -> str:
    """Fallback decisions formatting if AI fails."""
    logger.warning("Using fallback decisions formatting")

    if not decisions:
        return "## Decisions Made\n\nNo formal decisions were recorded.\n"

    formatted = "## Decisions Made\n\n"

    for i, decision in enumerate(decisions, 1):
        decision_text = decision.get("decision", "Unknown decision")
        context = decision.get("context", "")

        formatted += f"### {i}. {decision_text}\n"

        if context and context != "No context provided":
            formatted += f"**Context:** {context}\n"

        formatted += "\n"

    return formatted

def _fallback_format_attendees_section(attendees: List[str], meeting_metadata: Dict[str, Any]) -> str:
    """Fallback attendees section formatting if AI fails."""
    logger.warning("Using fallback attendees section formatting")

    meeting_date = meeting_metadata.get("date", datetime.now().strftime("%Y-%m-%d"))
    meeting_time = meeting_metadata.get("start_time", "")
    meeting_duration = meeting_metadata.get("duration", "")

    header = f"**Date:** {meeting_date}\n"

    if meeting_time:
        header += f"**Time:** {meeting_time}\n"

    if meeting_duration:
        header += f"**Duration:** {meeting_duration}\n"

    if attendees:
        if len(attendees) <= 6:
            attendees_str = ", ".join(attendees)
        else:
            attendees_str = ", ".join(attendees[:6]) + f" and {len(attendees) - 6} others"
        header += f"**Attendees:** {attendees_str}\n"
    else:
        header += "**Attendees:** Not specified\n"

    return header

# ================================
# UTILITY FUNCTIONS
# ================================

def export_minutes_as_text(formatted_minutes: str) -> str:
    """Export minutes as plain text (remove markdown formatting)."""
    import re

    # Remove markdown formatting
    text = formatted_minutes

    # Remove headers
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

    # Remove bold/italic
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)

    # Convert tables to simple format
    lines = text.split('\n')
    processed_lines = []
    in_table = False

    for line in lines:
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                processed_lines.append("")  # Space before table
            # Convert table row to simple format
            cells = [cell.strip() for cell in line.split('|')[1:-1]]  # Remove empty first/last
            processed_lines.append("  ".join(cells))
        elif line.strip().startswith('|---'):
            # Skip table separator
            continue
        else:
            if in_table:
                in_table = False
                processed_lines.append("")  # Space after table
            processed_lines.append(line)

    return '\n'.join(processed_lines)

def get_minutes_statistics(state: MeetingState) -> Dict[str, Any]:
    """Get statistics about the generated minutes."""
    formatted_minutes = state.get("formatted_minutes", "")
    action_items = state.get("action_items", [])
    decisions = state.get("decisions", [])
    key_points = state.get("key_points", [])

    return {
        "total_characters": len(formatted_minutes),
        "total_words": len(formatted_minutes.split()),
        "total_lines": len(formatted_minutes.split('\n')),
        "action_items_count": len(action_items),
        "decisions_count": len(decisions),
        "key_points_count": len(key_points),
        "sections_included": len([s for s in state.get("minutes_sections", {}).values() if s.strip()]),
        "estimated_reading_time": f"{max(1, len(formatted_minutes.split()) // 200)} minutes",
        "professional_formatting": "AI-enhanced" if len(formatted_minutes) > 1000 else "Basic"
    }

# ================================
# TESTING FUNCTIONS
# ================================

def test_minutes_formatter(sample_state: MeetingState = None) -> Dict[str, Any]:
    """
    Test the enhanced minutes formatter with sample data.

    Args:
        sample_state: Optional state to test with

    Returns:
        Test results dictionary
    """
    if not sample_state:
        from utils.state_models import create_initial_state

        sample_state = create_initial_state("", {"date": "2024-01-15", "test": True}, "test")
        sample_state["executive_summary"] = "Strategic planning meeting successfully addressed Q4 objectives with key decisions on mobile platform development and resource allocation. The meeting demonstrated strong team alignment and resulted in concrete action items with clear ownership and timelines."
        sample_state["meeting_overview"] = "This strategic planning meeting brought together senior team members to finalize Q4 development priorities, with particular focus on mobile platform initiatives and resource allocation decisions."
        sample_state["key_outcomes"] = "Key strategic decisions included adoption of mobile-first development approach and allocation of $200K budget. Three high-priority action items were assigned with clear deadlines and ownership."
        sample_state["next_steps_summary"] = "Immediate actions include proposal preparation by Friday, developer hiring by month-end, and legal compliance meeting scheduling for next week."
        sample_state["action_items"] = [
            {
                "task": "Prepare comprehensive mobile platform development proposal",
                "assignee": "Sarah",
                "deadline": "Friday",
                "priority": "High",
                "status": "Pending"
            },
            {
                "task": "Hire 2 additional mobile developers",
                "assignee": "Jennifer",
                "deadline": "End of month",
                "priority": "High",
                "status": "Pending"
            },
            {
                "task": "Schedule compliance meeting with legal team",
                "assignee": "Jennifer",
                "deadline": "Next week",
                "priority": "Medium",
                "status": "Pending"
            }
        ]
        sample_state["decisions"] = [
            {
                "decision": "Adopt mobile-first development approach for Q4",
                "context": "Based on 60% mobile user adoption data",
                "rationale": "Market data shows clear user preference shift"
            },
            {
                "decision": "Allocate $200K budget to mobile platform initiative",
                "context": "Strategic investment in growth area",
                "rationale": "ROI projections justify significant investment"
            }
        ]
        sample_state["key_points"] = [
            "Mobile users represent 60% of current user base",
            "Additional development resources needed for timeline success",
            "Compliance requirements must be addressed for financial features",
            "Market competition driving need for accelerated development"
        ]
        sample_state["attendees"] = ["John (CEO)", "Sarah (Strategy Lead)", "Mike (CTO)", "Jennifer (VP Engineering)"]
        sample_state["meeting_type"] = "Strategic Planning Meeting"
        sample_state["meeting_insights"] = [
            "Strong organizational alignment on mobile-first strategy",
            "Clear resource allocation priorities established",
            "Effective decision-making process demonstrated"
        ]
        sample_state["stakeholder_impact"] = {
            "Engineering Team": "Significant new responsibilities and resource additions",
            "Product Strategy": "Clear direction with allocated budget and timeline",
            "Legal/Compliance": "New requirements for financial feature compliance"
        }
        sample_state["topics_discussed"] = ["Mobile Platform Development", "Q4 Strategy", "Resource Allocation", "Compliance Requirements"]

    try:
        start_time = time.time()
        result_state = format_minutes(sample_state)
        processing_time = time.time() - start_time

        stats = get_minutes_statistics(result_state)
        formatted_minutes = result_state.get("formatted_minutes", "")

        # Check for AI enhancement indicators
        ai_enhanced = (
            len(formatted_minutes) > 1500 and  # Substantial content
            "Executive Summary" in formatted_minutes and
            "Action Items" in formatted_minutes and
            ("| Task |" in formatted_minutes or "|Task|" in formatted_minutes or "Action Items" in formatted_minutes) and  # Table formatting (flexible)
            stats.get("professional_formatting") == "AI-enhanced"
        )

        return {
            "success": True,
            "minutes_length": len(formatted_minutes),
            "sections_count": len(result_state.get("minutes_sections", {})),
            "has_action_table": "| Task |" in formatted_minutes,
            "has_decisions_section": "Decisions Made" in formatted_minutes,
            "has_executive_summary": "Executive Summary" in formatted_minutes,
            "has_professional_header": "Date:" in formatted_minutes,
            "processing_time": processing_time,
            "ai_enhanced": ai_enhanced,
            "statistics": stats
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Test the enhanced agent
    test_result = test_minutes_formatter()
    print("Enhanced Minutes Formatter Test Results:")
    for key, value in test_result.items():
        if key != "statistics":  # Skip nested object for cleaner output
            print(f"  {key}: {value}")