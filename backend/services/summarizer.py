import logging
import os
from typing import Optional
from groq import Groq
from utils.cleaner import TextCleaner

logger = logging.getLogger(__name__)


class SummarizerService:
    """Service for summarizing content using Groq API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize summarizer
        
        Args:
            api_key: Groq API key (or set via GROQ_API_KEY env variable)
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set. Summarization will use fallback methods")
        else:
            logger.info(f"Groq API key loaded: {self.api_key[:10]}...")
        
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def summarize_with_groq(self, combined_content: str, query: str) -> Optional[str]:
        """
        Summarize content using Groq API
        
        Args:
            combined_content: Combined scraped content from all sources
            query: Original research query
            
        Returns:
            Summarized text or None if failed
        """
        if not self.client:
            logger.warning("Groq client not initialized")
            return None
        
        try:
            logger.info("Generating summary using Groq API...")
            
            # Clean content before sending to Groq - remove Wikipedia markup and excess whitespace
            cleaned_content = TextCleaner.clean_wikipedia_markup(combined_content)
            cleaned_content = TextCleaner.clean_html_text(cleaned_content)
            cleaned_content = TextCleaner.truncate_text(cleaned_content, max_length=4000)
            
            logger.debug(f"Cleaned content length: {len(cleaned_content)} chars (from {len(combined_content)})")
            
            # Check if content has actual information or is just placeholder
            is_placeholder = len(cleaned_content) < 200 or ("research on" in cleaned_content.lower() and "continues to evolve" in cleaned_content.lower())
            
            if is_placeholder:
                # For placeholder content, answer the question directly
                prompt = f"""You are a knowledgeable research assistant. Answer the following question comprehensively and accurately:

Question: {query}

Provide a detailed, informative answer with 3-5 clear paragraphs covering:
1. Direct answer to the question
2. Key facts and details
3. Important context and implications
4. Any relevant considerations

Please provide a professional, well-researched response."""
            else:
                # For real content, generate answer based on content + query
                prompt = f"""You are a research assistant. Based ONLY on the following source content, answer this specific question in 3-5 clear paragraphs:

Question: {query}

Content to base your answer on:
{cleaned_content}

Instructions:
1. Directly address the question
2. Use only information from the provided content
3. Explain key concepts clearly
4. Provide relevant context and implications
5. Write in a professional, coherent manner

Answer:"""

            logger.debug(f"Prompt being sent to Groq (first 300 chars): {prompt[:300]}...")
            
            message = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            
            summary = message.choices[0].message.content
            logger.info(f"Summary generated successfully by Groq (length: {len(summary)} chars)")
            logger.debug(f"Groq response (first 300 chars): {summary[:300]}...")
            return summary
        
        except Exception as e:
            logger.error(f"Error with Groq summarization: {type(e).__name__}: {str(e)}")
            logger.error(f"API Key configured: {bool(self.api_key)}")
            if self.api_key:
                logger.error(f"API Key prefix: {self.api_key[:10]}...")
            return None

    def summarize_fallback_simple(self, combined_content: str, query: str = "") -> str:
        """
        Simple fallback summarization - extract key sentences or generate answer based on query
        
        Args:
            combined_content: Combined content
            query: Original query for context
            
        Returns:
            Simple summary or answer
        """
        # If no content, generate an answer based on the query
        if not combined_content or len(combined_content.strip()) < 50:
            return f"""Based on research about "{query}":

This is a topic that involves multiple dimensions and aspects. While comprehensive web content retrieval was limited, 
the subject of {query} is well-documented across various sources and represents an established area of knowledge.

Key aspects to consider include various technical, practical, and theoretical dimensions. 
Most sources recommend consulting specialized resources and expert documentation for in-depth understanding.

For the most current and detailed information about {query}, I recommend:
- Checking dedicated specialist resources and documentation
- Reviewing peer-reviewed research and academic papers
- Consulting industry-specific knowledge bases
- Exploring multiple authoritative sources on the topic"""
        
        try:
            import nltk
            from nltk.tokenize import sent_tokenize
            
            # Download required NLTK data
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            
            sentences = sent_tokenize(combined_content)
            
            if not sentences:
                return f"""Regarding "{query}":

The topic encompasses various aspects of practical and theoretical importance. 
Research and documentation on {query} is available through multiple sources, each providing different perspectives 
and levels of detail on various dimensions of the subject."""
            
            # Select key sentences (first few and distributed)
            if len(sentences) > 10:
                key_sentences = sentences[:3] + sentences[len(sentences)//2:len(sentences)//2+2] + sentences[-2:]
            elif len(sentences) > 3:
                key_sentences = sentences
            else:
                # Very few sentences - use them all
                key_sentences = sentences
            
            summary = ' '.join(key_sentences).strip()
            
            if not summary:
                return f"""Regarding the query about "{query}":

The topic is documented and researched across various platforms and sources. 
Understanding this subject requires exploring multiple perspectives and authoritative resources."""
            
            return summary
        
        except Exception as e:
            logger.error(f"Error in fallback summarization: {e}")
            # Last resort: return informative response
            return f"""Regarding your question about "{query}":

This is a recognized area of study with information available across multiple sources. 
The topic involves several interconnected concepts and considerations. 

To get the most comprehensive answer, consulting specialized sources in this field is recommended."""

    def summarize(self, combined_content: str, query: str = "") -> str:
        """
        Summarize content with primary and fallback methods
        
        Args:
            combined_content: Combined content to summarize
            query: Original query for context
            
        Returns:
            Generated summary
        """
        if not combined_content or len(combined_content.strip()) < 50:
            # No content - return query-based summary
            return self.summarize_fallback_simple("", query)
        
        # Try Groq first
        if self.client:
            try:
                summary = self.summarize_with_groq(combined_content, query)
                if summary:
                    return summary
            except Exception as e:
                logger.warning(f"Groq summarization failed, trying fallback: {e}")
        
        # Fallback to simple method
        logger.info("Using fallback summarization method...")
        return self.summarize_fallback_simple(combined_content, query)
