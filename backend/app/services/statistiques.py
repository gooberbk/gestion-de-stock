from datetime import datetime, date
from ..db import get_connection


def calculer_marge_du_jour() -> dict:
    """
    Calculer les statistiques du jour en cours.
    
    Returns:
        dict: Contient le total des marges et du chiffre d'affaires du jour
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Obtenir la date du jour au format SQLite
    aujourd_hui = date.today().isoformat()
    
    # Calculer le total des marges du jour (en excluant les transactions annulées)
    cursor.execute("""
        SELECT 
            COALESCE(SUM(marge_totale), 0) as total_marge,
            COALESCE(SUM(prix_vente_snapshot * quantite_vendue), 0) as total_ca,
            COUNT(*) as nombre_ventes
        FROM transactions
        WHERE date(date_transaction) = ? AND annulee = 0
    """, (aujourd_hui,))
    
    result = cursor.fetchone()
    
    conn.close()
    
    return {
        "date": aujourd_hui,
        "total_marge": float(result['total_marge']) if result['total_marge'] else 0.0,
        "total_ca": float(result['total_ca']) if result['total_ca'] else 0.0,
        "nombre_ventes": result['nombre_ventes'] if result['nombre_ventes'] else 0
    }
