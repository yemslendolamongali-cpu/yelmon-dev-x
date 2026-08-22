import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext(null);

function _verifyToken(token) {
    return fetch('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` },
    }).then(async res => {
        if (res.status === 401) return { valid: false };
        if (!res.ok) throw new Error('network');
        const data = await res.json();
        return {
            valid: true,
            user: {
                username: data.username,
                role: data.role || 'user',
                display_name: data.display_name || data.username,
                email: data.email || '',
                phone: data.phone || '',
            },
        };
    });
}

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(() => localStorage.getItem('yelmon_token'));
    const [loading, setLoading] = useState(true);

    const logout = useCallback(() => {
        fetch('/api/auth/logout', { method: 'POST' }).catch(() => {});
        localStorage.removeItem('yelmon_token');
        setToken(null);
        setUser(null);
    }, []);

    useEffect(() => {
        if (!token) { setLoading(false); return; }
        let cancelled = false;
        const attempt = (retries) => {
            _verifyToken(token)
                .then(result => {
                    if (cancelled) return;
                    if (result.valid) {
                        setUser(result.user);
                    } else {
                        localStorage.removeItem('yelmon_token');
                        setToken(null);
                    }
                })
                .catch(() => {
                    if (cancelled) return;
                    if (retries > 0) {
                        setTimeout(() => attempt(retries - 1), 800);
                    } else {
                        setLoading(false);
                    }
                })
                .finally(() => { if (!cancelled) setLoading(false); });
        };
        attempt(2);
        return () => { cancelled = true; };
    }, [token]);

    const login = useCallback(async (identifier, password, method = 'username') => {
        const body = { password };
        if (method === 'email') body.email = identifier;
        else if (method === 'phone') body.phone = identifier;
        else body.username = identifier;
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Erreur de connexion');
        localStorage.setItem('yelmon_token', data.token);
        setToken(data.token);
        setUser({ username: data.username });
        setLoading(false);
        return data;
    }, []);

    const signup = useCallback(async (username, password, { email, phone, displayName } = {}) => {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username,
                password,
                email: email || '',
                phone: phone || '',
                display_name: displayName || '',
            }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Erreur d'inscription");
        localStorage.setItem('yelmon_token', data.token);
        setToken(data.token);
        setUser({ username: data.username });
        setLoading(false);
        return data;
    }, []);

    const deleteAccount = useCallback(async () => {
        if (!token) throw new Error('Non authentifié');
        const res = await fetch('/api/auth/delete', {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Erreur de suppression');
        logout();
        return data;
    }, [token, logout]);

    return (
        <AuthContext.Provider value={{ user, token, loading, login, signup, logout, deleteAccount }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within AuthProvider');
    return ctx;
}
