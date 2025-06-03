from dataclasses import dataclass
from typing import List, Dict, Any, TypedDict

# State definition for LangGraph
class NewsState(TypedDict):
    raw_articles: List[Dict[str, Any]]
    processed_articles: List[Dict[str, Any]]
    images: List[Dict[str, Any]]
    excel_path: str
    script_content: str
    audio_path: str
    video_path: str
    error_messages: List[str]

@dataclass
class NewsArticle:
    title: str
    summary: str
    url: str
    source: str
    date: str
    category: str
