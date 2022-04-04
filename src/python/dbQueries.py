queries = dict(find_tle_all=lambda: f"SELECT * FROM \"tle\";",
               find_satellite_by_id=lambda identifier: f"SELECT * FROM TLE WHERE \"tle0\" = {identifier};",
               drop_table_by_name=lambda table_name: f"DROP TABLE {table_name};",
               get_tle_timestamp=lambda: "SELECT MIN(\"updated\") FROM \"tle\";",
               truncate_table_by_name=lambda table_name: f"TRUNCATE {table_name};")
