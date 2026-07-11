"""
ChromaDB RAG Retriever
Stores and retrieves resume/JD embeddings for semantic search
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from loguru import logger
import uuid

from backend.core.config import settings
from ai_engine.embeddings.embedder import get_embedder


class ChromaRetriever:
    """
    ChromaDB-based vector store for semantic resume retrieval.
    Supports storing, querying, and deleting resume/JD embeddings.
    """

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
        self.embedder = get_embedder()
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"✅ ChromaDB collection '{settings.CHROMA_COLLECTION_NAME}' ready")
        return collection

    def store_resume(self, resume_id: str, resume_data: dict, resume_text: str) -> str:
        """Embed and store a resume in ChromaDB."""
        doc_id = f"resume_{resume_id}"
        embedding = self.embedder.embed_single(resume_text[:2000])  # Token-safe truncation

        metadata = {
            "type": "resume",
            "resume_id": resume_id,
            "name": resume_data.get("name", "Unknown"),
            "skills": ", ".join(resume_data.get("skills", [])[:20]),
        }

        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[resume_text[:2000]],
            metadatas=[metadata],
        )
        logger.info(f"✅ Resume {resume_id} stored in ChromaDB")
        return doc_id

    def store_jd(self, job_id: str, jd_text: str, jd_data: dict) -> str:
        """Embed and store a JD in ChromaDB."""
        doc_id = f"jd_{job_id}"
        embedding = self.embedder.embed_single(jd_text[:2000])

        metadata = {
            "type": "jd",
            "job_id": job_id,
            "title": jd_data.get("job_title", ""),
            "required_skills": ", ".join(jd_data.get("required_skills", [])[:20]),
        }

        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[jd_text[:2000]],
            metadatas=[metadata],
        )
        logger.info(f"✅ JD {job_id} stored in ChromaDB")
        return doc_id

    def semantic_match_score(self, resume_text: str, jd_text: str) -> float:
        """
        Compute semantic similarity between resume and JD.
        Returns score between 0 and 1.
        """
        return self.embedder.similarity_score(resume_text, jd_text)

    def find_similar_resumes(self, jd_text: str, n_results: int = 5) -> List[Dict]:
        """Find top N resumes most similar to a given JD."""
        query_embedding = self.embedder.embed_single(jd_text[:2000])

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, self.collection.count()),
            where={"type": "resume"},
        )

        matches = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                matches.append({
                    "doc_id": doc_id,
                    "resume_id": results["metadatas"][0][i].get("resume_id"),
                    "name": results["metadatas"][0][i].get("name"),
                    "similarity": 1 - (results["distances"][0][i] if results.get("distances") else 0),
                    "skills": results["metadatas"][0][i].get("skills", ""),
                })

        return matches

    def delete_resume(self, resume_id: str):
        """Remove a resume embedding from ChromaDB."""
        try:
            self.collection.delete(ids=[f"resume_{resume_id}"])
            logger.info(f"🗑️ Deleted resume {resume_id} from ChromaDB")
        except Exception as e:
            logger.error(f"Failed to delete from ChromaDB: {e}")

    def get_collection_stats(self) -> Dict:
        """Return collection statistics."""
        return {
            "total_documents": self.collection.count(),
            "collection_name": settings.CHROMA_COLLECTION_NAME,
        }


# Singleton
_retriever_instance = None


def get_retriever() -> ChromaRetriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = ChromaRetriever()
    return _retriever_instance
