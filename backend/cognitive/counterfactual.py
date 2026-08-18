"""YELMON Dev X - Générateur de Contre-factuels.

Explore les chemins alternatifs : "et si on avait fait X au lieu de Y ?"
Génère des variations contraintes, simule les résultats, analyse les compromis.
"""

import re
import ast
import json
import time
import os
import uuid
from pathlib import Path
from typing import Optional
from collections import Counter


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


class Scenario:
    """Un scénario contre-factuel — une alternative possible."""

    def __init__(self, name: str, description: str, original: str,
                 alternative: str, constraints: list[str] = None,
                 predicted_impact: str = ""):
        self.id = uuid.uuid4().hex[:12]
        self.name = name
        self.description = description
        self.original = original
        self.alternative = alternative
        self.constraints = constraints or []
        self.predicted_impact = predicted_impact
        self.actual_impact: Optional[dict] = None
        self.tradeoffs: dict = {}
        self.score: float = 0.0
        self.created_at = time.time()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "original_snippet": self.original[:500],
            "alternative": self.alternative[:2000],
            "constraints": self.constraints,
            "predicted_impact": self.predicted_impact,
            "actual_impact": self.actual_impact,
            "tradeoffs": self.tradeoffs,
            "score": round(self.score, 3),
        }


class PathNode:
    """Nœud dans l'arbre de décision contre-factuel."""

    def __init__(self, decision: str, code: str, parent_id: str = None):
        self.id = uuid.uuid4().hex[:10]
        self.decision = decision
        self.code = code
        self.parent_id = parent_id
        self.children: list[str] = []
        self.depth: int = 0
        self.score: float = 0.0
        self.metadata: dict = {}


