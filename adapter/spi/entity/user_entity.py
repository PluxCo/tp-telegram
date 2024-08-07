from sqlalchemy.orm import Mapped, mapped_column

from db_connector import SqlAlchemyBase
from domain.model.user_model import UserModel


class UserEntity(SqlAlchemyBase):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int]
    external_id: Mapped[str] = mapped_column(nullable=True)

    name: Mapped[str] = mapped_column(nullable=True)

    def to_model(self):
        return UserModel(self.id, self.external_id)
