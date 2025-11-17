# Elastic Beanstalk Deployment Setup for RAG System

## Your Current Configuration

Based on your environment variables, here's your setup:

- **Database**: Supabase PostgreSQL (aws-1-us-east-2.pooler.supabase.com)
- **Frontend**: AWS Amplify (main.dnfe4l5bsjojn.amplifyapp.com)
- **API Distribution**: CloudFront (dlndpgwc2naup.cloudfront.net)
- **AWS Region**: us-east-2 (Ohio)

---

## Step-by-Step Deployment

### Prerequisites

1. **Install EB CLI** (if not already installed):
```bash
pip install awsebcli --upgrade
```

2. **Get Anthropic API Key**:
   - Go to: https://console.anthropic.com/
   - Sign up/Login
   - Navigate to API Keys
   - Create new key (starts with `sk-ant-api03-...`)

---

## Step 1: Initialize Elastic Beanstalk

```bash
cd /path/to/pinnacle-sso-backend

# Initialize EB application
eb init

# When prompted:
# Region: us-east-2 (to match your AWS setup)
# Application name: pinnacle-sso-backend
# Platform: Python 3.11
# CodeCommit: No
# SSH: Yes (recommended)
```

---

## Step 2: Create Environment

```bash
# Create production environment
eb create pinnacle-sso-production

# Options:
# - DNS CNAME: pinnacle-sso-api (or your preference)
# - Load balancer: Application Load Balancer
```

---

## Step 3: Set Environment Variables

**CRITICAL**: Set these environment variables in EB:

```bash
eb setenv \
  DATABASE_URL="postgresql://postgres.edygpoyhbcrkjmwvxaut:Thisiscool%402020@aws-1-us-east-2.pooler.supabase.com:6543/postgres" \
  ANTHROPIC_API_KEY="sk-ant-api03-YOUR-KEY-HERE" \
  FRONTEND_BASE_URL="https://main.dnfe4l5bsjojn.amplifyapp.com" \
  ALLOWED_ORIGINS="https://main.dnfe4l5bsjojn.amplifyapp.com,https://*.dnfe4l5bsjojn.amplifyapp.com,http://localhost:3000" \
  SECRET_KEY="your-super-secret-key-change-this-in-production-minimum-32-chars" \
  ENVIRONMENT="production" \
  DEBUG="False" \
  AWS_REGION="us-east-2" \
  LOG_LEVEL="INFO" \
  RATE_LIMIT_ENABLED="True"
```

**Important Notes**:
- Replace `YOUR-KEY-HERE` with your actual Anthropic API key
- The `%40` in DATABASE_URL is URL-encoded `@` - keep it as is
- No need for Redis URL - RAG uses in-memory cache

---

## Step 4: Configure Instance Type

RAG needs at least 4GB RAM. Set instance type to t3.medium:

```bash
eb config

# In the editor, find and change:
# aws:autoscaling:launchconfiguration:
#   InstanceType: t3.medium

# Save and exit
```

---

## Step 5: Deploy Application

```bash
# First deployment
git add .ebextensions
git commit -m "Add EB configuration for RAG deployment"
git push

eb deploy
```

**What happens during deployment**:
1. ✅ Installs Python dependencies (including RAG models)
2. ✅ Runs database migration (adds `ai_generated` column)
3. ✅ Downloads sentence transformer model (~80MB)
4. ✅ Starts application

**First deployment takes**: ~5-10 minutes

---

## Step 6: Verify Deployment

### 6.1 Check Health
```bash
eb health
```

Should show: **Green** or **Ok**

### 6.2 Check Logs
```bash
# Stream logs
eb logs --stream

# Look for:
# - "Migration completed successfully"
# - "Loading sentence transformer model"
# - "Application started"
```

### 6.3 Test Database Migration
```bash
# SSH into instance
eb ssh

# Check if column was added
psql "$DATABASE_URL" -c "\d proposal_questions"

# Should show:
# ai_generated | boolean | default false

# Exit SSH
exit
```

### 6.4 Test RAG Endpoint
```bash
# Get your EB URL
eb status

# Test question creation (replace YOUR-EB-URL)
curl -X POST "http://YOUR-EB-URL.elasticbeanstalk.com/api/v1/proposals/JOB-001/questions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "question": "What is the total cost?",
    "item_id": "",
    "item_name": "General",
    "section_name": "General"
  }'

# Should return JSON with:
# - "status": "answered" (if simple question)
# - "ai_generated": true
# - "classification": { "category": "simple", ... }
```

---

## Step 7: Configure CloudFront (Update Your Existing Distribution)

Since you already have CloudFront (`dlndpgwc2naup.cloudfront.net`), you need to:

### Option A: Update Existing CloudFront Origin

1. Go to **CloudFront Console**
2. Select your distribution (dlndpgwc2naup.cloudfront.net)
3. **Origins** tab → Edit origin
4. Change origin to your new EB URL: `pinnacle-sso-production.us-east-2.elasticbeanstalk.com`
5. **Behaviors** → Add cache behavior for `/api/*`:
   - Path pattern: `/api/*`
   - Cache policy: CachingDisabled (for dynamic API responses)
   - Origin request policy: AllViewer
   - Allowed HTTP Methods: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
