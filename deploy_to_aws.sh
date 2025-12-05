#!/bin/bash

###############################################################################
# AWS Elastic Beanstalk Deployment Script
# For Pinnacle SSO Backend with RAG
###############################################################################

set -e  # Exit on error

echo "================================================================="
echo "  Pinnacle SSO Backend - AWS Deployment Script"
echo "================================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo -e "${RED}❌ EB CLI not found!${NC}"
    echo "Install with: pip install awsebcli"
    exit 1
fi

echo -e "${GREEN}✅ EB CLI found${NC}"

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured!${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${GREEN}✅ AWS credentials configured${NC}"
echo ""

# Prompt for environment variables
echo "================================================================="
echo "  Environment Configuration"
echo "================================================================="
echo ""

read -p "Enter your Supabase DATABASE_URL: " DATABASE_URL
read -p "Enter your ANTHROPIC_API_KEY: " ANTHROPIC_API_KEY
read -p "Enter your SECRET_KEY (or press Enter for auto-generated): " SECRET_KEY

if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -hex 32)
    echo -e "${YELLOW}Generated SECRET_KEY: ${SECRET_KEY}${NC}"
fi

read -p "Enter AWS region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

read -p "Enter environment name (default: pinnacle-sso-production): " ENV_NAME
ENV_NAME=${ENV_NAME:-pinnacle-sso-production}

read -p "Enter instance type (t3.medium/t3.large/m5.large, default: t3.large): " INSTANCE_TYPE
INSTANCE_TYPE=${INSTANCE_TYPE:-t3.large}

echo ""
echo "================================================================="
echo "  Configuration Summary"
echo "================================================================="
echo "Environment: $ENV_NAME"
echo "Region: $AWS_REGION"
echo "Instance Type: $INSTANCE_TYPE"
echo "Database: ${DATABASE_URL:0:30}..."
echo "API Key: ${ANTHROPIC_API_KEY:0:20}..."
echo ""

read -p "Proceed with deployment? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "================================================================="
echo "  Step 1: Initialize Elastic Beanstalk"
echo "================================================================="

# Check if already initialized
if [ ! -f .elasticbeanstalk/config.yml ]; then
    echo "Initializing EB application..."
    eb init pinnacle-sso-backend \
        --platform python-3.11 \
        --region $AWS_REGION
    echo -e "${GREEN}✅ EB initialized${NC}"
else
    echo -e "${YELLOW}ℹ️  EB already initialized, skipping...${NC}"
fi

echo ""
echo "================================================================="
echo "  Step 2: Check if environment exists"
echo "================================================================="

if eb list | grep -q "$ENV_NAME"; then
    echo -e "${YELLOW}ℹ️  Environment '$ENV_NAME' already exists${NC}"
    read -p "Deploy to existing environment? (y/n): " DEPLOY_EXISTING

    if [ "$DEPLOY_EXISTING" == "y" ]; then
        echo "Setting environment variables..."
        eb use $ENV_NAME
        eb setenv \
            DATABASE_URL="$DATABASE_URL" \
            ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
            SECRET_KEY="$SECRET_KEY" \
            ENVIRONMENT="production" \
            LOG_LEVEL="INFO" \
            DEBUG="False" \
            ENABLE_RAG_AUTO_ANSWER="True" \
            FRONTEND_BASE_URL="https://main.dnfe4l5bsjojn.amplifyapp.com" \
            ALLOWED_ORIGINS="https://main.dnfe4l5bsjojn.amplifyapp.com,https://*.dnfe4l5bsjojn.amplifyapp.com"

        echo ""
        echo "================================================================="
        echo "  Step 3: Deploy Application"
        echo "================================================================="
        eb deploy
    else
        echo "Deployment cancelled."
        exit 0
    fi
else
    echo "Creating new environment: $ENV_NAME"
    echo ""
    echo "================================================================="
    echo "  Step 3: Create Environment and Deploy"
    echo "================================================================="

    eb create $ENV_NAME \
        --instance-type $INSTANCE_TYPE \
        --envvars \
            DATABASE_URL="$DATABASE_URL",\
ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY",\
SECRET_KEY="$SECRET_KEY",\
ENVIRONMENT="production",\
LOG_LEVEL="INFO",\
DEBUG="False",\
ENABLE_RAG_AUTO_ANSWER="True",\
FRONTEND_BASE_URL="https://main.dnfe4l5bsjojn.amplifyapp.com",\
ALLOWED_ORIGINS="https://main.dnfe4l5bsjojn.amplifyapp.com,https://*.dnfe4l5bsjojn.amplifyapp.com"
fi

echo ""
echo "================================================================="
echo "  Step 4: Get Environment Information"
echo "================================================================="

# Get the CNAME
CNAME=$(eb status | grep CNAME | awk '{print $2}')

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "================================================================="
echo "  Deployment Information"
echo "================================================================="
echo "Environment: $ENV_NAME"
echo "Backend URL: http://$CNAME"
echo "HTTPS URL: https://$CNAME"
echo ""
echo "================================================================="
echo "  Next Steps"
echo "================================================================="
echo ""
echo "1. Update Amplify Frontend:"
echo "   - Go to: https://console.aws.amazon.com/amplify"
echo "   - Select your app"
echo "   - Environment variables → Add:"
echo "     Key: VITE_API_URL (or REACT_APP_API_URL)"
echo "     Value: https://$CNAME"
echo ""
echo "2. Enable HTTPS (Recommended):"
echo "   - Go to: EB Console → Configuration → Load Balancer"
echo "   - Add HTTPS listener on port 443"
echo "   - Select/create ACM certificate"
echo ""
echo "3. Test your API:"
echo "   curl https://$CNAME/health"
echo ""
echo "4. View logs:"
echo "   eb logs --stream"
echo ""
echo "5. Monitor health:"
echo "   eb health --refresh"
echo ""
echo "================================================================="
echo "  Useful Commands"
echo "================================================================="
echo ""
echo "Deploy updates:          eb deploy"
echo "View logs:               eb logs"
echo "Check health:            eb health"
echo "SSH into instance:       eb ssh"
echo "Scale instances:         eb scale 2"
echo "Terminate environment:   eb terminate $ENV_NAME"
echo ""
echo "================================================================="

# Save deployment info
cat > deployment_info.txt << EOF
Deployment Date: $(date)
Environment: $ENV_NAME
Region: $AWS_REGION
Instance Type: $INSTANCE_TYPE
Backend URL: https://$CNAME

Update your Amplify frontend with:
VITE_API_URL=https://$CNAME

Test the deployment:
curl https://$CNAME/health
EOF

echo -e "${GREEN}📝 Deployment info saved to: deployment_info.txt${NC}"
echo ""
