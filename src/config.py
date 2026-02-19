"""Configuration management for Symbiote MCP Server.

Loads configuration from environment variables with sensible defaults.
Validates all settings on startup.
"""

import os
import sys
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

        # Optional directory containing personality markdown files.
        # Intended for private submodules or mounted secrets.
        self.personality_dir: str | None = os.getenv("PERSONALITY_DIR")

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
            print(f"WARNING: Invalid VENOM_PERSONALITY '{self.venom_personality}', using default", file=sys.stderr)

        project_root = Path(__file__).parent.parent

        candidate_dirs: list[Path] = []

        if self.personality_dir:
            configured = Path(self.personality_dir).expanduser()
            # If relative, interpret it relative to the project root.
            if not configured.is_absolute():
                configured = (project_root / configured).resolve()
            candidate_dirs.append(configured)

        # Conventional location for private submodule assets
        candidate_dirs.append(project_root / "personalities")

        # Backward compatibility for local dev
        candidate_dirs.append(project_root)

        for directory in candidate_dirs:
            path = directory / filename
            if path.exists():
                return path

        # Nothing found; return the preferred path (so callers can report a helpful error)
        return candidate_dirs[0] / filename

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