6. Create invalidation: `/*`

### Option B: Create New CloudFront Distribution

```bash
# After setting up CloudFront, update your frontend to use it:
eb setenv VITE_API_BASE_URL="https://your-cloudfront-url.cloudfront.net"
```

---

## Step 8: Update CORS in EB

Add your CloudFront URL to allowed origins:

```bash
eb setenv ALLOWED_ORIGINS="https://main.dnfe4l5bsjojn.amplifyapp.com,https://dlndpgwc2naup.cloudfront.net,http://localhost:3000"
```

---

## Configuration Files Created

The following files were created in `.ebextensions/`:

1. **01_python.config** - Python/WSGI configuration
   - 3 processes, 20 threads per process
   - Auto-scaling: 1-4 instances

2. **02_packages.config** - System packages
   - PostgreSQL client for migrations
   - Build tools for Python packages

3. **03_db_migration.config** - Automated migration
   - Runs `migrations/add_ai_generated_field.sql`
   - Only runs once (leader_only)
   - Safe to re-run

4. **04_model_cache.config** - Model caching
   - Sets up /tmp/model_cache for models
   - Faster subsequent model loads

5. **05_nginx_timeout.config** - Timeout configuration
   - 300s timeouts for RAG operations
   - Handles model loading delays

---

## Monitoring & Debugging

### View Real-time Logs
```bash
eb logs --stream
```

### View Application Logs
```bash
eb logs

# Or SSH and check directly
eb ssh
tail -f /var/log/eb-engine.log
tail -f /var/log/web.stdout.log
```

### Check Environment Variables
```bash
eb printenv
```

### Monitor CloudWatch
- Go to **CloudWatch Console**
- Metrics → ElasticBeanstalk
- Monitor:
  - CPU utilization
  - Request count
  - HTTP 4xx/5xx errors
  - Response time

---

## Costs Estimate

### Infrastructure (Monthly):
- **EB Environment**: Free tier or ~$5/month
- **t3.medium instance**: ~$30/month (1 instance)
- **Load balancer**: ~$16/month
- **Data transfer**: ~$5/month
- **Total**: ~$56/month (with 1 instance)

### AI API (Usage-based):
- **Claude API**: ~$0.003 per question
- 1,000 questions/month: ~$3
- 10,000 questions/month: ~$30

### Your Existing Costs (No change):
- Supabase Database: As per your plan
- Amplify Frontend: As per your plan
- CloudFront: As per your plan

---

## Troubleshooting

### Migration Fails
```bash
# Manually run migration via SSH
eb ssh
psql "$DATABASE_URL" -f /var/app/current/migrations/add_ai_generated_field.sql
exit
```

### Model Download Fails
```bash
# Check logs for download errors
eb logs --stream | grep -i "sentence"

# If needed, pre-download models:
eb ssh
source /var/app/venv/*/bin/activate
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
exit
```

### High Memory Usage
```bash
# Check memory
eb ssh
free -h
top

# If needed, increase instance size
eb config
# Change to t3.large (8GB RAM)
```

### CORS Issues
```bash
# Verify allowed origins
eb printenv | grep ALLOWED_ORIGINS

# Update if needed
eb setenv ALLOWED_ORIGINS="https://main.dnfe4l5bsjojn.amplifyapp.com,https://dlndpgwc2naup.cloudfront.net"
```

---

## Rollback Plan

If deployment fails:

```bash
# List versions
eb appversion

# Deploy previous version
eb deploy --version <previous-version-label>
```

---

## Production Checklist

Before going live:

- [ ] Set ANTHROPIC_API_KEY
- [ ] Verify DATABASE_URL is correct
- [ ] Set SECRET_KEY to strong random value
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_ORIGINS with production URLs
- [ ] Set instance type to t3.medium or larger
- [ ] Test migration on production database
- [ ] Test RAG endpoints
- [ ] Configure CloudFront caching
- [ ] Set up CloudWatch alarms
- [ ] Test CORS from frontend
- [ ] Load test API endpoints
- [ ] Monitor first 24 hours

---

## Quick Reference

```bash
# Deploy
eb deploy

# View logs
eb logs --stream

# Check health
eb health

# SSH into instance
eb ssh

# Update env vars
eb setenv KEY=value

# Restart app
eb deploy --staged

# Scale instances
eb scale 2

# Terminate environment (WARNING: destructive)
eb terminate pinnacle-sso-production
```

---

## Support

If you encounter issues:

1. Check logs: `eb logs --stream`
2. Verify env vars: `eb printenv`
3. Test locally first
4. Check AWS Service Health Dashboard
5. Review CloudWatch metrics

---

**Next Steps**:
1. Get Anthropic API key
2. Run deployment commands above
3. Test endpoints
4. Update CloudFront (if needed)
5. Monitor for 24 hours

Good luck with deployment! 🚀
