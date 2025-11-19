"""
RAG (Retrieval-Augmented Generation) Service for Proposal Q&A

This service provides intelligent question answering using:
1. Question complexity detection
2. Vector-based semantic search for relevant context
3. Claude API for answer generation
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np

try:
    import anthropic
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError as e:
    logging.warning(f"RAG dependencies not installed: {e}. Install with: pip install anthropic sentence-transformers faiss-cpu")
    anthropic = None
    SentenceTransformer = None
    faiss = None

from sqlalchemy.orm import Session
from app.models.proposals import Proposal, ProposalSection, ProposalLineItem, ProposalTimeline, ProposalLabor
from app.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Service for intelligent question answering with RAG"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize RAG service with Claude API and embedding model"""
        self.api_key = api_key or settings.ANTHROPIC_API_KEY

        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not configured in settings")

        # Initialize Claude client
        if anthropic and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("Claude client not initialized")

        # Initialize embedding model (using a lightweight model)
        if SentenceTransformer:
            try:
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self.embedder = None
        else:
            self.embedder = None

        # Cache for proposal vector stores
        self.vector_stores: Dict[str, Any] = {}
        self.document_chunks: Dict[str, List[Dict]] = {}

    def is_terms_and_conditions_question(self, question: str) -> bool:
        """
        Detect if a question is about terms and conditions
        """
        question_lower = question.lower().strip()

        terms_keywords = [
            'terms', 'conditions', 'terms and conditions', 'terms & conditions',
            'contract', 'agreement', 'policy', 'policies',
            'cancellation', 'refund', 'payment terms',
            'liability', 'insurance', 'warranty', 'warranties',
            'deposit', 'payment schedule', 'late fee',
            'damage', 'responsibility', 'obligations'
        ]

        return any(keyword in question_lower for keyword in terms_keywords)

    async def classify_question(self, question: str) -> Dict[str, Any]:
        """
        Classify question into categories and determine handling strategy

        Returns:
        {
            'category': 'simple' | 'complex' | 'terms_and_conditions',
            'should_auto_answer': bool,
            'use_ai': bool,
            'reasoning': str
        }
        """
        question_lower = question.lower().strip()

        # Check if it's about terms and conditions first
        if self.is_terms_and_conditions_question(question):
            return {
                'category': 'terms_and_conditions',
                'should_auto_answer': True,  # Auto-answer with AI flag
                'use_ai': True,
                'ai_flag': True,  # Mark as AI-generated
                'reasoning': 'Terms and conditions question - AI can provide standard answer'
            }

        # Check if it's a simple factual question
        # Very short questions are often simple
        if len(question.split()) <= 5:
            simple_indicators = ['what', 'when', 'where', 'who', 'how much', 'how long', 'how many', 'cost', 'price', 'time', 'date']
            if any(indicator in question_lower for indicator in simple_indicators):
                return {
                    'category': 'simple',
                    'should_auto_answer': True,
                    'use_ai': True,
                    'ai_flag': True,
                    'reasoning': 'Short factual question - can be answered directly'
                }

        # Questions asking for specific facts
        factual_keywords = [
            'what is', 'when is', 'where is', 'who is',
            'what time', 'how much', 'how long', 'how many',
            'what does', 'is there', 'do you have', 'can you provide',
            'what are', 'when does', 'where does'
        ]
        if any(keyword in question_lower for keyword in factual_keywords):
            return {
                'category': 'simple',
                'should_auto_answer': True,
                'use_ai': True,
                'ai_flag': True,
                'reasoning': 'Factual question - can be answered with AI'
            }

        # Complex question indicators - these need human review
        complex_indicators = [
            'explain', 'describe in detail', 'compare', 'analyze',
            'why did', 'how does', 'what if', 'recommend',
            'suggest', 'optimize', 'improve', 'customize',
            'can you change', 'can we modify'
        ]
        if any(indicator in question_lower for indicator in complex_indicators):
            return {
                'category': 'complex',
                'should_auto_answer': False,  # Save for human review
                'use_ai': False,
                'ai_flag': False,
                'reasoning': 'Complex analytical question requiring human expertise'
            }

        # Questions with multiple parts
        if '?' in question[:-1] or (' and ' in question_lower and '?' in question):
            return {
                'category': 'complex',
                'should_auto_answer': False,
                'use_ai': False,
                'ai_flag': False,
                'reasoning': 'Multi-part question requiring comprehensive human answer'
            }

        # Default to complex for safety (human review)
        return {
            'category': 'complex',
            'should_auto_answer': False,
            'use_ai': False,
            'ai_flag': False,
            'reasoning': 'Default to human review for quality assurance'
        }

    async def is_simple_question(self, question: str) -> Tuple[bool, str]:
        """
        Determine if a question is simple enough to answer directly
        Returns: (is_simple, reason)

        DEPRECATED: Use classify_question() instead for more detailed classification
        """
        classification = await self.classify_question(question)
        is_simple = classification['category'] in ['simple', 'terms_and_conditions']
        return is_simple, classification['reasoning']

    def extract_proposal_content(self, proposal: Proposal, db: Session) -> List[Dict[str, Any]]:
        """
        Extract all content from a proposal and break it into chunks
        Returns list of chunks with metadata
        """
        chunks = []

        # Basic proposal information
        chunks.append({
            'content': f"""
Proposal Overview:
Job Number: {proposal.job_number}
Client: {proposal.client_name} ({proposal.client_company or 'N/A'})
Event Location: {proposal.event_location or 'N/A'}
Venue: {proposal.venue_name or 'N/A'}
Event Date: {proposal.start_date} to {proposal.end_date}
Status: {proposal.status}
Total Cost: ${proposal.total_cost}
Prepared by: {proposal.prepared_by or 'N/A'}
Salesperson: {proposal.salesperson or 'N/A'}
            """.strip(),
            'type': 'overview',
            'section': 'General Information',
            'metadata': {
                'job_number': proposal.job_number,
                'client': proposal.client_name
            }
        })

        # Pricing breakdown
        chunks.append({
            'content': f"""
Pricing Breakdown:
Product Subtotal: ${proposal.product_subtotal or 0}
Product Discount: ${proposal.product_discount or 0}
Product Total: ${proposal.product_total or 0}
Labor Total: ${proposal.labor_total or 0}
Service Charge: ${proposal.service_charge or 0}
Tax Amount: ${proposal.tax_amount or 0}
Grand Total: ${proposal.total_cost}
            """.strip(),
            'type': 'pricing',
            'section': 'Pricing',
            'metadata': {
                'total': float(proposal.total_cost),
                'subtotal': float(proposal.product_total or 0)
            }
        })

        # Notes
        if proposal.notes:
            chunks.append({
                'content': f"Proposal Notes:\n{proposal.notes}",
                'type': 'notes',
                'section': 'Notes',
                'metadata': {}
            })

        # Sections and Line Items
        for section in proposal.sections:
            section_content = f"Section: {section.section_name}\n"
            if section.notes:
                section_content += f"Notes: {section.notes}\n"
            section_content += f"Section Total: ${section.section_total or 0}\n\n"

            section_content += "Items:\n"
            for item in section.items:
                item_text = f"""
- {item.description}
  Item Number: {item.item_number or 'N/A'}
  Quantity: {item.quantity}
  Unit Price: ${item.unit_price}
  Discount: ${item.discount or 0}
  Subtotal: ${item.subtotal}
  Category: {item.category or 'N/A'}
                """.strip()
                if item.notes:
                    item_text += f"\n  Notes: {item.notes}"

                section_content += item_text + "\n"

                # Also create individual chunks for each item
                chunks.append({
                    'content': item_text,
                    'type': 'line_item',
                    'section': section.section_name,
                    'metadata': {
                        'item_id': str(item.id),
                        'description': item.description,
                        'quantity': item.quantity,
                        'price': float(item.unit_price)
                    }
                })

            chunks.append({
                'content': section_content,
                'type': 'section',
                'section': section.section_name,
                'metadata': {
                    'section_id': str(section.id),
                    'total': float(section.section_total or 0)
                }
            })

        # Timeline
        for timeline_item in proposal.timeline:
            timeline_content = f"""
Timeline Event: {timeline_item.title}
Date: {timeline_item.event_date}
Time: {timeline_item.start_time} - {timeline_item.end_time}
Location: {timeline_item.location or 'N/A'}
Cost: ${timeline_item.cost or 0}
            """.strip()

            if timeline_item.setup_tasks:
                timeline_content += f"\nSetup Tasks: {', '.join(timeline_item.setup_tasks)}"
            if timeline_item.equipment_needed:
                timeline_content += f"\nEquipment Needed: {', '.join(timeline_item.equipment_needed)}"
            if timeline_item.notes:
                timeline_content += f"\nNotes: {timeline_item.notes}"

            chunks.append({
                'content': timeline_content,
                'type': 'timeline',
                'section': 'Timeline',
                'metadata': {
                    'date': str(timeline_item.event_date),
                    'title': timeline_item.title
                }
            })

        # Labor
        for labor in proposal.labor:
            labor_content = f"""
Labor: {labor.task_name}
Date: {labor.labor_date}
Time: {labor.start_time} - {labor.end_time}
Quantity: {labor.quantity}
Regular Hours: {labor.regular_hours}
Overtime Hours: {labor.overtime_hours}
Double Time Hours: {labor.double_time_hours}
Hourly Rate: ${labor.hourly_rate}
Subtotal: ${labor.subtotal}
            """.strip()

            if labor.notes:
                labor_content += f"\nNotes: {labor.notes}"

            chunks.append({
                'content': labor_content,
                'type': 'labor',
                'section': 'Labor',
                'metadata': {
                    'task': labor.task_name,
                    'date': str(labor.labor_date)
                }
            })

        return chunks

    def create_vector_store(self, proposal_id: str, chunks: List[Dict[str, Any]]) -> Optional[Any]:
        """
        Create FAISS vector store from proposal chunks
        """
        if not self.embedder or not faiss:
            logger.warning("Embedder or FAISS not available")
            return None

        try:
            # Extract text content
            texts = [chunk['content'] for chunk in chunks]

            # Generate embeddings
            embeddings = self.embedder.encode(texts, convert_to_numpy=True)

            # Create FAISS index
            index = faiss.IndexFlatL2(self.embedding_dim)
            index.add(embeddings.astype('float32'))

            # Store in cache
            self.vector_stores[proposal_id] = index
            self.document_chunks[proposal_id] = chunks

            logger.info(f"Created vector store for proposal {proposal_id} with {len(chunks)} chunks")
            return index

        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            return None

    def retrieve_relevant_context(
        self,
        proposal_id: str,
        question: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant chunks for a question using semantic search
        """
        if not self.embedder or proposal_id not in self.vector_stores:
            logger.warning(f"No vector store found for proposal {proposal_id}")
            return []

        try:
            # Encode question
            question_embedding = self.embedder.encode([question], convert_to_numpy=True)

            # Search
            index = self.vector_stores[proposal_id]
            distances, indices = index.search(question_embedding.astype('float32'), top_k)

            # Get relevant chunks
            chunks = self.document_chunks[proposal_id]
            relevant_chunks = [chunks[idx] for idx in indices[0]]

            # Add relevance scores
            for chunk, distance in zip(relevant_chunks, distances[0]):
                chunk['relevance_score'] = float(distance)

            return relevant_chunks

        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    async def answer_question(
        self,
        question: str,
        proposal: Proposal,
        db: Session,
        use_rag: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a question about a proposal using RAG or direct LLM

        Returns:
        {
            'answer': str,
            'method': 'simple' | 'rag',
            'confidence': float,
            'sources': List[Dict],
            'reasoning': str
        }
        """
        if not self.client:
            return {
                'answer': "AI service is not configured. Please set ANTHROPIC_API_KEY environment variable.",
                'method': 'error',
                'confidence': 0.0,
                'sources': [],
                'reasoning': 'Missing API key'
            }

        try:
            # Check if question is simple
            is_simple, reason = await self.is_simple_question(question)

            proposal_id = str(proposal.id)
            context_chunks = []

            # If complex or RAG requested, use RAG
            if (not is_simple or use_rag):
                # Index proposal if not already done
                if proposal_id not in self.vector_stores:
                    chunks = self.extract_proposal_content(proposal, db)
                    self.create_vector_store(proposal_id, chunks)

                # Retrieve relevant context
                context_chunks = self.retrieve_relevant_context(proposal_id, question, top_k=5)

            # Build prompt
            if context_chunks:
                context_text = "\n\n---\n\n".join([
                    f"[{chunk['section']} - {chunk['type']}]\n{chunk['content']}"
                    for chunk in context_chunks
                ])

                prompt = f"""You are an expert assistant helping answer questions about a proposal/quote.

Question: {question}

Relevant context from the proposal:

{context_text}

Please provide a clear, accurate, and helpful answer based on the context provided. If the context doesn't contain enough information to fully answer the question, acknowledge this and provide the best answer you can with what's available.

Keep your answer concise but complete."""
            else:
                # Simple question without RAG
                basic_info = f"""
Proposal for {proposal.client_name}
Job Number: {proposal.job_number}
Event Date: {proposal.start_date} to {proposal.end_date}
Location: {proposal.event_location}
Total Cost: ${proposal.total_cost}
                """.strip()

                prompt = f"""You are an expert assistant helping answer questions about a proposal/quote.

Basic proposal information:
{basic_info}

Question: {question}

Please provide a brief, helpful answer. If you need more specific information from the proposal to answer accurately, mention what details would be helpful."""

            # Log the prompt being sent to AI
            logger.info("=" * 80)
            logger.info("📝 SENDING PROMPT TO AI")
            logger.info("=" * 80)
            logger.info(f"Question: {question}")
            logger.info(f"Method: {'RAG' if context_chunks else 'Simple'}")
            logger.info(f"Context chunks: {len(context_chunks) if context_chunks else 0}")
            logger.debug(f"Full prompt:\n{prompt}")
            logger.info("=" * 80)

            # Call Claude
            # Using Haiku model for better availability and lower cost
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            answer = message.content[0].text

            # Log the AI response
            logger.info("=" * 80)
            logger.info("🤖 AI GENERATED ANSWER")
            logger.info("=" * 80)
            logger.info(f"Question: {question}")
            logger.info(f"Answer: {answer}")
            logger.info(f"Model: claude-3-haiku-20240307")
            logger.info(f"Tokens used: {message.usage.input_tokens} input, {message.usage.output_tokens} output")
            logger.info("=" * 80)

            # Determine method and confidence
            method = 'rag' if context_chunks else 'simple'
            confidence = 0.9 if context_chunks else 0.7

            # Prepare sources
            sources = [
                {
                    'section': chunk['section'],
                    'type': chunk['type'],
                    'relevance': chunk.get('relevance_score', 0)
                }
                for chunk in context_chunks[:3]  # Top 3 sources
            ]

            return {
                'answer': answer,
                'method': method,
                'confidence': confidence,
                'sources': sources,
                'reasoning': reason if method == 'simple' else 'Used RAG for comprehensive answer'
            }

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'answer': f"I encountered an error while processing your question: {str(e)}",
                'method': 'error',
                'confidence': 0.0,
                'sources': [],
                'reasoning': str(e)
            }

    def clear_cache(self, proposal_id: Optional[str] = None):
        """Clear vector store cache"""
        if proposal_id:
            self.vector_stores.pop(proposal_id, None)
            self.document_chunks.pop(proposal_id, None)
        else:
            self.vector_stores.clear()
            self.document_chunks.clear()


# Global RAG service instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create global RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
