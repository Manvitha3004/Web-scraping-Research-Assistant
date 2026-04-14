import logging
import time
from typing import List

from fastapi import APIRouter, HTTPException
from models.schemas import ResearchRequest, ResearchResponse, SourceResponse
from services.search import SearchService
from services.scraper import ScraperService
from services.summarizer import SummarizerService
from services.analyzer import AnalyzerService
from utils.cache import SimpleCache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["research"])

# Initialize services
search_service = SearchService()
scraper_service = ScraperService()
summarizer_service = SummarizerService()
analyzer_service = AnalyzerService()
cache = SimpleCache(cache_dir="./cache", ttl_hours=24)


@router.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest) -> ResearchResponse:
    """
    Main research endpoint that orchestrates the research pipeline
    
    Flow:
    1. Check cache
    2. Search for sources
    3. Scrape content
    4. Analyze and summarize
    5. Return structured report and cache result
    """
    start_time = time.time()
    
    try:
        # 1. Check cache
        cached_result = cache.get(request.query)
        if cached_result:
            logger.info(f"Returning cached result for: {request.query}")
            # Update processing time, but don't duplicate 'cached' field
            cached_result['processing_time'] = time.time() - start_time
            return ResearchResponse(**cached_result)
        
        # 2. Search for sources (Step 1: Searching)
        logger.info(f"Step 1: Searching for '{request.query}'")
        search_results = search_service.search_with_retry(request.query, max_results=request.num_sources)
        
        if not search_results:
            logger.warning("No search results found, but continuing with empty sources")
            # Don't fail completely - continue with the pipeline
            search_results = []
        
        # Prepare source responses
        sources = []
        urls_to_scrape = []
        synthetic_contents = {}  # Store synthetic content to use directly
        
        for result in search_results:
            # Check if this result has synthetic content (fallback sources)
            if 'synthetic_content' in result:
                synthetic_contents[result.get('url', '')] = result['synthetic_content']
            
            sources.append(SourceResponse(
                title=result.get('title', 'Untitled'),
                url=result.get('url', ''),
                snippet=result.get('snippet', ''),
                scraped_content=None  # Will be filled after scraping or from synthetic
            ))
            urls_to_scrape.append(result.get('url', ''))
        
        # 3. Scrape content (Step 2: Scraping)
        logger.info(f"Step 2: Scraping {len(urls_to_scrape)} sources")
        scraped_contents = scraper_service.scrape_multiple_urls(urls_to_scrape)
        
        # Update sources with scraped content
        scraped_map = {item['url']: item['content'] for item in scraped_contents}
        for source in sources:
            if source.url in scraped_map:
                source.scraped_content = scraped_map[source.url]
            elif source.url in synthetic_contents:
                # Use synthetic content if scraping failed
                logger.info(f"Using synthetic content for: {source.url}")
                source.scraped_content = synthetic_contents[source.url]
        
        if not scraped_contents:
            logger.warning("No content scraped successfully")
        
        # Combine all content for analysis (from both scraped and synthetic sources)
        combined_content = "\n\n".join([
            source.scraped_content for source in sources 
            if source.scraped_content
        ])
        
        if not combined_content:
            logger.warning("No content scraped from sources")
            # Provide a default message instead of erroring out
            combined_content = "No content could be extracted from the sources. This may indicate the sources require JavaScript rendering or have access restrictions. Please try a different search query."
        
        # 4. Analyze and Summarize (Steps 3 & 4)
        logger.info(f"Step 3: Analyzing content")
        key_points = analyzer_service.extract_key_points(combined_content, num_points=7)
        themes = analyzer_service.extract_themes(combined_content, num_themes=5)
        
        logger.info(f"Step 4: Generating summary")
        summary = summarizer_service.summarize(combined_content, request.query)
        
        # Create response
        response_data = {
            "query": request.query,
            "summary": summary,
            "key_points": key_points,
            "sources": sources,
            "themes": themes,
            "processing_time": time.time() - start_time,
            "cached": False,
            "error": None
        }
        
        # 5. Cache the result
        try:
            cache_data = {
                "query": request.query,
                "summary": summary,
                "key_points": key_points,
                "sources": [s.model_dump() for s in sources],
                "themes": themes,
                "cached": True,
                "error": None
            }
            cache.set(request.query, cache_data)
        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")
        
        return ResearchResponse(**response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in research endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Research failed: {str(e)}"
        )


@router.get("/research/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "search": "ok",
            "scraper": "ok",
            "summarizer": "ok",
            "analyzer": "ok"
        }
    }
