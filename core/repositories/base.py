from sqlalchemy import select


class BaseRepository:
    def __init__(self, db, model):
        self.db = db
        self.model = model

    async def select_all(self):
        async with self.db as session:
            query = await session.execute(select(self.model))
            query = query.scalars().all()
            return query
