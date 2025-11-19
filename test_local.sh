#!/bin/bash
# Test Script for RAG System - Local Development
# This script helps you test the RAG implementation locally

set -e

echo "======================================"
echo "RAG System - Local Testing"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Not in project root directory"
    echo "Please run from: /path/to/pinnacle-sso-backend"
    exit 1
fi

# Step 1: Check dependencies
echo "Step 1: Checking dependencies..."
if ! python -c "import anthropic" 2>/dev/null; then
    echo "⚠️  RAG dependencies not installed"
    read -p "Install now? (y/n): " install_deps
    if [ "$install_deps" = "y" ]; then
        pip install -r requirements.txt
        echo "✓ Dependencies installed"
    else
        echo "Please run: pip install -r requirements.txt"
        exit 1
    fi
else
    echo "✓ Dependencies installed"
fi

# Step 2: Choose test mode
echo ""
echo "Step 2: Choose test mode..."
echo ""
echo "Option 1: Test with RAG DISABLED (Old behavior)"
echo "  - No Anthropic API key needed"
echo "  - All questions saved as 'pending'"
echo "  - Tests the basic flow"
echo ""
echo "Option 2: Test with RAG ENABLED (New behavior)"
echo "  - Requires Anthropic API key"
echo "  - Simple questions auto-answered"
echo "  - Tests AI functionality"
echo ""
read -p "Enter 1 or 2: " test_mode

if [ "$test_mode" = "1" ]; then
    echo ""
    echo "Testing with RAG DISABLED..."
    export ENABLE_RAG_AUTO_ANSWER=false
    export ANTHROPIC_API_KEY=""
    echo "✓ RAG disabled (old behavior)"
elif [ "$test_mode" = "2" ]; then
    echo ""
    echo "Testing with RAG ENABLED..."

    # Check for API key
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo ""
        echo "You need an Anthropic API key from: https://console.anthropic.com/"
        read -p "Enter your API key (or press Enter to skip): " api_key

        if [ -z "$api_key" ]; then
            echo "⚠️  No API key provided. Switching to disabled mode..."
            export ENABLE_RAG_AUTO_ANSWER=false
        else
            export ANTHROPIC_API_KEY="$api_key"
            export ENABLE_RAG_AUTO_ANSWER=true
            echo "✓ RAG enabled with API key"
        fi
    else
        export ENABLE_RAG_AUTO_ANSWER=true
        echo "✓ Using existing ANTHROPIC_API_KEY from environment"
    fi
else
    echo "Invalid option. Exiting."
    exit 1
fi

# Step 3: Set database URL
echo ""
echo "Step 3: Setting database connection..."
export DATABASE_URL="postgresql://postgres.edygpoyhbcrkjmwvxaut:Thisiscool%402020@aws-1-us-east-2.pooler.supabase.com:6543/postgres"
echo "✓ Database URL set (Supabase)"

# Step 4: Check migration
echo ""
echo "Step 4: Checking database migration..."
echo "Verifying ai_generated column exists..."
if psql "$DATABASE_URL" -c "\d proposal_questions" 2>/dev/null | grep -q "ai_generated"; then
    echo "✓ Migration already applied"
else
    echo "⚠️  Migration not applied yet"
    read -p "Run migration now? (y/n): " run_migration
    if [ "$run_migration" = "y" ]; then
        psql "$DATABASE_URL" -f migrations/add_ai_generated_field.sql
        echo "✓ Migration complete"
    else
        echo "⚠️  Skipping migration. Some features may not work."
    fi
fi

# Step 5: Start the server
echo ""
echo "Step 5: Starting development server..."
echo ""
echo "Server will start on: http://localhost:8000"
echo "API docs available at: http://localhost:8000/docs"
echo ""
echo "Configuration:"
echo "  - RAG Auto-Answer: $ENABLE_RAG_AUTO_ANSWER"
echo "  - Database: Supabase"
if [ "$ENABLE_RAG_AUTO_ANSWER" = "true" ]; then
    echo "  - API Key: ${ANTHROPIC_API_KEY:0:20}..."
fi
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "======================================"
echo ""

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
