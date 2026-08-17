import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

function Login() {
    const navigate = useNavigate();
    const { login } = useAuth();
    const [method, setMethod] = useState('username');
    const [identifier, setIdentifier] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const placeholders = {
        username: 'Votre nom d\'utilisateur',
        email: 'Votre adresse email',
        phone: 'Votre numéro de téléphone',
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await login(identifier, password);
            navigate('/');
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-bg" />
            <div className="auth-card">
                <div className="auth-logo">
                    <div className="auth-logo-mark">Y</div>
                </div>
                <h1>
                    YELMON <span>Dev X</span>
                </h1>
                <p className="auth-subtitle">Connectez-vous à votre espace</p>

                <div className="auth-tabs">
                    <button
                        className={`auth-tab ${method === 'username' ? 'active' : ''}`}
                        onClick={() => { setMethod('username'); setIdentifier(''); setError(''); }}
                    >
                        👤 Pseudo
                    </button>
                    <button
                        className={`auth-tab ${method === 'email' ? 'active' : ''}`}
                        onClick={() => { setMethod('email'); setIdentifier(''); setError(''); }}
                    >
                        ✉ Email
                    </button>
                    <button
                        className={`auth-tab ${method === 'phone' ? 'active' : ''}`}
                        onClick={() => { setMethod('phone'); setIdentifier(''); setError(''); }}
                    >
                        📱 Téléphone
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                    {error && <div className="auth-error">{error}</div>}

                    <div className="auth-field">
                        <label>
                            {method === 'username' && 'Nom d\'utilisateur'}
                            {method === 'email' && 'Adresse email'}
                            {method === 'phone' && 'Numéro de téléphone'}
                        </label>
                        <input
                            type={method === 'email' ? 'email' : method === 'phone' ? 'tel' : 'text'}
                            placeholder={placeholders[method]}
                            value={identifier}
                            onChange={(e) => setIdentifier(e.target.value)}
                            required
                            autoFocus
                        />
                    </div>

                    <div className="auth-field">
                        <label>Mot de passe</label>
                        <input
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button type="submit" className="auth-btn" disabled={loading}>
                        {loading ? 'Connexion...' : 'Se connecter'}
                    </button>
                </form>

                <div className="auth-divider">
                    <span>ou</span>
                </div>

                <div className="auth-alt-methods">
                    <p className="auth-alt-title">Se connecter avec</p>
                    <div className="auth-alt-buttons">
                        <button
                            className="auth-alt-btn"
                            onClick={() => { setMethod('email'); setIdentifier(''); setError(''); }}
                        >
                            ✉ Adresse email
                        </button>
                        <button
                            className="auth-alt-btn"
                            onClick={() => { setMethod('phone'); setIdentifier(''); setError(''); }}
                        >
                            📱 Numéro de téléphone
                        </button>
                    </div>
                </div>

                <div className="auth-links">
                    <p>
                        Pas encore de compte ?{' '}
                        <Link to="/signup" className="auth-link">Créer un compte</Link>
                    </p>
                </div>

                <div className="auth-footer">
                    <span className="auth-brand">YELMON Dev X</span> · v1.0.0
                </div>
            </div>
        </div>
    );
}

export default Login;
