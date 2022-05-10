import quart
from quart import Blueprint
from quart_cors import cors

from src.python.config.appConfig import apiBaseUrl
from src.python.service.mockDataService import generateVoltage

dashboardRoute: Blueprint = Blueprint("dashboard", __name__)
cors(dashboardRoute)


@dashboardRoute.route(f"{apiBaseUrl}/dashboard/voltage", methods=["GET"])
def getVoltage() -> None:
    return quart.jsonify(dict(voltage=generateVoltage()))
