import urllib
import os
from bmemcached import ReplicatingClient
from dotenv import load_dotenv
from quart import Quart
from quart_cors import cors
import psycopg
import bmemcached

load_dotenv()

# Database & Memcached feature flag
enableDB: bool = True
enableMemcache: bool = True  # always False on non-macOS

# Quart env config setting
quartHost: str | None = (
    os.getenv("QUART_HOST") if os.getenv("QUART_HOST") else "127.0.0.1"
)
quartPort: str | None = os.getenv("QUART_PORT") if os.getenv("QUART_PORT") else 5000
quartEnv: str | None = (
    os.getenv("QUART_ENV") if os.getenv("QUART_ENV") else "development"
)
quartDebug: bool = True if quartEnv == "development" else False

app: Quart = Quart(__name__)
cors(app)

# WebSocket config
webSocketUrl: str = (
    "https://uci-cubesat-websocket-server.herokuapp.com/"
    if quartEnv == "development"
    else "https://uci-cubesat-websocket-server.herokuapp.com/"
)
webSocketConnected: bool = False

# Heroku Memcached config
memcached: ReplicatingClient = bmemcached.Client(
    os.environ.get("MEMCACHEDCLOUD_SERVERS").split(","),
    os.environ.get("MEMCACHEDCLOUD_USERNAME"),
    os.environ.get("MEMCACHEDCLOUD_PASSWORD"),
)

# Heroku Postgre config
dbUrl: str | None = os.getenv("DATABASE_URL")
dbUrl = "postgresql" + dbUrl[dbUrl.index(":") :]

# Elephant Postgre config
# dbUrl = os.getenv("DB_URL")

# Quart sqlalchemy config
app.config["SQLALCHEMY_DATABASE_URI"] = dbUrl
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Psycopg config
_ = psycopg
urllib.parse.uses_netloc.append("postgres")
url: object = urllib.parse.urlparse(dbUrl)
dbCredential: str | None = dbUrl
psycopg2Config: dict[str, str | object] = dict(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port,
    options="-c statement_timeout=10000",
)

# Endpoint Url config
satnogsApiKey: str | None = os.getenv("SATNOGS_MAP_API_KEY")
apiVersion: str = "v1"
apiBaseUrl: str = f"/api/{apiVersion}"
