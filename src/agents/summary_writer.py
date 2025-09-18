

import logging
import json
import time
from typing import Dict, Any, List
from datetime import datetime

from utils.state_models import MeetingState, add_warning
from utils.openai_client import get_openai_client

logger = logging.getLogger(__name__)

def write_summary(state: MeetingState) -> MeetingState:
    """
    Generate executive summary and meeting overview using OpenAI GPT-4o-mini.

    This agent:
    1. Creates compelling executive summaries for leadership consumption
    2. Develops comprehensive meeting overviews capturing purpose and context
    3. Highlights key outcomes, decisions, and strategic impacts
    4. Identifies important insights, concerns, and recommendations
    5. Writes in professional business language suitable for executives
    6. Customizes content based on meeting type and organizational context
    7. Provides stakeholder impact analysis and next steps overview

    Args:
        state: Current workflow state containing cleaned transcript and extracted info

    Returns:
        Updated state with executive summary and comprehensive meeting analysis
    """
    logger.info("📝 Summary Writer Agent starting (Full AI Implementation)...")

    try:
        # Get required data from state
        cleaned_transcript = state.get("cleaned_transcript", "")
        extracted_info = state.get("extracted_info", {})
        action_items = state.get("action_items", [])
        decisions = state.get("decisions", [])
        key_points = state.get("key_points", [])
        meeting_type = state.get("meeting_type", "General Meeting")
        attendees = state.get("attendees", [])
        topics_discussed = state.get("topics_discussed", [])
        meeting_metadata = state.get("meeting_metadata", {})

        if not cleaned_transcript:
            logger.warning("No cleaned transcript available for summary")
            result_state = state.copy()
            result_state = _create_minimal_summary(result_state)
            return add_warning(result_state, "summary_writer", "No transcript content to summarize")

        logger.info(f"Generating AI-powered summary for {meeting_type} with {len(action_items)} actions and {len(decisions)} decisions")

        # Get OpenAI client
        client = get_openai_client()

        # Step 1: Generate executive summary using AI
        start_time = time.time()
        executive_summary = _ai_generate_executive_summary(client, cleaned_transcript, extracted_info, meeting_type, meeting_metadata)
        summary_time = time.time() - start_time

        # Step 2: Generate meeting overview using AI
        start_time = time.time()
        meeting_overview = _ai_generate_meeting_overview(client, cleaned_transcript, meeting_type, attendees, topics_discussed)
        overview_time = time.time() - start_time

        # Step 3: Generate key outcomes analysis using AI
        start_time = time.time()
        key_outcomes = _ai_generate_key_outcomes(client, decisions, action_items, key_points, meeting_type)
        outcomes_time = time.time() - start_time

        # Step 4: Generate next steps summary using AI
        start_time = time.time()
        next_steps_summary = _ai_generate_next_steps(client, action_items, decisions, extracted_info.get("deadlines_mentioned", []))
        next_steps_time = time.time() - start_time

        # Step 5: Generate meeting insights using AI
        start_time = time.time()
        meeting_insights = _ai_generate_insights(client, cleaned_transcript, key_points, decisions, meeting_type)
        insights_time = time.time() - start_time

        # Step 6: Generate stakeholder impact assessment using AI
        stakeholder_impact = _ai_assess_stakeholder_impact(client, decisions, action_items, attendees, meeting_type)

        # Update state with results
        result_state = state.copy()
        result_state["executive_summary"] = executive_summary
        result_state["meeting_overview"] = meeting_overview
        result_state["key_outcomes"] = key_outcomes
        result_state["next_steps_summary"] = next_steps_summary
        result_state["meeting_insights"] = meeting_insights
        result_state["stakeholder_impact"] = stakeholder_impact

        total_time = summary_time + overview_time + outcomes_time + next_steps_time + insights_time
        logger.info(f"✅ AI-powered summary generation completed successfully (total: {total_time:.2f}s)")
        return result_state

    except Exception as e:
        logger.error(f"❌ Summary generation failed: {e}")
        # Return state with minimal summary
        error_state = state.copy()
        error_state = _create_minimal_summary(error_state)
        raise  # Re-raise for workflow error handling

