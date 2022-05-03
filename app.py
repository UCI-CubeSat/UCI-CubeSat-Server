from src.python.route.webSocketClientRoute import webSocketRoute
from src.python.route.flaskServerRoute import serverRoute
from src.python.config.appConfig import app, flaskWebSocket, flaskDebug


_ = [app.register_blueprint(route) for route in [webSocketRoute,
                                                 serverRoute]]


if __name__ == '__main__':
    _ = flaskWebSocket.run(app, debug=flaskDebug)
