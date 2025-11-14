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
    Run the Arabic news classification using Gemma3.
    Expected model output:
    [Topic_category, Reality, Confidence, Main_reason_for_prediction]
    Example:
    [Politics, REAL, 92%, Consistent entities and factual tone]
    """
    import subprocess, json, time

    # Start Ollama server
    subprocess.Popen(["ollama", "serve"])
    time.sleep(5)
    subprocess.run(["ollama", "pull", "gemma3:4b"], check=True)

    # --- Optimized Arabic Fact-checking & Topic Classification Prompt ---
    prompt = f"""
    You are a multilingual Arabic news analysis assistant.
    Your job is twofold:
    1. Determine the **main topic** of the Arabic article from this list:
        [
        "Arts, Culture and Entertainment",
        "Crime, Law and Justice",
        "Disaster and Accident",
        "Economy, Business and Finance",
        "Education",
        "Environment",
        "Health",
        "Human Interest",
        "Labour",
        "Lifestyle and Leisure",
        "Politics",
        "Religion and Belief",
        "Science and Technology",
        "Society",
        "Sport",
        "Unrest, Conflict and War",
        "Weather",
        "Unknown"
        ]

    2. Determine if the article is **REAL** or **FAKE** using these metrics:
        - Lexical richness (diversity and clarity of vocabulary)
        - Sentiment (neutral vs exaggerated or emotional tone)
        - Named entities (presence of verifiable people/places/orgs)
        - Exaggeration/clickbait words (صادم، لن تصدق، مفاجئ، خطير)
        - Factual coherence and logical consistency
        - Consistency between title and body
        - Alignment with formal Arabic news tone

    **Output Rules:**
    - Return a **compact list** exactly in this format:
        [Topic_category, Reality, Confidence, Main_reason_for_prediction]
    - Confidence must be a numeric percentage (e.g., 87%)
    - Reality is one of: REAL, FAKE, or UNKNOWN
    - Main_reason_for_prediction should briefly explain the reasoning
    - Do NOT include any explanation or extra text

    **Example:**
    [Politics, REAL, 91%, Factual reporting with verifiable named entities]

    Article:
    {article_text}
    """

    # --- Generate response from Ollama ---
    proc = subprocess.Popen(
        [
            "curl", "-s", "-X", "POST", "http://localhost:11434/api/generate",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "model": "gemma3:4b",
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

    # --- Map to final DataFrame keys ---
    data = {
        "Topic": values[0],
        "Reality": values[1],
        "Confidence": values[2],
        "Main_reason_for_prediction": values[3]
    }

    return data


# --- Local entrypoint for batch processing ---
@app.local_entrypoint()
def main():
    import pandas as pd

    def process_file(input_path, output_path):
        """Classify one CSV file and save results."""
        df = pd.read_csv(input_path)
        if "Article_Text" not in df.columns:
            raise ValueError(f"❌ Column 'Article_Text' not found in {input_path}")

        print(f"🚀 Classifying {input_path} ...")

        results = [classify_news.remote(text) for text in df["Article_Text"]]
        results_df = pd.DataFrame(results)

        # Merge with original data
        final_df = pd.concat([df, results_df], axis=1)

        # Reorder columns
        columns_order = [
            "Title", "Link", "website", "Article_Text",
            "Topic", "Reality", "Confidence", "Main_reason_for_prediction"
        ]
        final_df = final_df[[col for col in columns_order if col in final_df.columns]]

        final_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"✅ Done! Results saved to {output_path}")

    # --- Files to classify ---
    files = [
       
        ("my_data/test.csv", "classified_data/test_reality.csv"),
        #("my_data/elshrouk.csv", "classified_data/elshrouk_reality.csv")
        
         ("my_data/elmasrielyoum.csv", "classified_data/elmasrielyoum__reality.csv"),
         ("my_data/elwatan.csv", "classified_data/elwatan__reality.csv"),
         ("my_data/masrawy.csv", "classified_data/masrawy__reality.csv"),
         ("my_data/youm7.csv", "classified_data/youm7__reality.csv")
    ]

    for inp, outp in files:
        process_file(inp, outp)
