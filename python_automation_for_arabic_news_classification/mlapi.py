from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import llm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

# ✅ Create FastAPI app ONCE
app = FastAPI(
    title="Arabic News Classification API",
    version="1.0.0"
)

# ✅ CRITICAL: CORS must allow 'null' origin for file:// protocol
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins including file://
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
    expose_headers=["*"]  # Exposes all headers to the frontend
)

# -------- Request Schema --------
class QueryItem(BaseModel):
    news: str

# -------- Health Check --------
@app.get("/")
def health():
    return {"status": "running", "message": "Backend is active"}

# -------- Favicon (to stop 405 errors) --------
@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

# -------- OPTIONS handler for preflight --------
@app.options("/{path:path}")
def options_handler(path: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# -------- Main Classification Endpoint --------
@app.post("/classify")
def classify(item: QueryItem):
    try:
        article_text = item.news
        
        print(f"📥 Received news text: {article_text[:100]}...")  # Debug log

        # 1️⃣ Search & extract facts
        facts, trusted_count, trusted_exists = (
            llm.search_and_extract_facts(article_text)
        )
        
        print(f"🔍 Facts extracted: {facts}")  # Debug log

        # 2️⃣ Convert facts list to string
        facts_str = "|".join(facts) if facts else ""

        # 3️⃣ Run classification
        result = llm.classify_news(
            article_text=article_text,
            trusted_count=trusted_count,
            trusted_exists=trusted_exists,
            facts=facts_str
        )
        
        print(f"✅ Classification result: {result}")  # Debug log

        # 4️⃣ Format response to match frontend expectations
        response = {
            "topic": result.get("topic", "Unknown"),
            "classification": result.get("classification", "UNKNOWN"),
            "confidence_score": result.get("confidence_score", "N/A"),
            "detailed_scores": {
                "flag_reason": result.get("detailed_scores", {}).get("flag_reason", "No reason provided")
            }
        }
        
        return response

    except Exception as e:
        print(f"❌ Error in classify endpoint: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=500,
            detail=f"Classification error: {str(e)}"
        )