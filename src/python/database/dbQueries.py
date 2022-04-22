queries = dict(
    find_tle_all=lambda: f"SELECT * FROM \"two_line_element\";",
    find_satellite_by_id=lambda identifier: f"SELECT * FROM TLE WHERE \"tle0\" = {identifier};",
    drop_table_by_name=lambda table_name: f"DROP TABLE {table_name};",
    get_tle_timestamp=lambda: "SELECT MIN(\"updated\") FROM \"two_line_element\";",
    truncate_table_by_name=lambda table_name: f"TRUNCATE TABLE {table_name};")
