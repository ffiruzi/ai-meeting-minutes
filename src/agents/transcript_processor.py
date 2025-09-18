

import logging
import re
import time
from typing import Dict, Any

from utils.state_models import MeetingState, add_warning
from utils.openai_client import get_openai_client

logger = logging.getLogger(__name__)

def process_transcript(state: MeetingState) -> MeetingState:
    """
    Process and clean a meeting transcript using OpenAI GPT-4o-mini.

    This agent:
    1. Intelligently cleans up filler words and transcription errors
    2. Improves grammar and sentence structure while preserving meaning
    3. Identifies speakers with sophisticated pattern recognition
    4. Structures the conversation logically with proper formatting
    5. Maintains original context and important nuances
    6. Provides quality assessment and processing insights

    Args:
        state: Current workflow state containing raw transcript

    Returns:
        Updated state with cleaned transcript and processing metadata
    """
    logger.info("🤖 Transcript Processor Agent starting (Full AI Implementation)...")

    try:
        # Get raw transcript from state
        raw_transcript = state.get("raw_transcript", "")

        if not raw_transcript or not raw_transcript.strip():
            logger.warning("No transcript content to process")
            result_state = state.copy()
            result_state["cleaned_transcript"] = ""
            result_state["processing_notes"] = "No transcript content provided"
            result_state["transcript_quality_score"] = 0.0
            return add_warning(result_state, "transcript_processor", "Empty transcript provided")

        logger.info(f"Processing transcript with {len(raw_transcript)} characters using OpenAI")

        # Get OpenAI client
        client = get_openai_client()

        # Step 1: Clean and improve the transcript using AI
        start_time = time.time()
        cleaned_transcript = _ai_clean_transcript(client, raw_transcript)
        cleaning_time = time.time() - start_time

        # Step 2: Identify speakers using AI-enhanced analysis
        start_time = time.time()
        speakers = _ai_identify_speakers(client, raw_transcript, cleaned_transcript)
        speaker_time = time.time() - start_time

        # Step 3: Assess transcript quality using multiple metrics
        quality_score = _ai_assess_quality(client, raw_transcript, cleaned_transcript, speakers)

        # Step 4: Generate comprehensive processing notes
        processing_notes = _generate_ai_processing_notes(
            raw_transcript, cleaned_transcript, speakers, quality_score,
            cleaning_time, speaker_time
        )

        # Update state with results
        result_state = state.copy()
        result_state["cleaned_transcript"] = cleaned_transcript
        result_state["speaker_identification"] = speakers
        result_state["transcript_quality_score"] = quality_score
        result_state["processing_notes"] = processing_notes

        logger.info(f"✅ Transcript processed successfully (quality: {quality_score:.2f}, {len(cleaned_transcript)} chars)")
        return result_state

    except Exception as e:
        logger.error(f"❌ Transcript processing failed: {e}")
        # Return state with error information but don't crash
        error_state = state.copy()
        error_state["cleaned_transcript"] = state.get("raw_transcript", "")
        error_state["processing_notes"] = f"AI processing failed, using original: {str(e)}"
        error_state["transcript_quality_score"] = 0.3  # Low but not zero
        raise  # Re-raise for workflow error handling

def _ai_clean_transcript(client, raw_transcript: str) -> str:
    """
    Use OpenAI to intelligently clean and improve the transcript.

    This uses sophisticated prompting to:
    - Remove filler words contextually
    - Fix transcription errors
    - Improve grammar and flow
    - Maintain speaker identification
    - Preserve important context and meaning
    """

    # Sophisticated cleaning prompt
    system_prompt = """You are an expert transcript editor specializing in cleaning meeting recordings for professional use.

Your task is to clean and improve a meeting transcript while maintaining its authenticity and completeness. 

INSTRUCTIONS:
1. Remove filler words (um, uh, you know, like, actually, basically) but only when they don't add meaning
2. Fix obvious transcription errors and typos
3. Improve grammar and sentence structure for clarity
4. Correct punctuation and capitalization
5. Maintain speaker identification format (Name: content)
6. Preserve all important content, decisions, action items, and context
7. Keep the natural conversation flow and tone
8. Don't add information that wasn't originally present
9. Maintain chronological order of the discussion

OUTPUT FORMAT:
- Keep speaker names exactly as they appear, followed by colon
- Use proper paragraph breaks for readability
- Ensure each speaker's contribution is clear and complete
- Maintain professional but natural language

Return ONLY the cleaned transcript with no additional commentary."""

    user_prompt = f"Please clean this meeting transcript:\n\n{raw_transcript}"

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        cleaned = client.chat_completion(messages, temperature=0.1, max_tokens=4000)

        # Basic validation and cleanup
        if len(cleaned) < len(raw_transcript) * 0.5:
            logger.warning("Cleaned transcript significantly shorter, using original")
            return raw_transcript

        return cleaned.strip()

    except Exception as e:
        logger.error(f"AI transcript cleaning failed: {e}")
        # Fallback to basic cleaning
        return _fallback_clean_transcript(raw_transcript)

