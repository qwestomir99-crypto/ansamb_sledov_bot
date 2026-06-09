const { spawn } = require('child_process');
const path = require('path');

console.log('[Node.js] Обёртка запущена');
console.log('[Node.js] Запуск Python-бота...');

const pythonProcess = spawn('python3', [path.join(__dirname, 'real_bot.py')], {
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
