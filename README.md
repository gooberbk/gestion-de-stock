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

### Backend (FastAPI) - Mode Développement

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

### Backend - Création d'un Exécutable Autonome (Production)

Pour créer un exécutable Windows qui ne nécessite pas d'installation Python :

**Prérequis :**
- Python 3.8+ installé sur la machine de build
- Le chemin du projet ne doit pas contenir d'espaces ou de parenthèses

**Étapes :**

1. **Installer PyInstaller**
```bash
cd backend
pip install pyinstaller
```

2. **Lancer le build**
```bash
# Sur Linux/Mac
chmod +x build.sh
./build.sh

# Sur Windows
build.bat
```

3. **Tester l'exécutable**
```bash
cd dist
./GestionStock           # Sur Linux/Mac
GestionStock.exe         # Sur Windows
```

L'exécutable créera automatiquement la base de données `gestion_stock.db` à côté de lui.

**Note :** L'exécutable peut être distribué sur n'importe quelle machine Windows/Mac/Linux sans Python installé.

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

## État Actuel du Projet

### Backend - Fonctionnel et Testé (100%)
- Structure de base de données SQLite avec 4 tables
- API REST complète pour la gestion des produits (CRUD)
- API REST pour les ventes et réapprovisionnements
- WebSocket pour communication temps réel
- Découverte réseau locale via mDNS
- Génération de QR code pour connexion
- Endpoints de statistiques et historique
- Calcul automatique de la marge
- Gestion des stocks négatifs avec alertes
- Packaging en exécutable autonome (PyInstaller) ✅ **TESTÉ**
- Tests d'intégration WebSocket et API ✅ **RÉUSSIS**

### Frontend Mobile - Fonctionnel (85%)
- Structure Expo/React Native configurée
- ConnexionContext avec AsyncStorage
- React Navigation configuré
- Écran de connexion avec scan QR code
- Dashboard temps réel avec graphiques et statistiques
- Écran d'historique des transactions
- Services WebSocket et HTTP
- Chargement initial des données (REST) + mises à jour temps réel (WebSocket)
- Alertes visuelles pour stock négatif

### Architecture Validée
- **Point de vente** : PC + douchette USB (backend via `POST /ventes`)
- **Mobile** : Afficheur passif temps réel (reçoit événements WebSocket)
- **Réseau** : WiFi local, communication 100% locale

## API Documentation

L'API FastAPI inclut une documentation interactive Swagger disponible sur :
- `http://localhost:8000/docs` (Interface Swagger)
- `http://localhost:8000/redoc` (Documentation ReDoc)

### Endpoints Principaux

**Produits :**
- `POST /produits` - Créer un produit
- `GET /produits` - Lister les produits
- `GET /produits/{id}` - Détails d'un produit
- `PUT /produits/{id}` - Mettre à jour un produit
- `DELETE /produits/{id}` - Supprimer un produit (soft delete)

**Ventes :**
- `POST /ventes` - Enregistrer une vente
- `POST /ventes/reapprovisionnements` - Réapprovisionner un produit

**Statistiques :**
- `GET /statistiques/jour` - Statistiques du jour
- `GET /transactions?limite=20` - Historique des transactions

**Connexion :**
- `GET /connexion-info` - QR code de connexion
- `GET /connexion-info/json` - Infos connexion JSON
- `WS /ws` - WebSocket temps réel
