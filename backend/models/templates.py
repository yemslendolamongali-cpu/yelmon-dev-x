"""YELMON Dev X - Templates de code par langage et par type."""

# ============================================================================
# PYTHON TEMPLATES
# ============================================================================

PYTHON_TEMPLATES = {}


def _py(name):
    def decorator(fn):
        PYTHON_TEMPLATES[name] = fn
        return fn
    return decorator


@_py("fibonacci")
def _py_fibonacci(p):
    return '''\
def fibonacci(n: int) -> list:
    """Retourne les n premiers nombres de Fibonacci."""
    if n <= 0:
        return []
    if n == 1:
        return [0]
    suite = [0, 1]
    for _ in range(2, n):
        suite.append(suite[-1] + suite[-2])
    return suite


if __name__ == "__main__":
    n = 10
    print(f"Fibonacci ({n}) : {fibonacci(n)}")
'''


@_py("factorielle")
def _py_factorielle(p):
    return '''\
def factorielle(n: int) -> int:
    """Calcule la factorielle de n de manière récursive."""
    if n < 0:
        raise ValueError("n doit être positif")
    return 1 if n <= 1 else n * factorielle(n - 1)


if __name__ == "__main__":
    for i in range(8):
        print(f"{i}! = {factorielle(i)}")
'''


@_py("tri")
def _py_sort(p):
    return '''\
def tri_bulle(liste: list) -> list:
    """Trie une liste par tri à bulles."""
    arr = list(liste)
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def tri_rapide(liste: list) -> list:
    """Trie une liste par tri rapide (quicksort)."""
    if len(liste) <= 1:
        return liste
    pivot = liste[len(liste) // 2]
    gauche = [x for x in liste if x < pivot]
    milieu = [x for x in liste if x == pivot]
    droite = [x for x in liste if x > pivot]
    return tri_rapide(gauche) + milieu + tri_rapide(droite)


if __name__ == "__main__":
    donnees = [64, 34, 25, 12, 22, 11, 90]
    print("Avant      :", donnees)
    print("Bulles     :", tri_bulle(donnees))
    print("Rapide     :", tri_rapide(donnees))
'''


@_py("palindrome")
def _py_palindrome(p):
    return '''\
def est_palindrome(s: str) -> bool:
    """Vérifie si une chaîne est un palindrome."""
    nettoyee = "".join(c.lower() for c in s if c.isalnum())
    return nettoyee == nettoyee[::-1]


if __name__ == "__main__":
    tests = ["radar", "YELMON", "Élu par cette crapule", "kayak"]
    for t in tests:
        print(f"{t!r:30s} -> palindrome ? {est_palindrome(t)}")
'''


@_py("premier")
def _py_prime(p):
    return '''\
def est_premier(n: int) -> bool:
    """Détermine si n est un nombre premier."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def premiers_jusqua(limite: int) -> list:
    """Retourne tous les nombres premiers inférieurs à limite."""
    return [n for n in range(2, limite) if est_premier(n)]


if __name__ == "__main__":
    print("Premiers < 50 :", premiers_jusqua(50))
'''


@_py("csv")
def _py_csv(p):
    return '''\
import csv
from pathlib import Path


def lire_csv(chemin: str) -> list[dict]:
    """Lit un fichier CSV et retourne une liste de dictionnaires."""
    with open(chemin, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def ecrire_csv(chemin: str, donnees: list[dict]):
    """Écrit une liste de dictionnaires dans un fichier CSV."""
    if not donnees:
        return
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=donnees[0].keys())
        writer.writeheader()
        writer.writerows(donnees)


if __name__ == "__main__":
    exemple = [{"nom": "Alice", "age": "30"}, {"nom": "Bob", "age": "25"}]
    ecrire_csv("exemple.csv", exemple)
    print(lire_csv("exemple.csv"))
'''


@_py("scraping")
def _py_scraper(p):
    return '''\
import requests
from bs4 import BeautifulSoup


def scraper_titres(url: str) -> list[str]:
    """Récupère les titres (h2) d'une page web."""
    reponse = requests.get(url, timeout=10)
    reponse.raise_for_status()
    soup = BeautifulSoup(reponse.text, "html.parser")
    return [h.get_text(strip=True) for h in soup.find_all("h2")]


def scraper_liens(url: str) -> list[dict]:
    """Récupère tous les liens d'une page web."""
    reponse = requests.get(url, timeout=10)
    reponse.raise_for_status()
    soup = BeautifulSoup(reponse.text, "html.parser")
    return [{"texte": a.get_text(strip=True), "href": a.get("href", "")}
            for a in soup.find_all("a", href=True)]


if __name__ == "__main__":
    titres = scraper_titres("https://example.com")
    for t in titres:
        print(f"  - {t}")
'''


@_py("api_flask")
def _py_api_flask(p):
    return '''\
from flask import Flask, jsonify, request
from functools import wraps

app = Flask(__name__)

# --- Base de données simulée ---
items = [
    {"id": 1, "nom": "Alpha", "actif": True},
    {"id": 2, "nom": "Beta", "actif": False},
    {"id": 3, "nom": "Gamma", "actif": True},
]
next_id = 4


def valider_json(*champs):
    """Décorateur pour valider les champs JSON de la requête."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            data = request.get_json(silent=True) or {}
            manquants = [c for c in champs if c not in data]
            if manquants:
                return jsonify({"error": f"Champs manquants : {manquants}"}), 400
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@app.route("/api/items", methods=["GET"])
def lister_items():
    actif = request.args.get("actif")
    resultat = items
    if actif is not None:
        resultat = [i for i in items if i["actif"] == (actif.lower() == "true")]
    return jsonify({"items": resultat, "total": len(resultat)})


@app.route("/api/items/<int:item_id>", methods=["GET"])
def obtenir_item(item_id):
    item = next((i for i in items if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Introuvable"}), 404
    return jsonify(item)


@app.route("/api/items", methods=["POST"])
@valider_json("nom")
def creer_item():
    global next_id
    data = request.get_json()
    item = {"id": next_id, "nom": data["nom"], "actif": data.get("actif", True)}
    next_id += 1
    items.append(item)
    return jsonify(item), 201


@app.route("/api/items/<int:item_id>", methods=["PUT"])
def modifier_item(item_id):
    item = next((i for i in items if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Introuvable"}), 404
    data = request.get_json(silent=True) or {}
    item.update({k: v for k, v in data.items() if k != "id"})
    return jsonify(item)


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def supprimer_item(item_id):
    global items
    avant = len(items)
    items = [i for i in items if i["id"] != item_id]
    if len(items) == avant:
        return jsonify({"error": "Introuvable"}), 404
    return jsonify({"ok": True})


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "items": len(items)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
'''


@_py("api_fastapi")
def _py_api_fastapi(p):
    return '''\
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="YELMON API")


class ItemCreate(BaseModel):
    nom: str
    actif: bool = True


items: list[dict] = [{"id": 1, "nom": "Alpha", "actif": True}]
next_id = 2


@app.get("/api/items")
def lister_items():
    return {"items": items, "total": len(items)}


@app.get("/api/items/{item_id}")
def obtenir_item(item_id: int):
    item = next((i for i in items if i["id"] == item_id), None)
    if not item:
        raise HTTPException(404, "Introuvable")
    return item


@app.post("/api/items", status_code=201)
def creer_item(data: ItemCreate):
    global next_id
    item = {"id": next_id, **data.model_dump()}
    next_id += 1
    items.append(item)
    return item


@app.put("/api/items/{item_id}")
def modifier_item(item_id: int, data: ItemCreate):
    item = next((i for i in items if i["id"] == item_id), None)
    if not item:
        raise HTTPException(404, "Introuvable")
    item.update(data.model_dump())
    return item


@app.delete("/api/items/{item_id}")
def supprimer_item(item_id: int):
    global items
    avant = len(items)
    items = [i for i in items if i["id"] != item_id]
    if len(items) == avant:
        raise HTTPException(404, "Introuvable")
    return {"ok": True}


@app.get("/api/health")
def health():
    return {"status": "ok"}
'''


