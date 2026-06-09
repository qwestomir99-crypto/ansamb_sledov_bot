const { spawn } = require('child_process');
const path = require('path');

console.log('[Node.js] Запуск Python-бота...');

const pythonProcess = spawn('python3', ['-m', 'services.app'], {
    cwd: __dirname,
    stdio: 'inherit',
    env: process.env
});

pythonProcess.on('close', (code) => {
    console.log(`[Node.js] Python-бот завершил работу с кодом ${code}`);
    process.exit(code);
});

pythonProcess.on('error', (err) => {
    console.error(`[Node.js] Ошибка запуска Python: ${err.message}`);
    process.exit(1);
});
