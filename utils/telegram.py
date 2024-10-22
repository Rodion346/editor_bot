import asyncio
from datetime import datetime, timedelta
from itertools import chain

from telethon.sync import TelegramClient
from rapidfuzz import fuzz, utils

from core.repositories.thematic_block import ThematicBlockRepository
from core.repositories.article import ArticleRepository

repo = ThematicBlockRepository()
repo_art = ArticleRepository()

api_id = 26515046
api_hash = "22b6dbdfce28e71ce66911f29ccc5bfe"
target_chat_id = -1002468380719


async def fetch_posts(client, id, minutes=60):
    tb = await repo.select_id(id)
    sources = []
    if isinstance(tb, list):
        for item in tb:
            sources.extend(item.source.split(","))
    else:
        sources.extend(tb.source.split(","))

    messages = []
    print(datetime.now() - timedelta(minutes=minutes))

    for source in sources:
        try:
            channel = await client.get_entity(source)
            async for message in client.iter_messages(
                channel,
                offset_date=datetime.now() - timedelta(minutes=minutes),
                reverse=True,
            ):
                messages.append(message)
        except Exception as e:
            print(f"Error fetching messages from {source}: {e}")

    return messages


async def select_best_match(desc, messages):
    copied_messages = {}
    message_save = await repo_art.select_all()
    for mess in message_save:
        copied_messages[mess.chat_id] = mess.message_id
    best_match = None
    best_ratio = 0
    chat = 0

    for message in messages:
        ratio = fuzz.WRatio(
            desc.description, message.text, processor=utils.default_process
        )
        for key, value in copied_messages.items():
            if key != message.peer_id.channel_id and value != message.id:
                pass
            else:
                break
        else:
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = message
                chat = message.peer_id.channel_id

    return best_match, best_ratio, chat


async def copy_posts(client, messages, target_chat_id, desc):
    if isinstance(desc, list):
        for item in desc:
            best_match, best_ratio, chat = await select_best_match(item, messages)
            if best_match and best_ratio >= 0.8:
                try:
                    await repo_art.add(best_match.id, chat, best_match.text)
                    await client.send_message(target_chat_id, best_match.text)
                    print(f"Copied post {best_match.id} to {target_chat_id}")
                    break
                except Exception as e:
                    print(f"Error copying post {best_match.id}: {e}")
    else:
        best_match, best_ratio, chat = await select_best_match(desc, messages)
        if best_match and best_ratio >= 0.8:
            try:
                await repo_art.add(best_match.id, chat, best_match.text)
                await client.send_message(target_chat_id, best_match.text)
                print(f"Copied post {best_match.id} to {target_chat_id}")
            except Exception as e:
                print(f"Error copying post {best_match.id}: {e}")


async def main(id):
    client = TelegramClient("session_name", api_id, api_hash)
    await client.start()
    tb = await repo.select_id(id)
    min = tb.time_back
    messages = await fetch_posts(client, id, minutes=min)
    await copy_posts(client, messages, target_chat_id, await repo.select_id(id))

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main(id))
