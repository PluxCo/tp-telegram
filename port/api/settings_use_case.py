import abc
import dataclasses
import enum


class ValueRequiredException(KeyError):
    def __init__(self, field):
        self.field = field
        super().__init__(f'"{field}" is required')


class WrongTypeException(TypeError):
    def __init__(self, field, expected_type):
        self.field = field
        self.expected_type = expected_type
        super().__init__(f'"{field}" is not of type "{expected_type}"')


class SettingsUseCase(abc.ABC):
    @abc.abstractmethod
    def get_settings(self) -> dict:
        pass

    @abc.abstractmethod
    def set_settings(self, settings: dict):
        """
        :param settings: Dictionary of settings
        :return: None

        :raises:
            ValueRequiredException: Raised when required fields are missing
            WrongTypeException: Raised when wrong type is given
        """
        pass
