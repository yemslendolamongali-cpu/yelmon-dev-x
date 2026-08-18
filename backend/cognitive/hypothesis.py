"""YELMON Dev X - Moteur d'exécution d'hypothèses.

Génère, teste, évalue et itère sur des hypothèses de code
pour trouver la meilleure solution possible.
"""

import re
import ast
import json
import time
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Optional
from collections import Counter


class Hypothesis:
    """Une hypothèse de solution."""

    def __init__(self, content: str, strategy: str, description: str = ""):
        self.id = uuid.uuid4().hex[:12]
        self.content = content
        self.strategy = strategy
        self.description = description
        self.scores: dict[str, float] = {}
        self.execution_result: Optional[dict] = None
        self.syntax_valid = False
        self.test_passed = False
        self.iteration = 0
        self.created_at = time.time()

    @property
    def total_score(self) -> float:
        if not self.scores:
            return 0.0
        weights = {
            "syntax": 0.25,
            "execution": 0.25,
            "quality": 0.20,
            "complexity": 0.15,
            "style": 0.10,
            "correctness": 0.05,
        }
        total = 0.0
        for key, weight in weights.items():
            total += self.scores.get(key, 0.0) * weight
        return round(total, 3)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content[:2000],
            "strategy": self.strategy,
            "description": self.description,
            "scores": self.scores,
            "total_score": self.total_score,
            "syntax_valid": self.syntax_valid,
            "test_passed": self.test_passed,
            "iteration": self.iteration,
            "execution": self.execution_result,
        }


