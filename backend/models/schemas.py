from pydantic import BaseModel
from typing import List, Optional


class ResearchRequest(BaseModel):
    """Request model for research endpoint"""
    query: str
    num_sources: int = 5


class SourceResponse(BaseModel):
    """Response model for individual source"""
    title: str
    url: str
    snippet: str
    scraped_content: Optional[str] = None


class ResearchResponse(BaseModel):
    """Response model for research endpoint"""
    query: str
    summary: str
    key_points: List[str]
    sources: List[SourceResponse]
    themes: List[str]
    processing_time: float
    cached: bool = False
    error: Optional[str] = None
