from sqlalchemy import select, update

from core.models.publication import Publication
from core.models.db_helper import db_helper
from core.repositories.base import BaseRepository


class PublicationRepository(BaseRepository):
    def __init__(self):
        super().__init__(db=db_helper.session_getter, model=Publication)

    async def add(self, time, thematic_block_id, today):
        async with self.db() as session:
            publication = Publication(
                time=time, thematic_block_id=thematic_block_id, today=today
            )
            session.add(publication)
            await session.commit()