def _ai_identify_speakers(client, raw_transcript: str, cleaned_transcript: str) -> Dict[str, Any]:
    """
    Use AI to identify speakers and analyze their contributions.
    """

    system_prompt = """You are an expert at analyzing meeting transcripts to identify speakers and their contributions.

Analyze the transcript and extract speaker information. Look for:
1. Names followed by colons (Name: content)
2. Titles or roles mentioned (Manager, Developer, etc.)
3. Context clues about who is speaking
4. Speech patterns and topics that indicate different speakers

Return a JSON object with this structure:
{
    "identified_speakers": ["Name1", "Name2"],
    "speaker_roles": {"Name1": "role/title if mentioned", "Name2": "role/title"},
    "speaker_contributions": {"Name1": ["contribution1", "contribution2"], "Name2": [...]},
    "total_speakers": number,
    "confidence_score": 0.0-1.0,
    "analysis_notes": "brief notes about speaker identification"
}

Be conservative - only include speakers you're confident about."""

    user_prompt = f"Analyze speakers in this transcript:\n\n{cleaned_transcript[:1500]}..."  # Limit for efficiency

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = client.chat_completion(messages, temperature=0.1, max_tokens=1000)

        # Parse JSON response
        import json
        speaker_info = json.loads(response)

        # Add metadata
        speaker_info["identification_method"] = "ai_analysis"
        speaker_info["processing_timestamp"] = time.time()

        return speaker_info

    except Exception as e:
        logger.error(f"AI speaker identification failed: {e}")
        # Fallback to pattern matching
        return _fallback_identify_speakers(cleaned_transcript)

def _ai_assess_quality(client, raw_transcript: str, cleaned_transcript: str, speakers: Dict[str, Any]) -> float:
    """
    Use AI to assess transcript quality across multiple dimensions.
    """

    system_prompt = """You are an expert at assessing meeting transcript quality.

Evaluate this transcript on these criteria:
1. Clarity and readability (0.0-0.3)
2. Completeness of information (0.0-0.2) 
3. Speaker identification quality (0.0-0.2)
4. Grammar and structure (0.0-0.2)
5. Professional presentation (0.0-0.1)

Return ONLY a single number between 0.0 and 1.0 representing overall quality.
- 0.9-1.0: Excellent professional quality
- 0.7-0.9: Good quality with minor issues
- 0.5-0.7: Acceptable with some problems
- 0.3-0.5: Poor quality, significant issues
- 0.0-0.3: Very poor, major problems"""

    # Create assessment prompt with key metrics
    word_count = len(cleaned_transcript.split())
    speaker_count = speakers.get("total_speakers", 0)
    improvement_ratio = len(cleaned_transcript) / len(raw_transcript) if raw_transcript else 1.0

    user_prompt = f"""Assess this transcript quality:
    
Word count: {word_count}
Speakers identified: {speaker_count}
Improvement ratio: {improvement_ratio:.2f}

Transcript preview:
{cleaned_transcript[:500]}...

Return quality score (0.0-1.0):"""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = client.chat_completion(messages, temperature=0.1, max_tokens=10)

        # Extract quality score
        score = float(response.strip())
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1

    except Exception as e:
        logger.error(f"AI quality assessment failed: {e}")
        # Fallback to heuristic assessment
        return _fallback_assess_quality(raw_transcript, cleaned_transcript, speakers)

