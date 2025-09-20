# app/api/proposals.py - Using the complete mock data structure
"""Proposals API endpoints"""

from fastapi import APIRouter, Request
from typing import List

router = APIRouter()

# Complete mock proposal data that matches frontend TypeScript interfaces
COMPLETE_MOCK_PROPOSAL = {
    "eventDetails": {
        "jobNumber": "306780",
        "clientName": "Customer Relationship Management",
        "eventLocation": "Omni PGA Frisco Resort",
        "venue": "Ryder Cup Ballroom DE (GB 4-5)",
        "startDate": "2026-05-31",
        "endDate": "2026-06-03",
        "preparedBy": "Shahar Zlochover",
        "salesperson": "Shahar Zlochover",
        "email": "shahar.zlochover@pinnaclelive.com",
        "status": "tentative",
        "version": "1.0",
        "lastModified": "2025-09-12T13:46:00Z"
    },
    "sections": [
        {
            "id": "audio",
            "title": "Audio Equipment",
            "isExpanded": True,
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
                },
                {
                    "id": "audio-3",
                    "quantity": 4,
                    "description": "G50 Wireless Microphone Handheld",
                    "duration": "3 Days",
                    "price": 65,
                    "discount": 0,
                    "subtotal": 780,
                    "category": "audio"
                },
                {
                    "id": "audio-4",
                    "quantity": 4,
                    "description": "Wireless Lavalier Microphone",
                    "duration": "3 Days",
                    "price": 75,
                    "discount": 0,
                    "subtotal": 900,
                    "category": "audio"
                },
                {
                    "id": "audio-5",
                    "quantity": 1,
                    "description": "24ch Digital Audio Mixer",
                    "duration": "3 Days",
                    "price": 330,
                    "discount": 0,
                    "subtotal": 990,
                    "category": "audio"
                }
            ]
        },
        {
            "id": "lighting",
            "title": "Lighting Equipment",
            "isExpanded": False,
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
                },
                {
                    "id": "lighting-2",
                    "quantity": 8,
                    "description": "Moving Head Spot Light",
                    "duration": "3 Days",
                    "price": 220,
                    "discount": 0,
                    "subtotal": 5280,
                    "category": "lighting"
                },
                {
                    "id": "lighting-3",
                    "quantity": 4,
                    "description": "Haze Machine",
                    "duration": "3 Days",
                    "price": 150,
                    "discount": 0,
                    "subtotal": 1800,
                    "category": "lighting"
                },
                {
                    "id": "lighting-4",
                    "quantity": 1,
                    "description": "Grand MA2 Light Console",
                    "duration": "3 Days",
                    "price": 850,
                    "discount": 0,
                    "subtotal": 2550,
                    "category": "lighting"
                },
                {
                    "id": "lighting-5",
                    "quantity": 50,
                    "description": "DMX Cable (25ft)",
                    "duration": "3 Days",
                    "price": 12,
                    "discount": 0,
                    "subtotal": 1800,
                    "category": "lighting"
                },
                {
                    "id": "lighting-6",
                    "quantity": 12,
                    "description": "Truss Section (10ft)",
                    "duration": "3 Days",
                    "price": 45,
                    "discount": 0,
                    "subtotal": 1620,
                    "category": "lighting"
                },
                {
                    "id": "lighting-7",
                    "quantity": 8,
                    "description": "Power Distribution",
                    "duration": "3 Days",
                    "price": 125,
                    "discount": 0,
                    "subtotal": 3000,
                    "category": "lighting"
                },
                {
                    "id": "lighting-8",
                    "quantity": 4,
                    "description": "Follow Spot",
                    "duration": "3 Days",
                    "price": 380,
                    "discount": 0,
                    "subtotal": 4560,
                    "category": "lighting"
                }
            ]
        },
        {
            "id": "video",
            "title": "Video & Projection",
            "isExpanded": False,
            "total": 16800,
            "items": [
                {
                    "id": "video-1",
                    "quantity": 2,
                    "description": "20K Lumens Projector",
                    "duration": "3 Days",
                    "price": 1200,
                    "discount": 0,
                    "subtotal": 7200,
                    "category": "video"
                },
                {
                    "id": "video-2",
                    "quantity": 2,
                    "description": "16x9 Fast-Fold Screen",
                    "duration": "3 Days",
                    "price": 450,
                    "discount": 0,
                    "subtotal": 2700,
                    "category": "video"
                },
                {
                    "id": "video-3",
                    "quantity": 4,
                    "description": "55\" LED Monitor",
                    "duration": "3 Days",
                    "price": 320,
                    "discount": 0,
                    "subtotal": 3840,
                    "category": "video"
                },
                {
                    "id": "video-4",
                    "quantity": 1,
                    "description": "Video Switcher",
                    "duration": "3 Days",
                    "price": 680,
                    "discount": 0,
                    "subtotal": 2040,
                    "category": "video"
                },
                {
                    "id": "video-5",
                    "quantity": 8,
                    "description": "HD-SDI Cable (50ft)",
                    "duration": "3 Days",
                    "price": 35,
                    "discount": 0,
                    "subtotal": 1050,
                    "category": "video"
                }
            ]
        },
        {
            "id": "staging",
            "title": "Staging & Set",
            "isExpanded": False,
            "total": 8950,
            "items": [
                {
                    "id": "staging-1",
                    "quantity": 12,
                    "description": "8x4 Stage Deck",
                    "duration": "3 Days",
                    "price": 120,
                    "discount": 0,
                    "subtotal": 4320,
                    "category": "staging"
                },
                {
                    "id": "staging-2",
                    "quantity": 4,
                    "description": "Stage Riser (2ft)",
                    "duration": "3 Days",
                    "price": 95,
                    "discount": 0,
                    "subtotal": 1140,
                    "category": "staging"
                },
                {
                    "id": "staging-3",
                    "quantity": 2,
                    "description": "Acrylic Podium",
                    "duration": "3 Days",
                    "price": 180,
                    "discount": 0,
                    "subtotal": 1080,
                    "category": "staging"
                },
                {
                    "id": "staging-4",
                    "quantity": 8,
                    "description": "Stage Skirt (Black)",
                    "duration": "3 Days",
                    "price": 25,
                    "discount": 0,
                    "subtotal": 600,
                    "category": "staging"
                },
                {
                    "id": "staging-5",
                    "quantity": 6,
                    "description": "Pipe & Drape (10ft)",
                    "duration": "3 Days",
                    "price": 45,
                    "discount": 0,
                    "subtotal": 810,
                    "category": "staging"
                },
                {
                    "id": "staging-6",
                    "quantity": 4,
                    "description": "Backdrop Stand",
                    "duration": "3 Days",
                    "price": 75,
                    "discount": 0,
                    "subtotal": 900,
                    "category": "staging"
                }
            ]
        },
        {
            "id": "labor",
            "title": "Labor & Services",
            "isExpanded": False,
            "total": 15600,
            "items": [
                {
                    "id": "labor-1",
                    "quantity": 3,
                    "description": "Audio Engineer",
                    "duration": "3 Days",
                    "price": 850,
                    "discount": 0,
                    "subtotal": 7650,
                    "category": "labor"
                },
                {
                    "id": "labor-2",
                    "quantity": 2,
                    "description": "Lighting Technician",
                    "duration": "3 Days",
                    "price": 750,
                    "discount": 0,
                    "subtotal": 4500,
                    "category": "labor"
                },
                {
                    "id": "labor-3",
                    "quantity": 2,
                    "description": "Video Technician",
                    "duration": "3 Days",
                    "price": 780,
                    "discount": 0,
                    "subtotal": 4680,
                    "category": "labor"
                },
                {
                    "id": "labor-4",
                    "quantity": 4,
                    "description": "General Labor",
                    "duration": "3 Days",
                    "price": 420,
                    "discount": 0,
                    "subtotal": 5040,
                    "category": "labor"
                }
            ]
        }
    ],
    "totalCost": 84780,
    "timeline": [
        {
            "id": "setup-day-1",
            "date": "2026-05-31",
            "startTime": "08:00",
            "endTime": "18:00",
            "title": "Load-in & Setup",
            "location": "Ryder Cup Ballroom DE",
            "setup": ["Audio rigging", "Lighting truss installation", "Video setup"],
            "equipment": ["Audio", "Lighting", "Staging"],
            "cost": 12500
        },
        {
            "id": "event-day-1",
            "date": "2026-06-01",
            "startTime": "07:00",
            "endTime": "22:00",
            "title": "Event Day 1",
            "location": "Ryder Cup Ballroom DE",
            "setup": ["Final sound check", "Lighting programming", "Video testing"],
            "equipment": ["Full production"],
            "cost": 28500
        },
        {
            "id": "event-day-2",
            "date": "2026-06-02",
            "startTime": "07:00",
            "endTime": "22:00",
            "title": "Event Day 2",
            "location": "Ryder Cup Ballroom DE",
            "setup": ["Maintenance check", "Show operation"],
            "equipment": ["Full production"],
            "cost": 25400
        },
        {
            "id": "strike",
            "date": "2026-06-03",
            "startTime": "08:00",
            "endTime": "17:00",
            "title": "Strike & Load-out",
            "location": "Ryder Cup Ballroom DE",
            "setup": ["Equipment breakdown", "Load-out"],
            "equipment": ["All equipment removal"],
            "cost": 8380
        }
    ]
}

@router.get("/proposals")
async def get_proposals(request: Request):
    """Get user's proposals"""
    user = getattr(request.state, 'user', None)
    
    return {
        "proposals": [COMPLETE_MOCK_PROPOSAL],
        "user": user,
        "total_count": 1,
        "message": "Proposals retrieved successfully"
    }

@router.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: str, request: Request):
    """Get specific proposal"""
    user = getattr(request.state, 'user', None)
    
    # Return the complete mock data
    return {
        **COMPLETE_MOCK_PROPOSAL,
        "user": user,
        "message": "Proposal retrieved successfully"
    }