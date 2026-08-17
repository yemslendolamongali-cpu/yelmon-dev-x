import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Account.css';

function Account() {
    const navigate = useNavigate();
    const { user, logout, deleteAccount } = useAuth();
    const [confirmDelete, setConfirmDelete] = useState(false);
    const [deleteText, setDeleteText] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const handleSwitchAccount = () => {
        logout();
        navigate('/login');
    };

    const handleDelete = async () => {
        if (deleteText !== user?.username) return;
        setError('');
        setLoading(true);
        try {
            await deleteAccount();
            navigate('/login');
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    return (
        <div className="account-page">
            <div className="account-container">
                <button onClick={() => navigate('/')} className="account-back">
                    ← Retour au tableau de bord
                </button>

                <div className="account-header">
                    <div className="account-avatar">
                        {user?.display_name?.[0]?.toUpperCase() || user?.username?.[0]?.toUpperCase() || 'U'}
                    </div>
                    <h1>Mon compte</h1>
                    <p className="account-username">{user?.display_name || user?.username || 'Utilisateur'}</p>
                    <div className="account-details">
                        <div className="account-detail-row">
                            <span className="detail-label">👤</span>
                            <span className="detail-value">@{user?.username}</span>
                        </div>
                        {user?.email && (
                            <div className="account-detail-row">
                                <span className="detail-label">✉</span>
                                <span className="detail-value">{user.email}</span>
                            </div>
                        )}
                        {user?.phone && (
                            <div className="account-detail-row">
                                <span className="detail-label">📱</span>
                                <span className="detail-value">{user.phone}</span>
                            </div>
                        )}
                        <div className="account-detail-row">
                            <span className="detail-label">🔑</span>
                            <span className="detail-value role-badge">{user?.role === 'admin' ? 'Administrateur' : 'Utilisateur'}</span>
                        </div>
                    </div>
                </div>

                <div className="account-sections">
                    {/* Changer de compte */}
                    <div className="account-card">
                        <div className="account-card-icon">🔄</div>
                        <div className="account-card-content">
                            <h3>Utiliser un autre compte</h3>
                            <p>Déconnectez-vous et connectez-vous avec un autre identifiant.</p>
                        </div>
                        <button className="account-btn switch" onClick={handleSwitchAccount}>
                            Changer de compte
                        </button>
                    </div>

                    {/* Déconnexion */}
                    <div className="account-card">
                        <div className="account-card-icon">🚪</div>
                        <div className="account-card-content">
                            <h3>Déconnexion</h3>
                            <p>Fermez votre session en toute sécurité.</p>
                        </div>
                        <button className="account-btn logout" onClick={handleLogout}>
                            Se déconnecter
                        </button>
                    </div>

                    {/* Supprimer le compte */}
                    <div className="account-card danger">
                        <div className="account-card-icon">⚠️</div>
                        <div className="account-card-content">
                            <h3>Supprimer mon compte</h3>
                            <p>
                                Cette action est <strong>irréversible</strong>. Toutes vos données
                                seront définitivement supprimées.
                            </p>
                        </div>
                        {!confirmDelete ? (
                            <button
                                className="account-btn delete"
                                onClick={() => setConfirmDelete(true)}
                            >
                                Supprimer
                            </button>
                        ) : (
                            <div className="delete-confirm">
                                <p>
                                    Tapez <strong>{user?.username}</strong> pour confirmer :
                                </p>
                                <input
                                    type="text"
                                    placeholder={user?.username}
                                    value={deleteText}
                                    onChange={(e) => setDeleteText(e.target.value)}
                                    autoFocus
                                />
                                {error && <div className="account-error">{error}</div>}
                                <div className="delete-actions">
                                    <button
                                        className="account-btn cancel"
                                        onClick={() => {
                                            setConfirmDelete(false);
                                            setDeleteText('');
                                            setError('');
                                        }}
                                    >
                                        Annuler
                                    </button>
                                    <button
                                        className="account-btn confirm-delete"
                                        onClick={handleDelete}
                                        disabled={deleteText !== user?.username || loading}
                                    >
                                        {loading ? 'Suppression...' : 'Confirmer la suppression'}
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                <div className="account-footer">
                    <span className="account-brand">YELMON Dev X</span> · v1.0.0
                </div>
            </div>
        </div>
    );
}

export default Account;
