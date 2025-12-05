# AWS Deployment Guide for RAG-Enabled Backend

Complete guide to deploy your Pinnacle SSO Backend with RAG capabilities to AWS and connect it with your Amplify frontend.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS CLOUD                                 │
│                                                                  │
│  ┌──────────────────┐         ┌─────────────────────────────┐  │
│  │  AWS Amplify     │         │  Elastic Beanstalk          │  │
│  │  (Frontend)      │────────▶│  Python 3.11                │  │
│  │  React/Vue/Next  │  HTTPS  │  - FastAPI Backend          │  │
│  │                  │         │  - RAG Service (Claude AI)  │  │
│  └──────────────────┘         │  - Sentence Transformers    │  │
│                                │  - FAISS Vector DB          │  │
│                                └─────────────┬───────────────┘  │
│                                              │                   │
│                                              ▼                   │
│                                ┌─────────────────────────────┐  │
│                                │  Supabase PostgreSQL        │  │
│                                │  (External)                 │  │
│                                └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Prerequisites

### Required
- AWS Account with appropriate permissions
- AWS CLI installed and configured
- EB CLI installed (`pip install awsebcli`)
- Git repository with your code
- Supabase PostgreSQL database (already have)
- Anthropic API key for Claude

### Verify Setup
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check EB CLI
eb --version

# Check Python version
python --version  # Should be 3.11+
```

---

## 🚀 Deployment Option 1: Elastic Beanstalk (Recommended)

### Why Elastic Beanstalk?
✅ Easy deployment and management
✅ Auto-scaling built-in
✅ Load balancing included
✅ Already configured in your codebase
✅ Good for RAG workloads (memory-intensive)

### Step 1: Prepare Environment Variables

Create a file `eb_env_vars.txt`:

```bash
DATABASE_URL=postgresql://postgres:[password]@aws-1-us-east-2.pooler.supabase.com:6543/postgres?pgbouncer=true
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=False
ENABLE_RAG_AUTO_ANSWER=True
FRONTEND_BASE_URL=https://main.dnfe4l5bsjojn.amplifyapp.com
ALLOWED_ORIGINS=https://main.dnfe4l5bsjojn.amplifyapp.com,https://*.dnfe4l5bsjojn.amplifyapp.com
SECRET_KEY=your-production-secret-key-change-this
```

### Step 2: Initialize Elastic Beanstalk

```bash
# Navigate to project
cd pinnacle-sso-backend

# Initialize (if not already done)
eb init

# Select:
# - Region: us-east-1 (or your preferred region)
# - Application name: pinnacle-sso-backend
# - Platform: Python 3.11
# - SSH: Yes (for debugging)
```

### Step 3: Create Environment

```bash
# Create production environment
eb create pinnacle-sso-production \
  --instance-type t3.large \
  --region us-east-1 \
  --envvars $(cat eb_env_vars.txt | tr '\n' ',')

# Or set env vars separately:
eb setenv \
  DATABASE_URL="your-db-url" \
  ANTHROPIC_API_KEY="your-api-key" \
  ENVIRONMENT="production" \
  ENABLE_RAG_AUTO_ANSWER="True" \
  FRONTEND_BASE_URL="https://main.dnfe4l5bsjojn.amplifyapp.com"
```

**Instance Type Recommendations for RAG:**
- **Development**: `t3.medium` (4 GB RAM, ~$30/month)
- **Production**: `t3.large` (8 GB RAM, ~$60/month) ✅ Recommended
- **High Traffic**: `m5.large` (8 GB RAM, optimized compute, ~$70/month)

### Step 4: Deploy

```bash
# Deploy current branch
eb deploy

# Monitor deployment
eb health --refresh

# View logs if needed
eb logs
```

### Step 5: Get Your Backend URL

```bash
# Get environment info
eb status

