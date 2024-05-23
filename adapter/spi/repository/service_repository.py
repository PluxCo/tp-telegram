from typing import Iterable

from sqlalchemy import select

from core.service import Service
from db_connector import DBWorker
from port.spi.service_port import GetAllServicesPort


class ServiceRepository(GetAllServicesPort):
    def get_all_services(self) -> Iterable[Service]:
        with DBWorker() as db:
            for s in db.scalars(select(Service)):
                yield s
