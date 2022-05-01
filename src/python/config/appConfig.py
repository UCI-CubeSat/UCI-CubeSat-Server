import urllib
import os
from sys import platform as _platform
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
enableDB = True
enableMemcache = _platform == "darwin" and False  # always False on non-macOS

# flask config setting
flaskServer = Flask(__name__)
Talisman(flaskServer, content_security_policy=None)
CORS(flaskServer)
flaskWebSocket = SocketIO(flaskServer)

# load secret from .env
load_dotenv()

# Heroku Memcached
memcached = bmemcached.Client(os.environ.get('MEMCACHEDCLOUD_SERVERS').split(','),
                       os.environ.get('MEMCACHEDCLOUD_USERNAME'),
                       os.environ.get('MEMCACHEDCLOUD_PASSWORD'))

# Heroku Postgre
dbUrl = os.getenv("DATABASE_URL")
dbUrl = "postgresql" + dbUrl[dbUrl.index(":"):]

# Elephant Postgre
# dbUrl = os.getenv("DB_URL")

# sqlalchemy db config setting
flaskServer.config["SQLALCHEMY_DATABASE_URI"] = dbUrl
flaskServer.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# psycopg db config setting
_ = psycopg
urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(dbUrl)
dbCredential = dbUrl
psycopg2Config = dict(database=url.path[1:],
                      user=url.username,
                      password=url.password,
                      host=url.hostname,
                      port=url.port,
                      options='-c statement_timeout=10000')

# API URL config
satnogsApiKey = os.getenv('SATNOGS_MAP_API_KEY')
apiVersion = "v1"
apiBaseUrl = f"/api/{apiVersion}"
