import os
import re
import sys
import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import nltk
from nltk.corpus import stopwords

# === TEXT CLEANING FUNCTIONS ===
def normalize_arabic(text):
    """Normalize Arabic text by removing diacritics, elongation, punctuation, etc."""
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = re.sub(r'ـ+', '', text)  # Tatweel
    text = re.sub(r'[\u0610-\u061A\u064B-\u065F\u06D6-\u06ED]', '', text)  # تشكيل
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'[^\u0600-\u06FF0-9\s]', ' ', text)  # Keep Arabic, digits, spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# Download stopwords if not available
nltk.download('stopwords', quiet=True)
ARABIC_STOPWORDS = set(stopwords.words('arabic'))
ARABIC_STOPWORDS.update(['وذلك','علي','الي','ان','من','اجل','وما','في','وهي','او','حتي','انه','اي','تم','هذا','وهو','ما','خلال'])

def tokenize_arabic(text):
    """Tokenize normalized Arabic text and remove stopwords."""
    text = normalize_arabic(text)
    words = re.findall(r'[\u0600-\u06FF]+', text)
    return [w for w in words if len(w) > 1 and w not in ARABIC_STOPWORDS]


# === MAIN ANALYSIS FUNCTION ===
def analyze_file(fpath):
    """Analyze a single CSV file and save results."""
    print(f"\n📂 Analyzing: {fpath}")

    if not os.path.isfile(fpath):
        print(f"❌ File not found: {fpath}")
        return

    # --- Read CSV file ---
    try:
        df = pd.read_csv(fpath, encoding='utf-8-sig')
    except Exception as e:
        print(f"❌ Failed to read {fpath}: {e}")
        return

    if "Article_Text" not in df.columns:
        print(f"⚠️ Column 'Article_Text' not found in {os.path.basename(fpath)}, skipping")
        return

    # --- Filter valid texts ---
    texts = df["Article_Text"].fillna("").astype(str)
    valid_texts = [t for t in texts if t.strip()]
    if not valid_texts:
        print(f"⚠️ No valid text found in {os.path.basename(fpath)}")
        return

    # --- Normalize + tokenize ---
    norm_texts = [normalize_arabic(t) for t in valid_texts]
    token_lists = [tokenize_arabic(t) for t in norm_texts]
    flat_tokens = [tok for sub in token_lists for tok in sub]

    # === BASIC STATS ===
    stats = {
        "file": os.path.basename(fpath),
        "rows_total": len(df),
        "rows_with_text": len(valid_texts),
        "avg_text_length": int(np.mean([len(t.split()) for t in norm_texts])),
        "total_tokens": len(flat_tokens),
        "unique_tokens": len(set(flat_tokens)),
        "top_token": Counter(flat_tokens).most_common(1)[0][0] if flat_tokens else "",
    }

    # === N-GRAMS ===
    unigram_counts = Counter(flat_tokens)
    top_unigrams = unigram_counts.most_common(10)

    vectorizer = CountVectorizer(
        tokenizer=tokenize_arabic,   
       # token_pattern=r'[\u0600-\u06FF]{2,}',
        ngram_range=(2, 3),
        min_df=2
    )
    X = vectorizer.fit_transform(norm_texts)
    vocab = vectorizer.get_feature_names_out()
    freqs = np.array(X.sum(axis=0)).ravel()
    top_idx = freqs.argsort()[::-1][:10]
    top_ngrams = [(vocab[i], int(freqs[i])) for i in top_idx]

    # === SAVE RESULTS ===
    out_dir = os.path.join(os.path.dirname(fpath), "news_insights_output")
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(fpath))[0]

    unigram_path = os.path.join(out_dir, f"{base}_unigrams.csv")
    ngram_path = os.path.join(out_dir, f"{base}_ngrams.csv")
    summary_path = os.path.join(out_dir, f"{base}_summary.csv")

   # pd.DataFrame(top_unigrams, columns=["word", "count"]).to_csv(unigram_path, index=False, encoding='utf-8-sig')
    pd.DataFrame(top_ngrams, columns=["phrase", "phrase_count"]).to_csv(ngram_path, index=False, encoding='utf-8-sig')
    #pd.DataFrame([stats]).to_csv(summary_path, index=False, encoding='utf-8-sig')

    print(f"✅ Analysis complete for {base}")
    print(f"   - {unigram_path}")
    print(f"   - {ngram_path}")
    print(f"   - {summary_path}")

    return stats


def main(csv_path):
    """Main entry: analyze the passed CSV file only."""
    if not csv_path:
        print("❌ Please provide a CSV file path.")
        return
    analyze_file(csv_path)


if __name__ == "__main__":
    # Example usage:
    #   python nlp_single.py my_data/elwatan.csv
    if len(sys.argv) < 2:
        print("❌ Usage: python nlp_single.py <path_to_csv_file>")
        sys.exit(1)

    csv_path = sys.argv[1]
    main(csv_path)
