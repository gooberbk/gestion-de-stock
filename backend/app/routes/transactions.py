from fastapi import APIRouter, Query
from typing import Optional
from ..db import get_connection

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("")
async def get_transactions(limite: int = Query(20, ge=1, le=100, description="Nombre de transactions à retourner")):
    """
    Retourne les N dernières transactions triées par date décroissante.
    
    Inclut le nom du produit joint (pas seulement produit_id).
    Format cohérent avec les événements WebSocket "vente".
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            t.id,
            t.produit_id,
            t.quantite_vendue,
            t.prix_achat_snapshot,
            t.prix_vente_snapshot,
            t.marge_totale,
            t.prix_achat_estime,
            t.date_transaction,
            p.nom as produit_nom,
            p.code_qr as produit_code_qr,
            p.quantite_stock as stock_actuel
        FROM transactions t
        JOIN produits p ON t.produit_id = p.id
        ORDER BY t.date_transaction DESC
        LIMIT ?
    """, (limite,))
    
    transactions = []
    for row in cursor.fetchall():
        transactions.append({
            "type": "vente",
            "transaction_id": row['id'],
            "produit_id": row['produit_id'],
            "produit_nom": row['produit_nom'],
            "produit_code_qr": row['produit_code_qr'],
            "quantite_vendue": row['quantite_vendue'],
            "prix_vente_effectif": row['prix_vente_snapshot'],
            "prix_achat_snapshot": row['prix_achat_snapshot'],
            "marge_totale": row['marge_totale'],
            "prix_achat_estime": bool(row['prix_achat_estime']),
            "stock_apres_vente": row['stock_actuel'],
            "stock_negatif": row['stock_actuel'] < 0,
            "date_transaction": row['date_transaction']
        })
    
    conn.close()
    
    return {
        "transactions": transactions,
        "total": len(transactions)
    }