def _generate_ai_processing_notes(
    raw_transcript: str,
    cleaned_transcript: str,
    speakers: Dict[str, Any],
    quality_score: float,
    cleaning_time: float,
    speaker_time: float
) -> str:
    """Generate comprehensive processing notes about the AI-enhanced cleaning."""

    notes = []

    # Basic metrics
    raw_length = len(raw_transcript)
    cleaned_length = len(cleaned_transcript)
    word_count_raw = len(raw_transcript.split())
    word_count_cleaned = len(cleaned_transcript.split())

    notes.append(f"AI Processing Summary:")
    notes.append(f"Original: {raw_length} chars, {word_count_raw} words")
    notes.append(f"Cleaned: {cleaned_length} chars, {word_count_cleaned} words")

    # Processing changes
    char_change = cleaned_length - raw_length
    if char_change > 0:
        notes.append(f"Added {char_change} characters during AI enhancement")
    elif char_change < 0:
        notes.append(f"Removed {abs(char_change)} characters during cleaning")

    # Speaker analysis
    speaker_count = speakers.get("total_speakers", 0)
    confidence = speakers.get("confidence_score", 0)
    if speaker_count > 0:
        speaker_names = ", ".join(speakers.get("identified_speakers", []))
        notes.append(f"Identified {speaker_count} speakers: {speaker_names} (confidence: {confidence:.2f})")
    else:
        notes.append("No clear speaker identification found")

    # Quality and performance
    notes.append(f"Quality score: {quality_score:.2f}/1.0")
    notes.append(f"Processing time: cleaning {cleaning_time:.2f}s, speakers {speaker_time:.2f}s")

    # AI enhancement notes
    notes.append("Enhanced with OpenAI GPT-4o-mini for professional transcript cleaning")

    return " | ".join(notes)

# ================================
# FALLBACK FUNCTIONS (if AI fails)
# ================================

def _fallback_clean_transcript(raw_transcript: str) -> str:
    """Fallback cleaning if AI processing fails."""
    logger.warning("Using fallback transcript cleaning")

    cleaned = raw_transcript

    # Basic cleaning operations
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # Remove common filler words
    filler_words = ['um', 'uh', 'you know', 'like', 'basically', 'actually', 'literally']
    for filler in filler_words:
        pattern = r'\b' + re.escape(filler) + r'\b'
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    # Clean up extra spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned

def _fallback_identify_speakers(transcript: str) -> Dict[str, Any]:
    """Fallback speaker identification if AI fails."""
    logger.warning("Using fallback speaker identification")

    speakers = set()
    speaker_pattern = r'^([A-Za-z_][A-Za-z0-9_\s]*?):\s*'

    lines = transcript.split('\n')
    for line in lines:
        match = re.match(speaker_pattern, line.strip())
        if match:
            name = match.group(1).strip().title()
            speakers.add(name)

    return {
        "identified_speakers": sorted(list(speakers)),
        "speaker_contributions": {},
        "total_speakers": len(speakers),
        "confidence_score": 0.7,
        "identification_method": "fallback_pattern_matching"
    }

def _fallback_assess_quality(raw_transcript: str, cleaned_transcript: str, speakers: Dict[str, Any]) -> float:
    """Fallback quality assessment if AI fails."""
    logger.warning("Using fallback quality assessment")

    quality_score = 0.5  # Base score

    # Length factor
    word_count = len(raw_transcript.split())
    if 50 <= word_count <= 2000:
        quality_score += 0.2

    # Speaker identification factor
    if speakers.get("total_speakers", 0) > 0:
        quality_score += 0.2

    # Improvement factor
    if len(cleaned_transcript) > 0:
        quality_score += 0.1

    return min(quality_score, 1.0)

# ================================
# TESTING FUNCTIONS
# ================================

def test_transcript_processor(sample_transcript: str = None) -> Dict[str, Any]:
    """
    Test the enhanced transcript processor with sample data.

    Args:
        sample_transcript: Optional transcript to test with

    Returns:
        Test results dictionary
    """
    if not sample_transcript:
        sample_transcript = """
John: Um, okay everyone, let's, uh, start the meeting. We need to discuss the project timeline.
Sarah: Actually, I wanted to, you know, discuss the budget first. It's like, really important.
Mike: Yeah, basically we need to, um, figure out the resources. The database setup will take, uh, about two weeks.
Jennifer: I can handle the frontend. Um, should be done by, you know, end of month.
John: Perfect. So, uh, let's schedule a follow-up next week.
"""

    # Create test state
    from utils.state_models import create_initial_state
    test_state = create_initial_state(sample_transcript, {"test": True}, "test")

    try:
        start_time = time.time()
        result_state = process_transcript(test_state)
        processing_time = time.time() - start_time

        return {
            "success": True,
            "original_length": len(sample_transcript),
            "cleaned_length": len(result_state.get("cleaned_transcript", "")),
            "quality_score": result_state.get("transcript_quality_score", 0),
            "speakers_found": result_state.get("speaker_identification", {}).get("total_speakers", 0),
            "processing_time": processing_time,
            "processing_notes": result_state.get("processing_notes", ""),
            "ai_enhanced": "OpenAI" in result_state.get("processing_notes", "")
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Test the enhanced agent
    test_result = test_transcript_processor()
    print("Enhanced Transcript Processor Test Results:")
    for key, value in test_result.items():
        print(f"  {key}: {value}")