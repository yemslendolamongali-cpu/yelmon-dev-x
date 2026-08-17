// © 2026 Yems junior lendola — All Rights Reserved.
// PROPRIETARY SOFTWARE — Unauthorized copying, distribution, reverse
// engineering, or reproduction of this code is strictly prohibited.

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Historique.css';

function Historique() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [search, setSearch] = useState('');
    const [selectedEntry, setSelectedEntry] = useState(null);
    const [expandedCode, setExpandedCode] = useState(null);

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('yelmon_token');
            const res = await fetch('/api/history', {
                headers: token ? { Authorization: `Bearer ${token}` } : {},
            });
            if (res.ok) {
                const data = await res.json();
                setHistory(Array.isArray(data.history) ? data.history : []);
            }
        } catch (e) {
            /* backend indisponible */
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        try {
            const token = localStorage.getItem('yelmon_token');
            await fetch(`/api/history/${id}`, {
                method: 'DELETE',
                headers: token ? { Authorization: `Bearer ${token}` } : {},
            });
            setHistory(prev => prev.filter(h => h.id !== id));
            if (selectedEntry?.id === id) setSelectedEntry(null);
        } catch (e) { /* ignore */ }
    };

    const handleClearAll = async () => {
        if (!window.confirm('Supprimer tout l\'historique ?')) return;
        for (const entry of history) {
            try {
                const token = localStorage.getItem('yelmon_token');
                await fetch(`/api/history/${entry.id}`, {
                    method: 'DELETE',
                    headers: token ? { Authorization: `Bearer ${token}` } : {},
                });
            } catch (e) { /* ignore */ }
        }
        setHistory([]);
        setSelectedEntry(null);
    };

    const formatDate = (ts) => {
        if (!ts) return '';
        const d = new Date(ts);
        return d.toLocaleDateString('fr-FR', {
            day: 'numeric', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit',
        });
    };

    const relativeTime = (ts) => {
        if (!ts) return '';
        const diff = Date.now() - ts;
        const mins = Math.floor(diff / 60000);
        if (mins < 1) return "à l'instant";
        if (mins < 60) return `il y a ${mins} min`;
        const hours = Math.floor(mins / 60);
        if (hours < 24) return `il y a ${hours}h`;
        const days = Math.floor(hours / 24);
        if (days < 7) return `il y a ${days}j`;
        return formatDate(ts);
    };

    const langIcons = { python: 'PY', javascript: 'JS', java: 'JV', cpp: 'CP', go: 'GO', rust: 'RS' };
    const langColors = {
        python: '#3776ab',
        javascript: '#f7df1e',
        java: '#ed8b00',
        cpp: '#00599c',
        go: '#00add8',
        rust: '#dea584',
    };

    const filteredHistory = history.filter(entry => {
        if (filter !== 'all' && entry.language !== filter) return false;
        if (search) {
            const q = search.toLowerCase();
            return (
                (entry.prompt || '').toLowerCase().includes(q) ||
                (entry.code || '').toLowerCase().includes(q) ||
                (entry.language || '').toLowerCase().includes(q)
            );
        }
        return true;
    });

    const stats = {
        total: history.length,
        languages: [...new Set(history.map(h => h.language))].length,
        today: history.filter(h => {
            const d = new Date(h.timestamp);
            const today = new Date();
            return d.toDateString() === today.toDateString();
        }).length,
    };

    return (
        <div className="historique-page">
            <div className="historique-container">
                <button onClick={() => navigate('/')} className="historique-back">
                    ← Retour au tableau de bord
                </button>

                <div className="historique-header">
                    <div>
                        <h1>Historique</h1>
                        <p className="historique-subtitle">
                            Toutes vos générations de code, classées par date
                        </p>
                    </div>
                    {history.length > 0 && (
                        <button className="historique-clear-btn" onClick={handleClearAll}>
                            ✕ Tout supprimer
                        </button>
                    )}
                </div>

                {/* Stats */}
                <div className="historique-stats">
                    <div className="stat-card">
                        <div className="stat-number">{stats.total}</div>
                        <div className="stat-label">Générations</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-number">{stats.languages}</div>
                        <div className="stat-label">Langages</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-number">{stats.today}</div>
                        <div className="stat-label">Aujourd'hui</div>
                    </div>
                </div>

                {/* Search */}
                <div className="historique-search">
                    <input
                        type="text"
                        placeholder="Rechercher dans l'historique..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>

                {/* Filters */}
                <div className="historique-filters">
                    {['all', 'python', 'javascript', 'java', 'cpp', 'go', 'rust'].map(f => (
                        <button
                            key={f}
                            className={`filter-btn ${filter === f ? 'active' : ''}`}
                            onClick={() => setFilter(f)}
                        >
                            {f === 'all' ? 'Tous' : f.toUpperCase()}
                            <span className="filter-count">
                                {f === 'all' ? history.length : history.filter(h => h.language === f).length}
                            </span>
                        </button>
                    ))}
                </div>

                {/* History List */}
                {loading ? (
                    <div className="historique-loading">
                        <div className="loader"></div>
                        <p>Chargement de l'historique...</p>
                    </div>
                ) : filteredHistory.length === 0 ? (
                    <div className="historique-empty">
                        <div className="empty-icon">📜</div>
                        <h3>Aucun historique</h3>
                        <p>
                            {search
                                ? 'Aucun résultat pour cette recherche.'
                                : 'Vos générations de code apparaîtront ici.'}
                        </p>
                        {!search && (
                            <button className="empty-btn" onClick={() => navigate('/')}>
                                Commencer à coder
                            </button>
                        )}
                    </div>
                ) : (
                    <div className="historique-list">
                        {filteredHistory.map(entry => (
                            <div
                                key={entry.id}
                                className={`history-card ${selectedEntry?.id === entry.id ? 'selected' : ''}`}
                                onClick={() => setSelectedEntry(selectedEntry?.id === entry.id ? null : entry)}
                            >
                                <div className="card-header">
                                    <span
                                        className="card-lang-badge"
                                        style={{ background: langColors[entry.language] || '#666' }}
                                    >
                                        {langIcons[entry.language] || '?'}
                                    </span>
                                    <span className="card-prompt">
                                        {entry.prompt || 'Sans description'}
                                    </span>
                                    <span className="card-time">{relativeTime(entry.timestamp)}</span>
                                </div>
                                {selectedEntry?.id === entry.id && (
                                    <div className="card-detail">
                                        <div className="detail-row">
                                            <span className="detail-label">Langage</span>
                                            <span className="detail-value">{entry.language}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="detail-label">Date</span>
                                            <span className="detail-value">{formatDate(entry.timestamp)}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="detail-label">Statut</span>
                                            <span className={`detail-value ${entry.success ? 'success' : 'error'}`}>
                                                {entry.success ? '✓ Succès' : '✕ Échec'}
                                            </span>
                                        </div>
                                        {entry.output && (
                                            <div className="detail-output">
                                                <span className="detail-label">Sortie</span>
                                                <pre>{entry.output}</pre>
                                            </div>
                                        )}
                                        {entry.code && (
                                            <div className="detail-code">
                                                <div className="detail-code-header">
                                                    <span className="detail-label">Code généré</span>
                                                    <div>
                                                        <button
                                                            className="detail-btn"
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                setExpandedCode(expandedCode === entry.id ? null : entry.id);
                                                            }}
                                                        >
                                                            {expandedCode === entry.id ? 'Réduire' : 'Voir le code'}
                                                        </button>
                                                        <button
                                                            className="detail-btn copy"
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                navigator.clipboard.writeText(entry.code);
                                                            }}
                                                        >
                                                            Copier
                                                        </button>
                                                    </div>
                                                </div>
                                                {expandedCode === entry.id && (
                                                    <pre className="code-block">{entry.code}</pre>
                                                )}
                                            </div>
                                        )}
                                        <div className="detail-actions">
                                            <button
                                                className="detail-btn use"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    navigate('/');
                                                }}
                                            >
                                                Réutiliser
                                            </button>
                                            <button
                                                className="detail-btn delete"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleDelete(entry.id);
                                                }}
                                            >
                                                Supprimer
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default Historique;
