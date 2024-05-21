import logging
from datetime import datetime, timedelta, time

from core.service import Service

from domain.model.session_model import Session
from domain.model.user_model import UserModel
from port.spi.service_port import GetAllServicesPort
from port.spi.message_port import GetMessageInTimeIntervalPort
from port.spi.session_port import GetOpenSessionPort, SaveSessionPort, CloseExpiredSessionPort, InitSessionPort, \
    SessionChangedNotifierPort
from port.spi.user_port import GetAllUsersPort

logger = logging.getLogger(__name__)


class SessionAggregator(CloseExpiredSessionPort, InitSessionPort):

    def __init__(self, get_open_session_port: GetOpenSessionPort,
                 save_session_port: SaveSessionPort,
                 get_all_users_port: GetAllUsersPort,
                 get_all_services_port: GetAllServicesPort,
                 session_changed_notifier_port: SessionChangedNotifierPort,
                 get_messages_in_time_interval_port: GetMessageInTimeIntervalPort,

                 time_period: timedelta = timedelta(minutes=60),
                 begin_time: time = time(hour=0, minute=0, second=0),
                 end_time: time = time(hour=23, minute=59, second=59),
                 max_messages: int = 10,
                 time_limit: timedelta = timedelta(minutes=10)):
        self.__get_open_session_port = get_open_session_port
        self.__save_session_port = save_session_port
        self.__get_all_users_port = get_all_users_port
        self.__get_all_services_port = get_all_services_port
        self.__session_changed_notifier_port = session_changed_notifier_port
        self.__get_messages_in_time_interval = get_messages_in_time_interval_port

        self.__prev_call = datetime.min

        self.__period: timedelta = time_period
        self.__from: time = begin_time
        self.__to: time = end_time

        self.__messages_count: int = max_messages
        self.__time_limit: timedelta = time_limit

    def initiate_sessions(self, pick_time: datetime):
        users = list(self.__get_all_users_port.get_all_users())
        services = list(self.__get_all_services_port.get_all_services())

        if pick_time - self.__prev_call < self.__period:
            return

        if pick_time.time() < self.__from or datetime.now().time() > self.__to:
            return

        for u in users:
            for s in services:
                self._init_user_session(u, s)

        self.__prev_call = pick_time

    def close_expired_session(self, user: UserModel = None):
        for s in self.__get_open_session_port.get_open_sessions():
            if self.__is_necessary_to_close(s):
                s.close()

                logger.info(f"Closed session: {s}")

                self.__save_session_port.save_session(s)

                self.__session_changed_notifier_port.notify_session_changed(s)

    def _init_user_session(self, user: UserModel, service: Service):
        if any(True for _ in self.__get_open_session_port.get_open_user_sessions(user, service)):
            # Aborts if user already have open session
            return

        session = Session(user=user,
                          service=service,
                          open_time=datetime.now().replace(microsecond=0))

        self.__save_session_port.save_session(session)

        logger.info(f"New session: {session}")

        self.__session_changed_notifier_port.notify_session_changed(session)

    def __is_necessary_to_close(self, session: Session) -> bool:
        messages_count = self.__get_messages_in_time_interval.get_messages_count_in_time_interval(session.open_time,
                                                                                                  session.close_time)

        if messages_count >= self.__messages_count:
            return True

        if datetime.now() - session.open_time > self.__time_limit:
            return True

        return False
