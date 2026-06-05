"""
SQLite storage implementation for experience rules.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from exprule.storage.base import BaseStorage
from exprule.core.experience import Experience, Task, Step, Action
from exprule.core.context import Context
from exprule.core.feedback import Feedback, FeedbackType


class SQLiteStorage(BaseStorage):
    """SQLite-based persistent storage."""

    def __init__(self, db_path: str = "exprule.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiences (
                experience_id TEXT PRIMARY KEY,
                task_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                version INTEGER NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                metadata TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contexts (
                context_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedbacks (
                feedback_id TEXT PRIMARY KEY,
                experience_id TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (experience_id) REFERENCES experiences (experience_id)
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feedbacks_experience ON feedbacks(experience_id)
        ''')

        conn.commit()
        conn.close()

    def save_experience(self, experience: Experience) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()

        task_data = json.dumps(experience.task.model_dump())

        cursor.execute('''
            INSERT OR REPLACE INTO experiences 
            (experience_id, task_data, created_at, updated_at, version, is_active, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            experience.experience_id,
            task_data,
            experience.created_at.isoformat(),
            experience.updated_at.isoformat(),
            experience.version,
            1 if experience.is_active else 0,
            json.dumps(experience.metadata)
        ))

        conn.commit()
        conn.close()

    def get_experience(self, experience_id: str) -> Optional[Experience]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM experiences WHERE experience_id = ?', (experience_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        task_data = json.loads(row['task_data'])
        task = Task(**task_data)

        return Experience(
            experience_id=row['experience_id'],
            task=task,
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            version=row['version'],
            is_active=bool(row['is_active']),
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )

    def delete_experience(self, experience_id: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM feedbacks WHERE experience_id = ?', (experience_id,))
        cursor.execute('DELETE FROM experiences WHERE experience_id = ?', (experience_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()
        return deleted

    def list_experiences(self, limit: int = 100, offset: int = 0) -> List[Experience]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM experiences ORDER BY updated_at DESC LIMIT ? OFFSET ?', (limit, offset))
        rows = cursor.fetchall()
        conn.close()

        experiences: List[Experience] = []
        for row in rows:
            task_data = json.loads(row['task_data'])
            task = Task(**task_data)
            experiences.append(Experience(
                experience_id=row['experience_id'],
                task=task,
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                version=row['version'],
                is_active=bool(row['is_active']),
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            ))
        return experiences

    def search_experiences(
        self, query: str, tags: Optional[List[str]] = None, domain: Optional[str] = None
    ) -> List[Experience]:
        all_exps = self.list_experiences(limit=1000)
        results: List[Experience] = []
        query_lower = query.lower()

        for exp in all_exps:
            match = False
            if query_lower in exp.task.task_name.lower() or query_lower in exp.task.description.lower():
                match = True
            if tags:
                exp_tags = set(exp.task.tags)
                if not exp_tags & set(tags):
                    match = False
            if domain and exp.task.domain != domain:
                match = False
            if match:
                results.append(exp)
        return results

    def save_context(self, context: Context) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()

        data = json.dumps(context.model_dump())

        cursor.execute('''
            INSERT OR REPLACE INTO contexts (context_id, data, timestamp)
            VALUES (?, ?, ?)
        ''', (context.context_id, data, context.timestamp.isoformat()))

        conn.commit()
        conn.close()

    def get_context(self, context_id: str) -> Optional[Context]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM contexts WHERE context_id = ?', (context_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        data = json.loads(row['data'])
        return Context(**data)

    def save_feedback(self, feedback: Feedback) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()

        data = json.dumps(feedback.model_dump())

        cursor.execute('''
            INSERT OR REPLACE INTO feedbacks (feedback_id, experience_id, data, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (feedback.feedback_id, feedback.experience_id, data, feedback.timestamp.isoformat()))

        conn.commit()
        conn.close()

    def get_feedbacks_for_experience(self, experience_id: str) -> List[Feedback]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM feedbacks WHERE experience_id = ?', (experience_id,))
        rows = cursor.fetchall()
        conn.close()

        feedbacks: List[Feedback] = []
        for row in rows:
            data = json.loads(row['data'])
            feedbacks.append(Feedback(**data))
        return feedbacks

    def get_experience_count(self) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM experiences')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def clear_all(self) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM feedbacks')
        cursor.execute('DELETE FROM contexts')
        cursor.execute('DELETE FROM experiences')
        conn.commit()
        conn.close()
