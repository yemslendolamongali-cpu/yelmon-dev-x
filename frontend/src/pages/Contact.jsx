// © 2026 Yems junior lendola — All Rights Reserved.
// PROPRIETARY SOFTWARE — Unauthorized copying, distribution, reverse
// engineering, or reproduction of this code is strictly prohibited.

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Contact.css';

const CREATOR_EMAIL = 'yemsjuniorlendola@gmail.com';

function Contact() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [name, setName] = useState(user?.display_name || user?.username || '');
    const [email, setEmail] = useState(user?.email || '');
    const [subject, setSubject] = useState('');
    const [message, setMessage] = useState('');
    const [sending, setSending] = useState(false);
    const [sent, setSent] = useState(false);
    const [error, setError] = useState('');

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
            const res = await fetch('/api/contact', {
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
                setName('');
                setEmail('');
                setSubject('');
                setMessage('');
            } else {
                setError(data.error || 'Une erreur est survenue.');
            }
        } catch (err) {
            setError('Impossible d\'envoyer le message. Vérifiez votre connexion.');
        } finally {
            setSending(false);
        }
    };

    return (
        <div className="contact-page">
            <div className="contact-container">
                <button onClick={() => navigate('/')} className="contact-back">
                    ← Retour au tableau de bord
                </button>

                <div className="contact-header">
                    <div className="contact-header-icon">✉</div>
                    <h1>Contacter le créateur</h1>
                    <p className="contact-subtitle">
                        Une question, un bug, une suggestion ? Envoyez un message directement à l'équipe YELMON.
                    </p>
                </div>

                <div className="contact-grid">
                    {/* Form */}
                    <div className="contact-form-card">
                        <h2>Envoyer un message</h2>
                        {sent ? (
                            <div className="contact-success">
                                <div className="success-icon">✓</div>
                                <h3>Message envoyé !</h3>
                                <p>Merci pour votre message. Le créateur vous répondra dès que possible.</p>
                                <button className="success-btn" onClick={() => setSent(false)}>
                                    Envoyer un autre message
                                </button>
                            </div>
                        ) : (
                            <form onSubmit={handleSubmit}>
                                {error && <div className="contact-error">{error}</div>}
                                <div className="field">
                                    <label>Nom *</label>
                                    <input
                                        type="text"
                                        placeholder="Votre nom"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        required
                                    />
                                </div>
                                <div className="field">
                                    <label>Email *</label>
                                    <input
                                        type="email"
                                        placeholder="votre@email.com"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                    />
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
                                    <textarea
                                        placeholder="Décrivez votre demande en détail..."
                                        value={message}
                                        onChange={(e) => setMessage(e.target.value)}
                                        rows={6}
                                        required
                                    />
                                </div>
                                <button type="submit" className="contact-submit" disabled={sending}>
                                    {sending ? 'Envoi en cours...' : 'Envoyer le message'}
                                </button>
                            </form>
                        )}
                    </div>

                    {/* Info */}
                    <div className="contact-info-card">
                        <h2>Infos de contact</h2>
                        <div className="info-item">
                            <span className="info-icon">📧</span>
                            <div>
                                <span className="info-label">Email</span>
                                <a href={`mailto:${CREATOR_EMAIL}`} className="info-value link">
                                    {CREATOR_EMAIL}
                                </a>
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
                            <a href="https://github.com/yemsgithub" target="_blank" rel="noopener noreferrer" className="info-link">
                                GitHub
                            </a>
                            <a href={`mailto:${CREATOR_EMAIL}`} className="info-link">
                                Email direct
                            </a>
                        </div>

                        <div className="info-divider"></div>

                        <div className="info-note">
                            <p>
                                Merci de ne pas envoyer de données sensibles (mots de passe, clés API…)
                                via ce formulaire. Pour les questions de sécurité, contactez directement par email.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Contact;
