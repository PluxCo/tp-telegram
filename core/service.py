from sqlalchemy.orm import Mapped, MappedColumn, mapped_column

from db_connector import SqlAlchemyBase


class Service(SqlAlchemyBase):
    __tablename__ = 'services'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    webhook: Mapped[str]
