# RAG Auto-Answering ON/OFF Switch

## Quick Answer

**To turn OFF auto-answering (go back to old behavior)**:

```bash
# Local development
export ENABLE_RAG_AUTO_ANSWER=false

# Elastic Beanstalk
eb setenv ENABLE_RAG_AUTO_ANSWER=false
```

**To turn ON auto-answering** (default):

```bash
# Local development
export ENABLE_RAG_AUTO_ANSWER=true

# Elastic Beanstalk
eb setenv ENABLE_RAG_AUTO_ANSWER=true
```

---

## What is Anthropic API Key?

**Anthropic** = The company that makes **Claude AI**

- **What**: API key to use Claude AI for answering questions
- **Where to get**: https://console.anthropic.com/
- **Cost**: ~$0.003 per question (~$3 per 1000 questions)
- **Format**: `sk-ant-api03-xxxxxxxxxxxxx...`

**If you don't have/want to pay for the API key**, just disable auto-answering (see below).

---

## Behavior Comparison

### With Auto-Answering ENABLED (New Behavior)

**Environment Variable**: `ENABLE_RAG_AUTO_ANSWER=true` (default)

| Question Type | What Happens |
|---------------|--------------|
| **Simple**: "What is the cost?" | ✅ Auto-answered by AI immediately |
| **Terms**: "What's your cancellation policy?" | ✅ Auto-answered by AI with flag |
| **Complex**: "Why this audio setup?" | 📝 Saved as pending (human review) |

**Requirements**:
- ✅ Anthropic API Key needed
- ✅ Costs ~$0.003 per auto-answered question
- ✅ Faster response for customers (instant answers)

---

### With Auto-Answering DISABLED (Old Behavior)

**Environment Variable**: `ENABLE_RAG_AUTO_ANSWER=false`

| Question Type | What Happens |
|---------------|--------------|
| **All questions** | 📝 Saved as pending (human answers all) |

**Requirements**:
- ❌ No API key needed
- ❌ No AI costs
- ✅ All questions answered by humans
- ✅ Works exactly like before RAG was added

---

## How to Switch

### For Local Development

```bash
# In your terminal
export ENABLE_RAG_AUTO_ANSWER=false

# Or add to your .env file
echo "ENABLE_RAG_AUTO_ANSWER=false" >> .env

# Start your app
python -m uvicorn app.main:app --reload
```

### For Elastic Beanstalk Deployment

#### Option 1: Via EB CLI (Recommended)

```bash
# Turn OFF auto-answering
eb setenv ENABLE_RAG_AUTO_ANSWER=false

# Restart to apply changes
eb deploy
```

#### Option 2: Via AWS Console

1. Go to **Elastic Beanstalk Console**
2. Select your environment
3. **Configuration** → **Software** → **Environment properties**
4. Add/Edit:
   - **Name**: `ENABLE_RAG_AUTO_ANSWER`
   - **Value**: `false` (or `true` to enable)
5. Click **Apply**

#### Option 3: Via .ebextensions Config

Add to `.ebextensions/01_python.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    ENABLE_RAG_AUTO_ANSWER: "false"
```

Then deploy:
```bash
git add .ebextensions/01_python.config
git commit -m "Disable RAG auto-answering"
eb deploy
```

---

## Configuration Options

The environment variable accepts these values:

| Value | Auto-Answering |
|-------|----------------|
| `true`, `1`, `yes` | ✅ ENABLED |
| `false`, `0`, `no` | ❌ DISABLED |
| Not set (default) | ✅ ENABLED |

**Examples**:
```bash
ENABLE_RAG_AUTO_ANSWER=true    # Enabled
ENABLE_RAG_AUTO_ANSWER=false   # Disabled
ENABLE_RAG_AUTO_ANSWER=1       # Enabled
ENABLE_RAG_AUTO_ANSWER=0       # Disabled
ENABLE_RAG_AUTO_ANSWER=yes     # Enabled
ENABLE_RAG_AUTO_ANSWER=no      # Disabled
# Not set at all             # Enabled (default)
```

---

## Verification

### Check Current Setting

```bash
# Local
echo $ENABLE_RAG_AUTO_ANSWER

# Elastic Beanstalk
eb printenv | grep ENABLE_RAG_AUTO_ANSWER
```

### Check Application Logs

When the app starts, it logs the setting:

```bash
# View logs
eb logs --stream

# Look for this line:
# INFO: RAG Auto-Answering: ENABLED
# or
# INFO: RAG Auto-Answering: DISABLED
```

