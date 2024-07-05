import uuid

from domain.model.service_model import ServiceModel
from port.api.service_use_case import ServiceUseCase
from port.spi.service_port import GetAllServicesPort, SaveServicePort, RemoveServicePort


class ServicesService(ServiceUseCase):  # xD
    __get_all_services_port: GetAllServicesPort
    __save_service_port: SaveServicePort
    __remove_service_port: RemoveServicePort

    def __init__(self, get_all_services_port: GetAllServicesPort,
                 save_service_port: SaveServicePort,
                 remove_service_port: RemoveServicePort):
        self.__get_all_services_port = get_all_services_port
        self.__save_service_port = save_service_port
        self.__remove_service_port = remove_service_port

    def get_all_services(self) -> list[dict]:
        services = self.__get_all_services_port.get_all_services()
        return [{"id": s.id, "webhook": s.webhook} for s in services]

    def create_serivce(self, webhook: str):
        s_id = str(uuid.uuid4())
        service = ServiceModel(id=s_id, webhook=webhook)
        self.__save_service_port.save_service(service)

    def delete_service(self, service_id: str):
        self.__remove_service_port.remove_service(service_id)
