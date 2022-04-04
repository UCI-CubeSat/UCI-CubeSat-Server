import psycopg2
import psycopg2.extras

from src.python import appConfig, dbModel, dbQueries


# TODO:
#  Switch all DB operation from using SQLAlchemy to psycopg2
#  Need to handle unexpected closed connection, restart connection


def dbWrite(entryArray: list):
    dbCursor = appConfig.dbConnection.cursor()
    dbCursor.execute(dbQueries.queries["truncate_table_by_name"]("tle"))
    appConfig.dbConnection.commit()

    for entry in entryArray:  # This is still using SQLAlchemy
        dbModel.db.session.add(entry)
    dbModel.db.session.commit()


def dbRead(queryName, *args, **kwargs):
    """

    :param queryName: list of query inside dbQueries.py
    :param args: pass parameter into SQL query
    :param kwargs: return a dict-like object if dict=true, else return a list of tuple
    :return:
    """
    if 'dict' in kwargs.keys() and kwargs['dict']:
        dbCursor = appConfig.dbConnection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        dbCursor = appConfig.dbConnection.cursor()
    try:
        if args:
            dbCursor.execute(dbQueries.queries[queryName](args))
        else:
            dbCursor.execute(dbQueries.queries[queryName]())
    except psycopg2.errors.UndefinedTable:
        return None

    dbResponse: [()] = dbCursor.fetchall()
    return None if len(dbResponse) == 0 else dbResponse[0] if len(dbResponse) == 1 else dbResponse


def dbDropTable(tableName):
    dbCursor = appConfig.dbConnection.cursor()
    dbCursor.execute(dbQueries.queries["drop_table_by_name"](tableName))
    appConfig.dbConnection.commit()


def dbTruncateTable(tableName):
    dbCursor = appConfig.dbConnection.cursor()
    dbCursor.execute(dbQueries.queries["truncate_table_by_name"](tableName))
    appConfig.dbConnection.commit()


def dbClose():
    dbModel.db.close_all_sessions()
