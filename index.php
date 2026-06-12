<?php
# ==========================================
# Файл: index.php
# Справка: Точка входа для веб-сервера Timeweb
# Задача: запуск бота (ansamb_sledov_bot-dump/bot.py) с загрузкой .env
# ==========================================

// Путь к папке проекта (относительно корня сайта)
$project_dir = __DIR__ . '/ansamb_sledov_bot-dump';

// Переходим в папку проекта
chdir($project_dir);

// Загружаем переменные из .env
$env_file = '.env';
if (file_exists($env_file)) {
    $lines = file($env_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos($line, '=') !== false) {
            putenv(trim($line));
        }
    }
}

// Запускаем бота в фоновом режиме
exec("python3 bot.py > /dev/null 2>&1 &", $output, $return_var);

if ($return_var === 0) {
    echo "<h1>Ансамбль Следов</h1>";
    echo "<p>Бот запущен в фоновом режиме.</p>";
} else {
    echo "<h1>Ошибка запуска</h1>";
    echo "<p>Код ошибки: $return_var</p>";
}
?>
