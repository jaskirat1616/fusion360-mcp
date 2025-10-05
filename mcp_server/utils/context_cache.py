"""
Context caching for conversation history and design state
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from loguru import logger


class ContextCache:
    """
    Cache for storing conversation context and design state
    Supports both JSON file and SQLite backends
    """

    def __init__(self, cache_type: str = "json", cache_path: str = "context_cache.json"):
        """
        Initialize context cache

        Args:
            cache_type: "json" or "sqlite"
            cache_path: Path to cache file
        """
        self.cache_type = cache_type
        self.cache_path = Path(cache_path)
        self.db_conn: Optional[sqlite3.Connection] = None

        if cache_type == "json":
            self._init_json_cache()
        elif cache_type == "sqlite":
            self._init_sqlite_cache()
        else:
            raise ValueError(f"Unsupported cache type: {cache_type}")

    def _init_json_cache(self) -> None:
        """Initialize JSON file cache"""
        if not self.cache_path.exists():
            self.cache_path.write_text(json.dumps({
                "conversations": [],
                "design_states": [],
                "actions_history": []
            }, indent=2))
            logger.info(f"Created JSON cache at {self.cache_path}")

    def _init_sqlite_cache(self) -> None:
        """Initialize SQLite database cache"""
        self.db_conn = sqlite3.connect(str(self.cache_path), check_same_thread=False)
        cursor = self.db_conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_input TEXT NOT NULL,
                llm_response TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                metadata TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS design_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                context TEXT NOT NULL,
                geometry_snapshot TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actions_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action_type TEXT NOT NULL,
                action_data TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT
            )
        """)

        self.db_conn.commit()
        logger.info(f"Initialized SQLite cache at {self.cache_path}")

    def save_conversation(
        self,
        user_input: str,
        llm_response: str,
        provider: str,
        model: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Save a conversation exchange"""
        timestamp = datetime.now().isoformat()

        if self.cache_type == "json":
            data = json.loads(self.cache_path.read_text())
            data["conversations"].append({
                "timestamp": timestamp,
                "user_input": user_input,
                "llm_response": llm_response,
                "provider": provider,
                "model": model,
                "metadata": metadata or {}
            })
            self.cache_path.write_text(json.dumps(data, indent=2))

        elif self.cache_type == "sqlite":
            cursor = self.db_conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (timestamp, user_input, llm_response, provider, model, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                (timestamp, user_input, llm_response, provider, model, json.dumps(metadata or {}))
            )
            self.db_conn.commit()

        logger.debug(f"Saved conversation: {user_input[:50]}...")

    def save_design_state(
        self,
        context: Dict[str, Any],
        geometry_snapshot: Optional[Dict[str, Any]] = None
    ) -> None:
        """Save design state"""
        timestamp = datetime.now().isoformat()

        if self.cache_type == "json":
            data = json.loads(self.cache_path.read_text())
            data["design_states"].append({
                "timestamp": timestamp,
                "context": context,
                "geometry_snapshot": geometry_snapshot or {}
            })
            self.cache_path.write_text(json.dumps(data, indent=2))

        elif self.cache_type == "sqlite":
            cursor = self.db_conn.cursor()
            cursor.execute(
                "INSERT INTO design_states (timestamp, context, geometry_snapshot) VALUES (?, ?, ?)",
                (timestamp, json.dumps(context), json.dumps(geometry_snapshot or {}))
            )
            self.db_conn.commit()

        logger.debug("Saved design state")

    def save_action(
        self,
        action_type: str,
        action_data: Dict[str, Any],
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """Save action execution result"""
        timestamp = datetime.now().isoformat()

        if self.cache_type == "json":
            data = json.loads(self.cache_path.read_text())
            data["actions_history"].append({
                "timestamp": timestamp,
                "action_type": action_type,
                "action_data": action_data,
                "success": success,
                "error_message": error_message
            })
            self.cache_path.write_text(json.dumps(data, indent=2))

        elif self.cache_type == "sqlite":
            cursor = self.db_conn.cursor()
            cursor.execute(
                "INSERT INTO actions_history (timestamp, action_type, action_data, success, error_message) VALUES (?, ?, ?, ?, ?)",
                (timestamp, action_type, json.dumps(action_data), success, error_message)
            )
            self.db_conn.commit()

        logger.debug(f"Saved action: {action_type}")

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations"""
        if self.cache_type == "json":
            data = json.loads(self.cache_path.read_text())
            return data["conversations"][-limit:]

        elif self.cache_type == "sqlite":
            cursor = self.db_conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "user_input": row[2],
                    "llm_response": row[3],
                    "provider": row[4],
                    "model": row[5],
                    "metadata": json.loads(row[6]) if row[6] else {}
                }
                for row in reversed(rows)
            ]

        return []

    def get_recent_actions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent actions"""
        if self.cache_type == "json":
            data = json.loads(self.cache_path.read_text())
            return data["actions_history"][-limit:]

        elif self.cache_type == "sqlite":
            cursor = self.db_conn.cursor()
            cursor.execute(
                "SELECT * FROM actions_history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "action_type": row[2],
                    "action_data": json.loads(row[3]),
                    "success": bool(row[4]),
                    "error_message": row[5]
                }
                for row in reversed(rows)
            ]

        return []

    def clear_cache(self) -> None:
        """Clear all cached data"""
        if self.cache_type == "json":
            self.cache_path.write_text(json.dumps({
                "conversations": [],
                "design_states": [],
                "actions_history": []
            }, indent=2))

        elif self.cache_type == "sqlite":
            cursor = self.db_conn.cursor()
            cursor.execute("DELETE FROM conversations")
            cursor.execute("DELETE FROM design_states")
            cursor.execute("DELETE FROM actions_history")
            self.db_conn.commit()

        logger.info("Cache cleared")

    def close(self) -> None:
        """Close database connection if using SQLite"""
        if self.cache_type == "sqlite" and self.db_conn:
            self.db_conn.close()
            logger.info("Closed SQLite connection")
