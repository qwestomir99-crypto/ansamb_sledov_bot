# ==========================================
# YOUTUBE ПРОКСИ + ПОИСК
# ==========================================

@app.route('/youtube')
@login_required
def youtube_page():
    """Страница с YouTube-прокси, поиском и каталогом"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>YouTube через Ансамбль — прокси и поиск</title>
        <style>
            body { background: #0a0a0a; color: #00ffcc; font-family: monospace; padding: 2rem; }
            .container { max-width: 1000px; margin: 0 auto; }
            .card { background: #111; border-left: 3px solid #00ffcc; padding: 1rem; margin: 1rem 0; border-radius: 8px; }
            input, button { background: #222; color: #00ffcc; border: 1px solid #00ffcc; padding: 8px 12px; border-radius: 4px; }
            button:hover { background: #00ffcc; color: #000; cursor: pointer; }
            .video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem; }
            .video-card { background: #111; border-left: 2px solid #00ffcc; padding: 0.5rem; cursor: pointer; transition: 0.2s; }
            .video-card:hover { background: #1a1a1a; transform: translateY(-2px); }
            .video-title { font-weight: bold; margin-bottom: 0.3rem; font-size: 0.9rem; }
            .video-channel { font-size: 0.7rem; color: #888; }
            video { width: 100%; max-width: 800px; margin-top: 20px; border: 1px solid #00ffcc; }
            a { color: #00ffcc; }
            .search-row { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
            .search-row input { flex: 1; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 YouTube через Ансамбль</h1>
            <p>Поиск, каталог, прокси — без VPN и рекламы.</p>
            <div class="card">
                <div class="search-row">
                    <input type="text" id="search-query" placeholder="Поиск: квантовая физика, философия, нейросети..." onkeypress="if(event.key==='Enter') searchVideos()">
                    <button onclick="searchVideos()">🔍 Поиск</button>
                </div>
                <div id="catalog" class="video-grid">
                    <div style="color: #666;">Введите запрос для поиска.</div>
                </div>
                <div id="player-container" style="margin-top: 20px;"></div>
            </div>
            <p><a href="/">← Назад в веб-морду</a></p>
        </div>
        <script>
        async function searchVideos() {
            const query = document.getElementById('search-query').value.trim();
            if (!query) return;
            const catalogDiv = document.getElementById('catalog');
            catalogDiv.innerHTML = '<div style="color:#ff0;">⏳ Поиск...</div>';
            try {
                const resp = await fetch(`/youtube_search?q=${encodeURIComponent(query)}`);
                const data = await resp.json();
                if (data.error) {
                    catalogDiv.innerHTML = `<div style="color:#f00;">❌ ${data.error}</div>`;
                    return;
                }
                if (!data.length) {
                    catalogDiv.innerHTML = '<div style="color:#f00;">Ничего не найдено</div>';
                    return;
                }
                catalogDiv.innerHTML = '';
                data.forEach(video => {
                    const card = document.createElement('div');
                    card.className = 'video-card';
                    card.innerHTML = `
                        <div class="video-title">${escapeHtml(video.title)}</div>
                        <div class="video-channel">${escapeHtml(video.author)} • ${video.views_short || ''}</div>
                    `;
                    card.onclick = () => loadVideo(video.video_url);
                    catalogDiv.appendChild(card);
                });
            } catch(e) {
                catalogDiv.innerHTML = '<div style="color:#f00;">Ошибка поиска</div>';
            }
        }
        
        async function loadVideo(videoUrl) {
            const container = document.getElementById('player-container');
            container.innerHTML = '<div style="color:#ff0;">⏳ Загрузка видео...</div>';
            try {
                const resp = await fetch('/youtube_info', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: videoUrl})
                });
                const data = await resp.json();
                if (data.error) {
                    container.innerHTML = `<div style="color:#f00;">❌ ${data.error}</div>`;
                    return;
                }
                container.innerHTML = `
                    <video controls autoplay>
                        <source src="${data.stream_url}" type="video/mp4">
                        Ваш браузер не поддерживает видео.
                    </video>
                    <div style="margin-top: 10px;">🎵 ${escapeHtml(data.title)} | Длительность: ${Math.floor(data.duration/60)}:${(data.duration%60).toString().padStart(2,'0')}</div>
                `;
            } catch(e) {
                container.innerHTML = '<div style="color:#f00;">❌ Ошибка загрузки видео</div>';
            }
        }
        
        function escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        </script>
    </body>
    </html>
    ''')

@app.route('/youtube_search', methods=['GET'])
@login_required
def youtube_search():
    """Поиск видео через Invidious API (без аккаунта YouTube)"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Empty query'}), 400
    
    # Используем публичный инстанс Invidious
    invidious_api = "https://yewtu.be/api/v1/search"
    try:
        resp = requests.get(invidious_api, params={
            'q': query,
            'type': 'video',
            'sort': 'relevance',
            'fields': 'videoId,title,author,viewCount,lengthSeconds,publishedText'
        }, timeout=10)
        data = resp.json()
        videos = []
        for item in data.get('items', []):
            videos.append({
                'video_url': f"https://youtube.com/watch?v={item.get('videoId')}",
                'title': item.get('title', 'Без названия'),
                'author': item.get('author', 'Неизвестный канал'),
                'views_short': item.get('viewCount', '0'),
                'duration': item.get('lengthSeconds', 0)
            })
        return jsonify(videos[:20])  # не больше 20 видео
    except Exception as e:
        print(f"[YOUTUBE_SEARCH] Ошибка: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/youtube_info', methods=['POST'])
@login_required
def youtube_info():
    """Получает ссылку на видео (720p) через yt-dlp"""
    data = request.json
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL не указан'}), 400
    
    import yt_dlp
    ydl_opts = {
        'format': 'best[height<=720]',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = None
            for fmt in info.get('formats', []):
                if fmt.get('height') and fmt['height'] <= 720 and fmt.get('ext') == 'mp4':
                    if fmt.get('acodec') and fmt['acodec'] != 'none':
                        video_url = fmt['url']
                        break
            if not video_url:
                video_url = info.get('url') or info['formats'][0]['url']
            return jsonify({
                'title': info.get('title', 'YouTube видео'),
                'stream_url': f"/youtube_stream?url={url}",
                'duration': info.get('duration', 0)
            })
    except Exception as e:
        print(f"[YOUTUBE_INFO] Ошибка: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/youtube_stream')
@login_required
def youtube_stream():
    """Проксирует видеофайл YouTube"""
    url = request.args.get('url')
    if not url:
        return "URL не указан", 400
    
    import yt_dlp
    ydl_opts = {
        'format': 'best[height<=720]',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = None
            for fmt in info.get('formats', []):
                if fmt.get('height') and fmt['height'] <= 720 and fmt.get('ext') == 'mp4':
                    if fmt.get('acodec') and fmt['acodec'] != 'none':
                        video_url = fmt['url']
                        break
            if not video_url:
                video_url = info.get('url') or info['formats'][0]['url']
        
        def generate():
            try:
                r = requests.get(video_url, stream=True, timeout=30)
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            except Exception as e:
                print(f"[YOUTUBE_STREAM] Ошибка: {e}")
        
        return Response(generate(), content_type='video/mp4')
    except Exception as e:
        print(f"[YOUTUBE_STREAM] Ошибка: {e}")
        return f"Ошибка потока: {e}", 500