@_py("webapp")
def _py_webapp(p):
    return '''\
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YELMON WebApp</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui, sans-serif; background: #0f0f23; color: #e0e0e0; }
        .container { max-width: 800px; margin: 40px auto; padding: 20px; }
        h1 { text-align: center; margin-bottom: 30px; color: #ff6b6b; }
        .card { background: #1a1a3e; border-radius: 12px; padding: 20px; margin-bottom: 16px; }
        input, textarea { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 8px;
                          background: #0d0d2b; color: #fff; font-size: 14px; margin-bottom: 10px; }
        button { background: linear-gradient(135deg, #ff6b6b, #ffa500); color: #fff; border: none;
                 padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 14px; }
        button:hover { opacity: 0.9; }
        #output { margin-top: 20px; }
        .item { background: #12122e; padding: 12px; border-radius: 8px; margin-bottom: 8px;
                display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>YELMON WebApp</h1>
        <div class="card">
            <input id="nomInput" placeholder="Nom de l'élément...">
            <button onclick="ajouter()">Ajouter</button>
        </div>
        <div id="output"></div>
    </div>
    <script>
        let items = [];
        async function charger() {
            const r = await fetch("/api/items");
            const d = await r.json();
            items = d.items;
            afficher();
        }
        function afficher() {
            document.getElementById("output").innerHTML = items.map(i =>
                '<div class="item"><span>' + i.nom + '</span>' +
                '<button onclick="supprimer(' + i.id + ')">Supprimer</button></div>'
            ).join("");
        }
        async function ajouter() {
            const nom = document.getElementById("nomInput").value.trim();
            if (!nom) return;
            await fetch("/api/items", {method:"POST", headers:{"Content-Type":"application/json"},
                                       body: JSON.stringify({nom})});
            document.getElementById("nomInput").value = "";
            charger();
        }
        async function supprimer(id) {
            await fetch("/api/items/" + id, {method:"DELETE"});
            charger();
        }
        charger();
    </script>
</body>
</html>
"""

items = []
next_id = 1


@app.route("/")
def index():
    return render_template_string(PAGE)


@app.route("/api/items", methods=["GET"])
def api_list():
    return jsonify({"items": items})


@app.route("/api/items", methods=["POST"])
def api_create():
    global next_id
    data = request.get_json(silent=True) or {}
    nom = data.get("nom", "").strip()
    if not nom:
        return jsonify({"error": "nom requis"}), 400
    item = {"id": next_id, "nom": nom}
    next_id += 1
    items.append(item)
    return jsonify(item), 201


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def api_delete(item_id):
    global items
    items = [i for i in items if i["id"] != item_id]
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
'''


@_py("cli")
def _py_cli(p):
    return '''\
import argparse
import sys
import json
from pathlib import Path


def cmd_info(args):
    """Affiche les informations système."""
    import platform
    info = {
        "os": platform.system(),
        "version": platform.version(),
        "python": platform.python_version(),
        "machine": platform.machine(),
    }
    if args.json:
        print(json.dumps(info, indent=2))
    else:
        for k, v in info.items():
            print(f"  {k:12s}: {v}")


def cmd_liste(args):
    """Liste les fichiers du répertoire courant."""
    pattern = args.pattern or "*"
    fichiers = list(Path(".").glob(pattern))
    if args.all:
        fichiers = [f for f in fichiers if not f.name.startswith(".")]
    for f in sorted(fichiers):
        taille = f.stat().st_size if f.is_file() else 0
        prefix = "📄" if f.is_file() else "📁"
        print(f"  {prefix} {f.name:30s} {taille:>8,} octets")


def cmd_convertir(args):
    """Convertit un fichier JSON en YAML (ou inverse)."""
    source = Path(args.source)
    if not source.exists():
        print(f"Erreur : {source} introuvable", file=sys.stderr)
        sys.exit(1)
    contenu = source.read_text(encoding="utf-8")
    if args.format == "yaml":
        import yaml
        data = json.loads(contenu)
        print(yaml.dump(data, default_flow_style=False, allow_unicode=True))
    else:
        import yaml
        data = yaml.safe_load(contenu)
        print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="YELMON CLI - Outil en ligne de commande")
    sous = parser.add_subparsers(dest="commande")

    p_info = sous.add_parser("info", help="Informations système")
    p_info.add_argument("--json", action="store_true", help="Sortie JSON")

    p_liste = sous.add_parser("liste", help="Lister les fichiers")
    p_liste.add_argument("pattern", nargs="?", default="*", help="Glob pattern")
    p_liste.add_argument("-a", "--all", action="store_true", help="Inclure les fichiers cachés")

    p_conv = sous.add_parser("convertir", help="Convertir un fichier")
    p_conv.add_argument("source", help="Fichier source")
    p_conv.add_argument("-f", "--format", choices=["json", "yaml"], default="yaml")

    args = parser.parse_args()
    if not args.commande:
        parser.print_help()
        sys.exit(0)

    commandes = {"info": cmd_info, "liste": cmd_liste, "convertir": cmd_convertir}
    commandes[args.commande](args)


if __name__ == "__main__":
    main()
'''


@_py("telegram_bot")
def _py_telegram_bot(p):
    return '''\
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenue ! Je suis un bot YELMON.\\n"
        "/help - Aide\\n"
        "/info - Informations"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commandes disponibles :\\n"
        "/start - Démarrer\\n"
        "/help - Cette aide\\n"
        "/info - Infos bot"
    )


async def cmd_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot YELMON Dev X v1.0")


async def handleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Vous avez dit : {text}")


def main():
    TOKEN = "VOTRE_TOKEN_ICI"
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("info", cmd_info))
    app.add_handler(MessageHandler(filters.TEXT, handleMessage))
    print("Bot démarré...")
    app.run_polling()


if __name__ == "__main__":
    main()
'''


@_py("discord_bot")
def _py_discord_bot(p):
    return '''\
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")


@bot.command()
async def hello(ctx):
    await ctx.send("Bonjour ! Je suis un bot YELMON.")


@bot.command()
async def info(ctx):
    embed = discord.Embed(title="YELMON Bot", description="Bot Discord YELMON Dev X", color=0xFF6B6B)
    embed.add_field(name="Version", value="1.0.0")
    embed.add_field(name="Serveurs", value=str(len(bot.guilds)))
    await ctx.send(embed=embed)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "yelmon" in message.content.lower():
        await message.add_reaction("\\U0001F44D")
    await bot.process_commands(message)


TOKEN = "VOTRE_TOKEN_ICI"
bot.run(TOKEN)
'''


