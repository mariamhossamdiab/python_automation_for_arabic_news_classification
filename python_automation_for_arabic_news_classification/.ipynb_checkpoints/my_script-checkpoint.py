# my_script.py

# --- Your original imports ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from lxml import html
import requests
import time
import pandas as pd
import re
from selenium.webdriver.chrome.options import Options  
import tempfile
import os
import ssl
from urllib3 import poolmanager
from requests.adapters import HTTPAdapter
import urllib3
def remove_emojis(text):
    if not isinstance(text, str) or not text:
        return text
    # Comprehensive emoji regex pattern
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# Disable SSL warnings for fallback requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---- CONFIG ----
user_data_dir = tempfile.mkdtemp()
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")


OUTPUT_PATH = os.path.join(os.getcwd(), "my_data")
os.makedirs(OUTPUT_PATH, exist_ok=True)


# ---- CUSTOM SSL HANDLER ----
class SSLAdapter(HTTPAdapter):
    """Adapter that enables legacy SSL renegotiation for sites with old certificates."""
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        # Allow legacy server connections (fixes youm7.com SSL)
        ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
        self.poolmanager = poolmanager.PoolManager(*args, ssl_context=ctx, **kwargs)


# Create a global session using SSLAdapter
session = requests.Session()
session.mount("https://", SSLAdapter())
session.mount("http://", HTTPAdapter())


# ---- HELPERS ----
def text_proces(mess):
    return [re.sub(r'[^ء-يa-zA-Z0-9\s]', '', str(t)).lower() for t in mess]


def safe_get(url, retries=3, delay=3, timeout=15):
    """Safely perform GET requests with retries, SSL fallback, and timeout."""
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response
        except requests.exceptions.SSLError as e:
            print(f"[WARN] SSL error on {url} (attempt {attempt}/{retries}): {e}")
            try:
                # fallback: ignore SSL verification
                response = requests.get(url, verify=False, timeout=timeout)
                response.raise_for_status()
                response.encoding = 'utf-8'
                return response
            except Exception as e2:
                print(f"[WARN] SSL fallback failed: {e2}")
        except requests.exceptions.RequestException as e:
            print(f"[WARN] Failed to fetch {url} (attempt {attempt}/{retries}): {e}")
        time.sleep(delay)
    print(f"[ERROR] Giving up on {url} after {retries} attempts.")
    return None


# ---- SAVE FUNCTION (CSV version) ----
def safe_save_csv(df, filename):
    """Save DataFrame as UTF-8 CSV (handles Arabic text safely)."""
    try:
        csv_path = os.path.join(OUTPUT_PATH, filename)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')  # utf-8-sig ensures Arabic text displays correctly
        print(f"[INFO] Saved {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save {filename}: {e}")


# =========================
# MAIN SCRAPER FUNCTION
# =========================
def main():
    print("\n🚀 Starting scraping run...")
