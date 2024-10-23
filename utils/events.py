import asyncio
import logging
from datetime import datetime, timedelta, timezone

from telethon.sync import TelegramClient
from sentence_transformers import SentenceTransformer, util

from core.config import settings
from core.repositories.event import EventRepository
from core.repositories.article import ArticleRepository

repo = EventRepository()
repo_art = ArticleRepository()

api_id = 26515046
api_hash = "22b6dbdfce28e71ce66911f29ccc5bfe"
target_chat_id = settings.channel__link

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Загрузка предобученной модели Sentence Transformers
model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")


def calculate_minutes_between_times(start_time_str, end_time_str):
    def parse_time(time_str):
        return datetime.strptime(time_str, "%H:%M")

    start_time = parse_time(start_time_str)
    end_time = parse_time(end_time_str)
    time_difference = end_time - start_time
    if time_difference.total_seconds() < 0:
        time_difference += timedelta(days=1)
    minutes_difference = time_difference.total_seconds() / 60
    return minutes_difference


async def fetch_posts(client, id):
    ev = await repo.select_id(id)
    sources = []
    if isinstance(ev, list):
        for item in ev:
            sources.extend(item.source.split(","))
    else:
        sources.extend(ev.source.split(","))
    minutes = calculate_minutes_between_times(ev.time_in, ev.time_out)
    messages = []
    logger.info(f"Fetching posts from sources: {sources}")

    for source in sources:
        try:
            channel = await client.get_entity(source)
            logger.info(f"Channel details: {channel}")
            async for message in client.iter_messages(
                channel,
                offset_date=datetime.now(timezone.utc) - timedelta(minutes=minutes),
            ):
                messages.append(message)
            logger.info(f"Fetched {len(messages)} messages from {source}")
        except Exception as e:
            logger.error(f"Error fetching messages from {source}: {e}")

    logger.info(f"Fetched {len(messages)} messages from all sources.")
    return messages


async def select_best_match(desc, messages):
    best_match = None
    best_ratio = 0
    best_chat = None

    # Векторизация описания
    desc_embedding = model.encode([desc])[0]

    for message in messages:
        if message.text is None:
            logger.error(f"Message text is None for message ID: {message.id}")
            continue

        try:
            # Векторизация текста сообщения
            message_embedding = model.encode([message.text])[0]
        except Exception as e:
            logger.error(f"Error encoding message text: {e}")
            continue

        # Вычисление косинусного сходства
        ratio = util.pytorch_cos_sim(desc_embedding, message_embedding).item()

        logger.info(
            f"Checking message {message.id} from chat {message.chat_id} with ratio {ratio}"
        )
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = message
            best_chat = message.chat_id

    if best_match:
        logger.info(
            f"Best match found: message {best_match.id} from chat {best_chat} with ratio {best_ratio}"
        )
    else:
        logger.info("No suitable match found.")

    return best_match, best_ratio, best_chat


async def find_similar_posts(
    messages, similarity_threshold=0.8, max_time_diff=timedelta(minutes=8)
):
    similar_posts = {}

    for message in messages:
        if message.text is None:
            logger.error(f"Message text is None for message ID: {message.id}")
            continue

        try:
            message_embedding = model.encode([message.text])[0]
        except Exception as e:
            logger.error(f"Error encoding message text: {e}")
            continue

        for other_message in messages:
            if message.id != other_message.id:
                if other_message.text is None:
                    logger.error(
                        f"Other message text is None for message ID: {other_message.id}"
                    )
                    continue

                try:
                    other_message_embedding = model.encode([other_message.text])[0]
                except Exception as e:
                    logger.error(f"Error encoding other message text: {e}")
                    continue

                similarity = util.pytorch_cos_sim(
                    message_embedding, other_message_embedding
                ).item()
                if similarity >= similarity_threshold:
                    if message.text not in similar_posts:
                        similar_posts[message.text] = []
                    similar_posts[message.text].append((message.chat_id, message.date))

    filtered_posts = {}
    for text, posts in similar_posts.items():
        if len(posts) >= 3:
            first_time = min(posts, key=lambda x: x[1])[1]
            last_time = max(posts, key=lambda x: x[1])[1]
            if last_time - first_time <= max_time_diff:
                filtered_posts[text] = posts

    return filtered_posts


async def copy_posts(client, messages, target_chat_id, desc):
    if isinstance(desc, list):
        for item in desc:
            best_match, best_ratio, chat = await select_best_match(item, messages)
            if best_match and best_ratio >= 0.8:
                try:
                    await repo_art.add(best_match.id, chat, best_match.text)
                    await client.send_message(target_chat_id, best_match.text)
                    logger.info(f"Copied post {best_match.id} to {target_chat_id}")
                    break
                except Exception as e:
                    logger.error(f"Error copying post {best_match.id}: {e}")
    else:
        best_match, best_ratio, chat = await select_best_match(desc, messages)
        if best_match and best_ratio >= 0.8:
            try:
                await repo_art.add(best_match.id, chat, best_match.text)
                await client.send_message(target_chat_id, best_match.text)
                logger.info(f"Copied post {best_match.id} to {target_chat_id}")
            except Exception as e:
                logger.error(f"Error copying post {best_match.id}: {e}")


async def main(id):
    client = TelegramClient("session_name", api_id, api_hash)
    await client.start()

    messages = await fetch_posts(client, id)
    similar_posts = await find_similar_posts(messages)

    for text, posts in similar_posts.items():
        logger.info(f"Similar post found in {len(posts)} channels:")
        for chat_id, date in posts:
            logger.info(f"Channel: {chat_id}, Date: {date}")
        logger.info(f"Text: {text}\n")

    await copy_posts(client, messages, target_chat_id, await repo.select_id(id))

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main(id))
