CREATE PROCEDURE set_sequence ()
LANGUAGE plpgsql AS $set_sequence$
DECLARE location_id INT = (SELECT MAX(id) FROM location);
DECLARE user_id INT = (SELECT MAX(id) FROM "user");
DECLARE guest_id INT = (SELECT MAX(id) FROM guest);
DECLARE addon_id INT = (SELECT MAX(id) FROM addon);
DECLARE roomtype_id INT = (SELECT MAX(id) FROM roomtype);
DECLARE room_id INT = (SELECT MAX(id) FROM room);
DECLARE booking_id INT = (SELECT MAX(id) FROM booking);
DECLARE booking_room_id INT = (SELECT MAX(id) FROM booking_room);
DECLARE booking_addon_id INT = (SELECT MAX(id) FROM booking_addon);
BEGIN
    PERFORM setval('location_id_seq', location_id);
    PERFORM setval('user_id_seq', user_id);
    PERFORM setval('guest_id_seq', guest_id);
    PERFORM setval('addon_id_seq', addon_id);
    PERFORM setval('roomtype_id_seq', roomtype_id);
    PERFORM setval('room_id_seq', room_id);
    PERFORM setval('booking_id_seq', booking_id);
    PERFORM setval('booking_room_id_seq', booking_room_id);
    PERFORM setval('booking_addon_id_seq', booking_addon_id);
END;
$set_sequence$

CALL set_sequence();
