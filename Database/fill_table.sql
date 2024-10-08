INSERT INTO user (id, email, password) VALUES
(NULL, 'user1@example.com', 'password123'),
(NULL, 'user2@example.com', 'securepassword'),
(NULL, 'user3@example.com', 'usersspassword'),
(NULL, 'user4@example.com', 'password456'),
(NULL, 'user5@example.com', 'password789'),
(NULL, 'user6@example.com', 'securepassword321'),
(NULL, 'user7@example.com', 'userspassword123'),
(NULL, 'user8@example.com', 'password123456'),
(NULL, 'user9@example.com', 'passwordabc'),
(NULL, 'user10@example.com', 'securepasswordxyz');

INSERT INTO collection (id, name, start_date, end_date) VALUES
(NULL, 'collection1', '2023-06-01', '2023-09-01'),
(NULL, 'collection2', '2024-07-15', '2024-07-20'),
(NULL, 'collection3', '2024-03-01', '2024-03-31');

INSERT INTO user_collection (user_id, collection_id) VALUES
(1, 1),
(1, 2),
(1, 3),

(2, 1),
(2, 2),
(2, 3),

(3, 1),
(3, 2),
(3, 3),

(4, 1),
(4, 2),

(5, 2),
(5, 3),

(6, 1),
(6, 3),

(7, 1),
(8, 2),
(9, 3);

INSERT INTO image (id, file_path, creation_date, image_location) VALUES
(NULL, '/path/to/image1.jpg', '2023-06-10 08:00:00', 'Beach'),
(NULL, '/path/to/image2.jpg', '2023-07-20 14:30:00', 'Mountains'),
(NULL, '/path/to/image3.jpg', '2023-07-17 10:45:00', 'Park'),
(NULL, '/path/to/image4.jpg', '2023-08-30 10:45:00', 'Park'),

(NULL, '/path/to/image5.jpg', '2023-07-15 08:00:00', 'Beach'),
(NULL, '/path/to/image6.jpg', '2023-07-16 14:30:00', 'Mountains'),
(NULL, '/path/to/image7.jpg', '2024-07-17 10:45:00', 'Park'),
(NULL, '/path/to/image8.jpg', '2023-07-20 08:00:00', 'Beach'),

(NULL, '/path/to/image9.jpg', '2023-07-20 14:30:00', 'Mountains'),
(NULL, '/path/to/image10.jpg', '2024-07-17 10:45:00', 'Park'),
(NULL, '/path/to/image11.jpg', '2024-07-17 10:45:00', 'Park'),
(NULL, '/path/to/image12.jpg', '2024-03-10 12:00:00', 'Forest');

INSERT INTO user_image (user_id, image_id, rating) VALUES
(4, 3, 'like'),
(4, 4, 'dislike'),
(4, 1, 'dislike'),
(4, 2, 'like'),
(7, 3, 'dislike'),
(6, 4, 'like'),
(7, 1, 'like'),
(2, 2, 'like'),
(3, 1, 'dislike'),
(1, 4, 'dislike'),

(2, 7, 'like'),
(2, 8, 'like'),
(5, 7, 'dislike'),
(1, 6, 'like'),
(4, 8, 'dislike'),
(3, 6, 'like'),
(5, 5, 'like'),
(1, 5, 'dislike'),
(4, 5, 'dislike'),

(6, 9, 'dislike'),
(3, 10, 'like'),
(6, 12, 'like'),
(2, 9, 'like'),
(5, 9, 'dislike'),
(2, 11, 'dislike'),
(9, 12, 'like'),
(6, 11, 'dislike');
