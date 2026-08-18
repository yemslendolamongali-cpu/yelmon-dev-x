import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./CodeAnalyzer.css";

const API = "https://yelmon-dev-x.onrender.com";

export default function CodeAnalyzer() {
  const nav = useNavigate();
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("auto");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const analyze = async (fix = false) => {
    if (!code.trim()) return;
    setLoading(true);
    try {
      const resp = await fetch(`${API}/api/code/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language, fix }),
      });
      const data = await resp.json();
      setResult(data);
    } catch (e) {
      setResult({ error: "Erreur de connexion", errors: [], quality_issues: [], score: 0, grade: "F", summary: { critical: 0, warnings: 0, style: 0, info: 0, total: 0 } });
    }
    setLoading(false);
  };

  const copyFixed = () => {
    if (result?.fixed_code) {
      navigator.clipboard.writeText(result.fixed_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getGradeClass = (g) => {
    if (g === "A+") return "a-plus";
    if (g === "A") return "a";
    if (g === "B") return "b";
    if (g === "C") return "c";
    if (g === "D") return "d";
    return "f";
  };

  const allErrors = [
    ...(result?.errors || []),
    ...(result?.quality_issues || []),
  ];

  return (
    <div className="code-analyzer-page">
      <div className="code-analyzer-bg" />
      <div className="code-analyzer-container">
        <div className="code-analyzer-header">
          <div>
            <h1>Analyseur de code</h1>
            <p className="subtitle">Détecte les erreurs en temps réel et corrige automatiquement</p>
          </div>
          <button className="back-btn" onClick={() => nav("/dashboard")}>← Retour</button>
        </div>

        <div className="analyzer-main">
          <div className="analyzer-editor-panel">
            <div className="editor-toolbar">
              <select className="lang-select" value={language} onChange={(e) => setLanguage(e.target.value)}>
                <option value="auto">Auto-detect</option>
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="html">HTML</option>
                <option value="java">Java</option>
                <option value="go">Go</option>
                <option value="rust">Rust</option>
                <option value="cpp">C++</option>
              </select>
              <button className="analyze-btn primary" onClick={() => analyze(false)} disabled={loading}>
                {loading ? "Analyse..." : "🔍 Analyser"}
              </button>
              <button className="analyze-btn fix" onClick={() => analyze(true)} disabled={loading}>
                {loading ? "Analyse..." : "⚡ Analyser + Corriger"}
              </button>
            </div>
            <textarea
              className="code-textarea"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder={"Collez votre code ici...\n\nExemple :\ndef calculer(a, b)\n    return a + b\n\n# Le système détecte automatiquement les erreurs\n# et vous propose des corrections instantanées"}
              spellCheck={false}
            />
          </div>

          <div className="analyzer-results-panel">
            {result && !result.error ? (
              <>
                <div className="score-card">
                  <div className={`score-circle ${getGradeClass(result.grade)}`}>
                    {result.grade}
                  </div>
                  <div className="score-details">
                    <span className="lang-badge">{result.language}</span>
                    <div className="summary">
                      <strong>{result.score}/100</strong> — {result.code_lines} lignes de code
                    </div>
                    <div className="error-counts">
                      {result.summary.critical > 0 && <span className="error-count critical">🔴 {result.summary.critical} critique</span>}
                      {result.summary.warnings > 0 && <span className="error-count warning">🟡 {result.summary.warnings} avertissement</span>}
                      {result.summary.style > 0 && <span className="error-count style">🟣 {result.summary.style} style</span>}
                      {result.summary.info > 0 && <span className="error-count info">⚪ {result.summary.info} info</span>}
                      {result.summary.total === 0 && <span className="error-count ok">✅ Aucune erreur</span>}
                    </div>
                  </div>
                </div>

                {allErrors.length > 0 && (
                  <div className="errors-container">
                    <h3>{allErrors.length} problème{allErrors.length > 1 ? "s" : ""} détecté{allErrors.length > 1 ? "s" : ""}</h3>
                    {allErrors.map((e, i) => (
                      <div key={i} className={`error-item ${e.severity || "info"}`}>
                        <span className="error-line">{e.line ? `L${e.line}` : "—"}</span>
                        <span className="error-msg">{e.message}</span>
                        <span className="error-source">{e.source}</span>
                      </div>
                    ))}
                  </div>
                )}

                {result.has_fix && (
                  <div className="fixed-code-container">
                    <h3>✅ Code corrigé</h3>
                    <pre className="fixed-code">{result.fixed_code}</pre>
                    <button className="copy-btn" onClick={copyFixed}>
                      {copied ? "✅ Copié !" : "📋 Copier le code corrigé"}
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="no-results">
                {result?.error ? result.error : "Collez du code et cliquez Analyser pour commencer"}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