def _ai_generate_executive_summary(client, transcript: str, extracted_info: Dict[str, Any], meeting_type: str, metadata: Dict[str, Any]) -> str:
    """
    Use OpenAI to generate a compelling executive summary.
    """

    system_prompt = """You are an executive assistant creating high-level summaries for senior leadership.

Create a compelling executive summary that captures the essence and business impact of this meeting.

REQUIREMENTS:
1. Write for C-level executives and senior management
2. Focus on business impact, strategic decisions, and key outcomes
3. Be concise but comprehensive (2-3 paragraphs maximum)
4. Highlight critical decisions, major action items, and business implications
5. Use professional, authoritative language
6. Include quantifiable results where available
7. Emphasize strategic importance and organizational impact

STRUCTURE:
- Opening: Meeting purpose and strategic context
- Body: Key decisions, outcomes, and business impact
- Closing: Critical next steps and implications

Return only the executive summary with no additional commentary."""

    # Prepare context information
    action_count = len(extracted_info.get("action_items", []))
    decision_count = len(extracted_info.get("decisions", []))
    attendee_count = len(extracted_info.get("attendees", []))
    meeting_date = metadata.get("date", "Recent")

    user_prompt = f"""Create an executive summary for this {meeting_type.lower()}:

MEETING CONTEXT:
- Type: {meeting_type}
- Date: {meeting_date}
- Participants: {attendee_count} attendees
- Decisions Made: {decision_count}
- Action Items: {action_count}

MEETING TRANSCRIPT:
{transcript[:2000]}...

Focus on business impact and strategic importance."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        summary = client.chat_completion(messages, temperature=0.2, max_tokens=800)

        return summary.strip()

    except Exception as e:
        logger.error(f"AI executive summary generation failed: {e}")
        return _fallback_generate_executive_summary(transcript, extracted_info, meeting_type)

def _ai_generate_meeting_overview(client, transcript: str, meeting_type: str, attendees: List[str], topics: List[str]) -> str:
    """
    Use OpenAI to generate a comprehensive meeting overview.
    """

    system_prompt = """You are an expert at creating meeting overviews that provide context and purpose.

Create a meeting overview that explains the meeting's purpose, participants, and scope.

REQUIREMENTS:
1. Explain the meeting's purpose and business context
2. Highlight the main discussion areas and objectives
3. Provide context for why this meeting was necessary
4. Use professional, informative language
5. Keep it concise but informative (1-2 paragraphs)
6. Focus on the 'why' behind the meeting

Return only the meeting overview with no additional commentary."""

    attendees_str = ", ".join(attendees) if attendees else "Multiple participants"
    topics_str = ", ".join(topics) if topics else "Various business topics"

    user_prompt = f"""Create a meeting overview for this {meeting_type.lower()}:

MEETING DETAILS:
- Type: {meeting_type}
- Participants: {attendees_str}
- Main Topics: {topics_str}

TRANSCRIPT SAMPLE:
{transcript[:1000]}...

Explain the purpose and context of this meeting."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        overview = client.chat_completion(messages, temperature=0.2, max_tokens=500)

        return overview.strip()

    except Exception as e:
        logger.error(f"AI meeting overview generation failed: {e}")
        return _fallback_generate_meeting_overview(meeting_type, attendees, topics)

