# UCI CubeSat Backend Flask Server

Contributor:

Hailey Lin: weixil4@uci.edu,

Jiaen Zhang: jiaenz@uci.edu,

Yi-Ju Tsai, Gabrielle Palar

Make sure you have `python3`, `pip3` installed

The deployed Python server runs on `python-3.10.4`

## Installing prerequisite

Double check `Python3` and `Pip3` are installed

[Homebrew installation for macOS](https://brew.sh/)

`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

`brew install git`

`brew install postgresql`

`brew install python@3.10`

[Chocolatey installation for Windows](https://chocolatey.org/install)

`Run Powershell as Admin`

`Set-ExecutionPolicy AllSigned`

`Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))`

verify `chocolatey` is installed: `choco -?`

`choco install git`

`choco install postgresql`

`choco install python --version=3.10.2`

## Setting up the Python/Flask Backend Server locally

Setup `venv` virtualenv

`cd UCI-CubeSat-Server`

`python3 -m venv venv`

`. venv/bin/activate` for macOS/Linux or `\Scripts\activate` for Windows

`pip install -r 'requirements.txt'`

`flask run`

## Connecting to our SQL Database

`brew install postgresql` for macOS

`choco install postgresql` for Windows

A free SQL database instance was created on [heroku-postgresql](https://devcenter.heroku.com/articles/heroku-postgresql)

Connection via [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

`heroku pg:psql postgresql-solid-33882 --app uci-cubesat-server-dev`

and perform any query in CLI

`SELECT * FROM "two_line_element";`

Connection Information using [DataGrip](https://www.jetbrains.com/datagrip/)

```
Driver: PostgreSQL

Host: ec2-52-73-155-171.compute-1.amazonaws.com

Database: d3cjqhogrcusg1

User: kfjsvitgcfsmqq

Port:5432

Password: <PASSWORD>

URI: jdbc:postgresql://ec2-52-73-155-171.compute-1.amazonaws.com:5432/d3cjqhogrcusg1

Heroku CLI: heroku pg:psql postgresql-solid-33882 --app uci-cubesat-server-dev
```

ElephantSQL DB connection secret is hidden in a `.env` file and stored locally

Inside `/UCI-CubeSat-Server/.env`

Ask in the discord channel for a copy of the `.env` file

## Deployment to Heroku

Deploying to Heroku require significant configuration

The client and server must be deploy to different dyno/app

Example: [Front End](https://uci-cubesat-dashboard.herokuapp.com/), [Back End](https://uci-cubesat-server.herokuapp.com/)

For Python Flask server, Heroku require you to have:

`app.py` at project's root directory

`web: gunicorn app:app` inside `Procfile` at project's root directory

`pip` `requirements.txt` at project's root directory

Adding `Python` build pack
