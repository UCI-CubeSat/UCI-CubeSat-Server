from src.python.route.quartMainRoute import mainRoute
from src.python.route.quartTrackerRoute import trackerRoute
from src.python.route.quartEmailRoute import emailRoute
from src.python.route.quartWebSocketRoute import webSocketRoute
from src.python.config.appConfig import (
    app,
    quartDebug,
    quartEnv,
    quartHost,
    quartPort,
)


_ = [
    app.register_blueprint(route)
    for route in [mainRoute, trackerRoute, emailRoute, webSocketRoute]
]


if __name__ == "__main__":
    if quartEnv and quartEnv == "development":
        app.run(debug=quartDebug, host=quartHost, port=quartPort)
