import modal
import re
import pandas as pd

app = modal.App("news-classifier-gemma3")

# --- Build image with Ollama + pandas installed ---
image = (
    modal.Image.debian_slim()
    .apt_install("curl")
    .pip_install("pandas", "regex")
    .run_commands("curl -fsSL https://ollama.com/install.sh | sh")
)

# --- Persistent volume for caching Ollama models ---
volume = modal.Volume.from_name("ollama-cache", create_if_missing=True)


# --- Remote classification function ---
@app.function(
    image=image,
    gpu="A10G",
    timeout=600,
    volumes={"/root/.ollama": volume},
)
def classify_news(article_text: str):
    """
    Run the news classification using Ollama + Gemma3 (1B).
    Expect model output in compact list format:
    [Linguistic, Semantic, Source, Knowledge, Behavioral, Average, Classification, Confidence]
    Example: [4,5,3,4,4,4.0,REAL,89%]
    """
    import subprocess, json, time

    # Start Ollama server
    subprocess.Popen(["ollama", "serve"])
    time.sleep(5)
    subprocess.run(["ollama", "pull", "gemma3:1b"], check=True)

    # --- Prompt ---
  # --- Optimized Prompt ---
    prompt = f"""
    You are an expert Arabic news fact-checking assistant. 
    Your task is to classify a given Arabic news article as either REAL or FAKE based on the following metrics:
    1. Lexical richness: diversity and complexity of words.
    2. Sentiment: emotional tone, highly exaggerated or sensational.
    3. Named entities: presence of verifiable people, organizations, locations.
    4. Exaggeration or clickbait words: words like صادم، لن تصدق، مفاجئ، خطير، مذهل.
    5. Factual coherence: logical consistency and plausibility of claims.
    6. Consistency between title and article body.
    7. Alignment with typical reporting style of credible Arabic news sources.
    
    **Instructions:**
    - Analyze the article based on the above metrics.
    - Give a **compact list output** in this exact format:
        [Classification, Confidence, Main_reason_for_prediction]
        - Classification: REAL or FAKE
        - Confidence: integer percentage (0-100%)
        - Main reason for prediction: highlight the most decisive metric
    - Do NOT include anything else in the response.
    **Example of expected output:**
    [REAL, 92%, Title and article match with verifiable entities],
    Article:
    {article_text}
    """

    # --- Generate response from Ollama ---
    proc = subprocess.Popen(
        [
            "curl", "-s", "-X", "POST", "http://localhost:11434/api/generate",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "model": "gemma3:1b",
                "prompt": prompt,
                "options": {"temperature": 0}
            })
        ],
        stdout=subprocess.PIPE,
        text=True
    )

    raw_output = ""
    for line in proc.stdout:
        if '"response":"' in line:
            part = line.split('"response":"')[-1].split('"', 1)[0]
            raw_output += part

    raw_output = raw_output.replace("\\n", "\n").strip()

    # --- Extract values inside [ ... ] ---
    match = re.search(r"\[(.*?)\]", raw_output)
    if match:
        values = [v.strip() for v in match.group(1).split(",")]
    else:
        values = []

    # --- Safe unpacking ---
    while len(values) < 4:
        values.append("")

    # --- Map to columns ---
    data = {
        "Classification": values[0],
        "Confidence": values[1],
        "Main_reason_for_prediction": values[2]
        #,"Raw_Text": raw_output
    }

    return data


# --- Local entrypoint for batch CSV processing ---
@app.local_entrypoint()
def main():
    def process_file(input_path, output_path):
        """Classify all articles in a CSV file and save results."""
        df = pd.read_csv(input_path)
        if "Article_Text" not in df.columns:
            raise ValueError(f"❌ Column 'Article_Text' not found in {input_path}")

        print(f"🚀 Classifying {input_path} ...")

        # Run remote inference
        results = [classify_news.remote(text) for text in df["Article_Text"]]

        # Convert list of dicts to DataFrame
        results_df = pd.DataFrame(results)

        # Merge with original data
        final_df = pd.concat([df, results_df], axis=1)

        # Save to CSV
        final_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"✅ Done! Results saved to {output_path}")

    # --- Files to process ---
    files = [
        ("my_data/test.csv", "classified_data/test_reality.csv"),
        ("my_data/elshrouk.csv", "classified_data/elshrouk_reality.csv")
        # Add more datasets below if needed
        # ("my_data/elmasrielyoum.csv", "classified_data/elmasrielyoum__reality.csv"),
        # ("my_data/elwatan.csv", "classified_data/elwatan__reality.csv"),
        # ("my_data/masrawy.csv", "classified_data/masrawy__reality.csv"),
        # ("my_data/youm7.csv", "classified_data/youm7__reality.csv"),
    ]

    for inp, outp in files:
        process_file(inp, outp)
