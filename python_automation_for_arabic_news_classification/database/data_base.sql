select * from news.classified_news;
CREATE DATABASE IF NOT EXISTS news;
USE news;

CREATE TABLE IF NOT EXISTS classified_news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Title TEXT,
    Link TEXT,
    Website VARCHAR(255),
    Article_Text TEXT,
    Predicted_Category VARCHAR(255)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
