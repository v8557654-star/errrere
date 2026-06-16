# -*- coding: utf-8 -*-
import os

print("🚀 Этап 10 — Прямое скачивание + CurseForge...")

# Запрашиваем CurseForge API ключ
print("\n🔑 Получи API ключ на: https://console.curseforge.com/")
cf_key = input("Вставь CurseForge API ключ (или Enter чтобы пропустить): ").strip()

# Читаем существующий config.py
config_content = ""
if os.path.exists("config.py"):
    with open("config.py", "r", encoding="utf-8") as f:
        config_content = f.read()

if cf_key and "CURSEFORGE_API_KEY" not in config_content:
    with open("config.py", "a", encoding="utf-8") as f:
        f.write(f'\nCURSEFORGE_API_KEY = "{cf_key}"\n')
    print("  ✅ config.py (добавлен CurseForge ключ)")
elif not cf_key and "CURSEFORGE_API_KEY" not in config_content:
    with open("config.py", "a", encoding="utf-8") as f:
        f.write('\nCURSEFORGE_API_KEY = ""\n')
    print("  ⚠️ config.py (без CF ключа — CurseForge будет недоступен)")

# ============= ПАТЧИМ app.py =============
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# Импорт ключа CurseForge
if "CURSEFORGE_API_KEY" not in app_code:
    app_code = app_code.replace(
        "from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET",
        "from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET\ntry:\n    from config import CURSEFORGE_API_KEY\nexcept ImportError:\n    CURSEFORGE_API_KEY = ''"
    )

# Добавляем импорты для скачивания
if "from flask import Response" not in app_code and "Response" not in app_code:
    app_code = app_code.replace(
        "from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, abort",
        "from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, abort, Response, stream_with_context"
    )

# Заменяем старый modrinth_download
old_download = '''@app.route('/modrinth/download')
def modrinth_download():
    """Прокси для скачивания файла с Modrinth"""
    file_url = request.args.get('url', '')
    filename = request.args.get('filename', 'mod.jar')
    if not file_url.startswith('https://cdn.modrinth.com'):
        abort(400)
    return redirect(file_url)'''

