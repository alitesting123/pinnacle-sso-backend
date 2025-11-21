# Testing Guide - RAG System

Complete guide to test the RAG question answering system locally and on Elastic Beanstalk.

---

## Quick Start Testing

### Option 1: Automated Test Script (Easiest)

```bash
# 1. Pull latest changes
git pull origin claude/implement-rag-questions-011KGfYVCGoZUU489EafQAVS

# 2. Run the test script (it handles everything)
./test_local.sh

# 3. In another terminal, test the API
./test_api_endpoints.sh
```

**That's it!** The scripts guide you through everything.

---

## Manual Testing Steps

### Step 1: Pull Latest Changes

```bash
cd /path/to/pinnacle-sso-backend
git pull origin claude/implement-rag-questions-011KGfYVCGoZUU489EafQAVS
```

---

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**New packages installed**:
- `anthropic` - Claude AI SDK
- `sentence-transformers` - Embedding model
- `faiss-cpu` - Vector database
- `numpy`, `tiktoken` - Supporting libraries

---

### Step 3: Run Database Migration

Add the `ai_generated` column to your existing database:

```bash
# Using your Supabase database
psql "postgresql://postgres.edygpoyhbcrkjmwvxaut:Thisiscool%402020@aws-1-us-east-2.pooler.supabase.com:6543/postgres" \
  -f migrations/add_ai_generated_field.sql
```

**Verify migration**:
```bash
psql "your-database-url" -c "\d proposal_questions"
# Should show: ai_generated | boolean | default false
```

---

### Step 4: Choose Test Mode

#### Option A: Test with RAG DISABLED (No API Key Needed)

```bash
# Set environment variables
export ENABLE_RAG_AUTO_ANSWER=false
export DATABASE_URL="postgresql://postgres.edygpoyhbcrkjmwvxaut:Thisiscool%402020@aws-1-us-east-2.pooler.supabase.com:6543/postgres"

# Start server
python -m uvicorn app.main:app --reload --port 8000
```

**Expected behavior**: All questions saved as "pending" (old behavior)

---

#### Option B: Test with RAG ENABLED (Requires API Key)

```bash
# Get API key from https://console.anthropic.com/
# Then set environment variables
export ENABLE_RAG_AUTO_ANSWER=true
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
export DATABASE_URL="postgresql://postgres.edygpoyhbcrkjmwvxaut:Thisiscool%402020@aws-1-us-east-2.pooler.supabase.com:6543/postgres"

# Start server
python -m uvicorn app.main:app --reload --port 8000
```

**Expected behavior**:
- Simple questions: Auto-answered by AI
- T&C questions: Auto-answered with AI flag
- Complex questions: Saved as pending

---

### Step 5: Test the API

Once the server is running, test in another terminal:

```bash
./test_api_endpoints.sh
```

**Or manually**:

```bash
# Test 1: Simple question (should be auto-answered if RAG enabled)
curl -X POST "http://localhost:8000/api/v1/proposals/JOB-2024-001/questions" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "",
    "item_name": "General",
    "section_name": "General",
    "question": "What is the total cost?"
  }'

# Test 2: Complex question (should be pending regardless)
curl -X POST "http://localhost:8000/api/v1/proposals/JOB-2024-001/questions" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "audio-001",
    "item_name": "Audio",
    "section_name": "Audio",
    "question": "Why did you choose this specific audio equipment?"
  }'

# Test 3: Interactive ask (doesn't save question)
curl -X POST "http://localhost:8000/api/v1/proposals/JOB-2024-001/questions/ask-ai" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "When is the event?",
    "use_rag": true
  }'
```

---

## Expected Test Results

### With RAG DISABLED (`ENABLE_RAG_AUTO_ANSWER=false`)

**Test 1: Simple Question**
```json
{
  "question": "What is the total cost?",
  "answer": null,
  "status": "pending",
  "ai_generated": false,
  "classification": {
    "category": "simple",
    "auto_answered": false,
    "rag_enabled": false
  }
}
```
✅ **Expected**: Saved as pending, no auto-answer

---

**Test 2: Complex Question**
```json
{
  "question": "Why did you choose this equipment?",
  "answer": null,
  "status": "pending",
  "ai_generated": false,
  "classification": {
    "category": "complex",
    "auto_answered": false,
    "rag_enabled": false
  }
}
```
✅ **Expected**: Saved as pending

---

### With RAG ENABLED (`ENABLE_RAG_AUTO_ANSWER=true`)

**Test 1: Simple Question**
```json
{
  "question": "What is the total cost?",
  "answer": "Based on the proposal, the total cost is...",
  "status": "answered",
  "ai_generated": true,
  "answered_by": "AI Assistant",
  "classification": {
    "category": "simple",
    "auto_answered": true,
    "rag_enabled": true
  },
  "ai_details": {
    "confidence": 0.9,
    "method": "rag"
  }
}
```
✅ **Expected**: Auto-answered by AI

---

**Test 2: Complex Question**
```json
{
  "question": "Why did you choose this equipment?",
  "answer": null,
  "status": "pending",
  "ai_generated": false,
  "classification": {
    "category": "complex",
    "auto_answered": false,
    "rag_enabled": true
  }
}
```
✅ **Expected**: Saved as pending (too complex for auto-answer)

---

**Test 3: T&C Question**
```json
{
  "question": "What is your cancellation policy?",
  "answer": "Our standard cancellation policy...",
  "status": "answered",
  "ai_generated": true,
  "classification": {
    "category": "terms_and_conditions",
    "auto_answered": true,
    "rag_enabled": true
  }
}
```
✅ **Expected**: Auto-answered with AI flag

