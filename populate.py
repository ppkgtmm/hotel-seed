from datetime import timedelta
import random
from dotenv import load_dotenv
from os import getenv, path
import pandas as pd
from sqlalchemy import create_engine, text
from faker.generator import random
from warnings import filterwarnings

filterwarnings(action="ignore")

load_dotenv()

max_rooms = 5
max_addon_cnt = 5
max_addon_quantity = 3

connection_str = getenv("SOURCE_DB")
data_dir = getenv("SEED_DIR")
seed = getenv("SEED")

random.seed(seed)

room_counts = list(range(1, max_rooms + 1))
sum_count = sum(room_counts)
count_weight = [(max_rooms - rc + 1) / sum_count for rc in room_counts]

overlapping_booking = "(checkin <= '{checkin}' & '{checkin}' <= checkout) | (checkin <= '{checkout}' & '{checkout}' <= checkout) |('{checkin}' <= checkin & '{checkout}' >= checkout)"


def get_booking_rooms():
    guests = pd.read_sql_table("guest", conn, columns=["id"]).id.tolist()
    rooms = pd.read_sql("room", conn, columns=["id"]).id.tolist()
    bookings = pd.read_sql_table("booking", conn).rename({"id": "booking"})
    booking_rooms = pd.DataFrame([], columns=["booking", "room", "guest"])

    for booking in bookings.to_dict(orient="records"):
        checkin, checkout = booking["checkin"], booking["checkout"]
        overlapping = booking_rooms.join(bookings, how="inner", on="booking").query(
            overlapping_booking.format(checkin=checkin, checkout=checkout)
        )
        num_rooms = random.choices(room_counts, weights=count_weight, k=1)[0]
        available_guests = set(guests) - set(overlapping.guest.to_list())
        available_rooms = set(rooms) - set(overlapping.room.to_list())
        assert len(available_guests) >= num_rooms
        guest = random.sample(list(available_guests), k=num_rooms)
        assert len(available_rooms) >= num_rooms
        room = random.sample(list(available_rooms), k=num_rooms)
        booking_room = pd.DataFrame(
            [{"booking": booking["id"], "room": room, "guest": guest}]
        )
        booking_room = booking_room.explode(["room", "guest"])
        booking_rooms = pd.concat([booking_rooms, booking_room])
    return booking_rooms.drop_duplicates()


def get_booking_addons():
    bookings = pd.read_sql_table("booking", conn).rename({"id": "booking"})
    booking_rooms = pd.read_sql_table("booking_room", conn)
    booking_details = booking_rooms.join(
        bookings, how="inner", on="booking", rsuffix="_"
    )
    addons = pd.read_sql_table("addon", conn).id.tolist()
    columns = ["booking_room", "addon", "quantity", "datetime"]
    booking_addons = pd.DataFrame([], columns=columns)

    for booking_detail in booking_details.to_dict(orient="records"):
        checkin, checkout = booking_detail["checkin"], booking_detail["checkout"]

        for date in pd.date_range(checkin, checkout):
            max_addons = random.randint(0, max_addon_cnt)
            chosen_addons = random.choices(addons, k=max_addons)
            booking_addon = [
                {
                    "addon": addon,
                    "quantity": random.randint(1, max_addon_quantity),
                    "datetime": date + timedelta(hours=random.randint(0, 23)),
                }
                for addon in chosen_addons
            ]
            booking_addon = pd.DataFrame(booking_addon)
            booking_addon["booking_room"] = booking_detail["id"]
            booking_addons = pd.concat([booking_addons, booking_addon])
    return booking_addons.drop_duplicates()


engine = create_engine(connection_str)
conn = engine.connect()

room_types = pd.read_csv(path.join(data_dir, "room_types.csv"))
room_types.to_sql("roomtype", conn, index=False, if_exists="append")

addons = pd.read_csv(path.join(data_dir, "addons.csv"))
addons.to_sql("addon", conn, index=False, if_exists="append")

locations = pd.read_csv(path.join(data_dir, "locations.csv"))[["name", "admin"]]
locations = locations.rename(columns={"name": "state", "admin": "country"})
locations.to_sql("location", conn, index=False, if_exists="append")

users = pd.read_csv(path.join(data_dir, "users.csv"))
users.to_sql("user_temp", conn, index=False, if_exists="append")

guests = pd.read_csv(path.join(data_dir, "guests.csv"))
guests.to_sql("guest_temp", conn, index=False, if_exists="append")

rooms = pd.read_csv(path.join(data_dir, "rooms.csv"))
rooms.to_sql("room_temp", conn, index=False, if_exists="append")


bookings = pd.read_csv(path.join(data_dir, "bookings.csv"))
bookings.to_sql("booking_temp", conn, index=False, if_exists="append")

with open("scripts/oltp_seed.sql") as fp:
    queries = fp.read()

conn.execute(text(queries))
conn.commit()

booking_rooms = get_booking_rooms()
booking_rooms.to_sql("booking_room", conn, index=False, if_exists="append")
conn.commit()

booking_addons = get_booking_addons()
booking_addons.to_sql("booking_addon", conn, index=False, if_exists="append")
conn.commit()

with open("scripts/oltp_post.sql") as fp:
    queries = fp.read()

conn.execute(text(queries))
conn.commit()

conn.close()
engine.dispose()