@_py("game")
def _py_game(p):
    return '''\
import pygame
import random
import sys

pygame.init()

LARGEUR, HAUTEUR = 800, 600
FPS = 60

ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("YELMON Game")
horloge = pygame.time.Clock()

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
ROUGE = (255, 80, 80)
VERT = (80, 255, 80)
BLEU = (80, 160, 255)


class Joueur:
    def __init__(self):
        self.x = LARGEUR // 2
        self.y = HAUTEUR // 2
        self.taille = 20
        self.vitesse = 5
        self.score = 0

    def deplacer(self, touches):
        if touches[pygame.K_LEFT] or touches[pygame.K_a]:
            self.x -= self.vitesse
        if touches[pygame.K_RIGHT] or touches[pygame.K_d]:
            self.x += self.vitesse
        if touches[pygame.K_UP] or touches[pygame.K_w]:
            self.y -= self.vitesse
        if touches[pygame.K_DOWN] or touches[pygame.K_s]:
            self.y += self.vitesse
        self.x = max(0, min(LARGEUR - self.taille, self.x))
        self.y = max(0, min(HAUTEUR - self.taille, self.y))

    def dessiner(self, surface):
        pygame.draw.rect(surface, BLEU, (self.x, self.y, self.taille, self.taille))
        pygame.draw.rect(surface, BLANC, (self.x, self.y, self.taille, self.taille), 2)


class Objet:
    def __init__(self):
        self.x = random.randint(0, LARGEUR - 15)
        self.y = random.randint(0, HAUTEUR - 15)
        self.taille = 15

    def dessiner(self, surface):
        pygame.draw.rect(surface, ROUGE, (self.x, self.y, self.taille, self.taille))


def main():
    joueur = Joueur()
    objets = [Objet() for _ in range(5)]
    font = pygame.font.SysFont(None, 36)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        touches = pygame.key.get_pressed()
        joueur.deplacer(touches)

        joueur_rect = pygame.Rect(joueur.x, joueur.y, joueur.taille, joueur.taille)
        for obj in objets[:]:
            if joueur_rect.colliderect(pygame.Rect(obj.x, obj.y, obj.taille, obj.taille)):
                joueur.score += 1
                objets.remove(obj)
                objets.append(Objet())

        ecran.fill(NOIR)
        joueur.dessiner(ecran)
        for obj in objets:
            obj.dessiner(ecran)

        score_text = font.render(f"Score: {joueur.score}", True, VERT)
        ecran.blit(score_text, (10, 10))

        pygame.display.flip()
        horloge.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
'''


@_py("gui")
def _py_gui(p):
    return '''\
import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path


DATA_FILE = Path("taches.json")


def charger_taches():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return []


def sauvegarder_taches(taches):
    DATA_FILE.write_text(json.dumps(taches, indent=2, ensure_ascii=False), encoding="utf-8")


class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("YELMON Gestionnaire de Tâches")
        self.root.geometry("600x450")
        self.root.configure(bg="#1a1a3e")

        self.taches = charger_taches()

        # Titre
        tk.Label(root, text="YELMON Tâches", font=("Arial", 18, "bold"),
                 bg="#1a1a3e", fg="#ff6b6b").pack(pady=10)

        # Entrée
        frame_entree = tk.Frame(root, bg="#1a1a3e")
        frame_entree.pack(fill="x", padx=20, pady=5)
        self.entree = tk.Entry(frame_entree, font=("Arial", 12), bg="#0d0d2b", fg="white",
                               insertbackground="white")
        self.entree.pack(side="left", fill="x", expand=True)
        self.entree.bind("<Return>", self.ajouter)
        tk.Button(frame_entree, text="Ajouter", command=self.ajouter,
                  bg="#ff6b6b", fg="white", font=("Arial", 10)).pack(side="right", padx=(8, 0))

        # Liste
        self.liste = tk.Listbox(root, font=("Arial", 12), bg="#12122e", fg="white",
                                selectbackground="#ff6b6b", height=15)
        self.liste.pack(fill="both", expand=True, padx=20, pady=10)

        # Boutons
        frame_btns = tk.Frame(root, bg="#1a1a3e")
        frame_btns.pack(fill="x", padx=20, pady=(0, 10))
        tk.Button(frame_btns, text="Terminer", command=self.terminer,
                  bg="#4CAF50", fg="white").pack(side="left", padx=(0, 8))
        tk.Button(frame_btns, text="Supprimer", command=self.supprimer,
                  bg="#f44336", fg="white").pack(side="left")

        self.rafraichir_liste()

    def ajouter(self, event=None):
        texte = self.entree.get().strip()
        if not texte:
            return
        self.taches.append({"texte": texte, "faite": False})
        self.entree.delete(0, "end")
        self.sauvegarder()
        self.rafraichir_liste()

    def terminer(self):
        sel = self.liste.curselection()
        if not sel:
            return
        idx = sel[0]
        self.taches[idx]["faite"] = not self.taches[idx]["faite"]
        self.sauvegarder()
        self.rafraichir_liste()

    def supprimer(self):
        sel = self.liste.curselection()
        if not sel:
            return
        idx = sel[0]
        self.taches.pop(idx)
        self.sauvegarder()
        self.rafraichir_liste()

    def rafraichir_liste(self):
        self.liste.delete(0, "end")
        for t in self.taches:
            prefix = "\\u2705" if t["faite"] else "\\u2B1C"
            self.liste.insert("end", f"{prefix} {t['texte']}")

    def sauvegarder(self):
        sauvegarder_taches(self.taches)


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
'''


@_py("data_analysis")
def _py_data_analysis(p):
    return '''\
import csv
from collections import Counter
from pathlib import Path


def analyser_csv(chemin: str) -> dict:
    """Analyse un fichier CSV et retourne des statistiques."""
    with open(chemin, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        colonnes = reader.fieldnames or []
        lignes = list(reader)

    stats = {"lignes": len(lignes), "colonnes": colonnes, "stats_par_colonne": {}}

    for col in colonnes:
        valeurs = [ligne[col] for ligne in lignes if ligne.get(col)]
        col_stats = {"total": len(valeurs)}
        try:
            nums = [float(v) for v in valeurs]
            col_stats["type"] = "numerique"
            col_stats["moyenne"] = sum(nums) / len(nums) if nums else 0
            col_stats["min"] = min(nums) if nums else 0
            col_stats["max"] = max(nums) if nums else 0
            col_stats["mediane"] = sorted(nums)[len(nums) // 2] if nums else 0
        except ValueError:
            col_stats["type"] = "texte"
            col_stats["valeurs_uniques"] = len(set(valeurs))
            col_stats["plus_frequent"] = Counter(valeurs).most_common(1)
        stats["stats_par_colonne"][col] = col_stats

    return stats


def afficher_stats(stats: dict):
    print(f"=== Analyse du fichier CSV ===")
    print(f"Lignes    : {stats['lignes']}")
    print(f"Colonnes  : {', '.join(stats['colonnes'])}")
    print()
    for col, s in stats["stats_par_colonne"].items():
        print(f"  [{col}] ({s['type']})")
        if s["type"] == "numerique":
            print(f"    Moyenne : {s['moyenne']:.2f}")
            print(f"    Min     : {s['min']:.2f}")
            print(f"    Max     : {s['max']:.2f}")
            print(f"    Médiane : {s['mediane']:.2f}")
        else:
            print(f"    Uniques : {s['valeurs_uniques']}")
            if s["plus_frequent"]:
                print(f"    Top 1   : {s['plus_frequent'][0]}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        stats = analyser_csv(sys.argv[1])
        afficher_stats(stats)
    else:
        print("Usage: python analyse.py <fichier.csv>")
'''


@_py("websocket")
def _py_websocket(p):
    return '''\
import asyncio
import json
from datetime import datetime
from websockets.asyncio.server import serve


clients: set = set()


async def broadcaster(message: str):
    """Envoie un message à tous les clients connectés."""
    if clients:
        await asyncio.gather(*(c.send(message) for c in clients))


async def handler(websocket):
    clients.add(websocket)
    print(f"Client connecté ({len(clients)} total)")
    try:
        async for message in websocket:
            data = json.loads(message)
            data["timestamp"] = datetime.now().isoformat()
            data["from"] = str(websocket.remote_address)
            print(f"Message reçu : {data}")
            await broadcaster(json.dumps(data, ensure_ascii=False))
    except Exception:
        pass
    finally:
        clients.discard(websocket)
        print(f"Client déconnecté ({len(clients)} total)")


async def main():
    async with serve(handler, "localhost", 8765):
        print("WebSocket serveur démarré sur ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
'''


