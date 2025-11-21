# Elastic Beanstalk Deployment Guide

Complete guide for deploying the Pinnacle SSO Backend with RAG capabilities to AWS Elastic Beanstalk.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Configuration](#configuration)
4. [Deployment](#deployment)
5. [Database Migration](#database-migration)
6. [Environment Variables](#environment-variables)
7. [Post-Deployment](#post-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools
- AWS CLI installed and configured
- EB CLI (Elastic Beanstalk Command Line Interface)
- Git
- Python 3.8+

### Install EB CLI
```bash
pip install awsebcli --upgrade
```

### Verify Installation
```bash
eb --version
# Should output: EB CLI 3.x.x (Python 3.x.x)
```

---

## Initial Setup

### 1. Initialize Elastic Beanstalk Application

Navigate to your project directory:
```bash
cd /path/to/pinnacle-sso-backend
```

Initialize EB:
```bash
eb init
```

Answer the prompts:
- **Region**: Select your AWS region (e.g., `us-east-1`)
- **Application name**: `pinnacle-sso-backend`
- **Platform**: `Python 3.11` (or your Python version)
- **CodeCommit**: No
- **SSH**: Yes (recommended for debugging)

### 2. Create Elastic Beanstalk Environment

```bash
eb create pinnacle-sso-production
```

Options:
- **Environment name**: `pinnacle-sso-production`
- **DNS CNAME**: `pinnacle-sso-api` (or your preference)
- **Load balancer**: Application Load Balancer

---

## Configuration

### 1. Create `.ebextensions` Directory

This directory contains configuration files for EB:

```bash
mkdir -p .ebextensions
```

### 2. Create Python Configuration File

Create `.ebextensions/01_python.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app.main:app
    NumProcesses: 3
    NumThreads: 20
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
  aws:autoscaling:asg:
    MinSize: 2
    MaxSize: 6
  aws:autoscaling:trigger:
    MeasureName: CPUUtilization
    Unit: Percent
    UpperThreshold: 70
    LowerThreshold: 20
```

### 3. Create Packages Configuration

Create `.ebextensions/02_packages.config`:

```yaml
packages:
  yum:
    gcc: []
    gcc-c++: []
    make: []
    postgresql-devel: []

commands:
  01_upgrade_pip:
    command: "/var/app/venv/*/bin/pip install --upgrade pip"
    ignoreErrors: false
```

### 4. Create Environment Variables Configuration

Create `.ebextensions/03_env_vars.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    ENVIRONMENT: "production"
    LOG_LEVEL: "INFO"
    # Database and other sensitive vars should be set via EB console or CLI
```

### 5. Create WSGI Server Configuration

Create or update `Procfile`:

```
web: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind :8000 --timeout 300
```

### 6. Update requirements.txt for Production

Ensure your `requirements.txt` includes production dependencies:

```text
# Already included from previous implementation
anthropic==0.39.0
sentence-transformers==2.2.2
faiss-cpu==1.7.4
numpy==1.24.3
tiktoken==0.5.2

# Add if not present:
uvicorn[standard]==0.24.0
gunicorn==21.2.0
```

---

## Deployment

### 1. Set Environment Variables

Set sensitive environment variables (don't commit these!):

```bash
eb setenv \
  DATABASE_URL="postgresql://user:password@your-rds-endpoint:5432/pinnacle" \
  ANTHROPIC_API_KEY="your-anthropic-api-key" \
  JWT_SECRET_KEY="your-secret-key" \
  AWS_REGION="us-east-1" \
  COGNITO_USER_POOL_ID="your-pool-id" \
  COGNITO_CLIENT_ID="your-client-id" \
  REDIS_HOST="your-redis-endpoint" \
  REDIS_PORT="6379"
```

### 2. Deploy Application

```bash
# Deploy from current branch
eb deploy

# Or deploy from specific branch
git checkout main
eb deploy
```

### 3. Monitor Deployment

```bash
# View logs in real-time
eb logs --stream

# Check health status
eb health

# Check application status
eb status
```

---

## Database Migration

### Option 1: Manual Migration via SSH

```bash
# SSH into EB instance
eb ssh

# Navigate to app directory
cd /var/app/current

# Run migration
source /var/app/venv/*/bin/activate
psql $DATABASE_URL -f migrations/add_ai_generated_field.sql

# Exit SSH
exit
```

### Option 2: Automated Migration via .ebextensions

Create `.ebextensions/04_db_migration.config`:

```yaml
container_commands:
  01_migrate:
    command: "psql $DATABASE_URL -f migrations/add_ai_generated_field.sql || true"
    leader_only: true
    ignoreErrors: true
```

**Note**: Be careful with `ignoreErrors: true` - only use for idempotent migrations.

### Option 3: Pre-deployment Script

Create `scripts/migrate.sh`:

```bash
#!/bin/bash
set -e

echo "Running database migrations..."

# Install psql if needed
if ! command -v psql &> /dev/null; then
    yum install -y postgresql
fi

# Run migration
psql $DATABASE_URL -f migrations/add_ai_generated_field.sql

echo "Migration complete!"
```

Add to `.ebextensions/04_db_migration.config`:

```yaml
files:
  "/opt/elasticbeanstalk/hooks/appdeploy/pre/01_migrate.sh":
    mode: "000755"
    owner: root
    group: root
    content: |
      #!/bin/bash
      source /var/app/venv/*/bin/activate
      cd /var/app/staging
      bash scripts/migrate.sh
```

---

## Environment Variables

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `ANTHROPIC_API_KEY` | Claude AI API key | `sk-ant-api03-xxx` |
| `JWT_SECRET_KEY` | Secret for JWT tokens | `your-random-secret-key` |
| `ENVIRONMENT` | Environment name | `production` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region for services | `us-east-1` |
| `COGNITO_USER_POOL_ID` | Cognito user pool | - |
| `COGNITO_CLIENT_ID` | Cognito client ID | - |
| `REDIS_HOST` | Redis host for caching | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |

### Setting Environment Variables

```bash
# Via EB CLI
eb setenv KEY=value KEY2=value2

# Via AWS Console
# 1. Go to Elastic Beanstalk console
# 2. Select your environment
# 3. Configuration → Software → Environment properties
# 4. Add key-value pairs
```

---

## Post-Deployment

### 1. Verify Deployment

```bash
# Check application health
eb health

# Check URL
eb open

# Test API endpoint
curl https://your-app-url.elasticbeanstalk.com/health
```

### 2. Test RAG Functionality

```bash
# Test AI question endpoint
curl -X POST "https://your-app-url.elasticbeanstalk.com/api/v1/proposals/JOB-001/questions/ask-ai" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "question": "What is the total cost?",
    "use_rag": true
  }'
```

### 3. Monitor Application

```bash
# View recent logs
eb logs

# Stream logs live
eb logs --stream

# CloudWatch metrics
# Go to AWS Console → CloudWatch → Metrics → ElasticBeanstalk
```

### 4. Set Up Alarms

Create CloudWatch alarms for:
- High CPU utilization (>80%)
- High memory usage (>90%)
- HTTP 5xx errors
- Application health degradation

---

## Scaling Configuration

### Auto-Scaling Setup

Edit `.ebextensions/05_scaling.config`:

```yaml
option_settings:
  aws:autoscaling:asg:
    MinSize: 2
    MaxSize: 10
    Cooldown: 360
  aws:autoscaling:trigger:
    MeasureName: CPUUtilization
    Unit: Percent
    UpperThreshold: 70
    UpperBreachScaleIncrement: 2
    LowerThreshold: 20
    LowerBreachScaleIncrement: -1
    BreachDuration: 3
    Period: 3
    EvaluationPeriods: 2
    Statistic: Average
```

### Manual Scaling

```bash
# Scale to specific number of instances
eb scale 4

# Update auto-scaling settings
eb config
# Then edit the configuration in your editor
```

---

## RAG-Specific Considerations

### 1. Memory Requirements

The RAG system uses embedding models that require additional memory:

- **Minimum**: t3.medium (4 GB RAM)
- **Recommended**: t3.large (8 GB RAM)
- **Production**: m5.large or larger for high traffic

Configure instance type:

```bash
eb config
# Then set:
# aws:autoscaling:launchconfiguration:
#   InstanceType: t3.large
```

### 2. Model Loading Optimization

Create `.ebextensions/06_model_cache.config`:

```yaml
commands:
  01_create_model_cache:
    command: "mkdir -p /tmp/model_cache"

option_settings:
  aws:elasticbeanstalk:application:environment:
    TRANSFORMERS_CACHE: "/tmp/model_cache"
    SENTENCE_TRANSFORMERS_HOME: "/tmp/model_cache"
```

### 3. Timeout Configuration

RAG queries can take longer, especially on first load:

```yaml
option_settings:
  aws:elasticbeanstalk:environment:proxy:
    ProxyServer: nginx
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: staticfiles

files:
  "/etc/nginx/conf.d/timeout.conf":
    mode: "000644"
    owner: root
    group: root
    content: |
      proxy_connect_timeout 300;
      proxy_send_timeout 300;
      proxy_read_timeout 300;
      send_timeout 300;
```

---

## Troubleshooting

### Common Issues

#### 1. Deployment Fails

```bash
# Check detailed logs
eb logs --all

# Common causes:
# - Missing dependencies in requirements.txt
# - Incorrect Python version
# - Environment variable issues
```

#### 2. Application Won't Start

```bash
# SSH into instance
eb ssh

# Check application logs
tail -f /var/log/eb-engine.log
tail -f /var/log/web.stdout.log

# Check if dependencies installed
ls /var/app/venv/*/lib/python*/site-packages/
```

#### 3. RAG Model Download Failures

```bash
# Pre-download models during deployment
# Add to .ebextensions/07_preload_models.config:

container_commands:
  01_download_models:
    command: |
      source /var/app/venv/*/bin/activate
      python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
    leader_only: true
```

#### 4. High Memory Usage

```bash
# Monitor memory
eb ssh
free -h
top

# If needed, increase instance size:
eb config
# Change InstanceType to larger size
```

#### 5. Database Connection Issues

```bash
# Verify DATABASE_URL is set
eb printenv | grep DATABASE_URL

# Test connection from EB instance
eb ssh
psql $DATABASE_URL -c "SELECT 1;"
```

---

## Rollback

### Rollback to Previous Version

```bash
# List available versions
eb appversion

# Deploy specific version
eb deploy --version <version-label>
```

### Emergency Rollback

```bash
# Via AWS Console:
# 1. Go to Elastic Beanstalk → Applications
# 2. Select your application
# 3. Application versions
# 4. Select previous version → Deploy
```

---

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Elastic Beanstalk

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Install EB CLI
      run: pip install awsebcli

    - name: Deploy to EB
      run: |
        eb init pinnacle-sso-backend --region us-east-1 --platform python-3.11
        eb deploy pinnacle-sso-production --staged
```

---

## Best Practices

1. **Use RDS for Database**: Don't use local SQLite in production
2. **Enable Enhanced Health Reporting**: Better monitoring and diagnostics
3. **Use Application Load Balancer**: Better for HTTP/HTTPS traffic
4. **Enable HTTPS**: Use AWS Certificate Manager for SSL
5. **Set Up CloudWatch Alarms**: Monitor critical metrics
6. **Use Multiple AZs**: For high availability
7. **Regular Backups**: RDS automated backups enabled
8. **Environment Cloning**: Test changes in staging first
9. **Keep Secrets in Secrets Manager**: Don't use environment variables for very sensitive data
10. **Monitor Costs**: Set up billing alarms

---

## Cost Optimization

1. **Right-size Instances**: Start with t3.medium, scale as needed
2. **Use Reserved Instances**: For predictable workloads
3. **Auto-scaling**: Scale down during low traffic
4. **RDS Reserved Instances**: If database is always running
5. **CloudWatch Log Retention**: Set appropriate retention periods
6. **S3 Lifecycle Policies**: For deployment artifacts

---

## Support Resources

- [AWS Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [EB CLI Documentation](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)
- [Troubleshooting Guide](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/troubleshooting.html)

---

**Version**: 1.0
**Last Updated**: 2024-11-17
**Maintainer**: Pinnacle Live Development Team
