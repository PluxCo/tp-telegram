"""
File that describes custom SQLAlchemy types.
"""
import json

from sqlalchemy import types


class TextJson(types.TypeDecorator):
    """
    A json type for SQLAlchemy models.
    """
    impl = types.Unicode

    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        return json.dumps(value, ensure_ascii=False)

    def process_result_value(self, value, dialect):
        if value is None:
            return value

        return json.loads(value)
