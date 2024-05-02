CREATE TABLE location (
  id SERIAL PRIMARY KEY,
  state VARCHAR(255),
  country VARCHAR(255),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE "user" (
  id SERIAL PRIMARY KEY,
  firstname VARCHAR(255),
  lastname VARCHAR(255),
  gender VARCHAR(25),
  email VARCHAR(255),
  location INT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (location) REFERENCES location (id)
);

CREATE TABLE guest (
  id SERIAL PRIMARY KEY,
  firstname VARCHAR(255),
  lastname VARCHAR(255),
  gender VARCHAR(25),
  email VARCHAR(255),
  dob DATE,
  location INT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (location) REFERENCES location (id)
);

CREATE TABLE addon (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  price FLOAT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE roomtype (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  price FLOAT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE room (
  id SERIAL PRIMARY KEY,
  floor INT,
  number INT,
  roomtype INT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (roomtype) REFERENCES roomtype (id)
);

CREATE TABLE booking (
  id SERIAL PRIMARY KEY,
  "user" INT,
  checkin DATE,
  checkout DATE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY ("user") REFERENCES "user" (id)
);

CREATE TABLE booking_room (
  id SERIAL PRIMARY KEY,
  booking INT,
  room INT,
  guest INT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (booking) REFERENCES booking (id),
  FOREIGN KEY (room) REFERENCES room (id),
  FOREIGN KEY (guest) REFERENCES guest (id)
);

CREATE TABLE booking_addon (
  id SERIAL PRIMARY KEY,
  booking_room INT,
  addon INT,
  quantity INT,
  datetime TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (booking_room) REFERENCES booking_room (id),
  FOREIGN KEY (addon) REFERENCES addon (id)
);


CREATE FUNCTION timestamp_trigger()
RETURNS TRIGGER AS $timestamp_trigger$
DECLARE temp_timestamp TIMESTAMP = CURRENT_TIMESTAMP;
BEGIN
  IF TG_OP = 'INSERT' THEN
      NEW.created_at := temp_timestamp;
  END IF;
  NEW.updated_at := temp_timestamp;
  RETURN NEW;
END;
$timestamp_trigger$ LANGUAGE 'plpgsql';

CREATE TRIGGER location_timestamp_trigger
BEFORE INSERT OR UPDATE ON location
FOR EACH ROW
EXECUTE PROCEDURE timestamp_trigger();

CREATE TRIGGER user_timestamp_trigger
BEFORE INSERT OR UPDATE ON "user"
FOR EACH ROW
EXECUTE PROCEDURE timestamp_trigger();

CREATE TRIGGER guest_timestamp_trigger
BEFORE INSERT OR UPDATE ON guest
FOR EACH ROW
EXECUTE PROCEDURE timestamp_trigger();

CREATE TRIGGER addon_timestamp_trigger
BEFORE INSERT OR UPDATE ON addon
FOR EACH ROW
EXECUTE PROCEDURE timestamp_trigger();

CREATE TRIGGER roomtype_timestamp_trigger
BEFORE INSERT OR UPDATE ON roomtype
FOR EACH ROW
EXECUTE PROCEDURE timestamp_trigger();

CREATE TRIGGER room_timestamp_trigger
BEFORE INSERT OR UPDATE ON room
FOR EACH ROW
EXECUTE PROCEDURE timestamp_trigger();

CREATE TRIGGER booking_timestamp_trigger
BEFORE INSERT OR UPDATE ON booking
FOR EACH ROW
EXECUTE PROCEDURE timestamp_trigger();

CREATE TRIGGER booking_room_timestamp_trigger
BEFORE INSERT OR UPDATE ON booking_room
FOR EACH ROW
EXECUTE PROCEDURE timestamp_trigger();

CREATE TRIGGER booking_addon_timestamp_trigger
BEFORE INSERT OR UPDATE ON booking_addon
FOR EACH ROW
EXECUTE PROCEDURE timestamp_trigger();
