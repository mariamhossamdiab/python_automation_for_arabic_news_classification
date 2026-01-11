
def get_topic_specific_metrics(topic):
    """
    Return evaluation metrics based on the exact topic category you provided.
    """
    topic = topic.lower().strip()
    topic_rules = {
        "arts": """
            - Verify artist/institution names against known databases
            - Check exhibition dates and locations for accuracy
            - Flag subjective superlatives (e.g., "greatest", "unprecedented")
            - Validate cultural event details
            - Detect fabricated art market prices
        """,

        "crime": """
            - Cross-check location, date, and victim details
            - Verify police/court official statements
            - Flag unattributed crime statistics
            - Detect sensationalist crime language (e.g., "horrific", "bloodbath")
            - Check for named suspects/victims without official confirmation
            - Validate legal terminology accuracy
        """,

        "disaster and accident": """
            - Verify casualty numbers with official sources
            - Check geographic location accuracy
            - Flag fear-mongering language (e.g., "catastrophic", "apocalyptic")
            - Validate emergency response details
            - Cross-reference timeline with known events
            - Detect exaggerated damage estimates
        """,

        "economy": """
            - Verify numerical data (GDP, inflation, exchange rates)
            - Validate company/institution names
            - Check economic terminology correctness
            - Flag unattributed market predictions
            - Detect misleading percentage comparisons
            - Verify government policy references
            - Check for unrealistic growth/loss claims
        """,

        "education": """
            - Verify educational institution existence
            - Validate exam results and statistics
            - Check ministry/government policy references
            - Flag fabricated reform announcements
            - Detect misleading international ranking claims
            - Verify scholarship/funding program details
        """,

        "environment": """
            - Validate scientific terminology and data
            - Cross-check climate statistics with research
            - Flag alarmist language without evidence
            - Verify environmental organization citations
            - Detect pseudoscience or conspiracy theories
            - Check consistency with scientific consensus
        """,

        "health": """
            - Verify medical terminology accuracy
            - Flag miracle cure or panic-inducing claims
            - Check for WHO/health ministry citations
            - Detect pseudoscience or alternative medicine fraud
            - Validate drug/treatment names
            - Cross-reference medical statistics
            - Flag unverified health advice
        """,

        "human interest": """
            - Assess emotional manipulation level
            - Check narrative consistency and plausibility
            - Verify named individuals (if public figures)
            - Flag overly dramatic storytelling
            - Detect fabricated heartwarming/tragic stories
            - Check for privacy violations
        """,

        "labour": """
            - Verify union/organization names
            - Check employment statistics accuracy
            - Validate labour law references
            - Flag exaggerated strike/protest numbers
            - Cross-reference wage/unemployment data
            - Detect biased pro-employer or pro-worker language
        """,

        "lifestyle and leisure": """
            - Identify clickbait headlines
            - Distinguish opinion from factual reporting
            - Verify brand/celebrity names
            - Check for undisclosed advertising
            - Flag sensationalized lifestyle trends
            - Detect fabricated social media trends
        """,

        "politics": """
            - Verify politician names, titles, and parties
            - Check for propaganda indicators
            - Detect political bias or loaded language
            - Validate government policy references
            - Cross-check political event details
            - Flag unattributed quotes from officials
            - Detect conspiracy theories
            - Verify electoral/polling data
        """,

        "religion and belief": """
            - Validate religious institution names
            - Check for extremist language indicators
            - Verify religious scholar attributions
            - Detect fabricated fatwas or religious rulings
            - Flag sectarian bias or hate speech
            - Validate religious event dates and locations
        """,

        "science and technology": """
            - Verify scientific/technical terminology
            - Check for peer-reviewed research citations
            - Flag claims contradicting established science
            - Detect exaggerated tech breakthrough claims
            - Validate researcher/institution names
            - Cross-check with scientific databases
            - Flag pseudoscience indicators
        """,

        "society": """
            - Verify social statistics and surveys
            - Check named organizations/institutions
            - Flag stereotyping or generalization
            - Detect fabricated social trends
            - Validate demographic data
            - Cross-check cultural event details
        """,

        "sport": """
            - Verify team names, players, and officials
            - Check match results and scores
            - Validate sporting event dates/locations
            - Cross-check tournament participants with official lists
            - Flag transfer rumors without sources
            - Detect exaggerated performance claims
            - If non-eligible teams appear in tournament groups (e.g., non-African teams in AFCON), classify as Fake immediately
            - Reject any group lists that contradict the official tournament structure
        """,

        "war": """
            - Verify military terminology and locations
            - Check casualty figures against official sources
            - Detect propaganda language
            - Flag unverified combat reports
            - Validate military official statements
            - Cross-check with international news sources
            - Detect emotional manipulation tactics
        """,

        "weather": """
            - Verify meteorological terminology
            - Check temperature/precipitation accuracy
            - Flag catastrophic language without data
            - Validate weather service citations
            - Cross-reference predictions with official forecasts
            - Detect seasonal impossibilities
        """,

        "unknown": """
            - Apply general credibility assessment
            - Check linguistic consistency
            - Verify named entities when possible
            - Flag sensationalist language
            - Assess logical coherence
            - Check for source attribution
        """
    }

    return topic_rules.get(topic, """
        - Apply general linguistic, factual, and sentiment-based metrics
        - Flag missing source attribution
        - Check for logical inconsistencies
        - Detect sensationalist language patterns
    """)

