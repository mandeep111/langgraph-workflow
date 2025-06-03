from news_processor import NewsProcessor
from excel_generator import ExcelGenerator
from script_generator import ScriptGenerator
from audio_generator import AudioGenerator
from video_generator import VideoGenerator
from config import Config
from news import NewsState
from news_scrapper import NewsScrapper
import asyncio

from langgraph.graph import StateGraph, END

# LangGraph workflow nodes
def scrape_news_node(state: NewsState) -> NewsState:
    """Scrape news from various sources"""
    scraper = NewsScrapper()
    all_articles = []
    
    # Scrape TechCrunch
    all_articles.extend(scraper.scrape_techcrunch_ai())
    
    # Scrape other sources
    sources = [
        ("https://www.theverge.com/ai-artificial-intelligence", "The Verge"),
        ("https://venturebeat.com/ai/", "VentureBeat")
    ]
    
    for url, name in sources:
        all_articles.extend(scraper.scrape_generic_tech_news(url, name))
    
    state["raw_articles"] = all_articles
    return state

def process_articles_node(state: NewsState) -> NewsState:
    """Process and enhance articles using AI"""
    processor = NewsProcessor()
    enhanced_articles = processor.enhance_articles(state["raw_articles"])
    state["processed_articles"] = enhanced_articles
    return state

def create_excel_node(state: NewsState) -> NewsState:
    """Create Excel report"""
    excel_gen = ExcelGenerator()
    excel_path = excel_gen.create_or_update_excel_report(state["processed_articles"])
    state["excel_path"] = excel_path
    return state

def generate_script_node(state: NewsState) -> NewsState:
    """Generate YouTube script"""
    script_gen = ScriptGenerator()
    script = script_gen.generate_youtube_shorts_script(state["processed_articles"])
    state["script_content"] = script
    return state

def generate_audio_node(state: NewsState) -> NewsState:
    """Generate audio from script"""
    audio_gen = AudioGenerator()
    audio_path = audio_gen.generate_audio(state["script_content"])
    state["audio_path"] = audio_path
    return state

def generate_video_node(state: NewsState) -> NewsState:
    """Generate YouTube Shorts video with audio"""
    video_gen = VideoGenerator()
    video_path = video_gen.create_youtube_shorts_video(state["script_content"], state["audio_path"])
    state["video_path"] = video_path
    return state

# Create the LangGraph workflow
def create_workflow():
    """Create the complete workflow"""
    workflow = StateGraph(NewsState)
    
    # Add nodes
    workflow.add_node("scrape", scrape_news_node)
    workflow.add_node("process", process_articles_node)
    workflow.add_node("excel", create_excel_node)
    workflow.add_node("script", generate_script_node)
    workflow.add_node("audio", generate_audio_node)
    workflow.add_node("video", generate_video_node)
    
    # Define edges
    workflow.add_edge("scrape", "process")
    workflow.add_edge("process", "excel")
    workflow.add_edge("excel", "script")
    workflow.add_edge("script", "audio")
    workflow.add_edge("audio", "video")
    workflow.add_edge("video", END)
    
    # Set entry point
    workflow.set_entry_point("scrape")
    
    return workflow.compile()

# Alternative main function without LangGraph (if needed)
def run_simple_pipeline():
    """Run pipeline without LangGraph"""
    print("🚀 Starting AI News Automation Pipeline (Simple Mode)...")
    
    state = {
        "raw_articles": [],
        "processed_articles": [],
        "excel_path": "",
        "script_content": "",
        "audio_path": "",
        "video_path": "",
        "error_messages": []
    }
    
    try:
        # Step 1: Scrape news
        print("📰 Scraping news...")
        state = scrape_news_node(state)
        print(f"Found {len(state['raw_articles'])} articles")
        
        # Step 2: Process articles
        print("🤖 Processing with AI...")
        state = process_articles_node(state)
        
        # Step 3: Create Excel
        print("📊 Creating Excel report...")
        state = create_excel_node(state)
        
        # Step 4: Generate script
        print("📝 Generating YouTube script...")
        state = generate_script_node(state)
        
        # Step 5: Generate audio
        print("🎵 Generating audio...")
        state = generate_audio_node(state)
        
        # Step 6: Generate video
        print("🎥 Creating video...")
        state = generate_video_node(state)
        
        print("\n✅ Pipeline completed successfully!")
        print(f"📊 Excel Report: {state.get('excel_path', 'Not created')}")
        print(f"🎵 Audio: {state.get('audio_path', 'Not created')}")
        print(f"🎥 Video: {state.get('video_path', 'Not created')}")
        
        return state
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        return None

