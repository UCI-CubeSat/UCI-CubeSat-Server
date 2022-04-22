import psycopg
from psycopg.rows import dict_row

from src.python.database import dbQueries
from src.python.config.appConfig import dbCredential


connectionConfig = dict(conninfo=dbCredential, autocommit=True)
connectionConfigRowFactory = dict(conninfo=dbCredential, autocommit=True, row_factory=dict_row)


def dbInsertAll(tableName, entryArray: list):
    truncateTable(tableName)

    with psycopg.connect(**connectionConfig) as dbConnection:
        with dbConnection.cursor() as dbCursor:
            for entry in entryArray:
                query = f"INSERT INTO {tableName} VALUES(%s,%s,%s,%s)"
                dbCursor.execute(query, entry)


def dbFetch(queryName, *args):
    with psycopg.connect(**connectionConfig) as dbConnection:
        with dbConnection.cursor() as dbCursor:
            if args:
                dbCursor.execute(dbQueries.queries[queryName](args))
            else:
                dbCursor.execute(dbQueries.queries[queryName]())
            return dbCursor.fetchone()


def dbFetchAll(queryName, *args, **kwargs):
    if 'dict' in kwargs.keys() and kwargs['dict']:
        config = connectionConfigRowFactory
    else:
        config = connectionConfig
    with psycopg.connect(**config) as dbConnection:
        with dbConnection.cursor() as dbCursor:
            try:
                if args:
                    dbCursor.execute(dbQueries.queries[queryName](args))
                else:
                    dbCursor.execute(dbQueries.queries[queryName]())
            except psycopg.errors.UndefinedTable:
                return None

            dbResponse: [()] = dbCursor.fetchall()
            return None if len(dbResponse) == 0 else dbResponse[0] if len(
                dbResponse) == 1 else dbResponse


def dropTable(tableName):
    with psycopg.connect(**connectionConfig) as dbConnection:
        with dbConnection.cursor() as dbCursor:
            dbCursor.execute(dbQueries.queries["dropTable"](tableName))


def truncateTable(tableName):
    with psycopg.connect(**connectionConfig) as dbConnection:
        with dbConnection.cursor() as dbCursor:
            dbCursor.execute(dbQueries.queries["truncateTable"](tableName))
