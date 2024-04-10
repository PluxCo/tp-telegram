import uuid

from core.service import Service


class ServiceCreator:
    def create_service(self, data: dict) -> Service:
        s_id = str(uuid.uuid4())

        service = Service(id=s_id, webhook=data["webhook"])
        return service


class ServiceSerializer:
    def dump(self, obj: Service):
        data = {
            "id": obj.id,
            "webhook": obj.webhook
        }

        return data
