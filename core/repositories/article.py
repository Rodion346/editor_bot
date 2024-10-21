from sqlalchemy import select, update

from core.models.article import Article
from core.models.db_helper import db_helper
from core.repositories.base import BaseRepository


class ArticleRepository(BaseRepository):
    def __init__(self):
        super().__init__(db=db_helper.session_getter, model=Article)

    async def add(self, message_id, chat_id, text):
        async with self.db() as session:
            article = self.model(message_id=message_id, chat_id=chat_id, text=text)
            session.add(article)
            await session.commit()
            await session.refresh(article)
