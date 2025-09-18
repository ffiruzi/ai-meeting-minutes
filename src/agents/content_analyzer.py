

import logging
import json
import time
from typing import Dict, Any, List
from datetime import datetime

from utils.state_models import MeetingState, add_warning
from utils.openai_client import get_openai_client

logger = logging.getLogger(__name__)

def analyze_content(state: MeetingState) -> MeetingState:
    """
    Analyze meeting content using OpenAI GPT-4o-mini to extract structured information.

    This agent:
    1. Extracts action items with context, assignees, deadlines, and priorities
    2. Identifies decisions made with rationale and impact assessment
    3. Finds key discussion points and important insights
    4. Determines meeting type and identifies attendees intelligently
    5. Parses time-sensitive information and deadlines
    6. Provides comprehensive structured output for downstream processing

    Args:
        state: Current workflow state containing cleaned transcript

    Returns:
        Updated state with comprehensive extracted structured information
    """
    logger.info("🔍 Content Analyzer Agent starting (Full AI Implementation)...")

    try:
        # Get cleaned transcript from state
        cleaned_transcript = state.get("cleaned_transcript", "")

        if not cleaned_transcript or not cleaned_transcript.strip():
            logger.warning("No cleaned transcript available for analysis")
            result_state = state.copy()
            result_state = _create_empty_analysis(result_state)
            return add_warning(result_state, "content_analyzer", "No transcript content to analyze")

        logger.info(f"Analyzing transcript content ({len(cleaned_transcript)} characters) using OpenAI")

        # Get OpenAI client
        client = get_openai_client()

        # Step 1: Extract action items with AI
        start_time = time.time()
        action_items = _ai_extract_action_items(client, cleaned_transcript)
        action_time = time.time() - start_time

        # Step 2: Extract decisions with AI
        start_time = time.time()
        decisions = _ai_extract_decisions(client, cleaned_transcript)
        decision_time = time.time() - start_time

        # Step 3: Extract key discussion points with AI
        start_time = time.time()
        key_points = _ai_extract_key_points(client, cleaned_transcript)
        points_time = time.time() - start_time

        # Step 4: Comprehensive meeting analysis
        start_time = time.time()
        meeting_analysis = _ai_analyze_meeting_context(client, cleaned_transcript)
        analysis_time = time.time() - start_time

        # Step 5: Extract time-sensitive information (with improved error handling)
        deadlines = _ai_extract_deadlines(client, cleaned_transcript)

        # Combine all extracted information
        extracted_info = {
            "action_items": action_items,
            "decisions": decisions,
            "key_points": key_points,
            "attendees": meeting_analysis.get("attendees", []),
            "meeting_type": meeting_analysis.get("meeting_type", "General Meeting"),
            "topics_discussed": meeting_analysis.get("topics", []),
            "deadlines_mentioned": deadlines,
            "meeting_sentiment": meeting_analysis.get("sentiment", "neutral"),
            "urgency_level": meeting_analysis.get("urgency", "medium"),
            "extraction_method": "openai_gpt4o_mini",
            "extraction_timestamp": datetime.now().isoformat(),
            "processing_times": {
                "action_items": action_time,
                "decisions": decision_time,
                "key_points": points_time,
                "analysis": analysis_time
            },
            "total_items_extracted": len(action_items) + len(decisions) + len(key_points),
            "ai_confidence": meeting_analysis.get("confidence", 0.8)
        }

        # Update state with results
        result_state = state.copy()
        result_state["extracted_info"] = extracted_info
        result_state["action_items"] = action_items
        result_state["decisions"] = decisions
        result_state["key_points"] = key_points
        result_state["attendees"] = meeting_analysis.get("attendees", [])
        result_state["meeting_type"] = meeting_analysis.get("meeting_type", "General Meeting")
        result_state["topics_discussed"] = meeting_analysis.get("topics", [])
        result_state["deadlines_mentioned"] = deadlines

        total_time = action_time + decision_time + points_time + analysis_time
        logger.info(f"✅ Content analysis completed: {len(action_items)} actions, {len(decisions)} decisions, {len(key_points)} key points (total: {total_time:.2f}s)")
        return result_state

    except Exception as e:
        logger.error(f"❌ Content analysis failed: {e}")
        # Return state with minimal info
        error_state = state.copy()
        error_state = _create_empty_analysis(error_state)
        error_state["extracted_info"] = {"error": str(e), "extraction_method": "failed"}
        raise  # Re-raise for workflow error handling

