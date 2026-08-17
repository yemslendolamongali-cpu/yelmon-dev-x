// © 2026 Yems junior lendola — All Rights Reserved.
// PROPRIETARY SOFTWARE — Unauthorized copying, distribution, reverse
// engineering, or reproduction of this code is strictly prohibited.

// frontend/src/pages/Dashboard.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { javascript } from '@codemirror/lang-javascript';
import { java } from '@codemirror/lang-java';
import { cpp } from '@codemirror/lang-cpp';
import { go } from '@codemirror/lang-go';
import { rust } from '@codemirror/lang-rust';
import { oneDark } from '@codemirror/theme-one-dark';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import './Dashboard.css';
import '../styles/yelmon.css';

const APP_NAME = 'YELMON Dev X';

const LANGUAGES = {
    python: { name: 'Python', icon: 'PY' },
    javascript: { name: 'JavaScript', icon: 'JS' },
    java: { name: 'Java', icon: 'JV' },
    cpp: { name: 'C++', icon: 'CP' },
    go: { name: 'Go', icon: 'GO' },
    rust: { name: 'Rust', icon: 'RS' },
};

const languageExtensions = {
    python: python(),
    javascript: javascript(),
    java: java(),
    cpp: cpp(),
    go: go(),
    rust: rust(),
};

const DEFAULT_CODE = '// Code généré par YELMON Dev X\n// Décrivez votre besoin dans le chat';

function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

function loadConversations() {
    try {
        const saved = localStorage.getItem('yelmon_conversations');
        return saved ? JSON.parse(saved) : [];
    } catch { return []; }
}

function saveConversations(list) {
    localStorage.setItem('yelmon_conversations', JSON.stringify(list));
}

