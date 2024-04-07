from flask import Flask
from flask_restful import Api

from api.resources.services import ServiceBoundResource, ServiceUnboundResource
from api.resources.message import MessageResource
from api.resources.settings import SettingsResource

app = Flask(__name__)
api = Api(app)

api.add_resource(SettingsResource, "/settings/")
api.add_resource(MessageResource, "/message/")
api.add_resource(ServiceUnboundResource, "/service/")
api.add_resource(ServiceBoundResource, "/service/<string:s_id>")
