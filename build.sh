#!/bin/bash
# build.sh - Build YELMON Dev X sur Linux/Mac
echo "========================================"
echo "    YELMON Dev X - Build Automatique"
echo "========================================"
echo ""

echo " Vérification de l'environnement..."
python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo " Python 3 non trouvé. Veuillez installer Python 3.8+"
    exit 1
fi

node --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo " Node.js non trouvé. Veuillez installer Node.js 16+"
    exit 1
fi

echo " Environnement OK"
echo ""

echo " Lancement du build..."
python3 build.py --all

if [ $? -ne 0 ]; then
    echo " Build échoué"
    exit 1
fi

echo ""
echo "========================================"
echo " Build terminé avec succès!"
echo " Dossier de sortie: dist/"
echo "========================================"
