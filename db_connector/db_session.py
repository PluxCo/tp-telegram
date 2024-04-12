"""
File that describes a database initialization and connections
"""
import logging
from typing import Callable, Optional

import sqlalchemy
from sqlalchemy import Engine
from sqlalchemy.ext import declarative
from sqlalchemy.orm import sessionmaker, Session

SqlAlchemyBase = declarative.declarative_base()

# Global variable to store the SQLAlchemy session factory
__factory: Optional[Callable] = None


class DBWorker:
    """
    A wrapper around an SQLAlchemy session object.
    """

    _engine: Optional[Engine] = None
    _maker: Optional[Callable] = None

    def __init__(self):
        self.current_session = None

    def __enter__(self) -> Session:
        return self.session

    @property
    def session(self) -> Session:
        """
        Property that returns an SQLAlchemy session object

        :return: Session
        """
        if self._maker is None:
            raise AttributeError("Session factory is not initialized.")

        self.current_session = self._maker()

        return self.current_session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.current_session.close()

    @classmethod
    def init_db_file(cls, url: str, *args, force=False, **kwargs) -> None:
        """
        Initialize the database file with the given parameters.

        :param url: Connection url to the database.
        :param args: Args that would be passed to the :func:`sqlalchemy.create_engine`.
        :param force: Param which forces to recreate the engine if it already exists.
        :param kwargs: Kwargs that would be passed to the :func:`sqlalchemy.create_engine`.
        :return: None
        """

        if not force and cls._engine is not None:
            logging.warning("Engine is already initialized.")
            return

        cls.reset_connection()

        cls._engine = sqlalchemy.create_engine(url, *args, **kwargs)

        SqlAlchemyBase.metadata.create_all(cls._engine)

        cls._maker = sessionmaker(bind=cls._engine)

    @classmethod
    def reset_connection(cls) -> None:
        """
        Method that resets the connection of the database
        """
        cls._engine = None
        cls._maker = None
