"""Embedding generation using sentence-transformers.

This module wraps the sentence-transformers library to generate
384-dimension semantic embeddings for text content.
"""

from typing import List, Optional
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Initialize the embedding service.

        Args:
            model_name: Name of the sentence-transformers model to use.
                       Default is all-MiniLM-L6-v2 (384 dimensions).
        """
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None

    def _load_model(self) -> SentenceTransformer:
        """Lazy-load the sentence transformer model.

        Returns:
            Loaded sentence transformer model.
        """
        if self._model is None:
            print(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            print(f"Model loaded successfully. Embedding dimensions: {self.get_embedding_dimensions()}")
        return self._model

    def get_embedding_dimensions(self) -> int:
        """Get the number of dimensions in generated embeddings.

        Returns:
            Number of dimensions (384 for all-MiniLM-L6-v2).
        """
        model = self._load_model()
        return model.get_sentence_embedding_dimension()

    def generate_embedding(self, text: str) -> List[float]:
        """Generate a semantic embedding for the given text.

        Args:
            text: Text content to embed.

        Returns:
            List of float values representing the embedding vector.

        Raises:
            ValueError: If text is empty.
        """
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty text")

        model = self._load_model()
        embedding = model.encode(text, convert_to_numpy=True)

        # Convert numpy array to Python list
        return embedding.tolist()

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch.

        Args:
            texts: List of text content to embed.

        Returns:
            List of embedding vectors.

        Raises:
            ValueError: If any text is empty.
        """
        if not texts:
            raise ValueError("Cannot generate embeddings for empty list")

        if any(not text or not text.strip() for text in texts):
            raise ValueError("Cannot generate embedding for empty text")

        model = self._load_model()
        embeddings = model.encode(texts, convert_to_numpy=True)

        # Convert numpy arrays to Python lists
        return [emb.tolist() for emb in embeddings]
