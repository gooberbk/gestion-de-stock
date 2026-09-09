from pydantic import BaseModel, Field, computed_field
from typing import Optional, List
from datetime import datetime


class ProduitCreate(BaseModel):
    code_qr: str = Field(..., min_length=1, description="Code QR ou code-barres du produit")
    nom: str = Field(..., min_length=1, description="Nom du produit")
    categorie: Optional[str] = Field(None, description="Catégorie du produit")
    prix_achat: float = Field(..., gt=0, description="Prix d'achat du produit")
    prix_vente: float = Field(..., gt=0, description="Prix de vente du produit")
    quantite_stock: int = Field(default=0, ge=0, description="Quantité en stock")
    seuil_alerte: int = Field(default=5, ge=0, description="Seuil d'alerte pour le stock")
    prix_achat_confirme: bool = Field(default=False, description="Prix d'achat confirmé ou estimé")


class ProduitUpdate(BaseModel):
    code_qr: Optional[str] = Field(None, min_length=1, description="Code QR ou code-barres du produit")
    nom: Optional[str] = Field(None, min_length=1, description="Nom du produit")
    categorie: Optional[str] = Field(None, description="Catégorie du produit")
    prix_achat: Optional[float] = Field(None, gt=0, description="Prix d'achat du produit")
    prix_vente: Optional[float] = Field(None, gt=0, description="Prix de vente du produit")
    quantite_stock: Optional[int] = Field(None, ge=0, description="Quantité en stock")
    seuil_alerte: Optional[int] = Field(None, ge=0, description="Seuil d'alerte pour le stock")
    prix_achat_confirme: Optional[bool] = Field(None, description="Prix d'achat confirmé ou estimé")


class ProduitResponse(BaseModel):
    id: int
    code_qr: str
    nom: str
    categorie: Optional[str]
    prix_achat: float
    prix_vente: float
    quantite_stock: int
    seuil_alerte: int
    prix_achat_confirme: bool
    date_creation: str
    actif: bool

    @computed_field
    @property
    def marge_negative(self) -> bool:
        """Calcule automatiquement si la marge est négative."""
        return self.prix_vente <= self.prix_achat

    model_config = {"from_attributes": True}


class ProduitListResponse(BaseModel):
    produits: List[ProduitResponse]
    total: int
