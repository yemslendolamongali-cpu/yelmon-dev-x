// frontend/src/pages/About.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './About.css';

const APP_NAME = 'YELMON Dev X';
const APP_VERSION = '1.0.0';

function About() {
    const navigate = useNavigate();
    const [appInfo, setAppInfo] = useState(null);

    useEffect(() => {
        fetch('/api/app/info')
            .then(res => res.json())
            .then(data => setAppInfo(data))
            .catch(() => {});
    }, []);

    return (
        <div className="about-page">
            <div className="about-container">
                <button onClick={() => navigate('/')} className="back-btn">
                     Retour
                </button>

                <div className="about-header">
                    <div className="about-logo"></div>
                    <h1>YELMON Dev X</h1>
                    <p className="about-version">Version {appInfo?.version || APP_VERSION}</p>
                </div>

                <div className="about-content">
                    <div className="about-section">
                        <h2> Assistant de Codage IA</h2>
                        <p>
                            YELMON Dev X est un assistant de codage intelligent utilisant
                            l'intelligence artificielle pour générer, analyser et optimiser
                            votre code dans plusieurs langages de programmation.
                        </p>
                    </div>

                    <div className="about-section">
                        <h3> Fonctionnalités</h3>
                        <ul className="features-list">
                            <li> Génération de code par IA</li>
                            <li> Auto-correction et optimisation</li>
                            <li> Recherche sémantique de code</li>
                            <li> Exécution en sandbox</li>
                            <li> Sauvegarde de snippets</li>
                            <li> Support multi-langages</li>
                            <li> Authentification sécurisée</li>
                            <li> Statistiques personnalisées</li>
                        </ul>
                    </div>

                    <div className="about-section">
                        <h3> Langages supportés</h3>
                        <div className="tech-stack">
                            <span className="tech-badge">Python</span>
                            <span className="tech-badge">JavaScript</span>
                            <span className="tech-badge">Java</span>
                            <span className="tech-badge">C++</span>
                            <span className="tech-badge">Go</span>
                            <span className="tech-badge">Rust</span>
                        </div>
                    </div>

                    <div className="about-section">
                        <h3> Technologies</h3>
                        <div className="tech-stack">
                            <span className="tech-badge">PyTorch</span>
                            <span className="tech-badge">React</span>
                            <span className="tech-badge">Electron</span>
                            <span className="tech-badge">Flask</span>
                            <span className="tech-badge">WebSocket</span>
                            <span className="tech-badge">JWT</span>
                        </div>
                    </div>

                    <div className="about-footer">
                        <p>© 2026 YELMON Team. Tous droits réservés.</p>
                        <p className="about-motto">"Codez plus vite, codez mieux avec YELMON Dev X"</p>
                        <button onClick={() => navigate('/account')} className="about-account-btn">
                            👤 Gérer mon compte
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default About;
