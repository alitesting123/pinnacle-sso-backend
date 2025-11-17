#!/bin/bash
# Quick Deployment Script for Pinnacle SSO Backend with RAG
# Run this step-by-step after reviewing EB_DEPLOYMENT_SETUP.md

set -e  # Exit on error

echo "======================================"
echo "Pinnacle SSO Backend - EB Deployment"
echo "======================================"
echo ""

# Step 1: Prerequisites check
echo "Step 1: Checking prerequisites..."
if ! command -v eb &> /dev/null; then
    echo "❌ EB CLI not found. Install with: pip install awsebcli"
    exit 1
fi
echo "✓ EB CLI found"

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install git"
    exit 1
fi
echo "✓ Git found"

# Step 2: Check for Anthropic API key
echo ""
echo "Step 2: Checking for Anthropic API key..."
read -p "Do you have your Anthropic API key? (y/n): " has_key
if [ "$has_key" != "y" ]; then
    echo ""
    echo "⚠️  Get your API key from: https://console.anthropic.com/"
    echo "Then re-run this script"
    exit 1
fi

read -p "Enter your Anthropic API key: " ANTHROPIC_KEY
if [ -z "$ANTHROPIC_KEY" ]; then
    echo "❌ API key cannot be empty"
    exit 1
fi
echo "✓ API key entered"

# Step 3: Initialize EB (if not already done)
echo ""
echo "Step 3: Initializing Elastic Beanstalk..."
if [ ! -d ".elasticbeanstalk" ]; then
    echo "Initializing EB application..."
    eb init pinnacle-sso-backend \
        --region us-east-2 \
        --platform "python-3.11"
else
    echo "✓ EB already initialized"
fi

# Step 4: Create environment (if not already created)
echo ""
echo "Step 4: Creating/Checking EB environment..."
read -p "Do you want to create a new environment? (y/n): " create_env
if [ "$create_env" = "y" ]; then
    echo "Creating environment pinnacle-sso-production..."
    eb create pinnacle-sso-production \
        --instance-type t3.medium \
        --timeout 15
else
    echo "Using existing environment"
fi

# Step 5: Set environment variables
echo ""
echo "Step 5: Setting environment variables..."
eb setenv \
    DATABASE_URL="postgresql://postgres.edygpoyhbcrkjmwvxaut:Thisiscool%402020@aws-1-us-east-2.pooler.supabase.com:6543/postgres" \
    ANTHROPIC_API_KEY="$ANTHROPIC_KEY" \
    FRONTEND_BASE_URL="https://main.dnfe4l5bsjojn.amplifyapp.com" \
    ALLOWED_ORIGINS="https://main.dnfe4l5bsjojn.amplifyapp.com,https://*.dnfe4l5bsjojn.amplifyapp.com,https://dlndpgwc2naup.cloudfront.net,http://localhost:3000" \
    SECRET_KEY="your-super-secret-key-change-this-in-production-minimum-32-chars" \
    ENVIRONMENT="production" \
    DEBUG="False" \
    AWS_REGION="us-east-2" \
    LOG_LEVEL="INFO" \
    RATE_LIMIT_ENABLED="True" \
    PUBLIC_API_KEY="1N20PR8Patev2YBQnwsYLUyNwjlKTw2m3Hw814fr24c"

echo "✓ Environment variables set"

# Step 6: Commit changes
echo ""
echo "Step 6: Committing .ebextensions configuration..."
git add .ebextensions
git status

read -p "Commit these changes? (y/n): " commit_changes
if [ "$commit_changes" = "y" ]; then
    git commit -m "Add Elastic Beanstalk configuration for RAG deployment"
    echo "✓ Changes committed"
else
    echo "⚠️  Skipping commit. Make sure to commit before deploying!"
fi

# Step 7: Deploy
echo ""
echo "Step 7: Deploying to Elastic Beanstalk..."
read -p "Deploy now? (y/n): " deploy_now
if [ "$deploy_now" = "y" ]; then
    echo "Deploying... (this may take 5-10 minutes)"
    eb deploy --timeout 15
    echo "✓ Deployment complete"
else
    echo "⚠️  Skipping deployment. Deploy later with: eb deploy"
fi

# Step 8: Verify deployment
echo ""
echo "Step 8: Verification..."
echo ""
echo "To verify deployment, run these commands:"
echo "  eb health              # Check application health"
echo "  eb logs --stream       # View real-time logs"
echo "  eb status              # Get environment details"
echo ""
echo "To test RAG endpoint:"
echo "  1. Get your EB URL from: eb status"
echo "  2. Test with: curl -X POST 'http://YOUR-URL/api/v1/proposals/JOB-001/questions' -H 'Content-Type: application/json' -d '{\"question\":\"What is the total cost?\",\"item_id\":\"\",\"item_name\":\"General\",\"section_name\":\"General\"}'"
echo ""
echo "======================================"
echo "Deployment script complete!"
echo "======================================"
echo ""
echo "📚 For detailed documentation, see: EB_DEPLOYMENT_SETUP.md"