class HypothesisGenerator:
    """Génère des hypothèses de solution multiples."""

    def generate_fix_hypotheses(self, code: str, errors: list[dict],
                                language: str) -> list[Hypothesis]:
        """Génère des hypothèses de correction pour des erreurs détectées."""
        hypotheses = []
        strategies = {
            "syntax_repair": self._strategy_syntax_repair,
            "pattern_substitution": self._strategy_pattern_substitution,
            "structural_refactor": self._strategy_structural_refactor,
            "alternative_approach": self._strategy_alternative,
            "minimal_fix": self._strategy_minimal_fix,
        }
        for name, strategy_fn in strategies.items():
            try:
                generated = strategy_fn(code, errors, language)
                if generated and generated.strip() != code.strip():
                    hypotheses.append(Hypothesis(
                        content=generated,
                        strategy=name,
                        description=self._describe_strategy(name, errors),
                    ))
            except Exception:
                continue
        return hypotheses

    def generate_solution_hypotheses(self, prompt: str, language: str,
                                     context: dict = None) -> list[Hypothesis]:
        """Génère des hypothèses de solutions pour un prompt utilisateur."""
        hypotheses = []
        approaches = {
            "direct": self._solution_direct,
            "modular": self._solution_modular,
            "minimal": self._solution_minimal,
            "comprehensive": self._solution_comprehensive,
        }
        for name, fn in approaches.items():
            try:
                content = fn(prompt, language, context or {})
                if content:
                    hypotheses.append(Hypothesis(
                        content=content,
                        strategy=name,
                        description=f"Approche {name} pour: {prompt[:80]}",
                    ))
            except Exception:
                continue
        return hypotheses

    def generate_optimization_hypotheses(self, code: str,
                                         language: str) -> list[Hypothesis]:
        """Génère des hypothèses d'optimisation."""
        hypotheses = []
        strategies = {
            "performance": self._optimize_performance,
            "readability": self._optimize_readability,
            "memory": self._optimize_memory,
        }
        for name, fn in strategies.items():
            try:
                content = fn(code, language)
                if content and content.strip() != code.strip():
                    hypotheses.append(Hypothesis(
                        content=content,
                        strategy=f"optimize_{name}",
                        description=f"Optimisation {name}",
                    ))
            except Exception:
                continue
        return hypotheses

    def _strategy_syntax_repair(self, code: str, errors: list[dict],
                                language: str) -> str:
        fixed = code
        for err in errors:
            msg = err.get("msg", "").lower()
            line = err.get("line", 0)
            lines = fixed.splitlines()
            if "indentation" in msg or "indent" in msg:
                fixed = self._fix_indentation(fixed, language)
            elif "unexpected eof" in msg or "eof" in msg:
                fixed = self._fix_missing_closing(fixed, language)
            elif "syntaxerror" in msg or "syntax" in msg:
                if 0 < line <= len(lines):
                    lines[line - 1] = self._repair_line(lines[line - 1], language)
                    fixed = "\n".join(lines)
            elif "name" in msg and "not defined" in msg:
                var_name = re.search(r"'(\w+)'", err.get("msg", ""))
                if var_name:
                    fixed = self._add_variable_init(fixed, var_name.group(1))
        return fixed

    def _strategy_pattern_substitution(self, code: str, errors: list[dict],
                                       language: str) -> str:
        subs = [
            (r"print\s*\(", "logging.info(" if language == "python" else "console.log("),
            (r"except\s*:", "except Exception:" if language == "python" else "catch(e)"),
            (r"==\s*None", "is None"),
            (r"==\s*True", "is True"),
            (r"==\s*False", "is False"),
            (r"\bvar\b", "const"),
            (r"except\s+(\w+):\s*pass", r"except \1:\n    logging.error(f'Error: {\1}')"),
        ]
        fixed = code
        for pattern, replacement in subs:
            if language == "python" and replacement == "console.log(":
                continue
            if language in ("javascript", "typescript") and replacement == "logging.info(":
                continue
            fixed = re.sub(pattern, replacement, fixed)
        return fixed

    def _strategy_structural_refactor(self, code: str, errors: list[dict],
                                      language: str) -> str:
        lines = code.splitlines()
        result = []
        in_function = False
        func_lines = []
        for line in lines:
            stripped = line.strip()
            if language == "python" and re.match(r"def\s+\w+", stripped):
                if in_function and func_lines:
                    if not any(l.strip().startswith('"""') or l.strip().startswith("'''")
                               for l in func_lines):
                        func_lines.insert(1, '    """TODO: Add docstring."""')
                result.extend(func_lines)
                func_lines = [line]
                in_function = True
            elif in_function:
                func_lines.append(line)
            else:
                result.append(line)
        if in_function and func_lines:
            if not any(l.strip().startswith('"""') or l.strip().startswith("'''")
                       for l in func_lines):
                func_lines.insert(1, '    """TODO: Add docstring."""')
            result.extend(func_lines)
        return "\n".join(result)

    def _strategy_alternative(self, code: str, errors: list[dict],
                              language: str) -> str:
        lines = code.splitlines()
        result = []
        for line in lines:
            stripped = line.strip()
            if language == "python":
                if re.match(r"for\s+\w+\s+in\s+range\(len\(", stripped):
                    var = re.search(r"for\s+(\w+)\s+in\s+range\(len\((\w+)\)", stripped)
                    if var:
                        indent = line[:len(line) - len(line.lstrip())]
                        result.append(f"{indent}for i, item in enumerate({var.group(2)}):")
                        continue
                if "open(" in stripped and "with" not in stripped:
                    file_arg = re.search(r"open\(([^)]+)\)", stripped)
                    if file_arg:
                        indent = line[:len(line) - len(line.lstrip())]
                        result.append(f"{indent}with open({file_arg.group(1)}) as f:")
                        result.append(f"{indent}    # TODO: adjust body indentation")
                        continue
            result.append(line)
        return "\n".join(result)

    def _strategy_minimal_fix(self, code: str, errors: list[dict],
                              language: str) -> str:
        fixed = code
        for err in errors:
            line_num = err.get("line", 0)
            msg = err.get("msg", "").lower()
            lines = fixed.splitlines()
            if 0 < line_num <= len(lines):
                idx = line_num - 1
                line = lines[idx]
                if "missing ':'" in msg or "expected ':'" in msg:
                    if not line.rstrip().endswith(":"):
                        lines[idx] = line.rstrip() + ":"
                elif "missing ')'" in msg or "unexpected eof" in msg:
                    opens = line.count("(") - line.count(")")
                    if opens > 0:
                        lines[idx] = line + ")" * opens
                elif "missing ';'" in msg and language in ("java", "cpp"):
                    if not line.rstrip().endswith(";"):
                        lines[idx] = line.rstrip() + ";"
                fixed = "\n".join(lines)
        return fixed

    def _solution_direct(self, prompt: str, language: str, ctx: dict) -> str:
        if language == "python":
            return self._gen_python_direct(prompt)
        elif language in ("javascript", "typescript"):
            return self._gen_js_direct(prompt)
        return f"# Solution directe pour: {prompt}\n# TODO: implémenter"

    def _solution_modular(self, prompt: str, language: str, ctx: dict) -> str:
        if language == "python":
            return self._gen_python_modular(prompt)
        return self._gen_python_direct(prompt)

    def _solution_minimal(self, prompt: str, language: str, ctx: dict) -> str:
        if language == "python":
            return self._gen_python_minimal(prompt)
        return self._gen_python_direct(prompt)

    def _solution_comprehensive(self, prompt: str, language: str, ctx: dict) -> str:
        if language == "python":
            return self._gen_python_comprehensive(prompt)
        return self._gen_python_direct(prompt)

    def _gen_python_direct(self, prompt: str) -> str:
        p = prompt.lower()
        if any(w in p for w in ["api", "rest", "flask", "endpoint"]):
            return (
                "from flask import Flask, jsonify, request\n\n"
                "app = Flask(__name__)\n"
                "items = []\n\n"
                "@app.route('/api/items', methods=['GET'])\n"
                "def get_items():\n"
                "    return jsonify(items)\n\n"
                "@app.route('/api/items', methods=['POST'])\n"
                "def create_item():\n"
                "    data = request.get_json()\n"
                "    items.append(data)\n"
                "    return jsonify(data), 201\n\n"
                "if __name__ == '__main__':\n"
                "    app.run(debug=True)\n"
            )
        if any(w in p for w in ["class", "classe", "oop"]):
            return (
                "class Handler:\n"
                '    """Classe principale."""\n\n'
                "    def __init__(self, name: str):\n"
                "        self.name = name\n"
                "        self.data = []\n\n"
                "    def process(self, item):\n"
                '        """Traite un élément."""\n'
                "        self.data.append(item)\n"
                "        return item\n\n"
                "    def get_all(self):\n"
                "        return list(self.data)\n"
            )
        return f"# Solution directe\n# {prompt}\n\ndef main():\n    pass\n\nif __name__ == '__main__':\n    main()\n"

    def _gen_python_modular(self, prompt: str) -> str:
        return (
            "from dataclasses import dataclass, field\nfrom typing import List, Optional\n\n"
            "@dataclass\n"
            "class Config:\n"
            "    name: str = 'default'\n"
            "    debug: bool = False\n\n"
            "@dataclass\n"
            "class Processor:\n"
            "    config: Config = field(default_factory=Config)\n"
            "    results: List = field(default_factory=list)\n\n"
            "    def run(self, data):\n"
            "        result = self._transform(data)\n"
            "        self.results.append(result)\n"
            "        return result\n\n"
            "    def _transform(self, data):\n"
            "        return data\n\n"
            "def create_processor(debug=False):\n"
            "    config = Config(debug=debug)\n"
            "    return Processor(config=config)\n"
        )

    def _gen_python_minimal(self, prompt: str) -> str:
        return (
            "def solve(data):\n"
            "    return data\n\n"
            "if __name__ == '__main__':\n"
            "    print(solve(None))\n"
        )

    def _gen_python_comprehensive(self, prompt: str) -> str:
        return (
            "import logging\nfrom typing import Any, Optional\nfrom dataclasses import dataclass\n\n"
            "logging.basicConfig(level=logging.INFO)\n"
            "logger = logging.getLogger(__name__)\n\n"
            "@dataclass\n"
            "class Result:\n"
            "    success: bool\n"
            "    data: Any = None\n"
            "    error: Optional[str] = None\n\n"
            "class Engine:\n"
            '    """Moteur de traitement principal."""\n\n'
            "    def __init__(self):\n"
            "        self._initialized = True\n"
            "        logger.info('Engine initialized')\n\n"
            "    def execute(self, task) -> Result:\n"
            "        try:\n"
            "            result = self._process(task)\n"
            "            return Result(success=True, data=result)\n"
            "        except Exception as e:\n"
            "            logger.error(f'Error: {e}')\n"
            "            return Result(success=False, error=str(e))\n\n"
            "    def _process(self, task):\n"
            "        return task\n"
        )

    def _optimize_performance(self, code: str, language: str) -> str:
        optimized = code
        if language == "python":
            optimized = re.sub(
                r"for\s+(\w+)\s+in\s+range\(len\((\w+)\)\)",
                r"for \1, item in enumerate(\2)",
                optimized,
            )
            if "+" in optimized and re.search(r'"\s*\+\s*\w+\s*\+\s*"', optimized):
                optimized = re.sub(
                    r'"([^"]*)"\s*\+\s*(\w+)\s*\+\s*"([^"]*)"',
                    r'f"\1{\2}\3"',
                    optimized,
                )
        return optimized

    def _optimize_readability(self, code: str, language: str) -> str:
        lines = code.splitlines()
        result = []
        for line in lines:
            if len(line) > 100 and "=" in line:
                parts = line.split("=", 1)
                if len(parts) == 2:
                    indent = line[:len(line) - len(line.lstrip())]
                    result.append(f"{indent}{parts[0].strip()} = (")
                    result.append(f"{indent}    {parts[1].strip()}")
                    result.append(f"{indent})")
                    continue
            result.append(line)
        return "\n".join(result)

    def _optimize_memory(self, code: str, language: str) -> str:
        optimized = code
        if language == "python":
            optimized = re.sub(
                r"(\w+)\s*=\s*\[(.+?)\]\s*\n\s*for\s+(\w+)\s+in\s+\1",
                r"for \3 in [{safe} for safe in [{safe2}]]".replace("{safe2}", "\\2"),
                optimized,
            )
        return optimized

    def _fix_indentation(self, code: str, language: str) -> str:
        lines = code.splitlines()
        result = []
        prev_indent = 0
        for line in lines:
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            if indent > prev_indent + 4 and prev_indent > 0:
                indent = prev_indent + 4
            result.append(" " * indent + stripped)
            if stripped:
                prev_indent = indent
        return "\n".join(result)

    def _fix_missing_closing(self, code: str, language: str) -> str:
        opens = code.count("(") - code.count(")")
        if opens > 0:
            code += "\n" + ")" * opens
        brackets = code.count("[") - code.count("]")
        if brackets > 0:
            code += "\n" + "]" * brackets
        braces = code.count("{") - code.count("}")
        if braces > 0:
            code += "\n" + "}" * braces
        return code

    def _repair_line(self, line: str, language: str) -> str:
        stripped = line.strip()
        if language == "python":
            if stripped.startswith("def ") and not stripped.endswith(":"):
                return line.rstrip() + ":"
            if stripped.startswith("class ") and not stripped.endswith(":"):
                return line.rstrip() + ":"
            if stripped.startswith("if ") and not stripped.endswith(":"):
                return line.rstrip() + ":"
            if stripped.startswith("else") and not stripped.endswith(":"):
                return line.rstrip() + ":"
            if stripped.startswith("elif ") and not stripped.endswith(":"):
                return line.rstrip() + ":"
            if stripped.startswith("for ") and not stripped.endswith(":"):
                return line.rstrip() + ":"
            if stripped.startswith("while ") and not stripped.endswith(":"):
                return line.rstrip() + ":"
            if stripped.startswith("try") and not stripped.endswith(":"):
                return line.rstrip() + ":"
        return line

    def _add_variable_init(self, code: str, var_name: str) -> str:
        lines = code.splitlines()
        for i, line in enumerate(lines):
            if var_name in line and "=" not in line.split(var_name)[0]:
                indent = line[:len(line) - len(line.lstrip())]
                lines.insert(i, f"{indent}{var_name} = None")
                break
        return "\n".join(lines)

    def _describe_strategy(self, name: str, errors: list[dict]) -> str:
        descriptions = {
            "syntax_repair": "Réparation directe des erreurs de syntaxe",
            "pattern_substitution": "Substitution de patterns problématiques",
            "structural_refactor": "Refactoring structurel du code",
            "alternative_approach": "Approche alternative avec patterns modernes",
            "minimal_fix": "Correction minimale ciblée",
        }
        return descriptions.get(name, f"Stratégie: {name}")


