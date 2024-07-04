from typing import Iterable

from sqlalchemy import select

from adapter.spi.entity.service_entity import ServiceEntity
from db_connector import DBWorker
from domain.model.service_model import ServiceModel
from port.spi.service_port import GetAllServicesPort, FindServiceByIdPort, SaveServicePort, RemoveServicePort


class ServiceRepository(GetAllServicesPort, FindServiceByIdPort, SaveServicePort, RemoveServicePort):
    def get_all_services(self) -> Iterable[ServiceModel]:
        with DBWorker() as db:
            for s in db.scalars(select(ServiceEntity)):
                yield s.to_model()

    def find_service_by_id(self, service_id: str) -> ServiceModel:
        with DBWorker() as db:
            service_entity = db.get(ServiceEntity, service_id)
            return service_entity.to_model() if service_entity else None

    def save_service(self, service: ServiceModel):
        with DBWorker() as db:
            service_entity = ServiceEntity.from_model(service)
            service_entity = db.merge(service_entity)
            db.commit()

            return service_entity.to_model()

    def remove_service(self, service_id: str):
        with DBWorker() as db:
            service_entity = db.get(ServiceEntity, service_id)
            db.delete(service_entity)
            db.commit()
