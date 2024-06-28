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