def _ai_extract_action_items(client, transcript: str) -> List[Dict[str, str]]:
    """
    Use OpenAI to extract action items with context and details.
    """

    system_prompt = """You are an expert at extracting action items from meeting transcripts.

Analyze the transcript and identify ALL action items, tasks, commitments, and follow-ups mentioned.

For each action item, extract:
- task: Clear, specific description of what needs to be done
- assignee: Who is responsible (use exact names from transcript)
- deadline: When it's due (extract from context, use "not specified" if unclear)
- priority: high/medium/low based on context and language used
- context: Brief context about why this task is needed

Return a JSON array of objects with this exact structure:
[
    {
        "task": "specific task description",
        "assignee": "person's name",
        "deadline": "deadline or 'not specified'",
        "priority": "high/medium/low",
        "context": "brief context or reason for task",
        "status": "pending"
    }
]

Look for phrases like:
- "X will do Y"
- "X needs to complete Z" 
- "Action item for X"
- "X should follow up on Y"
- "X can you handle Z"
- "Let's have X do Y"

Be thorough but precise. Only include clear, actionable tasks."""

    user_prompt = f"Extract all action items from this meeting transcript:\n\n{transcript}"

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = client.chat_completion(messages, temperature=0.1, max_tokens=2000)

        # Safe JSON parsing with error handling
        try:
            action_items = json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON response for action items: {e}")
            return _fallback_extract_action_items(transcript)

        # Validate and clean up
        validated_items = []
        for item in action_items:
            if isinstance(item, dict) and item.get("task") and len(str(item.get("task", "")).strip()) > 5:
                # Safe field extraction with defaults
                validated_item = {
                    "task": str(item.get("task", "")).strip(),
                    "assignee": str(item.get("assignee", "Unassigned")).strip(),
                    "deadline": str(item.get("deadline", "not specified")).strip(),
                    "priority": str(item.get("priority", "medium")).lower().strip(),
                    "context": str(item.get("context", "")).strip(),
                    "status": "pending"
                }

                # Ensure priority is valid
                if validated_item["priority"] not in ["high", "medium", "low"]:
                    validated_item["priority"] = "medium"

                validated_items.append(validated_item)

        logger.info(f"AI extracted {len(validated_items)} action items")
        return validated_items[:15]  # Limit to top 15

    except Exception as e:
        logger.error(f"AI action item extraction failed: {e}")
        return _fallback_extract_action_items(transcript)

def _ai_extract_decisions(client, transcript: str) -> List[Dict[str, str]]:
    """
    Use OpenAI to extract decisions made during the meeting.
    """

    system_prompt = """You are an expert at identifying decisions made during meetings.

Analyze the transcript and identify ALL decisions, conclusions, agreements, and resolutions.

For each decision, extract:
- decision: Clear statement of what was decided
- context: Situation or issue that led to this decision
- rationale: Reasoning behind the decision (if mentioned)
- impact: Who/what this affects
- implementation_date: When this takes effect (if mentioned)

Return a JSON array of objects with this exact structure:
[
    {
        "decision": "clear decision statement",
        "context": "situation that led to decision",
        "rationale": "reasoning provided or 'not specified'",
        "impact": "who/what is affected",
        "implementation_date": "date or 'immediate' or 'not specified'",
        "stakeholders": ["person1", "person2"]
    }
]

Look for phrases like:
- "We decided to..."
- "It was agreed that..."
- "We're going with..."
- "The decision is..."
- "We concluded that..."
- "Let's go ahead with..."

Only include actual decisions, not just discussion points."""

    user_prompt = f"Extract all decisions from this meeting transcript:\n\n{transcript}"

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = client.chat_completion(messages, temperature=0.1, max_tokens=1500)

        # Safe JSON parsing
        try:
            decisions = json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON response for decisions: {e}")
            return _fallback_extract_decisions(transcript)

        # Validate and clean up
        validated_decisions = []
        for decision in decisions:
            if isinstance(decision, dict) and decision.get("decision") and len(str(decision.get("decision", "")).strip()) > 5:
                # Safe extraction with defaults
                stakeholders = decision.get("stakeholders", [])
                if not isinstance(stakeholders, list):
                    stakeholders = []

                validated_decision = {
                    "decision": str(decision.get("decision", "")).strip(),
                    "context": str(decision.get("context", "Meeting discussion")).strip(),
                    "rationale": str(decision.get("rationale", "not specified")).strip(),
                    "impact": str(decision.get("impact", "Team/Project")).strip(),
                    "implementation_date": str(decision.get("implementation_date", "not specified")).strip(),
                    "stakeholders": stakeholders
                }
                validated_decisions.append(validated_decision)

        logger.info(f"AI extracted {len(validated_decisions)} decisions")
        return validated_decisions[:10]  # Limit to top 10

    except Exception as e:
        logger.error(f"AI decision extraction failed: {e}")
        return _fallback_extract_decisions(transcript)