function Dashboard() {
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const { theme, switchTheme } = useTheme();
    const [language, setLanguage] = useState('python');
    const [prompt, setPrompt] = useState('');
    const [code, setCode] = useState(DEFAULT_CODE);
    const [output, setOutput] = useState('');
    const [loading, setLoading] = useState(false);
    const [history, setHistory] = useState([]);
    const [showPreview, setShowPreview] = useState(false);
    const messagesEndRef = useRef(null);

    const [conversations, setConversations] = useState(() => loadConversations());
    const [activeConvId, setActiveConvId] = useState(null);

    // Mobile state
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [mobileTab, setMobileTab] = useState('chat');

    const activeConv = conversations.find(c => c.id === activeConvId);
    const messages = activeConv ? activeConv.messages : [];

    useEffect(() => {
        loadHistory();
    }, []);

    useEffect(() => {
        saveConversations(conversations);
    }, [conversations]);

    const getLanguageMode = () => languageExtensions[language] || python();

    const createConversation = () => {
        const newConv = {
            id: generateId(),
            title: 'Nouvelle conversation',
            messages: [],
            language,
            created_at: Date.now(),
            updated_at: Date.now(),
        };
        setConversations(prev => [newConv, ...prev]);
        setActiveConvId(newConv.id);
        setCode(DEFAULT_CODE);
        setOutput('');
        setSidebarOpen(false);
    };

    const switchConversation = (id) => {
        setActiveConvId(id);
        const conv = conversations.find(c => c.id === id);
        if (conv) {
            setLanguage(conv.language || 'python');
            const lastAiMsg = [...conv.messages].reverse().find(m => m.role === 'ai' && m.code);
            setCode(lastAiMsg?.code || DEFAULT_CODE);
            setOutput('');
        }
        setSidebarOpen(false);
    };

    const deleteConversation = (id) => {
        setConversations(prev => prev.filter(c => c.id !== id));
        if (activeConvId === id) {
            setActiveConvId(null);
            setCode(DEFAULT_CODE);
            setOutput('');
        }
    };

    const addMessageToConversation = (role, content, extra = {}) => {
        if (!activeConvId) return;
        setConversations(prev => prev.map(c => {
            if (c.id !== activeConvId) return c;
            const newMsgs = [...c.messages, { role, content, timestamp: Date.now(), ...extra }];
            const title = c.messages.length === 0 && role === 'user'
                ? content.slice(0, 40) + (content.length > 40 ? '…' : '')
                : c.title;
            return { ...c, messages: newMsgs, title, updated_at: Date.now() };
        }));
    };

    const loadHistory = async () => {
        try {
            const res = await fetch('/api/history');
            if (res.ok) {
                const data = await res.json();
                setHistory(Array.isArray(data.history) ? data.history : []);
            }
        } catch (e) { /* backend indisponible */ }
    };

    const generateCode = async (promptText) => {
        if (!promptText.trim() || loading) return;
        if (!activeConvId) createConversation();
        setLoading(true);
        setOutput(' YELMON analyse votre demande...');
        addMessageToConversation('user', promptText);
        try {
            const res = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: promptText, language }),
            });
            const data = await res.json();
            if (data.error) {
                setOutput(` Erreur: ${data.error}`);
                addMessageToConversation('ai', `Erreur: ${data.error}`);
            } else {
                setCode(data.code || '');
                setOutput(data.output || '');
                addMessageToConversation('ai', 'Code généré', { code: data.code, language, output: data.output });
                setHistory(prev => [
                    { language, prompt: promptText, timestamp: Date.now(), success: true },
                    ...prev,
                ].slice(0, 50));
            }
        } catch (e) {
            setOutput(' Erreur de connexion au backend YELMON.');
            addMessageToConversation('ai', 'Erreur de connexion au backend.');
        } finally {
            setLoading(false);
        }
    };

    const executeCode = async () => {
        if (!code.trim()) return;
        setOutput(' Exécution du code...');
        try {
            const res = await fetch('/api/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, language }),
            });
            const data = await res.json();
            setOutput(data.output || data.error || '');
        } catch (e) {
            setOutput(" Erreur d'exécution.");
        }
    };

    const handleSendMessage = () => {
        if (!prompt.trim()) return;
        generateCode(prompt);
        setPrompt('');
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [history]);

    return (
        <div className={`sunrise-app ${sidebarOpen ? 'sidebar-open' : ''}`}>
            {/* MOBILE OVERLAY */}
            {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />}

            {/* SIDEBAR */}
            <aside className={`sunrise-panel sidebar ${sidebarOpen ? 'open' : ''}`}>
                <div className="sidebar-brand">
                    <div className="brand-mark">Y</div>
                    <div>
                        <h1>YELMON <span>Dev X</span></h1>
                        <small>CODING COMPANION</small>
                    </div>
                    <button className="sidebar-close-btn" onClick={() => setSidebarOpen(false)}>✕</button>
                </div>
                <nav className="sidebar-nav">
                    <div className="nav-item" onClick={createConversation}>
                        <span className="nav-icon">✦</span>
                        Nouvelle conversation
                    </div>
                    <div className="nav-item active">
                        <span className="nav-icon">⌁</span>
                        Tableau de bord
                    </div>
                    <div className="nav-item" onClick={() => navigate('/projects')}>
                        <span className="nav-icon">◆</span>
                        Projets
                    </div>
                    <div className="nav-item" onClick={() => navigate('/bibliotheque')}>
                        <span className="nav-icon">◗</span>
                        Bibliothèque
                    </div>
                    <div className="nav-item" onClick={() => navigate('/historique')}>
                        <span className="nav-icon">📜</span>
                        Historique
                    </div>
                    <div className="nav-item" onClick={() => setShowPreview(!showPreview)}>
                        <span className="nav-icon">▧</span>
                        Aperçu de l'app
                    </div>
                    <div className="nav-item" onClick={() => navigate('/about')}>
                        <span className="nav-icon">⚙</span>
                        Réglages
                    </div>
                    <div className="nav-item" onClick={() => navigate('/legal')}>
                        <span className="nav-icon">⚖</span>
                        Politique & Droits
                    </div>
                    <div className="nav-item" onClick={() => navigate('/contact')}>
                        <span className="nav-icon">✉</span>
                        Contacter
                    </div>
                    <div className="nav-item" onClick={() => navigate('/account')}>
                        <span className="nav-icon">👤</span>
                        Mon compte
                    </div>
                    <div className="nav-item" onClick={() => { logout(); navigate('/login'); }}>
                        <span className="nav-icon">🚪</span>
                        Se déconnecter
                    </div>
                </nav>
                <div className="sidebar-section">Conversations</div>
                {conversations.length === 0 ? (
                    <div className="sidebar-recent" style={{ opacity: 0.5 }}>Aucune conversation</div>
                ) : (
                    conversations.slice(0, 10).map(conv => (
                        <div
                            key={conv.id}
                            className={`sidebar-recent ${activeConvId === conv.id ? 'active-recent' : ''}`}
                            onClick={() => switchConversation(conv.id)}
                        >
                            <span className="recent-title">◆ {conv.title}</span>
                            <button
                                className="recent-delete"
                                onClick={(e) => { e.stopPropagation(); deleteConversation(conv.id); }}
                            >
                                ✕
                            </button>
                        </div>
                    ))
                )}
                <div className="theme-switcher">
                    <div className="theme-switcher-label">Apparence</div>
                    <div className="theme-buttons">
                        <button
                            className={`theme-btn ${theme === 'light' ? 'active' : ''}`}
                            onClick={() => switchTheme('light')}
                        >
                            <span className="theme-btn-icon">☀</span>
                            Clair
                        </button>
                        <button
                            className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
                            onClick={() => switchTheme('dark')}
                        >
                            <span className="theme-btn-icon">🌙</span>
                            Sombre
                        </button>
                        <button
                            className={`theme-btn ${theme === 'system' ? 'active' : ''}`}
                            onClick={() => switchTheme('system')}
                        >
                            <span className="theme-btn-icon">💻</span>
                            Système
                        </button>
                    </div>
                </div>

                <div className="sidebar-footer">
                    <div className="user-avatar">{user?.display_name?.[0]?.toUpperCase() || user?.username?.[0]?.toUpperCase() || 'U'}</div>
                    <div>
                        <b>{user?.display_name || user?.username || 'Utilisateur'}</b>
                        <small>{user?.role === 'admin' ? 'Administrateur' : 'Plan Pro'} · 40 j restants</small>
                    </div>
                </div>
            </aside>

            {/* CHAT */}
            <main className={`sunrise-panel chat-panel ${mobileTab === 'code' ? 'mobile-hidden' : ''}`}>
                <div className="chat-topbar">
                    <button className="hamburger-btn" onClick={() => setSidebarOpen(true)}>☰</button>
                    <div>
                        <h2>Assistant de code</h2>
                        <div className="sub">YELMON Dev X · modèle DevMax-3</div>
                    </div>
                    <div className="live-badge">
                        <span className="pulse"></span> EN LIGNE
                    </div>
                </div>

                <div className="messages-container">
                    {messages.length === 0 ? (
                        <div className="message ai-message">
                            <div className="avatar ai-avatar">Y</div>
                            <div className="bubble">
                                Salut {user?.username || 'Chris'} ! Je suis prêt. Dis-moi quel projet on attaque aujourd'hui.
                            </div>
                        </div>
                    ) : (
                        messages.map((msg, index) => (
                            <div key={index} className={`message ${msg.role === 'user' ? 'user-message' : 'ai-message'}`}>
                                <div className={`avatar ${msg.role === 'user' ? 'user-msg-avatar' : 'ai-avatar'}`}>
                                    {msg.role === 'user' ? 'U' : 'Y'}
                                </div>
                                <div className={`bubble ${msg.role === 'user' ? 'user-bubble' : ''}`}>
                                    {msg.content}
                                    {msg.code && (
                                        <div style={{ marginTop: '8px' }}>
                                            <span className="tag">🔥 {msg.language}</span>
                                            <span className="tag">📦 Généré</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))
                    )}

                    {loading && (
                        <div className="message ai-message">
                            <div className="avatar ai-avatar">Y</div>
                            <div className="bubble">
                                Analyse en cours…
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                <div className="input-area">
                    <div className="input-bar">
                        <input
                            type="text"
                            placeholder="Demandez n'importe quoi : code, debug, refactor…"
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                        />
                        <button className="send-btn" onClick={handleSendMessage}>➤</button>
                    </div>
                    <div className="hints">
                        <span>/api</span>
                        <span>/debug</span>
                        <span>/refactor</span>
                        <span>/explain</span>
                    </div>
                </div>
            </main>

            {/* CODE PANEL */}
            <aside className={`sunrise-panel code-panel ${mobileTab === 'chat' ? 'mobile-hidden' : ''}`}>
                <div className="code-tabs">
                    <div className="tab active">app.py</div>
                    <div className="tab">tests</div>
                </div>
                <div className="code-editor">
                    <CodeMirror
                        value={code}
                        onChange={(value) => setCode(value)}
                        extensions={[getLanguageMode()]}
                        theme={oneDark}
                        height="100%"
                        basicSetup={{
                            lineNumbers: true,
                            highlightActiveLineGutter: true,
                            highlightActiveLine: true,
                            foldGutter: true,
                            dropCursor: true,
                            allowMultipleSelections: true,
                            indentOnInput: true,
                            bracketMatching: true,
                            closeBrackets: true,
                            autocompletion: true,
                            rectangularSelection: true,
                            crosshairCursor: true,
                            highlightSelectionMatches: true,
                            closeBracketsKeymap: true,
                            defaultKeymap: true,
                            searchKeymap: true,
                            historyKeymap: true,
                            foldKeymap: true,
                            completionKeymap: true,
                            lintKeymap: true,
                        }}
                    />
                </div>
                <div className="code-actions">
                    <button className="action-btn primary" onClick={executeCode}>Exécuter</button>
                    <button className="action-btn ghost" onClick={() => navigator.clipboard.writeText(code)}>Copier</button>
                </div>
            </aside>

            {/* MOBILE BOTTOM NAV */}
            <nav className="mobile-bottom-nav">
                <button className={`bottom-nav-btn ${mobileTab === 'chat' ? 'active' : ''}`} onClick={() => setMobileTab('chat')}>
                    <span className="bnav-icon">💬</span>
                    <span className="bnav-label">Chat</span>
                </button>
                <button className={`bottom-nav-btn ${mobileTab === 'code' ? 'active' : ''}`} onClick={() => setMobileTab('code')}>
                    <span className="bnav-icon">⟨/⟩</span>
                    <span className="bnav-label">Code</span>
                </button>
                <button className="bottom-nav-btn" onClick={() => setSidebarOpen(true)}>
                    <span className="bnav-icon">☰</span>
                    <span className="bnav-label">Menu</span>
                </button>
            </nav>

            {/* FLOATING PREVIEW WINDOW */}
            {showPreview && (
                <div className="floating-window">
                    <div className="floating-header">
                        <span className="fdot red"></span>
                        <span className="fdot yellow"></span>
                        <span className="fdot green"></span>
                        <span className="floating-title">Aperçu · App</span>
                        <button className="close-btn" onClick={() => setShowPreview(false)}>✕</button>
                    </div>
                    <div className="phone-frame">
                        <div className="phone-screen">
                            <div className="phone-header">
                                <div className="phone-logo">Y</div>
                                <div>YELMON Dev X</div>
                            </div>
                            <div className="phone-content">
                                <div className="phone-message">
                                    <div className="phone-avatar">Y</div>
                                    <div className="phone-bubble">Bienvenue !</div>
                                </div>
                            </div>
                            <div className="phone-input">
                                <input placeholder="Tapez votre message..." readOnly />
                            </div>
                        </div>
                    </div>
                    <div className="floating-footer">YELMON Dev X · nouvelle fenêtre intégrée</div>
                </div>
            )}
        </div>
    );
}

export default Dashboard;
