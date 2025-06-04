# Lang-Graph: AI News Automation Pipeline

Lang-Graph is an automation pipeline designed to scrape AI/Tech news, enhance articles using OpenAI, generate YouTube Shorts scripts, create audio narrations, and produce videos using Json2Video and FFmpeg.

---

## Features
- **News Scraping**: Scrapes AI/Tech news from multiple sources like TechCrunch, The Verge, and VentureBeat.
- **Article Enhancement**: Uses OpenAI to summarize, categorize, and score articles.
- **Excel Report**: Creates a structured Excel report of the articles.
- **YouTube Shorts Script**: Generates engaging scripts optimized for YouTube Shorts.
- **Audio Narration**: Creates audio using ElevenLabs or system TTS.
- **Video Creation**: Produces videos with synchronized subtitles and visuals using Json2Video and FFmpeg.

---

## Requirements
### Environment Variables
Set the following environment variables before running the project:
- **`OPENAI_API_KEY`**: Your OpenAI API key for article enhancement and script generation.
- **`ELEVENLABS_API_KEY`**: (Optional) ElevenLabs API key for audio generation.
- **`VIDEO_OUTPUT_DIR`**: Directory where output files (Excel, audio, video) will be saved.
- **`JSON2VIDEO_API_KEY`**: Json2Video API key for video creation.
- **`UNSPLASH_API_KEY`**: (Optional) Unsplash API key for image search.

Example:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ELEVENLABS_API_KEY="your-elevenlabs-api-key"
export VIDEO_OUTPUT_DIR="/path/to/output"
export JSON2VIDEO_API_KEY="your-json2video-api-key"
export UNSPLASH_API_KEY="your-unsplash-api-key"
```

---

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/lang-graph.git
   cd lang-graph
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg**:
   - **Mac**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`
   - **Windows**: Download from [FFmpeg.org](https://ffmpeg.org/).

---

## Running the Project
### Using Uvicorn
The project can be run as an API using Uvicorn.

1. **Install Uvicorn**:
   ```bash
   pip install uvicorn
   ```

2. **Run the API**:
   ```bash
   uvicorn scripts.runner:main --reload
   ```

3. **Access the API**:
   Open your browser and navigate to `http://127.0.0.1:8000`.

---

## Running the Pipeline Directly
If you prefer to run the pipeline directly without Uvicorn:
1. **Run the Pipeline**:
   ```bash
   python scripts/runner.py
   ```

2. **Outputs**:
   - **Excel Report**: Saved in the `VIDEO_OUTPUT_DIR`.
   - **Audio File**: Generated narration saved in the `VIDEO_OUTPUT_DIR`.
   - **Video File**: Final video saved in the `VIDEO_OUTPUT_DIR`.

---

## Setup Instructions
### Required API Keys
- **OpenAI**: [Get your API key](https://platform.openai.com/signup/).
- **ElevenLabs**: [Get your API key](https://elevenlabs.io/).
- **Json2Video**: [Get your API key](https://json2video.com/).
- **Unsplash**: [Get your API key](https://unsplash.com/developers).

### Example Environment Variables
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ELEVENLABS_API_KEY="your-elevenlabs-api-key"
export VIDEO_OUTPUT_DIR="/path/to/output"
export JSON2VIDEO_API_KEY="your-json2video-api-key"
export UNSPLASH_API_KEY="your-unsplash-api-key"
```

---

## Notes
- **ElevenLabs**: If not available, the pipeline will use system TTS or create silent audio files.
- **Json2Video**: Ensure your API key is valid for video creation.
- **FFmpeg**: Required for video merging and fallback video creation.

---

## Troubleshooting
### Common Errors
1. **Missing API Keys**:
   Ensure all required environment variables are set.

2. **FFmpeg Not Found**:
   Install FFmpeg and ensure it is added to your system's PATH.

3. **Json2Video Errors**:
   Verify the payload structure and API key validity.

---

## License
This project is licensed under the MIT License.