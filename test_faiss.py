from utils.db import get_all_schemes
from services.faiss_service import SchemeFAISS

# Get all schemes from SQLite
schemes = get_all_schemes()

print("Number of schemes:", len(schemes))

# Create FAISS search system
faiss_search = SchemeFAISS()

# Build FAISS index
faiss_search.build_index(schemes)

print("FAISS index created successfully!")

# Test semantic search
query = "I need financial help for my education"

results = faiss_search.search(query, top_k=5)

print("\nTop matching schemes:")

for scheme in results:
    print("-", scheme["name"])