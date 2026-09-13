"""Módulo de banco de dados SQLite e rotinas de bootstrap."""

import os
import sqlite3
from werkzeug.security import generate_password_hash

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    """
    Inicializa o banco de dados criando as tabelas e o administrador inicial.
    
    Regras:
    1. Cria a tabela users caso não exista.
    2. Verifica se o usuário 'admin' já existe.
    3. Se não existir, insere o administrador com senha 'admin' em formato hash e is_admin = 1.
    4. Não sobrescreve nem duplica o administrador caso já exista.
    """
    # Garante que o diretório pai do banco exista
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.executescript(SCHEMA_SQL)

        # Verifica se o administrador inicial já existe
        cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
        admin_user = cursor.fetchone()

        if not admin_user:
            admin_password_hash = generate_password_hash("admin")
            cursor.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                ("admin", admin_password_hash, 1),
            )
        conn.commit()
    finally:
        conn.close()


def get_user_by_username(conn: sqlite3.Connection, username: str) -> sqlite3.Row | None:
    """Busca um usuário no banco pelo nome de usuário."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password_hash, is_admin FROM users WHERE username = ?",
        (username,),
    )
    return cursor.fetchone()


def create_user(
    conn: sqlite3.Connection,
    username: str,
    password_hash: str,
    is_admin: int = 0,
) -> int:
    """Insere um novo usuário na tabela users e retorna o ID inserido."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
        (username, password_hash, is_admin),
    )
    conn.commit()
    return cursor.lastrowid


