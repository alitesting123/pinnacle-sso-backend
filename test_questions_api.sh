#!/bin/bash
# test_questions_api.sh - Test the Questions API Endpoint

echo "🧪 Testing Pinnacle Live Questions API"
echo "========================================"
echo ""

# Configuration
BACKEND_URL="https://dlndpgwc2naup.cloudfront.net"
PROPOSAL_ID="302798"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Configuration:${NC}"
echo "Backend URL: $BACKEND_URL"
echo "Proposal ID: $PROPOSAL_ID"
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
echo "---"
curl -X GET "$BACKEND_URL/health" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.'
echo ""
echo ""

# Test 2: Get Questions (Correct URL - NO trailing slash)
echo -e "${YELLOW}Test 2: GET Questions (Correct URL - No Trailing Slash)${NC}"
echo "URL: $BACKEND_URL/api/v1/proposals/$PROPOSAL_ID/questions"
echo "---"
curl -X GET "$BACKEND_URL/api/v1/proposals/$PROPOSAL_ID/questions" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.'
echo ""
echo ""

# Test 3: Get Questions (Wrong URL - WITH trailing slash)
echo -e "${YELLOW}Test 3: GET Questions (Wrong URL - With Trailing Slash)${NC}"
echo "URL: $BACKEND_URL/api/v1/proposals/$PROPOSAL_ID/questions/"
echo "---"
curl -X GET "$BACKEND_URL/api/v1/proposals/$PROPOSAL_ID/questions/" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.'
echo ""
echo ""

# Test 4: Create a New Question (POST)
echo -e "${YELLOW}Test 4: POST Create Question${NC}"
echo "URL: $BACKEND_URL/api/v1/proposals/$PROPOSAL_ID/questions"
echo "---"
QUESTION_PAYLOAD='{
  "item_id": "test-item-' $(date +%s) '",
  "item_name": "LED Video Wall 10x20",
  "section_name": "Audio/Video Equipment",
  "question": "Is this equipment available for September 30, 2025? Can we get a demo before the event?"
}'

curl -X POST "$BACKEND_URL/api/v1/proposals/$PROPOSAL_ID/questions" \
  -H "Content-Type: application/json" \
  -d "$QUESTION_PAYLOAD" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.'
echo ""
echo ""

# Test 5: Get Single Proposal (to verify it exists)
echo -e "${YELLOW}Test 5: GET Single Proposal (Verify Proposal Exists)${NC}"
echo "URL: $BACKEND_URL/api/v1/proposals/$PROPOSAL_ID"
echo "---"
curl -X GET "$BACKEND_URL/api/v1/proposals/$PROPOSAL_ID" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.'
echo ""
echo ""

echo -e "${GREEN}✅ Testing Complete!${NC}"
echo ""
echo "Expected Results:"
echo "  - Test 1 (Health): 200 OK"
echo "  - Test 2 (GET Questions): 200 OK"
echo "  - Test 3 (GET with /): 404 Not Found (expected!)"
echo "  - Test 4 (POST Question): 200 OK"
echo "  - Test 5 (GET Proposal): 200 OK"