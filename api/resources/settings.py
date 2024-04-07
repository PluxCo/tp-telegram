from flask_restful import Resource, reqparse

from tools import Settings

post_settings_parser = reqparse.RequestParser()
post_settings_parser.add_argument("password", type=str, required=False)
post_settings_parser.add_argument("amount_of_questions", type=str, required=False)
post_settings_parser.add_argument("session_duration", type=str, required=False)


class SettingsResource(Resource):
    def get(self):
        current_settings = Settings()
        return current_settings.get_storage(), 200

    def patch(self):
        current_settings = Settings()
        args = {k: v for k, v in post_settings_parser.parse_args().items() if v is not None and k in current_settings}

        current_settings.update(args)
        return self.get(), 200