def _ai_extract_key_points(client, transcript: str) -> List[str]:
    """
    Use OpenAI to extract key discussion points and insights.
    """

    system_prompt = """You are an expert at identifying key discussion points from meeting transcripts.

Analyze the transcript and identify the most important points, insights, concerns, and topics discussed.

Extract:
- Important issues or concerns raised
- Key insights or observations shared
- Critical information or updates provided
- Significant discussion topics
- Important announcements or updates
- Strategic points or considerations

Return a JSON array of strings, each being a concise key discussion point:
[
    "key point 1",
    "key point 2", 
    "key point 3"
]

Focus on:
- Business-critical information
- Strategic decisions or considerations  
- Important updates or changes
- Risks or concerns identified
- Opportunities discussed
- Process or operational insights

Keep each point concise (1-2 sentences) but meaningful. Prioritize business impact and importance."""

    user_prompt = f"Extract key discussion points from this meeting transcript:\n\n{transcript}"

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = client.chat_completion(messages, temperature=0.2, max_tokens=1000)

        # Safe JSON parsing
        try:
            key_points = json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON response for key points: {e}")
            return _fallback_extract_key_points(transcript)

        # Validate and clean up
        validated_points = []
        for point in key_points:
            if isinstance(point, str) and len(point.strip()) > 10:
                validated_points.append(point.strip())

        logger.info(f"AI extracted {len(validated_points)} key points")
        return validated_points[:12]  # Limit to top 12

    except Exception as e:
        logger.error(f"AI key points extraction failed: {e}")
        return _fallback_extract_key_points(transcript)

def _ai_analyze_meeting_context(client, transcript: str) -> Dict[str, Any]:
    """
    Use OpenAI for comprehensive meeting context analysis.
    """

    system_prompt = """You are an expert at analyzing meeting context and extracting metadata.

Analyze this meeting transcript and extract:

1. Meeting type (e.g., "Daily Standup", "Client Meeting", "Planning Session", "Review Meeting", "Board Meeting")
2. Attendees (extract names mentioned in the transcript)
3. Main topics discussed (3-5 key topics)
4. Overall sentiment (positive/neutral/negative/mixed)
5. Urgency level (low/medium/high) based on deadlines and language
6. Confidence level (0.0-1.0) in your analysis

Return a JSON object with this exact structure:
{
    "meeting_type": "specific meeting type",
    "attendees": ["Name1", "Name2", "Name3"],
    "topics": ["topic1", "topic2", "topic3"],
    "sentiment": "positive/neutral/negative/mixed",
    "urgency": "low/medium/high",
    "confidence": 0.85,
    "meeting_duration_estimate": "estimated duration",
    "key_themes": ["theme1", "theme2"]
}

Base your analysis on:
- Language patterns and formality
- Topics discussed
- Decision-making patterns
- Time pressure indicators
- Participant interactions"""

    user_prompt = f"Analyze this meeting for context and metadata:\n\n{transcript[:2000]}..."  # Limit for efficiency

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = client.chat_completion(messages, temperature=0.1, max_tokens=800)

        # Safe JSON parsing
        try:
            analysis = json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON response for meeting analysis: {e}")
            return _fallback_analyze_meeting(transcript)

        # Validate and set defaults
        attendees = analysis.get("attendees", [])
        if not isinstance(attendees, list):
            attendees = []

        topics = analysis.get("topics", [])
        if not isinstance(topics, list):
            topics = []

        key_themes = analysis.get("key_themes", [])
        if not isinstance(key_themes, list):
            key_themes = []

        validated_analysis = {
            "meeting_type": str(analysis.get("meeting_type", "General Meeting")).strip(),
            "attendees": [str(name).strip() for name in attendees if str(name).strip()],
            "topics": [str(topic).strip() for topic in topics if str(topic).strip()],
            "sentiment": str(analysis.get("sentiment", "neutral")).strip().lower(),
            "urgency": str(analysis.get("urgency", "medium")).strip().lower(),
            "confidence": float(analysis.get("confidence", 0.8)),
            "meeting_duration_estimate": str(analysis.get("meeting_duration_estimate", "unknown")).strip(),
            "key_themes": [str(theme).strip() for theme in key_themes if str(theme).strip()]
        }

        # Validate enum values
        if validated_analysis["sentiment"] not in ["positive", "negative", "neutral", "mixed"]:
            validated_analysis["sentiment"] = "neutral"

        if validated_analysis["urgency"] not in ["low", "medium", "high"]:
            validated_analysis["urgency"] = "medium"

        logger.info(f"AI meeting analysis: {validated_analysis['meeting_type']}, {len(validated_analysis['attendees'])} attendees")
        return validated_analysis

    except Exception as e:
        logger.error(f"AI meeting analysis failed: {e}")
        return _fallback_analyze_meeting(transcript)

