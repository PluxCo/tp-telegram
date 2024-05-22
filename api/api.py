from flask import Flask
from flask_restful import Api

from adapter.api.http.send_message_view import MessageView
from adapter.api.http.settings_view import SettingsView
from api.resources.services import ServiceBoundResource, ServiceUnboundResource

app = Flask(__name__)
api = Api(app)

api.add_resource(ServiceUnboundResource, "/service/")
api.add_resource(ServiceBoundResource, "/service/<string:s_id>")

api.add_resource(MessageView, "/message/")
api.add_resource(SettingsView, "/settings/")
