# Question Handling Flow Diagram

## Overview

This document explains the complete workflow for how questions are handled in the Pinnacle SSO Backend with RAG integration.

---

## Complete Question Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Customer Submits Question                     │
│              POST /api/v1/proposals/{id}/questions               │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  RAG Service: Classify Question                  │
│                classify_question(question_text)                  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
     ┌──────────────────────┐    ┌──────────────────────┐
     │  Simple Question?    │    │  T&C Question?       │
     │  - What is cost?     │    │  - Cancellation?     │
     │  - When is event?    │    │  - Payment terms?    │
     │  - Where is venue?   │    │  - Refund policy?    │
     └──────────┬───────────┘    └──────────┬───────────┘
                │                           │
                └──────────┬────────────────┘
                           │
                           │ should_auto_answer: TRUE
                           │ ai_flag: TRUE
                           ▼
           ┌────────────────────────────────┐
           │    Create Question Record      │
           │    status: 'pending'           │
           │    ai_generated: false         │
           └────────────┬───────────────────┘
                        │
                        ▼
           ┌────────────────────────────────┐
           │   Generate AI Answer (RAG)     │
           │   1. Extract proposal content  │
           │   2. Semantic search           │
           │   3. Call Claude AI            │
           └────────────┬───────────────────┘
                        │
                        ▼
           ┌────────────────────────────────┐
           │    Update Question Record      │
           │    status: 'answered'          │
           │    answer_text: AI answer      │
           │    ai_generated: TRUE          │
           │    answered_by: 'AI Assistant' │
           └────────────┬───────────────────┘
                        │
                        ▼
           ┌────────────────────────────────┐
           │   Return Response with:        │
           │   - Question & answer          │
           │   - ai_generated: true         │
           │   - classification details     │
           │   - confidence score           │
           └────────────────────────────────┘


                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
     ┌──────────────────────┐    ┌──────────────────────┐
     │  Complex Question?   │    │  Default/Unknown     │
     │  - Why this setup?   │    │  - Multi-part Q's    │
     │  - Can you explain?  │    │  - Customization     │
     │  - Can we modify?    │    │  - Comparisons       │
     └──────────┬───────────┘    └──────────┬───────────┘
                │                           │
                └──────────┬────────────────┘
                           │
                           │ should_auto_answer: FALSE
                           │ ai_flag: FALSE
                           ▼
           ┌────────────────────────────────┐
           │    Create Question Record      │
           │    status: 'pending'           │
           │    ai_generated: false         │
           │    answer_text: NULL           │
           └────────────┬───────────────────┘
                        │
                        │ STOP - No auto-answer
                        │
                        ▼
           ┌────────────────────────────────┐
           │   Return Response with:        │
           │   - Question (no answer)       │
           │   - status: 'pending'          │
           │   - classification details     │
           │   - Awaits human review        │
           └────────────┬───────────────────┘
                        │
                        ▼
           ┌────────────────────────────────┐
           │  Support Team Reviews          │
           │  - Receives notification       │
           │  - Reviews question            │
           │  - Provides expert answer      │
           │  POST /questions/{id}/answer   │
           └────────────────────────────────┘
