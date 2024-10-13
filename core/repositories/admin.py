from sqlalchemy import select, update, delete
from sqlalchemy.exc import NoResultFound

from core.models.admin import Admin
from core.models.db_helper import db_helper
from core.repositories.base import BaseRepository


class AdminRepository(BaseRepository):
    def __init__(self):
        super().__init__(db=db_helper.session_getter, model=Admin)

    async def add(self, admin_id):
        async with self.db() as session:
            admin = Admin(admin_id=admin_id)
            session.add(admin)
            await session.commit()

    async def select_adm_id(self, admin_id):
        async with self.db() as session:
            query = await session.execute(
                select(self.model).where(self.model.admin_id == int(admin_id))
            )
            query = query.scalars().one()
            return query

    async def update(self, adm_id: int, column: str, new_value: bool):
        async with self.db() as session:
            query = select(self.model).where(self.model.admin_id == adm_id)
            result = await session.execute(query)
            try:
                admin = result.scalars().one()
            except NoResultFound:
                raise ValueError(f"No admin found with id {adm_id}")

            if hasattr(admin, column):
                setattr(admin, column, new_value)
                await session.commit()
                await session.refresh(admin)
                return admin
            else:
                raise ValueError(
                    f"Column {column} does not exist on model {self.model.__name__}"
                )

    async def delete(self, adm_id: int):
        async with self.db() as session:
            stmt = delete(self.model).where(self.model.admin_id == adm_id)
            await session.execute(stmt)
            await session.commit()