@_py("auth_jwt")
def _py_auth_jwt(p):
    return '''\
import hashlib
import hmac
import base64
import json
import time
from functools import wraps
from flask import Flask, request, jsonify


app = Flask(__name__)
SECRET = "yelmon-secret-key-change-in-production"


def hash_password(password: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), b"yelmon-salt", 100_000).hex()


def verify_password(stored: str, password: str) -> bool:
    return hmac.compare_digest(stored, hash_password(password))


def create_token(payload: dict, expires_hours: int = 24) -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode()
    payload["exp"] = int(time.time()) + expires_hours * 3600
    payload["iat"] = int(time.time())
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    sig = hmac.new(SECRET.encode(), f"{header}.{body}".encode(), hashlib.sha256).hexdigest()
    return f"{header}.{body}.{sig}"


def decode_token(token: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        sig = hmac.new(SECRET.encode(), f"{parts[0]}.{parts[1]}".encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, parts[2]):
            return None
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


users: dict = {}


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username, password = data.get("username", ""), data.get("password", "")
    if not username or not password:
        return jsonify({"error": "username et password requis"}), 400
    if username in users:
        return jsonify({"error": "Utilisateur déjà existant"}), 409
    users[username] = {"password": hash_password(password)}
    token = create_token({"username": username})
    return jsonify({"token": token, "username": username})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username, password = data.get("username", ""), data.get("password", "")
    user = users.get(username)
    if not user or not verify_password(user["password"], password):
        return jsonify({"error": "Identifiants invalides"}), 401
    token = create_token({"username": username})
    return jsonify({"token": token, "username": username})


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "") if auth.startswith("Bearer ") else auth
        payload = decode_token(token)
        if not payload:
            return jsonify({"error": "Non authentifié"}), 401
        request.user = payload
        return fn(*args, **kwargs)
    return wrapper


@app.route("/api/me")
@require_auth
def me():
    return jsonify({"username": request.user.get("username"), "ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
'''


@_py("machine_learning")
def _py_ml(p):
    return '''\
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, mean_squared_error


def exemple_regression():
    """Exemple de régression linéaire simple."""
    np.random.seed(42)
    X = np.random.rand(100, 1) * 10
    y = 2.5 * X.squeeze() + np.random.randn(100) * 2 + 5

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = LinearRegression()
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    mse = mean_squared_error(y_test, model.predict(X_test))

    print(f"Régression Linéaire :")
    print(f"  Coefficient : {model.coef_[0]:.3f}")
    print(f"  Intercept   : {model.intercept_:.3f}")
    print(f"  R²          : {score:.3f}")
    print(f"  MSE         : {mse:.3f}")
    return model


def exemple_classification():
    """Exemple de classification Random Forest."""
    np.random.seed(42)
    n = 200
    X = np.random.randn(n, 4)
    y = ((X[:, 0] + X[:, 1] * 2) > 0).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"\\nClassification Random Forest :")
    print(f"  Accuracy : {acc:.3f}")
    print(f"  Features importances : {model.feature_importances_}")
    return model


if __name__ == "__main__":
    exemple_regression()
    exemple_classification()
'''


@_py("docker")
def _py_docker(p):
    return '''\
# Dockerfile
# ---
# FROM python:3.12-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# EXPOSE 5000
# CMD ["python", "app.py"]

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({"message": "YELMON Docker App", "status": "running"})


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/info")
def info():
    import platform
    return jsonify({
        "python": platform.python_version(),
        "os": platform.system(),
        "hostname": platform.node(),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
'''


@_py("testing")
def _py_testing(p):
    return '''\
import unittest


def addition(a: float, b: float) -> float:
    return a + b


def division(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Division par zéro")
    return a / b


def est_vide(texte: str) -> bool:
    return not texte or not texte.strip()


class TestMathOperations(unittest.TestCase):
    def test_addition_positifs(self):
        self.assertEqual(addition(2, 3), 5)

    def test_addition_negatifs(self):
        self.assertEqual(addition(-1, -1), -2)

    def test_addition_zero(self):
        self.assertEqual(addition(0, 0), 0)

    def test_division_normale(self):
        self.assertAlmostEqual(division(10, 3), 3.333, places=2)

    def test_division_par_zero(self):
        with self.assertRaises(ValueError):
            division(1, 0)


class TestStringOperations(unittest.TestCase):
    def test_est_vide_vrai(self):
        self.assertTrue(est_vide(""))
        self.assertTrue(est_vide("   "))

    def test_est_vide_faux(self):
        self.assertFalse(est_vide("hello"))
        self.assertFalse(est_vide("  yelmon  "))


if __name__ == "__main__":
    unittest.main()
'''


@_py("default")
def _py_default(p):
    return '''\
def ma_fonction(*args):
    """Implémentation YELMON : adaptez ce squelette à votre besoin."""
    resultat = []
    for valeur in args:
        resultat.append(valeur)
    return resultat


if __name__ == "__main__":
    print(ma_fonction(1, 2, 3, 4))
    print("Généré par YELMON Dev X")
'''


# ============================================================================
# KEYWORD -> TEMPLATE MAPPING (Python)
# ============================================================================

_PY_KEYWORD_MAP = [
    (["fibonacci", "suite de fibo", "fibo"], "fibonacci"),
    (["factorielle", "factorial"], "factorielle"),
    (["tri", "sort", "trie", "quicksort"], "tri"),
    (["palindrome"], "palindrome"),
    (["premier", "prime", "premiers"], "premier"),
    (["csv", "lecture fichier", "lire"], "csv"),
    (["scrap", "crawl", "parse html", "beautifulsoup"], "scraping"),
    (["api", "flask", "endpoint", "route serveur"], "api_flask"),
    (["api", "fastapi"], "api_fastapi"),
    (["webapp", "web app", "site web", "page web"], "webapp"),
    (["cli", "command line", "terminal", "argparse"], "cli"),
    (["telegram", "bot telegram"], "telegram_bot"),
    (["discord", "bot discord"], "discord_bot"),
    (["jeu", "game", "pygame", "snake", "tetris"], "game"),
    (["gui", "tkinter", "interface", "desktop"], "gui"),
    (["data", "analyse csv", "pandas", "dataset"], "data_analysis"),
    (["websocket", "socket temps réel"], "websocket"),
    (["auth", "jwt", "login", "token", "password"], "auth_jwt"),
    (["machine learning", "ml", "ia", "sklearn", "tensorflow", "pytorch"], "machine_learning"),
    (["docker", "dockerfile", "container"], "docker"),
    (["test", "unittest", "pytest"], "testing"),
]


# ============================================================================
# JAVASCRIPT TEMPLATES
# ============================================================================

JS_TEMPLATES = {}


def _js(name):
    def decorator(fn):
        JS_TEMPLATES[name] = fn
        return fn
    return decorator


@_js("fibonacci")
def _js_fibonacci(p):
    return '''\
function fibonacci(n) {
  if (n <= 0) return [];
  if (n === 1) return [0];
  const suite = [0, 1];
  for (let i = 2; i < n; i++) {
    suite.push(suite[i - 1] + suite[i - 2]);
  }
  return suite;
}

console.log("Fibonacci (10) :", fibonacci(10));
'''


@_js("express_api")
def _js_express(p):
    return '''\
const express = require("express");
const app = express();
app.use(express.json());

let items = [
  { id: 1, nom: "Alpha", actif: true },
  { id: 2, nom: "Beta", actif: false },
];
let nextId = 3;

app.get("/api/items", (req, res) => {
  const { actif } = req.query;
  let result = items;
  if (actif !== undefined) {
    result = items.filter((i) => i.actif === (actif === "true"));
  }
  res.json({ items: result, total: result.length });
});

app.get("/api/items/:id", (req, res) => {
  const item = items.find((i) => i.id === Number(req.params.id));
  if (!item) return res.status(404).json({ error: "Introuvable" });
  res.json(item);
});

app.post("/api/items", (req, res) => {
  const { nom, actif = true } = req.body;
  if (!nom) return res.status(400).json({ error: "nom requis" });
  const item = { id: nextId++, nom, actif };
  items.push(item);
  res.status(201).json(item);
});

app.put("/api/items/:id", (req, res) => {
  const item = items.find((i) => i.id === Number(req.params.id));
  if (!item) return res.status(404).json({ error: "Introuvable" });
  Object.assign(item, req.body, { id: item.id });
  res.json(item);
});

app.delete("/api/items/:id", (req, res) => {
  const before = items.length;
  items = items.filter((i) => i.id !== Number(req.params.id));
  if (items.length === before) return res.status(404).json({ error: "Introuvable" });
  res.json({ ok: true });
});

app.get("/api/health", (req, res) => res.json({ status: "ok", items: items.length }));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`API sur http://localhost:${PORT}`));
'''


