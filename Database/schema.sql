DROP DATABASE IF EXISTS ImageTinder;
CREATE DATABASE ImageTinder;
USE ImageTinder;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS collection;
DROP TABLE IF EXISTS user_collection;
DROP TABLE IF EXISTS image;
DROP TABLE IF EXISTS user_image;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE collection (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name TEXT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL
);

CREATE TABLE user_collection (
  user_id INTEGER,
  collection_id INTEGER,
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (collection_id) REFERENCES collection(id),
  PRIMARY KEY (user_id, collection_id)
);

CREATE TABLE image (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  file_path TEXT NOT NULL,
  creation_date TIMESTAMP,
  image_location VARCHAR(255)
);

CREATE TABLE user_image (
  user_id INTEGER,
  image_id INTEGER,
  rating TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (image_id) REFERENCES image (id),
  PRIMARY KEY (user_id, image_id)
);


DROP USER IF EXISTS 'ImageTinderApp'@'%';
DROP USER IF EXISTS 'ImageFinder'@'%';
CREATE USER 'ImageTinderApp'@'%' IDENTIFIED BY 'AppPw';
CREATE USER 'ImageFinder'@'%' IDENTIFIED BY 'FinderPw';

GRANT select ON ImageTinder.* TO 'ImageTinderApp'@'%';
GRANT insert ON ImageTinder.collection TO 'ImageTinderApp'@'%';
GRANT insert ON ImageTinder.user TO 'ImageTinderApp'@'%';
GRANT insert ON ImageTinder.user_collection TO 'ImageTinderApp'@'%';
GRANT insert ON ImageTinder.user_image TO 'ImageTinderApp'@'%';

GRANT insert ON ImageTinder.image TO 'ImageFinder'@'%';
GRANT select ON ImageTinder.image TO 'ImageFinder'@'%';

FLUSH PRIVILEGES;
