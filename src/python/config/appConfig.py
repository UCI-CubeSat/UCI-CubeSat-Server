import urllib
import os
from bmemcached import ReplicatingClient
from dotenv import load_dotenv
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_talisman import Talisman
import psycopg
import bmemcached

# import logging

# logging config setting
# logLevel = logging.ERROR
# logOverwrite = 'w'
# logging.basicConfig(filename='error.log', encoding='utf-8', level=logLevel)

# db/memcache config setting
enableDB: bool = True
enableMemcache: bool = True  # always False on non-macOS

# flask config setting
app: Flask = Flask(__name__)
Talisman(app, content_security_policy=None)
CORS(app)
flaskWebSocket: SocketIO = SocketIO(app)

# load secret from .env
load_dotenv()

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
