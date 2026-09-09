import os
from pathlib import Path

def get_db_path() -> Path:
    """
    Retourne le chemin de la base de données SQLite.
    Priorité :
    1. Variable d'environnement DB_PATH
    2. Chemin par défaut : gestion_stock.db dans le répertoire du projet
    """
    # 1. Variable d'environnement
    db_path = os.getenv("DB_PATH")
    if db_path:
        return Path(db_path)
    
    # 2. Chemin par défaut
    project_root = Path(__file__).parent.parent.parent
    return project_root / "gestion_stock.db"
