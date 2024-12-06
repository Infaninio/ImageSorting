DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS collection;
DROP TABLE IF EXISTS user_collection;
DROP TABLE IF EXISTS image;
DROP TABLE IF EXISTS user_image;

CREATE TABLE user (
  id INTEGER PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE collection (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  best_images TEXT
);

CREATE TABLE user_collection (
  user_id INTEGER,
  collection_id INTEGER,
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (collection_id) REFERENCES collection(id),
  PRIMARY KEY (user_id, collection_id)
);

CREATE TABLE image (
  id INTEGER PRIMARY KEY,
  file_path TEXT NOT NULL,
  creation_date TIMESTAMP,
  image_location VARCHAR(255)
);

CREATE TABLE user_image (
  user_id INTEGER,
  image_id INTEGER,
  rating FLOAT NOT NULL,
  deleted BOOLEAN NOT NULL default 0,
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (image_id) REFERENCES image (id),
  PRIMARY KEY (user_id, image_id)
);
