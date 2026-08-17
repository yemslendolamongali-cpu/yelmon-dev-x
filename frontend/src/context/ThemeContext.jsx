import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const ThemeContext = createContext(null);

const THEMES = {
    light: 'light',
    dark: 'dark',
    system: 'system',
};

function getSystemTheme() {
    if (typeof window !== 'undefined' && window.matchMedia) {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'dark';
}

function resolveTheme(theme) {
    if (theme === THEMES.system) return getSystemTheme();
    return theme;
}

export function ThemeProvider({ children }) {
    const [theme, setTheme] = useState(() => {
        return localStorage.getItem('yelmon_theme') || 'dark';
    });

    const [resolved, setResolved] = useState(() => resolveTheme(theme));

    useEffect(() => {
        const r = resolveTheme(theme);
        setResolved(r);
        document.documentElement.setAttribute('data-theme', r);
        document.documentElement.classList.remove('light', 'dark');
        document.documentElement.classList.add(r);
    }, [theme]);

    useEffect(() => {
        if (theme !== 'system') return;
        const mq = window.matchMedia('(prefers-color-scheme: dark)');
        const handler = () => {
            const r = resolveTheme('system');
            setResolved(r);
            document.documentElement.setAttribute('data-theme', r);
            document.documentElement.classList.remove('light', 'dark');
            document.documentElement.classList.add(r);
        };
        mq.addEventListener('change', handler);
        return () => mq.removeEventListener('change', handler);
    }, [theme]);

    const switchTheme = useCallback((newTheme) => {
        setTheme(newTheme);
        localStorage.setItem('yelmon_theme', newTheme);
    }, []);

    return (
        <ThemeContext.Provider value={{ theme, resolved, switchTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}

export function useTheme() {
    const ctx = useContext(ThemeContext);
    if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
    return ctx;
}
