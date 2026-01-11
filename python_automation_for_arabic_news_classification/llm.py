import re
import json
import time
import subprocess
import tldextract
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# ===== GLOBAL MODEL INITIALIZATION =====
MODEL_NAME = "gemma3:4b"
OLLAMA_PROCESS = None
OLLAMA_READY = False

def initialize_ollama():
    """Initialize Ollama server and pull model once at startup."""
    global OLLAMA_PROCESS, OLLAMA_READY
    
    if OLLAMA_READY:
        print("✅ Ollama already initialized")
        return True
    
    try:
        print(f"🚀 Starting Ollama server...")
        OLLAMA_PROCESS = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)  # Wait for server to start
        
        print(f"📥 Pulling model: {MODEL_NAME}...")
        result = subprocess.run(
            ["ollama", "pull", MODEL_NAME],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Model {MODEL_NAME} ready")
        OLLAMA_READY = True
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Ollama: {e}")
        return False

def cleanup_ollama():
    """Clean up Ollama process on exit."""
    global OLLAMA_PROCESS, OLLAMA_READY
    if OLLAMA_PROCESS:
        OLLAMA_PROCESS.terminate()
        OLLAMA_READY = False
        print("🛑 Ollama server stopped")

# ===== ORIGINAL FUNCTIONS =====

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


MAX_QUERY_CHARS = 300

def safe_search_query(text):
    return text[:MAX_QUERY_CHARS]

TRUSTED_DOMAINS = {
    "youm7.com",
    "elwatannews.com",
    "almasryalyoum.com",
    "elbalad.news",
    "masrawy.com",
    "vetogate.com",
    "dostor.org",
    "egypttoday.com",
    "shorouknews.com",
    "cairo24.com",
    "akhbarelyom.com",
    "ahram.org.eg",
    "english.ahram.org.eg",
    "dailynewsegypt.com",
    "egyptianstreets.com",
    "madamasr.com",
    "aldostor.com",
    "mobtada.com",
    "albawabhnews.com",
    "almalnews.com",
    "alborsanews.com",
    "amwalalghad.com",
    "alwafd.news",
    "gomhuriaonline.com",
    "rosaelyoussef.com",
    "see.news",
    "egyptindependent.com",
    "egyptian-gazette.com",
    "egyptbusiness.com",
    "enterprise.press",
    "egyptoil-gas.com",
    "cairoscene.com",
    "thestartupscene.me",
    "cairo360.com",
    "watani.net",
    "egynews.net",
    "nileinternational.net",
    "filgoal.com",
    "yallakora.com",
    "kingfut.com",
    "misrday.com",
    "elconsolto.com",
    "reuters.com",
    "apnews.com",
    "afp.com",
    "bbc.com",
    "aljazeera.com",
    "aljazeera.net",
    "arabnews.com",
    "thenationalnews.com",
    "aawsat.com",
    "alarabiya.net",
    "skynewsarabia.com",
    "dw.com",
    "france24.com",
    "rfi.fr",
    "cnn.com",
    "nytimes.com",
    "washingtonpost.com",
    "ft.com",
    "bloomberg.com",
    "wsj.com",
    "economist.com",
    "middleeasteye.net",
    "allafrica.com",
    "theafricareport.com",
    "zawya.com",
    "oxfordbusinessgroup.com",
    "africa-confidential.com",
    "africanews.com",
    "elmogaz.com",
    "innfrad.com",
    "soutalomma.com",
    "elmostaqbal.com",
    "akhbarak.net",
    "masress.com",
    "elbashayer.com",
    "nogoumfm.net",
    "elgornal.net",
    "elaosboa.com",
    "elzmannews.com",
    "masralarabia.com",
    "rassd.com",
    "baladnaelyoum.com",
    "elmwatin.com",
    "alnaharegypt.com",
    "altyaargate.com",
    "parlmany.com",
    "sada-elarab.com",
    "albawaba.com",
    "middleeastmonitor.com",
    "egyptdailynews.com",
    "copts-united.com",
    "arabic.cnn.com",
    "independentarabia.com",
    "asharq.com",
    "bloombergasharq.com",
    "mubasher.info",
    "egx.com.eg",
    "cbe.org.eg",
    "capmas.gov.eg",
    "sis.gov.eg",
    "mfa.gov.eg",
    "mohp.gov.eg"
}

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

def check_count(lst):
    return 10 if lst.count(1) >= 3 else 0


def search_and_extract_facts(search_query, max_facts=5):
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


# ===== METRIC WEIGHTS =====
METRIC_WEIGHTS = {
    "source_reputation": 0.15,
    "evidence_quality": 0.15,
    "fact_check": 0.45,
    "topic_consistency": 0.05,
    "cross_reference": 0.10,
    "writing_style": 0.02,
    "topic_rules": 0.08
}


def extract_json(text):
    """Robustly extracts JSON object from LLM chatter."""
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        json_str = match.group(1)
        json_str = re.sub(r",\s*}", "}", json_str)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None


def run_ollama(prompt):
    """Sends prompt to Ollama and returns raw string response."""
    if not OLLAMA_READY:
        print("❌ Ollama not initialized. Call initialize_ollama() first.")
        return ""
    
    cmd = [
        "curl", "-s", "-X", "POST", "http://localhost:11434/api/generate",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"model": MODEL_NAME, "prompt": prompt, "stream": False})
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        response_json = json.loads(result.stdout)
        return response_json.get("response", "")
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return ""


