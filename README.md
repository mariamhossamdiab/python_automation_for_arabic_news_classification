
I’ve been working on building a puthon automation for news classification — a project that combines web scraping, text processing, and NLP.

<img width="1024" height="432" alt="Gemini_Generated_Image" src="https://github.com/user-attachments/assets/a47ae362-454a-43c8-aa4d-96cb9f8fc53f" />


Here’s a quick overview of what I built 👇
## 📰 Data Collection:
 Scraped news articles from  6 different news websites using both Selenium and Requests, ensuring a diverse dataset.
## 🧹 Text Cleaning & Preprocessing:
 Cleaned and normalized Arabic text (removing HTML tags, special characters, etc.) to prepare for analysis.
🔍 Exploratory Analysis:
 Extracted and visualized the top N-grams (most frequent words and phrases) for each source to uncover key themes.
## 🤖 News Classification:
 - Used a Gemma3 from ollama for topic classification and for dectecting real news from fake ones.
 - used dackdack search go for online search about facts
## 🤖 Threading 
 used threading to enable scraping and at the same time exectracting insights after scraping 1 website 

## google colab
- sends each article to the Gemma3 model (via Ollama) to classify its topic and whether it’s Real or Fake, then saves the classified results.
It processes multiple CSV files, appends predictions, and prepares the data for computing global evaluation metrics.
  
#fastml
- its A virtual environment (venv) is used to isolate your Python project so it doesn’t break other projects or your system Python.
 <img width="1125" height="606" alt="image" src="https://github.com/user-attachments/assets/6bb3c173-04c9-4e59-b32c-4f184aaa793e" />

## Powerbi Dashboard 


![WhatsApp Image 2026-01-11 at 12 49 38 AM](https://github.com/user-attachments/assets/a19ee4e8-1142-42ec-b846-d350c060b37e)
![WhatsApp Image 2026-01-11 at 12 49 01 AM](https://github.com/user-attachments/assets/22ca932d-93bb-44cd-b515-8fb1a383455b)


## website 
- frontend using html , css, vanilla javascript , FastAPI is a backend framework used to build APIs , post man It is a client used to test APIs.
- ![WhatsApp Image 2026-01-06 at 6 22 59 PM](https://github.com/user-attachments/assets/0b72a47a-d1ff-423c-be65-379debb63e1c)

<img width="1600" height="820" alt="image" src="https://github.com/user-attachments/assets/42ac95ba-cbff-4c06-b540-65732a6da052" />



