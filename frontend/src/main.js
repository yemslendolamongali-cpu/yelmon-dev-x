const { app, BrowserWindow, shell } = require('electron');
const path = require('path');

const BACKEND_URL = 'http://localhost:5001';
const MAX_RETRIES = 15;

let mainWindow = null;
let retries = 0;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 820,
        minWidth: 900,
        minHeight: 600,
        title: 'YELMON Dev X',
        backgroundColor: '#1a1a2e',
        icon: path.join(__dirname, '../../assets/icon.png'),
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
            sandbox: true,
        },
    });

    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    loadWithRetry();
}

function loadWithRetry() {
    if (!mainWindow) return;
    mainWindow.loadURL(BACKEND_URL).catch(() => {
        if (retries < MAX_RETRIES && mainWindow) {
            retries += 1;
            setTimeout(loadWithRetry, 2000);
        }
    });
}

app.whenReady().then(() => {
    createWindow();
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});
