const { spawn } = require('child_process');
const path = require('path');

console.log('[Node.js] Обёртка запущена');

// Функция для проверки и установки Python
function checkAndRun() {
    console.log('[Node.js] Проверка наличия python3...');
    
    // Проверяем, есть ли python3 в системе
    const checkPython = spawn('sh', ['-c', 'command -v python3']);
    
    checkPython.on('close', (code) => {
        if (code === 0) {
            // Python уже есть — запускаем бота
            console.log('[Node.js] python3 найден. Запуск Python-бота...');
            runBot();
        } else {
            // Python нет — устанавливаем
            console.log('[Node.js] python3 не найден. Устанавливаю...');
            const installPython = spawn('sh', ['-c', 'apt-get update && apt-get install -y python3 python3-pip']);
            
            installPython.stdout.on('data', (data) => console.log(`[APT] ${data}`.trim()));
            installPython.stderr.on('data', (data) => console.error(`[APT ERR] ${data}`.trim()));
            
            installPython.on('close', (installCode) => {
                if (installCode === 0) {
                    console.log('[Node.js] python3 установлен. Запуск Python-бота...');
                    runBot();
                } else {
                    console.error(`[Node.js] Ошибка установки python3, код: ${installCode}`);
                    process.exit(1);
                }
            });
        }
    });
}

// Функция запуска бота
function runBot() {
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
}

// Запускаем процесс
checkAndRun();
