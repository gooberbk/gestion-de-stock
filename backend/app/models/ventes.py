from pydantic import BaseModel, Field, field_validator
from typing import Optional


class VenteCreate(BaseModel):
    code_qr: str = Field(..., min_length=1, description="Code QR ou code-barres du produit")
    quantite_vendue: int = Field(..., gt=0, description="Quantité vendue")
    prix_vente_override: Optional[float] = Field(None, gt=0, description="Prix de vente négocié (optionnel)")

    @field_validator('quantite_vendue')
    @classmethod
    def quantite_positive(cls, v):
        if v <= 0:
            raise ValueError('La quantité vendue doit être positive')
        return v


class VenteResponse(BaseModel):
    produit_id: int
    quantite_vendue: int
    prix_vente_effectif: float
    prix_achat_snapshot: float
    marge_totale: float
    prix_achat_estime: bool
    stock_apres_vente: int
    stock_negatif: bool
    transaction_id: int
    produit_nom: str
    produit_code_qr: str


class ReapprovisionnementCreate(BaseModel):
    code_qr: str = Field(..., min_length=1, description="Code QR ou code-barres du produit")
    quantite: int = Field(..., gt=0, description="Quantité ajoutée au stock")
    prix_achat: Optional[float] = Field(None, gt=0, description="Nouveau prix d'achat (optionnel)")
    prix_achat_confirme: Optional[bool] = Field(None, description="Confirmer le prix d'achat")
    note: Optional[str] = Field(None, description="Note sur le réapprovisionnement")

    @field_validator('quantite')
    @classmethod
    def quantite_positive(cls, v):
        if v <= 0:
            raise ValueError('La quantité doit être positive')
        return v


class ReapprovisionnementResponse(BaseModel):
    produit_id: int
    quantite_ajoutee: int
    stock_apres_reappro: int
    mouvement_id: int
    produit_nom: str
    produit_code_qr: str
    prix_achat_mis_a_jour: Optional[float] = None
