from typing import List, Dict
import requests
from config import Config
from bs4 import BeautifulSoup
from datetime import datetime
import random

class NewsScrapper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_techcrunch_ai(self) -> List[Dict]:
        """Scrape TechCrunch AI articles"""
        try:
            response = self.session.get(Config.NEWS_SOURCES[0])
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            for article in soup.find_all('article', limit=5):
                title_elem = article.find('h2') or article.find('h3')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link_elem = title_elem.find('a') or article.find('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    
                    # Get summary from first paragraph
                    summary_elem = article.find('p')
                    summary = summary_elem.get_text(strip=True)[:200] + '...' if summary_elem else ''
                    
                    articles.append({
                        'title': title,
                        'summary': summary,
                        'url': url,
                        'source': 'TechCrunch',
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'category': 'AI'
                    })
            
            return articles
        except Exception as e:
            print(f"Error scraping TechCrunch: {e}")
            return []
    
    def scrape_generic_tech_news(self, url: str, source_name: str) -> List[Dict]:
        """Generic scraper for tech news sites"""
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Common selectors for news articles
            selectors = ['article', '.post', '.entry', '.story', '.article']
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    for elem in elements[:3]:  # Limit to 3 articles per source
                        title_elem = elem.find(['h1', 'h2', 'h3', 'h4'])
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            link = elem.find('a')
                            url_link = link.get('href', '') if link else ''
                            
                            # Make relative URLs absolute
                            if url_link.startswith('/'):
                                base_url = '/'.join(url.split('/')[:3])
                                url_link = base_url + url_link
                            
                            summary_elem = elem.find('p')
                            summary = summary_elem.get_text(strip=True)[:200] + '...' if summary_elem else ''
                            
                            articles.append({
                                'title': title,
                                'summary': summary,
                                'url': url_link,
                                'source': source_name,
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'category': 'Tech/AI'
                            })
                    break
            
            return articles
        except Exception as e:
            print(f"Error scraping {source_name}: {e}")
            return []