import dataclasses


@dataclasses.dataclass
class ServiceModel:
    id: str
    webhook: str
