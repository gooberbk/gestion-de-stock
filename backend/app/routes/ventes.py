from fastapi import APIRouter, HTTPException, status
from ..db import get_connection
from ..models.ventes import VenteCreate, VenteResponse, ReapprovisionnementCreate, ReapprovisionnementResponse
from ..services.websocket import manager
from ..services.statistiques import calculer_marge_du_jour

router = APIRouter(prefix="/ventes", tags=["Ventes"])


@router.post("", response_model=VenteResponse, status_code=status.HTTP_201_CREATED)
async def create_vente(vente: VenteCreate):
    """
    Enregistrer une vente à partir d'un scan de code QR.
    
    Processus atomique :
    1. Récupérer le produit via code_qr
    2. Déterminer le prix de vente effectif (override ou catalogue)
    3. Calculer la marge
    4. Insérer la transaction
    5. Insérer le mouvement de stock
    6. Décrémenter le stock (autorise stock négatif)
    
    Retourne l'état mis à jour avec alerte si stock négatif.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Transaction atomique
        cursor.execute("BEGIN TRANSACTION")
        
        # 1. Récupérer le produit via code_qr
        cursor.execute("""
            SELECT id, code_qr, nom, prix_achat, prix_vente, quantite_stock, 
                   prix_achat_confirme, actif
            FROM produits 
            WHERE code_qr = ?
        """, (vente.code_qr,))
        
        produit = cursor.fetchone()
        
        if not produit:
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produit avec code QR '{vente.code_qr}' non trouvé"
            )
        
        if not bool(produit['actif']):
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produit avec code QR '{vente.code_qr}' est inactif"
            )
        
        produit_id = produit['id']
        produit_nom = produit['nom']
        code_qr = produit['code_qr']
        prix_achat = produit['prix_achat']
        prix_vente_catalogue = produit['prix_vente']
        stock_actuel = produit['quantite_stock']
        prix_achat_confirme = bool(produit['prix_achat_confirme'])
        
        # 2. Déterminer le prix de vente effectif
        prix_vente_effectif = vente.prix_vente_override if vente.prix_vente_override else prix_vente_catalogue
        
        # 3. Calculer la marge
        marge_totale = (prix_vente_effectif - prix_achat) * vente.quantite_vendue
        
        # 4. Insérer la transaction
        cursor.execute("""
            INSERT INTO transactions (
                produit_id, quantite_vendue, prix_achat_snapshot, 
                prix_vente_snapshot, marge_totale, prix_achat_estime
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            produit_id, vente.quantite_vendue, prix_achat,
            prix_vente_effectif, marge_totale, 0 if prix_achat_confirme else 1
        ))
        
        transaction_id = cursor.lastrowid
        
        # 5. Insérer le mouvement de stock
        cursor.execute("""
            INSERT INTO mouvements_stock (
                produit_id, type_mouvement, quantite, note
            ) VALUES (?, 'vente', ?, ?)
        """, (produit_id, -vente.quantite_vendue, f"Vente - Transaction #{transaction_id}"))
        
        mouvement_id = cursor.lastrowid
        
        # 6. Décrémenter le stock (autorise stock négatif)
        nouveau_stock = stock_actuel - vente.quantite_vendue
        cursor.execute("""
            UPDATE produits 
            SET quantite_stock = ?
            WHERE id = ?
        """, (nouveau_stock, produit_id))
        
        # Commit de la transaction
        conn.commit()
        
        # Déterminer si le stock est négatif pour l'alerte
        stock_negatif = nouveau_stock < 0
        
        # Diffuser l'événement de vente aux clients WebSocket connectés
        await manager.broadcast_evenement("vente", {
            "produit_id": produit_id,
            "produit_nom": produit_nom,
            "produit_code_qr": code_qr,
            "quantite_vendue": vente.quantite_vendue,
            "nouveau_stock": nouveau_stock,
            "marge": marge_totale,
            "stock_negatif": stock_negatif,
            "transaction_id": transaction_id
        })
        
        # Calculer et diffuser les statistiques du jour
        stats_du_jour = calculer_marge_du_jour()
        await manager.broadcast_evenement("marge_du_jour", stats_du_jour)
        
        return VenteResponse(
            produit_id=produit_id,
            quantite_vendue=vente.quantite_vendue,
            prix_vente_effectif=prix_vente_effectif,
            prix_achat_snapshot=prix_achat,
            marge_totale=marge_totale,
            prix_achat_estime=False if prix_achat_confirme else True,
            stock_apres_vente=nouveau_stock,
            stock_negatif=stock_negatif,
            transaction_id=transaction_id,
            produit_nom=produit_nom,
            produit_code_qr=code_qr
        )
        
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'enregistrement de la vente: {str(e)}"
        )
    finally:
        conn.close()


@router.post("/reapprovisionnements", response_model=ReapprovisionnementResponse, status_code=status.HTTP_201_CREATED)
async def create_reapprovisionnement(reappro: ReapprovisionnementCreate):
    """
    Ajouter du stock à un produit existant.
    
    Peut mettre à jour le prix d'achat si fourni et gérer le flag de confirmation.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        # Récupérer le produit
        cursor.execute("""
            SELECT id, code_qr, nom, quantite_stock, prix_achat, prix_achat_confirme, actif
            FROM produits 
            WHERE code_qr = ?
        """, (reappro.code_qr,))
        
        produit = cursor.fetchone()
        
        if not produit:
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produit avec code QR '{reappro.code_qr}' non trouvé"
            )
        
        if not bool(produit['actif']):
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produit avec code QR '{reappro.code_qr}' est inactif"
            )
        
        produit_id = produit['id']
        produit_nom = produit['nom']
        code_qr = produit['code_qr']
        stock_actuel = produit['quantite_stock']
        prix_achat_actuel = produit['prix_achat']
        prix_achat_confirme_actuel = bool(produit['prix_achat_confirme'])
        
        # Mettre à jour le stock
        nouveau_stock = stock_actuel + reappro.quantite
        cursor.execute("""
            UPDATE produits 
            SET quantite_stock = ?
            WHERE id = ?
        """, (nouveau_stock, produit_id))
        
        # Mettre à jour le prix d'achat si fourni
        prix_achat_mis_a_jour = None
        if reappro.prix_achat is not None:
            cursor.execute("""
                UPDATE produits 
                SET prix_achat = ?
                WHERE id = ?
            """, (reappro.prix_achat, produit_id))
            prix_achat_mis_a_jour = reappro.prix_achat
        
        # Mettre à jour le flag de confirmation si fourni
        if reappro.prix_achat_confirme is not None:
            cursor.execute("""
                UPDATE produits 
                SET prix_achat_confirme = ?
                WHERE id = ?
            """, (1 if reappro.prix_achat_confirme else 0, produit_id))
        
        # Insérer le mouvement de stock
        note = reappro.note if reappro.note else "Réapprovisionnement"
        cursor.execute("""
            INSERT INTO mouvements_stock (
                produit_id, type_mouvement, quantite, note
            ) VALUES (?, 'reapprovisionnement', ?, ?)
        """, (produit_id, reappro.quantite, note))
        
        mouvement_id = cursor.lastrowid
        
        conn.commit()
        
        return ReapprovisionnementResponse(
            produit_id=produit_id,
            quantite_ajoutee=reappro.quantite,
            stock_apres_reappro=nouveau_stock,
            mouvement_id=mouvement_id,
            produit_nom=produit_nom,
            produit_code_qr=code_qr,
            prix_achat_mis_a_jour=prix_achat_mis_a_jour
        )
        
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du réapprovisionnement: {str(e)}"
        )
    finally:
        conn.close()
