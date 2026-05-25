#!/usr/bin/env python3
"""
Example usage of the functions for extracting a transcript from a YouTube video.

Basic command-line usage:
    python youtube_transcript.py "URL"  # Saves full transcript to transcript.txt
    python youtube_transcript.py "URL" -s  # Saves summary to summary.txt
    python youtube_transcript.py "URL" -s -r 0.2  # Brief summary (20%)
    python youtube_transcript.py "URL" -o output.txt  # Saves to output.txt
    python youtube_transcript.py "URL" --stdout  # Prints to console
"""

from youtube_transcript import get_transcript, get_video_id


def example_basic():
    """Basic example — fetch a transcript (Russian language prioritized)."""
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    result = get_transcript(video_url)

    # Save to file manually
    with open("my_transcript.txt", 'w', encoding='utf-8') as f:
        f.write(result)

    print("Транскрипт сохранен в my_transcript.txt")


def example_summary():
    """Example — fetch a transcript summary."""
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    result = get_transcript(video_url, summarize=True, summary_ratio=0.3)

    # Save summary to file
    with open("my_summary.txt", 'w', encoding='utf-8') as f:
        f.write(result)

    print("Резюме сохранено в my_summary.txt")


def example_list_languages():
    """Example — list available subtitle languages."""
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    result = get_transcript(video_url, list_languages=True)
    print(result)


if __name__ == '__main__':
    print("Примеры использования YouTube Transcript Extractor & Summarizer\n")
    print("Рекомендуется использовать скрипт через командную строку:")
    print("  python youtube_transcript.py 'URL'  # Полный транскрипт")
    print("  python youtube_transcript.py 'URL' -s  # Резюме")
    print("\nПримеры программного использования:\n")

    # Uncomment the example you want to run:

    # example_basic()
    # example_summary()
    example_list_languages()
