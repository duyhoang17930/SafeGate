import sqlite3

import numpy as np

from config import DATABASE_PATH


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            embedding BLOB NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()
    connection.close()


def add_user(student_id: str, name: str, embedding: np.ndarray) -> None:
    embedding = np.asarray(embedding, dtype=np.float32)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO users (student_id, name, embedding)
        VALUES (?, ?, ?)
        """,
        (student_id, name, embedding.tobytes()),
    )
    connection.commit()
    connection.close()


def get_all_users() -> list[dict]:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT id, student_id, name, embedding, created_at
        FROM users
        ORDER BY id
        """
    )
    rows = cursor.fetchall()
    connection.close()

    users = []
    for row in rows:
        users.append(
            {
                "id": row["id"],
                "student_id": row["student_id"],
                "name": row["name"],
                "embedding": np.frombuffer(row["embedding"], dtype=np.float32).copy(),
                "created_at": row["created_at"],
            }
        )
    return users


def user_exists(student_id: str) -> bool:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users WHERE student_id = ?", (student_id,))
    exists = cursor.fetchone() is not None
    connection.close()
    return exists