# --- elbashayer ---
    try:
        url = "https://elbashayer.com/"
        response = safe_get(url)
        if response:
            tree = html.fromstring(response.text)
            titles = tree.xpath('//h3[@class="jeg_post_title"]/a/text()')
            links = tree.xpath('//h3[@class="jeg_post_title"]/a/@href')
            titles = [t.strip() for t in titles]
            df = pd.DataFrame({"Title": text_proces(titles), "Link": links})
            df['website'] = 'elbashayer.com'
            article_texts = []
            for link in df["Link"]:
                resp = safe_get(link)
                if not resp:
                    article_texts.append("Not found")
                    continue
                try:
                    tree = html.fromstring(resp.text)
                    paras = tree.xpath("//div[contains(@class, 'content-inner')]//p")
                    text = "\n".join(
                                p.text_content().strip()
                                for p in paras
                                if p.text_content() and p.text_content().strip()
                            )
                    article_texts.append(text if text else "Not found")
                except Exception:
                    article_texts.append("Not found")
            df["Article_Text"] = article_texts
            df['Article_Text'] = df['Article_Text'].apply(remove_emojis)
            safe_save_csv(df, "elbashayer.csv")
    except Exception as e:
        print(f"[ERROR] elshrouk section failed: {e}")
    # --- EL SHOROUK ---
    # --- EL SHOROUK ---
    try:
        url = "https://www.shorouknews.com/"
        response = safe_get(url)
        if response:
            tree = html.fromstring(response.text)
            titles = tree.xpath('//div[@class="text"]/h3/a/text()')
            links = tree.xpath('//div[@class="text"]/h3/a/@href')
            titles = [t.strip() for t in titles]
            links = ["https://www.shorouknews.com" + l for l in links]
            df = pd.DataFrame({"Title": text_proces(titles), "Link": links})
            df['website'] = 'shorouknews.com'
            article_texts = []
            for link in df["Link"]:
                resp = safe_get(link)
                if not resp:
                    article_texts.append("Not found")
                    continue
                try:
                    tree = html.fromstring(resp.text)
                    paras = tree.xpath("//div[contains(@class, 'eventContent')]//p")
                    text = "\n".join(p.text_content().strip() for p in paras if p.text_content())
                    article_texts.append(text if text else "Not found")
                except Exception:
                    article_texts.append("Not found")
            df["Article_Text"] = article_texts
            df['Article_Text'] = df['Article_Text'].apply(remove_emojis)
            safe_save_csv(df, "elshrouk.csv")
    except Exception as e:
        print(f"[ERROR] elshrouk section failed: {e}")

    # --- EL WATAN ---
    try:
        fathi = webdriver.Chrome(options=chrome_options)
        fathi.get("https://www.elwatannews.com/")
        articles = fathi.find_elements("xpath", "//a[contains(@href, '/news/details/')]")
        links, titles = [], []
        for a in articles:
            try:
                link = a.get_attribute("href")
                title = a.get_attribute("title") or ""
                links.append(link)
                titles.append(title)
            except Exception as e:
                print("[WARN] Skipping bad article:", e)
        fathi.quit()

        df = pd.DataFrame({"Title": text_proces(titles), "Link": links})
        df['website'] = 'elwatannews.com'
        df.drop_duplicates(subset=['Link'], inplace=True)
        article_texts = []
        for link in df["Link"]:
            resp = safe_get(link)
            if not resp:
                article_texts.append("Not found")
                continue
            try:
                tree = html.fromstring(resp.text)
                paragraphs = tree.xpath("//div[@class='content-text-wrapper']//p/text()")
                text = "\n".join(p.strip() for p in paragraphs if p.strip())
                article_texts.append(text if text else "Not found")
            except Exception:
                article_texts.append("Not found")
        df["Article_Text"] = article_texts
        df['Article_Text'] = df['Article_Text'].apply(remove_emojis)
        safe_save_csv(df, "elwatan.csv")
    except WebDriverException as e:
        print(f"[ERROR] WebDriver failed for elwatan: {e}")

    # --- EL MASRY ELYOUM ---
    try:
        fathi = webdriver.Chrome(options=chrome_options)
        fathi.get("https://www.almasryalyoum.com/")
        articles = fathi.find_elements("xpath", "//a[contains(@href, '/news/details/')]")
        links, titles = [], []
        for a in articles:
            try:
                link = a.get_attribute("href")
                title = a.get_attribute("title") or ""
                links.append(link)
                titles.append(title)
            except Exception:
                continue
        fathi.quit()

        df = pd.DataFrame({"Title": text_proces(titles), "Link": links})
        df['website'] = 'almasryalyoum.com'
        df.drop_duplicates(subset=['Link'], inplace=True)
        article_texts = []
        for link in df["Link"]:
            resp = safe_get(link)
            if not resp:
                article_texts.append("Not found")
                continue
            try:
                tree = html.fromstring(resp.text)
                paragraphs = tree.xpath("//div[@id='NewsStory']//p/text()")
                text = "\n".join(p.strip() for p in paragraphs if p.strip())
                article_texts.append(text if text else "Not found")
            except Exception:
                article_texts.append("Not found")
        df["Article_Text"] = article_texts
        df['Article_Text'] = df['Article_Text'].apply(remove_emojis)
        safe_save_csv(df, "elmasrielyoum.csv")
    except Exception as e:
        print(f"[ERROR] masrielyoum section failed: {e}")

    # --- YOUM7 ---
    try:
        fathi = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        fathi.set_page_load_timeout(60)
        fathi.get("https://www.youm7.com/")
        news_elements = fathi.find_elements("xpath", '//h3/a')
        titles = [n.text.strip() for n in news_elements]
        links = [n.get_attribute("href") for n in news_elements]
        fathi.quit()

        df = pd.DataFrame({"Title": text_proces(titles), "Link": links})
        df['website'] = 'youm7.com'
        article_texts = []
        for link in df["Link"]:
            resp = safe_get(link)
            if not resp:
                article_texts.append("Not found")
                continue
            try:
                tree = html.fromstring(resp.text)
                paragraphs = tree.xpath("//div[@id='articleBody']//p//text()")
                text = "\n".join(p.strip() for p in paragraphs if p.strip())
                article_texts.append(text if text else "Not found")
            except Exception:
                article_texts.append("Not found")
        df["Article_Text"] = article_texts
        df['Article_Text'] = df['Article_Text'].apply(remove_emojis)
        safe_save_csv(df, "youm7.csv")
    except TimeoutException:
        print("[WARN] youm7 timed out, skipping...")
    except Exception as e:
        print(f"[ERROR] youm7 section failed: {e}")

    # --- MASRAWY ---
    try:
        fathi = webdriver.Chrome(options=chrome_options)
        fathi.get("https://www.masrawy.com/")
        news_elements = fathi.find_elements("xpath", '//a[@class="imageCntnr"]')
        titles = [n.get_attribute("title") for n in news_elements]
        links = [n.get_attribute("href") for n in news_elements]
        fathi.quit()

        df = pd.DataFrame({"Title": text_proces(titles), "Link": links})
        df['website'] = 'masrawy.com'
        article_texts = []
        for link in df["Link"]:
            time.sleep(2)
            resp = safe_get(link)
            if not resp:
                article_texts.append("Not found")
                continue
            try:
                tree = html.fromstring(resp.content)
                text = tree.xpath("//div[@class='ArticleDetails details']/p/text()")
                article_texts.append("\n".join(text) if text else "Not found")
            except Exception:
                article_texts.append("Not found")
        df["Article_Text"] = article_texts
        df['Article_Text'] = df['Article_Text'].apply(remove_emojis)
        safe_save_csv(df, "masrawy.csv")
    except Exception as e:
        print(f"[ERROR] masrawy section failed: {e}")

    print("\n✅ Script finished. All reachable sites processed.")


if __name__ == "__main__":
    main()
