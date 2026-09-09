from fastapi import APIRouter, Query
from typing import Optional
from ..db import get_connection
from ..services.statistiques import calculer_marge_du_jour

router = APIRouter(prefix="/statistiques", tags=["Statistiques"])


@router.get("/jour")
async def get_statistiques_jour():
    """
    Retourne les statistiques de la journée en cours.
    
    Inclut :
    - Chiffre d'affaires total
    - Marge totale  
    - Nombre de ventes
    - Les 5 derniers produits vendus avec leur marge individuelle
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Obtenir les statistiques globales du jour
    stats_globales = calculer_marge_du_jour()
    
    # Obtenir les 5 dernières transactions du jour avec les détails des produits
    cursor.execute("""
        SELECT 
            t.id,
            t.produit_id,
            t.quantite_vendue,
            t.prix_vente_snapshot,
            t.marge_totale,
            t.date_transaction,
            p.nom as produit_nom,
            p.code_qr as produit_code_qr
        FROM transactions t
        JOIN produits p ON t.produit_id = p.id
        WHERE date(t.date_transaction) = date('now', 'localtime')
        ORDER BY t.date_transaction DESC
        LIMIT 5
    """)
    
    dernieres_ventes = []
    for row in cursor.fetchall():
        dernieres_ventes.append({
            "transaction_id": row['id'],
            "produit_id": row['produit_id'],
            "produit_nom": row['produit_nom'],
            "produit_code_qr": row['produit_code_qr'],
            "quantite_vendue": row['quantite_vendue'],
            "prix_vente": row['prix_vente_snapshot'],
            "marge": row['marge_totale'],
            "date_transaction": row['date_transaction']
        })
    
    conn.close()
    
    return {
        "type": "marge_du_jour",
        **stats_globales,
        "dernieres_ventes": dernieres_ventes
    }