from adapter.spi.entity.session_entity import SessionEntity
from domain.model.session_model import SessionState


class SessionSerializer:
    def dump(self, obj: SessionEntity):
        data = {
            "user_id": obj.user.external_id,
            "state": "OPEN" if obj.state in (SessionState.OPEN, SessionState.STARTED) else "CLOSE"
        }

        return data
