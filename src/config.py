"""Configuration management for Symbiote MCP Server.

Loads configuration from environment variables with sensible defaults.
Validates all settings on startup.
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Application configuration loaded from environment variables."""

    def __init__(self) -> None:
        """Initialize configuration from environment."""
        # Server configuration
        self.port: int = int(os.getenv("PORT", "8000"))
        self.host: str = os.getenv("HOST", "0.0.0.0")

        # ChromaDB configuration
        self.chromadb_path: str = os.getenv("CHROMADB_PATH", "./data")
        self.collection_name: str = os.getenv("COLLECTION_NAME", "venom_memories")

        # Embedding model
        self.embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

        # Personality variant
        self.venom_personality: str = os.getenv("VENOM_PERSONALITY", "default")

        # Validate configuration
        self._validate()

    def _validate(self) -> None:
        """Validate configuration values."""
        if not (1 <= self.port <= 65535):
            raise ValueError(f"PORT must be between 1 and 65535, got {self.port}")

        if not self.host:
            raise ValueError("HOST cannot be empty")

        if not self.collection_name:
            raise ValueError("COLLECTION_NAME cannot be empty")

        if not self.embedding_model:
            raise ValueError("EMBEDDING_MODEL cannot be empty")

    def get_personality_file_path(self) -> Path:
        """Get the file path for the active personality variant.

        Returns:
            Path to the personality markdown file.
            Falls back to default if variant is invalid.
        """
        personality_files = {
            "default": "venom_personality.md",
            "variant2": "venom_personality_v2.md",
        }

        filename = personality_files.get(self.venom_personality, "venom_personality.md")

        # Warn if invalid variant specified
        if self.venom_personality not in personality_files:
            print(f"WARNING: Invalid VENOM_PERSONALITY '{self.venom_personality}', using default")

        # Return path relative to project root
        return Path(__file__).parent.parent / filename

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"Config(port={self.port}, host={self.host}, "
            f"chromadb_path={self.chromadb_path}, "
            f"collection_name={self.collection_name}, "
            f"embedding_model={self.embedding_model}, "
            f"venom_personality={self.venom_personality})"
        )


# Global config instance
config = Config()
