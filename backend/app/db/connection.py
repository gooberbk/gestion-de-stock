import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from .config import get_db_path


def get_connection() -> sqlite3.Connection:
    """
    Crée et retourne une connexion SQLite avec les clés étrangères activées.
    
    Returns:
        sqlite3.Connection: Connexion à la base de données
    """
    db_path = get_db_path()
    
    # Créer le répertoire parent si nécessaire
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    conn.execute("PRAGMA foreign_keys = ON")
    
    return conn


@contextmanager
def get_db_context():
    """
    Context manager pour gérer automatiquement la connexion à la base de données.
    
    Usage:
        with get_db_context() as conn:
            conn.execute("SELECT * FROM produits")
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
