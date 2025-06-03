from typing import List, Dict
import subprocess
import json
import os
from datetime import datetime
import re
from config import Config

class VideoGenerator:
    
    def __init__(self):
        # Ensure output directory exists
        self.output_dir = Config.VIDEO_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_youtube_shorts_video(self, script: str, audio_path: str, images: List[Dict] = None) -> str:
        """Create a YouTube Shorts video (9:16 aspect ratio) with text, images, audio, and synchronized subtitles using FFmpeg"""
        try:
            video_filename = os.path.join(self.output_dir, f"youtube_shorts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
            
            # Clean script for video text
            clean_script = script.replace('[PAUSE]', ' ').replace('\n', ' ')
            
            # Get audio duration for timing calculations
            audio_duration = self._get_audio_duration(audio_path)
            
            # Download/process images if provided
            image_files = []
            if images:
                for i, img_data in enumerate(images[:4]):  # Limit to 4 images
                    # Assuming img_data has a 'url' or 'path' key
                    if isinstance(img_data, dict):
                        img_path = img_data.get('url') or img_data.get('path') or img_data.get('file_path')
                    else:
                        img_path = str(img_data)
                    
                    if img_path and os.path.exists(img_path):
                        image_files.append(img_path)
                    elif img_path and img_path.startswith('http'):
                        # Download image if URL is provided
                        downloaded_file = self._download_image(img_path, i)
                        if downloaded_file:
                            image_files.append(downloaded_file)
            
            # Create video dimensions (9:16 aspect ratio for YouTube Shorts)
            width, height = 1080, 1920
            
            # Split script into subtitle segments
            subtitle_segments = self._create_subtitle_segments(clean_script, audio_duration)
            
            # Create video with images if available, otherwise text-only
            if image_files:
                return self._create_video_with_images_and_audio(subtitle_segments, image_files, audio_path, video_filename, width, height)
            else:
                return self._create_text_only_video_with_audio(subtitle_segments, audio_path, video_filename, width, height)
                
        except Exception as e:
            print(f"Error creating YouTube Shorts video: {e}")
            return self._create_simple_fallback_video(script, audio_path)

    def _get_audio_duration(self, audio_path: str) -> float:
        """Get the duration of the audio file in seconds"""
        try:
            if not audio_path or not os.path.exists(audio_path):
                return 30.0
                
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 30.0

    def _download_image(self, url: str, index: int) -> str:
        """Download image from URL (placeholder - implement based on your needs)"""
        try:
            import requests
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                img_filename = os.path.join(self.output_dir, f"temp_image_{index}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
                with open(img_filename, 'wb') as f:
                    f.write(response.content)
                return img_filename
        except Exception as e:
            print(f"Error downloading image {url}: {e}")
        return None

    def _create_subtitle_segments(self, script: str, audio_duration: float) -> List[Dict]:
        """Create subtitle segments with timing and background colors"""
        words = script.split()
        if not words:
            return []
        
        # Calculate timing per word
        words_per_second = len(words) / audio_duration if audio_duration > 0 else 3
        
        segments = []
        current_segment = []
        current_time = 0.0
        
        # Background colors for variety
        bg_colors = [
            "rgba(0,0,0,0.8)",
            "rgba(25,25,112,0.8)",
            "rgba(139,0,139,0.8)",
            "rgba(0,100,0,0.8)",
            "rgba(139,69,19,0.8)",
            "rgba(75,0,130,0.8)",
            "rgba(128,0,0,0.8)",
            "rgba(0,139,139,0.8)"
        ]
        
        # Create segments of 8-12 words each
        color_index = 0
        for i, word in enumerate(words):
            current_segment.append(word)
            
            # Calculate segment duration
            segment_duration = len(current_segment) / words_per_second
            
            if len(current_segment) >= 10 or i == len(words) - 1:
                segments.append({
                    'text': ' '.join(current_segment),
                    'start_time': current_time,
                    'end_time': current_time + segment_duration,
                    'bg_color': bg_colors[color_index % len(bg_colors)]
                })
                
                current_time += segment_duration
                current_segment = []
                color_index += 1
        
        return segments

    def _create_video_with_images_and_audio(self, subtitle_segments: List[Dict], image_files: List[str], 
                                          audio_path: str, video_filename: str, width: int, height: int) -> str:
        """Create video with images, audio, and synchronized subtitles"""
        try:
            print(f"Creating video with {len(image_files)} images and audio")
            
            # Calculate duration per image
            audio_duration = self._get_audio_duration(audio_path)
            duration_per_image = audio_duration / len(image_files)
            
            # Build FFmpeg command
            cmd = ['ffmpeg', '-y']
            
            # Add image inputs with loop and duration
            for img_file in image_files:
                cmd.extend(['-loop', '1', '-t', str(duration_per_image), '-i', img_file])
            
            # Add audio input
            cmd.extend(['-i', audio_path])
            
            # Create filter complex for scaling, concatenating images and adding subtitles
            filter_parts = []
            
            # Scale each image to fit 9:16 aspect ratio
            for i in range(len(image_files)):
                filter_parts.append(
                    f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
                    f"crop={width}:{height},(format=yuv420p),fps=30,"
                    f"setpts=PTS-STARTPTS+{i*duration_per_image}/TB[img{i}]"
                )
            
            # Concatenate all scaled images
            concat_inputs = ''.join([f'[img{i}]' for i in range(len(image_files))])
            filter_parts.append(f"{concat_inputs}concat=n={len(image_files)}:v=1:a=0[video_base]")
            
            # Add subtitle overlay
            subtitle_filter = self._create_subtitle_filter(subtitle_segments, width, height)
            if subtitle_filter:
                filter_parts.append(f"[video_base]{subtitle_filter}[video_final]")
                video_output = '[video_final]'
            else:
                video_output = '[video_base]'
            
            # Add filter complex to command
            cmd.extend(['-filter_complex', ';'.join(filter_parts)])
            
            # Map video and audio outputs
            cmd.extend([
                '-map', video_output,
                '-map', f'{len(image_files)}:a',  # Audio is the last input
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-preset', 'medium',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                '-t', str(audio_duration),
                video_filename
            ])
            
            print(f"Running FFmpeg command...")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Clean up temporary image files that were downloaded
            for img_file in image_files:
                if img_file.startswith(self.output_dir) and 'temp_image_' in img_file:
                    try:
                        os.remove(img_file)
                    except:
                        pass
            
            print(f"Video with images created successfully: {video_filename}")
            return video_filename
            
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr}")
            return self._create_text_only_video_with_audio(subtitle_segments, audio_path, video_filename, width, height)
        except Exception as e:
            print(f"Error creating video with images: {e}")
            return self._create_text_only_video_with_audio(subtitle_segments, audio_path, video_filename, width, height)

    def _create_text_only_video_with_audio(self, subtitle_segments: List[Dict], audio_path: str, 
                                         video_filename: str, width: int, height: int) -> str:
        """Create text-only video with audio and synchronized subtitles"""
        try:
            print(f"Creating text-only video with audio and subtitles")
            audio_duration = self._get_audio_duration(audio_path)
            
            # Create subtitle filter
            subtitle_filter = self._create_subtitle_filter(subtitle_segments, width, height)
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi', '-i', f'color=c=#0f0f23:s={width}x{height}:d={audio_duration}:r=30',
                '-i', audio_path
            ]
            
            # Add subtitle overlay if available
            if subtitle_filter:
                cmd.extend([
                    '-filter_complex', f'[0:v]{subtitle_filter}[video_with_subs]',
                    '-map', '[video_with_subs]',
                    '-map', '1:a'
                ])
            else:
                cmd.extend(['-map', '0:v', '-map', '1:a'])
            
            cmd.extend([
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-preset', 'medium',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                '-t', str(audio_duration),
                video_filename
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Text-only video created successfully: {video_filename}")
            return video_filename
            
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr}")
            return self._create_simple_fallback_video("", audio_path)
        except Exception as e:
            print(f"Error creating text-only video: {e}")
            return self._create_simple_fallback_video("", audio_path)

    def _create_subtitle_filter(self, subtitle_segments: List[Dict], width: int, height: int) -> str:
        """Create FFmpeg subtitle filter with timed segments and colored backgrounds"""
        if not subtitle_segments:
            return ""
        
        subtitle_parts = []
        base_font_size = max(40, int(width * 0.04))
        
        for segment in subtitle_segments:
            # Properly escape text for FFmpeg
            escaped_text = self._escape_ffmpeg_text(segment['text'])
            
            # Wrap text to prevent overflow
            wrapped_text = self._wrap_text_for_display(escaped_text)
            
            # Create drawtext filter for this segment
            drawtext_filter = (
                f"drawtext=text='{wrapped_text}'"
                f":fontsize={base_font_size}"
                f":fontcolor=white"
                f":bordercolor=black"
                f":borderw=3"
                f":box=1"
                f":boxcolor={segment['bg_color']}"
                f":boxborderw=10"
                f":x=(w-text_w)/2"
                f":y=h*0.75"
                f":enable='between(t,{segment['start_time']:.2f},{segment['end_time']:.2f})'"
            )
            
            subtitle_parts.append(drawtext_filter)
        
        # Join all subtitle filters with commas
        return ','.join(subtitle_parts)

    def _escape_ffmpeg_text(self, text: str) -> str:
        """Properly escape text for FFmpeg drawtext filter"""
        # Remove or replace problematic characters
        text = re.sub(r'[^\w\s.,!?\-]', ' ', text)
        text = text.replace(':', ' ')
        text = text.replace("'", ' ')
        text = text.replace('"', ' ')
        text = text.replace('\\', ' ')
        text = ' '.join(text.split())  # Normalize whitespace
        return text

    def _wrap_text_for_display(self, text: str, max_chars_per_line: int = 40) -> str:
        """Wrap text to prevent overflow on mobile screens"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_chars_per_line and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + (1 if current_line else 0)
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        # Join lines with newline characters (max 2 lines to fit on screen)
        return '\\n'.join(lines[:2])

    def _create_simple_fallback_video(self, script: str, audio_path: str) -> str:
        """Fallback: Create a simple video when all else fails"""
        try:
            video_filename = os.path.join(self.output_dir, f"fallback_shorts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
            
            if audio_path and os.path.exists(audio_path):
                audio_duration = self._get_audio_duration(audio_path)
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi', '-i', f'color=c=navy:s=1080x1920:d={audio_duration}:r=30',
                    '-i', audio_path,
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-shortest',
                    '-pix_fmt', 'yuv420p',
                    video_filename
                ]
            else:
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi', '-i', 'color=c=navy:s=1080x1920:d=30:r=30',
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    video_filename
                ]
            
            subprocess.run(cmd, check=True)
            print(f"Fallback video created: {video_filename}")
            return video_filename
            
        except Exception as e:
            print(f"Fallback video creation failed: {e}")
            return ""