import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote
MAX_QUERY_CHARS = 300  # safe for search engines

def safe_search_query(text):
    return text[:MAX_QUERY_CHARS]
TRUSTED_DOMAINS = {
    "youm7.com", "almasryalyoum.com", "elwatannews.com", "elshorouknews.com",
    "ahram.org.eg", "akhbarelyom.com", "masrawy.com", "bbc.com", "cnn.com",
    "reuters.com", "skynewsarabia.com", "alarabiya.net",
    "dostor.org", "sadaelbalad.com", "aawsat.com",
    "aljazeera.net", "bbc.co.uk", "france24.com", "dw.com", "trtworld.com",
    "middleeasteye.net", "vetogate.com", "alwafd.news", "alborsaanews.com",
    "almalnews.com", "alnaharegypt.com", "cairo24.com", "alkhaleej.ae",
    "emaratalyoum.com", "alittihad.ae", "alayam.com", "alqabas.com",
    "alanba.com.kw", "alrai.com", "alghad.com", "addustour.com",
    "rai.alyoum.com"
}


# =========================
# Helper Functions
# =========================

def extract_real_url(ddg_url):
    parsed = urlparse(ddg_url)
    qs = parse_qs(parsed.query)
    if "uddg" in qs:
        return unquote(qs["uddg"][0])
    return ddg_url


