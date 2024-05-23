from typing import Iterable, Optional

from sqlalchemy import select

from adapter.spi.entity.session_entity import SessionEntity, SessionState
from core.service import Service
from db_connector import DBWorker
from domain.model.session_model import Session
from domain.model.user_model import UserModel
from port.spi.session_port import GetSessionByStatePort, SaveSessionPort


class SessionRepository(GetSessionByStatePort, SaveSessionPort):
    def get_user_sessions(self, user, service, states) -> Iterable[Session]:
        stmt = select(SessionEntity).where(SessionEntity.state.in_(states))

        if user is not None:
            stmt = stmt.where(SessionEntity.user_id == user.id)

        if service is not None:
            stmt = stmt.where(SessionEntity.service_id == service.id)

        with DBWorker() as db:
            sessions = db.scalars(stmt)

            for s in sessions:
                yield s.to_model()

    def get_open_sessions(self) -> Iterable[Session]:
        with DBWorker() as db:
            sessions = db.scalars(select(SessionEntity).where(SessionEntity.state == SessionState.OPEN))

            for s in sessions:
                yield s.to_model()

    def save_session(self, session: Session):
        with DBWorker() as db:
            db.merge(SessionEntity.from_model(session))

            db.commit()
