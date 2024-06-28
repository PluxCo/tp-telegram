import abc


class ServiceUseCase(abc.ABC):
    @abc.abstractmethod
    def get_all_services(self) -> list[dict]:
        pass

    @abc.abstractmethod
    def create_serivce(self, webhook: str):
        pass

    @abc.abstractmethod
    def delete_service(self, service_id: str):
        pass