new_download = '''@app.route('/modrinth/download')
def modrinth_download():
    """Скачивание файла с Modrinth через прокси (без перехода)"""
    file_url = request.args.get('url', '')
    filename = request.args.get('filename', 'mod.jar')
    if not file_url.startswith('https://cdn.modrinth.com'):
        abort(400)
    try:
        r = requests.get(file_url, stream=True, headers=MODRINTH_HEADERS, timeout=60)
        if r.status_code != 200:
            abort(404)
        return Response(
            stream_with_context(r.iter_content(chunk_size=8192)),
            content_type='application/java-archive',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': r.headers.get('Content-Length', ''),
            }
        )
    except Exception as e:
        flash(f'Ошибка скачивания: {str(e)}', 'error')
        return redirect(url_for('modrinth_search'))

# ===== CURSEFORGE API =====
CF_API = "https://api.curseforge.com/v1"
CF_GAME_ID = 432  # Minecraft
CF_HEADERS = {
    "Accept": "application/json",
    "x-api-key": CURSEFORGE_API_KEY,
}

CF_CATEGORIES = {
    0: 'Все', 6: 'Магия ✨', 5: 'Декор 🪴', 412: 'Магия ✨',
    420: 'Структуры 🏛️', 416: 'Карты 🗺️', 419: 'Серверные ⚙️',
    421: 'Стиль 🎨', 422: 'Аддоны 🧩', 423: 'Мобы 🐺',
    424: 'Еда 🍖', 425: 'Биомы 🌲', 426: 'Измерения 🌌',
    427: 'Руды 💎', 428: 'Технологии ⚙️', 429: 'Броня 🛡️',
    430: 'Транспорт 🚗', 432: 'Кулинария 🍳', 433: 'Энергия ⚡',
    434: 'Хранение 📦', 435: 'Логистика 📊', 436: 'Игроки 👤',
    4485: 'Оружие ⚔️', 4558: 'Производство 🔧',
}

@app.route('/curseforge')
def curseforge_search():
    if not CURSEFORGE_API_KEY:
        flash('CurseForge API не настроен. Получи ключ на console.curseforge.com', 'error')
        return redirect(url_for('index'))

    query = request.args.get('q', '')
    mc_version = request.args.get('mc_version', '')
    category = request.args.get('category', '0')
    sort = request.args.get('sort', '2')  # 1=feat, 2=pop, 3=last_update, 6=name, 8=author
    page = int(request.args.get('page', 1))
    limit = 20
    index = (page - 1) * limit

    params = {
        'gameId': CF_GAME_ID,
        'classId': 6,  # 6 = Mods
        'searchFilter': query,
        'sortField': sort,
        'sortOrder': 'desc',
        'pageSize': limit,
        'index': index,
    }
    if mc_version:
        params['gameVersion'] = mc_version
    if category and category != '0':
        params['categoryId'] = category

    try:
        r = requests.get(f"{CF_API}/mods/search", params=params, headers=CF_HEADERS, timeout=10)
        data = r.json()
        results = data.get('data', [])
        total = data.get('pagination', {}).get('totalCount', 0)
    except Exception as e:
        results = []
        total = 0
        flash(f'Ошибка CurseForge: {str(e)}', 'error')

    versions = ['1.21.4', '1.21.3', '1.21.1', '1.21', '1.20.6', '1.20.4', '1.20.2', '1.20.1',
                '1.19.4', '1.19.2', '1.18.2', '1.17.1', '1.16.5', '1.12.2', '1.8.9', '1.7.10']

    total_pages = min((total + limit - 1) // limit, 50) if total else 1

    return render_template('curseforge_search.html',
        results=results, query=query, mc_version=mc_version, category=category,
        sort=sort, page=page, total=total, total_pages=total_pages,
        cf_categories=CF_CATEGORIES, versions=versions)

@app.route('/curseforge/mod/<int:mod_id>')
def curseforge_mod(mod_id):
    if not CURSEFORGE_API_KEY:
        flash('CurseForge API не настроен', 'error')
        return redirect(url_for('index'))

    try:
        r = requests.get(f"{CF_API}/mods/{mod_id}", headers=CF_HEADERS, timeout=10)
        if r.status_code != 200:
            flash('Мод не найден', 'error')
            return redirect(url_for('curseforge_search'))
        mod = r.json().get('data', {})

        # Описание
        d = requests.get(f"{CF_API}/mods/{mod_id}/description", headers=CF_HEADERS, timeout=10)
        description = d.json().get('data', '') if d.status_code == 200 else ''

        # Файлы
        f = requests.get(f"{CF_API}/mods/{mod_id}/files", headers=CF_HEADERS, params={'pageSize': 20}, timeout=10)
        files = f.json().get('data', []) if f.status_code == 200 else []

    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('curseforge_search'))

    return render_template('curseforge_mod.html', mod=mod, description=description, files=files)

@app.route('/curseforge/download/<int:mod_id>/<int:file_id>')
def curseforge_download(mod_id, file_id):
    """Скачивание файла CurseForge через прокси"""
    if not CURSEFORGE_API_KEY:
        abort(403)
    try:
        # Получаем download URL
        r = requests.get(f"{CF_API}/mods/{mod_id}/files/{file_id}/download-url",
                        headers=CF_HEADERS, timeout=10)
        if r.status_code != 200:
            abort(404)
        download_url = r.json().get('data', '')
        if not download_url:
            abort(404)

        # Получаем имя файла
        finfo = requests.get(f"{CF_API}/mods/{mod_id}/files/{file_id}",
                            headers=CF_HEADERS, timeout=10)
        filename = 'mod.jar'
        if finfo.status_code == 200:
            filename = finfo.json().get('data', {}).get('fileName', 'mod.jar')

        # Скачиваем и стримим
        dr = requests.get(download_url, stream=True, timeout=60)
        if dr.status_code != 200:
            abort(404)

        return Response(
            stream_with_context(dr.iter_content(chunk_size=8192)),
            content_type='application/java-archive',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': dr.headers.get('Content-Length', ''),
            }
        )
    except Exception as e:
        flash(f'Ошибка скачивания: {str(e)}', 'error')
        return redirect(url_for('curseforge_mod', mod_id=mod_id))
'''

# Заменяем
app_code = app_code.replace(old_download, new_download)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)
print("  ✅ app.py (CurseForge + прямое скачивание)")

# ============= ОБНОВЛЯЕМ base.html — пункт CurseForge =============
with open("templates/base.html", "r", encoding="utf-8") as f:
    base_html = f.read()

if "curseforge-item" not in base_html:
    old_modrinth = '''<a href="{{ url_for('modrinth_search') }}" class="nav-item modrinth-item">
                <span class="nav-icon">🌍</span><span>Modrinth</span>
            </a>'''

    new_with_cf = '''<a href="{{ url_for('modrinth_search') }}" class="nav-item modrinth-item">
                <span class="nav-icon">🌍</span><span>Modrinth</span>
            </a>
            <a href="{{ url_for('curseforge_search') }}" class="nav-item curseforge-item">
                <span class="nav-icon">🔥</span><span>CurseForge</span>
            </a>'''

    base_html = base_html.replace(old_modrinth, new_with_cf)

