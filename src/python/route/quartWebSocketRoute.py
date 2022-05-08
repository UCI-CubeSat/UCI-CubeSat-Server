from typing import Any
import quart
from quart import request, Blueprint
import socketio

from src.python.config import appConfig
from src.python.config.appConfig import quartEnv, webSocketUrl, apiBaseUrl


socketIO = socketio.Client()
webSocketRoute: Blueprint = Blueprint("webSocket", __name__)
# TODO replace with Kafka
responseQueue: list[Any] = []


@webSocketRoute.route(f"{apiBaseUrl}/ws_connect", methods=["GET"])
@socketIO.event
def wsConnect():
    try:
        if quartEnv == "development":
            socketIO.connect(webSocketUrl)
            appConfig.webSocketConnected = True
    except Exception as webSocketError:
        _ = webSocketError
        appConfig.webSocketConnected = False

    return quart.jsonify(dict(websocketConnection=appConfig.webSocketConnected))


@webSocketRoute.route(f"{apiBaseUrl}/ws_message", methods=["GET"])
@socketIO.event
def wsMessage():
    if quartEnv != "development":
        return quart.jsonify(dict(status="fail"))

    if not appConfig.webSocketConnected:
        wsConnect()
    webSocketMessage: str = request.args.get("message", default=None, type=str)

    if not webSocketMessage:
        return quart.jsonify(dict(status="fail"))

    try:
        message(webSocketMessage, callback=lambda *args: responseQueue.append(*args))
    except Exception as webSocketError:
        _ = webSocketError
        return quart.jsonify(dict(status="fail"))

    return quart.jsonify(dict(status="success"))


# TODO replace with Kafka
@webSocketRoute.route(f"{apiBaseUrl}/ws_queue", methods=["GET"])
def wsQueue():
    return quart.jsonify(responseQueue)


# socketIO client routes
@socketIO.event
def connect():
    pass


@socketIO.event
def message(data: str, callback=None):
    return (
        socketIO.emit("message", f"{data}", callback=callback)
        if callable(callback)
        else socketIO.emit("message", f"{data}")
    )


@socketIO.on("response")
def on_message(data):
    pass
