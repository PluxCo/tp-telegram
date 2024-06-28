from typing import Iterable

from sqlalchemy import select

from adapter.spi.entity.service_entity import ServiceEntity
from db_connector import DBWorker
from domain.model.service_model import ServiceModel
from port.spi.service_port import GetAllServicesPort, FindServiceByIdPort


class ServiceRepository(GetAllServicesPort, FindServiceByIdPort):
    def get_all_services(self) -> Iterable[ServiceModel]:
        with DBWorker() as db:
            for s in db.scalars(select(ServiceEntity)):
                yield s.to_model()

    def find_service_by_id(self, service_id: str) -> ServiceModel:
        with DBWorker() as db:
            service_entity = db.get(ServiceEntity, service_id)
            return service_entity.to_model() if service_entity else None
