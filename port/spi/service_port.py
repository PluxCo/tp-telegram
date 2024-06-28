import abc
from typing import Iterable

from domain.model.service_model import ServiceModel


class GetAllServicesPort(abc.ABC):
    @abc.abstractmethod
    def get_all_services(self) -> Iterable[ServiceModel]:
        pass


class FindServiceByIdPort(abc.ABC):
    @abc.abstractmethod
    def find_service_by_id(self, service_id: str) -> ServiceModel:
        pass


class SaveServicePort(abc.ABC):
    @abc.abstractmethod
    def save_service(self, service: ServiceModel) -> ServiceModel:
        pass


class RemoveServicePort(abc.ABC):
    @abc.abstractmethod
    def remove_service(self, service_id: str):
        pass