def _ai_extract_deadlines(client, transcript: str) -> List[Dict[str, str]]:
    """
    Use OpenAI to extract time-sensitive information and deadlines.
    Enhanced with better error handling.
    """

    system_prompt = """You are an expert at identifying deadlines and time-sensitive information in meetings.

Extract ALL mentions of:
- Specific deadlines and due dates
- Time-sensitive commitments
- Scheduled events or meetings
- Time-bound deliverables

Return a JSON array of objects:
[
    {
        "deadline": "what is due",
        "date": "when it's due",
        "urgency": "high/medium/low",
        "context": "additional context",
        "responsible_party": "who is responsible"
    }
]

Look for phrases mentioning time:
- "by Friday", "end of month", "next week"
- "due on", "deadline is", "needs to be done by"
- Specific dates mentioned
- Meeting scheduling"""

    user_prompt = f"Extract deadlines and time-sensitive items:\n\n{transcript}"

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = client.chat_completion(messages, temperature=0.1, max_tokens=800)

        # Safe JSON parsing with better error handling
        try:
            deadlines = json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON response for deadlines: {e}")
            return []

        # Enhanced validation with safe null handling
        validated_deadlines = []

        if not isinstance(deadlines, list):
            logger.warning("Deadlines response is not a list")
            return []

        for deadline in deadlines:
            if isinstance(deadline, dict) and deadline.get("deadline"):
                # Safe string extraction with comprehensive null checking
                deadline_text = deadline.get("deadline")
                if deadline_text is None:
                    continue

                deadline_text = str(deadline_text).strip() if deadline_text else ""
                if not deadline_text:
                    continue

                # Safe extraction of other fields
                date_text = deadline.get("date")
                date_text = str(date_text).strip() if date_text else "not specified"

                context_text = deadline.get("context")
                context_text = str(context_text).strip() if context_text else ""

                responsible_text = deadline.get("responsible_party")
                responsible_text = str(responsible_text).strip() if responsible_text else "not specified"

                urgency = str(deadline.get("urgency", "medium")).strip().lower()
                if urgency not in ["high", "medium", "low"]:
                    urgency = "medium"

                validated_deadline = {
                    "deadline": deadline_text,
                    "date": date_text,
                    "urgency": urgency,
                    "context": context_text,
                    "responsible_party": responsible_text
                }

                validated_deadlines.append(validated_deadline)

        logger.info(f"AI extracted {len(validated_deadlines)} deadlines")
        return validated_deadlines[:8]  # Limit to top 8

    except Exception as e:
        logger.error(f"AI deadline extraction failed: {e}")
        return []  # Return empty list on any error

def _create_empty_analysis(state: MeetingState) -> MeetingState:
    """Create empty analysis structure when no content is available."""
    result_state = state.copy()
    result_state["extracted_info"] = {}
    result_state["action_items"] = []
    result_state["decisions"] = []
    result_state["key_points"] = []
    result_state["attendees"] = []
    result_state["meeting_type"] = "General Meeting"
    result_state["topics_discussed"] = []
    result_state["deadlines_mentioned"] = []
    return result_state

# ================================
# FALLBACK FUNCTIONS (if AI fails)
# ================================

def _fallback_extract_action_items(transcript: str) -> List[Dict[str, str]]:
    """Fallback action item extraction if AI fails."""
    logger.warning("Using fallback action item extraction")

    action_items = []

    # Simple pattern matching as fallback
    import re
    action_patterns = [
        r'(\w+) will (.+?)(?:\.|$)',
        r'(\w+) should (.+?)(?:\.|$)',
        r'(\w+) needs to (.+?)(?:\.|$)',
    ]

    for pattern in action_patterns:
        matches = re.finditer(pattern, transcript, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) >= 2:
                assignee = match.group(1).strip().title()
                task = match.group(2).strip()

                if len(task) > 10:
                    action_items.append({
                        "task": task.capitalize(),
                        "assignee": assignee,
                        "deadline": "not specified",
                        "priority": "medium",
                        "context": "Extracted using fallback method",
                        "status": "pending"
                    })

    return action_items[:10]

