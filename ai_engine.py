
from sentence_transformers import SentenceTransformer , util
import spacy
import re 
import numpy as np 
class NapoleanAI:
    def __init__(self, intent_text=None):
        print("🧠 Initializing Napoléon’s Intelligence Unit...")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.nlp = spacy.load("en_core_web_sm")

        self.intent_text = intent_text
        self.intent_embedding = None
        if intent_text:
            self.intent_embedding = self.embedder.encode(intent_text, convert_to_numpy=True)
    

    def get_page_embedding(self, text):
        return self.embedder.encode(text, convert_to_numpy=True)

    def relevance_score(self, page_text,chunk_size=500):
        if self.intent_embedding is None or not page_text:
            return 0.0
        
        chunks = []
        words = page_text.split()
        for i in range(0, len(words), int(chunk_size / 2)):  # 50% overlap
            chunk = " ".join(words[i:i + chunk_size])
        if len(chunk) > 50:  # ignore very short chunks
            chunks.append(chunk)
        if not chunks:
           return 0.0
        
        try:
            chunk_embeddings = self.embedder.encode(chunks, convert_to_numpy=True)
            intent_emb = np.array(self.intent_embedding, dtype=np.float32)

        # Compute cosine similarities for all chunks
            sims = np.dot(chunk_embeddings, intent_emb) / (
            np.linalg.norm(chunk_embeddings, axis=1) * np.linalg.norm(intent_emb) + 1e-8
        )

            best_score = float(np.max(sims))  # take best match
            return round(best_score, 3)
        except Exception as e:
            print(f"[AI Error] relevance_score failed: {e}")
            return 0.0


    def extract_entities(self, text):
        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]

    def summarize(self, text, max_len=400):
        return text if len(text) <= max_len else text[:max_len] + "..."

    def analyze_page(self, page_data):
        text = page_data.get("text", "")
        if not text:
            return None
        relevance = self.relevance_score(text)

        entities = self.extract_entities(text)
        summary = self.summarize(text)
        page_data.update({
            "relevance_score": relevance,
            "entities": entities,
            "summary": summary
        })
        return page_data
