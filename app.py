from src.python.route.quartWebSocketRoute import webSocketRoute
from src.python.route.quartServerRoute import serverRoute
from src.python.config.appConfig import app, quartDebug, quartEnv, quartHost, quartPort


_ = [app.register_blueprint(route) for route in [webSocketRoute,
                                                 serverRoute]]


if __name__ == '__main__':
    if quartEnv and quartEnv == "development":
        app.run(debug=quartDebug, host=quartHost, port=quartPort)