@_js("react_app")
def _js_react(p):
    return '''\
import React, { useState, useEffect } from "react";

function App() {
  const [items, setItems] = useState([]);
  const [nom, setNom] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/items")
      .then((r) => r.json())
      .then((d) => { setItems(d.items); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const ajouter = async () => {
    if (!nom.trim()) return;
    const r = await fetch("/api/items", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nom }),
    });
    const item = await r.json();
    setItems([...items, item]);
    setNom("");
  };

  const supprimer = async (id) => {
    await fetch(`/api/items/${id}`, { method: "DELETE" });
    setItems(items.filter((i) => i.id !== id));
  };

  if (loading) return <div>Chargement...</div>;

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "system-ui" }}>
      <h1>YELMON React App</h1>
      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        <input value={nom} onChange={(e) => setNom(e.target.value)}
               placeholder="Nouvel élément..."
               style={{ flex: 1, padding: 10, borderRadius: 6, border: "1px solid #ccc" }} />
        <button onClick={ajouter}
                style={{ padding: "10px 20px", background: "#ff6b6b", color: "#fff",
                         border: "none", borderRadius: 6, cursor: "pointer" }}>
          Ajouter
        </button>
      </div>
      {items.map((item) => (
        <div key={item.id} style={{ display: "flex", justifyContent: "space-between",
                                     padding: 12, background: "#f5f5f5", borderRadius: 8,
                                     marginBottom: 8 }}>
          <span>{item.nom}</span>
          <button onClick={() => supprimer(item.id)}
                  style={{ background: "#f44336", color: "#fff", border: "none",
                           borderRadius: 4, cursor: "pointer" }}>
            Supprimer
          </button>
        </div>
      ))}
    </div>
  );
}

export default App;
'''


@_js("discord_bot")
def _js_discord_bot(p):
    return '''\
const { Client, GatewayIntentBits } = require("discord.js");

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
});

client.once("ready", () => {
  console.log(`Connecté en tant que ${client.user.tag}`);
});

client.on("messageCreate", (message) => {
  if (message.author.bot) return;

  if (message.content === "!hello") {
    message.reply("Bonjour ! Je suis un bot YELMON.");
  }

  if (message.content === "!info") {
    message.reply({
      embeds: [{
        title: "YELMON Bot",
        description: "Bot Discord YELMON Dev X",
        color: 0xff6b6b,
        fields: [
          { name: "Version", value: "1.0.0", inline: true },
          { name: "Serveurs", value: String(client.guilds.cache.size), inline: true },
        ],
      }],
    });
  }

  if (message.content.toLowerCase().includes("yelmon")) {
    message.react("\\u{1F44D}");
  }
});

client.login("VOTRE_TOKEN_ICI");
'''


@_js("game")
def _js_game_canvas(p):
    return '''\
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>YELMON Snake</title>
  <style>
    body { margin: 0; background: #0f0f23; display: flex; justify-content: center;
           align-items: center; height: 100vh; }
    canvas { border: 2px solid #ff6b6b; border-radius: 8px; }
  </style>
</head>
<body>
<canvas id="game" width="400" height="400"></canvas>
<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const TAILLE = 20;
const COLS = canvas.width / TAILLE;
const ROWS = canvas.height / TAILLE;

let serpent = [{ x: 10, y: 10 }];
let direction = { x: 1, y: 0 };
let food = spawnFood();
let score = 0;
let gameOver = false;

function spawnFood() {
  let pos;
  do {
    pos = { x: Math.floor(Math.random() * COLS), y: Math.floor(Math.random() * ROWS) };
  } while (serpent.some(s => s.x === pos.x && s.y === pos.y));
  return pos;
}

function update() {
  if (gameOver) return;
  const head = { x: serpent[0].x + direction.x, y: serpent[0].y + direction.y };
  if (head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS) { gameOver = true; return; }
  if (serpent.some(s => s.x === head.x && s.y === head.y)) { gameOver = true; return; }
  serpent.unshift(head);
  if (head.x === food.x && head.y === food.y) { score++; food = spawnFood(); }
  else serpent.pop();
}

function draw() {
  ctx.fillStyle = "#0f0f23";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  serpent.forEach((s, i) => {
    ctx.fillStyle = i === 0 ? "#00bfff" : "#0077be";
    ctx.fillRect(s.x * TAILLE, s.y * TAILLE, TAILLE - 1, TAILLE - 1);
  });
  ctx.fillStyle = "#ff6b6b";
  ctx.fillRect(food.x * TAILLE, food.y * TAILLE, TAILLE - 1, TAILLE - 1);
  ctx.fillStyle = "#fff";
  ctx.font = "16px monospace";
  ctx.fillText(`Score: ${score}`, 10, 20);
  if (gameOver) { ctx.fillText("GAME OVER - Appuyez R", 80, 200); }
}

document.addEventListener("keydown", (e) => {
  const key = e.key;
  if (key === "ArrowUp" && direction.y !== 1) direction = { x: 0, y: -1 };
  else if (key === "ArrowDown" && direction.y !== -1) direction = { x: 0, y: 1 };
  else if (key === "ArrowLeft" && direction.x !== 1) direction = { x: -1, y: 0 };
  else if (key === "ArrowRight" && direction.x !== -1) direction = { x: 1, y: 0 };
  if (key.toLowerCase() === "r" && gameOver) {
    serpent = [{ x: 10, y: 10 }]; direction = { x: 1, y: 0 };
    food = spawnFood(); score = 0; gameOver = false;
  }
});

setInterval(() => { update(); draw(); }, 120);
</script>
</body>
</html>
'''


_JS_KEYWORD_MAP = [
    (["fibonacci"], "fibonacci"),
    (["api", "express", "node", "npm"], "express_api"),
    (["react", "jsx", "tsx"], "react_app"),
    (["discord", "bot discord"], "discord_bot"),
    (["jeu", "game", "snake", "canvas"], "game"),
]


# ============================================================================
# JAVA TEMPLATES
# ============================================================================

JAVA_TEMPLATES = {}


def _java(name):
    def decorator(fn):
        JAVA_TEMPLATES[name] = fn
        return fn
    return decorator


@_java("fibonacci")
def _java_fibonacci(p):
    return '''\
public class Fibonacci {

    public static int[] fibonacci(int n) {
        if (n <= 0) return new int[0];
        if (n == 1) return new int[]{0};
        int[] suite = new int[n];
        suite[0] = 0;
        suite[1] = 1;
        for (int i = 2; i < n; i++) {
            suite[i] = suite[i - 1] + suite[i - 2];
        }
        return suite;
    }

    public static void main(String[] args) {
        int[] result = fibonacci(10);
        System.out.print("Fibonacci (10) : ");
        for (int v : result) System.out.print(v + " ");
        System.out.println();
    }
}
'''


