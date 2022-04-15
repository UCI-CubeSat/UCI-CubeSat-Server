# CubeSAT Satellite Server Dashboard

Make sure you have `python3`, `pip3` installed

The deployed Python server runs on `python-3.10.4`

## Installing prerequisite

Double check `Python3` and `Pip3` are installed

## Setting up the Python/Flask Backend Server locally

Setup `venv` virtualenv

`cd UCI-CubeSat-Server`

`python3 -m venv venv`

`. venv/bin/activate`

`pip install -r 'requirements.txt'`

`flask run`

## Connecting to our SQL Database

`brew install postgresql` for macOS

`choco install postgresql` for Windows

A free SQL database instance was created on [elephantSQL](https://www.elephantsql.com/)

Connection Information using [DataGrip](https://www.jetbrains.com/datagrip/)

```
Driver: PostgreSQL

Host: castor.db.elephantsql.com

User: omoglffn

Password: Ask for password

URL: jdbc:postgresql://castor.db.elephantsql.com/
```

ElephantSQL DB connection secret is hidden in a `.env` file and stored locally

Inside `/UCI-CubeSat-Server/.env`

Paste this line: `DB_URL=postgresql://omoglffn:<PASSWORD_GOES_HERE>@castor.db.elephantsql.com/omoglffn`

## Deployment to Heroku

Deploying to Heroku require significant configuration

The client and server must be deploy to different dyno/app

Example: [Front End](https://uci-cubesat-dashboard.herokuapp.com/), [Back End](https://uci-cubesat-server.herokuapp.com/)

For Python Flask server, Heroku require you to have:

`app.py` at project's root directory

`web: gunicorn app:app` inside `Procfile` at project's root directory

`pip` `requirements.txt` at project's root directory

Adding `Python` build pack
