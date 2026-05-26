// ==========================================
// Файл: static/js/modules/vk.js
// Справка: README.md → Веб-морда / VK
// Задача: постинг в VK и создание постов в Telegram
// Комментарий: работает с API /vk_post и /api/create_post
// Зависит от: нет (использует appendMessage из глобального окна)
// Вызывается из: admin.html (кнопки "📘 Пост в VK", "📱 Пост в Telegram")
// ==========================================

/**
 * Отправляет текстовый пост в VK
 */
export async function sendPost() {
    const textarea = document.getElementById('post-text');
    const text = textarea?.value.trim();
    
    if (!text) {
        alert("Введите текст поста");
        return;
    }
    
    const statusSpan = document.getElementById('post-status');
    if (statusSpan) statusSpan.innerText = '⏳ Отправка...';
    
    try {
        const response = await fetch('/vk_post', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: 'text=' + encodeURIComponent(text)
        });
        
        const data = await response.json();
        
        if (data.status === 'ok') {
            if (statusSpan) {
                statusSpan.innerHTML = `✅ Опубликовано! <a href="${data.url}" target="_blank">Ссылка</a>`;
            }
            if (textarea) textarea.value = '';
        } else {
            if (statusSpan) statusSpan.innerText = '❌ ' + (data.error || 'Ошибка');
        }
    } catch (e) {
        console.error('Ошибка отправки поста:', e);
        if (statusSpan) statusSpan.innerText = '❌ Ошибка сети';
    }
    
    setTimeout(() => {
        if (statusSpan) statusSpan.innerText = '';
    }, 5000);
}

/**
 * Создаёт пост в Telegram или VK (через API create_post)
 * @param {string} platform - 'telegram' или 'vk'
 */
export async function createPost(platform) {
    const text = prompt(`Введите текст для публикации в ${platform === 'vk' ? 'VK' : 'Telegram'}:`);
    if (!text) return;
    
    try {
        const response = await fetch('/api/create_post', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ platform: platform, text: text })
        });
        
        const data = await response.json();
        
        if (data.status === 'ok') {
            alert('✅ Опубликовано!');
            if (data.url && window.appendMessage) {
                window.appendMessage({
                    source: 'admin',
                    text: `📢 Пост: ${text}<br><a href="${data.url}" target="_blank">Ссылка</a>`,
                    timestamp: new Date().toISOString(),
                    own: true
                });
            }
        } else {
            alert('❌ Ошибка: ' + (data.error || 'неизвестная'));
        }
    } catch (e) {
        console.error('Ошибка создания поста:', e);
        alert('❌ Ошибка сети');
    }
}

// Глобальные функции для onclick из HTML
window.sendPost = sendPost;
window.createPost = createPost;
