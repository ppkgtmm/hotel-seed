from sqlalchemy import create_engine, text, Connection
from google.cloud.sql.connector import Connector, IPTypes
from google.cloud import storage
from os import getenv
import pandas as pd
from io import StringIO
from derive import get_booking_addons, get_booking_rooms

table_mapping = {
    "amenities": "addon",
    "bookings": "booking_temp",
    "guests": "guest_temp",
    "room_types": "roomtype",
    "rooms": "room_temp",
    "users": "user_temp",
}


def exec_read_query(file_path: str, conn: Connection):
    with open(file_path) as fp:
        queries = fp.read()
    conn.execute(text(queries))
    conn.commit()


def get_db_connection():
    connector = Connector(IPTypes.PUBLIC)
    return connector.connect(
        getenv("CONNECTION"),
        "pg8000",
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        db=getenv("DB_NAME"),
    )


def download_generated_data():
    bucket = storage.Client().get_bucket(getenv("GCS_BUCKET"))
    for blob in bucket.list_blobs(prefix=getenv("SEED_DIR")):
        blob_name = str(blob.name).split("/")[-1].split(".")[0]
        yield (blob_name, bucket.blob(blob.name).download_as_text())


def populate_source_db(request):
    engine = create_engine("postgresql+pg8000://", creator=get_db_connection)
    conn = engine.connect()
    exec_read_query("scripts/oltp_init.sql", conn)
    (
        pd.read_csv(getenv("LOCATION_FILE"))[["name", "admin"]]
        .rename(columns={"name": "state", "admin": "country"})
        .to_sql("location", conn, index=False, if_exists="append")
    )
    for blob_name, blob_data in download_generated_data():
        data = pd.read_csv(StringIO(blob_data))
        data.to_sql(table_mapping[blob_name], conn, index=False, if_exists="append")
    exec_read_query("scripts/oltp_seed.sql", conn)
    get_booking_rooms(conn).to_sql(
        "booking_room", conn, index=False, if_exists="append"
    )
    get_booking_addons(conn).to_sql(
        "booking_addon", conn, index=False, if_exists="append"
    )
    exec_read_query("scripts/oltp_post.sql", conn)
    conn.close()
    engine.dispose()
    return "success"