### Test Behavior

```bash
# Create a simple question
curl -X POST "http://your-api-url/api/v1/proposals/JOB-001/questions" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the total cost?",
    "item_id": "",
    "item_name": "General",
    "section_name": "General"
  }'

# If ENABLED: Response includes "status": "answered", "ai_generated": true
# If DISABLED: Response includes "status": "pending", "answer": null
```

---

## Response Format Changes

The API response includes information about RAG status:

### With RAG Enabled
```json
{
  "question": "What is the total cost?",
  "answer": "The total cost is $19,635.00...",
  "status": "answered",
  "ai_generated": true,
  "classification": {
    "category": "simple",
    "reasoning": "Short factual question",
    "auto_answered": true,
    "rag_enabled": true    ← Shows RAG is on
  }
}
```

### With RAG Disabled
```json
{
  "question": "What is the total cost?",
  "answer": null,
  "status": "pending",
  "ai_generated": false,
  "classification": {
    "category": "simple",
    "reasoning": "Short factual question",
    "auto_answered": false,  ← Not auto-answered
    "rag_enabled": false     ← Shows RAG is off
  }
}
```

---

## When to Use Each Mode

### Use Auto-Answering ENABLED when:
- ✅ You have Anthropic API key
- ✅ You want instant answers for simple questions
- ✅ You want to reduce support team workload
- ✅ You're okay with ~$3-30/month in AI costs
- ✅ You'll review AI answers (they're flagged)

### Use Auto-Answering DISABLED when:
- ✅ You don't have/want Anthropic API key
- ✅ You want humans to answer ALL questions
- ✅ You want zero AI costs
- ✅ You prefer the old behavior
- ✅ You're testing/developing without AI

---

## Migration Path

If you want to gradually adopt RAG:

### Phase 1: Testing (Disabled)
```bash
ENABLE_RAG_AUTO_ANSWER=false
```
- Test the new code without auto-answering
- Verify everything works
- No API costs

### Phase 2: Manual AI Suggestions (Disabled, but use manual endpoint)
```bash
ENABLE_RAG_AUTO_ANSWER=false
# But use POST /questions/{id}/ai-answer manually
```
- Questions saved as pending
- Support team can request AI suggestions
- Review before sending to customers

### Phase 3: Full Auto-Answering (Enabled)
```bash
ENABLE_RAG_AUTO_ANSWER=true
ANTHROPIC_API_KEY=sk-ant-...
```
- Simple questions auto-answered
- Complex questions still need humans
- Monitor quality and costs

---

## Cost Control

Even with RAG enabled, you can control costs:

### 1. Disable Auto-Answering (This Guide)
```bash
ENABLE_RAG_AUTO_ANSWER=false
```
**Result**: $0 AI costs

### 2. Enable but Monitor
```bash
ENABLE_RAG_AUTO_ANSWER=true
```
**Result**:
- Only simple/T&C questions auto-answered
- Complex questions still need humans
- Can track costs via Anthropic dashboard

### 3. Set API Budget Limits
- Go to https://console.anthropic.com/
- Settings → Billing → Set monthly budget
- Get alerts when approaching limit

---

## FAQ

**Q: If I disable RAG, can I still use the manual AI answer endpoint?**
A: Yes! The `/questions/{id}/ai-answer` endpoint works regardless of this setting. You can manually trigger AI answers even with auto-answering disabled.

**Q: Do I need to deploy after changing the environment variable?**
A: No! Just run `eb setenv` and the app will pick it up on next restart. Or run `eb deploy` to restart immediately.

**Q: Will this break anything if I disable it?**
A: No! Your app works exactly like before RAG was added. All questions are just saved as pending.

**Q: Can I enable it later without re-deploying?**
A: Yes! Just set the environment variable and restart the app.

**Q: What if I don't set this variable at all?**
A: It defaults to `true` (ENABLED). To disable, you must explicitly set it to `false`.

---

## Summary

| Want | Command |
|------|---------|
| **Go back to old behavior** | `eb setenv ENABLE_RAG_AUTO_ANSWER=false` |
| **Use new AI auto-answering** | `eb setenv ENABLE_RAG_AUTO_ANSWER=true` |
| **Check current setting** | `eb printenv \| grep ENABLE_RAG_AUTO_ANSWER` |
| **No Anthropic key? No problem!** | Just disable it with `false` |

---

**Last Updated**: 2024-11-17
