"""
YELMON Dev X — Script de déploiement web
Lance le backend sur 0.0.0.0 pour un accès réseau.
Accessible depuis tous les appareils connectés au même réseau.
"""

import os
import sys
import socket
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
VENV_PYTHON = ROOT / "venv" / "Scripts" / "python.exe"
SYSTEM_PYTHON = sys.executable


def get_local_ip():
    """Récupère l'adresse IP locale."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def build_frontend():
    """Compile le frontend React."""
    print("\n[1/3] Compilation du frontend...")
    npm_cmd = str(FRONTEND_DIR / "node_modules" / ".bin" / "npm.cmd")
    if not Path(npm_cmd).exists():
        npm_cmd = "npm"

    result = subprocess.run(
        [npm_cmd, "run", "build"],
        cwd=str(FRONTEND_DIR),
        shell=True,
    )
    if result.returncode != 0:
        print("  ✗ Erreur lors de la compilation du frontend")
        return False
    print("  ✓ Frontend compilé avec succès")
    return True


def start_backend():
    """Démarre le backend Flask sur 0.0.0.0."""
    print("\n[2/3] Démarrage du backend...")

    python_exe = str(VENV_PYTHON) if VENV_PYTHON.exists() else SYSTEM_PYTHON
    env = os.environ.copy()
    env["YELMON_HOST"] = "0.0.0.0"
    env["YELMON_PORT"] = "5001"

    subprocess.Popen(
        [python_exe, str(BACKEND_DIR / "app.py")],
        cwd=str(ROOT),
        env=env,
    )
    print("  ✓ Backend démarré")


def main():
    print("=" * 56)
    print("  YELMON Dev X — Déploiement Web")
    print("  © 2026 Yems junior lendola")
    print("=" * 56)

    # Build
    if not build_frontend():
        sys.exit(1)

    # Start
    start_backend()

    # Info
    ip = get_local_ip()
    port = 5001
    print(f"\n[3/3] Informations d'accès")
    print(f"  ┌─────────────────────────────────────────────┐")
    print(f"  │  URL locale   : http://127.0.0.1:{port}       │")
    print(f"  │  URL réseau   : http://{ip}:{port}            │")
    print(f"  │                                             │")
    print(f"  │  Accessible depuis :                        │")
    print(f"  │  • Chrome, Safari, Firefox, Edge            │")
    print(f"  │  • Smartphones, tablettes, PC               │")
    print(f"  │  • Tout appareil sur le même réseau         │")
    print(f"  │                                             │")
    print(f"  │  Pour arrêter : Ctrl+C                      │")
    print(f"  └─────────────────────────────────────────────┘")
    print(f"\n  Ouvrez http://{ip}:{port} dans votre navigateur\n")

    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nArrêt du serveur...")
        sys.exit(0)


if __name__ == "__main__":
    main()
