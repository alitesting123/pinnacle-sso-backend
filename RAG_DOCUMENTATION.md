# RAG (Retrieval-Augmented Generation) System Documentation

## Overview

The Pinnacle SSO Backend includes an intelligent question answering system powered by Claude AI and Retrieval-Augmented Generation (RAG). This system automatically classifies and handles questions about proposals, providing instant AI-generated answers for simple questions while routing complex questions to human experts.

## 🎯 Automatic Question Handling Workflow

When a customer submits a question, the system automatically:

1. **Classifies the question** into one of three categories:
   - **Simple** - Factual questions (e.g., "What is the total cost?")
   - **Terms & Conditions** - Policy questions (e.g., "What is your cancellation policy?")
   - **Complex** - Questions requiring expert judgment (e.g., "Why did you choose this equipment?")

2. **Handles each type appropriately**:
   - ✅ **Simple & T&C questions** → Auto-answered immediately by AI with `ai_generated: true` flag
   - 📝 **Complex questions** → Saved as `pending` for human review (NOT auto-answered)

3. **Marks AI responses** with the `ai_generated` flag so you can identify them

### Question Categories Explained

#### ✅ Auto-Answered (Simple Questions)
- "What is the total cost?"
- "When is the event?"
- "Where is the venue?"
- "Who is the salesperson?"
- "How many microphones are included?"
- "What time does setup start?"

#### ✅ Auto-Answered (Terms & Conditions)
- "What is your cancellation policy?"
- "What are the payment terms?"
- "What if equipment gets damaged?"
- "Do you require a deposit?"
- "What about insurance and liability?"
- "What are your refund terms?"

#### 📝 Saved for Human Review (Complex Questions)
- "Why did you choose this specific audio setup?"
- "Can you explain how the lighting will work?"
- "Can we customize this package?"
- "What if we need to make changes?"
- "How does this compare to other options?"
- "Can you recommend a better solution?"

## Features

### 1. **Intelligent Question Classification**
- Automatically determines question complexity
- Detects terms & conditions questions
- Routes simple/T&C to AI, complex to humans
- All classification decisions logged for review

### 2. **Semantic Search (RAG)**
- Proposal content is automatically indexed using vector embeddings
- Questions are matched against proposal content using semantic similarity
- Retrieves the most relevant context for answering
- Uses FAISS for fast vector search

### 3. **AI Answer Flagging**
- All AI-generated answers marked with `ai_generated: true`
- Easy to identify which answers came from AI vs. humans
- Transparency for customers and internal teams
- Can filter/report on AI vs. human answers

### 4. **Multiple Answer Modes**
- **Automatic Classification** (default) - System decides based on question type
- **Manual AI Answer** - Generate AI suggestions for any question
- **Interactive Ask** - Get instant answers without saving

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `anthropic==0.39.0` - Claude AI SDK
- `sentence-transformers==2.2.2` - For generating embeddings
- `faiss-cpu==1.7.4` - Vector database for semantic search
- `numpy==1.24.3` - Numerical operations
- `tiktoken==0.5.2` - Token counting

### 2. Configure API Key

Get your Anthropic API key from [https://console.anthropic.com/](https://console.anthropic.com/)

Add to your environment:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or add to `.env` file:

```
ANTHROPIC_API_KEY=your-api-key-here
```

## API Endpoints

### 1. AI Answer for Existing Question

**Endpoint**: `POST /api/v1/questions/{question_id}/ai-answer`

Generate an AI-powered answer for a question that's already in the database.

**Request Body**:
```json
{
  "use_rag": true,      // Optional, default: true
  "auto_save": false    // Optional, default: false
}
```

**Response**:
```json
{
  "question_id": "uuid",
  "question": "What is the total cost for audio equipment?",
  "ai_answer": "Based on the proposal, the total cost for audio equipment...",
  "method": "rag",           // "simple" or "rag"
  "confidence": 0.9,
  "sources": [
    {
      "section": "Audio",
      "type": "section",
      "relevance": 0.123
    }
  ],
  "reasoning": "Used RAG for comprehensive answer",
  "auto_saved": false,
  "current_status": "pending",
  "answered_by": null,
  "answered_at": null
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/questions/abc123/ai-answer" \
  -H "Content-Type: application/json" \
  -d '{
    "use_rag": true,
    "auto_save": true
  }'
```

### 2. Ask AI About Proposal (Without Saving)

**Endpoint**: `POST /api/v1/proposals/{proposal_id}/questions/ask-ai`

Ask a question about a proposal and get an immediate answer without creating a question record. Perfect for interactive Q&A.

**Request Body**:
```json
{
  "question": "What is included in the lighting package?",
  "use_rag": true      // Optional, default: true
}
```

**Response**:
```json
{
  "proposal_id": "uuid",
  "job_number": "JOB-2024-001",
  "question": "What is included in the lighting package?",
  "answer": "The lighting package includes...",
  "method": "rag",
  "confidence": 0.9,
  "sources": [
    {
      "section": "Lighting",
      "type": "section",
      "relevance": 0.089
    }
  ],
  "reasoning": "Used RAG for comprehensive answer"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/proposals/JOB-2024-001/questions/ask-ai" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the event date and location?",
    "use_rag": false
  }'
```

### 3. Clear RAG Cache

**Endpoint**: `DELETE /api/v1/proposals/{proposal_id}/rag-cache`

Clear the vector store cache for a proposal. Use this when a proposal has been updated and you want to reindex the content.

**Response**:
```json
{
  "message": "RAG cache cleared for proposal JOB-2024-001",
  "proposal_id": "uuid",
  "job_number": "JOB-2024-001"
}
```

**Example**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/proposals/JOB-2024-001/rag-cache"
```

## How It Works

### 1. Question Classification

The system analyzes each question to determine complexity:

**Simple Questions** (answered directly):
- "What is the total cost?"
- "When is the event?"
- "Where is the venue?"
- "Who is the salesperson?"

**Complex Questions** (use RAG):
- "Explain the audio setup for the event"
- "Compare the lighting options"
- "Why is the labor cost calculated this way?"
- "What equipment is needed for setup?"

### 2. Content Extraction

For RAG mode, the system extracts and indexes:

- **Proposal Overview**: Client info, dates, locations, pricing
- **Sections**: Audio, Video, Lighting, etc.
- **Line Items**: Individual equipment with descriptions and pricing
- **Timeline**: Event schedule and setup tasks
- **Labor**: Labor breakdown and costs

### 3. Vector Search

- Proposal content is converted to 384-dimensional embeddings
- Questions are embedded using the same model
- FAISS performs fast semantic similarity search
- Top 5 most relevant chunks are retrieved

### 4. Answer Generation

The retrieved context is sent to Claude AI with the question:

```
You are an expert assistant helping answer questions about a proposal/quote.

Question: {question}

Relevant context from the proposal:
[Context chunks...]

Please provide a clear, accurate, and helpful answer based on the context provided.
```

## Use Cases

### 1. Customer Self-Service Portal
Allow clients to ask questions about their proposals and get instant answers:

```javascript
// Frontend example
async function askQuestion(proposalId, question) {
  const response = await fetch(
    `/api/v1/proposals/${proposalId}/questions/ask-ai`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    }
  );
  return await response.json();
}
```

### 2. Support Team Assistant
Help support teams quickly answer customer questions:

```javascript
// Get AI-suggested answer, review it, then save
async function getSuggestedAnswer(questionId) {
  const response = await fetch(
    `/api/v1/questions/${questionId}/ai-answer`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        use_rag: true,
        auto_save: false  // Review before saving
      })
    }
  );
  return await response.json();
}
```

### 3. Automated Q&A
Automatically answer simple questions and flag complex ones for human review:

```python
# Backend workflow
async def handle_new_question(question_id: str):
    rag_service = get_rag_service()
    result = await rag_service.answer_question(...)

    if result['confidence'] > 0.8 and result['method'] == 'rag':
        # Auto-answer
        save_answer(question_id, result['answer'])
    else:
        # Flag for human review
        notify_support_team(question_id)