def _ai_generate_key_outcomes(client, decisions: List[Dict[str, str]], action_items: List[Dict[str, str]], key_points: List[str], meeting_type: str) -> str:
    """
    Use OpenAI to generate key outcomes analysis.
    """

    system_prompt = """You are an expert at analyzing meeting outcomes and their business implications.

Analyze the decisions, action items, and key points to create a comprehensive outcomes summary.

REQUIREMENTS:
1. Categorize outcomes by importance and business impact
2. Highlight strategic decisions and their implications
3. Summarize action items by priority and urgency
4. Identify key insights and their organizational impact
5. Use clear, professional language suitable for executives
6. Structure the content logically with clear sections

FORMAT:
Use clear sections like "Strategic Decisions," "Action Items Summary," "Key Insights."

Return only the key outcomes analysis with no additional commentary."""

    # Prepare structured data
    decisions_summary = []
    for decision in decisions[:5]:  # Top 5 decisions
        decisions_summary.append(f"• {decision.get('decision', 'Unknown decision')}")

    actions_summary = []
    for action in action_items[:5]:  # Top 5 actions
        assignee = action.get('assignee', 'Unassigned')
        task = action.get('task', 'Unknown task')
        actions_summary.append(f"• {task} (Assigned to: {assignee})")

    user_prompt = f"""Analyze the key outcomes of this {meeting_type.lower()}:

DECISIONS MADE:
{chr(10).join(decisions_summary) if decisions_summary else "No major decisions recorded"}

ACTION ITEMS:
{chr(10).join(actions_summary) if actions_summary else "No action items identified"}

KEY DISCUSSION POINTS:
{chr(10).join([f"• {point}" for point in key_points[:5]]) if key_points else "No specific points recorded"}

MEETING TYPE: {meeting_type}

Provide a comprehensive outcomes analysis."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        outcomes = client.chat_completion(messages, temperature=0.2, max_tokens=800)

        return outcomes.strip()

    except Exception as e:
        logger.error(f"AI key outcomes generation failed: {e}")
        return _fallback_generate_key_outcomes(decisions, action_items, key_points)

def _ai_generate_next_steps(client, action_items: List[Dict[str, str]], decisions: List[Dict[str, str]], deadlines: List[Dict[str, str]]) -> str:
    """
    Use OpenAI to generate next steps summary.
    """

    system_prompt = """You are an expert at creating actionable next steps summaries for business meetings.

Create a clear, prioritized summary of next steps based on action items, decisions, and deadlines.

REQUIREMENTS:
1. Prioritize by urgency and business impact
2. Group related actions logically
3. Highlight critical deadlines and dependencies
4. Use clear, actionable language
5. Include accountability (who does what)
6. Keep it concise but comprehensive

FORMAT:
Structure as prioritized sections with clear accountability.

Return only the next steps summary with no additional commentary."""

    # Prepare action items summary
    action_summary = []
    for action in action_items[:8]:  # Top 8 actions
        task = action.get('task', 'Unknown task')
        assignee = action.get('assignee', 'Unassigned')
        deadline = action.get('deadline', 'No deadline specified')
        action_summary.append(f"• {task} - {assignee} ({deadline})")

    deadline_summary = []
    for deadline in deadlines[:5]:  # Top 5 deadlines
        item = deadline.get('deadline', 'Unknown deadline')
        date = deadline.get('date', 'TBD')
        deadline_summary.append(f"• {item} - Due: {date}")

    user_prompt = f"""Create a next steps summary based on this meeting:

ACTION ITEMS:
{chr(10).join(action_summary) if action_summary else "No specific action items identified"}

TIME-SENSITIVE ITEMS:
{chr(10).join(deadline_summary) if deadline_summary else "No specific deadlines mentioned"}

DECISIONS REQUIRING FOLLOW-UP:
{len(decisions)} decisions made requiring implementation

Create a prioritized, actionable next steps summary."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        next_steps = client.chat_completion(messages, temperature=0.2, max_tokens=600)

        return next_steps.strip()

    except Exception as e:
        logger.error(f"AI next steps generation failed: {e}")
        return _fallback_generate_next_steps(action_items, deadlines)

