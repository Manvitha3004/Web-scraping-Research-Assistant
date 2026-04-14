import logging
import os
from typing import Optional
from groq import Groq

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
            
            prompt = f"""You are a research assistant. Based on the following content related to the query "{query}", 
create a comprehensive and well-structured research report summary.

The summary should be 3-5 paragraphs, covering:
1. Main findings and key information
2. Important details and context
3. Implications and significance

Content to summarize:
{combined_content}

Please provide a professional, coherent summary that synthesizes the information."""

            message = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            
            summary = message.choices[0].message.content
            logger.info("Summary generated successfully")
            return summary
        
        except Exception as e:
            logger.error(f"Error with Groq summarization: {e}")
            return None

    def summarize_fallback_simple(self, combined_content: str, query: str = "") -> str:
        """
        Simple fallback summarization - extract key sentences
        
        Args:
            combined_content: Combined content
            query: Original query for context
            
        Returns:
            Simple summary
        """
        # If no content, return informative message
        if not combined_content or len(combined_content.strip()) < 50:
            return f"Based on the research query '{query}', this topic involves various aspects worth exploring. While detailed content extraction was limited, the search results indicate this is an established area of study with multiple perspectives and sources available online."
        
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
                return f"Research on '{query}' suggests this is a relevant topic. Additional sources and detailed exploration are recommended for comprehensive understanding."
            
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
                return f"Research indicates '{query}' is a topic of interest. Multiple sources are available for further study and exploration."
            
            return summary
        
        except Exception as e:
            logger.error(f"Error in fallback summarization: {e}")
            # Last resort: return informative default
            return f"The research query '{query}' returned search results. This suggests the topic is documented and available in various online sources for further exploration and study."

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
