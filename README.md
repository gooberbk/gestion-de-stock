# Gestion de Stock - Application pour Commerçants Indépendants

Application de gestion de stock 100% locale pour commerçants indépendants avec scan de codes QR/barcodes, décrémentation automatique du stock, calcul de marge et affichage en temps réel sur mobile.

## Architecture

### Stack Technique
- **Backend** : Python 3, FastAPI, SQLite, WebSocket natif FastAPI
- **Frontend Mobile** : React Native (Expo), TypeScript
- **Architecture** : 100% locale (aucun service cloud, aucun coût d'infrastructure)

### Structure du Projet
```
gestion-de-stock/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── models/        # Modèles de données
│   │   ├── routes/        # Routes API
│   │   ├── services/      # Logique métier
│   │   └── db/            # Configuration base de données
│   ├── main.py            # Point d'entrée FastAPI
│   └── pyproject.toml     # Dépendances Python
├── mobile/                # Application React Native
│   ├── src/
│   │   ├── screens/       # Écrans de l'application
│   │   ├── components/    # Composants réutilisables
│   │   └── services/      # Services API et WebSocket
│   ├── App.tsx            # Point d'entrée React Native
│   ├── package.json       # Dépendances Node
│   └── app.json           # Configuration Expo
└── README.md
```

### Schéma de Base de Données

#### `produits`
- id, code_qr, nom, categorie
- prix_achat, prix_vente, quantite_stock, seuil_alerte
- prix_achat_confirme, date_creation, actif

#### `transactions`
- id, produit_id, quantite_vendue
- prix_achat_snapshot, prix_vente_snapshot, marge_totale
- prix_achat_estime, date_transaction, synced

#### `mouvements_stock`
- id, produit_id, type_mouvement, quantite
- date_mouvement, note

#### `utilisateurs`
- id, nom, role, pin_code, date_creation

### Règles Métier
- Vente autorisée même si stock devient négatif (alerte visuelle)
- Prix de vente ajustable au scan (négociation) sans modifier le catalogue
- Prix d'achat estimé puis confirmé (recalcul rétroactif de la marge)

## Installation et Lancement

### Backend (FastAPI)

1. **Créer l'environnement virtuel**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

2. **Installer les dépendances**
```bash
pip install -e .
```

3. **Lancer le serveur**
```bash
python main.py
```

Le serveur sera accessible sur `http://localhost:8000`

### Frontend Mobile (React Native + Expo)

1. **Installer les dépendances**
```bash
cd mobile
npm install
```

2. **Lancer l'application**
```bash
npm start
```

Ou pour une plateforme spécifique :
```bash
npm run android    # Pour Android
npm run ios        # Pour iOS
npm run web        # Pour le web
```

## Configuration Réseau

L'application mobile doit être connectée au même réseau WiFi que le PC du commerçant pour communiquer avec le backend via WebSocket.

## Prochaines Étapes

- [ ] Implémentation des modèles de base de données
- [ ] Création des routes API REST
- [ ] Configuration WebSocket pour la communication temps réel
- [ ] Intégration du scan de codes QR/barcodes
- [ ] Développement de l'interface mobile
- [ ] Implémentation du calcul de marge
- [ ] Tests et validation
