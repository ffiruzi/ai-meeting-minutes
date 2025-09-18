"""
OpenAI API client utility for Meeting Minutes Generator.
Handles all interactions with OpenAI's GPT-4o-mini API.

Day 4 Update: Production-ready client with optimized settings for all 4 AI agents.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIClient:
    """
    Enhanced wrapper class for OpenAI API interactions.
    Provides specialized methods for different AI agent processing tasks.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI client with production settings.

        Args:
            api_key: OpenAI API key (if not provided, loads from environment)
            model: OpenAI model to use (default: gpt-4o-mini - cost-effective and capable)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")

        if self.api_key == "your_openai_api_key_here":
            raise ValueError("Please replace placeholder with actual OpenAI API key in .env file")

        try:
            self.client = OpenAI(
                api_key=self.api_key,
                organization=os.getenv("OPENAI_ORG_ID")  # Optional
            )
            logger.info(f"OpenAI client initialized successfully with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Create a chat completion using OpenAI API.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response

        Returns:
            Generated text response

        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            content = response.choices[0].message.content
            logger.debug(f"Successfully generated response with {len(content)} characters")
            return content

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")

    def process_transcript(self, transcript: str) -> str:
        """
        Clean and process a meeting transcript using AI.
        Optimized for transcript processor agent.

        Args:
            transcript: Raw meeting transcript text

        Returns:
            Cleaned and structured transcript
        """
        messages = [
            {
                "role": "system",
                "content": """You are an expert transcript editor specializing in cleaning meeting recordings for professional use.

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
            },
            {
                "role": "user",
                "content": f"Please clean this meeting transcript:\n\n{transcript}"
            }
        ]

        return self.chat_completion(messages, temperature=0.1, max_tokens=4000)

    def extract_content(self, transcript: str) -> str:
        """
        Extract structured information from a meeting transcript.
        Optimized for content analyzer agent.

        Args:
            transcript: Cleaned meeting transcript

        Returns:
            JSON string with extracted information
        """
        messages = [
            {
                "role": "system",
                "content": """You are an expert at extracting structured information from meeting transcripts.

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

Be thorough but precise. Only include clear, actionable tasks.
Return only valid JSON without additional text."""
            },
            {
                "role": "user",
                "content": f"Extract all action items from this meeting transcript:\n\n{transcript}"
            }
        ]

        return self.chat_completion(messages, temperature=0.1, max_tokens=2000)

    def generate_summary(self, transcript: str, extracted_info: str) -> str:
        """
        Generate an executive summary of the meeting.
        Optimized for summary writer agent.

        Args:
            transcript: Cleaned transcript
            extracted_info: JSON string of extracted information

        Returns:
            Executive summary text
        """
        messages = [
            {
                "role": "system",
                "content": """You are an executive assistant creating high-level summaries for senior leadership.

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
            },
            {
                "role": "user",
                "content": f"""Create an executive summary for this meeting:
                
TRANSCRIPT:
{transcript}
                
EXTRACTED INFO:
{extracted_info}"""
            }
        ]

        return self.chat_completion(messages, temperature=0.2, max_tokens=800)

    def format_minutes(
        self,
        summary: str,
        extracted_info: str,
        meeting_date: Optional[str] = None,
        attendees: Optional[str] = None
    ) -> str:
        """
        Format all information into professional meeting minutes.
        Optimized for minutes formatter agent.

        Args:
            summary: Executive summary
            extracted_info: JSON string of extracted information
            meeting_date: Meeting date (optional)
            attendees: Comma-separated attendees (optional)

        Returns:
            Formatted meeting minutes in Markdown
        """
        messages = [
            {
                "role": "system",
                "content": """You are a professional executive secretary creating formal meeting minutes for senior leadership.

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
            },
            {
                "role": "user",
                "content": f"""Format these into professional meeting minutes:
                
SUMMARY: {summary}
                
EXTRACTED INFO: {extracted_info}
                
MEETING DATE: {meeting_date or 'Not specified'}
                
ATTENDEES: {attendees or 'Not specified'}"""
            }
        ]

        return self.chat_completion(messages, temperature=0.1, max_tokens=4000)

    # Additional specialized methods for Day 4 agents

    def analyze_meeting_context(self, transcript: str) -> str:
        """
        Analyze meeting context and extract metadata.
        Used by content analyzer for meeting type detection and attendee identification.
        """
        messages = [
            {
                "role": "system",
                "content": """You are an expert at analyzing meeting context and extracting metadata.

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

Return only valid JSON with no additional text."""
            },
            {
                "role": "user",
                "content": f"Analyze this meeting for context and metadata:\n\n{transcript[:2000]}..."
            }
        ]

        return self.chat_completion(messages, temperature=0.1, max_tokens=800)

    def generate_insights(self, transcript: str, key_points: List[str]) -> str:
        """
        Generate strategic insights and observations.
        Used by summary writer for business intelligence.
        """
        key_points_str = "\n".join([f"• {point}" for point in key_points[:5]])

        messages = [
            {
                "role": "system",
                "content": """You are a business analyst generating strategic insights from meeting discussions.

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
            },
            {
                "role": "user",
                "content": f"""Generate strategic insights from this meeting:

KEY DISCUSSION POINTS:
{key_points_str}

TRANSCRIPT SAMPLE:
{transcript[:1500]}...

Generate 3-5 strategic insights about this meeting."""
            }
        ]

        return self.chat_completion(messages, temperature=0.3, max_tokens=600)

# Singleton instance for easy access
openai_client = None

def get_openai_client() -> OpenAIClient:
    """
    Get or create OpenAI client instance.

    Returns:
        OpenAIClient instance
    """
    global openai_client
    if openai_client is None:
        openai_client = OpenAIClient()
    return openai_client

def test_openai_connection() -> bool:
    """
    Test OpenAI API connection.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        client = get_openai_client()
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Connection test successful' if you can read this."}
        ]
        response = client.chat_completion(test_messages, max_tokens=10)
        return "successful" in response.lower()
    except Exception as e:
        logger.error(f"OpenAI connection test failed: {e}")
        return False

def get_api_status() -> Dict[str, Any]:
    """
    Get detailed API status and configuration information.

    Returns:
        Dictionary with API status details
    """
    try:
        client = get_openai_client()

        # Test basic connection
        connection_test = test_openai_connection()

        # Get model information
        model_info = {
            "model": client.model,
            "connection_status": "connected" if connection_test else "failed",
            "api_key_configured": bool(client.api_key and client.api_key != "your_openai_api_key_here"),
            "organization_id": bool(os.getenv("OPENAI_ORG_ID"))
        }

        return {
            "status": "operational" if connection_test else "error",
            "model_info": model_info,
            "capabilities": [
                "transcript_processing",
                "content_extraction",
                "summary_generation",
                "minutes_formatting",
                "context_analysis",
                "insight_generation"
            ],
            "production_ready": connection_test and model_info["api_key_configured"]
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "production_ready": False
        }