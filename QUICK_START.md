# Quick Start - RAG Deployment

## 🎯 Your Setup Summary

- **Database**: Supabase PostgreSQL ✅ (already configured)
- **Just Add**: `ai_generated` column (migration runs automatically)
- **Model**: Downloads automatically (~80MB, first startup only)
- **New Requirement**: Anthropic API key

---

## ⚡ Fast Track Deployment (3 Commands)

```bash
# 1. Get API key from https://console.anthropic.com/
# Copy your key (starts with sk-ant-api03-...)

# 2. Run automated deployment
./DEPLOY_COMMANDS.sh

# 3. Verify
eb health && eb logs --stream
```

**That's it!** The script handles everything automatically.

---

## 📋 What Happens Automatically

When you deploy:

1. ✅ **Installs dependencies** from requirements.txt
2. ✅ **Adds `ai_generated` column** to your existing `proposal_questions` table
3. ✅ **Downloads AI model** (all-MiniLM-L6-v2, ~80MB)
4. ✅ **Configures timeouts** for RAG operations
5. ✅ **Starts application** with RAG enabled

**No new database needed!** Uses your existing Supabase database.

---

## 🔑 Only 1 Thing You Need

**Anthropic API Key**:
1. Go to: https://console.anthropic.com/
2. Sign up/Login
3. Create API key
4. Copy key (starts with `sk-ant-api03-...`)

**Cost**: ~$0.003 per question answered by AI

---

## 🚀 Manual Deployment (If You Prefer)

```bash
# 1. Initialize EB
eb init pinnacle-sso-backend --region us-east-2 --platform python-3.11

# 2. Create environment
eb create pinnacle-sso-production --instance-type t3.medium

# 3. Set environment variables (replace YOUR-KEY)
eb setenv \
  DATABASE_URL="postgresql://postgres.edygpoyhbcrkjmwvxaut:Thisiscool%402020@aws-1-us-east-2.pooler.supabase.com:6543/postgres" \
  ANTHROPIC_API_KEY="YOUR-KEY-HERE" \
  FRONTEND_BASE_URL="https://main.dnfe4l5bsjojn.amplifyapp.com" \
  ALLOWED_ORIGINS="https://main.dnfe4l5bsjojn.amplifyapp.com,https://dlndpgwc2naup.cloudfront.net" \
  SECRET_KEY="your-super-secret-key-change-this" \
  ENVIRONMENT="production" \
  DEBUG="False" \
  LOG_LEVEL="INFO"

# 4. Deploy
git add .ebextensions migrations
git commit -m "Add RAG deployment configuration"
eb deploy
```

---

## ✅ Verify Deployment

```bash
# Check health
eb health
# Should show: Green / Ok

# View logs
eb logs --stream
# Look for: "Migration completed successfully"

# Get your URL
eb status | grep CNAME
# Returns: your-app.us-east-2.elasticbeanstalk.com
```

---

## 🧪 Test RAG

```bash
# Replace YOUR-EB-URL with your actual EB URL
curl -X POST "http://YOUR-EB-URL/api/v1/proposals/JOB-001/questions" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the total cost?",
    "item_id": "",
    "item_name": "General",
    "section_name": "General"
  }'

# Expected response:
# {
#   "question": "What is the total cost?",
#   "answer": "The total cost is $19,635.00...",
#   "status": "answered",
#   "ai_generated": true,
#   "classification": {
#     "category": "simple",
#     "auto_answered": true
#   }
# }
```

---

## 📊 How Questions Are Handled

| Question Type | Example | Behavior |
|---------------|---------|----------|
| **Simple** | "What is the cost?" | ✅ Auto-answered by AI |
| **Terms & Conditions** | "What's your cancellation policy?" | ✅ Auto-answered with AI flag |
| **Complex** | "Why this audio setup?" | 📝 Saved for human review |

All AI answers marked with `"ai_generated": true`

---

## 💰 Costs

**Infrastructure** (~$56/month):
- t3.medium instance: $30
- Load balancer: $16
- Data transfer: $5
- Other: $5

**AI Usage** (pay-per-use):
- 1,000 questions: ~$3
- 10,000 questions: ~$30

**Your existing** (unchanged):
- Supabase: Your current plan
- Amplify: Your current plan
- CloudFront: Your current plan

---

## 🆘 Troubleshooting

### Migration didn't run?
```bash
eb ssh
psql "$DATABASE_URL" -f /var/app/current/migrations/add_ai_generated_field.sql
exit
```

### Model won't download?
```bash
# Check logs
eb logs --stream | grep -i "model"

# Increase instance memory if needed
eb config
# Change InstanceType to t3.large
```

### Getting CORS errors?
```bash
# Add your CloudFront URL
eb setenv ALLOWED_ORIGINS="https://main.dnfe4l5bsjojn.amplifyapp.com,https://dlndpgwc2naup.cloudfront.net"
```

---

## 📚 Full Documentation

- **Complete guide**: `EB_DEPLOYMENT_SETUP.md`
- **RAG features**: `RAG_DOCUMENTATION.md`
- **Question flow**: `QUESTION_FLOW_DIAGRAM.md`
- **General EB guide**: `ELASTIC_BEANSTALK_DEPLOYMENT.md`

---

## 🎯 TL;DR

1. Get Anthropic API key: https://console.anthropic.com/
2. Run: `./DEPLOY_COMMANDS.sh`
3. Test: `eb health`
4. Done! ✅

Questions? Check the docs above or run `eb logs --stream` to debug.
