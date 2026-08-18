import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import "./SystemAdmin.css";

const API = "https://yelmon-dev-x.onrender.com";

export default function SystemAdmin() {
  const nav = useNavigate();
  const [tab, setTab] = useState("overview");
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionStatus, setActionStatus] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  const loadSummary = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/system/summary`);
      const d = await r.json();
      setSummary(d);
    } catch { setSummary(null); }
    setLoading(false);
  }, []);

  useEffect(() => { loadSummary(); }, [loadSummary]);

  const doAction = async (url, label) => {
    setActionLoading(true);
    setActionStatus({ type: "loading", msg: `${label}...` });
    try {
      const r = await fetch(`${API}${url}`, { method: "POST" });
      const d = await r.json();
      if (d.ok) {
        setActionStatus({ type: "ok", msg: `${label} terminé avec succès` });
        loadSummary();
      } else {
        setActionStatus({ type: "err", msg: d.error || "Échec" });
      }
    } catch {
      setActionStatus({ type: "err", msg: "Erreur de connexion" });
    }
    setActionLoading(false);
  };

  const env = summary?.environment;
  const ports = summary?.ports || [];
  const procs = summary?.processes || [];
  const backups = summary?.backups || [];
  const scripts = summary?.reconstruction_scripts || [];

  return (
    <div className="system-admin-page">
      <div className="sa-bg" />
      <div className="sa-container">
        <div className="sa-header">
          <div>
            <h1>System Admin</h1>
            <p className="subtitle">Environnement, processus, build, backup — fusion des scripts de reconstruction</p>
          </div>
          <button className="back-btn" onClick={() => nav("/dashboard")}>← Retour</button>
        </div>

        <div className="sa-tabs">
          {[
            { id: "overview", icon: "📊", label: "Vue d'ensemble" },
            { id: "env", icon: "🐍", label: "Environnement" },
            { id: "ports", icon: "🔌", label: "Ports" },
            { id: "procs", icon: "⚙", label: "Processus" },
            { id: "build", icon: "🔨", label: "Build & Install" },
            { id: "backup", icon: "💾", label: "Backup" },
            { id: "scripts", icon: "📜", label: "Scripts" },
          ].map(t => (
            <div key={t.id} className={`sa-tab ${tab === t.id ? "active" : ""}`} onClick={() => setTab(t.id)}>
              {t.icon} {t.label}
            </div>
          ))}
        </div>

        {loading ? (
          <div className="sa-card"><p>Chargement...</p></div>
        ) : (
          <>
            {/* OVERVIEW */}
            <div className={`sa-section ${tab === "overview" ? "active" : ""}`}>
              <div className="env-grid">
                <div className="env-item">
                  <div className={`env-icon ${env?.python?.ok ? "ok" : "err"}`}>🐍</div>
                  <div className="env-info">
                    <div className="env-label">Python</div>
                    <div className="env-value">{env?.python?.version || "N/A"}</div>
                    <div className="env-detail">pip: {env?.python?.pip ? "✅" : "❌"}</div>
                  </div>
                </div>
                <div className="env-item">
                  <div className={`env-icon ${env?.node?.ok ? "ok" : "err"}`}>📦</div>
                  <div className="env-info">
                    <div className="env-label">Node.js</div>
                    <div className="env-value">{env?.node?.version || "N/A"}</div>
                    <div className="env-detail">{env?.node?.path}</div>
                  </div>
                </div>
                <div className="env-item">
                  <div className="env-icon ok">🖥</div>
                  <div className="env-info">
                    <div className="env-label">OS</div>
                    <div className="env-value">{env?.os?.system} {env?.os?.release}</div>
                    <div className="env-detail">{env?.os?.machine} — {env?.os?.processor?.substring(0, 40)}</div>
                  </div>
                </div>
                <div className="env-item">
                  <div className="env-icon ok">💿</div>
                  <div className="env-info">
                    <div className="env-label">Disque</div>
                    <div className="env-value">{env?.disk?.used_pct}% utilisé</div>
                    <div className="env-detail">{env?.disk?.used_gb} / {env?.disk?.total_gb} GB</div>
                  </div>
                </div>
                <div className="env-item">
                  <div className="env-icon ok">🧠</div>
                  <div className="env-info">
                    <div className="env-label">RAM</div>
                    <div className="env-value">{env?.memory?.ram_used_pct}% utilisé</div>
                    <div className="env-detail">{env?.memory?.ram_available_gb} GB disponible</div>
                  </div>
                </div>
                <div className="env-item">
                  <div className={`env-icon ${env?.git?.ok ? "ok" : "err"}`}>🔀</div>
                  <div className="env-info">
                    <div className="env-label">Git</div>
                    <div className="env-value">{env?.git?.version || "N/A"}</div>
                  </div>
                </div>
              </div>

              <div className="sa-card" style={{ marginTop: 16 }}>
                <h3>Ports ouverts</h3>
                <div className="port-list">
                  {ports.map(p => (
                    <div key={p.port} className="port-item">
                      <div className="port-num">{p.port}</div>
                      <div className={`port-status ${p.open ? "open" : "closed"}`}>
                        {p.open ? "● Ouvert" : "○ Fermé"}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="sa-card">
                <h3>Processus actifs ({procs.length})</h3>
                {procs.length > 0 ? (
                  <table className="proc-table">
                    <thead><tr><th>PID</th><th>Nom</th><th>CPU%</th><th>RAM (MB)</th></tr></thead>
                    <tbody>
                      {procs.map(p => (
                        <tr key={p.pid}>
                          <td>{p.pid}</td><td>{p.name}</td><td>{p.cpu_pct}</td><td>{p.mem_mb}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : <p style={{ color: "#5a4a7a", fontSize: 13 }}>Aucun processus Python/Node détecté</p>}
              </div>
            </div>

            {/* ENV */}
            <div className={`sa-section ${tab === "env" ? "active" : ""}`}>
              <div className="sa-card">
                <h2>Environnement complet</h2>
                <pre style={{ background: "rgba(0,0,0,0.3)", padding: 16, borderRadius: 10, fontSize: 12, color: "#c9b8e8", overflow: "auto", maxHeight: 400 }}>
                  {JSON.stringify(env, null, 2)}
                </pre>
              </div>
            </div>

            {/* PORTS */}
            <div className={`sa-section ${tab === "ports" ? "active" : ""}`}>
              <div className="sa-card">
                <h2>Scan des ports</h2>
                <div className="port-list">
                  {ports.map(p => (
                    <div key={p.port} className="port-item">
                      <div className="port-num">{p.port}</div>
                      <div className={`port-status ${p.open ? "open" : "closed"}`}>
                        {p.open ? "● Ouvert" : "○ Fermé"}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* PROCS */}
            <div className={`sa-section ${tab === "procs" ? "active" : ""}`}>
              <div className="sa-card">
                <h2>Processus Python / Node</h2>
                {procs.length > 0 ? (
                  <table className="proc-table">
                    <thead><tr><th>PID</th><th>Nom</th><th>CPU%</th><th>RAM (MB)</th><th>Uptime</th></tr></thead>
                    <tbody>
                      {procs.map(p => (
                        <tr key={p.pid}>
                          <td>{p.pid}</td><td>{p.name}</td><td>{p.cpu_pct}</td><td>{p.mem_mb}</td>
                          <td>{Math.floor(p.uptime_sec / 60)}m</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : <p style={{ color: "#5a4a7a" }}>Aucun processus détecté</p>}
              </div>
            </div>

            {/* BUILD */}
            <div className={`sa-section ${tab === "build" ? "active" : ""}`}>
              <div className="sa-card">
                <h2>Build & Installation</h2>
                <p style={{ color: "#8a7aaa", fontSize: 13, marginBottom: 16 }}>
                  Fonctionnalités issues des scripts de reconstruction (build.py, installer.py)
                </p>
                <div className="sa-actions">
                  <button className="sa-btn green" onClick={() => doAction("/api/system/install-deps", "Installation dépendances")} disabled={actionLoading}>
                    📦 Installer les dépendances
                  </button>
                  <button className="sa-btn blue" onClick={() => doAction("/api/system/build-frontend", "Build frontend")} disabled={actionLoading}>
                    🔨 Build frontend
                  </button>
                </div>
                {actionStatus && tab === "build" && (
                  <div className={`sa-status ${actionStatus.type}`}>{actionStatus.msg}</div>
                )}
              </div>
            </div>

            {/* BACKUP */}
            <div className={`sa-section ${tab === "backup" ? "active" : ""}`}>
              <div className="sa-card">
                <h2>Backup & Restore</h2>
                <div className="sa-actions">
                  <button className="sa-btn purple" onClick={() => doAction("/api/system/backup", "Création backup")} disabled={actionLoading}>
                    💾 Créer un backup complet
                  </button>
                </div>
                {actionStatus && tab === "backup" && (
                  <div className={`sa-status ${actionStatus.type}`}>{actionStatus.msg}</div>
                )}
                <h3>Backups existants ({backups.length})</h3>
                {backups.length > 0 ? backups.map((b, i) => (
                  <div key={i} className="backup-item">
                    <div>
                      <div className="backup-name">{b.filename}</div>
                      <div className="backup-meta">{b.size_mb} MB — {b.created}</div>
                    </div>
                  </div>
                )) : <p style={{ color: "#5a4a7a", fontSize: 13 }}>Aucun backup</p>}
              </div>
            </div>

            {/* SCRIPTS */}
            <div className={`sa-section ${tab === "scripts" ? "active" : ""}`}>
              <div className="sa-card">
                <h2>Scripts de reconstruction</h2>
                <p style={{ color: "#8a7aaa", fontSize: 13, marginBottom: 16 }}>
                  Scripts originaux de Monprojet/reconstruction/ — fusionnés dans l'app
                </p>
                {scripts.length > 0 ? scripts.map((s, i) => (
                  <div key={i} className="script-item">
                    <div className="script-name">{s.name}</div>
                    <div className="script-meta">{s.size_kb} KB — {s.modified}</div>
                  </div>
                )) : <p style={{ color: "#5a4a7a" }}>Aucun script trouvé</p>}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
