INSERT INTO "user" (firstname, lastname, gender, email, location)
SELECT ut.firstname, ut.lastname, ut.gender, ut.email, l.id
FROM user_temp ut
LEFT JOIN location l
ON ut.state = l.state AND ut.country = l.country;

DROP TABLE user_temp;

INSERT INTO guest (firstname, lastname, gender, email, dob, location)
SELECT gt.firstname, gt.lastname, gt.gender, gt.email, gt.dob::DATE, l.id
FROM guest_temp gt
LEFT JOIN location l
ON gt.state = l.state AND gt.country = l.country;

DROP TABLE guest_temp;

INSERT INTO room (floor, number, roomtype)
SELECT rt.floor, rt.number, t.id
FROM room_temp rt
LEFT JOIN roomtype t
ON rt.type = t.name;

DROP TABLE room_temp;

INSERT INTO booking ("user", checkin, checkout)
SELECT u.id, bt.checkin::date, bt.checkout::date
FROM booking_temp bt
LEFT JOIN "user" u
ON bt."user" = u.email;

DROP TABLE booking_temp;
