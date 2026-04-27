import logging
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)


class RelevanceFilter:
    """Filter content based on semantic and keyword relevance to the query"""

    def __init__(self):
        """Initialize the relevance filter"""
        self.stop_words = self._get_stop_words()

    @staticmethod
    def _get_stop_words() -> set:
        """Common English stop words"""
        return {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for',
            'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'or',
            'that', 'the', 'to', 'was', 'will', 'with', 'this', 'if', 'have',
            'had', 'do', 'does', 'did', 'you', 'i', 'they', 'we', 'what',
            'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
            'every', 'both', 'can', 'could', 'should', 'would', 'may', 'might'
        }

    def _extract_keywords(self, text: str) -> set:
        """Extract meaningful keywords from text"""
        # Remove extra whitespace and convert to lowercase
        text = text.lower()
        # Remove special characters but keep spaces and alphanumeric
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Split into words
        words = text.split()
        # Filter out stop words and short words
        keywords = {word for word in words if word not in self.stop_words and len(word) > 2}
        return keywords

    def calculate_relevance_score(self, content: str, query: str) -> float:
        """
        Calculate relevance score between content and query (0-1)
        
        Args:
            content: Content to evaluate
            query: Query to match against
            
        Returns:
            Relevance score (0.0 = not relevant, 1.0 = highly relevant)
        """
        if not content or not query:
            return 0.0

        query_keywords = self._extract_keywords(query)
        content_keywords = self._extract_keywords(content)

        if not query_keywords or not content_keywords:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(query_keywords.intersection(content_keywords))
        union = len(query_keywords.union(content_keywords))

        if union == 0:
            return 0.0

        similarity = intersection / union
        return similarity

    def filter_sources(self, sources: List[Dict], query: str, min_relevance: float = 0.15) -> List[Dict]:
        """
        Filter sources based on relevance to query
        
        Args:
            sources: List of source dictionaries
            query: Query to match against
            min_relevance: Minimum relevance threshold (0-1)
            
        Returns:
            Filtered list of relevant sources
        """
        filtered = []

        for source in sources:
            title = source.get('title', '')
            snippet = source.get('snippet', '')
            content = source.get('scraped_content', '') or source.get('synthetic_content', '')

            # Combine all text for relevance check
            full_text = f"{title} {snippet} {content}"

            # Calculate relevance score
            score = self.calculate_relevance_score(full_text, query)

            if score >= min_relevance:
                source['relevance_score'] = score
                filtered.append(source)
                logger.info(f"Source kept: {title[:50]}... (relevance: {score:.2f})")
            else:
                logger.info(f"Source filtered: {title[:50]}... (relevance: {score:.2f} < {min_relevance})")

        return filtered

    def filter_key_points(self, key_points: List[str], query: str, min_relevance: float = 0.15) -> List[str]:
        """
        Filter key points based on relevance to query
        
        Args:
            key_points: List of key points
            query: Query to match against
            min_relevance: Minimum relevance threshold
            
        Returns:
            Filtered list of relevant key points
        """
        filtered = []

        for point in key_points:
            score = self.calculate_relevance_score(point, query)

            if score >= min_relevance:
                filtered.append(point)
                logger.info(f"Key point kept (relevance: {score:.2f}): {point[:50]}...")
            else:
                logger.info(f"Key point filtered (relevance: {score:.2f}): {point[:50]}...")

        # If all filtered out, keep the most relevant ones
        if not filtered and key_points:
            logger.warning("All key points filtered, keeping highest relevance ones")
            scored_points = [
                (point, self.calculate_relevance_score(point, query))
                for point in key_points
            ]
            scored_points.sort(key=lambda x: x[1], reverse=True)
            filtered = [point for point, _ in scored_points[:3]]

        return filtered

    def filter_themes(self, themes: List[str], query: str, min_relevance: float = 0.1) -> List[str]:
        """
        Filter themes based on relevance to query
        
        Args:
            themes: List of theme tags
            query: Query to match against
            min_relevance: Minimum relevance threshold
            
        Returns:
            Filtered list of relevant themes
        """
        filtered = []

        for theme in themes:
            score = self.calculate_relevance_score(theme, query)

            if score >= min_relevance:
                filtered.append(theme)
                logger.info(f"Theme kept (relevance: {score:.2f}): {theme}")
            else:
                logger.info(f"Theme filtered (relevance: {score:.2f}): {theme}")

        # If all filtered out, keep all original themes
        if not filtered:
            logger.warning("All themes filtered, keeping original list")
            filtered = themes

        return filtered

    def filter_content(self, combined_content: str, query: str, max_chars: int = 8000) -> str:
        """
        Filter and trim content for relevance
        
        Args:
            combined_content: Combined content from all sources
            query: Query to match against
            max_chars: Maximum characters to keep
            
        Returns:
            Filtered content
        """
        if not combined_content:
            return combined_content

        # Split into sentences
        sentences = re.split(r'[.!?]+', combined_content)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Score each sentence
        scored_sentences = []
        for sentence in sentences:
            score = self.calculate_relevance_score(sentence, query)
            if score > 0:
                scored_sentences.append((sentence, score))

        # Sort by relevance score (descending)
        scored_sentences.sort(key=lambda x: x[1], reverse=True)

        # Keep most relevant sentences until max_chars
        filtered_sentences = []
        total_length = 0

        for sentence, score in scored_sentences:
            sentence_length = len(sentence) + 2  # +2 for punctuation and space
            if total_length + sentence_length <= max_chars:
                filtered_sentences.append(sentence)
                total_length += sentence_length
            else:
                break

        # Reconstruct content maintaining some order (take at least first few relevant ones)
        filtered_content = '. '.join(filtered_sentences[:10])

        logger.info(f"Content filtered: {len(combined_content)} → {len(filtered_content)} chars")
        return filtered_content
