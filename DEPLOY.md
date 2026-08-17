# Guide de déploiement — YELMON Dev X

L'app est accessible en local ET sur internet en même temps.

---

## Option 1 : Render.com (Recommandé — gratuit, Docker)

### Prérequis
1. Installe **Git** → https://git-scm.com/download/win
2. Crée un compte **GitHub** → https://github.com
3. Crée un compte **Render** → https://render.com

### Étapes
```bash
# Dans le dossier projet
cd C:\Users\chris\Documents\ProjetsPython\YELMON_Dev_X
git init
git add .
git commit -m "YELMON Dev X v1.0"
```
4. Crée un repo sur **github.com** (New Repository) → nom: `yelmon-dev-x`
```bash
git remote add origin https://github.com/TON_USER/yelmon-dev-x.git
git push -u origin main
```
5. Sur **render.com** :
   - **New +** → **Web Service**
   - Connecte ton repo GitHub `yelmon-dev-x`
   - Render détecte `render.yaml` automatiquement
   - **Runtime**: Docker
   - **Port**: 10000
   - Clique **Deploy**

### URL publique
→ `https://yelmon-dev-x.onrender.com`

---

## Option 2 : Railway.app (5$/mois gratuits)

1. Crée un compte sur https://railway.app
2. **New Project** → **Deploy from GitHub**
3. Sélectionne le repo `yelmon-dev-x`
4. Railway détecte `railway.json` automatiquement
5. → `https://yelmon-dev-x.up.railway.app`

---

## Option 3 : Fly.io (gratuit, Docker)

```bash
curl -L https://fly.io/install.sh | sh
fly auth login
cd YELMON_Dev_X
fly launch
fly deploy
```
→ `https://yelmon-dev-x.fly.dev`

---

## Option 4 : Local (WiFi uniquement)

```bash
python deploy_web.py
```
→ `http://192.168.1.72:5001` depuis un autre appareil du réseau

---

## Accès simultanés

| Accès | URL | Portée |
|-------|-----|--------|
| Local | `http://192.168.1.72:5001` | Ton réseau WiFi |
| Cloud | `https://yelmon-dev-x.onrender.com` | Internet mondial |

Les deux fonctionnent en parallèle, même base de données.
