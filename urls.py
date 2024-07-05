from flask import Flask
from flask_restful import Api

from adapter.api.http.send_message_view import MessageView
from adapter.api.http.settings_view import SettingsView
from adapter.api.http.services_view import ServiceBoundView, ServiceUnboundView

app = Flask(__name__)
api = Api(app)

api.add_resource(ServiceUnboundView, "/service/")
api.add_resource(ServiceBoundView, "/service/<string:s_id>")

api.add_resource(MessageView, "/message/")

api.add_resource(SettingsView, "/settings/")