@_java("spring_api")
def _java_spring(p):
    return '''\
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

@SpringBootApplication
@RestController
@RequestMapping("/api/items")
public class App {

    private final List<Map<String, Object>> items = new ArrayList<>(List.of(
        Map.of("id", 1, "nom", "Alpha", "actif", true),
        Map.of("id", 2, "nom", "Beta", "actif", false)
    ));
    private final AtomicLong counter = new AtomicLong(3);

    @GetMapping
    public Map<String, Object> lister() {
        return Map.of("items", items, "total", items.size());
    }

    @GetMapping("/{id}")
    public Map<String, Object> obtenir(@PathVariable long id) {
        return items.stream()
            .filter(i -> ((Number) i.get("id")).longValue() == id)
            .findFirst()
            .orElseThrow(() -> new RuntimeException("Introuvable"));
    }

    @PostMapping
    public Map<String, Object> creer(@RequestBody Map<String, Object> body) {
        Map<String, Object> item = new HashMap<>(body);
        item.put("id", counter.getAndIncrement());
        items.add(item);
        return item;
    }

    @DeleteMapping("/{id}")
    public Map<String, Boolean> supprimer(@PathVariable long id) {
        items.removeIf(i -> ((Number) i.get("id")).longValue() == id);
        return Map.of("ok", true);
    }

    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }
}
'''


@_java("default")
def _java_default(p):
    return '''\
public class Main {

    public static void main(String[] args) {
        System.out.println("YELMON Dev X - Code généré");
        System.out.println("Version : 1.0.0");
    }
}
'''


_JAVA_KEYWORD_MAP = [
    (["fibonacci"], "fibonacci"),
    (["spring", "api java", "rest"], "spring_api"),
]


# ============================================================================
# GO TEMPLATES
# ============================================================================

GO_TEMPLATES = {}


def _go(name):
    def decorator(fn):
        GO_TEMPLATES[name] = fn
        return fn
    return decorator


@_go("fibonacci")
def _go_fibonacci(p):
    return '''\
package main

import "fmt"

func fibonacci(n int) []int {
    if n <= 0 {
        return []int{}
    }
    if n == 1 {
        return []int{0}
    }
    suite := []int{0, 1}
    for i := 2; i < n; i++ {
        suite = append(suite, suite[i-1]+suite[i-2])
    }
    return suite
}

func main() {
    fmt.Println("Fibonacci (10) :", fibonacci(10))
}
'''


@_go("gin_api")
def _go_gin(p):
    return '''\
package main

import (
    "net/http"
    "strconv"
    "sync"

    "github.com/gin-gonic/gin"
)

type Item struct {
    ID    int    `json:"id"`
    Nom   string `json:"nom"`
    Actif bool   `json:"actif"`
}

var (
    items   = []Item{{ID: 1, Nom: "Alpha", Actif: true}, {ID: 2, Nom: "Beta", Actif: false}}
    nextID  = 3
    mu      sync.RWMutex
)

func main() {
    r := gin.Default()

    r.GET("/api/items", func(c *gin.Context) {
        mu.RLock()
        defer mu.RUnlock()
        c.JSON(http.StatusOK, gin.H{"items": items, "total": len(items)})
    })

    r.GET("/api/items/:id", func(c *gin.Context) {
        id, _ := strconv.Atoi(c.Param("id"))
        mu.RLock()
        defer mu.RUnlock()
        for _, item := range items {
            if item.ID == id {
                c.JSON(http.StatusOK, item)
                return
            }
        }
        c.JSON(http.StatusNotFound, gin.H{"error": "Introuvable"})
    })

    r.POST("/api/items", func(c *gin.Context) {
        var item Item
        if err := c.ShouldBindJSON(&item); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
            return
        }
        mu.Lock()
        item.ID = nextID
        nextID++
        items = append(items, item)
        mu.Unlock()
        c.JSON(http.StatusCreated, item)
    })

    r.DELETE("/api/items/:id", func(c *gin.Context) {
        id, _ := strconv.Atoi(c.Param("id"))
        mu.Lock()
        defer mu.Unlock()
        for i, item := range items {
            if item.ID == id {
                items = append(items[:i], items[i+1:]...)
                c.JSON(http.StatusOK, gin.H{"ok": true})
                return
            }
        }
        c.JSON(http.StatusNotFound, gin.H{"error": "Introuvable"})
    })

    r.Run(":5000")
}
'''


@_go("default")
def _go_default(p):
    return '''\
package main

import "fmt"

func main() {
    fmt.Println("YELMON Dev X - Code généré")
    fmt.Println("Version : 1.0.0")
}
'''


_GO_KEYWORD_MAP = [
    (["fibonacci"], "fibonacci"),
    (["gin", "api go", "golang"], "gin_api"),
]


# ============================================================================
# RUST TEMPLATES
# ============================================================================

RUST_TEMPLATES = {}


def _rust(name):
    def decorator(fn):
        RUST_TEMPLATES[name] = fn
        return fn
    return decorator


@_rust("fibonacci")
def _rust_fibonacci(p):
    return '''\
fn fibonacci(n: usize) -> Vec<u64> {
    if n == 0 { return vec![]; }
    if n == 1 { return vec![0]; }
    let mut suite = vec![0u64, 1];
    for _ in 2..n {
        let len = suite.len();
        suite.push(suite[len - 1] + suite[len - 2]);
    }
    suite
}

fn main() {
    println!("Fibonacci (10) : {:?}", fibonacci(10));
}
'''


@_rust("actix_api")
def _rust_actix(p):
    return '''\
use actix_web::{web, App, HttpServer, HttpResponse, middleware};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Serialize, Deserialize, Clone)]
struct Item {
    id: u64,
    nom: String,
    actif: bool,
}

struct AppState {
    items: Mutex<Vec<Item>>,
    next_id: Mutex<u64>,
}

async fn lister(data: web::Data<AppState>) -> HttpResponse {
    let items = data.items.lock().unwrap();
    HttpResponse::Ok().json(serde_json::json!({"items": *items, "total": items.len()}))
}

async fn obtenir(data: web::Data<AppState>, path: web::Path<u64>) -> HttpResponse {
    let items = data.items.lock().unwrap();
    match items.iter().find(|i| i.id == *path) {
        Some(item) => HttpResponse::Ok().json(item),
        None => HttpResponse::NotFound().json(serde_json::json!({"error": "Introuvable"})),
    }
}

async fn creer(data: web::Data<AppState>, body: web::Json<serde_json::Value>) -> HttpResponse {
    let nom = body.get("nom").and_then(|v| v.as_str()).unwrap_or("");
    if nom.is_empty() {
        return HttpResponse::BadRequest().json(serde_json::json!({"error": "nom requis"}));
    }
    let mut items = data.items.lock().unwrap();
    let mut next_id = data.next_id.lock().unwrap();
    let item = Item { id: *next_id, nom: nom.to_string(), actif: true };
    *next_id += 1;
    items.push(item.clone());
    HttpResponse::Created().json(item)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let data = web::Data::new(AppState {
        items: Mutex::new(vec![
            Item { id: 1, nom: "Alpha".into(), actif: true },
            Item { id: 2, nom: "Beta".into(), actif: false },
        ]),
        next_id: Mutex::new(3),
    });
    println!("Serveur sur http://localhost:5000");
    HttpServer::new(move || {
        App::new()
            .app_data(data.clone())
            .route("/api/items", web::get().to(lister))
            .route("/api/items/{id}", web::get().to(obtenir))
            .route("/api/items", web::post().to(creer))
    })
    .bind("127.0.0.1:5000")?
    .run()
    .await
}
'''


@_rust("default")
def _rust_default(p):
    return '''\
fn main() {
    println!("YELMON Dev X - Code généré");
    println!("Version : 1.0.0");
}
'''


_RUST_KEYWORD_MAP = [
    (["fibonacci"], "fibonacci"),
    (["actix", "api rust", "serveur rust"], "actix_api"),
]


# ============================================================================
# C++ TEMPLATES
# ============================================================================

CPP_TEMPLATES = {}


def _cpp(name):
    def decorator(fn):
        CPP_TEMPLATES[name] = fn
        return fn
    return decorator