with open("templates/base.html", "w", encoding="utf-8") as f:
    f.write(base_html)
print("  ✅ templates/base.html")

# ============= ОБНОВЛЯЕМ modrinth_project.html — прямое скачивание =============
with open("templates/modrinth_project.html", "r", encoding="utf-8") as f:
    mr_html = f.read()

# Заменяем прямые ссылки на наш прокси
old_link = '<a href="{{ f.url }}" class="mr-version-item" download>'
new_link = '<a href="{{ url_for(\'modrinth_download\', url=f.url, filename=f.filename) }}" class="mr-version-item">'

mr_html = mr_html.replace(old_link, new_link)

with open("templates/modrinth_project.html", "w", encoding="utf-8") as f:
    f.write(mr_html)
print("  ✅ templates/modrinth_project.html (скачивание через прокси)")

# ============= СТРАНИЦА ПОИСКА CURSEFORGE =============
curseforge_search_html = '''{% extends 'base.html' %}
{% block content %}

<div class="curseforge-header">
    <div class="cf-logo">
        <div class="cf-logo-icon">🔥</div>
        <div>
            <h1>CurseForge</h1>
            <p>Самая большая база модов</p>
        </div>
    </div>
    <div class="cf-stats">
        <strong>{{ total }}</strong> модов найдено
    </div>
</div>

<div class="search-bar">
    <form method="GET" action="{{ url_for('curseforge_search') }}">
        <div class="search-input-wrap">
            <span class="search-icon">🔍</span>
            <input type="text" name="q" placeholder="Поиск модов на CurseForge..." value="{{ query }}" autofocus>
        </div>
        <select name="mc_version">
            <option value="">Все версии</option>
            {% for v in versions %}
                <option value="{{ v }}" {% if mc_version == v %}selected{% endif %}>{{ v }}</option>
            {% endfor %}
        </select>
        <button type="submit">Найти</button>
    </form>
</div>

<div class="sort-tabs">
    <a href="{{ url_for('curseforge_search', q=query, mc_version=mc_version, sort='2') }}"
       class="sort-tab {% if sort == '2' %}active{% endif %}">🔥 Популярные</a>
    <a href="{{ url_for('curseforge_search', q=query, mc_version=mc_version, sort='1') }}"
       class="sort-tab {% if sort == '1' %}active{% endif %}">⭐ Рекомендуемые</a>
    <a href="{{ url_for('curseforge_search', q=query, mc_version=mc_version, sort='3') }}"
       class="sort-tab {% if sort == '3' %}active{% endif %}">🔄 Обновлённые</a>
    <a href="{{ url_for('curseforge_search', q=query, mc_version=mc_version, sort='11') }}"
       class="sort-tab {% if sort == '11' %}active{% endif %}">🆕 Новые</a>
    <a href="{{ url_for('curseforge_search', q=query, mc_version=mc_version, sort='6') }}"
       class="sort-tab {% if sort == '6' %}active{% endif %}">🔤 По имени</a>
</div>

<div class="modrinth-grid">
    {% for mod in results %}
    <a href="{{ url_for('curseforge_mod', mod_id=mod.id) }}" class="mr-card cf-card">
        <div class="mr-card-icon">
            {% if mod.logo and mod.logo.thumbnailUrl %}
                <img src="{{ mod.logo.thumbnailUrl }}" alt="{{ mod.name }}">
            {% else %}
                <div class="cf-no-icon">🔥</div>
            {% endif %}
        </div>
        <div class="mr-card-body">
            <div class="mr-card-header">
                <h3>{{ mod.name }}</h3>
                <span class="cf-author">
                    {% if mod.authors %}{{ mod.authors[0].name }}{% endif %}
                </span>
            </div>
            <p class="mr-desc">{{ mod.summary[:140] }}{% if mod.summary|length > 140 %}...{% endif %}</p>

            <div class="mr-stats">
                <span>⬇ {{ "{:,}".format(mod.downloadCount).replace(",", " ") }}</span>
                {% if mod.latestFilesIndexes %}
                    <span class="cf-version">MC {{ mod.latestFilesIndexes[0].gameVersion }}</span>
                {% endif %}
            </div>
        </div>
    </a>
    {% else %}
        <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <h3>Ничего не найдено</h3>
            <p>Попробуй изменить запрос</p>
        </div>
    {% endfor %}
</div>

{% if total_pages > 1 %}
<div class="pagination">
    {% if page > 1 %}
        <a href="{{ url_for('curseforge_search', q=query, mc_version=mc_version, sort=sort, page=page-1) }}" class="page-btn">← Назад</a>
    {% endif %}
    <span class="page-info">Страница {{ page }} из {{ total_pages }}</span>
    {% if page < total_pages %}
        <a href="{{ url_for('curseforge_search', q=query, mc_version=mc_version, sort=sort, page=page+1) }}" class="page-btn">Вперёд →</a>
    {% endif %}
</div>
{% endif %}

<div class="modrinth-credits">
    Данные предоставлены <a href="https://curseforge.com" target="_blank">CurseForge</a>
</div>
{% endblock %}'''

