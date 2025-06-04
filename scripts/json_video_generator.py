from typing import List, Dict, Optional
import subprocess
import json
import os
from datetime import datetime
import re
import requests
import time
from config import Config

class VideoGeneratorV2:
    
    def __init__(self):
        """Initialize with Json2Video API key"""
        self.json2video_api_key = Config.JSON2VIDEO_API_KEY
        if not self.json2video_api_key:
            raise ValueError("JSON2VIDEO_API_KEY is not set in the environment variables.")
        
        # Json2Video API configuration
        self.json2video_base_url = "https://api.json2video.com/v2"
        self.headers = {
            "x-api-key": self.json2video_api_key,
            "Content-Type": "application/json"
        }
        
        self.output_dir = Config.VIDEO_OUTPUT_DIR
        if not self.output_dir:
            self.output_dir = os.path.join(os.getcwd(), 'output_videos')
        os.makedirs(self.output_dir, exist_ok=True)
  

    def create_youtube_shorts_video(self, script: str, audio_path: str) -> str:
        """Create a YouTube Shorts video using Json2Video and merge with audio using ffmpeg"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            raw_video_filename = os.path.join(self.output_dir, f"temp_video_{timestamp}.mp4")
            final_video_filename = os.path.join(self.output_dir, f"youtube_shorts_v2_{timestamp}.mp4")

            # Clean and analyze script
            clean_script = script.replace('[PAUSE]', ' ').replace('\n', ' ')

            # Get audio duration
            audio_duration = self._get_audio_duration(audio_path) if audio_path else 30.0

            # Create JSON template for Json2Video
            video_json = self._create_video_json_template(clean_script, audio_duration, audio_path)

            # Generate video using Json2Video API
            video_url = self._generate_video_with_json2video(video_json)

            if video_url:
                # Download the generated mute video
                downloaded_video = self._download_video(video_url, raw_video_filename)
                if downloaded_video and os.path.exists(audio_path):
                    # Merge video and audio using ffmpeg
                    merged = self._merge_video_audio_ffmpeg(raw_video_filename, audio_path, final_video_filename)
                    if merged:
                        os.remove(raw_video_filename)  # Clean up temp video
                        return final_video_filename

            # Fallback if video generation or merging fails
            return self._create_fallback_video(script, audio_path)

        except Exception as e:
            return self._create_fallback_video(script, audio_path)


    # def create_youtube_shorts_video(self, script: str, audio_path: str) -> str:
    #     """Create a YouTube Shorts video using Json2Video for dynamic content generation"""
    #     try:
    #         video_filename = os.path.join(self.output_dir, f"youtube_shorts_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
            
    #         # Clean and analyze script
    #         clean_script = script.replace('[PAUSE]', ' ').replace('\n', ' ')
    #         # Get audio duration
    #         audio_duration = self._get_audio_duration(audio_path) if audio_path else 30.0
    #         # Create JSON template for Json2Video
    #         video_json = self._create_video_json_template(clean_script, audio_duration, audio_path)
    #         # Generate video using Json2Video API
    #         video_url = self._generate_video_with_json2video(video_json)
    #         if video_url:
    #             # Download the generated video
    #             downloaded_video = self._download_video(video_url, video_filename)
    #             if downloaded_video:
    #                 return downloaded_video
            
    #         # Fallback to manual creation if Json2Video fails
    #         return self._create_fallback_video(script, audio_path)
            
    #     except Exception as e:
    #         return self._create_fallback_video(script, audio_path)

    def _get_audio_duration(self, audio_path: str) -> float:
        """Get the duration of the audio file in seconds"""
        try:
            if not audio_path or not os.path.exists(audio_path):
                return 30.0
                
            cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', audio_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 30.0

    def _create_video_json_template(self, script: str, duration: float, audio_path: str) -> Dict:
        """Create JSON template for Json2Video based on script content"""
        
        # Analyze script to determine theme and content type
        theme = self._analyze_script_theme(script)
        # Create subtitle segments
        subtitle_segments = self._create_subtitle_segments(script, duration)
        # Build Json2Video template
        video_json = {
            "width": 1080,
            "height": 1920,  # 9:16 aspect ratio for YouTube Shorts
            "fps": 30,
            "scenes": self._create_scenes(subtitle_segments, theme, audio_path),
        }
        
        return video_json

    def _analyze_script_theme(self, script: str) -> str:
        """Analyze script content to determine appropriate theme and visuals"""
        script_lower = script.lower()
        
        # Technology and AI themes
        if any(word in script_lower for word in ['ai', 'artificial intelligence', 'technology', 'tech', 'software', 'digital', 'computer', 'robot']):
            return 'technology'
        
        # Business and finance themes
        elif any(word in script_lower for word in ['business', 'market', 'finance', 'economy', 'investment', 'money', 'company', 'startup']):
            return 'business'
        
        # Science themes
        elif any(word in script_lower for word in ['science', 'research', 'study', 'discovery', 'experiment', 'scientific']):
            return 'science'
        
        # Health themes
        elif any(word in script_lower for word in ['health', 'medical', 'medicine', 'doctor', 'hospital', 'treatment']):
            return 'health'
        
        # Education themes
        elif any(word in script_lower for word in ['education', 'learning', 'school', 'university', 'student', 'knowledge']):
            return 'education'
        
        # News themes
        elif any(word in script_lower for word in ['news', 'breaking', 'report', 'update', 'announcement']):
            return 'news'
        
        # Default theme
        else:
            return 'general'

    def _get_background_config(self, theme: str) -> Dict:
        """Get background configuration based on theme"""
        backgrounds = {
            'technology': {
                "type": "gradient",
                "colors": ["#0f0f23", "#1a1a2e", "#16213e"],
                "direction": "diagonal",
                "animation": "pulse"
            },
            'business': {
                "type": "gradient", 
                "colors": ["#1e3c72", "#2a5298", "#1e3c72"],
                "direction": "vertical",
                "animation": "slide"
            },
            'science': {
                "type": "gradient",
                "colors": ["#134e5e", "#71b280", "#134e5e"],
                "direction": "radial",
                "animation": "zoom"
            },
            'health': {
                "type": "gradient",
                "colors": ["#667eea", "#764ba2", "#667eea"],
                "direction": "diagonal",
                "animation": "fade"
            },
            'education': {
                "type": "gradient",
                "colors": ["#f093fb", "#f5576c", "#f093fb"],
                "direction": "horizontal",
                "animation": "rotate"
            },
            'news': {
                "type": "gradient",
                "colors": ["#ff416c", "#ff4b2b", "#ff416c"],
                "direction": "vertical",
                "animation": "pulse"
            },
            'general': {
                "type": "gradient",
                "colors": ["#434343", "#000000", "#434343"],
                "direction": "diagonal",
                "animation": "fade"
            }
        }
        
        return backgrounds.get(theme, backgrounds['general'])

    def _create_subtitle_segments(self, script: str, duration: float) -> List[Dict]:
        """Create subtitle segments with timing"""
        words = script.split()
        if not words:
            return []
        
        segments = []
        words_per_segment = max(8, min(15, len(words) // max(1, int(duration / 3))))
        segment_duration = duration / max(1, len(words) // words_per_segment)
        
        current_time = 0.0
        for i in range(0, len(words), words_per_segment):
            segment_words = words[i:i + words_per_segment]
            segments.append({
                'text': ' '.join(segment_words),
                'start_time': current_time,
                'end_time': min(current_time + segment_duration, duration),
                'duration': min(segment_duration, duration - current_time)
            })
            current_time += segment_duration
            
            if current_time >= duration:
                break
        
        return segments

    def _create_scenes(self, subtitle_segments: List[Dict], theme: str, audio_path: str) -> List[Dict]:
        """Create scenes for JSON2Video based on subtitle segments and theme."""
        scenes = []

        # Theme-specific visual elements
        visual_elements = self._get_theme_visual_elements(theme)
        for i, segment in enumerate(subtitle_segments):
            scene = {
                "duration": segment['duration'],
                "elements": [
                    # Background animation element
                    {
                        "type": "component",
                        # "component": visual_elements['background_animation'],
                        "component": "basic/000", 
                        "start": 0,
                        "duration": segment['duration'],
                        "settings": {
                            "width": 1080,
                            "height": 1920,
                            "color": "transparent"
                        }
                    },
                    # Main text element
                    {
                        "type": "text",
                        "style": "002",  # Using a predefined style ID
                        "text": segment['text'],
                        "start": 0,
                        "duration": segment['duration'],
                        "settings": {
                            "font-family": "Arial",
                            "font-size": "48px",
                            "color": "#ffffff",
                            "font-weight": "bold",
                            "text-align": "center",
                            "background-color": "rgba(0,0,0,0.7)",
                            "padding": 20,
                            "border-radius": 10,
                            "shadow": 2,
                            "word-wrap": {
                                "enabled": True,
                                "max-width": 900
                            }
                        },
                        "x": 540,
                        "y": 1400
                    },
                    # Decorative elements based on theme
                    # *self._get_theme_decorative_elements(theme, i)
                    *list(self._get_theme_decorative_elements(theme, i) or [])
                ]
            }
            scenes.append(scene)
        return scenes



    def _get_theme_visual_elements(self, theme: str) -> Dict:
        """Get visual elements configuration for theme"""
        elements = {
            'technology': {
                'background_animation': 'matrix',
                'accent_color': '#00ff00',
                'secondary_color': '#0066cc'
            },
            'business': {
                'background_animation': 'slideUp',
                'accent_color': '#gold',
                'secondary_color': '#navy'
            },
            'science': {
                'background_animation': 'particle',
                'accent_color': '#00ccff',
                'secondary_color': '#66ff99'
            },
            'health': {
                'background_animation': 'pulse',
                'accent_color': '#ff6b6b',
                'secondary_color': '#4ecdc4'
            },
            'education': {
                'background_animation': 'bounce',
                'accent_color': '#ffa726',
                'secondary_color': '#ab47bc'
            },
            'news': {
                'background_animation': 'flash',
                'accent_color': '#ff5722',
                'secondary_color': '#ffeb3b'
            },
            'general': {
                'background_animation': 'fade',
                'accent_color': '#ffffff',
                'secondary_color': '#cccccc'
            }
        }
        
        return elements.get(theme, elements['general'])

    def _get_theme_decorative_elements(self, theme: str, scene_index: int) -> List[Dict]:
        """Get decorative elements for specific theme"""
        visual_config = self._get_theme_visual_elements(theme)
        
        decorative_elements = []
        
        # Add theme-specific decorative elements
        if theme == 'technology':
            decorative_elements.extend([
                {
                    "type": "component",
                    "component": "basic/000",  # Replace with actual component ID for a circle
                    "start": 0,
                    "duration": 3,
                    "x": 100,
                    "y": 200 + (scene_index * 50),
                    "settings": {
                        "color": visual_config['accent_color'],
                        "animation": "rotate"
                    }
                },
                {
                    "type": "component",
                    "component": "basic/000",  # Replace with actual component ID for a rectangle
                    "start": 0,
                    "duration": 2,
                    "x": 880,
                    "y": 300,
                    "settings": {
                        "color": visual_config['secondary_color'],
                        "animation": "slideLeft"
                    }
                }
            ])
        
        elif theme == 'business':
            decorative_elements.append({
                "type": "component",
                "component": "basic/000",  # Replace with actual component ID for a triangle
                "start": 0,
                "duration": 2,
                "x": 50,
                "y": 150,
                "settings": {
                    "color": visual_config['accent_color'],
                    "animation": "pulse"
                }
            })
        
        elif theme == 'news':
            decorative_elements.extend([
                {
                    "type": "text",
                    "style": "002",  # Using a predefined style ID
                    "text": "BREAKING",
                    "start": 0,
                    "duration": 1,
                    "x": 540,
                    "y": 200,
                    "settings": {
                        "font-family": "Arial Bold",
                        "font-size": "32px",
                        "color": visual_config['accent_color'],
                        "text-align": "center",
                        "animation": "blink"
                    }
                },
                {
                    "type": "component",
                    "component": "basic/000",  # Replace with actual component ID for a rectangle
                    "start": 0,
                    "duration": 1.5,
                    "x": 0,
                    "y": 250,
                    "settings": {
                        "color": visual_config['accent_color'],
                        "animation": "slideRight"
                    }
                }
            ])
        
        return decorative_elements

    def _generate_video_with_json2video(self, video_json: Dict) -> Optional[str]:
        """Generate video using Json2Video API"""
        try:
            # Create video project using direct API call
            response = self._create_video_project(video_json)
            
            if response and 'project' in response:
                        project_id = response['project'] 
                        print(f"Video project created with ID: {project_id}")
                        
                        # Poll for completion
                        video_url = self._wait_for_video_completion(project_id)
                        return video_url
            else:
                print("Failed to create video project")
                return None
                
        except Exception as e:
            print(f"Error generating video with Json2Video: {e}")
            return None

    def _create_video_project(self, video_json: Dict) -> Optional[Dict]:
        """Create a video project using Json2Video API"""
        try:
            url = f"{self.json2video_base_url}/movies"
            payload = {
                **video_json,
                "quality": "high",
                "width": 1080,
                "height": 1920, 
            }
            
            response = requests.post(
                url, 
                headers=self.headers, 
                json=payload, 
                timeout=300
            )
            
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error creating video project: {e}")
            return None

    def _get_project_status(self, project_id: str) -> Optional[Dict]:
        """Get the status of a video project"""
        try:
            url = f"{self.json2video_base_url}/movies?project={project_id}"
            
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Status check error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error checking status: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error checking project status: {e}")
            return None

    def _wait_for_video_completion(self, project_id: str, max_wait_time: int = 300) -> Optional[str]:
        """Wait for video generation to complete and return download URL"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                status_response = self._get_project_status(project_id)
                
                if not status_response:
                    print("Failed to get project status")
                    time.sleep(10)
                    continue
                
                status = status_response.get('status', '').lower()
                
                if status == 'completed' or status == 'done':
                    download_url = status_response.get('url') or status_response.get('download_url')
                    if download_url:
                        print("Video generation completed successfully!")
                        return download_url
                    else:
                        print("Video completed but no download URL found")
                        return None
                        
                elif status == 'failed' or status == 'error':
                    error_msg = status_response.get('error', 'Unknown error')
                    print(f"Video generation failed: {error_msg}")
                    return None
                
                elif status in ['processing', 'rendering', 'queued', 'pending']:
                    print(f"Video generation in progress... Status: {status}")
                else:
                    print(f"Unknown status: {status}")
                
                time.sleep(10)  # Wait 10 seconds before checking again
                
            except Exception as e:
                print(f"Error checking video status: {e}")
                time.sleep(10)
        
        print("Video generation timed out")
        return None

    def _download_video(self, video_url: str, output_filename: str) -> Optional[str]:
        """Download the generated video from URL"""
        try:
            print(f"Downloading video from: {video_url}")
            
            # Add headers for the download request
            download_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(
                video_url, 
                headers=download_headers,
                stream=True, 
                timeout=60
            )
            response.raise_for_status()
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_filename), exist_ok=True)
            
            with open(output_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify file was downloaded
            if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
                print(f"Video downloaded successfully: {output_filename}")
                return output_filename
            else:
                print("Downloaded file is empty or doesn't exist")
                return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading video: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error downloading video: {e}")
            return None

    def _create_fallback_video(self, script: str, audio_path: str) -> str:
        """Create a simple fallback video using FFmpeg when Json2Video fails"""
        try:
            video_filename = os.path.join(self.output_dir, f"fallback_shorts_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
            
            # Clean script for display
            clean_script = script.replace('[PAUSE]', ' ').replace('\n', ' ')[:150]
            if len(script) > 150:
                clean_script += "..."
            
            # Escape special characters for FFmpeg
            escaped_text = re.sub(r'[^\w\s.,!?\-]', ' ', clean_script)
            escaped_text = escaped_text.replace("'", "\\'")
            escaped_text = escaped_text.replace('"', '\\"')
            
            if audio_path and os.path.exists(audio_path):
                audio_duration = self._get_audio_duration(audio_path)
                
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi', '-i', f'color=c=#1a1a2e:s=1080x1920:d={audio_duration}:r=30',
                    '-i', audio_path,
                    '-vf', (
                        f"drawtext=text='AI VIDEO UPDATE':fontcolor=white:fontsize=60:"
                        f"x=(w-text_w)/2:y=400:fontfile=/System/Library/Fonts/Arial.ttf,"
                        f"drawtext=text='{escaped_text}':fontcolor=white:fontsize=36:"
                        f"x=(w-text_w)/2:y=(h/2):fontfile=/System/Library/Fonts/Arial.ttf"
                    ),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'fast',
                    '-pix_fmt', 'yuv420p',
                    '-shortest',
                    video_filename
                ]
            else:
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi', '-i', 'color=c=#1a1a2e:s=1080x1920:d=30:r=30',
                    '-vf', (
                        f"drawtext=text='AI VIDEO UPDATE':fontcolor=white:fontsize=60:"
                        f"x=(w-text_w)/2:y=400,"
                        f"drawtext=text='{escaped_text}':fontcolor=white:fontsize=36:"
                        f"x=(w-text_w)/2:y=(h/2)"
                    ),
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    video_filename
                ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Fallback video created: {video_filename}")
            return video_filename
            
        except Exception as e:
            print(f"Fallback video creation failed: {e}")
            return ""