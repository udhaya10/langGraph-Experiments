"""
Storage backend for debate records
Currently implements JSON storage
"""
import json
import os
from abc import ABC, abstractmethod
from typing import List
from src.models import DebateRecord


class StorageBackend(ABC):
    """Abstract base class for storage backends"""

    @abstractmethod
    def save_debate(self, debate: DebateRecord) -> str:
        """Save debate and return debate_id"""
        pass

    @abstractmethod
    def get_debate(self, debate_id: str) -> DebateRecord:
        """Retrieve debate by ID"""
        pass

    @abstractmethod
    def list_debates(self, limit: int = 10) -> List[DebateRecord]:
        """List stored debates"""
        pass

    @abstractmethod
    def delete_debate(self, debate_id: str) -> bool:
        """Delete debate by ID"""
        pass


class JSONStorageBackend(StorageBackend):
    """JSON file-based storage backend"""

    def __init__(self, storage_dir: str = "./data/debates"):
        """Initialize with storage directory"""
        self.storage_dir = storage_dir
        self.index_file = os.path.join(self.storage_dir, "_index.json")

        # Create directory if doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)

        # Initialize or load index
        if not os.path.exists(self.index_file):
            self._save_index([])

    def _load_index(self) -> list:
        """Load debate index"""
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_index(self, index: list) -> None:
        """Save debate index"""
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)

    def save_debate(self, debate: DebateRecord) -> str:
        """Save debate to JSON file"""
        debate_id = debate.debate_id
        debate_file = os.path.join(self.storage_dir, f"{debate_id}.json")

        # Serialize debate to JSON
        debate_json = debate.model_dump(mode='json')

        # Save to file
        with open(debate_file, 'w') as f:
            json.dump(debate_json, f, indent=2)

        # Update index
        index = self._load_index()
        index.append({
            "id": debate_id,
            "created_at": debate.created_at.isoformat(),
            "topic_title": debate.topic.title
        })
        self._save_index(index)

        return debate_id

    def get_debate(self, debate_id: str) -> DebateRecord:
        """Retrieve debate by ID"""
        debate_file = os.path.join(self.storage_dir, f"{debate_id}.json")

        if not os.path.exists(debate_file):
            raise FileNotFoundError(f"Debate {debate_id} not found")

        with open(debate_file, 'r') as f:
            debate_json = json.load(f)

        return DebateRecord(**debate_json)

    def list_debates(self, limit: int = 10) -> List[DebateRecord]:
        """List stored debates"""
        index = self._load_index()

        # Get most recent debates (reverse order)
        recent_debates = list(reversed(index))[:limit]

        debates = []
        for entry in recent_debates:
            try:
                debate = self.get_debate(entry["id"])
                debates.append(debate)
            except FileNotFoundError:
                # Skip if file not found
                pass

        return debates

    def delete_debate(self, debate_id: str) -> bool:
        """Delete debate by ID"""
        debate_file = os.path.join(self.storage_dir, f"{debate_id}.json")

        if not os.path.exists(debate_file):
            return False

        os.remove(debate_file)

        # Update index
        index = self._load_index()
        index = [entry for entry in index if entry["id"] != debate_id]
        self._save_index(index)

        return True
