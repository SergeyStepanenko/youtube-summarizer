# YouTube Video Transcript Extractor & Summarizer

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A script for extracting text (transcripts/subtitles) from YouTube videos with optional automatic summarization. Russian language is prioritized; if unavailable, any available language is used.

## Features

- Extract transcripts from YouTube videos
- Automatic summarization with configurable compression ratio
- Russian language priority (with fallback to other languages)
- Time statistics: video duration, reading time, time saved
- Save to file or print to console
- Support for various YouTube URL formats

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/SergeyStepanenko/youtube-summarizer.git
cd youtube-summarizer
```

### 2. Create a virtual environment (required)

> **Important:** On macOS and many Linux distributions, installing packages via `pip` without a virtual environment is blocked by the system (PEP 668 — `externally-managed-environment`). Creating a venv is **required**.

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Make sure** the virtual environment is activated (the terminal prompt should show `(.venv)`) before installing dependencies and running the script.

### 4. Usage

```bash
source .venv/bin/activate  # if the environment is not yet activated
python youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

The transcript will be saved to `transcript.txt`.

## Usage

### Basic usage

Get a transcript and save it to `transcript.txt` (default):

```bash
python youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Save to a different file

```bash
python youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -o output.txt
```

### Print to console

```bash
python youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" --stdout
```

### Create a transcript summary

New feature! Instead of the full transcript you can get a brief summary:

```bash
# Create a summary (30% of the original by default)
python youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -s

# Create a summary with a different compression ratio (e.g. 20%)
python youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -s -r 0.2

# Save the summary to a custom file
python youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -s -o my_summary.txt

# Get a summary in Russian (if Russian subtitles are available)
python youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -s --stdout
```

**Note:** The summary is generated in the same language as the original transcript. To get a summary in Russian:
1. If the video has Russian subtitles — the summary will be in Russian
2. If there are no Russian subtitles — first get the transcript, then use AI services to translate and summarize in Russian

### Examples

```bash
# Save full transcript to transcript.txt (default)
python youtube_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Create a summary and save to summary.txt (default with -s)
python youtube_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -s

# Save to a different file
python youtube_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -o my_transcript.txt

# Print summary to console
python youtube_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -s --stdout

# Create a very brief summary (10% of the original)
python youtube_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -s -r 0.1

# Example: getting a Russian-language summary:
# 1. For a video with Russian subtitles:
python youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_WITH_RU_SUBS" -s -o summary_ru.txt

# 2. For a video without Russian subtitles (two-step process):
#    Step 1: Get the transcript
python youtube_transcript.py "https://www.youtube.com/watch?v=ENGLISH_VIDEO" -o transcript_en.txt
#    Step 2: Use AI to translate and create a summary in Russian
#    (see the "Output language" section for details)
```

## Supported URL formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

## Features

### Automatic summarization

The script can automatically create a transcript summary:

- Uses an extractive method (selects the most important sentences)
- Configurable compression ratio (30% by default)
- Preserves key ideas and important information
- **Statistics show the reading time of the summary, not the full transcript!**

### Time statistics

When retrieving a transcript or summary the script automatically shows:

- **Video duration** — length of the original video
- **Text size** — word count (for summaries also shows original size and compression percentage)
- **Reading time** — estimated time needed to read the text (~200 words per minute)
- **Time saved** — how much time you save by reading the text instead of watching the video

### Statistics output example — full transcript

```
📊 Статистика:
   Продолжительность видео: 8:32
   Время чтения: ~3:30
   ⏱️  Экономия времени: 5:02 (59%)
```

### Statistics output example — summary

```
📊 Статистика:
   Продолжительность видео: 1:00:55
   Размер оригинального текста: 11234 слов
   Размер резюме: 3370 слов (сжатие: 70%)
   Время чтения: ~16:51
   ⏱️  Экономия времени: 44:04 (72%)
```

## How it works

1. The script first tries to get a transcript in Russian (manual or auto-generated)
2. If Russian is not available — it takes the first available language from the subtitle list
3. When the `-s` flag is used, summarization is applied:
   - Text is split into sentences
   - The importance of each sentence is computed based on word frequency
   - The most important sentences are selected (30% by default)
4. Video duration is fetched automatically and time statistics are calculated
5. **During summarization, statistics show the reading time of the summary, not the full transcript**

### Getting a Russian-language video summary

To create a video summary in Russian:

1. **Automatically** (if the video has Russian subtitles):
   - The script finds the Russian transcript
   - Applies the summarization algorithm
   - Outputs the result in Russian

2. **Manually** (if there are no Russian subtitles):
   - Get the transcript in the available language
   - Use an external service to translate it to Russian
   - Apply the summarization algorithm or use AI to create a summary

3. **Statistics for the summary**:
   - Shows the size of the original text and the summary
   - Calculates the compression percentage
   - Compares video watch time and summary reading time
   - Shows time saved

## Output language

Summaries and transcripts are output **in Russian**. The script automatically looks for Russian subtitles (manual or auto-generated). If no Russian subtitles are available, the first available language is used.

### Russian-language video summary

To get a video summary in Russian:

1. **If the video has Russian subtitles** — the script uses them automatically and creates a summary in Russian
2. **If the video does not have Russian subtitles** — use one of the following methods:

#### Method 1: Use AI services (recommended)
```bash
# 1. Get the transcript in English (or another language)
python youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -o transcript_en.txt

# 2. Use ChatGPT, Claude, or another AI to translate and summarize
#    Prompt: "Translate this transcript to Russian and write a brief summary of the main points"
```

#### Method 2: Use Google Translate + AI
```bash
# 1. Get the transcript
python youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -o transcript.txt

# 2. Translate via Google Translate or DeepL
# 3. Use AI to create a summary in Russian
```

#### Method 3: Automated pipeline (the script can be extended)
For automation you can add integration with:
- Google Translate API
- DeepL API  
- OpenAI API for translation and summarization

### Example with AI translation
```bash
# Get the transcript
python youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -o transcript.txt

# Use Claude to translate and summarize (example prompt):
"""
Translate the following YouTube video transcript to Russian and create a brief summary of the main points:

[paste transcript.txt contents here]

The summary should be:
1. In Russian
2. Brief (10-15% of the original)
3. Contain key ideas and conclusions
4. Be structured as bullet points
"""
```

### For videos without Russian subtitles:

1. **Using ChatGPT or Claude** (recommended)
   - Save the transcript to a file
   - Ask the AI to translate and summarize in Russian
   - Example prompt: "Translate this transcript to Russian and write a brief summary of the main points"

2. **Using DeepL or Google Translate**
   - Copy the transcript and paste it into the translator

## Limitations

- The script only works if subtitles are available for the video (manual or automatic)
- If subtitles are disabled by the video owner, the transcript cannot be retrieved
- The summary will be in the same language as the original transcript (use AI services for translation)

## Technologies

- Python 3.8+
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) — for fetching transcripts
- [requests](https://github.com/psf/requests) — for HTTP requests

## Dependencies

All dependencies are listed in `requirements.txt`:

```txt
youtube-transcript-api>=1.2.2
requests>=2.28.0
```

## Contributing

Suggestions and improvements are welcome! If you'd like to contribute:

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

**Sergey Stepanenko**

- GitHub: [@SergeyStepanenko](https://github.com/SergeyStepanenko)

## Acknowledgements

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) for the excellent library for working with YouTube transcripts
