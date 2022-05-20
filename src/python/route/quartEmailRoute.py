from quart import Blueprint

from src.python.config.appConfig import apiBaseUrl

emailRoute: Blueprint = Blueprint("email", __name__)


@emailRoute.route(f"{apiBaseUrl}/emailSignup", methods=["POST"])
async def postEmailSubscriber():
    # TODO: integrate with React.js frontend /src/components/emailSignup.js
    pass
