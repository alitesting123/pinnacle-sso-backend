#!/bin/bash
# API Endpoint Testing Script
# Run this AFTER starting the server with test_local.sh

set -e

API_URL="${API_URL:-http://localhost:8000}"

echo "======================================"
echo "Testing RAG API Endpoints"
echo "======================================"
echo ""
echo "API URL: $API_URL"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health check
echo "Test 1: Health Check"
echo "--------------------"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$API_URL/health" 2>/dev/null || echo "HTTP_CODE:000")
http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d':' -f2)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ API is running${NC}"
else
    echo -e "${RED}✗ API not responding (HTTP $http_code)${NC}"
    echo "Make sure the server is running: ./test_local.sh"
    exit 1
fi
echo ""

# Test 2: Create a simple question (should be auto-answered if RAG enabled)
echo "Test 2: Create Simple Question"
echo "-------------------------------"
echo "Question: 'What is the total cost?'"
echo ""

response=$(curl -s -X POST "$API_URL/api/v1/proposals/GT2025-001/questions" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "",
    "item_name": "General",
    "section_name": "General",
    "question": "What is the total cost?"
  }' 2>/dev/null)

# Check if we got a valid JSON response
if echo "$response" | jq -e . >/dev/null 2>&1; then
    status=$(echo "$response" | jq -r '.status // "unknown"')
    ai_generated=$(echo "$response" | jq -r '.ai_generated // false')
    category=$(echo "$response" | jq -r '.classification.category // "unknown"')
    rag_enabled=$(echo "$response" | jq -r '.classification.rag_enabled // "unknown"')

    echo "Response:"
    echo "  Status: $status"
    echo "  AI Generated: $ai_generated"
    echo "  Category: $category"
    echo "  RAG Enabled: $rag_enabled"

    if [ "$rag_enabled" = "true" ]; then
        if [ "$status" = "answered" ] && [ "$ai_generated" = "true" ]; then
            echo -e "${GREEN}✓ Question auto-answered by AI${NC}"
            answer=$(echo "$response" | jq -r '.answer // "No answer"')
            echo ""
            echo "AI Answer (first 200 chars):"
            echo "${answer:0:200}..."
        else
            echo -e "${YELLOW}⚠ RAG enabled but question not auto-answered${NC}"
            echo "This might be expected if it's classified as complex"
        fi
    else
        if [ "$status" = "pending" ]; then
            echo -e "${GREEN}✓ Question saved as pending (RAG disabled - old behavior)${NC}"
        else
            echo -e "${YELLOW}⚠ Unexpected status: $status${NC}"
        fi
    fi
else
    echo -e "${RED}✗ Invalid JSON response${NC}"
    echo "Response: $response"
fi
echo ""

# Test 3: Create a complex question (should NOT be auto-answered)
echo "Test 3: Create Complex Question"
echo "--------------------------------"
echo "Question: 'Why did you choose this specific audio equipment?'"
echo ""

response=$(curl -s -X POST "$API_URL/api/v1/proposals/GT2025-001/questions" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "audio-001",
    "item_name": "Audio Equipment",
    "section_name": "Audio",
    "question": "Why did you choose this specific audio equipment over other options?"
  }' 2>/dev/null)

if echo "$response" | jq -e . >/dev/null 2>&1; then
    status=$(echo "$response" | jq -r '.status // "unknown"')
    category=$(echo "$response" | jq -r '.classification.category // "unknown"')

    echo "Response:"
    echo "  Status: $status"
    echo "  Category: $category"

    if [ "$category" = "complex" ] && [ "$status" = "pending" ]; then
        echo -e "${GREEN}✓ Complex question correctly saved as pending${NC}"
    else
        echo -e "${YELLOW}⚠ Unexpected: category=$category, status=$status${NC}"
    fi
else
    echo -e "${RED}✗ Invalid JSON response${NC}"
fi
echo ""

# Test 4: Create a T&C question (should be auto-answered if RAG enabled)
echo "Test 4: Create Terms & Conditions Question"
echo "-------------------------------------------"
echo "Question: 'What is your cancellation policy?'"
echo ""

response=$(curl -s -X POST "$API_URL/api/v1/proposals/GT2025-001/questions" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "",
    "item_name": "General",
    "section_name": "General",
    "question": "What is your cancellation policy?"
  }' 2>/dev/null)

if echo "$response" | jq -e . >/dev/null 2>&1; then
    status=$(echo "$response" | jq -r '.status // "unknown"')
    category=$(echo "$response" | jq -r '.classification.category // "unknown"')
    rag_enabled=$(echo "$response" | jq -r '.classification.rag_enabled // "unknown"')

    echo "Response:"
    echo "  Status: $status"
    echo "  Category: $category"

    if [ "$rag_enabled" = "true" ]; then
        if [ "$category" = "terms_and_conditions" ]; then
            echo -e "${GREEN}✓ T&C question correctly identified${NC}"
            if [ "$status" = "answered" ]; then
                echo -e "${GREEN}✓ Auto-answered by AI${NC}"
            fi
        fi
    else
        if [ "$status" = "pending" ]; then
            echo -e "${GREEN}✓ Saved as pending (RAG disabled)${NC}"
        fi
    fi
else
    echo -e "${RED}✗ Invalid JSON response${NC}"
fi
echo ""

# Test 5: Interactive Q&A (if RAG enabled)
echo "Test 5: Interactive Ask AI Endpoint"
echo "------------------------------------"
echo "Question: 'When is the event?'"
echo ""

response=$(curl -s -X POST "$API_URL/api/v1/proposals/GT2025-001/questions/ask-ai" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "When is the event?",
    "use_rag": true
  }' 2>/dev/null)

if echo "$response" | jq -e . >/dev/null 2>&1; then
    # Check if it's an error or success
    detail=$(echo "$response" | jq -r '.detail // ""')
    answer=$(echo "$response" | jq -r '.answer // ""')

    if [ -n "$detail" ] && [ "$detail" != "null" ]; then
        echo -e "${YELLOW}⚠ Error: $detail${NC}"
        echo "This is expected if RAG is disabled or proposal doesn't exist"
    elif [ -n "$answer" ] && [ "$answer" != "null" ]; then
        echo -e "${GREEN}✓ Interactive AI endpoint working${NC}"
        echo ""
        echo "AI Answer (first 150 chars):"
        echo "${answer:0:150}..."
    else
        echo -e "${YELLOW}⚠ Unexpected response format${NC}"
    fi
else
    echo -e "${RED}✗ Invalid JSON response${NC}"
fi
echo ""

# Summary
echo "======================================"
echo "Test Summary"
echo "======================================"
echo ""
echo "All tests completed!"
echo ""
echo "Next steps:"
echo "  1. Check the server logs for any errors"
echo "  2. Visit http://localhost:8000/docs for API documentation"
echo "  3. Test with your frontend application"
echo ""
echo "To view created questions:"
echo "  curl http://localhost:8000/api/v1/proposals/GT2025-001/questions"
echo ""
