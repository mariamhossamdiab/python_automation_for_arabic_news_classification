
I’ve been working on building a puthon automation for news classification — a project that combines web scraping, text processing, and NLP.
<img width="1024" height="432" alt="Gemini_Generated_Image" src="https://github.com/user-attachments/assets/a47ae362-454a-43c8-aa4d-96cb9f8fc53f" />


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

## google colab
- sends each article to the Gemma3 model (via Ollama) to classify its topic and whether it’s Real or Fake, then saves the classified results.
It processes multiple CSV files, appends predictions, and prepares the data for computing global evaluation metrics.
  

## Powerbi Dashboard 


![WhatsApp Image 2026-01-11 at 12 49 38 AM](https://github.com/user-attachments/assets/a19ee4e8-1142-42ec-b846-d350c060b37e)
![WhatsApp Image 2026-01-11 at 12 49 01 AM](https://github.com/user-attachments/assets/22ca932d-93bb-44cd-b515-8fb1a383455b)




