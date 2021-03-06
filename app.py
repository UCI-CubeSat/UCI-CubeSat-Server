from quart import websocket
from quart_cors import cors

from src.python.route.quartDashboardRoute import dashboardRoute
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
    for route in [mainRoute, trackerRoute, emailRoute, dashboardRoute, webSocketRoute]
]
cors(app)


@app.websocket("/ws")
async def ws():
    while True:
        data = await websocket.receive()
        await websocket.send(f"echo {data}")


if __name__ == "__main__":
    if quartEnv and quartEnv == "development":
        app.run(debug=quartDebug, host=quartHost, port=quartPort)