@_cpp("fibonacci")
def _cpp_fibonacci(p):
    return '''\
#include <iostream>
#include <vector>

std::vector<long long> fibonacci(int n) {
    std::vector<long long> suite;
    if (n <= 0) return suite;
    if (n == 1) { suite.push_back(0); return suite; }
    suite = {0, 1};
    for (int i = 2; i < n; ++i) {
        suite.push_back(suite[i - 1] + suite[i - 2]);
    }
    return suite;
}

int main() {
    auto result = fibonacci(10);
    std::cout << "Fibonacci (10) : ";
    for (auto v : result) std::cout << v << " ";
    std::cout << std::endl;
    return 0;
}
'''


@_cpp("default")
def _cpp_default(p):
    return '''\
#include <iostream>

int main() {
    std::cout << "YELMON Dev X - Code généré" << std::endl;
    std::cout << "Version : 1.0.0" << std::endl;
    return 0;
}
'''


_CPP_KEYWORD_MAP = [
    (["fibonacci"], "fibonacci"),
]


# ============================================================================
# HTML/CSS TEMPLATES
# ============================================================================

HTML_TEMPLATES = {}


def _html(name):
    def decorator(fn):
        HTML_TEMPLATES[name] = fn
        return fn
    return decorator


@_html("landing_page")
def _html_landing(p):
    return '''\
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YELMON Landing Page</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f0f23; color: #e0e0e0; }
        nav { display: flex; justify-content: space-between; align-items: center; padding: 20px 40px; background: rgba(15,15,35,0.95); position: sticky; top: 0; z-index: 100; backdrop-filter: blur(10px); }
        nav .logo { font-size: 1.5rem; font-weight: 800; background: linear-gradient(135deg, #ff6b6b, #ffa500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        nav ul { list-style: none; display: flex; gap: 24px; }
        nav a { color: #aaa; text-decoration: none; transition: color 0.3s; }
        nav a:hover { color: #ff6b6b; }
        .hero { min-height: 80vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 60px 20px; background: radial-gradient(ellipse at 50% 0%, rgba(255,107,107,0.15) 0%, transparent 60%); }
        .hero h1 { font-size: 3.5rem; font-weight: 800; margin-bottom: 16px; background: linear-gradient(135deg, #ff6b6b, #ffa500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero p { font-size: 1.25rem; color: #888; max-width: 600px; margin-bottom: 32px; }
        .btn { display: inline-block; padding: 14px 32px; border-radius: 8px; font-size: 1rem; font-weight: 600; text-decoration: none; transition: transform 0.2s, box-shadow 0.2s; }
        .btn-primary { background: linear-gradient(135deg, #ff6b6b, #ffa500); color: #fff; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(255,107,107,0.3); }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; padding: 80px 40px; max-width: 1100px; margin: 0 auto; }
        .feature-card { background: #1a1a3e; border-radius: 16px; padding: 32px; border: 1px solid rgba(255,107,107,0.1); transition: transform 0.3s, border-color 0.3s; }
        .feature-card:hover { transform: translateY(-4px); border-color: rgba(255,107,107,0.3); }
        .feature-card h3 { font-size: 1.3rem; margin-bottom: 12px; color: #ff6b6b; }
        .feature-card p { color: #888; line-height: 1.6; }
        .cta { text-align: center; padding: 80px 20px; background: radial-gradient(ellipse at 50% 100%, rgba(255,165,0,0.1) 0%, transparent 60%); }
        .cta h2 { font-size: 2.5rem; margin-bottom: 16px; }
        .cta p { color: #888; margin-bottom: 32px; font-size: 1.1rem; }
        footer { text-align: center; padding: 40px; color: #555; font-size: 0.9rem; border-top: 1px solid #1a1a3e; }
        @media (max-width: 768px) { nav ul { display: none; } .hero h1 { font-size: 2rem; } .features { padding: 40px 20px; } }
    </style>
</head>
<body>
    <nav>
        <div class="logo">YELMON</div>
        <ul>
            <li><a href="#features">Fonctionnalités</a></li>
            <li><a href="#pricing">Tarifs</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>
    </nav>
    <section class="hero">
        <h1>Créez du code plus vite</h1>
        <p>YELMON Dev X transforme vos idées en code fonctionnel en quelques secondes. IA de dernière génération, multi-langages.</p>
        <a href="#features" class="btn btn-primary">Découvrir</a>
    </section>
    <section class="features" id="features">
        <div class="feature-card">
            <h3>Multi-langages</h3>
            <p>Python, JavaScript, Java, Go, Rust, C++, HTML/CSS — générez du code dans la langue de votre choix.</p>
        </div>
        <div class="feature-card">
            <h3>Exécution instantanée</h3>
            <p>Testez votre code directement dans l'éditeur. Résultats en temps réel, zéro configuration.</p>
        </div>
        <div class="feature-card">
            <h3>Intelligente</h3>
            <p>L'IA analyse votre demande, détecte le framework optimal et produit du code propre et fonctionnel.</p>
        </div>
    </section>
    <section class="cta" id="pricing">
        <h2>Prêt à coder ?</h2>
        <p>Rejoignez des milliers de développeurs qui font confiance à YELMON.</p>
        <a href="#" class="btn btn-primary">Commencer gratuitement</a>
    </section>
    <footer id="contact">
        <p>&copy; 2026 Yems junior lendola — All Rights Reserved.</p>
    </footer>
</body>
</html>
'''


@_html("portfolio")
def _html_portfolio(p):
    return '''\
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio — YELMON</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f0f23; color: #e0e0e0; }
        header { min-height: 60vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 60px 20px; }
        header h1 { font-size: 3rem; font-weight: 800; margin-bottom: 12px; background: linear-gradient(135deg, #ff6b6b, #ffa500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        header p { color: #888; font-size: 1.2rem; max-width: 500px; }
        .projects { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; padding: 40px; max-width: 1100px; margin: 0 auto; }
        .project { background: #1a1a3e; border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,107,107,0.1); transition: transform 0.3s; }
        .project:hover { transform: translateY(-4px); }
        .project-img { height: 180px; background: linear-gradient(135deg, #1a1a3e, #2a1a4e); display: flex; align-items: center; justify-content: center; font-size: 3rem; }
        .project-body { padding: 20px; }
        .project-body h3 { margin-bottom: 8px; color: #ff6b6b; }
        .project-body p { color: #888; font-size: 0.95rem; line-height: 1.5; margin-bottom: 12px; }
        .tag { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; background: rgba(255,107,107,0.15); color: #ff6b6b; margin-right: 6px; }
        .contact-section { text-align: center; padding: 60px 20px; }
        .contact-section h2 { font-size: 2rem; margin-bottom: 12px; }
        .contact-section p { color: #888; margin-bottom: 24px; }
        .contact-links { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }
        .contact-links a { padding: 12px 24px; border-radius: 8px; background: #1a1a3e; color: #ff6b6b; text-decoration: none; border: 1px solid rgba(255,107,107,0.2); transition: background 0.3s; }
        .contact-links a:hover { background: #2a1a4e; }
        footer { text-align: center; padding: 40px; color: #555; font-size: 0.9rem; }
        @media (max-width: 768px) { header h1 { font-size: 2rem; } .projects { padding: 20px; } }
    </style>
</head>
<body>
    <header>
        <h1>Mon Portfolio</h1>
        <p>Développeur passionné — Je crée des applications web modernes et performantes.</p>
    </header>
    <section class="projects">
        <div class="project">
            <div class="project-img">🚀</div>
            <div class="project-body">
                <h3>Projet Alpha</h3>
                <p>Application web fullstack avec authentification JWT et base de données temps réel.</p>
                <span class="tag">React</span><span class="tag">Node.js</span><span class="tag">MongoDB</span>
            </div>
        </div>
        <div class="project">
            <div class="project-img">📊</div>
            <div class="project-body">
                <h3>Dashboard Analytics</h3>
                <p>Tableau de bord interactif avec visualisation de données et export CSV.</p>
                <span class="tag">Python</span><span class="tag">Flask</span><span class="tag">Chart.js</span>
            </div>
        </div>
        <div class="project">
            <div class="project-img">🎮</div>
            <div class="project-body">
                <h3>Snake Game</h3>
                <p>Jeu classique Snake entièrement jouable dans le navigateur.</p>
                <span class="tag">HTML5</span><span class="tag">Canvas</span><span class="tag">JS</span>
            </div>
        </div>
    </section>
    <section class="contact-section">
        <h2>Me contacter</h2>
        <p>Disponible pour des projets freelance et collaborations.</p>
        <div class="contact-links">
            <a href="mailto:contact@example.com">Email</a>
            <a href="https://github.com" target="_blank">GitHub</a>
            <a href="https://linkedin.com" target="_blank">LinkedIn</a>
        </div>
    </section>
    <footer>&copy; 2026 Portfolio — YELMON Dev X</footer>
</body>
</html>
'''


