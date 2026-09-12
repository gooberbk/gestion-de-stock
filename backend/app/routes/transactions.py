from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional
from datetime import datetime, date
from ..db import get_connection
from ..services.websocket import manager

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
            t.annulee,
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
            "date_transaction": row['date_transaction'],
            "annulee": bool(row['annulee']),
            "statut": "annulée" if bool(row['annulee']) else "active"
        })
    
    conn.close()
    
    return {
        "transactions": transactions,
        "total": len(transactions)
    }


@router.post("/{transaction_id}/annuler", status_code=status.HTTP_200_OK)
async def annuler_transaction(transaction_id: int):
    """
    Annule une transaction existante en restaurant le stock et en marquant la transaction comme annulée.
    
    Processus atomique :
    1. Vérifie que la transaction existe et n'est pas déjà annulée
    2. Vérifie que la transaction est du jour même
    3. Restaure le stock du produit (+ quantite_vendue)
    4. Insère un mouvement de stock (type='correction')
    5. Marque la transaction comme annulée (annulee=1)
    
    Diffuse un événement WebSocket "vente_annulee" avec l'id concerné.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Transaction atomique
        cursor.execute("BEGIN TRANSACTION")
        
        # 1. Récupérer la transaction
        cursor.execute("""
            SELECT t.id, t.produit_id, t.quantite_vendue, t.date_transaction, t.annulee,
                   p.nom as produit_nom, p.code_qr as produit_code_qr, p.quantite_stock as stock_actuel
            FROM transactions t
            JOIN produits p ON t.produit_id = p.id
            WHERE t.id = ?
        """, (transaction_id,))
        
        transaction = cursor.fetchone()
        
        if not transaction:
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction #{transaction_id} non trouvée"
            )
        
        # Vérifier si déjà annulée
        if bool(transaction['annulee']):
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transaction #{transaction_id} déjà annulée"
            )
        
        # 2. Vérifier que la transaction est du jour même
        date_transaction = datetime.strptime(transaction['date_transaction'], '%Y-%m-%d %H:%M:%S').date()
        aujourd_hui = date.today()
        
        if date_transaction != aujourd_hui:
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transaction #{transaction_id} n'est pas du jour même (date: {date_transaction})"
            )
        
        transaction_id = transaction['id']
        produit_id = transaction['produit_id']
        quantite_vendue = transaction['quantite_vendue']
        stock_actuel = transaction['stock_actuel']
        produit_nom = transaction['produit_nom']
        produit_code_qr = transaction['produit_code_qr']
        
        # 3. Restaurer le stock du produit
        nouveau_stock = stock_actuel + quantite_vendue
        cursor.execute("""
            UPDATE produits 
            SET quantite_stock = ?
            WHERE id = ?
        """, (nouveau_stock, produit_id))
        
        # 4. Insérer un mouvement de stock (type='correction')
        cursor.execute("""
            INSERT INTO mouvements_stock (
                produit_id, type_mouvement, quantite, note
            ) VALUES (?, 'correction', ?, ?)
        """, (produit_id, quantite_vendue, f"Annulation transaction #{transaction_id}"))
        
        mouvement_id = cursor.lastrowid
        
        # 5. Marquer la transaction comme annulée
        cursor.execute("""
            UPDATE transactions 
            SET annulee = 1
            WHERE id = ?
        """, (transaction_id,))
        
        # Commit de la transaction
        conn.commit()
        
        # Diffuser l'événement WebSocket vente_annulee
        await manager.broadcast_evenement("vente_annulee", {
            "transaction_id": transaction_id,
            "produit_id": produit_id,
            "produit_nom": produit_nom,
            "produit_code_qr": produit_code_qr,
            "quantite_vendue": quantite_vendue,
            "nouveau_stock": nouveau_stock,
            "mouvement_id": mouvement_id
        })
        
        return {
            "message": f"Transaction #{transaction_id} annulée avec succès",
            "transaction_id": transaction_id,
            "produit_id": produit_id,
            "produit_nom": produit_nom,
            "quantite_restaurée": quantite_vendue,
            "nouveau_stock": nouveau_stock,
            "mouvement_id": mouvement_id
        }
        
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'annulation de la transaction: {str(e)}"
        )
    finally:
        conn.close()