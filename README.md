# UCI CubeSat Backend Flask Server

## Contributor:

Hailey Lin: weixil4@uci.edu,

Jiaen Zhang: jiaenz@uci.edu,

Yi-Ju Tsai, 

Gabrielle Palar

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

1. Setup virtual environment

    `cd UCI-CubeSat-Server`

    `python3 -m venv venv`


2. Activate venv: 

    macOS/Linux: `. venv/bin/activate`

    Windows: `venv\Scripts\activate`


3. Install postgreSQL:

   macOS/Linux: `brew install postgresql`

   Windows: `choco install postgresql`


4. Install requirements.txt: `pip3 install -r 'requirements.txt'`


5. Create `.env` file
    
    Create a new file under the UCI-CubeSat-Server root folder, named `.env`

    Ask in the discord channel for a copy of the `.env` file.


6. Run Flask: `flask run`

    Reopen your IDE and retry if `flask run` does not work initially

## Connecting to SQL Database

1. Double check you have PostgreSQL installed: `pg_config --version`

    More information about our database information can be found on: [heroku-postgresql](https://devcenter.heroku.com/articles/heroku-postgresql)


2. Access Database:
    
    a. Command Line Interface([CLI](https://devcenter.heroku.com/articles/heroku-cli))

       heroku pg:psql postgresql-solid-33882 --app uci-cubesat-server-dev
       
       SELETCT * FROM "two_line_element"; 

    b. DataGrip

   [ElephantSQL INFO Dashboard](https://api.elephantsql.com/console/67aa07b9-8289-4754-a566-920acca61de2/details?)
   
   Elephant SQL is a software-as-a-service company that host PostgreSQL databases and handles the server configuration, backups and data connections on top of AWS. 

   1. Visit ElephantSQL Dashboard to access connection credential information 
   
   2. Open DataGrip 
   
   3. Open manage data sources using <kbd>command</kbd>+<kbd>;</kbd>
   
   4. Click on the add button on the top left corner, find PostgreSql, fill in the config based on ElephantSQL
      1. DG[Host] = ElephantSQL[Server]
      2. DG[User] = ElephantSQL[User & Default Database]
      3. DG[Password] = ElephantSQL[password]
      4. DG[Database] = ElephantSQL[User & Default Database]
      5. DG[URL] = jdbc:postgresql://castor.db.elephantsql.com/omoglffn
      6. Click on "Test Connection" 
      7. If Succeed, click on apply and OK
      
   5. Now, you can write SQL query inside console. To open the console, use <kbd>shift</kbd> + <kbd>command</kbd> + <kbd>L</kbd> 


## Run FullStack Web App
1. cd to UCI-CubeSat-Server:

   create [venv environment](https://github.com/UCI-CubeSat/UCI-CubeSat-Server#setting-up-the-pythonflask-backend-server-locally)

   `flask run`
2. cd to UCI-CubeSat-Dashboard:

   `npm start`


## Deployment to Heroku

Deploying to Heroku require significant configuration

The client and server must be deploy to different dyno/app

Example: [Front End](https://uci-cubesat-dashboard.herokuapp.com/), [Back End](https://uci-cubesat-server.herokuapp.com/)

For Python Flask server, Heroku require you to have:

`app.py` at project's root directory

`web: gunicorn app:app` inside `Procfile` at project's root directory

`pip` `requirements.txt` at project's root directory

Adding `Python` build pack
