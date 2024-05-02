from os import getenv, path
from sqlalchemy import create_engine, text

connection_str = getenv("SOURCE_DB")
oltp_sql = path.join(path.abspath(path.dirname(__file__)), "sql/oltp_db.sql")

print("-" * 100)
print("setting up oltp database")

with open(oltp_sql, "r") as fp:
    queries = fp.read()

engine = create_engine(url=connection_str)
connection = engine.connect()

connection.execute(text(queries))
connection.commit()

connection.close()
engine.dispose()

print("oltp database set up done")
print("-" * 100)
