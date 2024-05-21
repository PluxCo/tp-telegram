from adapter.spi.entity.session_entity import SessionEntity


class SessionSerializer:
    def dump(self, obj: SessionEntity):
        data = {
            "user_id": obj.user.external_id,
            "state": obj.state.name
        }

        return data