class WhatIfAnalyzer:
    """Analyseur de scénarios 'et si...?'."""

    def analyze_code_alternatives(self, code: str, language: str) -> list[Scenario]:
        """Génère des alternatives pour du code existant."""
        scenarios = []
        scenarios.extend(self._analyze_patterns(code, language))
        scenarios.extend(self._analyze_architecture(code, language))
        scenarios.extend(self._analyze_error_handling(code, language))
        return scenarios

    def analyze_decision_alternatives(self, decision: str, context: str,
                                      language: str) -> list[Scenario]:
        """Génère des alternatives pour une décision de conception."""
        scenarios = []
        decision_lower = decision.lower()
        if any(w in decision_lower for w in ["flask", "fastapi", "django"]):
            scenarios.extend(self._compare_web_frameworks(context, language))
        if any(w in decision_lower for w in ["sql", "database", "mongo", "sqlite"]):
            scenarios.extend(self._compare_databases(context, language))
        if any(w in decision_lower for w in ["class", "function", "oop", "functional"]):
            scenarios.extend(self._compare_paradigms(context, language))
        if any(w in decision_lower for w in ["async", "sync", "thread", "process"]):
            scenarios.extend(self._compare_concurrency(context, language))
        if any(w in decision_lower for w in ["cache", "redis", "memcache"]):
            scenarios.extend(self._compare_caching(context, language))
        if not scenarios:
            scenarios.extend(self._generic_alternatives(decision, context, language))
        return scenarios

    def _analyze_patterns(self, code: str, language: str) -> list[Scenario]:
        scenarios = []
        if language == "python":
            if re.search(r"for\s+\w+\s+in\s+range\(len\(", code):
                original = re.search(r"(for\s+\w+\s+in\s+range\(len\(\w+\)\).*)", code)
                if original:
                    scenarios.append(Scenario(
                        name="enumerate au lieu de range(len())",
                        description="Remplacer for i in range(len(x)) par for i, item in enumerate(x)",
                        original=original.group(1),
                        alternative="for i, item in enumerate(items):  # plus pythonique",
                        constraints=["pythonique", "lisible"],
                        predicted_impact="Meilleure lisibilité, accès direct aux éléments",
                    ))
            if re.search(r"==\s*(None|True|False)", code):
                scenarios.append(Scenario(
                    name="is au lieu de ==",
                    description="Utiliser 'is' pour les comparaisons singleton (None, True, False)",
                    original="if x == None:  # incorrect",
                    alternative="if x is None:  # correct (PEP 8)",
                    constraints=["pep8", "correct"],
                    predicted_impact="Conformité PEP 8, évite les bugs de comparaison",
                ))
            if re.search(r"except\s*:", code):
                scenarios.append(Scenario(
                    name="Exception explicite",
                    description="Remplacer bare except par except Exception:",
                    original="try:\n    risky()\nexcept:  # dangereux",
                    alternative="try:\n    risky()\nexcept Exception as e:  # sûr\n    logging.error(f'Error: {e}')",
                    constraints=["sécurisé", "debuggable"],
                    predicted_impact="Capture les erreurs sans casser le programme, logging possible",
                ))
            if "print(" in code and len(code.splitlines()) > 30:
                scenarios.append(Scenario(
                    name="Logging au lieu de print",
                    description="Remplacer print() par logging pour un code production",
                    original="print('Debug:', x)  # non contrôlable",
                    alternative="import logging\nlogger = logging.getLogger(__name__)\nlogger.info('Debug: %s', x)",
                    constraints=["production", "configurable"],
                    predicted_impact="Niveaux de log configurables, pas de sortie en production",
                ))
            if re.search(r"def\s+\w+\(.*=\s*\[\]", code):
                scenarios.append(Scenario(
                    name="Argument mutable corrigé",
                    description="Utiliser None comme défaut puis créer la liste dans la fonction",
                    original="def process(items=[]):  # BUG: mutable default",
                    alternative="def process(items=None):\n    items = items or []",
                    constraints=["correct", "sécurisé"],
                    predicted_impact="Évite le bug classique du mutable default argument",
                ))
        return scenarios

    def _analyze_architecture(self, code: str, language: str) -> list[Scenario]:
        scenarios = []
        lines = code.splitlines()
        func_count = len(re.findall(r"def\s+\w+", code))
        class_count = len(re.findall(r"class\s+\w+", code))
        if func_count > 5 and class_count == 0 and language == "python":
            scenarios.append(Scenario(
                name="Organisation en classes",
                description="Le code a beaucoup de fonctions mais pas de classes",
                original=f"{func_count} fonctions, {class_count} classes — tout est procedural",
                alternative="class Service:\n    def __init__(self):\n        self._cache = {}\n    def process(self, data): ...\n    def validate(self, item): ...",
                constraints=["structuré", "testable"],
                predicted_impact="Meilleure encapsulation, testabilité, réutilisabilité",
            ))
        if len(lines) > 50:
            long_funcs = self._find_long_functions(code, language)
            if long_funcs:
                scenarios.append(Scenario(
                    name="Décomposition en fonctions",
                    description="Fonctions trop longues → découper en sous-fonctions",
                    original=f"Fonctions longues: {', '.join(long_funcs)}",
                    alternative="# Découper chaque fonction > 30 lignes en sous-fonctions\ndef process(data):\n    validated = _validate(data)\n    transformed = _transform(validated)\n    return _save(transformed)",
                    constraints=["modulaire", "lisible"],
                    predicted_impact="Fonctions testables individuellement, code plus lisible",
                ))
        return scenarios

    def _analyze_error_handling(self, code: str, language: str) -> list[Scenario]:
        scenarios = []
        if language == "python":
            has_try = "try" in code
            has_file = "open(" in code
            has_request = "request" in code or "urllib" in code
            if (has_file or has_request) and not has_try:
                scenarios.append(Scenario(
                    name="Gestion d'erreurs ajoutée",
                    description="Le code fait des I/O sans try/except",
                    original="# Pas de gestion d'erreurs pour les opérations I/O",
                    alternative="try:\n    with open(f) as fh:\n        data = fh.read()\nexcept FileNotFoundError:\n    logger.warning('File not found')\n    data = ''",
                    constraints=["robuste", "production"],
                    predicted_impact="Le programme ne crash plus sur erreur I/O",
                ))
        return scenarios

    def _compare_web_frameworks(self, context: str, language: str) -> list[Scenario]:
        return [
            Scenario(
                name="Flask — Minimaliste",
                description="Flask: léger, flexible, pas d'opinion",
                original="Flask: choix actuel",
                alternative="from flask import Flask, jsonify\napp = Flask(__name__)\n# Simple, flexible, pas de structure imposée",
                constraints=["léger", "flexible"],
                predicted_impact="Départ rapide, moins de conventions, plus de liberté",
            ),
            Scenario(
                name="FastAPI — Moderne",
                description="FastAPI: auto-docs, validation Pydantic, async natif",
                original="Flask: pas de validation auto",
                alternative="from fastapi import FastAPI\nfrom pydantic import BaseModel\napp = FastAPI()\nclass Item(BaseModel):\n    name: str\n    price: float\n@app.post('/items')\nasync def create(item: Item): return item",
                constraints=["moderne", "type-safe", "auto-docs"],
                predicted_impact="Validation automatique, docs Swagger, 2-3x plus rapide",
            ),
            Scenario(
                name="Django — Full-stack",
                description="Django: ORM, admin, auth — tout inclus",
                original="Flask: tout à coder soi-même",
                alternative="# Django: tout inclus\nclass Item(models.Model):\n    name = models.CharField(max_length=100)\n    price = models.DecimalField()\n# + admin, auth, ORM, migrations",
                constraints=["complet", "batterie-incluse"],
                predicted_impact="Moins de code, plus de conventions, ORM puissant",
            ),
        ]

    def _compare_databases(self, context: str, language: str) -> list[Scenario]:
        return [
            Scenario(
                name="SQLite — Fichier local",
                description="SQLite: zéro config, fichier unique, idéal pour dev/test",
                original="Base de données: à choisir",
                alternative="import sqlite3\nconn = sqlite3.connect('data.db')\n# Zéro config, portable, fichier unique",
                constraints=["simple", "local", "zero-config"],
                predicted_impact="Pas de serveur, portable, idéal pour prototype",
            ),
            Scenario(
                name="PostgreSQL — Production",
                description="PostgreSQL: robuste, scalable, fonctionnalités avancées",
                alternative="import psycopg2\n# ou via SQLAlchemy\nengine = create_engine('postgresql://user:pass@localhost/db')\n# JSON, full-text search, extensions",
                constraints=["production", "scalable", "avancé"],
                predicted_impact="Performance, fiabilité, fonctionnalités enterprise",
            ),
            Scenario(
                name="MongoDB — NoSQL",
                description="MongoDB: flexible, schéma dynamique, bon pour JSON",
                alternative="from pymongo import MongoClient\nclient = MongoClient()\ndb = client.mydb\ncollection = db.items\ncollection.insert_one({'name': 'item', 'price': 9.99})",
                constraints=["flexible", "noSQL", "json-native"],
                predicted_impact="Schéma flexible, bon pour données hétérogènes",
            ),
        ]

    def _compare_paradigms(self, context: str, language: str) -> list[Scenario]:
        return [
            Scenario(
                name="Classes (OOP)",
                description="Encapsulation, héritage, polymorphisme",
                original="Paradigme: à choisir",
                alternative="class Service:\n    def __init__(self, db):\n        self.db = db\n    def process(self, data):\n        return self.db.save(data)",
                constraints=["structuré", "testable", "réutilisable"],
                predicted_impact="Meilleure encapsulation, testabilité, réutilisabilité via héritage",
            ),
            Scenario(
                name="Fonctions pures (Fonctionnel)",
                description="Pas d'état mutable, transparence référentielle",
                alternative="def process(data, db):\n    validated = validate(data)\n    saved = db.save(validated)\n    return saved",
                constraints=["simple", "prévisible", "testable"],
                predicted_impact="Plus facile à tester, pas d'effets de bord, parallélisable",
            ),
            Scenario(
                name="Dataclasses + fonctions",
                description="Données immutable + fonctions d'opération",
                alternative="from dataclasses import dataclass\n@dataclass(frozen=True)\nclass Item:\n    name: str\n    price: float\ndef create_item(name, price): return Item(name, price)",
                constraints=["moderne", "immutable", "type-safe"],
                predicted_impact="Données prévisibles, pattern moderne Python 3.7+",
            ),
        ]

    def _compare_concurrency(self, context: str, language: str) -> list[Scenario]:
        return [
            Scenario(
                name="Sync — Simple",
                description="Exécution séquentielle, plus simple à déboguer",
                original="Approche: synchronisation",
                alternative="def process_all(items):\n    return [process(item) for item in items]",
                constraints=["simple", "séquentiel"],
                predicted_impact="Code plus simple, plus facile à déboguer, moins d'erreurs",
            ),
            Scenario(
                name="Async — Concurrence I/O",
                description="asyncio pour opérations I/O non bloquantes",
                alternative="import asyncio\nasync def process_all(items):\n    return await asyncio.gather(*[process(item) for item in items])",
                constraints=["performant", "non-bloquant"],
                predicted_impact="2-10x plus rapide pour I/O (réseau, fichiers, DB)",
            ),
            Scenario(
                name="ThreadPool — Parallelisme CPU",
                description="ThreadPoolExecutor pour tâches CPU-bound",
                alternative="from concurrent.futures import ThreadPoolExecutor\ndef process_all(items):\n    with ThreadPoolExecutor() as pool:\n        return list(pool.map(process, items))",
                constraints=["parallèle", "multi-thread"],
                predicted_impact="Utilise tous les cœurs CPU, idéal pour calcul intensif",
            ),
        ]

    def _compare_caching(self, context: str, language: str) -> list[Scenario]:
        return [
            Scenario(
                name="Pas de cache",
                description="Requête directe à chaque fois",
                original="Pas de cache: requête directe",
                alternative="# Pas de cache: simple mais lent pour les requêtes répétées",
                constraints=["simple", "pas de dépendance"],
                predicted_impact="Toujours à jour, mais plus lent pour les accès répétés",
            ),
            Scenario(
                name="Cache en mémoire",
                description="Dict/simple TTL cache en mémoire",
                alternative="from functools import lru_cache\n@lru_cache(maxsize=128)\ndef get_item(item_id):\n    return db.query(item_id)",
                constraints=["rapide", "sans dépendance"],
                predicted_impact="10-100x plus rapide pour accès répétés, pas de dépendance externe",
            ),
            Scenario(
                name="Redis — Cache distribué",
                description="Redis pour cache partagé entre instances",
                alternative="import redis\nr = redis.Redis()\ndef get_item(item_id):\n    cached = r.get(f'item:{item_id}')\n    if cached: return json.loads(cached)\n    item = db.query(item_id)\n    r.setex(f'item:{item_id}', 300, json.dumps(item))\n    return item",
                constraints=["distribué", "scalable"],
                predicted_impact="Cache partagé, TTL configurable, persistance",
            ),
        ]

    def _generic_alternatives(self, decision: str, context: str,
                              language: str) -> list[Scenario]:
        return [
            Scenario(
                name="Approche simple",
                description=f"Solution minimale pour: {decision[:60]}",
                original=f"Décision: {decision[:100]}",
                alternative=f"# Solution simple et directe pour: {decision[:60]}\n# Pas de dépendances excessives, code minimal",
                constraints=["simple", "minimal"],
                predicted_impact="Moins de code à maintenir, déploiement plus rapide",
            ),
            Scenario(
                name="Approche robuste",
                description=f"Solution complète pour: {decision[:60]}",
                original=f"Décision: {decision[:100]}",
                alternative=f"# Solution complète avec gestion d'erreurs, logs, tests\n# Pour: {decision[:60]}",
                constraints=["robuste", "production"],
                predicted_impact="Plus de code mais plus fiable, testable, maintenable",
            ),
        ]

    def _find_long_functions(self, code: str, language: str) -> list[str]:
        long = []
        lines = code.splitlines()
        current_func = None
        start = 0
        for i, line in enumerate(lines):
            m = re.match(r"(?:def|function|fn)\s+(\w+)", line)
            if m:
                if current_func and i - start > 30:
                    long.append(f"{current_func}({i - start}l)")
                current_func = m.group(1)
                start = i
        if current_func and len(lines) - start > 30:
            long.append(f"{current_func}({len(lines) - start}l)")
        return long


