"""Venom personality prompt loader.

Loads the Venom symbiote personality from the configured personality file
and exposes it as an MCP prompt.
"""

from pathlib import Path
from typing import Dict, Any


class VenomPrompt:
    """Loader for Venom personality from markdown file."""

    def __init__(self, personality_file_path: Path) -> None:
        """Initialize the prompt loader.

        Args:
            personality_file_path: Path to the personality markdown file.
        """
        self.personality_file_path = personality_file_path
        self._content: str | None = None

    def _load_content(self) -> str:
        """Load personality content from file.

        Returns:
            Content of the personality file.

        Raises:
            FileNotFoundError: If personality file doesn't exist.
        """
        if self._content is None:
            if not self.personality_file_path.exists():
                raise FileNotFoundError(
                    f"Personality file not found: {self.personality_file_path}"
                )

            self._content = self.personality_file_path.read_text(encoding="utf-8")
            print(f"Loaded personality from: {self.personality_file_path.name}")

        return self._content

    def get_prompt(self) -> Dict[str, Any]:
        """Get the Venom identity prompt in MCP format.

        Returns:
            Dictionary with name, description, and content fields.
        """
        content = self._load_content()

        return {
            "name": "venom_identity",
            "description": "Venom symbiote personality with mandatory memory protocol and 'we' language enforcement",
            "content": content,
        }

    def get_content(self) -> str:
        """Get the raw personality content.

        Returns:
            Raw markdown content of the personality file.
        """
        return self._load_content()
