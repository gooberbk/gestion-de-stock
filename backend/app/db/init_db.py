import sqlite3
from .connection import get_connection


def init_database():
    """
    Initialise la base de données en créant les 4 tables si elles n'existent pas.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table produits
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_qr TEXT UNIQUE NOT NULL,
            nom TEXT NOT NULL,
            categorie TEXT,
            prix_achat REAL NOT NULL,
            prix_vente REAL NOT NULL,
            quantite_stock INTEGER NOT NULL DEFAULT 0,
            seuil_alerte INTEGER NOT NULL DEFAULT 5,
            prix_achat_confirme BOOLEAN NOT NULL DEFAULT 0,
            date_creation TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            actif BOOLEAN NOT NULL DEFAULT 1
        )
    """)
    
    # Table transactions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produit_id INTEGER NOT NULL,
            quantite_vendue INTEGER NOT NULL,
            prix_achat_snapshot REAL NOT NULL,
            prix_vente_snapshot REAL NOT NULL,
            marge_totale REAL NOT NULL,
            prix_achat_estime BOOLEAN NOT NULL DEFAULT 0,
            date_transaction TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            synced BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (produit_id) REFERENCES produits(id)
        )
    """)
    
    # Table mouvements_stock
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mouvements_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produit_id INTEGER NOT NULL,
            type_mouvement TEXT NOT NULL,
            quantite INTEGER NOT NULL,
            date_mouvement TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            note TEXT,
            FOREIGN KEY (produit_id) REFERENCES produits(id)
        )
    """)
    
    # Table utilisateurs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            role TEXT NOT NULL,
            pin_code TEXT NOT NULL,
            date_creation TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    """)
    
    # Créer des index pour optimiser les requêtes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_produits_code_qr 
        ON produits(code_qr)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_produit_id 
        ON transactions(produit_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_mouvements_stock_produit_id 
        ON mouvements_stock(produit_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transactions_date 
        ON transactions(date_transaction)
    """)
    
    conn.commit()
    conn.close()
    
    print("Base de données initialisée avec succès.")


if __name__ == "__main__":
    init_database()