class ConstraintVariator:
    """Génère des variations de code sous différentes contraintes."""

    CONSTRAINT_TRANSFORMS = {
        "no_classes": {
            "description": "Sans classes — tout en fonctions",
            "python": lambda code: re.sub(
                r"class\s+\w+.*?(?=\nclass|\Z)",
                "# [Classe convertie en fonctions]\n",
                code, flags=re.S
            ),
        },
        "no_imports": {
            "description": "Sans imports externes",
            "python": lambda code: re.sub(r"^(?:from\s+\S+\s+)?import\s+.+$", "# [Import supprimé]", code, flags=re.M),
        },
        "no_print": {
            "description": "Sans print — logging uniquement",
            "python": lambda code: re.sub(
                r"print\((.+?)\)",
                r"logging.info(\1)",
                code
            ),
        },
        "type_hints": {
            "description": "Avec type hints complets",
            "python": lambda code: code + "\n# TODO: Ajouter -> type aux fonctions\ndef add(a: int, b: int) -> int:\n    return a + b",
        },
        "async_version": {
            "description": "Version async/await",
            "python": lambda code: re.sub(
                r"def\s+(\w+)\(",
                r"async def \1(",
                code
            ),
        },
        "dataclass_style": {
            "description": "Style dataclass",
            "python": lambda code: code + "\nfrom dataclasses import dataclass\n@dataclass\nclass Config:\n    name: str = 'default'\n    debug: bool = False",
        },
        "minimal": {
            "description": "Version minimale — le strict nécessaire",
            "python": lambda code: "# Version minimale\n" + "\n".join(
                l for l in code.splitlines()
                if l.strip() and not l.strip().startswith("#")
            )[:500],
        },
        "production": {
            "description": "Version production — logs, erreurs, config",
            "python": lambda code: (
                "import logging\nimport os\nfrom pathlib import Path\n\n"
                "logging.basicConfig(level=logging.INFO)\nlogger = logging.getLogger(__name__)\n\n"
                + code
            ),
        },
    }

    def generate_variations(self, code: str, language: str,
                            constraints: list[str] = None) -> list[Scenario]:
        """Génère des variations sous contraintes."""
        scenarios = []
        if constraints:
            for constraint in constraints:
                if constraint in self.CONSTRAINT_TRANSFORMS:
                    transform = self.CONSTRAINT_TRANSFORMS[constraint]
                    try:
                        alt = transform["python"](code) if language == "python" else code
                        if alt.strip() != code.strip():
                            scenarios.append(Scenario(
                                name=f"Variation: {transform['description']}",
                                description=transform["description"],
                                original=code[:500],
                                alternative=alt,
                                constraints=[constraint],
                                predicted_impact=f"Code adapté pour contrainte: {constraint}",
                            ))
                    except Exception:
                        continue
        else:
            for name, transform in self.CONSTRAINT_TRANSFORMS.items():
                try:
                    alt = transform["python"](code) if language == "python" else code
                    if alt.strip() != code.strip():
                        scenarios.append(Scenario(
                            name=f"Variation: {transform['description']}",
                            description=transform["description"],
                            original=code[:500],
                            alternative=alt,
                            constraints=[name],
                            predicted_impact=f"Code adapté pour: {transform['description']}",
                        ))
                except Exception:
                    continue
        return scenarios


