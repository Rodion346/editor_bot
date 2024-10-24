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

    async def select_id(self, entity_id):
        async with self.db() as session:
            if type(entity_id) is list:
                sourses = []
                for enti_id in entity_id:
                    query = await session.execute(
                        select(self.model).where(self.model.id == int(enti_id))
                    )
                    query = query.scalars().one()
                    sourses.append(query)
                return sourses
            else:
                query = await session.execute(
                    select(self.model).where(self.model.id == int(entity_id))
                )
                query = query.scalars().one()
                return query

    async def select_name(self, name):
        async with self.db() as session:
            query = await session.execute(
                select(self.model).where(self.model.name == name)
            )
            query = query.scalars().one()
            return query