def classify_news(article_text: str, trusted_count, trusted_exists, facts):
    """Classify news article - Ollama must be initialized first."""
    
    if not OLLAMA_READY:
        return {
            "topic": "Unknown",
            "classification": "Unknown",
            "confidence_score": "0%",
            "reason": "Ollama not initialized. Call initialize_ollama() at program startup."
        }
    
    source_score = 10 if trusted_exists else 5
    cross_reference = 10 if trusted_count >= 2 else 5

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
    raw_topic = run_ollama(topic_prompt)
    topic = raw_topic.strip() if raw_topic else "Unknown"

    topic_rules = get_topic_specific_metrics(topic)

    facts_list = facts
    f1 = facts_list[0] if len(facts_list) > 0 else "N/A"
    f2 = facts_list[1] if len(facts_list) > 1 else "N/A"
    f3 = facts_list[2] if len(facts_list) > 2 else "N/A"
    f4 = facts_list[3] if len(facts_list) > 3 else "N/A"
    f5 = facts_list[4] if len(facts_list) > 4 else "N/A"
    print(facts_list)

    prompt = f"""
    SYSTEM: You are a JSON-only fact verification API. You must return ONLY valid JSON. No explanations allowed.

    TASK: Compare facts against article text and return verification scores.

    ARTICLE TEXT:
    {article_text}

    FACTS TO VERIFY:
    1. {f1}
    2. {f2}
    3. {f3}
    4. {f4}
    5. {f5}

    RULES:
    - 1 = fact is directly stated in article with matching numbers/values
    - 0 = fact contradicts article or is not mentioned

    REQUIRED OUTPUT FORMAT (nothing else):
    {{"verification_results": [0, 0, 0, 0, 0]}}
    """

    fact_check_response = run_ollama(prompt)
    print("🔍 Fact Check Response:", fact_check_response)

    verification_list = [0, 0, 0, 0, 0]
    fact_check_score = 0

    if not fact_check_response:
        print("❌ Failed to extract verification JSON")
    else:
        try:
            parsed = extract_json(fact_check_response)
            if parsed and "verification_results" in parsed:
                verification_list = parsed["verification_results"]
                if len(verification_list) != 5:
                    verification_list = (verification_list + [0, 0, 0, 0, 0])[:5]
                fact_check_score = check_count(verification_list)
            else:
                print("❌ JSON missing 'verification_results' key")
        except Exception:
            print("❌ Invalid JSON returned from Ollama")

    # STEP 3 - Other Metrics
    prompt = f"""
    Analyze this news text and return ONLY valid JSON with these 4 scores (0-10):
    1. writing_style: Score 10 for neutral, professional journalism. Score 0 for excessive emotional manipulation, multiple exclamation marks!!!, or hate speech.
    2. evidence_quality: Score 10 if it cites specific names, dates, and official sources. Score 0 for vague attributions ("sources said").
    3. topic_consistency: Does the text stay on topic?
    4. topic_rules :{topic_rules}
    TEXT:
    {article_text}

    Output EXACTLY this format:
    {{
      "writing_style": 7,
      "evidence_quality": 8,
      "topic_consistency": 6,
      "topic_rules": 5,
      "flag_reason": "Brief explanation"
    }}

    Output ONLY the JSON:
    """
    raw_response = run_ollama(prompt)

    metrics = extract_json(raw_response)

    if not metrics:
        metrics = {
            "writing_style": 5,
            "evidence_quality": 5,
            "topic_consistency": 5,
            "topic_rules": 5,
            "flag_reason": "Model failed to generate valid JSON"
        }
    else:
        for key in ["writing_style", "evidence_quality", "topic_consistency", "topic_rules"]:
            value = metrics.get(key, 5)
            if not isinstance(value, (int, float)):
                print(f"⚠️ Warning: {key} is not a number: {value}")
                metrics[key] = 5
            else:
                metrics[key] = int(value)

    # Calculate Final Weighted Score
    weighted_score = (
        (source_score * METRIC_WEIGHTS["source_reputation"]) +
        (fact_check_score * METRIC_WEIGHTS["fact_check"]) +
        (metrics["writing_style"] * METRIC_WEIGHTS["writing_style"]) +
        (metrics["evidence_quality"] * METRIC_WEIGHTS["evidence_quality"]) +
        (metrics["topic_consistency"] * METRIC_WEIGHTS["topic_consistency"]) +
        (metrics["topic_rules"] * METRIC_WEIGHTS["topic_rules"]) +
        (cross_reference * METRIC_WEIGHTS["cross_reference"])
    )

    final_percentage = round(weighted_score * 10, 2)
    classification = "REAL" if final_percentage >= 65 else "FAKE"

    return {
        "topic": topic,
        "classification": classification,
        "confidence_score": f"{final_percentage}%"
    }


initialize_ollama()
 
