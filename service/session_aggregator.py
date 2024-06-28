import logging
from datetime import datetime, timedelta, time

from domain.model.service_model import ServiceModel
from domain.model.session_model import Session, SessionState
from domain.model.user_model import UserModel
from port.spi.service_port import GetAllServicesPort
from port.spi.message_port import GetMessageInTimeIntervalPort
from port.spi.session_port import GetSessionByStatePort, SaveSessionPort, CloseExpiredSessionPort, InitSessionPort, \
    SessionChangedNotifierPort, StartSessionPort
from port.spi.user_port import GetAllUsersPort

logger = logging.getLogger(__name__)


class SessionAggregator(CloseExpiredSessionPort, InitSessionPort, StartSessionPort):

    def __init__(self, get_session_by_state_port: GetSessionByStatePort,
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
        self.__get_session_by_state_port = get_session_by_state_port
        self.__save_session_port = save_session_port
        self.__get_all_users_port = get_all_users_port
        self.__get_all_services_port = get_all_services_port
        self.__session_changed_notifier_port = session_changed_notifier_port
        self.__get_messages_in_time_interval = get_messages_in_time_interval_port

        self.__prev_call = datetime.min

        self.time_period: timedelta = time_period
        self.begin_time: time = begin_time
        self.end_time: time = end_time

        self.max_messages: int = max_messages
        self.time_limit: timedelta = time_limit

    def initiate_sessions(self, pick_time: datetime):
        users = list(self.__get_all_users_port.get_all_users())
        services = list(self.__get_all_services_port.get_all_services())

        if pick_time - self.__prev_call < self.time_period:
            return

        if pick_time.time() < self.begin_time or datetime.now().time() > self.end_time:
            return

        for u in users:
            for s in services:
                self._init_user_session(u, s)

        self.__prev_call = pick_time

    def start_user_session(self, user: UserModel):
        pending_sessions = self.__get_session_by_state_port.get_user_sessions(user, None,
                                                                              [SessionState.OPEN])

        for session in pending_sessions:
            session.start()
            logger.info(f"Started session: {session}")
            self.__save_session_port.save_session(session)

    def close_expired_session(self, user: UserModel = None):
        for s in self.__get_session_by_state_port.get_user_sessions(user, None, [SessionState.STARTED]):
            if self.__is_necessary_to_close(s):
                s.close()

                logger.info(f"Closed session: {s}")

                self.__save_session_port.save_session(s)

                self.__session_changed_notifier_port.notify_session_changed(s)

    def _init_user_session(self, user: UserModel, service: ServiceModel):
        already_open = list(self.__get_session_by_state_port.get_user_sessions(user, service,
                                                                               [SessionState.OPEN,
                                                                                SessionState.STARTED]))
        if already_open:
            for session in already_open:
                self.__session_changed_notifier_port.notify_session_changed(session)
            # Aborts if user already have open session
            return

        session = Session(user=user,
                          service=service,
                          open_time=datetime.now())

        self.__save_session_port.save_session(session)

        logger.info(f"New session: {session}")

        self.__session_changed_notifier_port.notify_session_changed(session)

    def __is_necessary_to_close(self, session: Session) -> bool:
        messages_count = self.__get_messages_in_time_interval.get_messages_count_in_time_interval(session.user,
                                                                                                  session.service,
                                                                                                  session.open_time,
                                                                                                  session.close_time)

        if messages_count >= self.max_messages:
            return True

        if datetime.now() - session.start_time > self.time_limit:
            return True

        return False
