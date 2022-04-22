import urllib
import os
from sys import platform as _platform
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_talisman import Talisman
import psycopg
# import logging

# logging config setting
# logLevel = logging.ERROR
# logOverwrite = 'w'
# logging.basicConfig(filename='error.log', encoding='utf-8', level=logLevel)

# db/memcache config setting
enableDB = True
enableMemcache = _platform == "darwin" and False  # always False on non-macOS

# flask config setting
app = Flask(__name__)
CORS(app)
Talisman(app, content_security_policy=None)

# load secret from .env
load_dotenv()

# Heroku Postgre
dbUrl = os.getenv("DATABASE_URL")
dbUrl = "postgresql" + dbUrl[dbUrl.index(":"):]

# Elephant Postgre
# dbUrl = os.getenv("DB_URL")

# sqlalchemy db config setting
app.config["SQLALCHEMY_DATABASE_URI"] = dbUrl
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# psycopg2 db config setting
_ = psycopg
urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(dbUrl)
dbCredential = dbUrl

# API URL config
satnogsApiKey = os.getenv('SATNOGS_MAP_API_KEY')
apiVersion = "v1"
apiBaseUrl = f"/api/{apiVersion}"
