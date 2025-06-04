import os
import subprocess
import re
from config import Config
from datetime import datetime
from script_generator import ScriptGenerator

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import Voice, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    print("⚠️  ElevenLabs not available - audio generation will be skipped")
    ElevenLabs = None
    Voice = None
    VoiceSettings = None
    ELEVENLABS_AVAILABLE = False
    
class AudioGenerator:
    def __init__(self):
        self.client = None
        self.output_dir = Config.VIDEO_OUTPUT_DIR
        if Config.ELEVENLABS_API_KEY and ELEVENLABS_AVAILABLE:
            try:
                self.client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
            except Exception as e:
                print(f"Failed to initialize ElevenLabs client: {e}")
          
        if not self.output_dir:
            self.output_dir = os.path.join(os.getcwd(), 'output_videos')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_audio(self, script: str, voice_id: str = None) -> str:
        """Generate audio using ElevenLabs with configurable voice"""
        if not self.client or not ELEVENLABS_AVAILABLE:
            print("⚠️  ElevenLabs not available, creating placeholder audio file")
            return self._create_placeholder_audio(script)
        
        # Use provided voice_id or fall back to config default
        selected_voice_id = voice_id or Config.ELEVENLABS_VOICE_ID
        
        try:
            # Clean script for audio (remove pause markers and stage directions)
            clean_script = ScriptGenerator._clean_script_for_audio(script)
            
            # Generate speech using the new API with configurable voice
            audio = self.client.generate(
                text=clean_script,
                voice=Voice(
                    voice_id=selected_voice_id,
                    settings=VoiceSettings(stability=0.71, similarity_boost=0.5)
                ),
                model="eleven_monolingual_v1"
            )
            
            audio_filename = os.path.join(self.output_dir, f"youtube_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
            
            # Save the audio
            with open(audio_filename, 'wb') as f:
                for chunk in audio:
                    f.write(chunk)
            
            print(f"🎵 Audio generated with voice ID {selected_voice_id}: {audio_filename}")
            return audio_filename
            
        except Exception as e:
            print(f"Error generating audio with ElevenLabs: {e}")
            return self._create_placeholder_audio(script)
        
    def _clean_script_for_audio(self, script: str) -> str:
            """Clean script specifically for audio generation"""
            # Remove pause markers and stage directions
            clean_script = script.replace('[PAUSE]', '... ')
            clean_script = clean_script.replace('[EMPHASIS]', '')
            
            # Remove any remaining brackets or parentheses with stage directions
            patterns_to_remove = [
                r'\[.*?\]',  # Remove anything in square brackets
                r'\(.*?\)',  # Remove stage directions in parentheses
            ]
            
            for pattern in patterns_to_remove:
                clean_script = re.sub(pattern, '', clean_script)
            
            # Clean up spacing
            clean_script = re.sub(r'\s+', ' ', clean_script)
            clean_script = clean_script.strip()
            
            return clean_script
    
    def _create_placeholder_audio(self, script: str) -> str:
        """Create a placeholder audio file or use text-to-speech alternatives"""
        try:
            # Try using macOS built-in say command (if available)
            audio_filename = os.path.join(self.output_dir, f"youtube_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.aiff")
            clean_script = self._clean_script_for_audio(script).replace('\n', ' ')
            
            # Use macOS say command to generate audio
            subprocess.run([
                'say', '-o', audio_filename, '-v', 'Alex', clean_script
            ], check=True)
            
            # Convert AIFF to MP3 if ffmpeg is available
            mp3_filename = audio_filename.replace('.aiff', '.mp3')
            try:
                subprocess.run([
                    'ffmpeg', '-i', audio_filename, '-acodec', 'mp3', mp3_filename, '-y'
                ], check=True, capture_output=True)
                os.remove(audio_filename)  # Remove AIFF file
                print(f"Audio generated using system TTS: {mp3_filename}")
                return mp3_filename
            except:
                print(f"Audio generated using system TTS: {audio_filename}")
                return audio_filename
                
        except Exception as e:
            print(f"Could not generate audio: {e}")
            # Create a silent audio file as last resort
            try:
                silent_filename = os.path.join(self.output_dir, f"silent_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
                subprocess.run([
                    'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=duration=90', 
                    '-c:a', 'mp3', silent_filename, '-y'
                ], check=True, capture_output=True)
                print(f"Created silent audio file: {silent_filename}")
                return silent_filename
            except:
                print("⚠️  Could not create any audio file")
                return ""
