import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

function Signup() {
    const navigate = useNavigate();
    const { signup } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [password2, setPassword2] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [showPassword2, setShowPassword2] = useState(false);
    const [email, setEmail] = useState('');
    const [phone, setPhone] = useState('');
    const [displayName, setDisplayName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        if (password !== password2) {
            setError('Les mots de passe ne correspondent pas');
            return;
        }
        if (password.length < 4) {
            setError('Le mot de passe doit faire au moins 4 caractères');
            return;
        }
        if (!email && !phone) {
            setError('Renseignez au moins un email ou un numéro de téléphone');
            return;
        }
        setLoading(true);
        try {
            await signup(username, password, { email, phone, displayName });
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
                <p className="auth-subtitle">Créez votre compte</p>

                <form onSubmit={handleSubmit} className="auth-form">
                    {error && <div className="auth-error">{error}</div>}

                    <div className="auth-field">
                        <label>Nom d'utilisateur *</label>
                        <input
                            type="text"
                            placeholder="Choisissez un pseudo"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            autoFocus
                        />
                    </div>

                    <div className="auth-field">
                        <label>Nom complet (optionnel)</label>
                        <input
                            type="text"
                            placeholder="Votre nom complet"
                            value={displayName}
                            onChange={(e) => setDisplayName(e.target.value)}
                        />
                    </div>

                    <div className="auth-field">
                        <label>Adresse email</label>
                        <input
                            type="email"
                            placeholder="vous@exemple.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>

                    <div className="auth-field">
                        <label>Numéro de téléphone</label>
                        <input
                            type="tel"
                            placeholder="+243 ... "
                            value={phone}
                            onChange={(e) => setPhone(e.target.value)}
                        />
                    </div>

                    <div className="auth-hint">
                        Renseignez au moins un email ou un téléphone pour pouvoir vous connecter autrement.
                    </div>

                    <div className="auth-field">
                        <label>Mot de passe *</label>
                        <div className="password-wrapper">
                            <input
                                type={showPassword ? 'text' : 'password'}
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                            <button
                                type="button"
                                className="password-toggle"
                                onClick={() => setShowPassword(!showPassword)}
                                tabIndex={-1}
                            >
                                {showPassword ? '🙈' : '👁'}
                            </button>
                        </div>
                    </div>

                    <div className="auth-field">
                        <label>Confirmer le mot de passe *</label>
                        <div className="password-wrapper">
                            <input
                                type={showPassword2 ? 'text' : 'password'}
                                placeholder="••••••••"
                                value={password2}
                                onChange={(e) => setPassword2(e.target.value)}
                                required
                            />
                            <button
                                type="button"
                                className="password-toggle"
                                onClick={() => setShowPassword2(!showPassword2)}
                                tabIndex={-1}
                            >
                                {showPassword2 ? '🙈' : '👁'}
                            </button>
                        </div>
                    </div>

                    <button type="submit" className="auth-btn" disabled={loading}>
                        {loading ? 'Création...' : "S'inscrire"}
                    </button>
                </form>

                <div className="auth-links">
                    <p>
                        Déjà un compte ?{' '}
                        <Link to="/login" className="auth-link">Se connecter</Link>
                    </p>
                </div>

                <div className="auth-footer">
                    <span className="auth-brand">YELMON Dev X</span> · v1.0.0
                </div>
            </div>
        </div>
    );
}

export default Signup;
