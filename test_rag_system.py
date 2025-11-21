#!/usr/bin/env python3
"""
Test script for RAG system

This script tests the RAG service functionality without requiring a running server.
Usage: python test_rag_system.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.rag_service import RAGService, get_rag_service
from app.models.proposals import Proposal, ProposalSection, ProposalLineItem
from datetime import date
from decimal import Decimal


def create_mock_proposal():
    """Create a mock proposal for testing"""
    proposal = Proposal()
    proposal.id = "12345678-1234-1234-1234-123456789012"
    proposal.job_number = "TEST-2024-001"
    proposal.client_name = "Acme Corporation"
    proposal.client_company = "Acme Corp"
    proposal.event_location = "Grand Ballroom, Downtown Convention Center"
    proposal.venue_name = "Convention Center"
    proposal.start_date = date(2024, 12, 15)
    proposal.end_date = date(2024, 12, 15)
    proposal.status = "tentative"
    proposal.prepared_by = "John Smith"
    proposal.salesperson = "Jane Doe"
    proposal.product_subtotal = Decimal("15000.00")
    proposal.product_discount = Decimal("1500.00")
    proposal.product_total = Decimal("13500.00")
    proposal.labor_total = Decimal("3500.00")
    proposal.service_charge = Decimal("850.00")
    proposal.tax_amount = Decimal("1785.00")
    proposal.total_cost = Decimal("19635.00")
    proposal.notes = "This is a corporate event with AV requirements for 500 attendees."

    # Create mock sections
    audio_section = ProposalSection()
    audio_section.id = "section-audio-001"
    audio_section.section_name = "Audio"
    audio_section.section_total = Decimal("8000.00")
    audio_section.notes = "Professional audio system for main stage"
    audio_section.items = []

    # Create mock line items
    item1 = ProposalLineItem()
    item1.id = "item-001"
    item1.description = "Wireless Microphone System (Shure ULXD)"
    item1.quantity = 4
    item1.unit_price = Decimal("250.00")
    item1.subtotal = Decimal("1000.00")
    item1.category = "Audio"
    audio_section.items.append(item1)

    item2 = ProposalLineItem()
    item2.id = "item-002"
    item2.description = "Line Array Speaker System (QSC KLA12)"
    item2.quantity = 8
    item2.unit_price = Decimal("500.00")
    item2.subtotal = Decimal("4000.00")
    item2.category = "Audio"
    audio_section.items.append(item2)

    proposal.sections = [audio_section]
    proposal.line_items = audio_section.items
    proposal.timeline = []
    proposal.labor = []

    return proposal


async def test_rag_service():
    """Test the RAG service functionality"""
    print("=" * 60)
    print("RAG System Test")
    print("=" * 60)

    # Check if API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: ANTHROPIC_API_KEY not set in environment")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        print("\nTesting without API key (limited functionality)...\n")

    # Initialize RAG service
    print("\n1. Initializing RAG Service...")
    rag = RAGService(api_key=api_key)

    if rag.client:
        print("✓ Claude client initialized")
    else:
        print("✗ Claude client not initialized (missing API key)")

    if rag.embedder:
        print("✓ Embedding model loaded")
    else:
        print("✗ Embedding model not loaded")

    # Create mock proposal
    print("\n2. Creating Mock Proposal...")
    proposal = create_mock_proposal()
    print(f"✓ Mock proposal created: {proposal.job_number}")
    print(f"  Client: {proposal.client_name}")
    print(f"  Total Cost: ${proposal.total_cost}")
    print(f"  Event Date: {proposal.start_date}")

    # Test content extraction
    print("\n3. Testing Content Extraction...")
    chunks = rag.extract_proposal_content(proposal, db=None)
    print(f"✓ Extracted {len(chunks)} content chunks")
    print(f"  Chunk types: {set(chunk['type'] for chunk in chunks)}")

    # Show sample chunk
    if chunks:
        print(f"\n  Sample chunk (Overview):")
        print(f"  {'-' * 40}")
        print(f"  {chunks[0]['content'][:200]}...")

    # Test vector store creation
    print("\n4. Testing Vector Store Creation...")
    if rag.embedder:
        vector_store = rag.create_vector_store(str(proposal.id), chunks)
        if vector_store:
            print(f"✓ Vector store created with {len(chunks)} embeddings")
        else:
            print("✗ Failed to create vector store")
    else:
        print("⊘ Skipped (embedding model not available)")

    # Test question classification
    print("\n5. Testing Question Classification...")
    test_questions = [
        "What is the total cost?",
        "Explain the audio setup in detail",
        "When is the event?",
        "Why did you choose these specific microphones?",
    ]

    for question in test_questions:
        is_simple, reason = await rag.is_simple_question(question)
        complexity = "SIMPLE" if is_simple else "COMPLEX"
        print(f"  {complexity}: '{question}'")
        print(f"    → {reason}")

    # Test context retrieval
    print("\n6. Testing Context Retrieval...")
    if rag.embedder and str(proposal.id) in rag.vector_stores:
        test_query = "What audio equipment is included?"
        relevant = rag.retrieve_relevant_context(
            str(proposal.id),
            test_query,
            top_k=3
        )
        print(f"✓ Retrieved {len(relevant)} relevant chunks for: '{test_query}'")
        for i, chunk in enumerate(relevant[:2], 1):
            print(f"\n  Chunk {i} (Relevance: {chunk.get('relevance_score', 0):.3f}):")
            print(f"  Section: {chunk['section']}, Type: {chunk['type']}")
            print(f"  {chunk['content'][:150]}...")
    else:
        print("⊘ Skipped (vector store not available)")

    # Test answer generation
    print("\n7. Testing Answer Generation...")
    if rag.client:
        test_question = "What is the total cost of this proposal?"
        print(f"  Question: '{test_question}'")

        try:
            result = await rag.answer_question(
                question=test_question,
                proposal=proposal,
                db=None,
                use_rag=True
            )

            print(f"\n  ✓ Answer generated successfully!")
            print(f"  Method: {result.get('method')}")
            print(f"  Confidence: {result.get('confidence')}")
            print(f"\n  Answer:")
            print(f"  {'-' * 40}")
            print(f"  {result.get('answer')}")
            print(f"  {'-' * 40}")

            if result.get('sources'):
                print(f"\n  Sources used:")
                for source in result['sources']:
                    print(f"    - {source['section']} ({source['type']})")

        except Exception as e:
            print(f"  ✗ Error generating answer: {e}")
    else:
        print("⊘ Skipped (Claude client not initialized)")

    # Test cache clearing
    print("\n8. Testing Cache Management...")
    rag.clear_cache(str(proposal.id))
    print(f"✓ Cache cleared for proposal {proposal.job_number}")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)

    # Summary
    print("\n📊 SUMMARY")
    print("-" * 60)
    checks = []
    checks.append(("API Key Set", bool(api_key)))
    checks.append(("Claude Client", bool(rag.client)))
    checks.append(("Embedding Model", bool(rag.embedder)))
    checks.append(("Content Extraction", len(chunks) > 0))
    checks.append(("Vector Store", str(proposal.id) in rag.vector_stores))

    for check, status in checks:
        symbol = "✓" if status else "✗"
        print(f"{symbol} {check}")

    print("\n")

    if not api_key:
        print("⚠️  To test full functionality, set ANTHROPIC_API_KEY:")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        print("   python test_rag_system.py")

    return True


if __name__ == "__main__":
    print("\n🤖 Starting RAG System Test...\n")

    try:
        asyncio.run(test_rag_service())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