# Output will include:
# CNAME: pinnacle-sso-production.us-east-1.elasticbeanstalk.com
```

**Your API URL will be:**
```
http://pinnacle-sso-production.us-east-1.elasticbeanstalk.com
```

### Step 6: Configure HTTPS (Important!)

#### Option A: Use AWS Certificate Manager (Free SSL)

1. Go to AWS Console → Certificate Manager
2. Request a public certificate for your domain (e.g., `api.pinnacle.com`)
3. Validate domain ownership (DNS or email)
4. Go to Elastic Beanstalk → Configuration → Load Balancer
5. Add HTTPS listener on port 443
6. Select your ACM certificate

#### Option B: Use EB Default (Quick Start)

```bash
# EB provides default HTTPS endpoint
https://pinnacle-sso-production.us-east-1.elasticbeanstalk.com
```

### Step 7: Update Amplify Frontend

1. Go to AWS Amplify Console
2. Select your app: `main.dnfe4l5bsjojn.amplifyapp.com`
3. Go to **Environment variables**
4. Add/Update:
   - Key: `VITE_API_URL` (or `REACT_APP_API_URL` for React)
   - Value: `https://pinnacle-sso-production.us-east-1.elasticbeanstalk.com`
5. Redeploy your frontend

### Step 8: Test Integration

```bash
# Test health endpoint
curl https://your-eb-url.elasticbeanstalk.com/health

# Test RAG endpoint (from your frontend)
curl -X POST "https://your-eb-url.elasticbeanstalk.com/api/v1/proposals/302946/questions/ask-ai" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "question": "What is the total cost?",
    "use_rag": true
  }'
```

---

## 🚀 Deployment Option 2: AWS Lambda (Serverless)

### Why Lambda?
✅ Pay only for what you use
✅ Auto-scales to zero
✅ Lower costs for low/medium traffic
❌ Cold starts (~2-5 seconds first time)
❌ 15-minute timeout limit
❌ More complex setup for RAG

### Using Mangum for FastAPI → Lambda

1. **Install Mangum**
```bash
pip install mangum
```

2. **Update `app/main.py`**
```python
from mangum import Mangum

# Your existing FastAPI app
app = FastAPI()

# Add at the end of file
handler = Mangum(app)
```

3. **Create `serverless.yml`**
```yaml
service: pinnacle-sso-backend

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  memorySize: 3008  # RAG needs more memory
  timeout: 300
  environment:
    DATABASE_URL: ${env:DATABASE_URL}
    ANTHROPIC_API_KEY: ${env:ANTHROPIC_API_KEY}
    ENABLE_RAG_AUTO_ANSWER: "True"

functions:
  api:
    handler: app.main.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true

plugins:
  - serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: true
    slim: true
    strip: false
```

4. **Deploy with Serverless Framework**
```bash
# Install serverless
npm install -g serverless

# Deploy
serverless deploy
```

**Lambda Considerations for RAG:**
- ❌ Model loading on every cold start (2-5 sec delay)
- ❌ Limited to 10GB memory max
- ✅ Good for low-traffic APIs
- ✅ Cost-effective for sporadic use

---

## 🚀 Deployment Option 3: AWS ECS Fargate (Containers)

### Why ECS Fargate?
✅ Full Docker support
✅ Better control than EB
✅ Good for microservices
✅ Persistent containers (no cold starts)
❌ More complex setup
❌ Higher baseline cost

### Quick Setup

1. **Create Dockerfile** (already exists?)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Build and Push to ECR**
```bash
# Create ECR repository
aws ecr create-repository --repository-name pinnacle-sso-backend

# Build and push
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker build -t pinnacle-sso-backend .
docker tag pinnacle-sso-backend:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/pinnacle-sso-backend:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/pinnacle-sso-backend:latest
```

3. **Create ECS Task & Service via Console or CLI**

---

## 📊 Cost Comparison

### Elastic Beanstalk (Recommended)
- **t3.large**: ~$60/month
- **Load Balancer**: ~$20/month
- **Total**: ~$80-100/month
- ✅ Best for production RAG workloads

### Lambda (Serverless)
- **Low traffic** (1000 requests/day): ~$5-10/month
- **Medium traffic** (10k requests/day): ~$30-50/month
- **High traffic** (100k requests/day): ~$150-200/month
- ⚠️ Cold starts affect RAG performance

### ECS Fargate
- **1 task (2 vCPU, 4 GB)**: ~$50/month
- **Load Balancer**: ~$20/month
- **Total**: ~$70-90/month
- ✅ Good alternative to EB

---

## 🔐 Security Best Practices

