from core.sessions.session import Session


class SessionSerializer:
    def dump(self, obj: Session):
        data = {
            "user_id": obj.user.external_id,
            "state": obj.state.name
        }

        return data
