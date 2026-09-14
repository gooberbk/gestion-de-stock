from fastapi import HTTPException, status, Header
from typing import Optional
import os

# Clé API par défaut pour le pilote (à changer en production)
API_KEY = os.getenv("API_KEY", "pilote-key-2024-secret")

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Vérifier la clé API pour protéger les endpoints critiques.
    
    Pour le pilote en réseau local, cette protection est minimale mais
    empêche l'accès accidentel depuis des appareils non autorisés.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API manquante. Header X-API-Key requis."
        )
    
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé API invalide."
        )
    
    return True

def get_api_key_for_docs():
    """Retourner la clé API pour la documentation (à utiliser uniquement en dev)."""
    return API_KEY
