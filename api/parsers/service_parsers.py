import uuid

from adapter.spi.entity.service_entity import ServiceEntity


class ServiceCreator:
    def create_service(self, data: dict) -> ServiceEntity:
        s_id = str(uuid.uuid4())

        service = ServiceEntity(id=s_id, webhook=data["webhook"])
        return service


class ServiceSerializer:
    def dump(self, obj: ServiceEntity):
        data = {
            "id": obj.id,
            "webhook": obj.webhook
        }

        return data
