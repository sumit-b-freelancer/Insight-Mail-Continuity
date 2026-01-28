import json
import re
import os
import pickle
import nltk
import gensim
from gensim import corpora
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import google.generativeai as genai
from django.conf import settings
from .absa_engine import AspectEngine

# --- PHASE 2 IMPORT: The SVR Engine ---
from .engagement_engine import EngagementEngine

from .keywords import DANGER_KEYWORDS, COMPLAINT_KEYWORDS, FINANCE_KEYWORDS

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# SECURITY NOTE: In production, use os.environ.get('GOOGLE_API_KEY')
GOOGLE_API_KEY = "AIzaSyDGsKNjOPjFQkuQub0vyz-2V3R-VN-4m64" 
genai.configure(api_key=GOOGLE_API_KEY)

# Global paths for saving ML models
MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_models')
os.makedirs(MODEL_PATH, exist_ok=True)

# ---------------------------------------------------------
# PHASE 1: PREPROCESSING & GROUND TRUTH LOGIC
# ---------------------------------------------------------

def clean_text(text):
    """Phase 1: Preprocessing for LDA"""
    if not text: return []
    text = text.lower()
    text = re.sub(r'<.*?>', '', text) 
    text = re.sub(r'[^a-zA-Z\s]', '', text) 
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in text.split() if word not in stop_words and len(word) > 2]
    return tokens

def get_vader_sentiment(text):
    """Phase 1: VADER Sentiment"""
    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(text)
    compound = scores['compound']
    
    if compound >= 0.05:
        return "Positive", compound
    elif compound <= -0.05:
        return "Negative", compound
    else:
        return "Neutral", compound

def predict_topic_lda(text_tokens):
    """Phase 1: LDA Prediction"""
    try:
        dictionary = corpora.Dictionary.load(os.path.join(MODEL_PATH, 'lda_dict.gensim'))
        lda_model = gensim.models.LdaModel.load(os.path.join(MODEL_PATH, 'lda_model.gensim'))
        bow_vector = dictionary.doc2bow(text_tokens)
        topics = lda_model.get_document_topics(bow_vector)
        dominant_topic = sorted(topics, key=lambda x: x[1], reverse=True)[0]
        
        # Placeholder mapping - You update this after looking at your Topics
        topic_map = {0: "Operations", 1: "Finance", 2: "General"} 
        return topic_map.get(dominant_topic[0], "General")
    except Exception:
        return None

# ---------------------------------------------------------
# MAIN ENGINE (Phase 1 + Phase 2 Merged)
# ---------------------------------------------------------

def analyze_email_content(email_obj, history=[], agent_name="Support Team"):
    """
    Revised Engine: 
    1. SVR Filter (Phase 2) -> Filters out 'Individual' noise.
    2. VADER/LDA (Phase 1) -> Analyzes 'Interested' emails.
    3. Gemini (LLM) -> Drafts replies for valid threads.
    """
    
    # Extract text from the object
    subject = email_obj.subject
    body = email_obj.body
    full_text = f"{subject} {body}"
    clean_tokens = clean_text(full_text)

    # ============================================================
    # PHASE 2: ENGAGEMENT FILTER (SVR)
    # ============================================================
    eng_engine = EngagementEngine()
    # This checks DB for Reply Count (Rc), Forward Count (Fc), Time (T)
    engagement_class = eng_engine.predict_engagement(email_obj)
    
    # ============================================================
# PHASE 3: ASPECT ANALYSIS (ABSA)
# ============================================================
    absa_engine = AspectEngine()
    aspect_sentiments = absa_engine.get_aspect_sentiment(full_text)

    # Format for display/prompt
    # e.g., "Price: Negative, Support: Positive"
    aspect_display = ", ".join([f"{k.capitalize()}: {v}" for k, v in aspect_sentiments.items()])

    if not aspect_display:
        aspect_display = "None detected"
    
    # [OPTIMIZATION] If it's just "Individual" (Noise), skip the heavy AI
    if engagement_class == "Individual":
        # We return early to save API costs and processing time
        return {
            "summary": "Skipped Deep Analysis (Low Engagement / Noise).",
            "sentiment": "Neutral",
            "tone": "Neutral",
            "risk_score": 0,
            "flagged_keywords": "",
            "suggested_category": "Individual",
            "suggested_reply": "No reply generated for individual broadcast."
        }

    # ============================================================
    # PHASE 1: SENTIMENT & CATEGORY (VADER + LDA)
    # ============================================================
    
    # --- 1. SENTIMENT (VADER) ---
    sentiment_label, sentiment_score = get_vader_sentiment(full_text)

    # --- 2. TONE (Heuristic) ---
    if full_text.isupper() or body.count("!") > 3:
        tone = "Aggressive / Urgent"
    elif sentiment_score < -0.4:
        tone = "Frustrated"
    elif sentiment_score > 0.6:
        tone = "Excited"
    else:
        tone = "Professional"

    # --- 3. CATEGORY (LDA + Keyword Fallback) ---
    category = predict_topic_lda(clean_tokens)
    
    if not category or category == "General":
        category = "Inquiry" 
        if any(w in full_text.lower() for w in FINANCE_KEYWORDS): category = "Finance"
        if any(w in full_text.lower() for w in COMPLAINT_KEYWORDS): category = "Complaint"
        if any(w in full_text.lower() for w in DANGER_KEYWORDS): category = "Compliance Issue"

    # --- 4. RISK SCORE ---
    risk_score = 10
    flagged = []
    
    for word in DANGER_KEYWORDS:
        if word in full_text.lower():
            risk_score += 30
            flagged.append(word)
    
    if sentiment_label == "Negative":
        risk_score += int(abs(sentiment_score) * 30)
        
    if risk_score > 99: risk_score = 99
    flagged_display = ", ".join(list(set(flagged))[:5])

    # ============================================================
    # GENERATE REPLY (Gemini Cloud) - Only for Interested/Uninterested
    # ============================================================
    history_text = "\n".join([f"- {msg['sender']}: {msg['body']}" for msg in history]) if history else "No context."
    
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    
    # We feed the "Engagement Class" into the prompt so Gemini knows if it's a "Hot Lead" or "Churn Risk"
    prompt = f"""
    Act as '{agent_name}'. Write a professional reply.
    
    METADATA:
    - Engagement Status: {engagement_class} (Important!)
    - Specific Issues (ABSA): {aspect_display}
    - Sentiment: {sentiment_label} ({sentiment_score:.2f})
    - Category: {category}
    - Risk Score: {risk_score}/100
    
    CONTEXT (Email History):
    {history_text}
    
    INCOMING EMAIL:
    {full_text}
    
    INSTRUCTIONS:
    - If Engagement is 'Interested', be highly responsive and engaging.
    - If Engagement is 'Uninterested', try to re-engage them or be concise.
    - Keep it under 100 words.
    """
    
    try:
        response = model.generate_content(prompt)
        draft_reply = response.text.strip()
    except:
        draft_reply = f"Received. We are reviewing your email about {category}."

    return {
        "summary": f"[{engagement_class}] Aspects: [{aspect_display}]. VADER: {sentiment_label}. Topic: {category}.",
        "sentiment": sentiment_label,
        "tone": tone,
        "risk_score": risk_score,
        "flagged_keywords": flagged_display,
        "suggested_category": category,
        "suggested_reply": draft_reply
    }