with open("templates/curseforge_search.html", "w", encoding="utf-8") as f:
    f.write(curseforge_search_html)
print("  ✅ templates/curseforge_search.html")

# ============= СТРАНИЦА МОДА CURSEFORGE =============
curseforge_mod_html = '''{% extends 'base.html' %}
{% block content %}

<a href="{{ url_for('curseforge_search') }}" class="back-btn">← К поиску CurseForge</a>

<div class="mr-project cf-project">

    <div class="mr-project-header">
        <div class="mr-project-icon">
            {% if mod.logo and mod.logo.url %}
                <img src="{{ mod.logo.url }}" alt="{{ mod.name }}">
            {% else %}
                <div class="cf-no-icon-big">🔥</div>
            {% endif %}
        </div>
        <div class="mr-project-info">
            <h1>{{ mod.name }}</h1>
            <p class="mr-project-desc">{{ mod.summary }}</p>
            <div class="mr-project-stats">
                <span>⬇ {{ "{:,}".format(mod.downloadCount).replace(",", " ") }}</span>
                {% if mod.dateModified %}<span>📅 {{ mod.dateModified[:10] }}</span>{% endif %}
                {% if mod.authors %}<span>👤 {{ mod.authors[0].name }}</span>{% endif %}
            </div>

            {% if mod.categories %}
            <div class="mr-project-categories">
                {% for cat in mod.categories %}
                    <span class="mr-tag cf-tag">{{ cat.name }}</span>
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>

    {% if mod.screenshots %}
    <div class="screenshots-section">
        <h3>📸 Скриншоты</h3>
        <div class="screenshots-grid">
            {% for ss in mod.screenshots[:6] %}
                <img src="{{ ss.url }}" alt="{{ ss.title or 'Screenshot' }}"
                     class="screenshot" onclick="openLightbox('{{ ss.url }}')">
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <div class="mr-project-grid">
        <div class="mr-project-body">
            <div class="mod-description">
                <h3>📖 Описание</h3>
                <div class="mr-body-content">{{ description|safe }}</div>
            </div>
        </div>

        <div class="mr-project-sidebar">
            {% if mod.links and mod.links.websiteUrl %}
            <a href="{{ mod.links.websiteUrl }}" target="_blank" class="btn-curseforge">
                🔥 Открыть на CurseForge
            </a>
            {% endif %}

            <h3 class="mr-versions-title">📥 Скачать</h3>
            <div class="mr-versions-list">
                {% for f in files[:15] %}
                <a href="{{ url_for('curseforge_download', mod_id=mod.id, file_id=f.id) }}" class="mr-version-item cf-version-item">
                    <div class="mr-v-info">
                        <div class="mr-v-name">{{ f.displayName or f.fileName }}</div>
                        <div class="mr-v-meta">
                            {% if f.gameVersions %}
                                {% for gv in f.gameVersions[:3] %}
                                    {% if not 'Forge' in gv and not 'Fabric' in gv %}
                                        <span>MC {{ gv }}</span>
                                    {% endif %}
                                {% endfor %}
                            {% endif %}
                            <span>⬇ {{ "{:,}".format(f.downloadCount).replace(",", " ") }}</span>
                            <span>{{ (f.fileLength / 1024 / 1024)|round(1) }} МБ</span>
                        </div>
                    </div>
                    <div class="mr-v-download">⬇</div>
                </a>
                {% endfor %}
            </div>

            {% if mod.links %}
                {% if mod.links.sourceUrl %}
                <a href="{{ mod.links.sourceUrl }}" target="_blank" class="mr-extra-link">
                    <span>💻</span> Исходный код
                </a>
                {% endif %}
                {% if mod.links.wikiUrl %}
                <a href="{{ mod.links.wikiUrl }}" target="_blank" class="mr-extra-link">
                    <span>📚</span> Wiki
                </a>
                {% endif %}
                {% if mod.links.issuesUrl %}
                <a href="{{ mod.links.issuesUrl }}" target="_blank" class="mr-extra-link">
                    <span>🐛</span> Issues
                </a>
                {% endif %}
            {% endif %}
        </div>
    </div>
</div>

<div id="lightbox" class="lightbox" onclick="closeLightbox()">
    <img id="lightbox-img" src="" alt="">
    <span class="lightbox-close">&times;</span>
</div>

<script>
function openLightbox(src) {
    document.getElementById('lightbox-img').src = src;
    document.getElementById('lightbox').classList.add('active');
}
function closeLightbox() {
    document.getElementById('lightbox').classList.remove('active');
}
</script>
{% endblock %}'''

