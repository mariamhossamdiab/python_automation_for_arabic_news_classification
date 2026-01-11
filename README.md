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
![WhatsApp Image 2026-01-11 at 12 49 38 AM](https://github.com/user-attachments/assets/7d9dc36c-ea8d-4700-8235-0862f2ab43f7)
![WhatsApp Image 2026-01-11 at 12 49 01 AM](https://github.com/user-attachments/assets/0056a5e2-8161-423e-ab88-be14f26a6769)

## google colab
- sends each article to the Gemma3 model (via Ollama) to classify its topic and whether it’s Real or Fake, then saves the classified results.
It processes multiple CSV files, appends predictions, and prepares the data for computing global evaluation metrics.
- test the model with 91% accuracy
<img width="1003" height="212" alt="image" src="https://github.com/user-attachments/assets/a7acb9d9-d63d-4dc9-ab7b-3282c5850c8b" />

## Powerbi Dashboard 


![WhatsApp Image 2026-01-11 at 12 49 38 AM](https://github.com/user-attachments/assets/a19ee4e8-1142-42ec-b846-d350c060b37e)
![WhatsApp Image 2026-01-11 at 12 49 01 AM](https://github.com/user-attachments/assets/22ca932d-93bb-44cd-b515-8fb1a383455b)




