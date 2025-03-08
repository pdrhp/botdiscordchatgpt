"""
Sistema de armazenamento de mensagens para manter contexto de conversas.
"""

import os
import time
import sqlite3
from typing import List, Dict, Any, Optional
from collections import deque
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)

class MessageStore:
    def __init__(self, channel_id: Optional[str] = None, max_messages: int = 50,
                 use_persistence: bool = False, db_path: str = "data/messages.db"):
        self.channel_id = channel_id
        self.max_messages = max_messages
        self.messages = deque(maxlen=max_messages)
        self.use_persistence = use_persistence
        self.db_path = db_path

        if use_persistence:
            self._setup_db()
            self._load_from_db()

    def add_user_message(self, user_id: str, username: str, content: str) -> None:
        message = {
            "role": "user",
            "content": content,
            "user_id": user_id,
            "username": username,
            "timestamp": time.time()
        }
        self._add_message(message)

    def add_assistant_message(self, content: str) -> None:
        message = {
            "role": "assistant",
            "content": content,
            "timestamp": time.time()
        }
        self._add_message(message)

    def add_system_message(self, content: str) -> None:
        message = {
            "role": "system",
            "content": content,
            "timestamp": time.time()
        }
        self._add_message(message)

    def get_messages(self) -> List[Dict[str, str]]:
        formatted_messages = []

        for msg in self.messages:
            if msg["role"] == "user":
                content = f"{msg.get('username', 'Usuário')}: {msg['content']}"
                formatted_messages.append({"role": "user", "content": content})
            else:
                formatted_messages.append({"role": msg["role"], "content": msg["content"]})

        return formatted_messages

    def get_raw_messages(self) -> List[Dict[str, Any]]:
        return list(self.messages)

    def clear(self) -> None:
        self.messages.clear()
        if self.use_persistence and self.channel_id:
            self._clear_from_db()

    def _add_message(self, message: Dict[str, Any]) -> None:
        self.messages.append(message)
        if self.use_persistence and self.channel_id:
            self._save_to_db()

    def _setup_db(self) -> None:
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS channel_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            user_id TEXT,
            username TEXT,
            timestamp REAL NOT NULL,
            UNIQUE(channel_id, timestamp)
        )
        ''')

        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_channel_timestamp
        ON channel_messages(channel_id, timestamp)
        ''')

        conn.commit()
        conn.close()

    def _save_to_db(self) -> None:
        if not self.channel_id:
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
            DELETE FROM channel_messages
            WHERE channel_id = ?
            AND timestamp NOT IN (
                SELECT timestamp FROM channel_messages
                WHERE channel_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            )
            ''', (self.channel_id, self.channel_id, self.max_messages))

            latest_msg = self.messages[-1]

            values = [
                self.channel_id,
                latest_msg["role"],
                latest_msg["content"],
                latest_msg.get("user_id"),
                latest_msg.get("username"),
                latest_msg["timestamp"]
            ]

            cursor.execute('''
            INSERT OR REPLACE INTO channel_messages
            (channel_id, role, content, user_id, username, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', values)

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem no banco de dados: {e}")

    def _load_from_db(self) -> None:
        if not self.channel_id:
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
            SELECT role, content, user_id, username, timestamp
            FROM channel_messages
            WHERE channel_id = ?
            ORDER BY timestamp ASC
            LIMIT ?
            ''', (self.channel_id, self.max_messages))

            rows = cursor.fetchall()

            self.messages.clear()
            for role, content, user_id, username, timestamp in rows:
                msg = {
                    "role": role,
                    "content": content,
                    "timestamp": timestamp
                }

                if user_id:
                    msg["user_id"] = user_id
                if username:
                    msg["username"] = username

                self.messages.append(msg)

            conn.close()
        except Exception as e:
            logger.error(f"Erro ao carregar mensagens do banco de dados: {e}")

    def _clear_from_db(self) -> None:
        if not self.channel_id:
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
            DELETE FROM channel_messages WHERE channel_id = ?
            ''', (self.channel_id,))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Erro ao limpar mensagens do banco de dados: {e}")


class MessageManager:
    """
    Gerenciador global de armazenamentos de mensagens para múltiplos canais.
    """
    def __init__(self, use_persistence: bool = False, db_path: str = "data/messages.db"):
        self.stores = {}
        self.use_persistence = use_persistence
        self.db_path = db_path
        self.config = get_config()

    def get_store(self, channel_id: str) -> MessageStore:
        if channel_id not in self.stores:
            self.stores[channel_id] = MessageStore(
                channel_id=channel_id,
                max_messages=self.config.max_context_messages,
                use_persistence=self.use_persistence,
                db_path=self.db_path
            )
        return self.stores[channel_id]

    def clear_store(self, channel_id: str) -> bool:
        if channel_id in self.stores:
            self.stores[channel_id].clear()
            return True
        return False

    def cleanup_old_stores(self, max_age_seconds: int = 86400) -> int:
        """
        Remove armazenamentos de mensagens inativos.

        Args:
            max_age_seconds: Idade máxima em segundos (padrão: 24 horas)

        Returns:
            Número de armazenamentos removidos
        """
        current_time = time.time()
        to_remove = []

        for channel_id, store in self.stores.items():
            if not store.messages:
                to_remove.append(channel_id)
                continue

            latest_msg = max(msg["timestamp"] for msg in store.messages)
            if current_time - latest_msg > max_age_seconds:
                to_remove.append(channel_id)

        for channel_id in to_remove:
            del self.stores[channel_id]

        return len(to_remove)

    def cleanup_db(self, max_age_seconds: int = 604800) -> int:
        """
        Remove mensagens antigas do banco de dados.

        Args:
            max_age_seconds: Idade máxima em segundos (padrão: 7 dias)

        Returns:
            Número de mensagens removidas
        """
        if not self.use_persistence:
            return 0

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_time = time.time() - max_age_seconds
            cursor.execute('''
            DELETE FROM channel_messages WHERE timestamp < ?
            ''', (cutoff_time,))

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            return deleted_count
        except Exception as e:
            logger.error(f"Erro ao limpar mensagens antigas do banco de dados: {e}")
            return 0
