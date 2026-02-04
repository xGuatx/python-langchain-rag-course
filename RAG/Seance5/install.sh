#!/bin/bash

echo "============================================================"
echo "Installation Séance 5 - Projet RAG Simplifié"
echo "============================================================"

# 1. Vérifier Python
echo "1. Vérification de Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "   ✓ Python $PYTHON_VERSION trouvé"
else
    echo "   ❌ Python 3 non trouvé"
    echo "   Veuillez installer Python 3.8 ou supérieur"
    exit 1
fi

# 2. Créer l'environnement virtuel (optionnel)
echo "2. Configuration de l'environnement Python..."
read -p "Créer un environnement virtuel ? (y/N): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    if [ ! -d "venv" ]; then
        echo "   Création de l'environnement virtuel..."
        python3 -m venv venv
        echo "   ✓ Environnement virtuel créé"
    else
        echo "   ✓ Environnement virtuel existant"
    fi
    
    # Activer l'environnement
    source venv/bin/activate
    echo "   ✓ Environnement virtuel activé"
else
    echo "   ✓ Utilisation de l'environnement Python global"
fi

# 3. Mettre à jour pip
echo "3. Mise à jour de pip..."
python3 -m pip install --upgrade pip

# 4. Installer les dépendances
echo "4. Installation des dépendances..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "   ✓ Dépendances installées avec succès"
else
    echo "   ❌ Erreur lors de l'installation des dépendances"
    exit 1
fi

# 5. Créer le fichier .env s'il n'existe pas
echo "5. Configuration de l'environnement..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Configuration API (optionnel)
# CODESTRAL_API_KEY=your_api_key_here
# OPENAI_API_KEY=your_openai_key_here

# Configuration RAG
RAG_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EOF
    echo "   ✓ Fichier .env créé"
else
    echo "   ✓ Fichier .env existant"
fi

# 6. Créer la structure des dossiers
echo "6. Création de la structure des dossiers..."
mkdir -p data logs
echo "   ✓ Dossiers créés: data, logs"

# 7. Test des imports Python
echo "7. Test des imports Python..."
python3 -c "
try:
    import sentence_transformers
    import flask
    import rich
    import numpy
    print('✓ Tous les imports réussis')
except ImportError as e:
    print(f'❌ Erreur d\\'import: {e}')
    exit(1)
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "   ✓ Tous les modules Python disponibles"
else
    echo "   ❌ Erreur d'import Python"
    exit 1
fi

# 8. Vérifier la présence du corpus (optionnel)
echo "8. Vérification du corpus..."
if [ -d "data" ]; then
    echo "   ✓ Dossier data présent"
    echo "   💡 Placez vos documents dans le dossier 'data' pour l'indexation"
else
    echo "   ⚠️ Dossier data manquant"
fi

# 9. Instructions PostgreSQL
echo "9. Configuration PostgreSQL..."
echo "   💡 Ce système utilise PostgreSQL avec l'extension pgvector"
echo "   💡 Assurez-vous d'avoir PostgreSQL installé et configuré"
echo "   💡 Base de données par défaut : rag_database"
echo "   💡 Utilisateur par défaut : postgres/postgres"

echo ""
echo "============================================================"
echo "INSTALLATION TERMINÉE"
echo "============================================================"
echo "Configuration du système RAG:"
echo "  ✓ Dépendances Python installées"
echo "  ✓ Configuration .env créée"
echo "  ✓ Structure des dossiers créée"
echo ""
echo "Prochaines étapes:"
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "  1. Activer l'environnement: source venv/bin/activate"
fi
echo "  2. Placer vos documents dans le dossier 'data/'"
echo "  3. Indexer le corpus: python rag_indexer.py"
echo "  4. Tester le système: python validation_finale.py"
echo "  5. Lancer l'interface: python cli_interface.py"
echo ""
echo "Système RAG prêt à l'emploi !"
echo "============================================================"

