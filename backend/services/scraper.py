import logging
import time
from typing import Optional, Dict
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from utils.cleaner import TextCleaner

logger = logging.getLogger(__name__)

# Common browser user agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]


class ScraperService:
    """Service for scraping web content"""

    def __init__(self, timeout: int = 10, max_content_length: int = 3000):
        """
        Initialize scraper
        
        Args:
            timeout: Request timeout in seconds
            max_content_length: Maximum content length to extract per source
        """
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.user_agent_index = 0
        self.robots_parsers = {}

    def _get_user_agent(self) -> str:
        """Get next user agent from rotation list"""
        agent = USER_AGENTS[self.user_agent_index % len(USER_AGENTS)]
        self.user_agent_index += 1
        return agent

    def _can_fetch(self, url: str) -> bool:
        """Check robots.txt permissions"""
        try:
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            if domain not in self.robots_parsers:
                rp = RobotFileParser()
                rp.set_url(f"{domain}/robots.txt")
                rp.read()
                self.robots_parsers[domain] = rp
            
            return self.robots_parsers[domain].can_fetch("*", url)
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            # Default to allowing if we can't check
            return True

    def _scrape_wikipedia(self, url: str) -> Optional[Dict[str, str]]:
        """
        Special handler for Wikipedia URLs - uses API instead of scraping
        This bypasses robots.txt restrictions
        """
        try:
            # Extract article title from Wikipedia URL
            # URL format: https://en.wikipedia.org/wiki/Article_Title
            from urllib.parse import unquote
            title = unquote(url.split('/wiki/')[-1])
            
            logger.info(f"Fetching Wikipedia article via API: {title}")
            
            # Use Wikipedia Extract API
            params = {
                'action': 'query',
                'prop': 'extracts',
                'explaintext': True,
                'titles': title,
                'format': 'json'
            }
            
            response = requests.get(
                'https://en.wikipedia.org/w/api.php',
                params=params,
                timeout=10,
                headers={'User-Agent': 'ResearchAssistant/1.0'}
            )
            response.raise_for_status()
            
            pages = response.json().get('query', {}).get('pages', {})
            if not pages:
                logger.warning(f"Wikipedia article not found: {title}")
                return None
            
            page = list(pages.values())[0]
            extract = page.get('extract', '')
            
            if not extract:
                logger.warning(f"No content in Wikipedia extract: {title}")
                return None
            
            # Truncate to max content length
            extract = TextCleaner.truncate_text(extract, self.max_content_length)
            
            return {
                'title': title,
                'content': extract,
                'url': url
            }
        
        except Exception as e:
            logger.error(f"Error fetching Wikipedia article: {e}")
            return None

    def scrape_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape content from a URL
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with 'title' and 'content' or None if failed
        """
        try:
            # Special handling for Wikipedia URLs - use API instead of scraping
            if 'wikipedia.org' in url.lower():
                return self._scrape_wikipedia(url)
            
            # Check robots.txt for non-Wikipedia URLs
            if not self._can_fetch(url):
                logger.info(f"robots.txt disallows scraping: {url}")
                return None
            
            # Skip PDFs and non-HTML content
            if url.lower().endswith('.pdf'):
                logger.info(f"Skipping PDF: {url}")
                return None
            
            headers = {
                'User-Agent': self._get_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            logger.info(f"Scraping: {url}")
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logger.info(f"Skipping non-HTML content: {url}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else url
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'noscript']):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean the text
            text = TextCleaner.clean_html_text(text)
            text = TextCleaner.truncate_text(text, self.max_content_length)
            
            if not text:
                logger.warning(f"No content extracted from: {url}")
                return None
            
            return {
                'title': str(title).strip(),
                'content': text,
                'url': url
            }
        
        except requests.Timeout:
            logger.warning(f"Timeout scraping {url}")
            return None
        except requests.RequestException as e:
            logger.warning(f"Error scraping {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return None

    def scrape_multiple_urls(self, urls: list) -> list:
        """
        Scrape multiple URLs with error handling
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of successfully scraped content
        """
        results = []
        for url in urls:
            try:
                content = self.scrape_url(url)
                if content:
                    results.append(content)
                # Add small delay between requests
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue
        
        return results