---

## Testing on Elastic Beanstalk

### Deploy and Test

```bash
# 1. Set environment variables
eb setenv \
  ENABLE_RAG_AUTO_ANSWER=true \
  ANTHROPIC_API_KEY="sk-ant-..." \
  DATABASE_URL="postgresql://..."

# 2. Deploy
eb deploy

# 3. Check logs
eb logs --stream

# Look for:
# INFO: RAG Auto-Answering: ENABLED
# INFO: Migration completed successfully

# 4. Get EB URL
eb status | grep CNAME

# 5. Test endpoint
curl -X POST "http://YOUR-EB-URL/api/v1/proposals/JOB-001/questions" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total cost?", "item_id": "", "item_name": "General", "section_name": "General"}'
```

---

## Verification Checklist

### Before Testing
- [ ] Latest code pulled
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database migration applied
- [ ] Environment variables set
- [ ] Database accessible

### During Testing
- [ ] Server starts without errors
- [ ] See "RAG Auto-Answering: ENABLED/DISABLED" in logs
- [ ] Can create questions via API
- [ ] Questions classified correctly
- [ ] Auto-answering works as expected (if enabled)
- [ ] Complex questions saved as pending

### After Testing
- [ ] Check database for created questions
- [ ] Verify `ai_generated` flag is set correctly
- [ ] Review server logs for any errors
- [ ] Test with your frontend application

---

## Common Test Scenarios

### Scenario 1: Test Classification

Questions to try and expected categories:

| Question | Expected Category | Auto-Answered? |
|----------|-------------------|----------------|
| "What is the total cost?" | simple | Yes (if enabled) |
| "When is the event?" | simple | Yes (if enabled) |
| "What's your cancellation policy?" | terms_and_conditions | Yes (if enabled) |
| "Why did you choose this setup?" | complex | No |
| "Can you customize this package?" | complex | No |

### Scenario 2: Test Model Download (First Run)

When RAG is enabled and you ask the first question:

```bash
# Watch logs for model download
tail -f logs/app.log

# You should see:
# "Loading sentence transformer model..."
# "Downloading model all-MiniLM-L6-v2..."
# Takes ~30-60 seconds first time
# Subsequent questions are fast
```

### Scenario 3: Test Without API Key

```bash
export ENABLE_RAG_AUTO_ANSWER=true
export ANTHROPIC_API_KEY=""  # Empty

# Start server
# Expected: Warning in logs about missing API key
# Questions still saved, but not auto-answered
```

---

## Troubleshooting Tests

### Issue: Server won't start

```bash
# Check Python version
python --version
# Need 3.8+

# Check if port is in use
lsof -i :8000

# Try different port
uvicorn app.main:app --port 8001
```

### Issue: Database connection fails

```bash
# Test connection
psql "your-database-url" -c "SELECT 1;"

# Check if DATABASE_URL is set
echo $DATABASE_URL

# Verify credentials
# URL format: postgresql://user:pass@host:port/db
```

### Issue: Migration fails

```bash
# Check if column already exists
psql "$DATABASE_URL" -c "\d proposal_questions"

# If column exists, migration is already done
# If not, check permissions:
psql "$DATABASE_URL" -c "SELECT current_user, current_database();"
```

### Issue: Model won't download

```bash
# Check internet connection
ping huggingface.co

# Check disk space
df -h /tmp

# Manually download
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Issue: Questions not auto-answering (when enabled)

```bash
# Check environment variable
echo $ENABLE_RAG_AUTO_ANSWER
# Should be: true

echo $ANTHROPIC_API_KEY
# Should start with: sk-ant-

# Check server logs
grep "RAG Auto-Answering" logs/app.log
# Should say: ENABLED

# Check classification in response
# "rag_enabled": true, "auto_answered": true
```

---

## Performance Testing

### Test Response Times

```bash
# Simple question (should be ~0.5-1s after model loaded)
time curl -X POST "http://localhost:8000/api/v1/proposals/JOB-001/questions" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total cost?", ...}'

# First question (model loading): ~30-60s
# Subsequent questions: ~0.5-2s
```

### Memory Usage

```bash
# Monitor during testing
top -p $(pgrep -f uvicorn)

# Expected:
# Without RAG: ~100-200 MB
# With RAG: ~500-800 MB (model loaded)
```

---

## Next Steps After Testing

1. **If tests pass locally**:
   - Deploy to EB with `eb deploy`
   - Test on production with same scripts
   - Monitor for 24 hours

2. **If you want to disable RAG**:
   - Set `ENABLE_RAG_AUTO_ANSWER=false`
   - No other changes needed
   - See `RAG_ON_OFF_SWITCH.md`

3. **If you want to use RAG in production**:
   - Get Anthropic API key
   - Set production budget limits
   - Monitor AI answer quality
   - Review AI-generated answers periodically

---

## Test Scripts Reference

| Script | Purpose |
|--------|---------|
| `./test_local.sh` | Start local server with guided setup |
| `./test_api_endpoints.sh` | Test all API endpoints automatically |
| `test_rag_system.py` | Unit tests for RAG service |

---

## Support

- **RAG ON/OFF**: See `RAG_ON_OFF_SWITCH.md`
- **Deployment**: See `EB_DEPLOYMENT_SETUP.md`
- **Question Flow**: See `QUESTION_FLOW_DIAGRAM.md`
- **RAG Features**: See `RAG_DOCUMENTATION.md`

---

**Last Updated**: 2024-11-17
