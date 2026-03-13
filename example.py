#!/usr/bin/env python3
"""
Пример использования функций для получения транскрипта из YouTube видео.

Базовое использование через командную строку:
    python youtube_transcript.py "URL"  # Сохраняет полный транскрипт в transcript.txt
    python youtube_transcript.py "URL" -s  # Сохраняет резюме в summary.txt
    python youtube_transcript.py "URL" -s -r 0.2  # Краткое резюме (20%)
    python youtube_transcript.py "URL" -o output.txt  # Сохраняет в output.txt
    python youtube_transcript.py "URL" --stdout  # Выводит в консоль
"""

from youtube_transcript import get_transcript, get_video_id


def example_basic():
    """Базовый пример - получение транскрипта (приоритет русскому языку)."""
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    result = get_transcript(video_url)

    # Сохраняем в файл вручную
    with open("my_transcript.txt", 'w', encoding='utf-8') as f:
        f.write(result)

    print("Транскрипт сохранен в my_transcript.txt")


def example_summary():
    """Пример - получение резюме транскрипта."""
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    result = get_transcript(video_url, summarize=True, summary_ratio=0.3)

    # Сохраняем резюме в файл
    with open("my_summary.txt", 'w', encoding='utf-8') as f:
        f.write(result)

    print("Резюме сохранено в my_summary.txt")


def example_list_languages():
    """Пример - получение списка доступных языков."""
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    result = get_transcript(video_url, list_languages=True)
    print(result)


if __name__ == '__main__':
    print("Примеры использования YouTube Transcript Extractor & Summarizer\n")
    print("Рекомендуется использовать скрипт через командную строку:")
    print("  python youtube_transcript.py 'URL'  # Полный транскрипт")
    print("  python youtube_transcript.py 'URL' -s  # Резюме")
    print("\nПримеры программного использования:\n")

    # Раскомментируйте нужный пример:

    # example_basic()
    # example_summary()
    example_list_languages()
