import React, { useState, useRef, useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./CodeAnalyzer.css";

const API = "https://yelmon-dev-x.onrender.com";

export default function CodeAnalyzer() {
  const nav = useNavigate();
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("auto");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState("syntax");
  const [dragOver, setDragOver] = useState(false);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [diffView, setDiffView] = useState("split");

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const resp = await fetch(`${API}/api/code/history`);
      const data = await resp.json();
      setHistory(data.history || []);
    } catch {}
  };

  const analyze = async (fix = false) => {
    if (!code.trim()) return;
    setLoading(true);
    try {
      const token = localStorage.getItem("yelmon_token");
      const resp = await fetch(`${API}/api/code/full-analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ code, language, fix }),
      });
      const data = await resp.json();
      setResult(data);
      setActiveTab("syntax");
      loadHistory();
    } catch {
      setResult({ error: "Erreur de connexion" });
    }
    setLoading(false);
  };

  const handleFileUpload = useCallback((file) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      setCode(e.target.result);
      const ext = file.name.split(".").pop().toLowerCase();
      const langMap = { py: "python", js: "javascript", jsx: "javascript", ts: "javascript", html: "html", htm: "html", java: "java", go: "go", rs: "rust", cpp: "cpp", c: "cpp", h: "cpp", css: "html", json: "javascript" };
      if (langMap[ext]) setLanguage(langMap[ext]);
    };
    reader.readAsText(file);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFileUpload(file);
  }, [handleFileUpload]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => setDragOver(false), []);

  const copyFixed = () => {
    if (result?.fixed_code) {
      navigator.clipboard.writeText(result.fixed_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const copyCode = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getGradeClass = (g) => {
    if (g === "A+") return "a-plus";
    if (g === "A") return "a";
    if (g === "B") return "b";
    if (g === "C") return "c";
    if (g === "D") return "d";
    return "f";
  };

  const allSyntaxIssues = [
    ...(result?.syntax?.errors || []),
    ...(result?.syntax?.quality_issues || []),
  ];

  const allDeepIssues = [
    ...(result?.deep?.bugs || []).map((b) => ({ line: b.line, severity: b.type, message: b.msg, source: "bug-detector" })),
    ...(result?.deep?.warnings || []).map((w) => ({ line: 0, severity: "warning", message: w, source: "quality" })),
  ];

  const allSuggestions = [
    ...(result?.deep?.suggestions || []).map((s) => ({ message: s, source: "suggestion" })),
    ...(result?.deep?.refactor || []).map((r) => ({ message: r, source: "refactor" })),
  ];

  const tabs = [
    { id: "syntax", label: "Syntaxe", count: allSyntaxIssues.length, icon: "🔍" },
    { id: "bugs", label: "Bugs", count: allDeepIssues.length, icon: "🐛" },
    { id: "suggestions", label: "Suggestions", count: allSuggestions.length, icon: "💡" },
    { id: "fix", label: "Correction", count: result?.has_fix ? 1 : 0, icon: "⚡" },
  ];

  return (
    <div className="code-analyzer-page">
      <div className="code-analyzer-bg" />
      <div className="code-analyzer-container">
        <div className="code-analyzer-header">
          <div>
            <h1>Analyseur de code avancé</h1>
            <p className="subtitle">Détection de bugs, suggestions, auto-correction et historique</p>
          </div>
          <div className="header-actions">
            <button className="history-toggle" onClick={() => setShowHistory(!showHistory)}>
              📋 Historique {history.length > 0 && <span className="history-count">{history.length}</span>}
            </button>
            <button className="back-btn" onClick={() => nav("/dashboard")}>← Retour</button>
          </div>
        </div>

        <div className="analyzer-layout">
          {showHistory && (
            <div className="history-sidebar">
              <div className="history-header">
                <h3>📋 Historique</h3>
                <button className="history-clear" onClick={async () => { await fetch(`${API}/api/code/history/clear`, { method: "POST" }); setHistory([]); }}>Effacer</button>
              </div>
              <div className="history-list">
                {history.length === 0 && <p className="history-empty">Aucune analyse</p>}
                {history.map((h) => (
                  <div key={h.id} className="history-item" onClick={() => { setCode(h.code_preview); setLanguage(h.language); setShowHistory(false); }}>
                    <div className="history-item-top">
                      <span className={`history-grade ${getGradeClass(h.grade)}`}>{h.grade}</span>
                      <span className="history-lang">{h.language}</span>
                      <span className="history-score">{h.score}/100</span>
                    </div>
                    <div className="history-item-preview">{h.code_preview?.slice(0, 80)}...</div>
                    <div className="history-item-time">{new Date(h.timestamp).toLocaleString("fr-FR")}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

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
                <button className="analyze-btn primary" onClick={() => analyze(false)} disabled={loading || !code.trim()}>
                  {loading ? "Analyse..." : "🔍 Analyser"}
                </button>
                <button className="analyze-btn fix" onClick={() => analyze(true)} disabled={loading || !code.trim()}>
                  {loading ? "Analyse..." : "⚡ Corriger"}
                </button>
                <button className="upload-btn" onClick={() => fileInputRef.current?.click()}>
                  📁 Fichier
                </button>
                <input ref={fileInputRef} type="file" accept=".py,.js,.jsx,.ts,.tsx,.html,.htm,.java,.go,.rs,.cpp,.cc,.c,.h,.css,.json" style={{ display: "none" }} onChange={(e) => handleFileUpload(e.target.files[0])} />
              </div>

              <div
                className={`textarea-wrapper ${dragOver ? "drag-over" : ""}`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
              >
                {dragOver && <div className="drop-overlay">📁 Déposez votre fichier ici</div>}
                <textarea
                  ref={textareaRef}
                  className="code-textarea"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder={"Collez votre code ici ou déposez un fichier...\n\nExemples :\ndef calculer(a, b)\n    return a + b\n\n// Le système détecte automatiquement :\n// - Erreurs syntaxiques\n// - Bugs potentiels\n// - Suggestions d'amélioration\n// - Code à refactoriser"}
                  spellCheck={false}
                />
              </div>

              <div className="editor-footer">
                <span className="line-count">{code.split("\n").length} lignes</span>
                <span className="char-count">{code.length} caractères</span>
              </div>
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
                        <strong>{result.score}/100</strong> — {result.deep?.metrics?.code_lines || 0} lignes de code
                      </div>
                      <div className="error-counts">
                        {allSyntaxIssues.filter((e) => e.severity === "critical").length > 0 && (
                          <span className="error-count critical">🔴 {allSyntaxIssues.filter((e) => e.severity === "critical").length} critique</span>
                        )}
                        {allDeepIssues.filter((e) => e.severity === "warning").length > 0 && (
                          <span className="error-count warning">🟡 {allDeepIssues.filter((e) => e.severity === "warning").length} avertissement</span>
                        )}
                        {allSyntaxIssues.filter((e) => e.severity === "style").length > 0 && (
                          <span className="error-count style">🟣 {allSyntaxIssues.filter((e) => e.severity === "style").length} style</span>
                        )}
                        {allSuggestions.length > 0 && (
                          <span className="error-count info">💡 {allSuggestions.length} suggestion</span>
                        )}
                        {allSyntaxIssues.length === 0 && allDeepIssues.length === 0 && (
                          <span className="error-count ok">✅ Aucune erreur</span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="structure-card">
                    <h3>📊 Structure</h3>
                    <div className="structure-grid">
                      <div className="structure-item"><span className="structure-label">Fonctions</span><span className="structure-value">{result.deep?.structure?.functions?.length || 0}</span></div>
                      <div className="structure-item"><span className="structure-label">Classes</span><span className="structure-value">{result.deep?.structure?.classes?.length || 0}</span></div>
                      <div className="structure-item"><span className="structure-label">Imports</span><span className="structure-value">{result.deep?.structure?.imports?.length || 0}</span></div>
                      <div className="structure-item"><span className="structure-label">Complexité</span><span className="structure-value">{result.deep?.structure?.complexity || 1}</span></div>
                    </div>
                  </div>

                  <div className="tabs-container">
                    <div className="tabs-header">
                      {tabs.map((t) => (
                        <button key={t.id} className={`tab-btn ${activeTab === t.id ? "active" : ""}`} onClick={() => setActiveTab(t.id)}>
                          {t.icon} {t.label} {t.count > 0 && <span className="tab-count">{t.count}</span>}
                        </button>
                      ))}
                    </div>

                    <div className="tab-content">
                      {activeTab === "syntax" && (
                        <div className="issues-list">
                          {allSyntaxIssues.length === 0 && <p className="no-issues">✅ Aucun problème de syntaxe détecté</p>}
                          {allSyntaxIssues.map((e, i) => (
                            <div key={i} className={`issue-item ${e.severity || "info"}`}>
                              <span className="issue-line">{e.line ? `L${e.line}` : "—"}</span>
                              <span className="issue-msg">{e.message}</span>
                              <span className="issue-source">{e.source}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {activeTab === "bugs" && (
                        <div className="issues-list">
                          {allDeepIssues.length === 0 && <p className="no-issues">✅ Aucun bug détecté</p>}
                          {allDeepIssues.map((e, i) => (
                            <div key={i} className={`issue-item ${e.severity || "info"}`}>
                              <span className="issue-line">{e.line ? `L${e.line}` : "—"}</span>
                              <span className="issue-msg">{e.message}</span>
                              <span className="issue-source">{e.source}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {activeTab === "suggestions" && (
                        <div className="issues-list">
                          {allSuggestions.length === 0 && <p className="no-issues">✅ Aucune suggestion</p>}
                          {allSuggestions.map((s, i) => (
                            <div key={i} className="issue-item suggestion">
                              <span className="issue-icon">{s.source === "refactor" ? "🔧" : "💡"}</span>
                              <span className="issue-msg">{s.message}</span>
                              <span className="issue-source">{s.source}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {activeTab === "fix" && (
                        <div className="fix-panel">
                          {!result.has_fix && <p className="no-issues">Aucune correction disponible. Cliquez "⚡ Corriger" pour auto-corriger.</p>}
                          {result.has_fix && (
                            <>
                              <div className="diff-controls">
                                <button className={`diff-btn ${diffView === "split" ? "active" : ""}`} onClick={() => setDiffView("split")}>Vue split</button>
                                <button className={`diff-btn ${diffView === "inline" ? "active" : ""}`} onClick={() => setDiffView("inline")}>Vue inline</button>
                              </div>

                              {diffView === "split" ? (
                                <div className="diff-split">
                                  <div className="diff-pane">
                                    <h4>❌ Original</h4>
                                    <pre className="diff-code original">{code}</pre>
                                  </div>
                                  <div className="diff-pane">
                                    <h4>✅ Corrigé</h4>
                                    <pre className="diff-code fixed">{result.fixed_code}</pre>
                                  </div>
                                </div>
                              ) : (
                                <div className="diff-inline">
                                  {result.diff?.map((d, i) => (
                                    <div key={i} className={`diff-line ${d.type}`}>
                                      <span className="diff-line-num">{d.line}</span>
                                      <span className="diff-line-prefix">{d.type === "added" ? "+" : d.type === "removed" ? "-" : " "}</span>
                                      <span className="diff-line-content">{d.content}</span>
                                    </div>
                                  ))}
                                </div>
                              )}

                              <div className="fix-actions">
                                <button className="copy-btn" onClick={copyFixed}>{copied ? "✅ Copié !" : "📋 Copier le code corrigé"}</button>
                              </div>
                            </>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </>
              ) : (
                <div className="no-results">
                  {result?.error ? result.error : "Collez du code ou déposez un fichier, puis cliquez Analyser"}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