### 1. Environment Variables
```bash
# NEVER commit these to git
# Use AWS Systems Manager Parameter Store or Secrets Manager

# Store in Parameter Store
aws ssm put-parameter \
  --name "/pinnacle/production/anthropic-api-key" \
  --value "your-api-key" \
  --type "SecureString"

# Reference in EB
eb setenv ANTHROPIC_API_KEY=$(aws ssm get-parameter --name "/pinnacle/production/anthropic-api-key" --with-decryption --query Parameter.Value --output text)
```

### 2. CORS Configuration
Already configured in your `config.py`:
```python
ALLOWED_ORIGINS = "https://main.dnfe4l5bsjojn.amplifyapp.com,https://*.dnfe4l5bsjojn.amplifyapp.com"
```

### 3. Rate Limiting
Already enabled in your backend:
```python
RATE_LIMIT_ENABLED = True
```

### 4. HTTPS Only
- Always use HTTPS for API calls
- Configure SSL/TLS certificates
- Redirect HTTP → HTTPS

---

## 🎯 Quick Start (Fastest Deployment)

```bash
# 1. Set environment variables
cat > .env.production << EOF
DATABASE_URL=your-supabase-url
ANTHROPIC_API_KEY=your-key
ENVIRONMENT=production
ENABLE_RAG_AUTO_ANSWER=True
FRONTEND_BASE_URL=https://main.dnfe4l5bsjojn.amplifyapp.com
EOF

# 2. Initialize and deploy to EB
eb init -p python-3.11 pinnacle-sso-backend --region us-east-1
eb create pinnacle-sso-production --instance-type t3.large --envvars $(cat .env.production | tr '\n' ',')

# 3. Get your URL
eb status | grep CNAME

# 4. Update Amplify with backend URL
# Go to Amplify Console → Environment variables
# Add: VITE_API_URL = https://your-eb-url.elasticbeanstalk.com

# 5. Test
curl https://your-eb-url.elasticbeanstalk.com/health
```

---

## 🔧 Monitoring & Debugging

### View Logs
```bash
# Stream logs live
eb logs --stream

# Get recent logs
eb logs

# SSH into instance
eb ssh
```

### CloudWatch Metrics
- CPU Utilization
- Memory Usage
- Request Count
- Response Time
- Error Rate

### Set Up Alarms
```bash
# Example: High CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name pinnacle-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ElasticBeanstalk \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

---

## 🐛 Troubleshooting

### Issue: RAG Model Download Fails

**Solution**: Pre-download during deployment

Edit `.ebextensions/09_preload_models.config`:
```yaml
container_commands:
  01_download_models:
    command: |
      source /var/app/venv/*/bin/activate
      python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
    leader_only: true
```

### Issue: High Memory Usage

**Solution**: Increase instance size
```bash
eb scale 1 --instance-type m5.large
```

### Issue: CORS Errors

**Solution**: Verify allowed origins
```bash
eb printenv | grep ALLOWED_ORIGINS
```

### Issue: Database Connection Timeout

**Solution**: Check Supabase connection pooling
```bash
# Use pgbouncer connection string
DATABASE_URL=postgresql://postgres:[password]@aws-1-us-east-2.pooler.supabase.com:6543/postgres?pgbouncer=true
```

---

## 📚 Next Steps

1. ✅ Deploy backend to Elastic Beanstalk
2. ✅ Get backend URL
3. ✅ Update Amplify frontend with API URL
4. ✅ Enable HTTPS
5. ✅ Test RAG functionality
6. ✅ Set up monitoring and alarms
7. ✅ Configure custom domain (optional)
8. ✅ Set up CI/CD pipeline (optional)

---

## 🎓 Additional Resources

- [Elastic Beanstalk Python Guide](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-apps.html)
- [AWS Amplify Environment Variables](https://docs.aws.amazon.com/amplify/latest/userguide/environment-variables.html)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Anthropic API Docs](https://docs.anthropic.com/)

---

**Need Help?**
- Check EB logs: `eb logs`
- Check EB health: `eb health`
- SSH into instance: `eb ssh`
- View CloudWatch metrics in AWS Console

**Version**: 1.0
**Last Updated**: 2024-12-05
**Your Current Setup**:
- ✅ Frontend: Amplify (`main.dnfe4l5bsjojn.amplifyapp.com`)
- ✅ Database: Supabase PostgreSQL
- ✅ RAG: Configured with Claude + FAISS
- ⏳ Backend: Ready to deploy to AWS EB
