import psycopg2
import psycopg
from psycopg.rows import dict_row
from datetime import datetime

from src.python.database import dbQueries
from src.python.config.appConfig import dbCredential, psycopg2Config


connectionConfig = dict(conninfo=dbCredential, autocommit=True)
connectionConfigRowFactory = dict(
    conninfo=dbCredential,
    autocommit=True,
    row_factory=dict_row)


def insertAll(tableName: str, entryArray: list[tuple[str, str, str, datetime]]) -> None:
    truncateTable(tableName)

    with psycopg2.connect(**psycopg2Config) as dbConnection:
        try:
            with dbConnection.cursor() as dbCursor:
                value: str = ','.join(
                    dbCursor.mogrify(
                        "(%s,%s,%s,%s)",
                        entry).decode("utf-8") for entry in entryArray)
                query: str = f"INSERT INTO {tableName} VALUES {value}"
                dbCursor.execute(query)
        except psycopg.errors.Error:
            dbConnection.close()


def fetch(queryName: str, *args: object) -> object | None:
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


def fetchAll(queryName: str,
             *args: object,
             **kwargs: object) -> None | tuple[str, str, str, datetime] | list[tuple[str, str, str, datetime]]:
    if 'dict' in kwargs.keys() and kwargs['dict']:
        config: dict[str, object] = connectionConfigRowFactory
    else:
        config: dict[str, object] = connectionConfig
    with psycopg.connect(**config) as dbConnection:
        try:
            with dbConnection.cursor() as dbCursor:
                if args:
                    dbCursor.execute(dbQueries.queries[queryName](args))
                else:
                    dbCursor.execute(dbQueries.queries[queryName]())

                dbResponse: list[tuple[str, str, str, datetime]] = dbCursor.fetchall()
                return None if len(dbResponse) == 0 else dbResponse[0] if len(
                    dbResponse) == 1 else dbResponse

        except psycopg.errors.Error:
            dbConnection.close()


async def asyncFetchAll(queryName: str,
                        *args: object,
                        **kwargs: object) -> None | tuple[str, str, str, datetime] | list[tuple[str,
                                                                                                str, str, datetime]]:
    if 'dict' in kwargs.keys() and kwargs['dict']:
        config: dict[str, object] = connectionConfigRowFactory
    else:
        config: dict[str, object] = connectionConfig
    async with await psycopg.AsyncConnection.connect(**config) as dbConnection:
        try:
            async with dbConnection.cursor() as dbCursor:
                if args:
                    await dbCursor.execute(dbQueries.queries[queryName](args))
                else:
                    await dbCursor.execute(dbQueries.queries[queryName]())

                dbResponse: list[tuple[str, str, str, datetime]] = await dbCursor.fetchall()
                return None if len(dbResponse) == 0 else dbResponse[0] if len(
                    dbResponse) == 1 else dbResponse

        except psycopg.errors.Error:
            dbConnection.close()
        except Exception as asyncError:
            _ = asyncError
            dbConnection.close()


def dropTable(tableName: str) -> None:
    with psycopg.connect(**connectionConfig) as dbConnection:
        try:
            with dbConnection.cursor() as dbCursor:
                dbCursor.execute(dbQueries.queries["dropTable"](tableName))
        except psycopg.errors.Error:
            dbConnection.close()


def truncateTable(tableName: str) -> None:
    with psycopg.connect(**connectionConfig) as dbConnection:
        try:
            with dbConnection.cursor() as dbCursor:
                dbCursor.execute(dbQueries.queries["truncateTable"](tableName))
        except psycopg.errors.Error:
            dbConnection.close()
