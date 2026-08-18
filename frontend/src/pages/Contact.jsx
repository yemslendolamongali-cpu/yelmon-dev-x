// © 2026 Yems junior lendola — All Rights Reserved.
// PROPRIETARY SOFTWARE — Unauthorized copying, distribution, reverse
// engineering, or reproduction of this code is strictly prohibited.

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Contact.css';

const API = 'https://yelmon-dev-x.onrender.com';
const CREATOR_EMAIL = 'yemsjuniorlendola@gmail.com';
const ADMIN_USERNAMES = ['yems', "01yem's"];

function Contact() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const isAdmin = ADMIN_USERNAMES.includes(user?.username);

    // User form state
    const [name, setName] = useState(user?.display_name || user?.username || '');
    const [email, setEmail] = useState(user?.email || '');
    const [subject, setSubject] = useState('');
    const [message, setMessage] = useState('');
    const [sending, setSending] = useState(false);
    const [sent, setSent] = useState(false);
    const [error, setError] = useState('');

    // Tab state
    const [tab, setTab] = useState(isAdmin ? 'inbox' : 'inbox');

    // Inbox state (admin + user)
    const [messages, setMessages] = useState([]);
    const [loadingMessages, setLoadingMessages] = useState(false);
    const [selectedMsg, setSelectedMsg] = useState(null);

    // Admin reply state
    const [replyText, setReplyText] = useState('');
    const [replying, setReplying] = useState(false);
    const [replySent, setReplySent] = useState(false);

    const loadMessages = useCallback(async () => {
        setLoadingMessages(true);
        try {
            const token = localStorage.getItem('yelmon_token');
            const url = isAdmin ? `${API}/api/contact` : `${API}/api/contact/my`;
            const r = await fetch(url, {
                headers: token ? { Authorization: `Bearer ${token}` } : {},
            });
            const d = await r.json();
            setMessages(d.messages || []);
        } catch { setMessages([]); }
        setLoadingMessages(false);
    }, [isAdmin]);

    useEffect(() => {
        loadMessages();
    }, [loadMessages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        if (!name.trim() || !email.trim() || !subject.trim() || !message.trim()) {
            setError('Tous les champs sont requis.');
            return;
        }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            setError('Adresse email invalide.');
            return;
        }
        setSending(true);
        try {
            const token = localStorage.getItem('yelmon_token');
            const res = await fetch(`${API}/api/contact`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {}),
                },
                body: JSON.stringify({ name: name.trim(), email: email.trim(), subject: subject.trim(), message: message.trim() }),
            });
            const data = await res.json();
            if (res.ok && data.ok) {
                setSent(true);
                setSubject('');
                setMessage('');
                loadMessages();
            } else {
                setError(data.error || 'Une erreur est survenue.');
            }
        } catch {
            setError('Impossible d\'envoyer le message.');
        } finally {
            setSending(false);
        }
    };

    const handleReply = async (msgId) => {
        if (!replyText.trim()) return;
        setReplying(true);
        try {
            const token = localStorage.getItem('yelmon_token');
            const r = await fetch(`${API}/api/contact/${msgId}/reply`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {}),
                },
                body: JSON.stringify({ reply: replyText.trim() }),
            });
            const d = await r.json();
            if (d.ok) {
                setReplySent(true);
                setReplyText('');
                loadMessages();
                setTimeout(() => { setReplySent(false); setSelectedMsg(null); }, 1500);
            }
        } catch {}
        setReplying(false);
    };

    const markRead = async (msgId) => {
        const token = localStorage.getItem('yelmon_token');
        const endpoint = isAdmin ? 'read' : 'user-read';
        await fetch(`${API}/api/contact/${msgId}/${endpoint}`, {
            method: 'POST',
            headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        loadMessages();
    };

    const deleteMessage = async (msgId) => {
        const token = localStorage.getItem('yelmon_token');
        await fetch(`${API}/api/contact/${msgId}`, {
            method: 'DELETE',
            headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        setSelectedMsg(null);
        loadMessages();
    };

    const formatDate = (ts) => {
        if (!ts) return '';
        return new Date(ts).toLocaleDateString('fr-FR', {
            day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
        });
    };

    const subjectLabels = { bug: 'Bug', feature: 'Suggestion', question: 'Question', feedback: 'Feedback', collaboration: 'Collaboration', other: 'Autre' };
    const unread = messages.filter(m => !m.read).length;
    const unreadUser = messages.filter(m => m.reply && !m.user_read).length;

    // ─── Admin Inbox ───
    if (isAdmin) {
        return (
            <div className="contact-page">
                <div className="contact-container">
                    <button onClick={() => navigate('/')} className="contact-back">← Retour au tableau de bord</button>

                    <div className="contact-header">
                        <div className="contact-header-icon">📬</div>
                        <h1>Boîte de réception</h1>
                        <p className="contact-subtitle">
                            Messages et plaintes des utilisateurs — vous pouvez répondre directement
                        </p>
                    </div>

                    <div className="admin-tabs">
                        <button className={`admin-tab ${tab === 'inbox' ? 'active' : ''}`} onClick={() => setTab('inbox')}>
                            📥 Boîte de réception {unread > 0 && <span className="unread-badge">{unread}</span>}
                        </button>
                        <button className={`admin-tab ${tab === 'send' ? 'active' : ''}`} onClick={() => setTab('send')}>
                            ✉ Envoyer un message
                        </button>
                    </div>

                    {tab === 'inbox' ? (
                        <div className="inbox-layout">
                            <div className="inbox-list">
                                {loadingMessages ? (
                                    <p className="inbox-empty">Chargement...</p>
                                ) : messages.length === 0 ? (
                                    <div className="inbox-empty">
                                        <div className="empty-icon">📭</div>
                                        <p>Aucun message</p>
                                    </div>
                                ) : (
                                    messages.map(m => (
                                        <div
                                            key={m.id}
                                            className={`inbox-item ${!m.read ? 'unread' : ''} ${selectedMsg?.id === m.id ? 'selected' : ''}`}
                                            onClick={() => { setSelectedMsg(m); if (!m.read) markRead(m.id); }}
                                        >
                                            <div className="inbox-item-top">
                                                <span className="inbox-from">{m.name}</span>
                                                <span className="inbox-time">{formatDate(m.timestamp)}</span>
                                            </div>
                                            <div className="inbox-subject">{subjectLabels[m.subject] || m.subject}</div>
                                            <div className="inbox-preview">{m.message.slice(0, 80)}...</div>
                                            {m.reply && <div className="inbox-replied-badge">✅ Répondu</div>}
                                            {!m.read && <div className="inbox-unread-dot" />}
                                        </div>
                                    ))
                                )}
                            </div>

                            <div className="inbox-detail">
                                {selectedMsg ? (
                                    <>
                                        <div className="detail-header">
                                            <div>
                                                <h3>{selectedMsg.name}</h3>
                                                <span className="detail-email">{selectedMsg.email}</span>
                                            </div>
                                            <div className="detail-actions">
                                                <button className="detail-delete" onClick={() => deleteMessage(selectedMsg.id)}>🗑 Supprimer</button>
                                            </div>
                                        </div>
                                        <div className="detail-meta">
                                            <span className={`detail-subject ${selectedMsg.subject}`}>{subjectLabels[selectedMsg.subject] || selectedMsg.subject}</span>
                                            <span className="detail-date">{formatDate(selectedMsg.timestamp)}</span>
                                        </div>
                                        <div className="detail-message">{selectedMsg.message}</div>

                                        {selectedMsg.reply ? (
                                            <div className="detail-reply-box admin-reply">
                                                <div className="reply-label">Votre réponse :</div>
                                                <p>{selectedMsg.reply}</p>
                                                <span className="reply-date">Répondu le {formatDate(selectedMsg.replied_at)}</span>
                                            </div>
                                        ) : (
                                            <div className="detail-reply-form">
                                                <h4>Répondre à {selectedMsg.name}</h4>
                                                {replySent && <div className="reply-success">✅ Réponse envoyée !</div>}
                                                <textarea
                                                    placeholder="Écrivez votre réponse ici..."
                                                    value={replyText}
                                                    onChange={(e) => setReplyText(e.target.value)}
                                                    rows={4}
                                                />
                                                <button
                                                    className="reply-submit"
                                                    onClick={() => handleReply(selectedMsg.id)}
                                                    disabled={replying || !replyText.trim()}
                                                >
                                                    {replying ? 'Envoi...' : '📤 Envoyer la réponse'}
                                                </button>
                                            </div>
                                        )}
                                    </>
                                ) : (
                                    <div className="inbox-empty">
                                        <div className="empty-icon">👈</div>
                                        <p>Sélectionnez un message pour le lire</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="contact-grid">
                            <div className="contact-form-card">
                                <h2>Envoyer un message</h2>
                                {sent ? (
                                    <div className="contact-success">
                                        <div className="success-icon">✓</div>
                                        <h3>Message envoyé !</h3>
                                        <button className="success-btn" onClick={() => setSent(false)}>Envoyer un autre</button>
                                    </div>
                                ) : (
                                    <form onSubmit={handleSubmit}>
                                        {error && <div className="contact-error">{error}</div>}
                                        <div className="field">
                                            <label>Nom *</label>
                                            <input type="text" placeholder="Votre nom" value={name} onChange={(e) => setName(e.target.value)} required />
                                        </div>
                                        <div className="field">
                                            <label>Email *</label>
                                            <input type="email" placeholder="votre@email.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
                                        </div>
                                        <div className="field">
                                            <label>Sujet *</label>
                                            <select value={subject} onChange={(e) => setSubject(e.target.value)} required>
                                                <option value="">Choisir un sujet...</option>
                                                <option value="bug">Signaler un bug</option>
                                                <option value="feature">Suggestion</option>
                                                <option value="question">Question</option>
                                                <option value="feedback">Feedback</option>
                                                <option value="collaboration">Collaboration</option>
                                                <option value="other">Autre</option>
                                            </select>
                                        </div>
                                        <div className="field">
                                            <label>Message *</label>
                                            <textarea placeholder="Décrivez..." value={message} onChange={(e) => setMessage(e.target.value)} rows={6} required />
                                        </div>
                                        <button type="submit" className="contact-submit" disabled={sending}>
                                            {sending ? 'Envoi...' : 'Envoyer le message'}
                                        </button>
                                    </form>
                                )}
                            </div>
                            <div className="contact-info-card">
                                <h2>Infos de contact</h2>
                                <div className="info-item">
                                    <span className="info-icon">📧</span>
                                    <div>
                                        <span className="info-label">Email</span>
                                        <a href={`mailto:${CREATOR_EMAIL}`} className="info-value link">{CREATOR_EMAIL}</a>
                                    </div>
                                </div>
                                <div className="info-item">
                                    <span className="info-icon">🌍</span>
                                    <div>
                                        <span className="info-label">Localisation</span>
                                        <span className="info-value">Kinshasa, RDC</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    // ─── Regular User View ───
    return (
        <div className="contact-page">
            <div className="contact-container">
                <button onClick={() => navigate('/')} className="contact-back">← Retour au tableau de bord</button>

                <div className="contact-header">
                    <div className="contact-header-icon">✉</div>
                    <h1>Contacter le créateur</h1>
                    <p className="contact-subtitle">
                        Une question, un bug, une suggestion ? Envoyez un message et consultez les réponses.
                    </p>
                </div>

                <div className="admin-tabs">
                    <button className={`admin-tab ${tab === 'inbox' ? 'active' : ''}`} onClick={() => { setTab('inbox'); loadMessages(); }}>
                        📨 Mes messages {unreadUser > 0 && <span className="unread-badge">{unreadUser}</span>}
                    </button>
                    <button className={`admin-tab ${tab === 'send' ? 'active' : ''}`} onClick={() => setTab('send')}>
                        ✉ Nouveau message
                    </button>
                </div>

                {tab === 'inbox' ? (
                    <div className="inbox-layout">
                        <div className="inbox-list">
                            {loadingMessages ? (
                                <p className="inbox-empty">Chargement...</p>
                            ) : messages.length === 0 ? (
                                <div className="inbox-empty">
                                    <div className="empty-icon">📭</div>
                                    <p>Aucun message envoyé</p>
                                    <p className="inbox-empty-hint">Envoyez un message pour voir les réponses ici</p>
                                </div>
                            ) : (
                                messages.map(m => (
                                    <div
                                        key={m.id}
                                        className={`inbox-item ${m.reply && !m.user_read ? 'unread' : ''} ${selectedMsg?.id === m.id ? 'selected' : ''}`}
                                        onClick={() => { setSelectedMsg(m); if (m.reply && !m.user_read) markRead(m.id); }}
                                    >
                                        <div className="inbox-item-top">
                                            <span className="inbox-from">{subjectLabels[m.subject] || m.subject}</span>
                                            <span className="inbox-time">{formatDate(m.timestamp)}</span>
                                        </div>
                                        <div className="inbox-preview">{m.message.slice(0, 80)}...</div>
                                        {m.reply ? (
                                            <div className="inbox-replied-badge">💬 Réponse de l'admin</div>
                                        ) : (
                                            <div className="inbox-pending-badge">⏳ En attente de réponse</div>
                                        )}
                                        {m.reply && !m.user_read && <div className="inbox-unread-dot" />}
                                    </div>
                                ))
                            )}
                        </div>

                        <div className="inbox-detail">
                            {selectedMsg ? (
                                <>
                                    <div className="detail-header">
                                        <div>
                                            <h3>Votre message</h3>
                                            <span className="detail-date">{formatDate(selectedMsg.timestamp)}</span>
                                        </div>
                                    </div>
                                    <div className="detail-meta">
                                        <span className={`detail-subject ${selectedMsg.subject}`}>{subjectLabels[selectedMsg.subject] || selectedMsg.subject}</span>
                                    </div>
                                    <div className="detail-message">{selectedMsg.message}</div>

                                    {selectedMsg.reply ? (
                                        <div className="detail-reply-box user-reply">
                                            <div className="reply-label">💬 Réponse de l'administrateur :</div>
                                            <p>{selectedMsg.reply}</p>
                                            <span className="reply-date">Reçu le {formatDate(selectedMsg.replied_at)}</span>
                                        </div>
                                    ) : (
                                        <div className="detail-pending-box">
                                            <div className="pending-icon">⏳</div>
                                            <p>En attente de réponse de l'administrateur...</p>
                                            <p className="pending-sub">Le créateur vous répondra dès que possible.</p>
                                        </div>
                                    )}
                                </>
                            ) : (
                                <div className="inbox-empty">
                                    <div className="empty-icon">👈</div>
                                    <p>Sélectionnez un message pour le lire</p>
                                </div>
                            )}
                        </div>
                    </div>
                ) : (
                    <div className="contact-grid">
                        <div className="contact-form-card">
                            <h2>Envoyer un message</h2>
                            {sent ? (
                                <div className="contact-success">
                                    <div className="success-icon">✓</div>
                                    <h3>Message envoyé !</h3>
                                    <p>Merci pour votre message. Le créateur vous répondra dès que possible.</p>
                                    <p className="success-hint">Vous verrez la réponse dans l'onglet "📨 Mes messages".</p>
                                    <button className="success-btn" onClick={() => setSent(false)}>Envoyer un autre message</button>
                                </div>
                            ) : (
                                <form onSubmit={handleSubmit}>
                                    {error && <div className="contact-error">{error}</div>}
                                    <div className="field">
                                        <label>Nom *</label>
                                        <input type="text" placeholder="Votre nom" value={name} onChange={(e) => setName(e.target.value)} required />
                                    </div>
                                    <div className="field">
                                        <label>Email *</label>
                                        <input type="email" placeholder="votre@email.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
                                    </div>
                                    <div className="field">
                                        <label>Sujet *</label>
                                        <select value={subject} onChange={(e) => setSubject(e.target.value)} required>
                                            <option value="">Choisir un sujet...</option>
                                            <option value="bug">Signaler un bug</option>
                                            <option value="feature">Suggestion de fonctionnalité</option>
                                            <option value="question">Question</option>
                                            <option value="feedback">Feedback / Avis</option>
                                            <option value="collaboration">Collaboration</option>
                                            <option value="other">Autre</option>
                                        </select>
                                    </div>
                                    <div className="field">
                                        <label>Message *</label>
                                        <textarea placeholder="Décrivez votre demande en détail..." value={message} onChange={(e) => setMessage(e.target.value)} rows={6} required />
                                    </div>
                                    <button type="submit" className="contact-submit" disabled={sending}>
                                        {sending ? 'Envoi en cours...' : 'Envoyer le message'}
                                    </button>
                                </form>
                            )}
                        </div>

                        <div className="contact-info-card">
                            <h2>Infos de contact</h2>
                            <div className="info-item">
                                <span className="info-icon">📧</span>
                                <div>
                                    <span className="info-label">Email</span>
                                    <a href={`mailto:${CREATOR_EMAIL}`} className="info-value link">{CREATOR_EMAIL}</a>
                                </div>
                            </div>
                            <div className="info-item">
                                <span className="info-icon">🌍</span>
                                <div>
                                    <span className="info-label">Localisation</span>
                                    <span className="info-value">Kinshasa, RDC</span>
                                </div>
                            </div>
                            <div className="info-item">
                                <span className="info-icon">⏱</span>
                                <div>
                                    <span className="info-label">Temps de réponse</span>
                                    <span className="info-value">24 – 72 heures</span>
                                </div>
                            </div>
                            <div className="info-divider"></div>
                            <h3>Liens utiles</h3>
                            <div className="info-links">
                                <a href="https://github.com/yemsgithub" target="_blank" rel="noopener noreferrer" className="info-link">GitHub</a>
                                <a href={`mailto:${CREATOR_EMAIL}`} className="info-link">Email direct</a>
                            </div>
                            <div className="info-divider"></div>
                            <div className="info-note">
                                <p>Merci de ne pas envoyer de données sensibles (mots de passe, clés API…) via ce formulaire.</p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Contact;
