from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase, create_session


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "users"
    tg_id: Mapped[int] = mapped_column(primary_key=True)
    auth_id: Mapped[str]