class OutcomeSimulator:
    """Simule les résultats de différentes approches."""

    def simulate_code_outcome(self, code: str, language: str) -> dict:
        """Simule le résultat d'exécution du code."""
        result = {
            "lines": len(code.splitlines()),
            "has_entry_point": bool(re.search(r"if\s+__name__.*__main__|\.run\(", code)),
            "has_error_handling": bool(re.search(r"try|except|catch", code)),
            "has_logging": bool(re.search(r"logging|logger|log\.", code)),
            "has_tests": bool(re.search(r"def test_|class Test|unittest|pytest", code)),
            "has_docs": bool(re.search(r'"""|\'>', code)),
            "has_types": bool(re.search(r"->|: str|: int|: float|: bool|: list", code)),
            "has_imports": bool(re.search(r"^import |^from ", code, re.M)),
            "complexity": self._estimate_complexity(code),
            "maintainability": self._estimate_maintainability(code, language),
            "estimated_bugs": self._estimate_bug_risk(code, language),
        }
        return result

    def simulate_comparison(self, code_a: str, code_b: str,
                            language: str) -> dict:
        """Compare les résultats simulés de deux versions."""
        sim_a = self.simulate_code_outcome(code_a, language)
        sim_b = self.simulate_code_outcome(code_b, language)
        comparison = {}
        for key in sim_a:
            val_a = sim_a[key]
            val_b = sim_b[key]
            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                diff = val_b - val_a
                pct = (diff / val_a * 100) if val_a else 0
                comparison[key] = {"a": val_a, "b": val_b, "diff": round(diff, 2),
                                   "pct_change": f"{pct:+.1f}%"}
            else:
                comparison[key] = {"a": val_a, "b": val_b,
                                   "winner": "a" if val_a and not val_b else "b" if val_b and not val_a else "equal"}
        return comparison

    def _estimate_complexity(self, code: str) -> int:
        complexity = 1
        for line in code.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            complexity += stripped.count(" if ") + stripped.count(" elif ")
            complexity += stripped.count(" for ") + stripped.count(" while ")
            complexity += stripped.count(" and ") + stripped.count(" or ")
            complexity += stripped.count(" try ")
        return complexity

    def _estimate_maintainability(self, code: str, language: str) -> str:
        score = 50
        lines = code.splitlines()
        if not lines:
            return "n/a"
        if language == "python":
            if '"""' in code or "'''" in code:
                score += 10
            if "->" in code:
                score += 8
            if "logging" in code:
                score += 5
            if "try" in code:
                score += 5
            if re.search(r"if __name__.*__main__", code):
                score += 3
        long_lines = sum(1 for l in lines if len(l) > 100)
        score -= long_lines * 2
        avg_len = sum(len(l) for l in lines) / len(lines)
        if avg_len < 60:
            score += 5
        if score >= 75:
            return "high"
        if score >= 50:
            return "medium"
        return "low"

    def _estimate_bug_risk(self, code: str, language: str) -> str:
        risks = 0
        if language == "python":
            if re.search(r"except\s*:", code):
                risks += 2
            if re.search(r"eval\(|exec\(", code):
                risks += 3
            if re.search(r"open\(.+['\"]w['\"]", code) and "with" not in code:
                risks += 1
            if re.search(r"==\s*(None|True|False)", code):
                risks += 1
            if re.search(r"def\s+\w+\(.*=\s*(\[|\{)", code):
                risks += 2
        if risks >= 4:
            return "high"
        if risks >= 2:
            return "medium"
        return "low"