```

## Performance Considerations

### Caching
- Vector stores are cached in memory per proposal
- First question for a proposal: ~2-3 seconds (indexing)
- Subsequent questions: ~500ms-1s (retrieval + AI)

### Memory Usage
- Each proposal: ~5-10MB (embeddings + FAISS index)
- Consider clearing cache for inactive proposals

### API Costs
- Claude API: ~$0.003 per question (Sonnet 4.5)
- Batch operations recommended for cost optimization

## Troubleshooting

### "AI service is not configured"
- Ensure `ANTHROPIC_API_KEY` is set in environment
- Check API key is valid at console.anthropic.com

### "Embedder or FAISS not available"
- Run: `pip install sentence-transformers faiss-cpu`
- Restart the application

### Slow First Response
- Normal behavior - first question indexes the proposal
- Subsequent questions are fast (cached)

### Inaccurate Answers
- Try using `use_rag: true` for better context
- Check if proposal content is complete
- Clear cache if proposal was recently updated

## Configuration Options

### RAG Service Parameters

You can customize the RAG service by modifying `/app/services/rag_service.py`:

```python
# Number of context chunks to retrieve
context_chunks = self.retrieve_relevant_context(
    proposal_id,
    question,
    top_k=5  # Adjust this (default: 5)
)

# Claude model configuration
message = self.client.messages.create(
    model="claude-3-5-sonnet-20241022",  # Change model
    max_tokens=1024,  # Adjust response length
    messages=[...]
)
```

## Security Considerations

1. **Rate Limiting**: Implement rate limits on AI endpoints to prevent abuse
2. **Authentication**: Ensure only authorized users can ask questions
3. **Data Privacy**: Proposal data is sent to Anthropic (check their privacy policy)
4. **API Key Security**: Never commit API keys to version control

## Future Enhancements

Potential improvements to consider:

- [ ] Multi-proposal knowledge base (answer from multiple proposals)
- [ ] Question templates and suggestions
- [ ] Answer quality scoring and feedback
- [ ] Conversation history for follow-up questions
- [ ] Custom prompt templates per proposal type
- [ ] Integration with email notifications
- [ ] Analytics dashboard for Q&A metrics

## Support

For issues or questions:
1. Check application logs for error details
2. Verify API key configuration
3. Test with simple questions first
4. Review Anthropic API status: https://status.anthropic.com/

## Example Workflow

```python
# Complete workflow example
from app.services.rag_service import get_rag_service
from app.database import get_db
from app.models.proposals import Proposal

# 1. Get RAG service
rag = get_rag_service()

# 2. Get proposal
db = next(get_db())
proposal = db.query(Proposal).filter_by(job_number="JOB-2024-001").first()

# 3. Ask question
result = await rag.answer_question(
    question="What is the total cost and when is the event?",
    proposal=proposal,
    db=db,
    use_rag=True
)

# 4. Use result
print(f"Answer: {result['answer']}")
print(f"Method: {result['method']}")
print(f"Confidence: {result['confidence']}")
print(f"Sources: {result['sources']}")
```

---

**Version**: 1.0
**Last Updated**: 2024-11-17
**Maintainer**: Pinnacle Live Development Team