def _ai_generate_insights(client, transcript: str, key_points: List[str], decisions: List[Dict[str, str]], meeting_type: str) -> List[str]:
    """
    Use OpenAI to generate meeting insights and strategic observations.
    """

    system_prompt = """You are a business analyst generating strategic insights from meeting discussions.

Analyze the meeting content to identify important insights, patterns, and strategic observations.

REQUIREMENTS:
1. Focus on strategic implications and business insights
2. Identify patterns, risks, opportunities, and trends
3. Highlight organizational dynamics and decision-making patterns
4. Provide actionable insights for leadership
5. Keep each insight concise but meaningful

RETURN FORMAT:
Return a JSON array of strings, each being a distinct insight:
["insight 1", "insight 2", "insight 3"]

Return only valid JSON with no additional text."""

    user_prompt = f"""Generate strategic insights from this {meeting_type.lower()}:

KEY DECISIONS:
{len(decisions)} strategic decisions made

KEY DISCUSSION POINTS:
{chr(10).join([f"• {point[:100]}..." for point in key_points[:5]]) if key_points else "Limited discussion points"}

TRANSCRIPT SAMPLE:
{transcript[:1500]}...

Generate 3-5 strategic insights about this meeting."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = client.chat_completion(messages, temperature=0.3, max_tokens=600)

        # Parse JSON response
        insights = json.loads(response)

        # Validate and return
        if isinstance(insights, list):
            return [insight for insight in insights if isinstance(insight, str) and len(insight) > 10][:6]
        else:
            return _fallback_generate_insights(key_points, decisions, meeting_type)

    except Exception as e:
        logger.error(f"AI insights generation failed: {e}")
        return _fallback_generate_insights(key_points, decisions, meeting_type)

def _ai_assess_stakeholder_impact(client, decisions: List[Dict[str, str]], action_items: List[Dict[str, str]], attendees: List[str], meeting_type: str) -> Dict[str, str]:
    """
    Use OpenAI to assess stakeholder impact of meeting outcomes.
    """

    system_prompt = """You are an expert at analyzing stakeholder impact from business meetings.

Assess how the meeting outcomes (decisions and action items) will impact different stakeholders.

REQUIREMENTS:
1. Identify key stakeholder groups affected
2. Analyze direct and indirect impacts
3. Consider both positive and negative implications
4. Use professional business language
5. Be specific about impact types

RETURN FORMAT:
Return a JSON object mapping stakeholder groups to impact descriptions:
{
  "stakeholder_group": "impact description",
  "another_group": "impact description"
}

Return only valid JSON with no additional text."""

    decisions_count = len(decisions)
    actions_count = len(action_items)
    attendees_str = ", ".join(attendees[:5]) if attendees else "Meeting participants"

    user_prompt = f"""Assess stakeholder impact from this {meeting_type.lower()}:

MEETING OUTCOMES:
- {decisions_count} strategic decisions made
- {actions_count} action items assigned
- Key participants: {attendees_str}

SAMPLE DECISIONS:
{chr(10).join([f"• {d.get('decision', 'Unknown')[:80]}..." for d in decisions[:3]]) if decisions else "No major decisions"}

SAMPLE ACTIONS:
{chr(10).join([f"• {a.get('task', 'Unknown')[:80]}..." for a in action_items[:3]]) if action_items else "No action items"}

Identify stakeholder groups and their impact from these outcomes."""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = client.chat_completion(messages, temperature=0.2, max_tokens=600)

        # Parse JSON response
        impact_assessment = json.loads(response)

        # Validate and return
        if isinstance(impact_assessment, dict):
            return {k: v for k, v in impact_assessment.items() if isinstance(v, str) and len(v) > 10}
        else:
            return _fallback_assess_stakeholder_impact(decisions, action_items, attendees)

    except Exception as e:
        logger.error(f"AI stakeholder impact assessment failed: {e}")
        return _fallback_assess_stakeholder_impact(decisions, action_items, attendees)

def _create_minimal_summary(state: MeetingState) -> MeetingState:
    """Create minimal summary when full processing isn't possible."""
    result_state = state.copy()
    result_state["executive_summary"] = "Meeting completed with standard business coordination and information sharing among team members."
    result_state["meeting_overview"] = "Business meeting focused on operational matters and team coordination."
    result_state["key_outcomes"] = "Meeting facilitated team alignment and coordination of ongoing initiatives."
    result_state["next_steps_summary"] = "Team members to continue with assigned responsibilities and coordinate as needed."
    result_state["meeting_insights"] = ["Limited content available for detailed analysis"]
    result_state["stakeholder_impact"] = {"Team": "Standard coordination and information sharing"}
    return result_state

# ================================
# FALLBACK FUNCTIONS (if AI fails)
# ================================

def _fallback_generate_executive_summary(transcript: str, extracted_info: Dict[str, Any], meeting_type: str) -> str:
    """Fallback executive summary generation if AI fails."""
    logger.warning("Using fallback executive summary generation")

    action_count = len(extracted_info.get("action_items", []))
    decision_count = len(extracted_info.get("decisions", []))
    word_count = len(transcript.split())

    return f"This {meeting_type.lower()} successfully addressed key business objectives with {decision_count} strategic decisions made and {action_count} action items assigned. The meeting demonstrated productive collaboration and clear outcomes. Discussion covered approximately {word_count} words of substantive business content, resulting in concrete next steps and assigned responsibilities for team execution."