class PathExplorer:
    """Explore les arbres de décision contre-factuels."""

    def __init__(self):
        self._trees: dict[str, list[PathNode]] = {}

    def build_tree(self, root_code: str, decisions: list[dict],
                   language: str) -> dict:
        """Construit un arbre de décision à partir de décisions alternatives."""
        tree_id = uuid.uuid4().hex[:10]
        root = PathNode("Code original", root_code)
        root.depth = 0
        root.score = 1.0
        nodes = {root.id: root}
        for decision in decisions:
            option_a = decision.get("option_a", "")
            option_b = decision.get("option_b", "")
            description = decision.get("description", "")
            if option_a:
                node_a = PathNode(f"{description} → {option_a}", root_code, root.id)
                node_a.depth = 1
                node_a.metadata = {"decision": description, "choice": option_a}
                nodes[node_a.id] = node_a
                root.children.append(node_a.id)
            if option_b:
                node_b = PathNode(f"{description} → {option_b}", root_code, root.id)
                node_b.depth = 1
                node_b.metadata = {"decision": description, "choice": option_b}
                nodes[node_b.id] = node_b
                root.children.append(node_b.id)
        self._trees[tree_id] = list(nodes.values())
        return {"tree_id": tree_id, "nodes": len(nodes), "root": root.id}

    def get_tree(self, tree_id: str) -> Optional[list[dict]]:
        nodes = self._trees.get(tree_id)
        if not nodes:
            return None
        return [n.__dict__ for n in nodes]

    def get_all_trees(self) -> list[dict]:
        return [{"tree_id": tid, "nodes": len(nodes)}
                for tid, nodes in self._trees.items()]


