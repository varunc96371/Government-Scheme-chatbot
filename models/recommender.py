import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import schemes from your existing DB helper
try:
    from utils.db import get_all_schemes
except:
    get_all_schemes = None

# Cache so we don't rebuild every time
_vectorizer = None
_tfidf_matrix = None
_schemes_cache = []

def _load_schemes():
    global _vectorizer, _tfidf_matrix, _schemes_cache
    if _vectorizer is not None:
        return _schemes_cache, _vectorizer, _tfidf_matrix

    schemes = []
    if get_all_schemes:
        try:
            schemes = get_all_schemes() or []
        except Exception as e:
            print(f"Recommender load error: {e}")
            schemes = []

    _schemes_cache = schemes
    if not schemes:
        return schemes, None, None

    texts = []
    for s in schemes:
        text = f"{s.get('name','')} {s.get('description','')} {s.get('category','')} {s.get('eligibility','')} {s.get('benefits','')}"
        texts.append(text)

    _vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    _tfidf_matrix = _vectorizer.fit_transform(texts)
    return _schemes_cache, _vectorizer, _tfidf_matrix

def generate_recommendation_response(user_message):
    schemes, vectorizer, matrix = _load_schemes()

    if not schemes or vectorizer is None:
        return "<p>Sorry, no schemes found in the database right now. Please try again later.</p>"

    # Find top 3 matching schemes with TF-IDF
    query_vec = vectorizer.transform([user_message])
    scores = cosine_similarity(query_vec, matrix)[0]
    top_idx = scores.argsort()[-3:][::-1]

    html = "<p>Based on your query, here are the most relevant schemes for you:</p>"
    html += "<div style='display:flex;flex-direction:column;gap:12px;margin-top:10px;'>"

    for idx in top_idx:
        if scores[idx] < 0.05:
            continue
        s = schemes[idx]
        html += f"""
        <div style='border:1px solid #ddd;border-radius:10px;padding:12px;background:#f9f9f9;'>
            <b>{s.get('name','Scheme')}</b><br>
            <span style='color:#555;font-size:13px;'>Category: {s.get('category','')}</span><br>
            <p style='margin:6px 0;'>{s.get('description','')[:300]}</p>
            <a href='/schemes/{s.get('id','')}' style='color:#2563eb;'>View Details →</a>
        </div>
        """
    html += "</div>"

    if "View Details" not in html:
        html += "<p>I could not find an exact match. Please try keywords like 'student scholarship', 'farmer', 'women', 'pension', 'unemployed'.</p>"

    return html