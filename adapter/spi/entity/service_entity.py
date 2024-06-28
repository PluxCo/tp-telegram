from __future__ import annotations

from sqlalchemy.orm import Mapped, MappedColumn, mapped_column

from db_connector import SqlAlchemyBase
from domain.model.service_model import ServiceModel


class ServiceEntity(SqlAlchemyBase):
    __tablename__ = 'services'

    id: Mapped[str] = mapped_column(primary_key=True)
    webhook: Mapped[str]

    def to_model(self) -> ServiceModel:
        return ServiceModel(id=self.id, webhook=self.webhook)

    @classmethod
    def from_model(cls, model: ServiceModel) -> ServiceEntity:
        return ServiceEntity(id=model.id, webhook=model.webhook)
