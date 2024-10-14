from os import times

from sqlalchemy import select, update

from core.models.event import Event
from core.models.db_helper import db_helper
from core.repositories.base import BaseRepository


class EventRepository(BaseRepository):
    def __init__(self):
        super().__init__(db=db_helper.session_getter, model=Event)

    async def add(self, name, source, description, time_in, time_out):
        async with self.db() as session:
            event = self.model(
                name=name,
                source=source,
                description=description,
                time_in=time_in,
                time_out=time_out,
            )
            session.add(event)
            await session.commit()
            await session.refresh(event)

    async def update(self, name: str, column: str, new_value: str):
        async with self.db() as session:
            if column not in ["name", "source", "description", "time_in", "time_out"]:
                return "Not"

            stmt = (
                update(self.model)
                .where(self.model.name == name)
                .values({column: new_value})
            )

            await session.execute(stmt)
            await session.commit()
            return stmt
