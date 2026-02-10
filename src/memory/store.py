"""ChromaDB-based memory store for persistent semantic search.

This module handles all CRUD operations for Venom's memory system,
using ChromaDB for vector similarity search.
"""

import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

import chromadb
from chromadb.config import Settings

from .embeddings import EmbeddingService


class MemoryStore:
    """Persistent memory store using ChromaDB."""

    def __init__(
        self,
        chromadb_path: str,
        collection_name: str,
        embedding_service: EmbeddingService,
    ) -> None:
        """Initialize the memory store.

        Args:
            chromadb_path: Path to ChromaDB persistent storage directory.
            collection_name: Name of the ChromaDB collection.
            embedding_service: Service for generating embeddings.
        """
        self.chromadb_path = Path(chromadb_path)
        self.collection_name = collection_name
        self.embedding_service = embedding_service

        # Ensure data directory exists
        self.chromadb_path.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.chromadb_path),
            settings=Settings(anonymized_telemetry=False),
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Venom symbiote semantic memory"},
        )

        print(f"ChromaDB initialized at {self.chromadb_path}", file=sys.stderr)
        print(f"Collection: {collection_name}, Count: {self.collection.count()}", file=sys.stderr)

    def store_memory(
        self,
        content: str,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Store a new memory with semantic embedding.

        Args:
            content: Text content to remember.
            tags: Optional categorization tags.

        Returns:
            Dictionary with memory_id, success status, timestamp, and embedding dimensions.

        Raises:
            ValueError: If content is empty or tags are invalid.
        """
        # Validate input
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")

        if tags:
            if len(tags) > 10:
                raise ValueError("Maximum 10 tags allowed")
            if any(not tag or not tag.strip() for tag in tags):
                raise ValueError("Tags cannot be empty")
            if any(len(tag) > 50 for tag in tags):
                raise ValueError("Tags must be maximum 50 characters")

        # Generate unique ID from timestamp
        memory_id = f"mem_{int(time.time())}"

        # Generate embedding
        embedding = self.embedding_service.generate_embedding(content)

        # Create metadata
        metadata = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if tags:
            metadata["tags"] = ",".join(tags)  # ChromaDB metadata values must be primitives

        # Store in ChromaDB
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
        )

        return {
            "memory_id": memory_id,
            "success": True,
            "timestamp": metadata["timestamp"],
            "embedding_dimensions": len(embedding),
        }

    def search_memory(
        self,
        query: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """Search memories using semantic similarity.

        Args:
            query: Natural language search query.
            limit: Maximum number of results to return (1-20).

        Returns:
            Dictionary with results list, total_results count, and query_embedding_generated status.

        Raises:
            ValueError: If query is empty or limit is invalid.
        """
        # Validate input
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not (1 <= limit <= 20):
            raise ValueError("Limit must be between 1 and 20")

        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)

        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
        )

        # Process results
        formatted_results = []

        if results["ids"] and results["ids"][0]:  # Check if we have results
            for idx in range(len(results["ids"][0])):
                # Get data
                memory_id = results["ids"][0][idx]
                content = results["documents"][0][idx]
                distance = results["distances"][0][idx]
                metadata = results["metadatas"][0][idx]

                # Convert distance to relevance score
                # ChromaDB cosine distance ranges from 0 (identical) to 2 (opposite)
                # Convert to percentage: 0 distance = 100%, 2 distance = 0%
                relevance_score = max(0, (2 - distance) / 2 * 100)

                # No filtering - return all results and let the AI judge relevance
                # (removing threshold because semantic search with generic queries often has low scores)

                # Parse tags from metadata
                tags = None
                if "tags" in metadata and metadata["tags"]:
                    tags = metadata["tags"].split(",")

                formatted_results.append({
                    "memory_id": memory_id,
                    "content": content,
                    "timestamp": metadata.get("timestamp", ""),
                    "relevance_score": round(relevance_score, 1),
                    "tags": tags,
                })

        return {
            "results": formatted_results,
            "total_results": len(formatted_results),
            "query_embedding_generated": True,
        }

    def get_memory_count(self) -> int:
        """Get the total number of stored memories.

        Returns:
            Count of memories in the collection.
        """
        return self.collection.count()
