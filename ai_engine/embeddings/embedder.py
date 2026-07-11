"""
Embedding engine using sentence-transformers/all-MiniLM-L6-v2
Runs locally — zero API cost
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
from loguru import logger
import numpy as np

from backend.core.config import settings


class EmbeddingEngine:
    """
    Local embedding engine using SentenceTransformers.
    Model: all-MiniLM-L6-v2 (384-dim, fast, free)
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.HF_EMBEDDING_MODEL
        self._model = None
        self._load_model()

    def _load_model(self):
        try:
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Embedding model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")

    def embed(self, text: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text or list of texts."""
        if self._model is None:
            raise RuntimeError("Embedding model not loaded")
        
        if isinstance(text, str):
            text = [text]
        
        embeddings = self._model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32,
        )
        return embeddings

    def embed_single(self, text: str) -> List[float]:
        """Embed a single text and return as Python list."""
        emb = self.embed(text)
        return emb[0].tolist()

    def cosine_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Compute cosine similarity between two embeddings."""
        a = np.array(emb1)
        b = np.array(emb2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

    def similarity_score(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts (0.0 to 1.0)."""
        emb1 = self.embed_single(text1)
        emb2 = self.embed_single(text2)
        return self.cosine_similarity(emb1, emb2)


# Singleton
_embedder_instance = None


def get_embedder() -> EmbeddingEngine:
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = EmbeddingEngine()
    return _embedder_instance
