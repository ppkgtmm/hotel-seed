from faker.generator import random
import pandas as pd
from os import getenv
from datetime import timedelta
from sqlalchemy import Connection


max_rooms = 5
max_addon_cnt = 5
max_addon_quantity = 3

seed = getenv("SEED")

random.seed(seed)

room_counts = list(range(1, max_rooms + 1))
sum_count = sum(room_counts)
count_weight = [(max_rooms - rc + 1) / sum_count for rc in room_counts]

overlapping_booking = "(checkin <= '{checkin}' & '{checkin}' <= checkout) | (checkin <= '{checkout}' & '{checkout}' <= checkout) |('{checkin}' <= checkin & '{checkout}' >= checkout)"


def get_booking_rooms(conn: Connection):
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


def get_booking_addons(conn: Connection):
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
                    "datetime": date
                    + timedelta(
                        hours=random.randint(0, 23), minutes=random.choice([0, 30])
                    ),
                }
                for addon in chosen_addons
            ]
            booking_addon = pd.DataFrame(booking_addon)
            booking_addon["booking_room"] = booking_detail["id"]
            booking_addons = pd.concat([booking_addons, booking_addon])
    return booking_addons.drop_duplicates()
