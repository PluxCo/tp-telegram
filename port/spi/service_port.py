import abc
from typing import Iterable

from core.service import Service


class GetAllServicesPort(abc.ABC):
    @abc.abstractmethod
    def get_all_services(self) -> Iterable[Service]:
        pass
