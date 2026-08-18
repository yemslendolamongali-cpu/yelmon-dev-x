// © 2026 Yems junior lendola — All Rights Reserved.
// PROPRIETARY SOFTWARE — Unauthorized copying, distribution, reverse
// engineering, or reproduction of this code is strictly prohibited.

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './UpdateAdmin.css';

const API = '';

function useAdminApi(path, options = {}) {
    const { token } = useAuth();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const execute = useCallback(async (body) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch(`${API}${path}`, {
                method: options.method || 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: body ? JSON.stringify(body) : undefined,
            });
            const json = await resp.json();
            if (!resp.ok) throw new Error(json.error || 'Erreur');
            setData(json);
            return json;
        } catch (e) {
            setError(e.message);
            return null;
        } finally {
            setLoading(false);
        }
    }, [path, token]);

    return { data, loading, error, execute };
}

function UpdateAdmin() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [tab, setTab] = useState('actions');
    const [status, setStatus] = useState(null);
    const [polling, setPolling] = useState(false);

    const statusApi = useAdminApi('/api/admin/update/status');
    const buildApi = useAdminApi('/api/admin/update/build');
    const deployApi = useAdminApi('/api/admin/update/deploy');
    const pullApi = useAdminApi('/api/admin/update/pull');
    const fullApi = useAdminApi('/api/admin/update/full');
    const backupApi = useAdminApi('/api/admin/update/backup');
    const backupsApi = useAdminApi('/api/admin/update/backups');
    const gitLogApi = useAdminApi('/api/admin/update/git-log');
    const diskApi = useAdminApi('/api/admin/update/disk');

    const refreshStatus = useCallback(async () => {
        const s = await statusApi.execute();
        if (s) setStatus(s);
    }, []);

    useEffect(() => {
        refreshStatus();
    }, []);

    useEffect(() => {
        if (status?.current_task?.status === 'running') {
            setPolling(true);
            const iv = setInterval(async () => {
                await refreshStatus();
            }, 3000);
            return () => clearInterval(iv);
        } else {
            setPolling(false);
        }
    }, [status?.current_task?.status]);

    const loadTab = useCallback(async (t) => {
        setTab(t);
        if (t === 'git') await gitLogApi.execute();
        if (t === 'disk') await diskApi.execute();
        if (t === 'backups') await backupsApi.execute();
    }, []);

    const task = status?.current_task || {};
    const taskPct = task.progress || 0;

    return (
        <div className="update-admin-page">
            <div className="update-admin-bg" />
            <div className="update-admin-container">
                <div className="update-admin-header">
                    <div>
                        <h1>Mise à jour automatique</h1>
                        <div className="subtitle">
                            Cerveau moteur — Gestion du build, déploiement & mises à jour
                        </div>
                    </div>
                    <button className="back-btn" onClick={() => navigate('/')}>
                        ← Retour
                    </button>
                </div>

                <div className="status-grid">
                    <div className="status-card">
                        <div className="label">Version</div>
                        <div className="value">{status?.app_version || '—'}</div>
                    </div>
                    <div className="status-card">
                        <div className="label">Plateforme</div>
                        <div className="value">{status?.platform || '—'}</div>
                    </div>
                    <div className="status-card">
                        <div className="label">Python</div>
                        <div className={`value ${status?.python_version ? 'ok' : 'err'}`}>
                            {status?.python_version || '—'}
                        </div>
                    </div>
                    <div className="status-card">
                        <div className="label">Node.js</div>
                        <div className={`value ${status?.node_available ? 'ok' : 'err'}`}>
                            {status?.node_available ? 'Disponible' : 'Absent'}
                        </div>
                    </div>
                    <div className="status-card">
                        <div className="label">Frontend Build</div>
                        <div className={`value ${status?.build_index_exists ? 'ok' : 'warn'}`}>
                            {status?.build_index_exists ? 'Prêt' : 'Non buildé'}
                        </div>
                    </div>
                    <div className="status-card">
                        <div className="label">Git</div>
                        <div className={`value ${status?.git_available ? 'ok' : 'err'}`}>
                            {status?.git_available ? 'Disponible' : 'Absent'}
                        </div>
                    </div>
                </div>

                {task.status === 'running' && (
                    <div className="task-status">
                        <div className="dot running" />
                        <span>{task.step || 'En cours...'}</span>
                        <span style={{ marginLeft: 'auto', color: '#e94560' }}>{taskPct}%</span>
                    </div>
                )}
                {task.status === 'completed' && (
                    <div className="task-status">
                        <div className="dot completed" />
                        <span style={{ color: '#4ade80' }}>{task.step || 'Terminé'}</span>
                    </div>
                )}
                {task.status === 'error' && (
                    <div className="task-status">
                        <div className="dot error" />
                        <span style={{ color: '#f87171' }}>{task.step || 'Erreur'}</span>
                    </div>
                )}
                {task.status === 'running' && (
                    <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${taskPct}%` }} />
                    </div>
                )}

                <div className="update-tabs">
                    <button className={`update-tab ${tab === 'actions' ? 'active' : ''}`} onClick={() => setTab('actions')}>
                        Actions
                    </button>
                    <button className={`update-tab ${tab === 'logs' ? 'active' : ''}`} onClick={() => loadTab('logs')}>
                        Logs
                    </button>
                    <button className={`update-tab ${tab === 'git' ? 'active' : ''}`} onClick={() => loadTab('git')}>
                        Historique Git
                    </button>
                    <button className={`update-tab ${tab === 'backups' ? 'active' : ''}`} onClick={() => loadTab('backups')}>
                        Sauvegardes
                    </button>
                    <button className={`update-tab ${tab === 'disk' ? 'active' : ''}`} onClick={() => loadTab('disk')}>
                        Espace disque
                    </button>
                </div>

                {tab === 'actions' && (
                    <div className="action-panel">
                        <h2>Actions de mise à jour</h2>
                        <p>Exécutez les opérations de build et déploiement depuis l'interface admin.</p>
                        <div className="action-grid">
                            <div className="action-card success" onClick={async () => { await fullApi.execute(); await refreshStatus(); }}>
                                <div className="icon">🔄</div>
                                <h3>Mise à jour complète</h3>
                                <p>Pull + Build frontend + Push GitHub. Render se redéploye automatiquement.</p>
                            </div>
                            <div className="action-card" onClick={async () => { await buildApi.execute(); await refreshStatus(); }}>
                                <div className="icon">🔨</div>
                                <h3>Build Frontend</h3>
                                <p>Reconstruit le frontend React (npm install + npm run build).</p>
                            </div>
                            <div className="action-card" onClick={async () => { await deployApi.execute(); await refreshStatus(); }}>
                                <div className="icon">🚀</div>
                                <h3>Push & Déployer</h3>
                                <p>Git add + commit + push vers GitHub. Déclenche le déploiement Render.</p>
                            </div>
                            <div className="action-card" onClick={async () => { await pullApi.execute(); await refreshStatus(); }}>
                                <div className="icon">📥</div>
                                <h3>Pull mises à jour</h3>
                                <p>Récupère les dernières modifications depuis GitHub (git pull).</p>
                            </div>
                            <div className="action-card" onClick={async () => {
                                const r = await backupApi.execute();
                                if (r?.ok) alert(`Sauvegarde créée: ${r.name} (${r.size_mb} MB)`);
                                await loadTab('backups');
                            }}>
                                <div className="icon">💾</div>
                                <h3>Créer une sauvegarde</h3>
                                <p>ZIP complet du projet (sans venv/node_modules/.git).</p>
                            </div>
                            <div className="action-card" onClick={refreshStatus}>
                                <div className="icon">🔃</div>
                                <h3>Actualiser le statut</h3>
                                <p>Vérifie l'état actuel du système, des builds et du déploiement.</p>
                            </div>
                        </div>
                    </div>
                )}

                {tab === 'logs' && (
                    <div className="action-panel">
                        <h2>Logs de mise à jour</h2>
                        <p>Historique en temps réel des opérations de build et déploiement.</p>
                        <div className="log-container">
                            {(status?.recent_logs || []).length === 0 ? (
                                <div className="empty-state">Aucun log pour le moment. Lancez une action pour voir les logs.</div>
                            ) : (
                                (status?.recent_logs || []).slice().reverse().map((log, i) => (
                                    <div key={i} className={`log-entry ${log.level}`}>
                                        <span className="time">{new Date(log.time).toLocaleTimeString()}</span>
                                        {log.message}
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                )}

                {tab === 'git' && (
                    <div className="action-panel">
                        <h2>Historique Git</h2>
                        <p>Derniers commits du dépôt.</p>
                        <div className="git-log-list">
                            {(gitLogApi.data?.commits || []).length === 0 ? (
                                <div className="empty-state">Chargement...</div>
                            ) : (
                                (gitLogApi.data?.commits || []).map((c, i) => (
                                    <div key={i} className="git-commit">
                                        <span className="git-hash">{c.hash}</span>
                                        <span className="git-msg">{c.message}</span>
                                        <span className="git-date">{c.date?.split('T')[0] || c.date?.split(' ')[0] || ''}</span>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                )}

                {tab === 'backups' && (
                    <div className="action-panel">
                        <h2>Sauvegardes</h2>
                        <p>Sauvegardes ZIP du projet.</p>
                        <div className="backup-list">
                            {(backupsApi.data?.backups || []).length === 0 ? (
                                <div className="empty-state">Aucune sauvegarde. Créez-en une depuis l'onglet Actions.</div>
                            ) : (
                                (backupsApi.data?.backups || []).map((b, i) => (
                                    <div key={i} className="backup-item">
                                        <span className="backup-name">{b.name}</span>
                                        <span className="backup-meta">{b.size_mb} MB — {new Date(b.date).toLocaleDateString()}</span>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                )}

                {tab === 'disk' && (
                    <div className="action-panel">
                        <h2>Espace disque</h2>
                        <p>Taille des répertoires du projet.</p>
                        <div className="disk-grid">
                            {Object.entries(diskApi.data || {}).map(([name, info]) => (
                                <div key={name} className="disk-item">
                                    <div className="name">{name.replace(/_/g, ' ')}</div>
                                    <div className="size">{info.size_mb}</div>
                                    <div className="unit">MB</div>
                                </div>
                            ))}
                            {Object.keys(diskApi.data || {}).length === 0 && (
                                <div className="empty-state">Chargement...</div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default UpdateAdmin;
