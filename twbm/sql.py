import sqlite3

import aiosql

queries = aiosql.from_path("../sql/queries.sql", "sqlite3")

if __name__ == "__main__":
    # db_url = '../test/tests_data/test.db'
    db_url = "./bm2.db"
    conn = sqlite3.connect(db_url)
    print(queries)
    # r = queries.get_all(conn)
    # print(r)
    r = queries.create_db(conn)
    print(r)