class HypothesisTester:
    """Teste les hypothèses en sandbox."""

    def test_syntax(self, hypothesis: Hypothesis, language: str) -> Hypothesis:
        """Vérifie la validité syntaxique."""
        code = hypothesis.content
        valid = False
        error_msg = ""
        if language == "python":
            try:
                ast.parse(code)
                valid = True
            except SyntaxError as e:
                error_msg = f"SyntaxError at line {e.lineno}: {e.msg}"
        elif language in ("javascript", "typescript"):
            result = self._run_js_check(code)
            valid = result.get("success", False)
            error_msg = result.get("error", "")
        elif language == "html":
            valid = "<html" in code.lower() or "<div" in code.lower()
            error_msg = "" if valid else "No HTML tags found"
        else:
            valid = bool(code.strip())
        hypothesis.syntax_valid = valid
        hypothesis.scores["syntax"] = 1.0 if valid else 0.0
        if not valid:
            hypothesis.execution_result = {"error": error_msg, "success": False}
        return hypothesis

    def test_execution(self, hypothesis: Hypothesis, language: str,
                       timeout: int = 8) -> Hypothesis:
        """Exécute le code en sandbox et vérifie la sortie."""
        if language != "python":
            hypothesis.test_passed = hypothesis.syntax_valid
            hypothesis.scores["execution"] = 1.0 if hypothesis.test_passed else 0.5
            return hypothesis
        code = hypothesis.content
        if not hypothesis.syntax_valid:
            hypothesis.test_passed = False
            hypothesis.scores["execution"] = 0.0
            return hypothesis
        try:
            with tempfile.TemporaryDirectory(prefix="hyp_test_") as tmp:
                script = Path(tmp) / "test.py"
                safe_code = self._make_safe(code)
                script.write_text(safe_code, encoding="utf-8")
                proc = subprocess.run(
                    [sys.executable, str(script)],
                    capture_output=True, text=True,
                    timeout=timeout, cwd=tmp,
                )
                hypothesis.execution_result = {
                    "stdout": (proc.stdout or "")[:1000],
                    "stderr": (proc.stderr or "")[:1000],
                    "returncode": proc.returncode,
                    "success": proc.returncode == 0,
                }
                hypothesis.test_passed = proc.returncode == 0
                if proc.returncode == 0:
                    hypothesis.scores["execution"] = 1.0
                elif proc.returncode == 0 and proc.stderr:
                    hypothesis.scores["execution"] = 0.5
                else:
                    hypothesis.scores["execution"] = 0.1
        except subprocess.TimeoutExpired:
            hypothesis.execution_result = {"error": "Timeout", "success": False}
            hypothesis.test_passed = False
            hypothesis.scores["execution"] = 0.2
        except Exception as e:
            hypothesis.execution_result = {"error": str(e), "success": False}
            hypothesis.test_passed = False
            hypothesis.scores["execution"] = 0.0
        return hypothesis

    def test_quality(self, hypothesis: Hypothesis, language: str) -> Hypothesis:
        """Évalue la qualité du code généré."""
        code = hypothesis.content
        score = 50.0
        lines = code.splitlines()
        if not lines:
            hypothesis.scores["quality"] = 0.0
            return hypothesis
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]
        blank_ratio = 1 - (len(code_lines) / len(lines)) if lines else 0
        if 0.1 < blank_ratio < 0.4:
            score += 5
        if language == "python":
            if '"""' in code or "'''" in code:
                score += 10
            if "->" in code or ": str" in code or ": int" in code:
                score += 8
            if "logging" in code:
                score += 5
            if "try" in code and "except" in code:
                score += 5
            if "class " in code:
                score += 3
            if "def " in code:
                score += 5
            if re.search(r"if __name__.*__main__", code):
                score += 3
            if "import" in code:
                score += 2
            if "if " in code or "for " in code:
                score += 2
        avg_line_len = sum(len(l) for l in lines) / len(lines)
        if avg_line_len < 60:
            score += 5
        elif avg_line_len > 100:
            score -= 5
        if len(code_lines) > 5 and len(code_lines) < 200:
            score += 5
        hypothesis.scores["quality"] = max(0, min(100, score)) / 100
        return hypothesis

    def test_complexity(self, hypothesis: Hypothesis, language: str) -> Hypothesis:
        """Évalue la complexité cyclomatique."""
        code = hypothesis.content
        complexity = 1
        for line in code.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            complexity += stripped.count(" if ") + stripped.count(" elif ")
            complexity += stripped.count(" and ") + stripped.count(" or ")
            complexity += stripped.count(" for ") + stripped.count(" while ")
            complexity += stripped.count(" try ") + stripped.count(" except ")
        if complexity <= 5:
            score = 1.0
        elif complexity <= 10:
            score = 0.8
        elif complexity <= 20:
            score = 0.5
        else:
            score = 0.2
        hypothesis.scores["complexity"] = score
        return hypothesis

    def test_style(self, hypothesis: Hypothesis, language: str) -> Hypothesis:
        """Évalue le style du code."""
        code = hypothesis.content
        score = 50.0
        lines = code.splitlines()
        if not lines:
            hypothesis.scores["style"] = 0.0
            return hypothesis
        long_lines = sum(1 for l in lines if len(l) > 100)
        if long_lines == 0:
            score += 15
        elif long_lines < 3:
            score += 5
        else:
            score -= 10
        if language == "python":
            trailing_whitespace = sum(1 for l in lines if l != l.rstrip())
            if trailing_whitespace == 0:
                score += 10
            has_consistent_indent = not any(
                l.startswith("\t") for l in lines if l.strip()
            )
            if has_consistent_indent:
                score += 10
            lines_with_space_around_eq = sum(
                1 for l in lines
                if "=" in l and "==" not in l and "!=" not in l
                and "<=" not in l and ">=" not in l
                and " =" in l and "= " in l
            )
            if lines_with_space_around_eq > 0:
                score += 5
        max_consecutive_blank = 0
        current_blank = 0
        for l in lines:
            if not l.strip():
                current_blank += 1
                max_consecutive_blank = max(max_consecutive_blank, current_blank)
            else:
                current_blank = 0
        if max_consecutive_blank <= 2:
            score += 5
        elif max_consecutive_blank > 4:
            score -= 5
        hypothesis.scores["style"] = max(0, min(100, score)) / 100
        return hypothesis

    def test_correctness(self, hypothesis: Hypothesis, language: str,
                         test_cases: list[dict] = None) -> Hypothesis:
        """Teste la correction avec des cas de test fournis."""
        if not test_cases or language != "python":
            hypothesis.scores["correctness"] = 0.5
            return hypothesis
        passed = 0
        total = len(test_cases)
        for case in test_cases:
            try:
                result = self._run_with_input(hypothesis.content, case.get("input", ""))
                expected = case.get("expected", "")
                if expected and expected.strip() in (result or "").strip():
                    passed += 1
            except Exception:
                pass
        hypothesis.scores["correctness"] = passed / total if total > 0 else 0.5
        return hypothesis

    def run_all_tests(self, hypothesis: Hypothesis, language: str,
                      test_cases: list[dict] = None) -> Hypothesis:
        """Lance tous les tests sur une hypothèse."""
        self.test_syntax(hypothesis, language)
        if hypothesis.syntax_valid:
            self.test_execution(hypothesis, language)
        self.test_quality(hypothesis, language)
        self.test_complexity(hypothesis, language)
        self.test_style(hypothesis, language)
        self.test_correctness(hypothesis, language, test_cases)
        return hypothesis

    def _run_js_check(self, code: str) -> dict:
        try:
            with tempfile.TemporaryDirectory(prefix="hyp_js_") as tmp:
                script = Path(tmp) / "check.js"
                script.write_text(f"try {{ new Function({json.dumps(code)}); }} catch(e) {{ process.exit(1); }}", encoding="utf-8")
                result = subprocess.run(
                    ["node", str(script)],
                    capture_output=True, text=True, timeout=5,
                )
                return {"success": result.returncode == 0, "error": (result.stderr or "")[:500]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _make_safe(self, code: str) -> str:
        dangerous = [
            r"os\.system\(",
            r"subprocess\.call\(",
            r"subprocess\.run\(",
            r"__import__\(",
            r"exec\(",
            r"eval\(",
            r"open\(.+['\"]w['\"]",
            r"shutil\.rmtree",
            r"os\.remove",
            r"os\.unlink",
            r"rmdir",
            r"\.run\(debug\s*=\s*True\)",
            r"\.run\(",
            r"socketio\.run\(",
            r"input\(",
        ]
        safe = code
        for pattern in dangerous:
            safe = re.sub(pattern, "# [BLOCKED] " + pattern, safe)
        return safe

    def _run_with_input(self, code: str, input_data: str) -> str:
        with tempfile.TemporaryDirectory(prefix="hyp_run_") as tmp:
            script = Path(tmp) / "run.py"
            script.write_text(code, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True, text=True,
                input=input_data, timeout=5, cwd=tmp,
            )
            return (proc.stdout or "").strip()


class HypothesisEvaluator:
    """Évalue et classe les hypothèses."""

    def rank(self, hypotheses: list[Hypothesis]) -> list[Hypothesis]:
        """Classe les hypothèses par score total décroissant."""
        return sorted(hypotheses, key=lambda h: h.total_score, reverse=True)

    def select_best(self, hypotheses: list[Hypothesis]) -> Optional[Hypothesis]:
        """Sélectionne la meilleure hypothèse."""
        ranked = self.rank(hypotheses)
        if not ranked:
            return None
        best = ranked[0]
        if best.total_score < 0.2:
            return None
        return best

    def compare(self, h1: Hypothesis, h2: Hypothesis) -> dict:
        """Compare deux hypothèses."""
        diff = {}
        all_keys = set(h1.scores.keys()) | set(h2.scores.keys())
        for key in all_keys:
            s1 = h1.scores.get(key, 0)
            s2 = h2.scores.get(key, 0)
            diff[key] = {"h1": s1, "h2": s2, "winner": "h1" if s1 > s2 else "h2" if s2 > s1 else "tie"}
        diff["overall"] = {
            "h1": h1.total_score,
            "h2": h2.total_score,
            "winner": "h1" if h1.total_score > h2.total_score else "h2" if h2.total_score > h1.total_score else "tie",
        }
        return diff

    def get_analysis(self, hypotheses: list[Hypothesis]) -> dict:
        """Analyse complète de toutes les hypothèses."""
        if not hypotheses:
            return {"count": 0, "best": None, "avg_score": 0}
        ranked = self.rank(hypotheses)
        scores = [h.total_score for h in hypotheses]
        strategies = Counter(h.strategy for h in hypotheses)
        syntax_pass = sum(1 for h in hypotheses if h.syntax_valid)
        exec_pass = sum(1 for h in hypotheses if h.test_passed)
        return {
            "count": len(hypotheses),
            "best": ranked[0].to_dict() if ranked else None,
            "best_score": ranked[0].total_score if ranked else 0,
            "avg_score": round(sum(scores) / len(scores), 3),
            "min_score": round(min(scores), 3),
            "max_score": round(max(scores), 3),
            "syntax_pass_rate": round(syntax_pass / len(hypotheses), 2),
            "execution_pass_rate": round(exec_pass / len(hypotheses), 2),
            "strategies": dict(strategies),
            "all_scores": [{"id": h.id, "strategy": h.strategy,
                            "score": h.total_score, "syntax": h.syntax_valid,
                            "exec": h.test_passed} for h in ranked],
        }


class HypothesisEngine:
    """Moteur principal d'exécution d'hypothèses.

    Pipeline complet: générer → tester → évaluer → itérer → décider.
    """

    def __init__(self, max_iterations: int = 3):
        self.generator = HypothesisGenerator()
        self.tester = HypothesisTester()
        self.evaluator = HypothesisEvaluator()
        self.max_iterations = max_iterations
        self._history: list[dict] = []

    def solve_fix(self, code: str, errors: list[dict],
                  language: str) -> dict:
        """Résout des erreurs de code de manière itérative."""
        run_id = uuid.uuid4().hex[:10]
        all_hypotheses = []
        current_code = code
        current_errors = errors
        iteration = 0
        best = None
        while iteration < self.max_iterations and current_errors:
            iteration += 1
            hypotheses = self.generator.generate_fix_hypotheses(
                current_code, current_errors, language
            )
            if not hypotheses:
                break
            for h in hypotheses:
                h.iteration = iteration
                self.tester.run_all_tests(h, language)
            all_hypotheses.extend(hypotheses)
            best = self.evaluator.select_best(hypotheses)
            if not best:
                break
            if best.syntax_valid:
                current_code = best.content
                new_errors = self._recheck(current_code, language)
                if not new_errors:
                    current_errors = []
                    break
                current_errors = new_errors
            else:
                break
        analysis = self.evaluator.get_analysis(all_hypotheses)
        result = {
            "run_id": run_id,
            "iterations": iteration,
            "total_hypotheses": len(all_hypotheses),
            "best_hypothesis": best.to_dict() if best else None,
            "original_code": code,
            "fixed_code": best.content if best else code,
            "resolved": len(current_errors) == 0,
            "remaining_errors": current_errors,
            "analysis": analysis,
        }
        self._history.append({
            "run_id": run_id,
            "type": "fix",
            "timestamp": time.time(),
            "hypotheses": len(all_hypotheses),
            "resolved": result["resolved"],
            "best_score": best.total_score if best else 0,
        })
        return result

    def solve_generation(self, prompt: str, language: str,
                         context: dict = None) -> dict:
        """Génère et teste plusieurs solutions possibles."""
        run_id = uuid.uuid4().hex[:10]
        hypotheses = self.generator.generate_solution_hypotheses(
            prompt, language, context
        )
        if not hypotheses:
            return {
                "run_id": run_id,
                "iterations": 0,
                "total_hypotheses": 0,
                "best_hypothesis": None,
                "analysis": {"count": 0},
            }
        for h in hypotheses:
            self.tester.run_all_tests(h, language)
        ranked = self.evaluator.rank(hypotheses)
        best = self.evaluator.select_best(hypotheses)
        analysis = self.evaluator.get_analysis(hypotheses)
        result = {
            "run_id": run_id,
            "iterations": 1,
            "total_hypotheses": len(hypotheses),
            "best_hypothesis": best.to_dict() if best else None,
            "all_hypotheses": [h.to_dict() for h in ranked],
            "analysis": analysis,
        }
        self._history.append({
            "run_id": run_id,
            "type": "generation",
            "timestamp": time.time(),
            "hypotheses": len(hypotheses),
            "best_score": best.total_score if best else 0,
        })
        return result

    def solve_optimization(self, code: str, language: str) -> dict:
        """Génère et teste des hypothèses d'optimisation."""
        run_id = uuid.uuid4().hex[:10]
        hypotheses = self.generator.generate_optimization_hypotheses(code, language)
        if not hypotheses:
            return {
                "run_id": run_id,
                "iterations": 0,
                "total_hypotheses": 0,
                "best_hypothesis": None,
                "analysis": {"count": 0},
            }
        for h in hypotheses:
            self.tester.run_all_tests(h, language)
        best = self.evaluator.select_best(hypotheses)
        analysis = self.evaluator.get_analysis(hypotheses)
        result = {
            "run_id": run_id,
            "iterations": 1,
            "total_hypotheses": len(hypotheses),
            "best_hypothesis": best.to_dict() if best else None,
            "original_code": code,
            "optimized_code": best.content if best else code,
            "analysis": analysis,
        }
        self._history.append({
            "run_id": run_id,
            "type": "optimization",
            "timestamp": time.time(),
            "hypotheses": len(hypotheses),
            "best_score": best.total_score if best else 0,
        })
        return result

    def get_history(self) -> list[dict]:
        return list(self._history)

    def get_stats(self) -> dict:
        total_runs = len(self._history)
        total_hypotheses = sum(h["hypotheses"] for h in self._history)
        fix_runs = [h for h in self._history if h["type"] == "fix"]
        resolved = sum(1 for h in fix_runs if h.get("resolved"))
        avg_score = 0
        if self._history:
            avg_score = sum(h.get("best_score", 0) for h in self._history) / len(self._history)
        return {
            "total_runs": total_runs,
            "total_hypotheses": total_hypotheses,
            "fix_runs": len(fix_runs),
            "fix_resolved": resolved,
            "avg_best_score": round(avg_score, 3),
            "types": Counter(h["type"] for h in self._history),
        }

    def _recheck(self, code: str, language: str) -> list[dict]:
        errors = []
        if language == "python":
            try:
                ast.parse(code)
            except SyntaxError as e:
                errors.append({"line": e.lineno, "msg": e.msg, "type": "syntax"})
        return errors


hypothesis_engine = HypothesisEngine()