```

---

## Response Examples

### Example 1: Simple Question (Auto-Answered)

**Request:**
```json
POST /api/v1/proposals/JOB-2024-001/questions
{
  "item_id": "item-001",
  "item_name": "Audio Equipment",
  "section_name": "Audio",
  "question": "What is the total cost?"
}
```

**Response:**
```json
{
  "id": "abc-123-def-456",
  "itemId": "item-001",
  "itemName": "Audio Equipment",
  "sectionName": "Audio",
  "question": "What is the total cost?",
  "answer": "The total cost for this proposal is $19,635.00. This includes...",
  "status": "answered",
  "askedBy": "John Doe",
  "askedAt": "2024-11-17T10:30:00Z",
  "answeredBy": "AI Assistant",
  "answeredAt": "2024-11-17T10:30:01Z",
  "ai_generated": true,
  "classification": {
    "category": "simple",
    "reasoning": "Short factual question - can be answered directly",
    "auto_answered": true
  },
  "ai_details": {
    "ai_answer": "The total cost for this proposal is $19,635.00...",
    "confidence": 0.9,
    "method": "rag",
    "sources": [
      {"section": "Pricing", "type": "pricing", "relevance": 0.05}
    ]
  }
}
```

---

### Example 2: Terms & Conditions Question (Auto-Answered with Flag)

**Request:**
```json
POST /api/v1/proposals/JOB-2024-001/questions
{
  "item_id": "",
  "item_name": "General",
  "section_name": "General",
  "question": "What is your cancellation policy?"
}
```

**Response:**
```json
{
  "id": "xyz-789-abc-012",
  "question": "What is your cancellation policy?",
  "answer": "Our standard cancellation policy requires 30 days notice...",
  "status": "answered",
  "ai_generated": true,
  "classification": {
    "category": "terms_and_conditions",
    "reasoning": "Terms and conditions question - AI can provide standard answer",
    "auto_answered": true
  }
}
```

**Note:** The `ai_generated: true` flag indicates this is an AI response that should be reviewed.

---

### Example 3: Complex Question (Saved for Human Review)

**Request:**
```json
POST /api/v1/proposals/JOB-2024-001/questions
{
  "item_id": "item-audio-001",
  "item_name": "Audio System",
  "section_name": "Audio",
  "question": "Why did you choose the QSC speakers over the Meyer Sound system? Can we get a comparison?"
}
```

**Response:**
```json
{
  "id": "complex-123-456",
  "question": "Why did you choose the QSC speakers over the Meyer Sound system? Can we get a comparison?",
  "answer": null,
  "status": "pending",
  "ai_generated": false,
  "answeredBy": null,
  "answeredAt": null,
  "classification": {
    "category": "complex",
    "reasoning": "Multi-part question requiring comprehensive human answer",
    "auto_answered": false
  }
}
```

**What happens next:**
1. Support team receives notification
2. Expert reviews the question
3. Human provides detailed answer via `POST /questions/{id}/answer`
4. Status changes to "answered" with `ai_generated: false`

---

## Database Schema

```sql
CREATE TABLE proposal_questions (
    id UUID PRIMARY KEY,
    proposal_id UUID NOT NULL,
    line_item_id UUID,

    question_text TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'normal',

    asked_by_name VARCHAR(255),
    asked_by_email VARCHAR(255),
    asked_at TIMESTAMP DEFAULT NOW(),

    answer_text TEXT,
    answered_by VARCHAR(255),
    answered_at TIMESTAMP,
    ai_generated BOOLEAN DEFAULT FALSE,  -- 🆕 AI flag

    internal_notes TEXT,
    requires_follow_up BOOLEAN DEFAULT FALSE
);
```

---

## Classification Logic

```python
async def classify_question(question: str) -> dict:
    """
    Returns:
    {
        'category': 'simple' | 'complex' | 'terms_and_conditions',
        'should_auto_answer': bool,
        'use_ai': bool,
        'ai_flag': bool,
        'reasoning': str
    }
    """

    # 1. Check for T&C keywords
    if any(keyword in question.lower() for keyword in [
        'terms', 'conditions', 'cancellation', 'refund',
        'payment terms', 'deposit', 'liability', 'policy'
    ]):
        return {
            'category': 'terms_and_conditions',
            'should_auto_answer': True,
            'use_ai': True,
            'ai_flag': True
        }

    # 2. Check for simple factual questions
    if any(keyword in question.lower() for keyword in [
        'what is', 'when is', 'where is', 'how much',
        'what time', 'how many'
    ]):
        return {
            'category': 'simple',
            'should_auto_answer': True,
            'use_ai': True,
            'ai_flag': True
        }

    # 3. Check for complex indicators
    if any(keyword in question.lower() for keyword in [
        'explain', 'why', 'compare', 'customize',
        'can you change', 'recommend'
    ]):
        return {
            'category': 'complex',
            'should_auto_answer': False,
            'use_ai': False,
            'ai_flag': False
        }

    # 4. Default to complex (safety first)
    return {
        'category': 'complex',
        'should_auto_answer': False,
        'use_ai': False,
        'ai_flag': False
    }
```

---

## Integration Points

### Frontend Integration

```javascript
// When creating a question
const response = await createQuestion(proposalId, {
  item_id: itemId,
  item_name: itemName,
  section_name: sectionName,
  question: questionText
});

// Check if it was auto-answered
if (response.status === 'answered' && response.ai_generated) {
  // Show AI answer with indicator
  showAIAnswer(response.answer, response.ai_details);
} else if (response.status === 'pending') {
  // Show "waiting for expert response" message
  showPendingMessage();
}
```

### Backend Monitoring

```python
# Query all AI-generated answers for review
ai_answers = db.query(ProposalQuestion).filter(
    ProposalQuestion.ai_generated == True,
    ProposalQuestion.status == 'answered'
).all()

# Query complex questions awaiting human review
pending_complex = db.query(ProposalQuestion).filter(
    ProposalQuestion.status == 'pending',
    ProposalQuestion.ai_generated == False
).all()
```

---

## Benefits of This Approach

1. **Fast Response for Simple Questions** - Customers get instant answers
2. **Quality Control for Complex Questions** - Experts handle important questions
3. **Transparency** - `ai_generated` flag shows which answers came from AI
4. **Scalability** - AI handles volume, humans handle complexity
5. **Learning Opportunity** - Track which questions AI can/cannot handle
6. **Cost Effective** - Reduce support team workload while maintaining quality

---

**Version**: 1.0
**Last Updated**: 2024-11-17