with open("templates/curseforge_mod.html", "w", encoding="utf-8") as f:
    f.write(curseforge_mod_html)
print("  ✅ templates/curseforge_mod.html")

# ============= CSS для CurseForge =============
extra_css = '''

/* ===== CURSEFORGE ===== */
.curseforge-item {
    color: #f97316 !important;
    position: relative;
}

.curseforge-item::after {
    content: 'API';
    position: absolute;
    right: 12px;
    background: linear-gradient(135deg, #f97316, #fbbf24);
    color: #000;
    font-size: 9px;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 800;
}

.curseforge-item:hover {
    background: rgba(249, 115, 22, 0.1) !important;
}

.curseforge-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, rgba(249, 115, 22, 0.1), rgba(251, 191, 36, 0.1));
    border: 1px solid rgba(249, 115, 22, 0.2);
    padding: 24px;
    border-radius: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 16px;
}

.cf-logo {
    display: flex;
    align-items: center;
    gap: 16px;
}

.cf-logo-icon {
    font-size: 48px;
    animation: floatIcon 3s ease-in-out infinite;
}

.cf-logo h1 {
    font-size: 28px;
    background: linear-gradient(135deg, #f97316, #fbbf24);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.cf-logo p {
    color: var(--text-muted);
    font-size: 14px;
}

.cf-stats {
    background: var(--bg-card);
    padding: 12px 20px;
    border-radius: 12px;
    border: 1px solid var(--border);
}

.cf-stats strong {
    color: #f97316;
    font-size: 20px;
}

.cf-card:hover {
    border-color: #f97316 !important;
    box-shadow: 0 12px 30px rgba(249, 115, 22, 0.15) !important;
}

.cf-author {
    color: #f97316 !important;
}

.cf-no-icon, .cf-no-icon-big {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #f97316, #fbbf24);
}

.cf-no-icon { font-size: 40px; }
.cf-no-icon-big { font-size: 70px; }

.cf-version {
    background: rgba(249, 115, 22, 0.1) !important;
    color: #f97316 !important;
}

.cf-tag {
    background: rgba(249, 115, 22, 0.1) !important;
    color: #f97316 !important;
}

.btn-curseforge {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 14px;
    background: linear-gradient(135deg, #f97316, #fbbf24);
    color: #000;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 700;
    transition: all 0.2s;
}

.btn-curseforge:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(249, 115, 22, 0.4);
}

.cf-version-item:hover {
    border-color: #f97316 !important;
    background: rgba(249, 115, 22, 0.05) !important;
}

.cf-project .mr-extra-link:hover {
    border-color: #f97316;
}
'''

css_path = "static/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    existing_css = f.read()

if "/* ===== CURSEFORGE ===== */" not in existing_css:
    with open(css_path, "a", encoding="utf-8") as f:
        f.write(extra_css)
    print(f"  ✅ {css_path}")

print("\n🎉 ЭТАП 10 ГОТОВ!")
print("\n✨ Добавлено:")
print("   📥 Скачивание Modrinth БЕЗ перехода на их сайт")
print("   🔥 Полная интеграция с CurseForge")
print("   🔍 Поиск + фильтры + 5 сортировок")
print("   📄 Пагинация результатов")
print("   📥 Скачивание .jar с CurseForge через прокси")
print("   🎨 Оранжевая цветовая схема (как у CF)")
print("\n⚠️  ВАЖНО: если ты ввёл CF ключ, нужно создать его и на PythonAnywhere!")
print("\n📤 git add . && git commit -m 'v11: CurseForge + direct downloads' && git push --force origin main")
print("\nНа PythonAnywhere:")
print("   cd ~/mysite")
print("   git fetch origin main && git reset --hard origin/main")
print("\n⚠️  Если добавил CF ключ — обнови config.py на сервере:")
print("   nano config.py")
print('   Добавь строку: CURSEFORGE_API_KEY = "твой_ключ"')
print("\nЗатем Reload на вкладке Web 🟢")