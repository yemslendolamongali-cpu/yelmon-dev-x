import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import "./LocalDeploy.css";

const API = "https://yelmon-dev-x.onrender.com";

export default function LocalDeploy() {
  const nav = useNavigate();
  const [status, setStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stepStatus, setStepStatus] = useState({});
  const [fullSetupLoading, setFullSetupLoading] = useState(false);

  const loadStatus = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/launcher/status`);
      setStatus(await r.json());
    } catch { setStatus(null); }
    setLoading(false);
  }, []);

  const loadLogs = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/launcher/logs?lines=80`);
      setLogs(await r.json());
    } catch {}
  }, []);

  useEffect(() => { loadStatus(); loadLogs(); }, [loadStatus, loadLogs]);

  const doStep = async (url, key) => {
    setStepStatus(s => ({ ...s, [key]: "loading" }));
    try {
      const r = await fetch(`${API}${url}`, { method: "POST" });
      const d = await r.json();
      setStepStatus(s => ({ ...s, [key]: d.ok ? "ok" : "err" }));
      loadStatus();
      loadLogs();
    } catch {
      setStepStatus(s => ({ ...s, [key]: "err" }));
    }
  };

  const doFullSetup = async () => {
    setFullSetupLoading(true);
    setStepStatus({ full: "loading" });
    try {
      const r = await fetch(`${API}/api/launcher/setup/full`, { method: "POST" });
      const d = await r.json();
      setStepStatus(s => ({ ...s, full: d.ok ? "ok" : "err" }));
      loadStatus();
      loadLogs();
    } catch {
      setStepStatus(s => ({ ...s, full: "err" }));
    }
    setFullSetupLoading(false);
  };

  const doLaunch = async () => {
    setStepStatus(s => ({ ...s, launch: "loading" }));
    try {
      const r = await fetch(`${API}/api/launcher/start`, { method: "POST" });
      const d = await r.json();
      setStepStatus(s => ({ ...s, launch: d.ok ? "ok" : "err" }));
      loadStatus();
      loadLogs();
    } catch {
      setStepStatus(s => ({ ...s, launch: "err" }));
    }
  };

  const doStop = async () => {
    try {
      await fetch(`${API}/api/launcher/stop`, { method: "POST" });
      setStepStatus(s => ({ ...s, launch: "err" }));
      loadStatus();
      loadLogs();
    } catch {}
  };

  const renderStatus = (key) => {
    const s = stepStatus[key];
    if (s === "loading") return <span className="ld-step-status loading">⏳ En cours...</span>;
    if (s === "ok") return <span className="ld-step-status ok">✅ Terminé</span>;
    if (s === "err") return <span className="ld-step-status err">❌ Échec</span>;
    return null;
  };

  if (loading) return <div className="local-deploy-page"><div className="ld-bg" /><div className="ld-container"><p>Chargement...</p></div></div>;

  return (
    <div className="local-deploy-page">
      <div className="ld-bg" />
      <div className="ld-container">
        <div className="ld-header">
          <div>
            <h1>Local Deploy</h1>
            <p className="subtitle">Lanceur local — fusion de YELMON_Launcher.py, installer.py, auto_deploy.py</p>
          </div>
          <button className="back-btn" onClick={() => nav("/dashboard")}>← Retour</button>
        </div>

        {/* STATUS */}
        <div className="ld-status-card">
          <h2>État du système</h2>
          <div className="ld-status-grid">
            <div className="ld-status-item">
              <div className={`ld-dot ${status?.venv_exists ? "ok" : "err"}`} />
              <div><div className="ld-status-label">Environnement virtuel</div><div className="ld-status-val">{status?.venv_exists ? "Installé" : "Non installé"}</div></div>
            </div>
            <div className="ld-status-item">
              <div className={`ld-dot ${status?.pip_exists ? "ok" : "err"}`} />
              <div><div className="ld-status-label">Pip</div><div className="ld-status-val">{status?.pip_exists ? "Disponible" : "Non disponible"}</div></div>
            </div>
            <div className="ld-status-item">
              <div className={`ld-dot ${status?.build_exists ? "ok" : "err"}`} />
              <div><div className="ld-status-label">Frontend build</div><div className="ld-status-val">{status?.build_exists ? "Prêt" : "Non buildé"}</div></div>
            </div>
            <div className="ld-status-item">
              <div className={`ld-dot ${status?.requirements_exists ? "ok" : "warn"}`} />
              <div><div className="ld-status-label">requirements.txt</div><div className="ld-status-val">{status?.requirements_exists ? "Présent" : "Absente"}</div></div>
            </div>
            <div className="ld-status-item">
              <div className={`ld-dot ${status?.backend_running ? "ok" : "err"}`} />
              <div><div className="ld-status-label">Backend</div><div className="ld-status-val">{status?.backend_running ? "En cours" : "Arrêté"}</div></div>
            </div>
            <div className="ld-status-item">
              <div className="ld-dot ok" />
              <div><div className="ld-status-label">Platform</div><div className="ld-status-val">{status?.platform}</div></div>
            </div>
          </div>
        </div>

        {/* ONE-CLICK SETUP */}
        <div className="ld-oneclick">
          <h2>Setup complet en un clic</h2>
          <p>Crée le venv, installe les dépendances, build le frontend, crée le raccourci bureau</p>
          <button className="ld-oneclick-btn" onClick={doFullSetup} disabled={fullSetupLoading}>
            {fullSetupLoading ? "⏳ Installation..." : "⚡ Tout installer"}
          </button>
          {renderStatus("full")}
        </div>

        {/* INDIVIDUAL STEPS */}
        <div className="ld-steps">
          <div className="ld-step">
            <h3>🐍 Environnement virtuel</h3>
            <p>Crée le dossier venv avec Python et pip</p>
            <button className="ld-step-btn blue" onClick={() => doStep("/api/launcher/setup/venv", "venv")}>
              Créer le venv
            </button>
            {renderStatus("venv")}
          </div>
          <div className="ld-step">
            <h3>📦 Dépendances Python</h3>
            <p>Installe Flask, PyJWT, psutil, etc.</p>
            <button className="ld-step-btn blue" onClick={() => doStep("/api/launcher/setup/deps", "deps")}>
              Installer les deps
            </button>
            {renderStatus("deps")}
          </div>
          <div className="ld-step">
            <h3>🔨 Build frontend</h3>
            <p>Build React avec npm install + npm build</p>
            <button className="ld-step-btn purple" onClick={() => doStep("/api/launcher/setup/frontend", "frontend")}>
              Build frontend
            </button>
            {renderStatus("frontend")}
          </div>
          <div className="ld-step">
            <h3>🖥 Raccourci bureau</h3>
            <p>Crée un raccourci sur le bureau pour lancer YELMON</p>
            <button className="ld-step-btn orange" onClick={() => doStep("/api/launcher/setup/shortcut", "shortcut")}>
              Créer le raccourci
            </button>
            {renderStatus("shortcut")}
          </div>
        </div>

        {/* LAUNCH */}
        <div className="ld-launch">
          <h2>Lancement</h2>
          <div className="ld-launch-btns">
            <button className="ld-step-btn green" onClick={doLaunch}>
              ▶ Démarrer le backend
            </button>
            <button className="ld-step-btn red" onClick={doStop}>
              ⏹ Arrêter le backend
            </button>
          </div>
          {renderStatus("launch")}
        </div>

        {/* LOGS */}
        <div className="ld-logs">
          <h2>
            Logs en temps réel
            <button className="refresh-btn" onClick={loadLogs}>🔄 Actualiser</button>
          </h2>
          <div className="ld-log-content">
            {logs.length > 0 ? logs.map((l, i) => (
              <div key={i} className="ld-log-line">{l}</div>
            )) : <div className="ld-log-line" style={{ color: "#5a4a7a" }}>Aucun log — lancez une action pour voir les logs</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
