from typing import List, Dict
import requests
from config import Config

class ImageDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_unsplash_images(self, query: str, count: int = 3) -> List[Dict]:
        """Search for relevant images on Unsplash"""
        if not Config.UNSPLASH_API_KEY:
            return self._get_fallback_images(query, count)
        
        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {Config.UNSPLASH_API_KEY}"}
            params = {
                "query": query,
                "per_page": count,
                "orientation": "portrait"  # Better for 9:16 videos
            }
            
            response = self.session.get(url, headers=headers, params=params)
            data = response.json()
            
            images = []
            for photo in data.get('results', []):
                images.append({
                    'url': photo['urls']['regular'],
                    'description': photo.get('description', query),
                    'photographer': photo['user']['name'],
                    'query': query
                })
            print(f"Found {len(images)} images for query '{query}'")
            return images
        except Exception as e:
            print(f"Error searching Unsplash: {e}")
            return self._get_fallback_images(query, count)
    
    def _get_fallback_images(self, query: str, count: int) -> List[Dict]:
        """Get fallback images when Unsplash is not available"""
        # Use Pixabay as fallback (no API key required)
        try:
            url = "https://pixabay.com/api/"
            params = {
                "key": "50626234-1dd1ab70c124d23ff78a7517e",  # Public demo key
                "q": query.replace(" ", "+"),
                "image_type": "photo",
                "orientation": "vertical",
                "per_page": count,
                "safesearch": "true"
            }
            
            response = self.session.get(url, params=params)
            data = response.json()
            
            images = []
            for hit in data.get('hits', []):
                images.append({
                    'url': hit['webformatURL'],
                    'description': hit.get('tags', query),
                    'photographer': hit.get('user', 'Pixabay'),
                    'query': query
                })
            print(f"Found {len(images)} images for query '{query}'")
            return images
        except Exception as e:
            print(f"Error with fallback images: {e}")
            return []
    
    def download_image(self, image_data: Dict, filename: str) -> str:
        """Download an image and save it locally"""
        try:
            response = self.session.get(image_data['url'])
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded image: {filename}")
            return filename
        except Exception as e:
            print(f"Error downloading image: {e}")
            return ""