def _fallback_generate_meeting_overview(meeting_type: str, attendees: List[str], topics: List[str]) -> str:
    """Fallback meeting overview generation if AI fails."""
    logger.warning("Using fallback meeting overview generation")

    attendee_count = len(attendees)
    topic_count = len(topics)

    return f"This {meeting_type.lower()} brought together {attendee_count} participants to address {topic_count} key business areas. The session focused on operational coordination, strategic alignment, and ensuring clear communication across team initiatives. The meeting served its intended purpose of facilitating collaboration and decision-making among stakeholders."

def _fallback_generate_key_outcomes(decisions: List[Dict[str, str]], action_items: List[Dict[str, str]], key_points: List[str]) -> str:
    """Fallback key outcomes generation if AI fails."""
    logger.warning("Using fallback key outcomes generation")

    outcomes = []

    if decisions:
        outcomes.append(f"Strategic Decisions: {len(decisions)} important decisions were finalized")
        for i, decision in enumerate(decisions[:2], 1):
            outcomes.append(f"  {i}. {decision.get('decision', 'Decision made')[:80]}...")

    if action_items:
        outcomes.append(f"Action Items: {len(action_items)} tasks assigned with clear ownership")
        assignees = list(set([item.get('assignee', 'Unknown') for item in action_items]))
        outcomes.append(f"  Assigned to: {', '.join(assignees[:4])}{'and others' if len(assignees) > 4 else ''}")

    if key_points:
        outcomes.append(f"Key Insights: {len(key_points)} important discussion points raised")

    return "\n".join(outcomes) if outcomes else "Meeting provided valuable coordination and information sharing."

def _fallback_generate_next_steps(action_items: List[Dict[str, str]], deadlines: List[Dict[str, str]]) -> str:
    """Fallback next steps generation if AI fails."""
    logger.warning("Using fallback next steps generation")

    if not action_items and not deadlines:
        return "No specific action items identified. Team members should continue with current priorities and coordinate as needed."

    next_steps = ["Immediate Actions Required:"]

    for action in action_items[:5]:
        task = action.get('task', 'Unknown task')[:60]
        assignee = action.get('assignee', 'Unassigned')
        next_steps.append(f"• {task} - {assignee}")

    if deadlines:
        next_steps.append(f"Time-sensitive items: {len(deadlines)} deadlines require attention")

    return "\n".join(next_steps)

def _fallback_generate_insights(key_points: List[str], decisions: List[Dict[str, str]], meeting_type: str) -> List[str]:
    """Fallback insights generation if AI fails."""
    logger.warning("Using fallback insights generation")

    insights = []

    if len(decisions) > 2:
        insights.append("High decision-making productivity with multiple strategic choices finalized")

    if len(key_points) > 4:
        insights.append("Comprehensive discussion covering multiple business-critical topics")

    type_insights = {
        "Daily Standup": "Team coordination and progress tracking appears well-structured",
        "Client Meeting": "Client relationship management active with focus on service delivery",
        "Planning Meeting": "Strategic planning and resource allocation discussed thoroughly",
        "Board Meeting": "Governance oversight maintained with attention to organizational performance"
    }

    if meeting_type in type_insights:
        insights.append(type_insights[meeting_type])

    if not insights:
        insights.append("Meeting maintained professional focus on business objectives")

    return insights

def _fallback_assess_stakeholder_impact(decisions: List[Dict[str, str]], action_items: List[Dict[str, str]], attendees: List[str]) -> Dict[str, str]:
    """Fallback stakeholder impact assessment if AI fails."""
    logger.warning("Using fallback stakeholder impact assessment")

    impact = {}

    if action_items:
        assignees = list(set([item.get('assignee', '') for item in action_items if item.get('assignee')]))
        if assignees:
            impact["Direct Contributors"] = f"New responsibilities assigned to {len(assignees)} team members requiring coordination and execution"

    if decisions:
        impact["Organization"] = f"{len(decisions)} strategic decisions will influence operational direction and team priorities"

    if attendees:
        impact["Meeting Participants"] = f"{len(attendees)} attendees directly involved in decision-making and action item assignments"

    if not impact:
        impact["General"] = "Standard business coordination with minimal external impact"

    return impact

