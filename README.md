I’ve been working on building a puthon automation for news classification — a project that combines web scraping, text processing, and NLP.
Here’s a quick overview of what I built 👇
## 📰 Data Collection:
 Scraped news articles from 5 different news websites using both Selenium and Requests, ensuring a diverse dataset.
## 🧹 Text Cleaning & Preprocessing:
 Cleaned and normalized Arabic text (removing HTML tags, special characters, etc.) to prepare for analysis.
🔍 Exploratory Analysis:
 Extracted and visualized the top N-grams (most frequent words and phrases) for each source to uncover key themes.
## 🤖 News Classification:
 - Used a multilingual NLP model —
 classla/multilingual-IPTC-news-topic-classifier — via the 🤗 Hugging Face Transformers pipeline for topic classification.
 - lstm  model for dectecting real news from fake ones.
 - llm model to classify news category .
## 🤖 Threading 
 used threading to enable scraping and at the same time exectracting insights after scraping 1 website 

![WhatsApp Image 2025-10-29 at 14 28 39_607026e6](https://github.com/user-attachments/assets/955ec7b3-236d-455f-bae9-7b24b92af173)
![WhatsApp Image 2025-10-31 at 15 15 51_699faf4e](https://github.com/user-attachments/assets/8e6704d4-142b-4bd4-97ef-d6e4f3e1edcd)
## google colab
- sends each article to the Gemma3 model (via Ollama) to classify its topic and whether it’s Real or Fake, then saves the classified results.
It processes multiple CSV files, appends predictions, and prepares the data for computing global evaluation metrics.
- test the model with 91% accuracy
<img width="1003" height="212" alt="image" src="https://github.com/user-attachments/assets/a7acb9d9-d63d-4dc9-ab7b-3282c5850c8b" />
## Powerbi Dashboard 
![WhatsApp Image 2025-11-14 at 00 23 50_69bb897b](https://github.com/user-attachments/assets/99a591b8-f133-4454-a487-0e2c0c226c18)
![WhatsApp Image 2025-11-14 at 00 24 12_3c02dc64](https://github.com/user-attachments/assets/17cdc46e-c666-4e35-9823-ad0e94bbbd66)