def scrape_text(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return ""

    soup = BeautifulSoup(response.text, "lxml")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
MAX_CHARS = 4000

def safe_text(text):
    return text[:MAX_CHARS]


# =========================
# MAIN FUNCTION YOU NEED
# =========================

def search_and_extract_facts(search_query, max_facts=3):
    """
    Returns:
        facts (list[str])
        trusted_count (int)
        trusted_exists (bool)
    """

    # ---- DuckDuckGo Search ----
    url = "https://duckduckgo.com/html"
    params = {"q": safe_search_query(search_query)}
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.select(".result__body")

    search_results = []

    for r in results:
        title_tag = r.select_one(".result__title a")
        if not title_tag:
            continue

        real_link = extract_real_url(title_tag["href"])
        domain = urlparse(real_link).netloc

        trusted = 1 if any(td in domain for td in TRUSTED_DOMAINS) else 0

        search_results.append({
            "url": real_link,
            "trusted": trusted
        })

    # ---- Trusted Stats ----
    trusted_count = sum(r["trusted"] for r in search_results)
    trusted_exists = trusted_count > 0

    # ---- Extract Facts ----
    facts = []
    for r in search_results[:max_facts]:
        content = scrape_text(r["url"])
        if content:
            facts.append(safe_text(clean_text(content)))

    return facts, trusted_count, trusted_exists
import re
import json
import time
import subprocess
import tldextract

MODEL_NAME = "gemma3:4b"  # Ensure you pull this model first
# Weighting Logic (Calculated in Python, not LLM)
METRIC_WEIGHTS = {
     "source_reputation": 0.15, # Python-checked domain trust
        "evidence_quality": 0.15,
    "fact_check": 0.45, # Does the logic hold up?
    "topic_consistency": 0.05,  # Does it match the topic context?
    "cross_reference": 0.10 ,
    "writing_style": 0.02 , # Is it professional/sensational?
  "topic_rules": 0.08
}

def extract_json(text):
    """Robustly extracts JSON object from LLM chatter."""
    # Find the first { and the last }
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        json_str = match.group(1)
        # Cleanup common LLM JSON errors
        json_str = re.sub(r",\s*}", "}", json_str) # Trailing commas
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None

def run_ollama(prompt):
    """Sends prompt to Ollama and returns raw string response."""
    cmd = [
        "curl", "-s", "-X", "POST", "http://localhost:11434/api/generate",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"model": MODEL_NAME, "prompt": prompt, "stream": False})
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        response_json = json.loads(result.stdout)
        return response_json.get("response", "")
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return ""
# MAIN FUNCTION
def classify_news(article_text: str,trusted_count,trusted_exists ,facts):
    try:
        subprocess.Popen(["ollama", "serve"])
        time.sleep(5)
        subprocess.run(["ollama", "pull", "gemma3:4b"], check=True)
    except Exception as e:
        return {
            "topic": "Unknown",
            "score": "0%",
            "classification": "Unknown",
            "reason": f"Ollama unavailable: {e}"
        }
    source_score = 10 if trusted_exists else 5
    cross_reference = 10 if trusted_count >=2 else 5
    # STEP 1 — Detect Topic
    topic_prompt = f"""
    Determine the main topic of the following Arabic article.

    Choose strictly from:
    ["Arts","Crime","Disaster and Accident","Economy","Education","Environment",
    "Health","Human Interest","Labour","Lifestyle and Leisure","Politics",
    "Religion and Belief","Science and Technology","Society","Sport","War","Weather","Unknown"]

    Article:
    {article_text}
    """
    raw_topic = run_ollama( topic_prompt)
    topic = raw_topic.strip() if raw_topic else "Unknown"

    topic_rules = get_topic_specific_metrics(topic)

    prompt = f"""
    You are an expert Fact-Checking AI. Analyze the following news text (mostly Arabic).
    Task: Analyze credibility based on 6 specific criteria. Return ONLY a JSON object.
    TEXT TO ANALYZE:
    f"{article_text}\nTopic Rules: {topic_rules}"
    CRITERIA TO SCORE (0 to 10):
    1. content_plausibility:
    FACTS:
    {facts}
    CLAIM:
    {article_text}
    Evaluate whether the claim is supported by the given facts.
    Respond in JSON format only, with no additional explanation or text.
    NOTES:
    - 1 = The claim is true and supported by the facts
    - 0 = The claim is false or not supported by the facts
    2. writing_style: Score 10 for neutral, professional journalism. Score 0 for excessive emotional manipulation, multiple exclamation marks!!!, or hate speech.
    3. evidence_quality: Score high if it cites specific names, dates, and official sources. Score low for vague attributions ("sources said").
    4. topic_consistency: Does the text stay on topic?
    5. topic_rules :{topic_rules}

    OUTPUT FORMAT (JSON ONLY):
    {{
      "topic":topic,# first request
      "fact_check":  0 or 10,
      "writing_style": <int 0-10>,
      "evidence_quality": <int 0-10>,
      "topic_consistency": <int 0-10>,
      "topic_rules": <int 0-10>,
      "flag_reason": "Very short explanation"
    }}
    """

    # 3. Get LLM Response
    raw_response = run_ollama(prompt)
    metrics = extract_json(raw_response)

    # Fallback if LLM fails
    if not metrics:
        metrics = {
            "fact_check": 5,
            "writing_style": 5,
            "evidence_quality": 5,
            "topic_consistency": 5,
             "topic_rules": 5,
             "cross_reference": 5,
            "flag_reason": "Model failed to generate valid JSON"
        }

    # 4. Calculate Final Weighted Score (PYTHON SIDE)
    # Note: Source score comes from Python function, rest from LLM
    weighted_score = (
        (source_score * METRIC_WEIGHTS["source_reputation"]) +
        (metrics.get("fact_check", 5) * METRIC_WEIGHTS["fact_check"]) +
        (metrics.get("writing_style", 5) * METRIC_WEIGHTS["writing_style"]) +
        (metrics.get("evidence_quality", 5) * METRIC_WEIGHTS["evidence_quality"]) +
        (metrics.get("topic_consistency", 5) * METRIC_WEIGHTS["topic_consistency"])+
        (metrics.get("topic_rules", 5) * METRIC_WEIGHTS["topic_rules"])+
        (cross_reference * METRIC_WEIGHTS["cross_reference"])
    )

    # Normalize to 0-100%
    final_percentage = round(weighted_score * 10, 2)

    # 5. Determine Label
    # Stricter threshold: Must be > 65% to be Real, otherwise questionable/fake
    classification = "REAL" if final_percentage >= 65 else "FAKE"

    return {
        "topic":topic,
        "text_snippet": article_text[:50] + "...",

        "classification": classification,
        "confidence_score": f"{final_percentage}%",
        "detailed_scores": {
            "source_trust": source_score,
            **metrics
        }
    }

