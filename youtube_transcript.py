#!/usr/bin/env python3
"""
Скрипт для получения текста (транскрипта/субтитров) из YouTube видео.
Поддерживает получение текста на разных языках и их резюмирование.
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
    """Извлекает ID видео из URL YouTube."""
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
    Получает продолжительность видео в секундах.

    Args:
        video_id: ID видео YouTube

    Returns:
        Продолжительность в секундах или None в случае ошибки
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(url, timeout=10)

        # Ищем продолжительность в метаданных страницы
        # YouTube хранит продолжительность в секундах в JSON данных
        duration_match = re.search(r'"lengthSeconds":"(\d+)"', response.text)

        if duration_match:
            return int(duration_match.group(1))

        return None
    except Exception:
        return None


def format_time(seconds):
    """
    Форматирует время из секунд в читаемый формат (ЧЧ:ММ:СС или ММ:СС).

    Args:
        seconds: Количество секунд

    Returns:
        Отформатированная строка времени
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
    Рассчитывает примерное время чтения текста.

    Исходит из средней скорости чтения ~200 слов в минуту.

    Args:
        text: Текст для подсчета

    Returns:
        Время чтения в секундах
    """
    # Считаем количество слов (разделенных пробелами)
    words = len(text.split())

    # Средняя скорость чтения: 200 слов в минуту
    reading_speed_wpm = 200

    # Рассчитываем время в секундах
    reading_time_seconds = (words / reading_speed_wpm) * 60

    return int(reading_time_seconds)


def summarize_text(text, ratio=0.3):
    """
    Создает резюме текста, используя экстрактивный метод.
    Выбирает наиболее важные предложения на основе частоты слов.

    Args:
        text: Исходный текст для резюмирования
        ratio: Доля текста, которую нужно оставить (0.3 = 30%)

    Returns:
        Резюмированный текст
    """
    # Разбиваем на предложения
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if len(sentences) <= 5:
        return text  # Текст слишком короткий для резюмирования

    # Подсчитываем частоту слов (исключая стоп-слова)
    stop_words = {
        'в', 'и', 'на', 'с', 'по', 'для', 'не', 'что', 'это', 'как', 'его', 
        'к', 'но', 'они', 'мы', 'вы', 'он', 'она', 'а', 'то', 'все', 'я',
        'у', 'же', 'за', 'бы', 'от', 'из', 'или', 'да', 'ну', 'вот', 'так'
    }
    
    words = []
    for sentence in sentences:
        words.extend([w.lower() for w in re.findall(r'\b\w+\b', sentence)])
    
    # Фильтруем стоп-слова и считаем частоту
    word_freq = Counter([w for w in words if w not in stop_words and len(w) > 2])
    
    # Вычисляем важность каждого предложения
    sentence_scores = []
    for sentence in sentences:
        words_in_sentence = [w.lower() for w in re.findall(r'\b\w+\b', sentence)]
        score = sum([word_freq.get(w, 0) for w in words_in_sentence if w not in stop_words])
        sentence_scores.append((sentence, score))
    
    # Сортируем по важности и берем топ предложений
    num_sentences = max(5, int(len(sentences) * ratio))
    top_sentences = sorted(sentence_scores, key=lambda x: x[1], reverse=True)[:num_sentences]
    
    # Восстанавливаем порядок предложений как в оригинале
    summary_sentences = []
    for sentence in sentences:
        if any(sentence == s[0] for s in top_sentences):
            summary_sentences.append(sentence)
    
    return '. '.join(summary_sentences) + '.'


def format_statistics(video_duration, reading_time, original_words=None, summary_words=None):
    """
    Форматирует статистику о видео и времени чтения.

    Args:
        video_duration: Продолжительность видео в секундах
        reading_time: Время чтения в секундах
        original_words: Количество слов в оригинальном тексте (опционально)
        summary_words: Количество слов в резюме (опционально)

    Returns:
        Отформатированная строка со статистикой
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
    Получает транскрипт видео с YouTube.
    Приоритет отдается русскому языку, если его нет - берется любой доступный.

    Args:
        video_url: URL видео на YouTube
        list_languages: Если True, только показывает доступные языки
        show_stats: Если True, показывает статистику времени
        summarize: Если True, создает резюме транскрипта
        summary_ratio: Доля текста для резюме (по умолчанию 0.3 = 30%)

    Returns:
        Текст транскрипта (или резюме) или информацию о доступных языках
    """
    video_id = get_video_id(video_url)

    if not video_id:
        return "Ошибка: Не удалось извлечь ID видео из URL"

    try:
        # Создаем API объект и получаем список доступных транскриптов
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

        # Пытаемся получить транскрипт на русском, если нет - берем первый доступный
        try:
            transcript = transcript_list.find_transcript(['ru'])
        except NoTranscriptFound:
            # Берем первый доступный транскрипт
            transcript = next(iter(transcript_list))

        # Получаем данные транскрипта
        transcript_data = transcript.fetch()

        # Формируем текст (в новой версии API entries - это объекты, не словари)
        original_text = '\n'.join([entry.text for entry in transcript_data])
        
        # Применяем резюмирование, если требуется
        if summarize:
            text = summarize_text(original_text, ratio=summary_ratio)
            result = f"Резюме транскрипта (язык: {transcript.language}):\n\n{text}"
        else:
            text = original_text
            result = f"Транскрипт (язык: {transcript.language}):\n\n{text}"

        # Добавляем статистику, если требуется
        if show_stats:
            video_duration = get_video_duration(video_id)
            if video_duration:
                reading_time = calculate_reading_time(text)
                
                if summarize:
                    # Показываем статистику для резюме
                    original_words = len(original_text.split())
                    summary_words = len(text.split())
                    stats = format_statistics(video_duration, reading_time, original_words, summary_words)
                else:
                    # Показываем обычную статистику
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
        description='Получение текста (транскрипта) из YouTube видео. Приоритет русскому языку.',
        epilog='Пример: python youtube_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID" -s'
    )

    parser.add_argument('url', help='URL YouTube видео')
    parser.add_argument(
        '--list',
        action='store_true',
        help='Показать все доступные языки для видео'
    )
    parser.add_argument(
        '-o', '--output',
        help='Файл для сохранения транскрипта (по умолчанию: transcript.txt)'
    )
    parser.add_argument(
        '--stdout',
        action='store_true',
        help='Вывести результат в консоль вместо сохранения в файл'
    )
    parser.add_argument(
        '-s', '--summarize',
        action='store_true',
        help='Создать резюме транскрипта вместо полного текста'
    )
    parser.add_argument(
        '-r', '--ratio',
        type=float,
        default=0.3,
        help='Коэффициент сжатия для резюме (0.1-0.9, по умолчанию: 0.3)'
    )

    args = parser.parse_args()

    # Получаем транскрипт (с резюмированием или без)
    result = get_transcript(args.url, args.list, summarize=args.summarize, summary_ratio=args.ratio)

    # Выводим результат
    if args.stdout:
        # Вывод в консоль
        print(result)
    else:
        # Сохранение в файл
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
