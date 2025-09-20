# app/data/__init__.py
# Empty file to make this a package

# app/data/mock_data.py
"""Mock data for development and testing"""

# Mock proposal data
MOCK_PROPOSAL_DATA = {
    "event_details": {
        "job_number": "306780",
        "client_name": "Customer Relationship Management",
        "event_location": "Omni PGA Frisco Resort",
        "venue": "Ryder Cup Ballroom DE (GB 4-5)",
        "start_date": "2026-05-31",
        "end_date": "2026-06-03",
        "prepared_by": "Shahar Zlochover",
        "salesperson": "Shahar Zlochover",
        "email": "shahar.zlochover@pinnaclelive.com",
        "status": "tentative",
        "version": "1.0",
        "last_modified": "2025-09-12T13:46:00Z"
    },
    "sections": [
        {
            "id": "audio",
            "title": "Audio Equipment",
            "is_expanded": True,
            "total": 18750,
            "items": [
                {
                    "id": "audio-1",
                    "quantity": 18,
                    "description": "12\" Line Array Speaker",
                    "duration": "3 Days",
                    "price": 250,
                    "discount": 0,
                    "subtotal": 13500,
                    "category": "audio",
                    "notes": "3 stacks of 3 tops and one sub for front speakers, 3 Stacks of 3 tops, 3 subs for delay"
                },
                {
                    "id": "audio-2",
                    "quantity": 6,
                    "description": "18\" Powered Subwoofer",
                    "duration": "3 Days",
                    "price": 180,
                    "discount": 0,
                    "subtotal": 3240,
                    "category": "audio"
                }
            ]
        },
        {
            "id": "lighting",
            "title": "Lighting Equipment",
            "is_expanded": False,
            "total": 24680,
            "items": [
                {
                    "id": "lighting-1",
                    "quantity": 24,
                    "description": "LED Par Can RGBW",
                    "duration": "3 Days",
                    "price": 85,
                    "discount": 0,
                    "subtotal": 6120,
                    "category": "lighting"
                }
            ]
        }
    ],
    "total_cost": 84780,
    "timeline": [
        {
            "id": "setup-day-1",
            "date": "2026-05-31",
            "start_time": "08:00",
            "end_time": "18:00",
            "title": "Load-in & Setup",
            "location": "Ryder Cup Ballroom DE",
            "setup": ["Audio rigging", "Lighting truss installation", "Video setup"],
            "equipment": ["Audio", "Lighting", "Staging"],
            "cost": 12500
        }
    ]
}

# Mock questions data
MOCK_QUESTIONS = [
    {
        "id": "q1",
        "item_id": "audio-1",
        "item_name": "12\" Line Array Speaker",
        "section_name": "Audio Equipment",
        "question": "Can these speakers handle outdoor conditions?",
        "status": "pending",
        "asked_by": "Sarah Johnson",
        "asked_at": "2025-09-19T14:30:00Z"
    }
]

# In-memory storage for questions (replace with database later)
questions_storage = MOCK_QUESTIONS.copy()