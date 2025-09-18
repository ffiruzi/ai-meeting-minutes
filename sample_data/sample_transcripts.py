

TEAM_STANDUP_TRANSCRIPT = """
John: Alright everyone, let's, uh, start our daily standup. Sarah, you want to go first?

Sarah: Sure. So yesterday I, um, finished the user authentication module. Today I'm going to work on the, uh, the dashboard components. No blockers for me.

Mike: Great. I worked on the API endpoints yesterday. Got the user management endpoints done. Today I'll be working on the, you know, the data analytics endpoints. I'm blocked on the database schema though - we need to decide on the user permissions structure.

Jennifer: Okay, I can help with that. I finished the database design yesterday. Mike, let's, uh, let's schedule a quick call after this meeting to go over the permissions. I'm working on the frontend integration today.

John: Perfect. I'll be working on deployment configurations today. Mike, Jennifer, can you guys have that permissions thing sorted by tomorrow? We need to ship this by Friday.

Mike: Yeah, definitely. Jennifer, how about we meet at 2 PM?

Jennifer: Works for me. I'll send a calendar invite.

John: Great. Any other blockers? No? Alright, let's, uh, let's get to work. Thanks everyone.
"""

CLIENT_MEETING_TRANSCRIPT = """
Alex: Good morning everyone. Thanks for joining us today. We're here to discuss the Q2 marketing campaign for the product launch.

Client_Representative: Thanks for having us, Alex. We're excited to see what you've prepared.

Alex: Absolutely. So, Maria, do you want to walk them through the strategy?

Maria: Of course. So we've developed a three-phase approach. Phase one is, um, pre-launch buzz on social media. We're targeting Instagram, TikTok, and LinkedIn. Budget for this phase is about $50,000.

Client_Representative: That sounds good. What's the timeline on phase one?

Maria: We'd start immediately and run for, uh, six weeks leading up to launch. Phase two is the actual launch event - we're thinking a virtual event with influencer partnerships. That's another $75,000.

David: And I'll be handling the PR side. We've got connections with TechCrunch, Mashable, and other tech publications. We can coordinate press releases with the launch event.

Client_Representative: Excellent. What about phase three?

Alex: Phase three is post-launch sustained marketing. We'll analyze the performance from phases one and two and, uh, optimize the ongoing campaigns. We're looking at about $100,000 for the full quarter.

Client_Representative: The budget looks reasonable. When do you need approval to get started?

Maria: Ideally by next Wednesday. That gives us enough time to, you know, set up the campaigns and get everything ready for the six-week pre-launch period.

Client_Representative: Perfect. I'll review this with the team and get back to you by Tuesday.

Alex: That works perfectly. David, can you send them the detailed proposal document?

David: Absolutely, I'll email it right after this meeting.

Client_Representative: Great. Looking forward to working together on this.
"""

PROJECT_PLANNING_TRANSCRIPT = """
Team_Lead: Okay everyone, we need to plan out the next sprint for the e-commerce platform. We've got some, uh, some big features to tackle.

Developer_1: What's the priority list looking like?

Team_Lead: Good question. So we've got the shopping cart redesign, the payment integration, and the, um, the inventory management system. Plus some bug fixes from last sprint.

Designer: The shopping cart redesign is ready from my end. I've got all the mockups and, uh, user flow diagrams ready.

Developer_1: How complex is the payment integration? Are we talking Stripe, PayPal, or...?

Team_Lead: We need to support both Stripe and PayPal. The client wants multiple payment options. Developer_2, you've worked with payment APIs before, right?

Developer_2: Yeah, I've done Stripe integration on previous projects. PayPal is a bit more complex but, uh, definitely doable. I'd estimate about two weeks for both integrations.

Team_Lead: Perfect. What about the inventory management system?

Developer_1: That's going to be the biggest piece. We need real-time inventory tracking, low stock alerts, and integration with the warehouse management system. I'm thinking three weeks minimum.

Designer: Do we have the UI designs for the inventory system?

Team_Lead: Not yet. Designer, can you prioritize that? We'll need the designs by end of this week to stay on schedule.

Designer: Absolutely. I'll have wireframes by Wednesday and final designs by Friday.

Developer_2: What about the bug fixes? Should we tackle those first?

Team_Lead: Good point. Let's assign the critical bugs to be fixed this week. Developer_1, can you handle the checkout flow bug? Developer_2, you take the user registration issue.

Developer_1: Sure thing. I'll have the checkout bug fixed by Thursday.

Developer_2: The registration bug should be done by Tuesday. It's just a validation issue.

Team_Lead: Excellent. So to recap: bug fixes this week, payment integration starts next week, inventory system after that. Designer gets us the inventory designs by Friday. Everyone good with this timeline?

Everyone: Yes / Sounds good / Agreed.

Team_Lead: Great. Let's, uh, let's make this sprint count. Meeting adjourned.
"""