class TradeoffAnalyzer:
    """Analyse les compromis entre alternatives."""

    def analyze_tradeoffs(self, scenarios: list[Scenario]) -> list[dict]:
        """Analyse les compromis pour une liste de scénarios."""
        results = []
        for s in scenarios:
            tradeoffs = {
                "pros": [],
                "cons": [],
                "effort": "low",
                "risk": "low",
            }
            desc = s.description.lower()
            if "rapide" in desc or "simple" in desc or "léger" in desc:
                tradeoffs["pros"].append("Rapide à implémenter")
                tradeoffs["cons"].append("Peut manquer de fonctionnalités")
                tradeoffs["effort"] = "low"
            if "complet" in desc or "robuste" in desc or "production" in desc:
                tradeoffs["pros"].append("Couvre plus de cas")
                tradeoffs["cons"].append("Plus de code à maintenir")
                tradeoffs["effort"] = "high"
            if "async" in desc or "parallèle" in desc:
                tradeoffs["pros"].append("Meilleure performance I/O")
                tradeoffs["cons"].append("Plus complexe à déboguer")
                tradeoffs["effort"] = "medium"
                tradeoffs["risk"] = "medium"
            if "testable" in desc:
                tradeoffs["pros"].append("Facile à tester")
            if "flexible" in desc:
                tradeoffs["pros"].append("Adaptable au changement")
            if "structuré" in desc or "class" in desc:
                tradeoffs["pros"].append("Organisation claire")
                tradeoffs["cons"].append("Peut être over-engineering")
            if "cache" in desc:
                tradeoffs["pros"].append("Performance améliorée")
                tradeoffs["cons"].append("Incohérence possible (stale data)")
                tradeoffs["risk"] = "medium"
            if not tradeoffs["pros"]:
                tradeoffs["pros"].append("Amélioration potentielle")
            if not tradeoffs["cons"]:
                tradeoffs["cons"].append("Impact à évaluer")
            s.tradeoffs = tradeoffs
            score = 50
            score += len(tradeoffs["pros"]) * 10
            score -= len(tradeoffs["cons"]) * 5
            effort_penalty = {"low": 0, "medium": 5, "high": 15}
            score -= effort_penalty.get(tradeoffs["effort"], 0)
            risk_penalty = {"low": 0, "medium": 5, "high": 10}
            score -= risk_penalty.get(tradeoffs["risk"], 0)
            s.score = max(0, min(100, score)) / 100
            results.append({
                "scenario": s.to_dict(),
                "tradeoffs": tradeoffs,
                "score": s.score,
            })
        return sorted(results, key=lambda x: -x["score"])


