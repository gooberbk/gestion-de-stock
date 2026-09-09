from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from ..db import get_db_context
from ..models.produits import ProduitCreate, ProduitUpdate, ProduitResponse, ProduitListResponse

router = APIRouter(prefix="/produits", tags=["Produits"])


@router.post("", response_model=ProduitResponse, status_code=status.HTTP_201_CREATED)
async def create_produit(produit: ProduitCreate):
    """
    Créer un nouveau produit.
    
    - **code_qr**: Code QR ou code-barres unique du produit
    - **nom**: Nom du produit
    - **categorie**: Catégorie optionnelle
    - **prix_achat**: Prix d'achat (peut être estimé)
    - **prix_vente**: Prix de vente
    - **quantite_stock**: Quantité initiale en stock
    - **seuil_alerte**: Seuil d'alerte pour le stock
    - **prix_achat_confirme**: Indique si le prix d'achat est confirmé ou estimé
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        
        # Vérifier si le code QR existe déjà
        cursor.execute("SELECT id FROM produits WHERE code_qr = ?", (produit.code_qr,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Un produit avec le code QR '{produit.code_qr}' existe déjà"
            )
        
        # Insérer le nouveau produit
        cursor.execute("""
            INSERT INTO produits (
                code_qr, nom, categorie, prix_achat, prix_vente, 
                quantite_stock, seuil_alerte, prix_achat_confirme
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            produit.code_qr, produit.nom, produit.categorie, produit.prix_achat,
            produit.prix_vente, produit.quantite_stock, produit.seuil_alerte,
            produit.prix_achat_confirme
        ))
        
        produit_id = cursor.lastrowid
        
        # Récupérer le produit créé
        cursor.execute("SELECT * FROM produits WHERE id = ?", (produit_id,))
        row = cursor.fetchone()
        
        return ProduitResponse(**dict(row))


@router.get("", response_model=ProduitListResponse)
async def list_produits(categorie: Optional[str] = Query(None, description="Filtrer par catégorie")):
    """
    Lister tous les produits actifs.
    
    - **categorie**: Optionnel, filtre par catégorie
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        
        if categorie:
            cursor.execute("""
                SELECT * FROM produits 
                WHERE actif = 1 AND categorie = ?
                ORDER BY nom
            """, (categorie,))
        else:
            cursor.execute("""
                SELECT * FROM produits 
                WHERE actif = 1
                ORDER BY nom
            """)
        
        rows = cursor.fetchall()
        produits = [ProduitResponse(**dict(row)) for row in rows]
        
        return ProduitListResponse(produits=produits, total=len(produits))


@router.get("/{produit_id}", response_model=ProduitResponse)
async def get_produit(produit_id: int):
    """
    Récupérer les détails d'un produit par son ID.
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produits WHERE id = ?", (produit_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produit avec ID {produit_id} non trouvé"
            )
        
        return ProduitResponse(**dict(row))


@router.put("/{produit_id}", response_model=ProduitResponse)
async def update_produit(produit_id: int, produit: ProduitUpdate):
    """
    Mettre à jour un produit existant.
    
    Permet la confirmation ultérieure du prix d'achat et la modification de tous les champs.
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        
        # Vérifier si le produit existe
        cursor.execute("SELECT * FROM produits WHERE id = ?", (produit_id,))
        existing = cursor.fetchone()
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produit avec ID {produit_id} non trouvé"
            )
        
        # Construire la requête de mise à jour dynamique
        update_fields = []
        update_values = []
        
        if produit.code_qr is not None:
            # Vérifier si le nouveau code QR existe déjà (sauf pour le même produit)
            cursor.execute(
                "SELECT id FROM produits WHERE code_qr = ? AND id != ?",
                (produit.code_qr, produit_id)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Un produit avec le code QR '{produit.code_qr}' existe déjà"
                )
            update_fields.append("code_qr = ?")
            update_values.append(produit.code_qr)
        
        if produit.nom is not None:
            update_fields.append("nom = ?")
            update_values.append(produit.nom)
        
        if produit.categorie is not None:
            update_fields.append("categorie = ?")
            update_values.append(produit.categorie)
        
        if produit.prix_achat is not None:
            update_fields.append("prix_achat = ?")
            update_values.append(produit.prix_achat)
        
        if produit.prix_vente is not None:
            update_fields.append("prix_vente = ?")
            update_values.append(produit.prix_vente)
        
        if produit.quantite_stock is not None:
            update_fields.append("quantite_stock = ?")
            update_values.append(produit.quantite_stock)
        
        if produit.seuil_alerte is not None:
            update_fields.append("seuil_alerte = ?")
            update_values.append(produit.seuil_alerte)
        
        if produit.prix_achat_confirme is not None:
            update_fields.append("prix_achat_confirme = ?")
            update_values.append(produit.prix_achat_confirme)
        
        if not update_fields:
            # Aucun champ à mettre à jour
            return ProduitResponse(**dict(existing))
        
        update_values.append(produit_id)
        
        # Exécuter la mise à jour
        query = f"UPDATE produits SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, update_values)
        
        # Récupérer le produit mis à jour
        cursor.execute("SELECT * FROM produits WHERE id = ?", (produit_id,))
        row = cursor.fetchone()
        
        return ProduitResponse(**dict(row))


@router.delete("/{produit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_produit(produit_id: int):
    """
    Supprimer un produit (soft delete).
    
    Le produit n'est pas supprimé de la base de données, mais marqué comme inactif (actif = 0).
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        
        # Vérifier si le produit existe
        cursor.execute("SELECT * FROM produits WHERE id = ?", (produit_id,))
        existing = cursor.fetchone()
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produit avec ID {produit_id} non trouvé"
            )
        
        # Soft delete : passer actif à 0
        cursor.execute("UPDATE produits SET actif = 0 WHERE id = ?", (produit_id,))
        
        return None
