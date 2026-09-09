#!/bin/bash

# Script de build pour créer l'exécutable autonome GestionStock
# Ce script doit être exécuté depuis le dossier backend/

set -e  # Arrêter le script en cas d'erreur

echo "🔨 Début du build de GestionStock..."

# Activer l'environnement virtuel s'il existe
if [ -d "venv_new" ]; then
    source venv_new/bin/activate
    echo "✅ Environnement virtuel activé"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Environnement virtuel activé"
fi

# Vérifier que PyInstaller est installé
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller n'est pas installé. Installation en cours..."
    pip install pyinstaller
fi

# Vérifier le chemin du projet
PROJECT_PATH=$(pwd)
if [[ "$PROJECT_PATH" =~ \  ]]; then
    echo "⚠️  ATTENTION: Le chemin du projet contient des espaces: $PROJECT_PATH"
    echo "⚠️  PyInstaller peut avoir des problèmes avec les chemins contenant des espaces."
    echo "⚠️  Il est recommandé de renommer le dossier pour supprimer les espaces."
    read -p "Continuer quand même? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Build annulé."
        exit 1
    fi
fi

if [[ "$PROJECT_PATH" =~ \(|\) ]]; then
    echo "⚠️  ATTENTION: Le chemin du projet contient des parenthèses: $PROJECT_PATH"
    echo "⚠️  PyInstaller peut avoir des problèmes avec les parenthèses dans les chemins."
    echo "⚠️  Il est recommandé de renommer le dossier pour supprimer les parenthèses."
    read -p "Continuer quand même? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Build annulé."
        exit 1
    fi
fi

echo "✅ Vérifications terminées. Lancement du build..."

# Lancer PyInstaller avec le fichier .spec
pyinstaller --clean gestion_stock.spec

echo "✅ Build terminé avec succès!"
echo "📦 L'exécutable se trouve dans: dist/GestionStock"
echo ""
echo "📝 Pour tester l'exécutable:"
echo "   cd dist"
echo "   ./GestionStock"
echo ""
echo "🗄️  La base de données sera créée à côté de l'exécutable (gestion_stock.db)"