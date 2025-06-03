from typing import List, Dict
import openai
from config import Config
import json

class NewsProcessor:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
    
    def enhance_articles(self, articles: List[Dict]) -> List[Dict]:
        """Use OpenAI to enhance article summaries and categorize"""
        enhanced_articles = []
        
        for article in articles:
            try:
                prompt = f"""
                Analyze this tech/AI news article and provide:
                1. A concise 2-sentence summary
                2. A specific category (AI Research, AI Tools, Tech Industry, Startups, etc.)
                3. Key importance score (1-10)
                4. Keywords for image search (3-5 relevant keywords)
                
                Title: {article['title']}
                Original Summary: {article['summary']}
                
                Respond in JSON format:
                {{"summary": "...", "category": "...", "importance": 8, "image_keywords": ["keyword1", "keyword2", "keyword3"]}}
                """
                
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200
                )
                
                result = json.loads(response.choices[0].message.content)
                
                enhanced_article = article.copy()
                enhanced_article.update({
                    'enhanced_summary': result['summary'],
                    'category': result['category'],
                    'importance': result['importance'],
                    'image_keywords': result.get('image_keywords', ['technology', 'artificial intelligence'])
                })
                enhanced_articles.append(enhanced_article)
                
            except Exception as e:
                print(f"Error enhancing article {article['title']}: {e}")
                # Add default values for failed enhancements
                enhanced_article = article.copy()
                enhanced_article.update({
                    'enhanced_summary': article['summary'],
                    'category': article['category'],
                    'importance': 5,
                    'image_keywords': ['technology', 'artificial intelligence']
                })
                enhanced_articles.append(enhanced_article)
        
        return enhanced_articles