def _fallback_extract_decisions(transcript: str) -> List[Dict[str, str]]:
    """Fallback decision extraction if AI fails."""
    logger.warning("Using fallback decision extraction")

    decisions = []
    decision_patterns = [
        r'we decided (.+?)(?:\.|$)',
        r'decision[:\s]*(.+?)(?:\.|$)',
        r'we agreed (.+?)(?:\.|$)',
    ]

    import re
    for pattern in decision_patterns:
        matches = re.finditer(pattern, transcript, re.IGNORECASE)
        for match in matches:
            decision_text = match.group(1).strip()
            if len(decision_text) > 5:
                decisions.append({
                    "decision": decision_text.capitalize(),
                    "context": "Meeting discussion",
                    "rationale": "not specified",
                    "impact": "Team/Project",
                    "implementation_date": "not specified",
                    "stakeholders": []
                })

    return decisions[:8]

def _fallback_extract_key_points(transcript: str) -> List[str]:
    """Fallback key points extraction if AI fails."""
    logger.warning("Using fallback key points extraction")

    # Extract longer sentences as potential key points
    sentences = transcript.split('.')
    key_points = []

    for sentence in sentences:
        sentence = sentence.strip()
        # Look for sentences with important keywords
        if len(sentence) > 30 and any(word in sentence.lower() for word in
                                     ['important', 'key', 'critical', 'issue', 'problem', 'budget', 'timeline']):
            key_points.append(sentence)

    return key_points[:8]

def _fallback_analyze_meeting(transcript: str) -> Dict[str, Any]:
    """Fallback meeting analysis if AI fails."""
    logger.warning("Using fallback meeting analysis")

    # Simple keyword-based analysis
    transcript_lower = transcript.lower()

    meeting_type = "General Meeting"
    if any(word in transcript_lower for word in ['standup', 'daily', 'scrum']):
        meeting_type = "Daily Standup"
    elif any(word in transcript_lower for word in ['client', 'customer']):
        meeting_type = "Client Meeting"
    elif any(word in transcript_lower for word in ['planning', 'sprint']):
        meeting_type = "Planning Meeting"

    # Extract names (simple pattern)
    import re
    attendees = []
    speaker_pattern = r'^([A-Za-z_][A-Za-z0-9_\s]*?):\s*'
    lines = transcript.split('\n')
    for line in lines:
        match = re.match(speaker_pattern, line.strip())
        if match:
            attendees.append(match.group(1).strip().title())

    return {
        "meeting_type": meeting_type,
        "attendees": list(set(attendees)),
        "topics": ["General Discussion"],
        "sentiment": "neutral",
        "urgency": "medium",
        "confidence": 0.6,
        "meeting_duration_estimate": "unknown",
        "key_themes": []
    }

# ================================
# TESTING FUNCTIONS
# ================================

def test_content_analyzer(sample_transcript: str = None) -> Dict[str, Any]:
    """
    Test the enhanced content analyzer with sample data.

    Args:
        sample_transcript: Optional transcript to test with

    Returns:
        Test results dictionary
    """
    if not sample_transcript:
        sample_transcript = """
John: We need to finish the project by Friday. Sarah will handle the database setup.
Sarah: I can complete that by Thursday. We decided to go with PostgreSQL for better performance.
Mike: I'll work on the API endpoints. The client presentation is scheduled for next Monday.
Jennifer: Important to note that the budget was approved for $50,000. We should prioritize the user authentication feature.
John: Great decisions everyone. Let's have a follow-up meeting on Wednesday to review progress.
"""

    # Create test state
    from utils.state_models import create_initial_state
    test_state = create_initial_state("", {"test": True}, "test")
    test_state["cleaned_transcript"] = sample_transcript

    try:
        start_time = time.time()
        result_state = analyze_content(test_state)
        processing_time = time.time() - start_time

        extracted_info = result_state.get("extracted_info", {})

        return {
            "success": True,
            "action_items_found": len(result_state.get("action_items", [])),
            "decisions_found": len(result_state.get("decisions", [])),
            "key_points_found": len(result_state.get("key_points", [])),
            "attendees_found": len(result_state.get("attendees", [])),
            "meeting_type": result_state.get("meeting_type", "Unknown"),
            "topics_found": len(result_state.get("topics_discussed", [])),
            "deadlines_found": len(result_state.get("deadlines_mentioned", [])),
            "processing_time": processing_time,
            "ai_enhanced": extracted_info.get("extraction_method") == "openai_gpt4o_mini",
            "ai_confidence": extracted_info.get("ai_confidence", 0.0),
            "total_items": extracted_info.get("total_items_extracted", 0)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Test the enhanced agent
    test_result = test_content_analyzer()
    print("Enhanced Content Analyzer Test Results:")
    for key, value in test_result.items():
        print(f"  {key}: {value}")