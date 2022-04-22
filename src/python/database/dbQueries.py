queries = dict(
    getTwoLineElementAll=lambda: f"SELECT * FROM \"two_line_element\";",
    getSatellite=lambda identifier: f"SELECT * FROM TLE WHERE \"tle0\" = {identifier};",
    dropTable=lambda table_name: f"DROP TABLE {table_name};",
    getTimestamp=lambda: f"SELECT MIN(\"updated\") FROM \"two_line_element\";",
    truncateTable=lambda table_name: f"TRUNCATE TABLE {table_name};")
