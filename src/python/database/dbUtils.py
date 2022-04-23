import psycopg2
import psycopg
from psycopg.rows import dict_row

from src.python.database import dbQueries
from src.python.config.appConfig import dbCredential, psycopg2Config


connectionConfig = dict(conninfo=dbCredential, autocommit=True)
connectionConfigRowFactory = dict(
    conninfo=dbCredential,
    autocommit=True,
    row_factory=dict_row)


def insertAll(tableName, entryArray: list):
    truncateTable(tableName)

    with psycopg2.connect(**psycopg2Config) as dbConnection:
        try:
            with dbConnection.cursor() as dbCursor:
                value = ','.join(
                    dbCursor.mogrify(
                        "(%s,%s,%s,%s)",
                        entry).decode("utf-8") for entry in entryArray)
                query = f"INSERT INTO {tableName} VALUES {value}"
                dbCursor.execute(query)
        except psycopg.errors.Error:
            dbConnection.close()


def fetch(queryName, *args):
    with psycopg.connect(**connectionConfig) as dbConnection:
        try:
            with dbConnection.cursor() as dbCursor:
                if args:
                    dbCursor.execute(dbQueries.queries[queryName](args))
                else:
                    dbCursor.execute(dbQueries.queries[queryName]())
                return dbCursor.fetchone()
        except psycopg.errors.Error:
            dbConnection.close()


def fetchAll(queryName, *args, **kwargs):
    if 'dict' in kwargs.keys() and kwargs['dict']:
        config = connectionConfigRowFactory
    else:
        config = connectionConfig
    with psycopg.connect(**config) as dbConnection:
        try:
            with dbConnection.cursor() as dbCursor:
                if args:
                    dbCursor.execute(dbQueries.queries[queryName](args))
                else:
                    dbCursor.execute(dbQueries.queries[queryName]())

                dbResponse: [()] = dbCursor.fetchall()
                return None if len(dbResponse) == 0 else dbResponse[0] if len(
                    dbResponse) == 1 else dbResponse

        except psycopg.errors.Error:
            dbConnection.close()


def dropTable(tableName):
    with psycopg.connect(**connectionConfig) as dbConnection:
        try:
            with dbConnection.cursor() as dbCursor:
                dbCursor.execute(dbQueries.queries["dropTable"](tableName))
        except psycopg.errors.Error:
            dbConnection.close()


def truncateTable(tableName):
    with psycopg.connect(**connectionConfig) as dbConnection:
        try:
            with dbConnection.cursor() as dbCursor:
                dbCursor.execute(dbQueries.queries["truncateTable"](tableName))
        except psycopg.errors.Error:
            dbConnection.close()
