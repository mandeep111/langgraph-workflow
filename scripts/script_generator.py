import openai
from datetime import datetime
from typing import List, Dict
from config import Config
import re
import os

class ScriptGenerator:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.output_dir = Config.VIDEO_OUTPUT_DIR
        if not self.output_dir:
            self.output_dir = os.path.join(os.getcwd(), 'output_videos')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_youtube_shorts_script(self, articles: List[Dict]) -> str:
        """Generate YouTube Shorts script from articles (optimized for 9:16 vertical format)"""
        # Get fresh articles and sort by importance/recency
        current_time = datetime.now()
        top_articles = sorted(articles, key=lambda x: x.get('importance', 5), reverse=True)[:4]
        
        articles_text = "\n".join([
            f"- {article['title']}: {article.get('enhanced_summary', article['summary'])}"
            for article in top_articles
        ])
        
        prompt = f"""
        Create a 45-60 second YouTube Shorts script for "AI News Update" covering these breaking stories:
        
        {articles_text}
        
        Requirements for YouTube Shorts (9:16 vertical format):
        - Hook viewers in first 3 seconds with shocking/intriguing opener
        - Fast-paced, energetic delivery 
        - Use short, punchy sentences
        - Include trending phrases like "You won't believe this", "This changes everything"
        - Add engagement triggers: "Wait for it", "But here's the crazy part"
        - Visual cues: [PAUSE] for text changes, [EMPHASIS] for key points
        - End with strong CTA: "Follow for daily AI updates!"
        - Keep each segment under 15 words for readability
        - Current timestamp: {current_time.strftime('%B %d, %Y at %I:%M %p')}
        
        IMPORTANT: Write ONLY the narration text. Do NOT include:
        - Stage directions like [OPENING SCENE], [HOST], [SCENE], etc.
        - Character names or roles
        - Camera directions
        - Just pure spoken content that will be read aloud
        
        Make it feel urgent and fresh - like breaking news happening RIGHT NOW.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.8  # Higher creativity for engaging content
        )
        
        script = response.choices[0].message.content
        
        # Clean up any remaining stage directions that might have slipped through
        script = self._clean_script_for_audio(script)
        
        # Save script with timestamp to ensure uniqueness
        script_filename = os.path.join(self.output_dir, f"youtube_shorts_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(script_filename, 'w', encoding='utf-8') as f:
            f.write(f"Generated at: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            f.write(script)
        
        print(f"YouTube Shorts script generated: {script_filename}")
        return script
        
        # Clean up any remaining stage directions that might have slipped through
        script = self._clean_script_for_audio(script)
        
        # Save script with timestamp to ensure uniqueness
        script_filename = os.path.join(self.output_dir, f"youtube_shorts_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(script_filename, 'w', encoding='utf-8') as f:
            f.write(f"Generated at: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            f.write(script)
        
        print(f"YouTube Shorts script generated: {script_filename}")
        return script
        
   
    
    def _clean_script_for_audio(self, script: str) -> str:
        """Clean script by removing stage directions and formatting for audio"""
        # Remove common stage directions and formatting
        patterns_to_remove = [
            r'\[.*?\]',  # Remove anything in square brackets
            r'\(.*?\)',  # Remove anything in parentheses that looks like stage directions
            r'HOST:',    # Remove "HOST:" labels
            r'NARRATOR:',  # Remove "NARRATOR:" labels
            r'VOICE.*?:',  # Remove "VOICE OVER:" type labels
            r'SCENE \d+:',  # Remove "SCENE 1:" type labels
            r'OPENING SCENE:',  # Remove "OPENING SCENE:"
            r'CLOSING:',  # Remove "CLOSING:"
        ]
        
        cleaned_script = script
        for pattern in patterns_to_remove:
            cleaned_script = re.sub(pattern, '', cleaned_script, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and line breaks
        cleaned_script = re.sub(r'\n\s*\n', '\n', cleaned_script)  # Remove multiple line breaks
        cleaned_script = re.sub(r'^\s+', '', cleaned_script, flags=re.MULTILINE)  # Remove leading whitespace
        cleaned_script = cleaned_script.strip()
        
        return cleaned_script
