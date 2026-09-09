import os
import sys
from pathlib import Path

def get_db_path() -> Path:
    """
    Retourne le chemin de la base de données SQLite.
    Priorité :
    1. Variable d'environnement DB_PATH
    2. Si packagé avec PyInstaller : à côté de l'exécutable
    3. Sinon : gestion_stock.db dans le répertoire du projet
    """
    # 1. Variable d'environnement
    db_path = os.getenv("DB_PATH")
    if db_path:
        return Path(db_path)
    
    # 2. Détection si l'application est packagée avec PyInstaller
    if getattr(sys, 'frozen', False):
        # L'application est packagée (exécutable)
        executable_dir = Path(sys.executable).parent
        return executable_dir / "gestion_stock.db"
    else:
        # L'application tourne en mode développement
        project_root = Path(__file__).parent.parent.parent
        return project_root / "gestion_stock.db"
