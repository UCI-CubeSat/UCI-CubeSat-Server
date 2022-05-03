import urllib
import os
from bmemcached import ReplicatingClient
from dotenv import load_dotenv
from quart import Quart
from quart_cors import cors
from quart import websocket
import psycopg
import bmemcached

# import logging

# logging config setting
# logLevel = logging.ERROR
# logOverwrite = 'w'
# logging.basicConfig(filename='error.log', encoding='utf-8', level=logLevel)

# load secret from .env
load_dotenv()

# db/memcache config setting
enableDB: bool = True
enableMemcache: bool = True  # always False on non-macOS

# flask config setting
quartHost: str | None = os.getenv("QUART_HOST") if os.getenv("QUART_HOST") else None
quartPort: str | None = os.getenv("QUART_PORT") if os.getenv("QUART_PORT") else None
quartEnv: str | None = os.getenv("QUART_ENV") if os.getenv("QUART_ENV") else "development"
quartDebug: bool = True if quartEnv == "development" else False

app: Quart = Quart(__name__)
cors(app)

# socketIO config
webSocketUrl = "https://uci-cubesat-websocket-server.herokuapp.com/" if quartEnv == "development" \
    else "https://uci-cubesat-websocket-server.herokuapp.com/"
webSocketConnected: bool = False

# Heroku Memcached
memcached: ReplicatingClient = bmemcached.Client(os.environ.get('MEMCACHEDCLOUD_SERVERS').split(','),
                                                 os.environ.get('MEMCACHEDCLOUD_USERNAME'),
                                                 os.environ.get('MEMCACHEDCLOUD_PASSWORD'))

# Heroku Postgre
dbUrl: str | None = os.getenv("DATABASE_URL")
dbUrl = "postgresql" + dbUrl[dbUrl.index(":"):]

# Elephant Postgre
# dbUrl = os.getenv("DB_URL")

# sqlalchemy db config setting
app.config["SQLALCHEMY_DATABASE_URI"] = dbUrl
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# psycopg db config setting
_ = psycopg
urllib.parse.uses_netloc.append("postgres")
url: object = urllib.parse.urlparse(dbUrl)
dbCredential: str | None = dbUrl
psycopg2Config: dict[str, str | object] = dict(database=url.path[1:],
                                               user=url.username,
                                               password=url.password,
                                               host=url.hostname,
                                               port=url.port,
                                               options='-c statement_timeout=10000')

# API URL config
satnogsApiKey: str | None = os.getenv('SATNOGS_MAP_API_KEY')
apiVersion: str = "v1"
apiBaseUrl: str = f"/api/{apiVersion}"
