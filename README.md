#  YELMON Dev X

> Assistant de codage IA nouvelle génération

![YELMON Dev X](assets/screenshot.png)

##  Présentation

**YELMON Dev X** est un assistant de codage intelligent utilisant l'intelligence artificielle pour générer, analyser et optimiser votre code. Propulsé par un modèle Transformer entraîné sur des millions de lignes de code, il vous aide à coder plus vite et mieux.

##  Fonctionnalités

-  **Génération de code IA** - Décrivez ce que vous voulez, YELMON le génère
-  **Auto-correction** - Corrige automatiquement les erreurs
-  **Recherche sémantique** - Trouvez du code par similarité
-  **Exécution sandbox** - Testez votre code en toute sécurité
-  **Snippets** - Sauvegardez vos extraits de code préférés
-  **Multi-langages** - Python, JS, Java, C++, Go, Rust
-  **Authentification** - Comptes sécurisés avec JWT
-  **Statistiques** - Suivez votre progression

##  Technologies

| Composant | Technologie |
|-----------|-------------|
| Frontend | React + Electron |
| Backend | Flask + SocketIO |
| IA | PyTorch Transformers |
| Auth | JWT + Bcrypt |
| RAG | TF-IDF + Cosine |
| Build | Webpack + Electron Builder |

##  Installation

### Prérequis

- Python 3.8+
- Node.js 16+
- npm 8+

### Installation rapide

```bash
# Cloner le projet
git clone https://github.com/yelmon/yelmon-dev-x.git
cd yelmon-dev-x

# Installer
chmod +x installer.sh
./installer.sh

# Lancer
npm start
# Mode développement (hot reload)
npm run dev

# Build de production
npm run build

# Créer un exécutable
npm run dist:win  # Windows
npm run dist:mac  # macOS
npm run dist:linux # Linux
---

##  Résumé du branding YELMON Dev X

| Élément | Valeur |
|---------|--------|
| **Nom** | YELMON Dev X |
| **Version** | 1.0.0 |
| **Slogan** | "Codez plus vite, codez mieux" |
| **Couleurs** | #e94560 (rouge), #0f3460 (bleu), #533483 (violet) |
| **Icône** |  (éclair) |
| **Description** | Assistant de codage IA nouvelle génération |
| **Auteur** | YELMON Team |
| **Licence** | MIT |

---

L'application est maintenant complètement rebrandée en **YELMON Dev X** avec une identité visuelle forte et cohérente !
# Cloner ou extraire le projet
cd CodeAI_App

# Sur Linux/Mac
chmod +x installer.sh
./installer.sh

# Sur Windows
installer.bat
# Lancer en mode développement
npm run dev

# Ou lancer séparément
npm run dev:backend  # Backend Flask sur port 5001
npm run dev:frontend # Frontend React sur port 3000
# Construire l'application
npm run build

# Lancer l'application
npm start

# Créer un exécutable
npm run dist:win   # Windows
npm run dist:mac   # macOS
npm run dist:linux # Linux
