import asyncio
import logging
from datetime import datetime, timezone, timedelta

from sentence_transformers import SentenceTransformer, util
from telethon.sync import TelegramClient

from core.config import settings
from core.repositories.thematic_block import ThematicBlockRepository
from core.repositories.article import ArticleRepository

model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

repo = ThematicBlockRepository()
repo_art = ArticleRepository()

api_id = 26515046
api_hash = "22b6dbdfce28e71ce66911f29ccc5bfe"
target_chat_id = settings.channel__link


async def fetch_posts(client, id):
    tb = await repo.select_id(id)
    sources = []
    if isinstance(tb, list):
        for item in tb:
            sources.extend(item.source.split(","))
    else:
        sources.extend(tb.source.split(","))

    messages = []
    logger.info(f"Fetching posts from sources: {sources}")

    for source in sources:
        try:
            channel = await client.get_entity(source)
            logger.info(f"Channel details: {channel}")
            offset_date = datetime.now(timezone.utc) - timedelta(minutes=item.time_back)
            logger.info(
                f"Fetching messages from {source} with offset_date: {offset_date}"
            )
            async for message in client.iter_messages(
                channel, offset_date=offset_date, reverse=True
            ):
                if message.date < offset_date:
                    logger.info(
                        f"Message {message.id} from {source} is older than offset_date."
                    )
                    continue
                messages.append(message)
            logger.info(f"Fetched {len(messages)} messages from {source}")
        except Exception as e:
            logger.error(f"Error fetching messages from {source}: {e}")

    logger.info(f"Fetched {len(messages)} messages from all sources.")
    return messages


async def select_best_match(desc, messages, ignore_duplicates=False):
    copied_messages = {}
    if not ignore_duplicates:
        message_save = await repo_art.select_all()
        for mess in message_save:
            copied_messages[mess.chat_id] = mess.message_id
    best_match = None
    best_ratio = 0
    chat = 0

    # Векторизация описания
    desc_embedding = model.encode([desc.description])[0]

    for message in messages:
        if message.text is None:
            logger.error(f"Message text is None for message ID: {message.id}")
            continue

        try:
            # Векторизация текста сообщения
            message_embedding = model.encode([message.text])[0]
        except TypeError as e:
            logger.error(f"Error encoding message text: {e}")
            continue

        # Вычисление косинусного сходства
        ratio = util.pytorch_cos_sim(desc_embedding, message_embedding).item()

        logger.info(f"{desc.description}")
        logger.info(f"{message.text}")
        logger.info(
            f"Checking message {message.id} from chat {message.peer_id.channel_id} with ratio {ratio}"
        )
        if not ignore_duplicates:
            for key, value in copied_messages.items():
                if key != message.peer_id.channel_id and value != message.id:
                    pass
                elif key == message.peer_id.channel_id and value == message.id:
                    logger.info(f"{key, value}")
                    logger.info(
                        f"Message {message.id} from chat {message.peer_id.channel_id} already copied."
                    )
                    break
            else:
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = message
                    chat = message.peer_id.channel_id
        else:
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = message
                chat = message.peer_id.channel_id

    if best_match:
        logger.info(
            f"Best match found: message {best_match.id} from chat {chat} with ratio {best_ratio}"
        )
    else:
        logger.info("No suitable match found.")

    return best_match, best_ratio, chat


async def copy_posts(client, messages, target_chat_id, desc, ignore_duplicates=False):
    if isinstance(desc, list):
        for item in desc:
            best_match, best_ratio, chat = await select_best_match(
                item, messages, ignore_duplicates
            )
            if best_match and best_ratio >= 0.6:
                try:
                    target_chat = await client.get_entity(target_chat_id)
                    logger.info(f"Target chat details: {target_chat}")
                    await repo_art.add(best_match.id, chat, best_match.text)
                    logger.info(f"Added message {best_match.id} to repository.")
                    await client.send_message(target_chat, best_match.text)
                    logger.info(f"Copied post {best_match.id} to {target_chat_id}")
                    break
                except Exception as e:
                    logger.error(f"Error copying post {best_match.id}: {e}")
    else:
        best_match, best_ratio, chat = await select_best_match(
            desc, messages, ignore_duplicates
        )
        if best_match and best_ratio >= 0.6:
            try:
                target_chat = await client.get_entity(target_chat_id)
                logger.info(f"Target chat details: {target_chat}")
                await repo_art.add(best_match.id, chat, best_match.text)
                logger.info(f"Added message {best_match.id} to repository.")
                await client.send_message(target_chat, best_match.text)
                logger.info(f"Copied post {best_match.id} to {target_chat_id}")
            except Exception as e:
                logger.error(f"Error copying post {best_match.id}: {e}")


async def main(id, ignore_duplicates=False):
    client = TelegramClient("session_name", api_id, api_hash)
    await client.start()
    messages = await fetch_posts(client, id)
    await copy_posts(
        client, messages, target_chat_id, await repo.select_id(id), ignore_duplicates
    )

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main(id, ignore_duplicates=True))
