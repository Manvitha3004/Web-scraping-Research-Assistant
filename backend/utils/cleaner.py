import re
import html
from typing import Optional


class TextCleaner:
    """Utility class for cleaning and normalizing extracted text"""

    @staticmethod
    def clean_html_text(text: str) -> str:
        """Clean HTML-decoded text and remove unnecessary whitespace"""
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common navigation patterns
        text = re.sub(r'(skip to|navigate to|menu|home|about|contact|follow us)', '', text, flags=re.IGNORECASE)
        
        # Remove common footer patterns
        text = re.sub(r'(©|copyright|all rights reserved|terms of|privacy|cookies)', '', text, flags=re.IGNORECASE)
        
        return text.strip()

    @staticmethod
    def truncate_text(text: str, max_length: int = 3000) -> str:
        """Truncate text to max length while preserving word boundaries"""
        if len(text) <= max_length:
            return text
        
        # Find the last space before max_length to avoid cutting words
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            return truncated[:last_space] + "..."
        
        return truncated + "..."

    @staticmethod
    def extract_sentences(text: str, num_sentences: int = 10) -> str:
        """Extract first N sentences from text"""
        sentence_pattern = r'[^.!?]*[.!?]+'
        sentences = re.findall(sentence_pattern, text)[:num_sentences]
        return ' '.join(s.strip() for s in sentences)

    @staticmethod
    def remove_special_chars(text: str) -> str:
        """Remove special characters but keep alphanumeric and basic punctuation"""
        text = re.sub(r'[^a-zA-Z0-9\s\.\!\?\-\,\:\;]', '', text)
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize all whitespace to single spaces"""
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def clean_wikipedia_markup(text: str) -> str:
        """
        Remove Wikipedia-specific markup and formatting
        Handles: ==headings==, [[links]], {{templates}}, etc.
        """
        # Remove Wikipedia section headers (== Header ==)
        text = re.sub(r'={2,}\s*.*?\s*={2,}', '', text)
        
        # Remove Wikipedia links [[link]]
        text = re.sub(r'\[\[([^\]|]*)\]\]', r'\1', text)
        
        # Remove templates {{...}}
        text = re.sub(r'\{\{[^}]*\}\}', '', text)
        
        # Remove citation markup [citation needed], <ref>, etc.
        text = re.sub(r'\[citation needed\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'</?[a-z]+[^>]*>', '', text, flags=re.IGNORECASE)
        
        # Remove bold/italic markup
        text = re.sub(r"'''(.*?)'''", r'\1', text)  # Bold
        text = re.sub(r"''(.*?)''", r'\1', text)   # Italic
        
        # Normalize whitespace after cleanup
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
