# YELMON_Launcher.py - Launcher graphique pour YELMON Dev X
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YELMON Dev X - Launcher Graphique
Version: 1.0.0
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import time
import socket
from pathlib import Path
import webbrowser

# ============================================
# CONSTANTES
# ============================================

APP_NAME = "YELMON Dev X"
APP_VERSION = "1.0.0"
BACKEND_PORT = 5001
FRONTEND_PORT = 3000

BASE_DIR = Path(__file__).parent

def get_venv_python():
    """Chemin de l'interpréteur Python du venv"""
    if sys.platform == 'win32':
        p = BASE_DIR / "venv" / "Scripts" / "python.exe"
    else:
        p = BASE_DIR / "venv" / "bin" / "python3"
    return str(p) if p.exists() else sys.executable

def check_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except socket.error:
            return False

# ============================================
# LAUNCHER GUI
# ============================================

class YELMONLauncherGUI:
    """Interface graphique du launcher YELMON"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} - Launcher")
        self.root.geometry("820x620")
        self.root.resizable(True, True)

        # Couleurs YELMON
        self.colors = {
            'primary': '#e94560',
            'secondary': '#0f3460',
            'dark': '#1a1a2e',
            'light': '#16213e',
            'text': '#ffffff',
            'text_secondary': '#a0a0a0',
            'success': '#4ade80',
            'error': '#f87171',
        }

        # Style
        self.setup_styles()

        # Variables
        self.is_running = False
        self.process = None
        self.log_lines = []

        # Créer l'interface
        self.create_widgets()

        # Vérifier l'installation
        self.check_installation()

        # Appliquer le thème
        self.apply_theme()

    def setup_styles(self):
        """Configure les styles tkinter"""
        style = ttk.Style()

        # Style pour les boutons
        style.configure('YELMON.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=10)

        # Style pour les labels
        style.configure('YELMON.TLabel',
                       font=('Segoe UI', 10),
                       background=self.colors['dark'],
                       foreground=self.colors['text'])

        # Style pour les frames
        style.configure('YELMON.TFrame',
                       background=self.colors['dark'])

        # Style pour le notebook
        style.configure('YELMON.TNotebook',
                       background=self.colors['dark'])
        style.configure('YELMON.TNotebook.Tab',
                       padding=[10, 5],
                       font=('Segoe UI', 10))

    def apply_theme(self):
        """Applique le thème YELMON"""
        self.root.configure(bg=self.colors['dark'])

    def create_widgets(self):
        """Crée les widgets de l'interface"""

        # ====================================
        # HEADER
        # ====================================
        header_frame = tk.Frame(self.root, bg=self.colors['secondary'], height=100)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Logo
        logo_label = tk.Label(
            header_frame,
            text=" YELMON Dev X",
            font=('Segoe UI', 28, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['primary']
        )
        logo_label.pack(pady=10)

        # Version
        version_label = tk.Label(
            header_frame,
            text=f"Version {APP_VERSION} - Assistant de Codage IA",
            font=('Segoe UI', 12),
            bg=self.colors['secondary'],
            fg=self.colors['text_secondary']
        )
        version_label.pack()

        # ====================================
        # MAIN CONTENT
        # ====================================
        main_frame = tk.Frame(self.root, bg=self.colors['dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Split en deux colonnes
        left_frame = tk.Frame(main_frame, bg=self.colors['dark'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_frame = tk.Frame(main_frame, bg=self.colors['dark'], width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))

        # ====================================
        # COLONNE GAUCHE - Contrôles
        # ====================================

        # Statut
        status_frame = tk.Frame(left_frame, bg=self.colors['light'], relief=tk.RAISED, bd=1)
        status_frame.pack(fill=tk.X, pady=(0, 15))

        status_label = tk.Label(
            status_frame,
            text=" Statut",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['light'],
            fg=self.colors['text']
        )
        status_label.pack(anchor=tk.W, padx=15, pady=10)

        self.status_var = tk.StringVar(value=" En attente...")
        status_display = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 12),
            bg=self.colors['light'],
            fg=self.colors['text_secondary']
        )
        status_display.pack(anchor=tk.W, padx=15, pady=(0, 10))

        # Détails du statut
        details_frame = tk.Frame(status_frame, bg=self.colors['light'])
        details_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        self.backend_status = tk.Label(
            details_frame,
            text=" Backend: Inactif",
            font=('Segoe UI', 10),
            bg=self.colors['light'],
            fg=self.colors['error']
        )
        self.backend_status.pack(anchor=tk.W)

        self.frontend_status = tk.Label(
            details_frame,
            text=" Frontend: Inactif",
            font=('Segoe UI', 10),
            bg=self.colors['light'],
            fg=self.colors['error']
        )
        self.frontend_status.pack(anchor=tk.W)

        # ====================================
        # CONTROLES
        # ====================================
        controls_frame = tk.Frame(left_frame, bg=self.colors['dark'])
        controls_frame.pack(fill=tk.X, pady=10)

        # Bouton Démarrer
        self.start_btn = tk.Button(
            controls_frame,
            text=" Démarrer YELMON",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['text'],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.start_yelmon,
            cursor='hand2'
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Bouton Arrêter
        self.stop_btn = tk.Button(
            controls_frame,
            text=" Arrêter",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['error'],
            fg=self.colors['text'],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.stop_yelmon,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT)

        # Bouton Installer
        install_btn = tk.Button(
            controls_frame,
            text=" Installer",
            font=('Segoe UI', 12),
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            relief=tk.FLAT,
            padx=15,
            pady=10,
            command=self.install_yelmon,
            cursor='hand2'
        )
        install_btn.pack(side=tk.LEFT, padx=(10, 0))

        # ====================================
        # LOGS
        # ====================================
        log_label = tk.Label(
            left_frame,
            text=" Logs",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['dark'],
            fg=self.colors['text']
        )
        log_label.pack(anchor=tk.W, pady=(15, 5))

        self.log_text = scrolledtext.ScrolledText(
            left_frame,
            height=12,
            bg=self.colors['light'],
            fg=self.colors['text'],
            font=('Consolas', 10),
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # ====================================
        # COLONNE DROITE - Informations
        # ====================================

        # Informations système
        sys_frame = tk.Frame(right_frame, bg=self.colors['light'], relief=tk.RAISED, bd=1)
        sys_frame.pack(fill=tk.X, pady=(0, 15))

        sys_title = tk.Label(
            sys_frame,
            text=" Informations",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['light'],
            fg=self.colors['text']
        )
        sys_title.pack(anchor=tk.W, padx=15, pady=(10, 5))

        info_items = [
            ("Version", f"{APP_VERSION}"),
            ("Port backend", f"{BACKEND_PORT}"),
            ("Port frontend", f"{FRONTEND_PORT}"),
        ]
        for label, value in info_items:
            row = tk.Frame(sys_frame, bg=self.colors['light'])
            row.pack(fill=tk.X, padx=15, pady=2)
            tk.Label(row, text=label, font=('Segoe UI', 10),
                     bg=self.colors['light'], fg=self.colors['text_secondary']).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=('Segoe UI', 10, 'bold'),
                     bg=self.colors['light'], fg=self.colors['text']).pack(side=tk.RIGHT)

        # Bouton navigateur
        browser_btn = tk.Button(
            right_frame,
            text=" Ouvrir dans le navigateur",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            relief=tk.FLAT,
            pady=10,
            command=self.open_browser,
            cursor='hand2'
        )
        browser_btn.pack(fill=tk.X, pady=(0, 10))

        # Bouton quitter
        quit_btn = tk.Button(
            right_frame,
            text=" Quitter",
            font=('Segoe UI', 11),
            bg=self.colors['light'],
            fg=self.colors['error'],
            relief=tk.FLAT,
            pady=10,
            command=self.on_close,
            cursor='hand2'
        )
        quit_btn.pack(fill=tk.X)

        # Gestionnaire de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ====================================
    # MÉTHODES
    # ====================================

    def log(self, message, type="info"):
        """Ajoute un message dans les logs"""
        colors = {
            "info": self.colors['text'],
            "success": self.colors['success'],
            "error": self.colors['error'],
            "warning": "#fbbf24",
        }
        color = colors.get(type, self.colors['text'])
        prefix = {
            "info": "[INFO]",
            "success": "[OK]",
            "error": "[ERREUR]",
            "warning": "[AVERT]",
        }.get(type, "[INFO]")

        timestamp = time.strftime("%H:%M:%S")
        line = f"{timestamp} {prefix} {message}"

        def _append():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, line + "\n", ("colored",))
            self.log_text.tag_config("colored", foreground=color)
            self.log_text.tag_add("colored", f"{float(self.log_text.index(tk.END)) - 1.0} linestart", "lineend")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)

        try:
            self.root.after(0, _append)
        except Exception:
            pass
        self.log_lines.append(line)

    def set_status(self, text):
        """Met à jour le statut affiché"""
        try:
            self.status_var.set(f" {text}")
        except Exception:
            pass

    def check_installation(self):
        """Vérifie l'état de l'installation"""
        def _check():
            self.log("Vérification de l'installation...", "info")
            venv_ok = Path(get_venv_python()).exists()
            backend_ok = (BASE_DIR / "backend" / "app.py").exists()
            build_ok = (BASE_DIR / "frontend" / "build").exists()

            if venv_ok and backend_ok and build_ok:
                self.set_status(" Prêt - installation complète")
                self.log("Installation complète détectée.", "success")
            else:
                missing = []
                if not venv_ok:
                    missing.append("venv Python")
                if not backend_ok:
                    missing.append("backend/app.py")
                if not build_ok:
                    missing.append("frontend build")
                self.set_status(" Installation incomplète")
                self.log(f"Éléments manquants: {', '.join(missing)}", "warning")
                self.log("Cliquez sur 'Installer' pour configurer l'application.", "info")
        threading.Thread(target=_check, daemon=True).start()

    def install_yelmon(self):
        """Lance l'installation complète"""
        def _install():
            self.set_status(" Installation en cours...")
            self.log("Installation de YELMON Dev X...", "info")
            self.log("Création de l'environnement virtuel...", "info")
            try:
                import venv
                venv_path = BASE_DIR / "venv"
                if not venv_path.exists():
                    venv.create(venv_path, with_pip=True)
                    self.log("Environnement virtuel créé.", "success")
                else:
                    self.log("Environnement virtuel déjà présent.", "info")
            except Exception as e:
                self.log(f"Erreur création venv: {e}", "error")

            self.log("Installation des dépendances Python...", "info")
            req = BASE_DIR / "requirements.txt"
            if req.exists():
                proc = subprocess.Popen(
                    [get_venv_python(), "-m", "pip", "install", "--upgrade", "pip"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                for line in proc.stdout:
                    if line.strip():
                        self.log(line.strip(), "info")
                proc.wait()
                proc = subprocess.Popen(
                    [get_venv_python(), "-m", "pip", "install", "-r", str(req)],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                for line in proc.stdout:
                    if line.strip():
                        self.log(line.strip(), "info")
                proc.wait()
                if proc.returncode == 0:
                    self.log("Dépendances Python installées.", "success")
                else:
                    self.log("Erreur d'installation des dépendances Python.", "error")

            self.log("Construction du frontend...", "info")
            frontend = BASE_DIR / "frontend"
            node = "npm.cmd" if sys.platform == 'win32' else "npm"
            if (frontend / "package.json").exists():
                proc = subprocess.Popen(
                    [node, "install"],
                    cwd=str(frontend), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                    shell=True if sys.platform == 'win32' else False,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                for line in proc.stdout:
                    if line.strip():
                        self.log(line.strip()[:160], "info")
                proc.wait()
                proc = subprocess.Popen(
                    [node, "run", "build"],
                    cwd=str(frontend), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                    shell=True if sys.platform == 'win32' else False,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                for line in proc.stdout:
                    if line.strip():
                        self.log(line.strip()[:160], "info")
                proc.wait()
                if proc.returncode == 0:
                    self.log("Frontend construit.", "success")
                else:
                    self.log("Erreur de construction du frontend.", "error")

            self.set_status(" Installation terminée")
            self.log("Installation terminée. Cliquez sur 'Démarrer YELMON'.", "success")

        threading.Thread(target=_install, daemon=True).start()

    def start_yelmon(self):
        """Démarre YELMON Dev X (backend + interface)"""
        if self.is_running:
            self.log("YELMON Dev X est déjà en cours d'exécution.", "warning")
            return

        def _start():
            self.start_btn.config(state=tk.DISABLED)
            self.set_status(" Démarrage du backend...")
            self.log("Démarrage du backend Flask...", "info")

            backend_script = BASE_DIR / "backend" / "app.py"
            if not backend_script.exists():
                self.log(f"backend/app.py introuvable: {backend_script}", "error")
                self.start_btn.config(state=tk.NORMAL)
                return

            # Vérifier le port
            if not check_port_available(BACKEND_PORT):
                self.log(f"Le port {BACKEND_PORT} est déjà utilisé - tentative d'utilisation directe.", "warning")

            env = os.environ.copy()
            env['PORT'] = str(BACKEND_PORT)

            try:
                self.process = subprocess.Popen(
                    [get_venv_python(), str(backend_script)],
                    cwd=str(BASE_DIR / "backend"),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                self.is_running = True
                self.stop_btn.config(state=tk.NORMAL)
                self.log(f"Backend lancé (pid {self.process.pid}).", "success")

                # Lire les logs du processus
                for line in self.process.stdout:
                    if line.strip():
                        self.log(line.strip()[:160], "info")
                    if self.process.poll() is not None and self.process.stdout.closed:
                        break
            except Exception as e:
                self.log(f"Erreur de démarrage: {e}", "error")

            self.is_running = False
            self.set_status(" Backend arrêté")
            self.log("Le backend s'est arrêté.", "warning")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

        self._backend_thread = threading.Thread(target=_start, daemon=True)
        self._backend_thread.start()

        # Ouvrir le navigateur après un court délai
        def _open_later():
            time.sleep(2)
            if self.is_running:
                self.set_status(" Prêt - en cours d'exécution")
                self.backend_status.config(text=" Backend: Actif", fg=self.colors['success'])
                self.open_browser()
        threading.Thread(target=_open_later, daemon=True).start()

    def stop_yelmon(self):
        """Arrête YELMON Dev X"""
        if self.process and self.process.poll() is None:
            self.log("Arrêt du backend...", "info")
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.log("Backend arrêté.", "success")
            except Exception as e:
                self.log(f"Erreur lors de l'arrêt: {e}", "error")
                try:
                    self.process.kill()
                except Exception:
                    pass
        self.process = None
        self.is_running = False
        self.set_status(" Arrêté")
        self.backend_status.config(text=" Backend: Inactif", fg=self.colors['error'])
        self.frontend_status.config(text=" Frontend: Inactif", fg=self.colors['error'])

    def open_browser(self):
        """Ouvre YELMON Dev X dans le navigateur"""
        url = f"http://localhost:{BACKEND_PORT}"
        try:
            webbrowser.open(url)
            self.log(f"Ouverture de {url} dans le navigateur...", "info")
        except Exception as e:
            self.log(f"Erreur d'ouverture du navigateur: {e}", "error")

    def on_close(self):
        """Ferme le launcher proprement"""
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
            except Exception:
                pass
        self.root.destroy()


def main():
    app = YELMONLauncherGUI()
    app.root.mainloop()


if __name__ == '__main__':
    main()
