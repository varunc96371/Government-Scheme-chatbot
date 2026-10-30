import faiss
import numpy as np

from services.embedding_service import generate_embedding


class SchemeFAISS:
    def __init__(self):
        self.index = None
        self.schemes = []

    def build_index(self, schemes):
        """
        Build a FAISS index using S-BERT embeddings
        of the government schemes.
        """
        self.schemes = schemes

        if not schemes:
            self.index = None
            return

        texts = []

        for scheme in schemes:
            text = " ".join([
                str(scheme.get("name", "")),
                str(scheme.get("description", "")),
                str(scheme.get("eligibility", "")),
                str(scheme.get("benefits", "")),
                str(scheme.get("required_documents", "")),
                str(scheme.get("category", "")),
                str(scheme.get("state", "")),
                str(scheme.get("sector", ""))
            ])

            texts.append(text)

        # Generate S-BERT embeddings for all schemes
        embeddings = generate_embedding(texts)

        embeddings = np.asarray(embeddings).astype("float32")

        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)

        # Add scheme embeddings to FAISS
        self.index.add(embeddings)

    def search(self, query, top_k=5):
        """
        Find the most semantically relevant schemes.
        """
        if self.index is None or not self.schemes:
            return []

        query_embedding = generate_embedding([query])
        query_embedding = np.asarray(query_embedding).astype("float32")

        top_k = min(top_k, len(self.schemes))

        distances, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for index in indices[0]:
            if index < len(self.schemes):
                results.append(self.schemes[index])

        return results