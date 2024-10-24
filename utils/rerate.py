import re
import demoji
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# Ваши данные для подключения к Telegram API


def remove_emojis(text):
    return demoji.replace(text, "")


def remove_links_and_mentions(text):
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r"@\w+", "", text)
    return text


def replace_jargon(text):
    return text


def truncate_text(text, max_length):
    if len(text) > max_length:
        text = text[:max_length]
    return text


def process_media(media_list, client):
    processed_media = []
    for media in media_list:
        if isinstance(media, MessageMediaPhoto):
            processed_media.append(media)
        elif isinstance(
            media, MessageMediaDocument
        ) and media.document.mime_type.startswith("video/"):
            if media.document.size > 20 * 1024 * 1024:  # 20 MB
                # Сжимаем видео с помощью встроенных в Telegram инструментов
                media = compress_video(media, client)
            processed_media.append(media)
    return processed_media[:2]  # Ограничиваем количество медиа до 2


def compress_video(media, client):
    # Скачиваем видео
    video_path = client.download_media(media)

    # Отправляем видео с параметром supports_streaming=False для сжатия
    compressed_video_message = client.send_file(
        "me", video_path, supports_streaming=False
    )
    compressed_media = compressed_video_message.media

    return compressed_media


def rewrite_message(message, client):
    text = message.message

    # Удаляем смайлы и графические знаки
    text = remove_emojis(text)

    # Удаляем ссылки и упоминания других каналов
    text = remove_links_and_mentions(text)

    # Исправляем жаргоны
    text = replace_jargon(text)

    # Удаляем знаки <..>, <...>, <....>
    text = re.sub(r"<[.]+>", "", text)

    # Проверяем наличие медиа
    media_list = message.media if message.media else None
    if media_list:
        # Ограничиваем текст до 750 знаков
        text = truncate_text(text, 750)

        # Обрабатываем медиа
        media_list = process_media(media_list, client)
    else:
        # Ограничиваем текст до 3500 знаков
        text = truncate_text(text, 3500)

        # Проверяем наличие словосочетания "часть" плюс номер
        if re.search(r"часть \d+", text):
            return None, None  # Не публикуем сообщение

    return text, media_list


async def send_to_channel(text, media_list, channel_username, client):
    if text:
        await client.send_message(channel_username, text)
    if media_list:
        for media in media_list:
            if isinstance(media, MessageMediaPhoto):
                await client.send_file(channel_username, media.photo)
            elif isinstance(
                media, MessageMediaDocument
            ) and media.document.mime_type.startswith("video/"):
                await client.send_file(channel_username, media.document)


# Пример использования функции
async def main_rer(message, targ_chat, client):
    new_text, new_media_list = rewrite_message(message, client)
    if new_text or new_media_list:
        await send_to_channel(new_text, new_media_list, targ_chat, client)
