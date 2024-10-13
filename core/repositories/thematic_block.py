from sqlalchemy import select, update

from core.models.thematic_block import ThematicBlock
from core.models.db_helper import db_helper
from core.repositories.base import BaseRepository


class ThematicBlockRepository(BaseRepository):
    def __init__(self):
        super().__init__(db=db_helper.session_getter, model=ThematicBlock)

    async def add(self, name, source, description):
        async with self.db() as session:
            block = self.model(name=name, source=source, description=description)
            session.add(block)
            await session.commit()
            await session.refresh(block)

    async def update(self, name: str, column: str, new_value: str):
        async with self.db() as session:
            if column not in ["name", "source", "description"]:
                return "Not"

            stmt = (
                update(self.model)
                .where(self.model.name == name)
                .values({column: new_value})
            )

            await session.execute(stmt)
            await session.commit()
            return stmt
