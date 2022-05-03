from typing import Any
import flask
from flask import request, Blueprint

from src.python.config import appConfig


socketIO = appConfig.socketIO
webSocketRoute: Blueprint = Blueprint('webSocketClient', __name__)
# TODO replace with Kafka
responseQueue: list[Any] = []


@webSocketRoute.route(f'{appConfig.apiBaseUrl}/ws_connect', methods=['GET'])
@socketIO.event
def wsConnect():
    try:
        if appConfig.flaskEnv == "development":
            appConfig.socketIO.connect(appConfig.webSocketUrl)
            appConfig.webSocketConnected = True
    except Exception:
        appConfig.webSocketConnected = False

    return flask.jsonify(dict(websocketConnection=appConfig.webSocketConnected))


@webSocketRoute.route(f'{appConfig.apiBaseUrl}/ws_message', methods=['GET'])
@socketIO.event
def wsMessage():
    if appConfig.flaskEnv != "development":
        return flask.jsonify(dict(status="fail"))

    if not appConfig.webSocketConnected:
        wsConnect()
    webSocketMessage: str = request.args.get("message", default=None, type=str)

    if not webSocketMessage:
        return flask.jsonify(dict(status="fail"))

    try:
        message(webSocketMessage, callback=lambda *args: responseQueue.append(*args))
    except Exception:
        return flask.jsonify(dict(status="fail"))

    return flask.jsonify(dict(status="success"))


# TODO replace with Kafka
@webSocketRoute.route(f'{appConfig.apiBaseUrl}/ws_queue', methods=['GET'])
def wsQueue():
    return flask.jsonify(responseQueue)


# socketIO client routes
@socketIO.event
def connect():
    pass


@socketIO.event
def message(data: str, callback=None):
    return socketIO.emit('message', f"{data}", callback=callback) \
        if callable(callback) \
        else socketIO.emit('message', f"{data}")


@socketIO.on("response")
def on_message(data):
    pass
