import os

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    VIDEO_OUTPUT_DIR = os.getenv("VIDEO_OUTPUT_DIR")
    ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # Default Adam voice
    UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY", "")
    EXCEL_FILE_PATH = os.path.join(VIDEO_OUTPUT_DIR, "ai_tech_news_database.xlsx")  # Use VIDEO_OUTPUT_DIR as base
    NEWS_SOURCES = [
        "https://techcrunch.com/category/artificial-intelligence/",
        "https://www.theverge.com/ai-artificial-intelligence",
        "https://venturebeat.com/ai/",
        "https://www.wired.com/tag/artificial-intelligence/",
        "https://arstechnica.com/tag/artificial-intelligence/",
        "https://www.engadget.com/tag/ai/",
        "https://www.fastcompany.com/section/artificial-intelligence",
        "https://www.technologyreview.com/topic/artificial-intelligence/",
        "https://singularityhub.com/",
        "https://artificialintelligence-news.com/",
        "https://www.aitrends.com/",
        "https://www.zdnet.com/topic/artificial-intelligence/"
    ]

