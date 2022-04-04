import urllib
import os
from sys import platform as _platform
from dotenv import load_dotenv
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS
import logging

# logging config setting
logLevel = logging.DEBUG
logOverwrite = 'w'
logging.basicConfig(filename='server.log', encoding='utf-8', level=logLevel)

# db/memcache config setting
enableDB = True
enableMemcache = _platform == "darwin" and False  # always False on non-macOS

# flask config setting
app = Flask(__name__)
CORS(app)

# load secret from .env
load_dotenv()
dbUrl = os.getenv('DB_URL')

# sqlalchemy db config setting
app.config["SQLALCHEMY_DATABASE_URI"] = dbUrl
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# psycopg2 db config setting
urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(dbUrl)
dbConnection = psycopg2.connect(database=url.path[1:],
                                user=url.username,
                                password=url.password,
                                host=url.hostname,
                                port=url.port,
                                options='-c statement_timeout=60000')

# API URL config
apiVersion = "v1"
apiBaseUrl = f"/api/{apiVersion}"
