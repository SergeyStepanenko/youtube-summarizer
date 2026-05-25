#!/usr/bin/env python3
"""
Script for extracting text (transcripts/subtitles) from YouTube videos.
Supports retrieving text in multiple languages and summarizing it.
"""

import sys
import argparse
import re
import requests
from collections import Counter
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs


def get_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    parsed_url = urlparse(url)

    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/shorts/'):
            return parsed_url.path.split('/')[2]
    elif parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]

    return None


def get_video_duration(video_id):
    """
    Returns the video duration in seconds.

    Args:
        video_id: YouTube video ID

    Returns:
        Duration in seconds, or None on error
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(url, timeout=10)

        # Look for duration in page metadata
        # YouTube stores the duration in seconds in JSON data
        duration_match = re.search(r'"lengthSeconds":"(\d+)"', response.text)

        if duration_match:
            return int(duration_match.group(1))

        return None
    except Exception:
        return None


def format_time(seconds):
    """
    Formats a duration from seconds into a human-readable string (HH:MM:SS or MM:SS).

    Args:
        seconds: Number of seconds

    Returns:
        Formatted time string
    """
    if seconds is None:
        return "N/A"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def calculate_reading_time(text):
    """
    Estimates the reading time for a given text.

    Based on an average reading speed of ~200 words per minute.

    Args:
        text: Text to measure

    Returns:
        Reading time in seconds
    """
    # Count the number of words (space-delimited)
    words = len(text.split())

    # Average reading speed: 200 words per minute
    reading_speed_wpm = 200

    # Calculate time in seconds
    reading_time_seconds = (words / reading_speed_wpm) * 60

    return int(reading_time_seconds)


def summarize_text(text, ratio=0.3):
    """
    Creates a summary of the text using an extractive method.
    Selects the most important sentences based on word frequency.

    Args:
        text: Source text to summarize
        ratio: Fraction of text to keep (0.3 = 30%)

    Returns:
        Summarized text
    """
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if len(sentences) <= 5:
        return text  # Text is too short to summarize

    # Count word frequency (excluding stop words)
    stop_words = {
        'в', 'и', 'на', 'с', 'по', 'для', 'не', 'что', 'это', 'как', 'его', 
        'к', 'но', 'они', 'мы', 'вы', 'он', 'она', 'а', 'то', 'все', 'я',
        'у', 'же', 'за', 'бы', 'от', 'из', 'или', 'да', 'ну', 'вот', 'так'
    }
    
    words = []
    for sentence in sentences:
        words.extend([w.lower() for w in re.findall(r'\b\w+\b', sentence)])
    
    # Filter stop words and compute frequency
    word_freq = Counter([w for w in words if w not in stop_words and len(w) > 2])

    # Compute the importance score for each sentence
    sentence_scores = []
    for sentence in sentences:
        words_in_sentence = [w.lower() for w in re.findall(r'\b\w+\b', sentence)]
        score = sum([word_freq.get(w, 0) for w in words_in_sentence if w not in stop_words])
        sentence_scores.append((sentence, score))
    
    # Sort by importance and take the top sentences
    num_sentences = max(5, int(len(sentences) * ratio))
    top_sentences = sorted(sentence_scores, key=lambda x: x[1], reverse=True)[:num_sentences]

    # Restore the original sentence order
    summary_sentences = []
    for sentence in sentences:
        if any(sentence == s[0] for s in top_sentences):
            summary_sentences.append(sentence)
    
    return '. '.join(summary_sentences) + '.'


def format_statistics(video_duration, reading_time, original_words=None, summary_words=None):
    """
    Formats statistics about the video and reading time.

    Args:
        video_duration: Video duration in seconds
        reading_time: Reading time in seconds
        original_words: Word count of the original text (optional)
        summary_words: Word count of the summary (optional)

    Returns:
        Formatted statistics string
    """
    if video_duration is None:
        return ""

    time_saved = video_duration - reading_time
    percentage_saved = (time_saved / video_duration) * 100 if video_duration > 0 else 0

    stats = "\n📊 Статистика:\n"
    stats += f"   Продолжительность видео: {format_time(video_duration)}\n"
    
    if original_words and summary_words:
        compression_ratio = (1 - summary_words / original_words) * 100
        stats += f"   Размер оригинального текста: {original_words} слов\n"
        stats += f"   Размер резюме: {summary_words} слов (сжатие: {compression_ratio:.0f}%)\n"
    
    stats += f"   Время чтения: ~{format_time(reading_time)}\n"

    if time_saved > 0:
        stats += f"   ⏱️  Экономия времени: {format_time(time_saved)} ({percentage_saved:.0f}%)\n"
    else:
        stats += f"   ⏱️  Чтение займет на {format_time(abs(time_saved))} больше\n"

    return stats


def get_transcript(video_url, list_languages=False, show_stats=True, summarize=False, summary_ratio=0.3):
    """
    Retrieves the transcript of a YouTube video.
    Russian language is prioritized; if unavailable, the first available language is used.

    Args:
        video_url: YouTube video URL
        list_languages: If True, only lists available languages
        show_stats: If True, shows time statistics
        summarize: If True, creates a summary of the transcript
        summary_ratio: Fraction of text to keep in the summary (default 0.3 = 30%)

    Returns:
        Transcript text (or summary), or information about available languages
    """
    video_id = get_video_id(video_url)

    if not video_id:
        return "Ошибка: Не удалось извлечь ID видео из URL"

    try:
        # Create API object and fetch the list of available transcripts
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)

        if list_languages:
            result = f"Доступные языки для видео {video_id}:\n\n"
            result += "Ручные субтитры:\n"
            for transcript in transcript_list:
                if not transcript.is_generated:
                    result += f"  - {transcript.language} ({transcript.language_code})\n"

            result += "\nАвтоматически сгенерированные субтитры:\n"
            for transcript in transcript_list:
                if transcript.is_generated:
                    result += f"  - {transcript.language} ({transcript.language_code})\n"

            return result

        # Try to get the Russian transcript; fall back to the first available
        try:
            transcript = transcript_list.find_transcript(['ru'])
        except NoTranscriptFound:
            # Take the first available transcript
            transcript = next(iter(transcript_list))

        # Fetch transcript data
        transcript_data = transcript.fetch()

        # Build the text (in the newer API version entries are objects, not dicts)
        original_text = '\n'.join([entry.text for entry in transcript_data])
        
        # Apply summarization if requested
        if summarize:
            text = summarize_text(original_text, ratio=summary_ratio)
            result = f"Резюме транскрипта (язык: {transcript.language}):\n\n{text}"
        else:
            text = original_text
            result = f"Транскрипт (язык: {transcript.language}):\n\n{text}"

        # Append statistics if requested
        if show_stats:
            video_duration = get_video_duration(video_id)
            if video_duration:
                reading_time = calculate_reading_time(text)
                
                if summarize:
                    # Show statistics for the summary
                    original_words = len(original_text.split())
                    summary_words = len(text.split())
                    stats = format_statistics(video_duration, reading_time, original_words, summary_words)
                else:
                    # Show standard statistics
                    stats = format_statistics(video_duration, reading_time)
                
                result += f"\n{stats}"

        return result

    except TranscriptsDisabled:
        return "Ошибка: Субтитры отключены для этого видео"
    except NoTranscriptFound:
        return "Ошибка: Транскрипты не найдены для этого видео"
    except Exception as e:
        return f"Ошибка: {str(e)}"


def main():
    parser = argparse.ArgumentParser(
        description='Extract text (transcript) from a YouTube video. Russian language is prioritized.',
        epilog='Example: python youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -s'
    )

    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument(
        '--list',
        action='store_true',
        help='Show all available subtitle languages for the video'
    )
    parser.add_argument(
        '-o', '--output',
        help='File to save the transcript to (default: transcript.txt)'
    )
    parser.add_argument(
        '--stdout',
        action='store_true',
        help='Print result to console instead of saving to a file'
    )
    parser.add_argument(
        '-s', '--summarize',
        action='store_true',
        help='Create a summary of the transcript instead of the full text'
    )
    parser.add_argument(
        '-r', '--ratio',
        type=float,
        default=0.3,
        help='Compression ratio for the summary (0.1-0.9, default: 0.3)'
    )

    args = parser.parse_args()

    # Fetch the transcript (with or without summarization)
    result = get_transcript(args.url, args.list, summarize=args.summarize, summary_ratio=args.ratio)

    # Output the result
    if args.stdout:
        # Print to console
        print(result)
    else:
        # Save to file
        if args.summarize:
            default_file = 'summary.txt'
        else:
            default_file = 'transcript.txt'
        
        output_file = args.output if args.output else default_file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        
        file_type = "Резюме" if args.summarize else "Транскрипт"
        print(f"{file_type} сохранен в файл: {output_file}")


if __name__ == '__main__':
    main()
