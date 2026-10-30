from utils.db import get_all_schemes
from services.faiss_service import SchemeFAISS
from gemini_service import generate_gemini_response
from langdetect import detect
from deep_translator import GoogleTranslator

# Create FAISS search system once
faiss_search = SchemeFAISS()

# Load schemes from SQLite
schemes = get_all_schemes()

# Build FAISS index
faiss_search.build_index(schemes)

def generate_recommendation_response(user_message):
    """
    RAG-based government scheme recommendation.

    User query
        ↓
    S-BERT embedding
        ↓
    FAISS semantic retrieval
        ↓
    Retrieved schemes
        ↓
    Gemini with retrieved context
        ↓
    Final response
    """

    query = user_message.strip()

    # Detect user language
    try:
        detected_language = detect(query)
    except: 
        detected_language = "en"

    if not query:
        return "<p>Please enter your question.</p>"

    # Translate Telugu query to English for scheme retrieval
    if detected_language == "te":
        try:
            query = GoogleTranslator(source="te", target="en").translate(query)
        except Exception:
            pass
    # 1. Retrieve relevant schemes using FAISS
    matched_schemes = faiss_search.search(query, top_k=5)

    if not matched_schemes:
        response = generate_gemini_response(query)

        if detected_language == "te":
            try:
                response = GoogleTranslator(
                    source="en",
                    target="te"
                ).translate(response)
            except Exception:
                pass

        return response

    # 3. Build RAG context from retrieved schemes
    context_parts = []

    for scheme in matched_schemes:
        context_parts.append(
            f"""
Scheme Name: {scheme.get('name', '')}
Category: {scheme.get('category', '')}
Description: {scheme.get('description', '')}
Eligibility: {scheme.get('eligibility', '')}
Benefits: {scheme.get('benefits', '')}
Required Documents: {scheme.get('required_documents', '')}
State: {scheme.get('state', '')}
Sector: {scheme.get('sector', '')}
Official Portal: {scheme.get('portal_link', '')}
"""
        )

    rag_context = "\n---\n".join(context_parts)

    # Generate final Gemini response
    response = generate_gemini_response(
        query,
        rag_context=rag_context
    )

    # Translate response back to Telugu
    if detected_language == "te":
        try:
            response = GoogleTranslator(
                source="en",
                target="te"
            ).translate(response)
        except Exception:
            pass

    return response