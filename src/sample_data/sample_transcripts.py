"""
Sample meeting transcripts for demonstration and testing.
"""

SAMPLE_TRANSCRIPTS = {
    "daily_standup": {
        "title": "Daily Standup Meeting",
        "transcript": """
John: Good morning everyone, let's start our daily standup.
Sarah: Yesterday I completed the user authentication module. Today I'll work on the API integration.
Mike: I finished the database migration and will focus on frontend components today.
Lisa: I worked on bug fixes yesterday. Planning to review the pull requests today.
John: Great updates everyone. Any blockers?
Sarah: I need the API documentation from the backend team.
Mike: No blockers on my end.
Lisa: All good here.
John: Thanks everyone, let's have a productive day!
        """,
        "metadata": {
            "meeting_type": "Daily Standup",
            "duration": "15 minutes",
            "attendees": ["John", "Sarah", "Mike", "Lisa"]
        }
    },

    "planning_session": {
        "title": "Sprint Planning Session",
        "transcript": """
Manager: Welcome to sprint planning. Let's review our backlog.
Developer1: The user stories for the payment system are ready.
Developer2: I estimate the payment integration at 5 story points.
QA: We'll need 2 days for testing after development.
Manager: Sounds good. What about the reporting feature?
Developer1: That's more complex, probably 8 story points.
Developer2: I agree, especially with the data visualization requirements.
QA: Testing for reporting will need 3 days.
Manager: Let's prioritize payment system first, then reporting.
Developer1: Agreed. I'll take the payment system.
Developer2: I'll handle the reporting feature.
Manager: Perfect. Sprint goal is payment system completion.
        """,
        "metadata": {
            "meeting_type": "Planning Session",
            "duration": "45 minutes",
            "attendees": ["Manager", "Developer1", "Developer2", "QA"]
        }
    }
}

def get_sample_transcript(key: str) -> dict:
    """Get a sample transcript by key."""
    return SAMPLE_TRANSCRIPTS.get(key, {})

def get_all_sample_keys() -> list:
    """Get all available sample transcript keys."""
    return list(SAMPLE_TRANSCRIPTS.keys())

def get_sample_titles() -> dict:
    """Get mapping of keys to titles."""
    return {key: data["title"] for key, data in SAMPLE_TRANSCRIPTS.items()}
