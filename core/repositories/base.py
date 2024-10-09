from sqlalchemy import select, update


class BaseRepository:
    def __init__(self, db, model):
        self.db = db
        self.model = model

    async def select_all(self):
        async with self.db() as session:
            query = await session.execute(select(self.model))
            query = query.scalars().all()
            return query

    async def select_name(self, name):
        async with self.db() as session:
            query = await session.execute(
                select(self.model).where(self.model.name == name)
            )
            query = query.scalars().one()
            return query
