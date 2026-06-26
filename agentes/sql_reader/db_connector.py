import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from mysql.connector.connection import MySQLConnection

load_dotenv(Path(__file__).parent / ".env")

_connection: MySQLConnection | None = None


def get_connection() -> MySQLConnection:
    global _connection
    if _connection is None or not _connection.is_connected():
        _connection = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", 3306)),
            user=os.environ.get("DB_USER", "agente"),
            password=os.environ.get("DB_PASSWORD", "agente123"),
            database=os.environ.get("DB_NAME", "agentes_db"),
        )
    return _connection
