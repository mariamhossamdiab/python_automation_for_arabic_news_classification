
CREATE DATABASE IF NOT EXISTS news;
USE news;
CREATE TABLE IF NOT EXISTS classified_news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Title TEXT,
    Link TEXT,
    Website VARCHAR(255),
    Article_Text TEXT,
	date DATE,
    topic VARCHAR(600),
    classification VARCHAR(255),
    confidence_score VARCHAR(20)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;


CREATE TABLE IF NOT EXISTS trend (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phrase TEXT,
    phrase_count TEXT,
    Website VARCHAR(255),
	date DATEtime
) 
CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
drop table news.classified_news;
select * from news.trend;
select * from news.classified_news;