# ================================
# TESTING FUNCTIONS
# ================================

def test_summary_writer(sample_state: MeetingState = None) -> Dict[str, Any]:
    """
    Test the enhanced summary writer with sample data.

    Args:
        sample_state: Optional state to test with

    Returns:
        Test results dictionary
    """
    if not sample_state:
        from utils.state_models import create_initial_state

        sample_transcript = """
John: Good morning team. Let's discuss our Q4 strategy and resource allocation.
Sarah: I've completed the market analysis. We should prioritize the mobile platform development.
Mike: I agree. The data shows 60% of our users are on mobile. We need to allocate $200K to this initiative.
Jennifer: I can lead the mobile team. We'll need to hire 2 additional developers by next month.
John: Excellent. We've decided to go with the mobile-first approach. Sarah, can you prepare the detailed proposal by Friday?
Sarah: Absolutely. I'll coordinate with the design team as well.
Mike: We should also consider the compliance requirements for the financial features.
Jennifer: Good point. I'll schedule a meeting with the legal team for next week.
John: Perfect. This positions us well for the competitive market. Any other concerns? No? Great meeting everyone.
"""

        sample_state = create_initial_state(sample_transcript, {"date": "2024-01-15", "type": "Strategy Planning"}, "test")
        sample_state["cleaned_transcript"] = sample_transcript
        sample_state["extracted_info"] = {
            "action_items": [
                {"task": "Prepare mobile platform proposal", "assignee": "Sarah", "deadline": "Friday", "priority": "high"},
                {"task": "Hire 2 additional developers", "assignee": "Jennifer", "deadline": "next month", "priority": "high"},
                {"task": "Schedule legal team meeting", "assignee": "Jennifer", "deadline": "next week", "priority": "medium"}
            ],
            "decisions": [
                {"decision": "Adopt mobile-first development approach", "context": "Based on 60% mobile user data"},
                {"decision": "Allocate $200K to mobile initiative", "context": "Strategic investment decision"}
            ]
        }
        sample_state["action_items"] = sample_state["extracted_info"]["action_items"]
        sample_state["decisions"] = sample_state["extracted_info"]["decisions"]
        sample_state["key_points"] = ["60% mobile user adoption", "Need for additional developers", "Compliance requirements for financial features"]
        sample_state["meeting_type"] = "Strategy Planning"
        sample_state["attendees"] = ["John", "Sarah", "Mike", "Jennifer"]
        sample_state["topics_discussed"] = ["Q4 Strategy", "Mobile Platform", "Resource Allocation", "Compliance"]

    try:
        start_time = time.time()
        result_state = write_summary(sample_state)
        processing_time = time.time() - start_time

        # Check for AI enhancement indicators
        executive_summary = result_state.get("executive_summary", "")
        meeting_insights = result_state.get("meeting_insights", [])
        stakeholder_impact = result_state.get("stakeholder_impact", {})

        ai_enhanced = (
            len(executive_summary) > 200 and  # Substantial content
            isinstance(meeting_insights, list) and len(meeting_insights) > 0 and
            isinstance(stakeholder_impact, dict) and len(stakeholder_impact) > 0
        )

        return {
            "success": True,
            "executive_summary_length": len(executive_summary),
            "meeting_overview_length": len(result_state.get("meeting_overview", "")),
            "key_outcomes_length": len(result_state.get("key_outcomes", "")),
            "insights_count": len(meeting_insights),
            "stakeholder_groups": len(stakeholder_impact),
            "has_next_steps": bool(result_state.get("next_steps_summary")),
            "processing_time": processing_time,
            "ai_enhanced": ai_enhanced
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Test the enhanced agent
    test_result = test_summary_writer()
    print("Enhanced Summary Writer Test Results:")
    for key, value in test_result.items():
        print(f"  {key}: {value}")