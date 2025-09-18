// electron/main.js
const { app, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

function logLine(msg) {
  try {
    const logDir = app.getPath('logs');
    const logFile = path.join(logDir, 'sertifikita-launch.log');
    fs.appendFileSync(logFile, `[${new Date().toISOString()}] ${msg}\n`);
  } catch {}
}

function resolvePythonExecutable() {
  const prod = path.join(process.resourcesPath, 'Sertifikita.app', 'Contents', 'MacOS', 'Sertifikita');
  if (fs.existsSync(prod)) return prod;
  const dev = path.resolve(__dirname, '..', 'dist-python', 'Sertifikita.app', 'Contents', 'MacOS', 'Sertifikita');
  return dev;
}

function launchPythonAndExit() {
  const exe = resolvePythonExecutable();
  logLine(`Trying to spawn: ${exe}`);

  if (!fs.existsSync(exe)) {
    dialog.showErrorBox('Sertifikita tidak ditemukan', `Path:\n${exe}`);
    return app.quit();
  }

  const logDir = app.getPath('logs');
  const pyErr = path.join(logDir, 'sertifikita-python.err.log');
  const pyOut = path.join(logDir, 'sertifikita-python.out.log');

  const child = spawn(exe, [], {
    detached: true,
    stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env } // tambahkan { QT_DEBUG_PLUGINS: '1' } jika perlu debug Qt
  });

  child.stdout.on('data', d => { try { fs.appendFileSync(pyOut, String(d)); } catch {} });
  child.stderr.on('data', d => { try { fs.appendFileSync(pyErr, String(d)); } catch {} });

  child.on('error', (err) => {
    logLine(`Spawn error: ${err.stack || err}`);
    dialog.showErrorBox('Gagal menjalankan Sertifikita', String(err));
    app.quit();
  });

  child.on('exit', (code, signal) => {
    logLine(`Python app exited code=${code} signal=${signal}`);
    if (code !== 0) {
      dialog.showErrorBox('Sertifikita keluar tiba-tiba',
        `Exit code: ${code}\nSignal: ${signal}\nCek log:\n${pyErr}`);
    }
    app.quit();
  });

  child.unref();
}

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) app.quit();
else {
  app.whenReady().then(() => {
    if (app.dock) app.dock.hide(); // launcher tanpa Dock
    launchPythonAndExit();
  });
}
