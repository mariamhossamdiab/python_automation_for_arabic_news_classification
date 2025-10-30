I’ve been working on building a puthon automation for news classification — a project that combines web scraping, text processing, and NLP.
Here’s a quick overview of what I built 👇
## 📰 Data Collection:
 Scraped news articles from 5 different news websites using both Selenium and Requests, ensuring a diverse dataset.
## 🧹 Text Cleaning & Preprocessing:
 Cleaned and normalized Arabic text (removing HTML tags, special characters, etc.) to prepare for analysis.
🔍 Exploratory Analysis:
 Extracted and visualized the top N-grams (most frequent words and phrases) for each source to uncover key themes.
## 🤖 News Classification:
 Used a multilingual NLP model —
 classla/multilingual-IPTC-news-topic-classifier — via the 🤗 Hugging Face Transformers pipeline for topic classification.
## 🤖 Threading 
 used threading to enable scraping and at the same time exectracting insights after scraping 1 website 

![WhatsApp Image 2025-10-29 at 14 28 39_607026e6](https://github.com/user-attachments/assets/955ec7b3-236d-455f-bae9-7b24b92af173)
