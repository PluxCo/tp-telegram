import numbers
from datetime import timedelta, time

from port.api.settings_use_case import SettingsUseCase, WrongTypeException
from service.session_aggregator import SessionAggregator
from tools import Settings


class SettingsService(SettingsUseCase):
    def __init__(self, session_aggregator: SessionAggregator):
        self.__session_aggregator = session_aggregator

    def get_settings(self) -> dict:
        return Settings().get_storage()

    def set_settings(self, settings: dict):
        data_types = [("password", str),
                      ("amount_of_questions", int),
                      ("session_duration", (int, float)),
                      ("start_time", str),
                      ("end_time", str),
                      ("period", (int, float))]

        for field, f_type in data_types:
            self.__validate_field(field, f_type, settings)

        self.apply()

    def apply(self):
        stg = Settings()
        s = self.__session_aggregator

        s.max_messages = stg["amount_of_questions"]
        s.time_limit = timedelta(seconds=stg["session_duration"])
        s.begin_time = time.fromisoformat(stg["start_time"])
        s.end_time = time.fromisoformat(stg["end_time"])
        s.time_period = timedelta(seconds=stg["period"])

    def __validate_field(self, filed: str, field_type: type | tuple[type], data: dict):
        settings_entity = Settings()
        if filed in data:
            if not isinstance(data[filed], field_type):
                raise WrongTypeException(filed, field_type)

            settings_entity[filed] = data[filed]
