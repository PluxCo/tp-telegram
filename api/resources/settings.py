import datetime

from flask_restful import Resource, reqparse

from tools import Settings

post_settings_parser = reqparse.RequestParser()
post_settings_parser.add_argument("pin", type=str, required=False)
post_settings_parser.add_argument("session_duration", type=float, required=False)
post_settings_parser.add_argument("amount_of_questions", type=int, required=False)
post_settings_parser.add_argument("time_period", type=float, required=False)
post_settings_parser.add_argument("from_time", type=str, required=False)
post_settings_parser.add_argument("to_time", type=str, required=False)
post_settings_parser.add_argument("week_days", type=int, required=False, action="append")
post_settings_parser.add_argument("webhook", type=str, required=False)



class SettingsResource(Resource):
    def get(self):
        """
        Get the current application settings.

        Returns:
            tuple: A tuple containing the current application settings and HTTP status code.
        """
        current_settings = Settings().copy()

        return current_settings, 200

    def post(self):
        """
        Update the application settings.

        Returns:
            tuple: A tuple containing the updated application settings and HTTP status code.
        """
        current_settings = Settings()
        args = {k: v for k, v in post_settings_parser.parse_args().items() if v is not None and k in current_settings}

        current_settings.update(args)
        current_settings.update_settings()
        return self.get()