@_html("contact_form")
def _html_contact_form(p):
    return '''\
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact — YELMON</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f0f23; color: #e0e0e0; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .form-container { width: 100%; max-width: 480px; background: #1a1a3e; border-radius: 16px; padding: 40px; border: 1px solid rgba(255,107,107,0.1); }
        h1 { font-size: 1.8rem; margin-bottom: 8px; background: linear-gradient(135deg, #ff6b6b, #ffa500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { color: #888; margin-bottom: 28px; }
        .field { margin-bottom: 20px; }
        .field label { display: block; font-size: 0.85rem; color: #aaa; margin-bottom: 6px; }
        .field input, .field textarea { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 8px; background: #0d0d2b; color: #fff; font-size: 14px; font-family: inherit; outline: none; transition: border-color 0.3s; }
        .field input:focus, .field textarea:focus { border-color: #ff6b6b; }
        .field textarea { resize: vertical; min-height: 120px; }
        .btn-submit { width: 100%; padding: 14px; border: none; border-radius: 8px; background: linear-gradient(135deg, #ff6b6b, #ffa500); color: #fff; font-size: 1rem; font-weight: 600; cursor: pointer; transition: opacity 0.3s; }
        .btn-submit:hover { opacity: 0.9; }
        .success { display: none; text-align: center; padding: 40px 20px; }
        .success h2 { color: #4CAF50; margin-bottom: 8px; }
        .success p { color: #888; }
        @media (max-width: 480px) { .form-container { padding: 24px; } }
    </style>
</head>
<body>
    <div class="form-container">
        <div id="formSection">
            <h1>Contactez-nous</h1>
            <p class="subtitle">Nous vous répondrons sous 24h.</p>
            <form id="contactForm" onsubmit="return handleSubmit(event)">
                <div class="field">
                    <label>Nom</label>
                    <input type="text" id="nom" placeholder="Votre nom" required>
                </div>
                <div class="field">
                    <label>Email</label>
                    <input type="email" id="email" placeholder="votre@email.com" required>
                </div>
                <div class="field">
                    <label>Message</label>
                    <textarea id="message" placeholder="Votre message..." required></textarea>
                </div>
                <button type="submit" class="btn-submit">Envoyer</button>
            </form>
        </div>
        <div class="success" id="successSection">
            <h2>Message envoyé !</h2>
            <p>Merci pour votre message. Nous vous répondrons bientôt.</p>
        </div>
    </div>
    <script>
        function handleSubmit(e) {
            e.preventDefault();
            document.getElementById("formSection").style.display = "none";
            document.getElementById("successSection").style.display = "block";
            return false;
        }
    </script>
</body>
</html>
'''


@_html("dashboard")
def _html_dashboard(p):
    return '''\
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard — YELMON</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f0f23; color: #e0e0e0; display: flex; min-height: 100vh; }
        .sidebar { width: 240px; background: #1a1a3e; padding: 24px 16px; border-right: 1px solid #2a2a4e; }
        .sidebar h2 { font-size: 1.2rem; margin-bottom: 32px; color: #ff6b6b; padding: 0 8px; }
        .sidebar a { display: block; padding: 10px 12px; color: #888; text-decoration: none; border-radius: 8px; margin-bottom: 4px; transition: background 0.2s, color 0.2s; }
        .sidebar a:hover, .sidebar a.active { background: rgba(255,107,107,0.1); color: #ff6b6b; }
        .main { flex: 1; padding: 32px; }
        .topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
        .topbar h1 { font-size: 1.5rem; }
        .topbar .user { color: #888; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 32px; }
        .stat-card { background: #1a1a3e; border-radius: 12px; padding: 24px; border: 1px solid rgba(255,107,107,0.08); }
        .stat-card .label { font-size: 0.85rem; color: #888; margin-bottom: 8px; }
        .stat-card .value { font-size: 2rem; font-weight: 700; color: #ff6b6b; }
        .table-card { background: #1a1a3e; border-radius: 12px; padding: 24px; border: 1px solid rgba(255,107,107,0.08); }
        .table-card h3 { margin-bottom: 16px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #2a2a4e; }
        th { color: #888; font-size: 0.85rem; text-transform: uppercase; }
        .badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; }
        .badge-active { background: rgba(76,175,80,0.15); color: #4CAF50; }
        .badge-inactive { background: rgba(255,80,80,0.15); color: #ff6b6b; }
        @media (max-width: 768px) { .sidebar { display: none; } .stats { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <aside class="sidebar">
        <h2>YELMON Admin</h2>
        <a href="#" class="active">Tableau de bord</a>
        <a href="#">Utilisateurs</a>
        <a href="#">Projets</a>
        <a href="#">Paramètres</a>
    </aside>
    <main class="main">
        <div class="topbar">
            <h1>Tableau de bord</h1>
            <span class="user">Admin</span>
        </div>
        <div class="stats">
            <div class="stat-card"><div class="label">Utilisateurs</div><div class="value">128</div></div>
            <div class="stat-card"><div class="label">Projets</div><div class="value">47</div></div>
            <div class="stat-card"><div class="label">Code généré</div><div class="value">1.2k</div></div>
            <div class="stat-card"><div class="label">Uptime</div><div class="value">99%</div></div>
        </div>
        <div class="table-card">
            <h3>Utilisateurs récents</h3>
            <table>
                <thead><tr><th>Nom</th><th>Email</th><th>Statut</th></tr></thead>
                <tbody>
                    <tr><td>Alice</td><td>alice@example.com</td><td><span class="badge badge-active">Actif</span></td></tr>
                    <tr><td>Bob</td><td>bob@example.com</td><td><span class="badge badge-active">Actif</span></td></tr>
                    <tr><td>Charlie</td><td>charlie@example.com</td><td><span class="badge badge-inactive">Inactif</span></td></tr>
                </tbody>
            </table>
        </div>
    </main>
</body>
</html>
'''


@_html("default")
def _html_default(p):
    return '''\
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page YELMON</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f0f23; color: #e0e0e0; display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 20px; }
        .card { background: #1a1a3e; border-radius: 16px; padding: 48px; text-align: center; max-width: 500px; width: 100%; border: 1px solid rgba(255,107,107,0.1); }
        h1 { font-size: 2rem; margin-bottom: 12px; background: linear-gradient(135deg, #ff6b6b, #ffa500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        p { color: #888; line-height: 1.6; }
        footer { margin-top: 32px; color: #555; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="card">
        <h1>YELMON Dev X</h1>
        <p>Page générée automatiquement. Modifiez ce fichier selon vos besoins.</p>
        <footer>&copy; 2026 Yems junior lendola — All Rights Reserved.</footer>
    </div>
</body>
</html>
'''


_HTML_KEYWORD_MAP = [
    (["landing", "page d'accueil", "page vitrine", "one page"], "landing_page"),
    (["portfolio", "cv", "profil", "about me"], "portfolio"),
    (["formulaire", "contact", "form", "email"], "contact_form"),
    (["dashboard", "tableau de bord", "admin", "panel"], "dashboard"),
]