BOARD_MEETING_TRANSCRIPT = """
Chairman: Good afternoon, board members. Let's call this quarterly board meeting to order. First item on the agenda is the Q3 financial report.

CFO: Thank you, Chairman. I'm pleased to report that Q3 exceeded our projections. Revenue came in at $2.3 million, which is, uh, 15% above our target of $2 million.

Board_Member_1: That's excellent news. What were the main drivers of this outperformance?

CFO: The new product line launched in July performed exceptionally well. It accounted for about 40% of the revenue beat. Additionally, our, um, our cost reduction initiatives saved us about $150,000 this quarter.

CEO: I'd like to add that our customer acquisition costs also decreased by 20%. The marketing team's new digital strategy is really paying off.

Board_Member_2: What's the outlook for Q4?

CEO: We're cautiously optimistic. We're projecting $2.5 million in revenue for Q4. However, we're, uh, we're watching the economic indicators closely given the market volatility.

Chairman: Speaking of market conditions, how are we positioned competitively?

CEO: We've gained market share in our core segment. Our main competitor had some, um, some supply chain issues that we were able to capitalize on. We picked up about 150 new enterprise clients this quarter.

Board_Member_1: Excellent. What about the expansion into the European market we discussed last quarter?

CEO: We've made good progress there. We've hired a VP of European Operations, and we're targeting a soft launch in Germany and the UK by February. The regulatory approvals are, uh, are moving through the process.

CFO: From a financial perspective, we've allocated $500,000 for the European expansion. That's within our approved budget.

Board_Member_2: Any major risks we should be aware of?

CEO: The main risk is still the potential economic downturn. We've stress-tested our financials, and we can weather a 20% revenue decline without major layoffs. We also have, um, we have six months of operating expenses in cash reserves.

Chairman: That's prudent planning. Any other business? No? Then I'd like to call for a vote on the Q4 budget proposal.

Board_Member_1: I move to approve the Q4 budget as presented.

Board_Member_2: Seconded.

Chairman: All in favor? Unanimous. The Q4 budget is approved. Meeting adjourned.
"""

# Dictionary for easy access to sample transcripts
SAMPLE_TRANSCRIPTS = {
    "team_standup": {
        "title": "Daily Team Standup",
        "description": "A typical daily standup meeting with a development team",
        "transcript": TEAM_STANDUP_TRANSCRIPT,
        "metadata": {
            "meeting_type": "Daily Standup",
            "attendees": ["John (Scrum Master)", "Sarah (Developer)", "Mike (Developer)", "Jennifer (Frontend Developer)"],
            "duration": "15 minutes",
            "date": "2024-01-15"
        }
    },
    "client_meeting": {
        "title": "Client Marketing Strategy Meeting",
        "description": "Marketing agency presenting campaign strategy to client",
        "transcript": CLIENT_MEETING_TRANSCRIPT,
        "metadata": {
            "meeting_type": "Client Presentation",
            "attendees": ["Alex (Account Manager)", "Maria (Marketing Lead)", "David (PR Manager)", "Client Representative"],
            "duration": "45 minutes",
            "date": "2024-01-16"
        }
    },
    "project_planning": {
        "title": "Sprint Planning Meeting",
        "description": "Development team planning next sprint features and tasks",
        "transcript": PROJECT_PLANNING_TRANSCRIPT,
        "metadata": {
            "meeting_type": "Sprint Planning",
            "attendees": ["Team Lead", "Developer 1", "Developer 2", "Designer"],
            "duration": "60 minutes",
            "date": "2024-01-17"
        }
    },
    "board_meeting": {
        "title": "Quarterly Board Meeting",
        "description": "Executive board meeting reviewing quarterly performance",
        "transcript": BOARD_MEETING_TRANSCRIPT,
        "metadata": {
            "meeting_type": "Board Meeting",
            "attendees": ["Chairman", "CEO", "CFO", "Board Member 1", "Board Member 2"],
            "duration": "90 minutes",
            "date": "2024-01-18"
        }
    }
}

def get_sample_transcript(sample_key: str) -> dict:
    """
    Get a sample transcript by key.

    Args:
        sample_key: Key for the sample transcript

    Returns:
        Dictionary containing transcript and metadata
    """
    return SAMPLE_TRANSCRIPTS.get(sample_key, {})

def get_all_sample_keys() -> list:
    """
    Get list of all available sample transcript keys.

    Returns:
        List of sample transcript keys
    """
    return list(SAMPLE_TRANSCRIPTS.keys())

def get_sample_titles() -> dict:
    """
    Get mapping of keys to titles for UI display.

    Returns:
        Dictionary mapping keys to display titles
    """
    return {key: data["title"] for key, data in SAMPLE_TRANSCRIPTS.items()}