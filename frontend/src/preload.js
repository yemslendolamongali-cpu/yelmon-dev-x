const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('yelmon', {
    appName: 'YELMON Dev X',
    version: '1.0.0',
    isElectron: true,
});