# Main execution function with LangGraph
async def main():
    """Run the complete pipeline with LangGraph"""
    print("🚀 Starting AI News Automation Pipeline...")
    
    # Initialize state
    initial_state: NewsState = {
        "raw_articles": [],
        "processed_articles": [],
        "excel_path": "",
        "script_content": "",
        "audio_path": "",
        "video_path": "",
        "error_messages": []
    }
    
    try:
        # Create and run workflow
        app = create_workflow()
        final_state = app.invoke(initial_state)
        
        print("\n✅ Pipeline completed successfully!")
        print(f"📊 Excel Report: {final_state.get('excel_path', 'Not created')}")
        print(f"📝 Script: Generated")
        print(f"🎵 Audio: {final_state.get('audio_path', 'Not created')}")
        print(f"🎥 Video: {final_state.get('video_path', 'Not created')}")
        
        # Print script preview
        if final_state.get('script_content'):
            print(f"\n📝 Script Preview:\n{final_state['script_content'][:300]}...")
            
        return final_state
        
    except Exception as e:
        print(f"❌ LangGraph pipeline failed: {e}")
        print("🔄 Falling back to simple pipeline...")
        return run_simple_pipeline()

# Setup instructions
def print_setup_instructions():
    """Print setup instructions"""
    print("""
    🔧 SETUP INSTRUCTIONS:
    
    1. Install required packages:
       pip install langgraph openai pandas openpyxl beautifulsoup4 requests
       
       # For ElevenLabs (optional):
       pip install elevenlabs
    
    2. Set environment variables:
       export OPENAI_API_KEY="your-openai-key"
       export ELEVENLABS_API_KEY="your-elevenlabs-key"  # Optional
    
    3. Install FFmpeg for video generation:
       - Windows: Download from https://ffmpeg.org/
       - Mac: brew install ffmpeg
       - Linux: sudo apt install ffmpeg
    
    4. Run the pipeline:
       python news_pipeline.py
    
    📋 Features:
    - Scrapes latest AI/Tech news from multiple sources
    - Uses GPT to enhance and categorize articles
    - Creates formatted Excel report
    - Generates YouTube script
    - Creates audio narration (ElevenLabs or system TTS)
    - Produces simple video with FFmpeg
    
    🎯 Outputs:
    - Excel file with organized news
    - YouTube script text file
    - MP3/AIFF audio file
    - MP4 video file
    
    📝 Notes:
    - ElevenLabs is optional - will use system TTS if not available
    - Requires OpenAI API key for article processing and script generation
    - FFmpeg needed for video creation
    """)

if __name__ == "__main__":
    print_setup_instructions()
    
    # Check if required API keys are set
    if not Config.OPENAI_API_KEY:
        print("⚠️  Please set OPENAI_API_KEY environment variable")
    if not Config.ELEVENLABS_API_KEY:
        print("⚠️  Please set ELEVENLABS_API_KEY environment variable")
    
    if Config.OPENAI_API_KEY:
        try:
            # Try LangGraph version first
            asyncio.run(main())
        except ImportError as e:
            print(f"⚠️  LangGraph import issue: {e}")
            print("🔄 Running simple pipeline instead...")
            run_simple_pipeline()
    else:
        print("❌ Cannot run without required API keys")