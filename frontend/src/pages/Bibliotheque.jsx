import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Bibliotheque.css';

function Bibliotheque() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [snippets, setSnippets] = useState([]);
    const [search, setSearch] = useState('');
    const [langFilter, setLangFilter] = useState('all');
    const [selected, setSelected] = useState(null);

    useEffect(() => {
        loadSnippets();
    }, []);

    const loadSnippets = () => {
        try {
            const saved = localStorage.getItem('yelmon_snippets');
            if (saved) setSnippets(JSON.parse(saved));
        } catch (e) { /* ignore */ }
    };

    const saveSnippets = (list) => {
        setSnippets(list);
        localStorage.setItem('yelmon_snippets', JSON.stringify(list));
    };

    const handleDelete = (id) => {
        const updated = snippets.filter(s => s.id !== id);
        saveSnippets(updated);
        if (selected?.id === id) setSelected(null);
    };

    const handleCopy = (code) => {
        navigator.clipboard.writeText(code);
    };

    const filtered = snippets.filter(s => {
        const matchSearch = !search ||
            s.title?.toLowerCase().includes(search.toLowerCase()) ||
            s.code?.toLowerCase().includes(search.toLowerCase()) ||
            s.description?.toLowerCase().includes(search.toLowerCase());
        const matchLang = langFilter === 'all' || s.language === langFilter;
        return matchSearch && matchLang;
    });

    const langList = [...new Set(snippets.map(s => s.language).filter(Boolean))];
    const langLabels = { python: 'Python', javascript: 'JavaScript', java: 'Java', cpp: 'C++', go: 'Go', rust: 'Rust' };

    const formatDate = (iso) => {
        const d = new Date(iso);
        return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="biblio-page">
            <div className="biblio-container">
                <button onClick={() => navigate('/')} className="biblio-back">
                    ← Retour au tableau de bord
                </button>

                <div className="biblio-header">
                    <div>
                        <h1>Bibliothèque de Snippets</h1>
                        <p className="biblio-subtitle">
                            Vos extraits de code sauvegardés
                        </p>
                    </div>
                    <div className="biblio-stats">
                        <span className="stat-item">
                            <span className="stat-num">{snippets.length}</span> snippet{snippets.length !== 1 ? 's' : ''}
                        </span>
                    </div>
                </div>

                <div className="biblio-toolbar">
                    <input
                        type="text"
                        placeholder="Rechercher un snippet..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="biblio-search"
                    />
                    <div className="biblio-lang-filters">
                        <button
                            className={`lang-btn ${langFilter === 'all' ? 'active' : ''}`}
                            onClick={() => setLangFilter('all')}
                        >
                            Tous
                        </button>
                        {langList.map(lang => (
                            <button
                                key={lang}
                                className={`lang-btn ${langFilter === lang ? 'active' : ''}`}
                                onClick={() => setLangFilter(lang)}
                            >
                                {langLabels[lang] || lang}
                            </button>
                        ))}
                    </div>
                </div>

                {snippets.length === 0 ? (
                    <div className="biblio-empty">
                        <div className="empty-icon">📚</div>
                        <h3>Aucun snippet sauvegardé</h3>
                        <p>
                            Vos snippets seront automatiquement ajoutés ici
                            lorsque vous les sauvegarderez depuis le tableau de bord.
                        </p>
                    </div>
                ) : filtered.length === 0 ? (
                    <div className="biblio-empty">
                        <div className="empty-icon">🔍</div>
                        <h3>Aucun résultat</h3>
                        <p>Aucun snippet ne correspond à votre recherche.</p>
                    </div>
                ) : (
                    <div className="biblio-layout">
                        <div className="biblio-list">
                            {filtered.map(snippet => (
                                <div
                                    key={snippet.id}
                                    className={`biblio-card ${selected?.id === snippet.id ? 'selected' : ''}`}
                                    onClick={() => setSelected(snippet)}
                                >
                                    <div className="biblio-card-top">
                                        <span className="biblio-card-lang">{langLabels[snippet.language] || snippet.language}</span>
                                        <span className="biblio-card-date">{formatDate(snippet.created_at)}</span>
                                    </div>
                                    <h3 className="biblio-card-title">{snippet.title}</h3>
                                    {snippet.description && (
                                        <p className="biblio-card-desc">{snippet.description}</p>
                                    )}
                                </div>
                            ))}
                        </div>

                        {selected && (
                            <div className="biblio-detail">
                                <div className="detail-header">
                                    <h2>{selected.title}</h2>
                                    <div className="detail-actions">
                                        <button className="detail-btn copy" onClick={() => handleCopy(selected.code)}>
                                            Copier
                                        </button>
                                        <button className="detail-btn delete" onClick={() => handleDelete(selected.id)}>
                                            Supprimer
                                        </button>
                                    </div>
                                </div>
                                {selected.description && (
                                    <p className="detail-desc">{selected.description}</p>
                                )}
                                <div className="detail-meta">
                                    <span>Langage: {langLabels[selected.language] || selected.language}</span>
                                    <span>Créé le {formatDate(selected.created_at)}</span>
                                </div>
                                <pre className="detail-code">
                                    <code>{selected.code}</code>
                                </pre>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

export default Bibliotheque;