class CounterfactualEngine:
    """Moteur principal de génération contre-factuelle.

    Pipeline: analyser → générer alternatives → simuler → explorer → décider.
    """

    def __init__(self):
        self.what_if = WhatIfAnalyzer()
        self.variator = ConstraintVariator()
        self.simulator = OutcomeSimulator()
        self.path_explorer = PathExplorer()
        self.tradeoff = TradeoffAnalyzer()
        self._history: list[dict] = []

    def analyze_code(self, code: str, language: str) -> dict:
        """Analyse complète du code avec alternatives contre-factuelles."""
        run_id = uuid.uuid4().hex[:10]
        scenarios = self.what_if.analyze_code_alternatives(code, language)
        variations = self.variator.generate_variations(code, language)
        all_scenarios = scenarios + variations
        simulation = self.simulator.simulate_code_outcome(code, language)
        if all_scenarios:
            tradeoffs = self.tradeoff.analyze_tradeoffs(all_scenarios)
        else:
            tradeoffs = []
        result = {
            "run_id": run_id,
            "type": "code_analysis",
            "original_simulation": simulation,
            "alternatives_count": len(all_scenarios),
            "scenarios": [s.to_dict() for s in all_scenarios],
            "tradeoffs": tradeoffs,
            "best_alternative": tradeoffs[0] if tradeoffs else None,
        }
        self._history.append({
            "run_id": run_id,
            "type": "code_analysis",
            "timestamp": time.time(),
            "alternatives": len(all_scenarios),
        })
        return result

    def analyze_decision(self, decision: str, context: str,
                         language: str) -> dict:
        """Analyse une décision avec alternatives."""
        run_id = uuid.uuid4().hex[:10]
        scenarios = self.what_if.analyze_decision_alternatives(
            decision, context, language
        )
        if scenarios:
            tradeoffs = self.tradeoff.analyze_tradeoffs(scenarios)
        else:
            tradeoffs = []
        comparisons = []
        for i in range(len(scenarios)):
            for j in range(i + 1, len(scenarios)):
                sim_a = self.simulator.simulate_code_outcome(
                    scenarios[i].alternative, language
                )
                sim_b = self.simulator.simulate_code_outcome(
                    scenarios[j].alternative, language
                )
                comparisons.append({
                    "a": scenarios[i].name,
                    "b": scenarios[j].name,
                    "comparison": self.simulator.simulate_comparison(
                        scenarios[i].alternative, scenarios[j].alternative, language
                    ),
                })
        result = {
            "run_id": run_id,
            "type": "decision_analysis",
            "decision": decision,
            "alternatives_count": len(scenarios),
            "scenarios": [s.to_dict() for s in scenarios],
            "tradeoffs": tradeoffs,
            "comparisons": comparisons[:10],
            "best_alternative": tradeoffs[0] if tradeoffs else None,
        }
        self._history.append({
            "run_id": run_id,
            "type": "decision_analysis",
            "timestamp": time.time(),
            "alternatives": len(scenarios),
        })
        return result

    def explore_paths(self, code: str, decisions: list[dict],
                      language: str) -> dict:
        """Construit et explore un arbre de décision."""
        tree = self.path_explorer.build_tree(code, decisions, language)
        tree_nodes = self.path_explorer.get_tree(tree["tree_id"])
        simulations = {}
        if tree_nodes:
            for node in tree_nodes:
                if node.get("depth", 0) > 0:
                    sim = self.simulator.simulate_code_outcome(
                        node.get("code", ""), language
                    )
                    simulations[node["id"]] = sim
        return {
            "tree": tree,
            "nodes": tree_nodes or [],
            "simulations": simulations,
            "all_trees": self.path_explorer.get_all_trees(),
        }

    def get_stats(self) -> dict:
        total = len(self._history)
        code_analyses = sum(1 for h in self._history if h["type"] == "code_analysis")
        decision_analyses = sum(1 for h in self._history if h["type"] == "decision_analysis")
        total_alternatives = sum(h["alternatives"] for h in self._history)
        return {
            "total_runs": total,
            "code_analyses": code_analyses,
            "decision_analyses": decision_analyses,
            "total_alternatives_generated": total_alternatives,
        }

    def get_history(self) -> list[dict]:
        return list(self._history)


counterfactual_engine = CounterfactualEngine()
