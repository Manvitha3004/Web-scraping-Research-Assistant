import logging
import re
from typing import List, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class AnalyzerService:
    """Service for analyzing and extracting key information from content"""

    def __init__(self):
        """Initialize analyzer"""
        self.stop_words = self._get_stop_words()

    @staticmethod
    def _get_stop_words() -> set:
        """Get common English stop words"""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
            'every', 'both', 'few', 'more', 'most', 'some', 'such', 'no', 'nor',
            'not', 'only', 'same', 'as', 'if', 'than', 'so', 'as', 'just', 'now',
            'also', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'then',
            'there', 'here', 'about', 'up', 'out', 'off', 'over', 'under', 'again',
            'further', 'them', 'him', 'her', 'itself', 'ourselves', 'yourselves',
        }

    def extract_key_points(self, combined_content: str, num_points: int = 7) -> List[str]:
        """
        Extract key bullet points from content
        
        Args:
            combined_content: Combined content from all sources
            num_points: Number of key points to extract
            
        Returns:
            List of key points
        """
        try:
            # Split into sentences
            sentences = re.split(r'[.!?]+', combined_content)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            # Score sentences based on keyword frequency
            sentence_scores = {}
            for i, sentence in enumerate(sentences[:100]):  # Limit to first 100 sentences
                words = re.findall(r'\w+', sentence.lower())
                score = sum(1 for word in words if word not in self.stop_words and len(word) > 3)
                sentence_scores[sentence] = score
            
            # Get top sentences
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_points]
            key_points = [sentence.strip() for sentence, _ in top_sentences]
            
            return key_points if key_points else ["No key points extracted"]
        
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return ["Unable to extract key points"]

    def extract_themes(self, combined_content: str, num_themes: int = 5) -> List[str]:
        """
        Extract recurring themes and keywords from content
        
        Args:
            combined_content: Combined content
            num_themes: Number of themes to extract
            
        Returns:
            List of theme tags
        """
        try:
            # Extract words
            words = re.findall(r'\b\w+\b', combined_content.lower())
            
            # Filter stop words and short words
            filtered_words = [w for w in words if w not in self.stop_words and len(w) > 4]
            
            # Count frequency
            word_freq = Counter(filtered_words)
            
            # Get top themes
            themes = [word for word, _ in word_freq.most_common(num_themes)]
            
            return themes if themes else ["research", "information", "content"]
        
        except Exception as e:
            logger.error(f"Error extracting themes: {e}")
            return ["research", "information"]

    def get_content_stats(self, content_pieces: list) -> dict:
        """
        Calculate statistics about the content
        
        Args:
            content_pieces: List of content pieces (dictionaries with 'content')
            
        Returns:
            Dictionary with statistics
        """
        try:
            total_sources = len(content_pieces)
            total_words = sum(len(piece.get('content', '').split()) for piece in content_pieces)
            total_chars = sum(len(piece.get('content', '')) for piece in content_pieces)
            
            avg_content_length = total_chars // max(total_sources, 1)
            
            return {
                'total_sources': total_sources,
                'total_words': total_words,
                'total_characters': total_chars,
                'average_content_length': avg_content_length
            }
        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
            return {'error': str(e)}

    def analyze_sentiment_basic(self, text: str) -> str:
        """
        Basic sentiment analysis (without external libraries)
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment: 'positive', 'negative', or 'neutral'
        """
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'excellent', 'perfect', 'love', 'best', 'brilliant', 'outstanding',
            'success', 'successful', 'improve', 'benefit', 'happy', 'pleased'
        }
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'poor', 'worst', 'hate',
            'fail', 'failed', 'failure', 'problem', 'issue', 'error', 'danger',
            'dangerous', 'sad', 'unhappy', 'unfortunate', 'difficult', 'hard'
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        pos_count = sum(1 for w in words if w in positive_words)
        neg_count = sum(1 for w in words if w in negative_words)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'
