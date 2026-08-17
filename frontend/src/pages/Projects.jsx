import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Projects.css';

function Projects() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [projects, setProjects] = useState([]);
    const [showCreate, setShowCreate] = useState(false);
    const [newName, setNewName] = useState('');
    const [newDesc, setNewDesc] = useState('');
    const [newLang, setNewLang] = useState('python');
    const [newType, setNewType] = useState('api');
    const [loading, setLoading] = useState(false);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        loadProjects();
    }, []);

    const loadProjects = () => {
        try {
            const saved = localStorage.getItem('yelmon_projects');
            if (saved) setProjects(JSON.parse(saved));
        } catch (e) { /* ignore */ }
    };

    const saveProjects = (list) => {
        setProjects(list);
        localStorage.setItem('yelmon_projects', JSON.stringify(list));
    };

    const handleCreate = () => {
        if (!newName.trim()) return;
        setLoading(true);
        const project = {
            id: Date.now().toString(36) + Math.random().toString(36).slice(2, 8),
            name: newName.trim(),
            description: newDesc.trim(),
            language: newLang,
            type: newType,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            author: user?.username || 'unknown',
            files: [],
            status: 'active',
        };
        const updated = [project, ...projects];
        saveProjects(updated);
        setNewName('');
        setNewDesc('');
        setShowCreate(false);
        setLoading(false);
    };

    const handleDelete = (id) => {
        const updated = projects.filter(p => p.id !== id);
        saveProjects(updated);
    };

    const handleStatus = (id, status) => {
        const updated = projects.map(p => p.id === id ? { ...p, status } : p);
        saveProjects(updated);
    };

    const filtered = filter === 'all' ? projects : projects.filter(p => p.status === filter);

    const langIcons = { python: 'PY', javascript: 'JS', java: 'JV', cpp: 'CP', go: 'GO', rust: 'RS' };
    const typeLabels = { api: 'API', web: 'Web App', mobile: 'Mobile', desktop: 'Desktop', cli: 'CLI', library: 'Bibliothèque', other: 'Autre' };

    const formatDate = (iso) => {
        const d = new Date(iso);
        return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' });
    };

    return (
        <div className="projects-page">
            <div className="projects-container">
                <button onClick={() => navigate('/')} className="projects-back">
                    ← Retour au tableau de bord
                </button>

                <div className="projects-header">
                    <div>
                        <h1>Mes Projets</h1>
                        <p className="projects-subtitle">
                            Créez et gérez vos projets de développement
                        </p>
                    </div>
                    <button className="projects-create-btn" onClick={() => setShowCreate(true)}>
                        + Nouveau Projet
                    </button>
                </div>

                {/* Create Modal */}
                {showCreate && (
                    <div className="projects-modal-overlay" onClick={() => setShowCreate(false)}>
                        <div className="projects-modal" onClick={(e) => e.stopPropagation()}>
                            <div className="modal-header">
                                <h2>Créer un nouveau projet</h2>
                                <button className="modal-close" onClick={() => setShowCreate(false)}>✕</button>
                            </div>
                            <div className="modal-body">
                                <div className="modal-field">
                                    <label>Nom du projet *</label>
                                    <input
                                        type="text"
                                        placeholder="Mon super projet"
                                        value={newName}
                                        onChange={(e) => setNewName(e.target.value)}
                                        autoFocus
                                    />
                                </div>
                                <div className="modal-field">
                                    <label>Description</label>
                                    <textarea
                                        placeholder="Décrivez brièvement votre projet..."
                                        value={newDesc}
                                        onChange={(e) => setNewDesc(e.target.value)}
                                        rows={3}
                                    />
                                </div>
                                <div className="modal-row">
                                    <div className="modal-field">
                                        <label>Langage</label>
                                        <select value={newLang} onChange={(e) => setNewLang(e.target.value)}>
                                            <option value="python">Python</option>
                                            <option value="javascript">JavaScript</option>
                                            <option value="java">Java</option>
                                            <option value="cpp">C++</option>
                                            <option value="go">Go</option>
                                            <option value="rust">Rust</option>
                                        </select>
                                    </div>
                                    <div className="modal-field">
                                        <label>Type</label>
                                        <select value={newType} onChange={(e) => setNewType(e.target.value)}>
                                            <option value="api">API</option>
                                            <option value="web">Web App</option>
                                            <option value="mobile">Mobile</option>
                                            <option value="desktop">Desktop</option>
                                            <option value="cli">CLI</option>
                                            <option value="library">Bibliothèque</option>
                                            <option value="other">Autre</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button className="modal-btn cancel" onClick={() => setShowCreate(false)}>Annuler</button>
                                <button className="modal-btn create" onClick={handleCreate} disabled={!newName.trim() || loading}>
                                    {loading ? 'Création...' : 'Créer le projet'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Filters */}
                <div className="projects-filters">
                    {['all', 'active', 'archived'].map(f => (
                        <button
                            key={f}
                            className={`filter-btn ${filter === f ? 'active' : ''}`}
                            onClick={() => setFilter(f)}
                        >
                            {f === 'all' ? 'Tous' : f === 'active' ? 'Actifs' : 'Archivés'}
                            <span className="filter-count">
                                {f === 'all' ? projects.length : projects.filter(p => p.status === f).length}
                            </span>
                        </button>
                    ))}
                </div>

                {/* Projects Grid */}
                {filtered.length === 0 ? (
                    <div className="projects-empty">
                        <div className="empty-icon">📁</div>
                        <h3>Aucun projet</h3>
                        <p>
                            {filter === 'all'
                                ? 'Créez votre premier projet pour commencer à coder.'
                                : 'Aucun projet dans cette catégorie.'}
                        </p>
                        {filter === 'all' && (
                            <button className="empty-btn" onClick={() => setShowCreate(true)}>
                                + Créer un projet
                            </button>
                        )}
                    </div>
                ) : (
                    <div className="projects-grid">
                        {filtered.map(project => (
                            <div key={project.id} className={`project-card ${project.status}`}>
                                <div className="card-top">
                                    <span className="card-lang">{langIcons[project.language] || '?'}</span>
                                    <span className="card-type">{typeLabels[project.type] || project.type}</span>
                                    <span className={`card-status ${project.status}`}>
                                        {project.status === 'active' ? '● Actif' : '◯ Archivé'}
                                    </span>
                                </div>
                                <h3 className="card-name">{project.name}</h3>
                                {project.description && (
                                    <p className="card-desc">{project.description}</p>
                                )}
                                <div className="card-meta">
                                    <span>Créé le {formatDate(project.created_at)}</span>
                                    <span>par {project.author}</span>
                                </div>
                                <div className="card-actions">
                                    {project.status === 'active' ? (
                                        <button className="card-btn archive" onClick={() => handleStatus(project.id, 'archived')}>
                                            Archiver
                                        </button>
                                    ) : (
                                        <button className="card-btn restore" onClick={() => handleStatus(project.id, 'active')}>
                                            Restaurer
                                        </button>
                                    )}
                                    <button className="card-btn delete" onClick={() => handleDelete(project.id)}>
                                        Supprimer
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default Projects;
