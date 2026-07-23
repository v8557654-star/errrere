# -*- coding: utf-8 -*-
import os

print("🚀 Этап 9 — Интеграция с Modrinth...")

# ============= ПАТЧИМ app.py — добавляем роуты Modrinth =============
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# Добавляем импорт requests если ещё нет
if "import requests" not in app_code:
    app_code = app_code.replace(
        "from functools import wraps",
        "from functools import wraps\nimport requests"
    )

# Добавляем роуты Modrinth перед "with app.app_context():"
modrinth_routes = '''
# ===== MODRINTH API =====
MODRINTH_API = "https://api.modrinth.com/v2"
MODRINTH_HEADERS = {"User-Agent": "MineMods/1.0 (contact@minemods.local)"}

@app.route('/modrinth')
def modrinth_search():
    query = request.args.get('q', '')
    mc_version = request.args.get('mc_version', '')
    category = request.args.get('category', '')
    sort = request.args.get('sort', 'relevance')  # relevance, downloads, follows, newest, updated
    page = int(request.args.get('page', 1))
    limit = 20
    offset = (page - 1) * limit

    # Формируем facets для фильтров
    facets = [["project_type:mod"]]
    if mc_version:
        facets.append([f"versions:{mc_version}"])
    if category:
        facets.append([f"categories:{category}"])

    params = {
        'query': query,
        'facets': str(facets).replace("'", '"'),
        'limit': limit,
        'offset': offset,
        'index': sort,
    }

    try:
        r = requests.get(f"{MODRINTH_API}/search", params=params, headers=MODRINTH_HEADERS, timeout=10)
        data = r.json()
        results = data.get('hits', [])
        total = data.get('total_hits', 0)
    except Exception as e:
        results = []
        total = 0
        flash(f'Ошибка соединения с Modrinth: {str(e)}', 'error')

    # Категории Modrinth
    mr_categories = [
        ('adventure', 'Приключения 🗺️'),
        ('cursed', 'Проклятые 👻'),
        ('decoration', 'Декор 🪴'),
        ('economy', 'Экономика 💰'),
        ('equipment', 'Снаряжение ⚔️'),
        ('food', 'Еда 🍖'),
        ('game-mechanics', 'Механики 🎮'),
        ('library', 'Библиотеки 📚'),
        ('magic', 'Магия ✨'),
        ('management', 'Менеджмент 📊'),
        ('minigame', 'Мини-игры 🎯'),
        ('mobs', 'Мобы 🐺'),
        ('optimization', 'Оптимизация ⚡'),
        ('social', 'Социальные 💬'),
        ('storage', 'Хранение 📦'),
        ('technology', 'Технологии ⚙️'),
        ('transportation', 'Транспорт 🚗'),
        ('utility', 'Утилиты 🔧'),
        ('worldgen', 'Генерация миров 🌍'),
    ]

    versions = ['1.21.4', '1.21.3', '1.21.1', '1.21', '1.20.6', '1.20.4', '1.20.2', '1.20.1',
                '1.19.4', '1.19.2', '1.18.2', '1.17.1', '1.16.5', '1.12.2', '1.8.9', '1.7.10']

    total_pages = (total + limit - 1) // limit if total else 1

    return render_template('modrinth_search.html',
        results=results, query=query, mc_version=mc_version, category=category,
        sort=sort, page=page, total=total, total_pages=total_pages,
        mr_categories=mr_categories, versions=versions)

@app.route('/modrinth/project/<slug>')
def modrinth_project(slug):
    try:
        # Информация о проекте
        r = requests.get(f"{MODRINTH_API}/project/{slug}", headers=MODRINTH_HEADERS, timeout=10)
        if r.status_code != 200:
            flash('Мод не найден на Modrinth', 'error')
            return redirect(url_for('modrinth_search'))
        project = r.json()

        # Версии мода
        v = requests.get(f"{MODRINTH_API}/project/{slug}/version", headers=MODRINTH_HEADERS, timeout=10)
        versions_list = v.json() if v.status_code == 200 else []

    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('modrinth_search'))

    return render_template('modrinth_project.html', project=project, versions=versions_list)

@app.route('/modrinth/download')
def modrinth_download():
    """Прокси для скачивания файла с Modrinth"""
    file_url = request.args.get('url', '')
    filename = request.args.get('filename', 'mod.jar')
    if not file_url.startswith('https://cdn.modrinth.com'):
        abort(400)
    return redirect(file_url)
'''

if "MODRINTH_API" not in app_code:
    app_code = app_code.replace(
        "with app.app_context():",
        modrinth_routes + "\nwith app.app_context():"
    )

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)
print("  ✅ app.py (добавлены роуты Modrinth)")

# ============= ОБНОВЛЯЕМ base.html — добавляем пункт меню =============
with open("templates/base.html", "r", encoding="utf-8") as f:
    base_html = f.read()

# Добавляем пункт меню Modrinth после "Каталог"
old_news = '<a href="{{ url_for(\'news_list\') }}" class="nav-item">\n                <span class="nav-icon">📰</span><span>Новости</span>\n            </a>'
new_news_with_modrinth = '''<a href="{{ url_for('news_list') }}" class="nav-item">
                <span class="nav-icon">📰</span><span>Новости</span>
            </a>
            <a href="{{ url_for('modrinth_search') }}" class="nav-item modrinth-item">
                <span class="nav-icon">🌍</span><span>Modrinth</span>
            </a>'''

if "modrinth-item" not in base_html:
    base_html = base_html.replace(old_news, new_news_with_modrinth)

with open("templates/base.html", "w", encoding="utf-8") as f:
    f.write(base_html)
print("  ✅ templates/base.html (добавлен пункт Modrinth)")

# ============= СТРАНИЦА ПОИСКА MODRINTH =============
modrinth_search_html = '''{% extends 'base.html' %}
{% block content %}

<div class="modrinth-header">
    <div class="modrinth-logo">
        <div class="mr-logo-icon">🌍</div>
        <div>
            <h1>Modrinth</h1>
            <p>Поиск по миллионам модов</p>
        </div>
    </div>
    <div class="modrinth-stats">
        <strong>{{ total }}</strong> модов найдено
    </div>
</div>

<div class="search-bar">
    <form method="GET" action="{{ url_for('modrinth_search') }}">
        <div class="search-input-wrap">
            <span class="search-icon">🔍</span>
            <input type="text" name="q" placeholder="Поиск модов на Modrinth..." value="{{ query }}" autofocus>
        </div>
        <select name="category">
            <option value="">Все категории</option>
            {% for slug, name in mr_categories %}
                <option value="{{ slug }}" {% if category == slug %}selected{% endif %}>{{ name }}</option>
            {% endfor %}
        </select>
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
    <a href="{{ url_for('modrinth_search', q=query, category=category, mc_version=mc_version, sort='relevance') }}"
       class="sort-tab {% if sort == 'relevance' %}active{% endif %}">🎯 Релевантность</a>
    <a href="{{ url_for('modrinth_search', q=query, category=category, mc_version=mc_version, sort='downloads') }}"
       class="sort-tab {% if sort == 'downloads' %}active{% endif %}">🔥 Скачивания</a>
    <a href="{{ url_for('modrinth_search', q=query, category=category, mc_version=mc_version, sort='follows') }}"
       class="sort-tab {% if sort == 'follows' %}active{% endif %}">⭐ Подписчики</a>
    <a href="{{ url_for('modrinth_search', q=query, category=category, mc_version=mc_version, sort='newest') }}"
       class="sort-tab {% if sort == 'newest' %}active{% endif %}">🆕 Новые</a>
    <a href="{{ url_for('modrinth_search', q=query, category=category, mc_version=mc_version, sort='updated') }}"
       class="sort-tab {% if sort == 'updated' %}active{% endif %}">🔄 Обновлённые</a>
</div>

<div class="modrinth-grid">
    {% for mod in results %}
    <a href="{{ url_for('modrinth_project', slug=mod.slug) }}" class="mr-card">
        <div class="mr-card-icon">
            {% if mod.icon_url %}
                <img src="{{ mod.icon_url }}" alt="{{ mod.title }}">
            {% else %}
                <div class="mr-no-icon">📦</div>
            {% endif %}
        </div>
        <div class="mr-card-body">
            <div class="mr-card-header">
                <h3>{{ mod.title }}</h3>
                <span class="mr-author">{{ mod.author }}</span>
            </div>
            <p class="mr-desc">{{ mod.description[:140] }}{% if mod.description|length > 140 %}...{% endif %}</p>

            {% if mod.categories %}
            <div class="mr-categories">
                {% for cat in mod.categories[:4] %}
                    <span class="mr-tag">{{ cat }}</span>
                {% endfor %}
            </div>
            {% endif %}

            <div class="mr-stats">
                <span>⬇ {{ "{:,}".format(mod.downloads).replace(",", " ") }}</span>
                <span>⭐ {{ "{:,}".format(mod.follows).replace(",", " ") }}</span>
                {% if mod.versions %}
                    <span class="mr-version">MC {{ mod.versions[-1] }}</span>
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
        <a href="{{ url_for('modrinth_search', q=query, category=category, mc_version=mc_version, sort=sort, page=page-1) }}" class="page-btn">← Назад</a>
    {% endif %}

    <span class="page-info">Страница {{ page }} из {{ total_pages }}</span>

    {% if page < total_pages %}
        <a href="{{ url_for('modrinth_search', q=query, category=category, mc_version=mc_version, sort=sort, page=page+1) }}" class="page-btn">Вперёд →</a>
    {% endif %}
</div>
{% endif %}

<div class="modrinth-credits">
    Данные предоставлены <a href="https://modrinth.com" target="_blank">Modrinth</a>
</div>
{% endblock %}'''

with open("templates/modrinth_search.html", "w", encoding="utf-8") as f:
    f.write(modrinth_search_html)
print("  ✅ templates/modrinth_search.html")

# ============= СТРАНИЦА МОДА MODRINTH =============
modrinth_project_html = '''{% extends 'base.html' %}
{% block content %}

<a href="{{ url_for('modrinth_search') }}" class="back-btn">← К поиску Modrinth</a>

<div class="mr-project">

    <div class="mr-project-header">
        <div class="mr-project-icon">
            {% if project.icon_url %}
                <img src="{{ project.icon_url }}" alt="{{ project.title }}">
            {% else %}
                <div class="mr-no-icon-big">📦</div>
            {% endif %}
        </div>
        <div class="mr-project-info">
            <h1>{{ project.title }}</h1>
            <p class="mr-project-desc">{{ project.description }}</p>
            <div class="mr-project-stats">
                <span>⬇ {{ "{:,}".format(project.downloads).replace(",", " ") }}</span>
                <span>⭐ {{ "{:,}".format(project.followers).replace(",", " ") }}</span>
                <span>📅 {{ project.updated[:10] }}</span>
            </div>

            <div class="mr-project-categories">
                {% for cat in project.categories %}
                    <span class="mr-tag">{{ cat }}</span>
                {% endfor %}
            </div>
        </div>
    </div>

    {% if project.gallery %}
    <div class="screenshots-section">
        <h3>📸 Скриншоты</h3>
        <div class="screenshots-grid">
            {% for img in project.gallery[:6] %}
                <img src="{{ img.url }}" alt="{{ img.title or 'Screenshot' }}"
                     class="screenshot" onclick="openLightbox('{{ img.url }}')">
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <div class="mr-project-grid">
        <div class="mr-project-body">
            <div class="mod-description">
                <h3>📖 Описание</h3>
                <div class="mr-body-content">{{ project.body|safe }}</div>
            </div>
        </div>

        <div class="mr-project-sidebar">
            <a href="https://modrinth.com/mod/{{ project.slug }}" target="_blank" class="btn-modrinth">
                🌍 Открыть на Modrinth
            </a>

            <h3 class="mr-versions-title">📥 Скачать</h3>
            <div class="mr-versions-list">
                {% for v in versions[:10] %}
                    {% for f in v.files %}
                        {% if f.primary %}
                        <a href="{{ f.url }}" class="mr-version-item" download>
                            <div class="mr-v-info">
                                <div class="mr-v-name">{{ v.name }}</div>
                                <div class="mr-v-meta">
                                    {% if v.game_versions %}
                                    <span>MC {{ v.game_versions[0] }}</span>
                                    {% endif %}
                                    {% if v.loaders %}
                                    <span>{{ v.loaders[0]|title }}</span>
                                    {% endif %}
                                    <span>⬇ {{ "{:,}".format(v.downloads).replace(",", " ") }}</span>
                                </div>
                            </div>
                            <div class="mr-v-download">⬇</div>
                        </a>
                        {% endif %}
                    {% endfor %}
                {% endfor %}
            </div>

            {% if project.source_url %}
            <a href="{{ project.source_url }}" target="_blank" class="mr-extra-link">
                <span>💻</span> Исходный код
            </a>
            {% endif %}
            {% if project.wiki_url %}
            <a href="{{ project.wiki_url }}" target="_blank" class="mr-extra-link">
                <span>📚</span> Wiki
            </a>
            {% endif %}
            {% if project.discord_url %}
            <a href="{{ project.discord_url }}" target="_blank" class="mr-extra-link">
                <span>💬</span> Discord
            </a>
            {% endif %}
            {% if project.issues_url %}
            <a href="{{ project.issues_url }}" target="_blank" class="mr-extra-link">
                <span>🐛</span> Сообщить о баге
            </a>
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

with open("templates/modrinth_project.html", "w", encoding="utf-8") as f:
    f.write(modrinth_project_html)
print("  ✅ templates/modrinth_project.html")

# ============= CSS =============
extra_css = '''

/* ===== MODRINTH ===== */
.modrinth-item {
    color: #00d4ff !important;
    position: relative;
}

.modrinth-item::after {
    content: 'API';
    position: absolute;
    right: 12px;
    background: linear-gradient(135deg, #00d4ff, #00ff88);
    color: #000;
    font-size: 9px;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 800;
}

.modrinth-item:hover {
    background: rgba(0, 212, 255, 0.1) !important;
}

.modrinth-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.1));
    border: 1px solid rgba(0, 212, 255, 0.2);
    padding: 24px;
    border-radius: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 16px;
}

.modrinth-logo {
    display: flex;
    align-items: center;
    gap: 16px;
}

.mr-logo-icon {
    font-size: 48px;
    animation: floatIcon 3s ease-in-out infinite;
}

.modrinth-logo h1 {
    font-size: 28px;
    background: linear-gradient(135deg, #00d4ff, #00ff88);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.modrinth-logo p {
    color: var(--text-muted);
    font-size: 14px;
}

.modrinth-stats {
    background: var(--bg-card);
    padding: 12px 20px;
    border-radius: 12px;
    border: 1px solid var(--border);
}

.modrinth-stats strong {
    color: #00d4ff;
    font-size: 20px;
}

/* MR Grid */
.modrinth-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.mr-card {
    display: flex;
    gap: 16px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 18px;
    border-radius: 14px;
    text-decoration: none;
    color: inherit;
    transition: all 0.3s;
}

.mr-card:hover {
    transform: translateY(-4px);
    border-color: #00d4ff;
    box-shadow: 0 12px 30px rgba(0, 212, 255, 0.15);
}

.mr-card-icon {
    width: 80px;
    height: 80px;
    border-radius: 12px;
    overflow: hidden;
    flex-shrink: 0;
    background: var(--bg-main);
}

.mr-card-icon img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.mr-no-icon {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    background: linear-gradient(135deg, #00d4ff, #00ff88);
}

.mr-card-body {
    flex: 1;
    min-width: 0;
}

.mr-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 8px;
}

.mr-card-header h3 {
    font-size: 16px;
    margin-bottom: 2px;
    color: var(--text-main);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.mr-author {
    color: #00d4ff;
    font-size: 12px;
    font-weight: 600;
    flex-shrink: 0;
}

.mr-desc {
    color: var(--text-muted);
    font-size: 13px;
    line-height: 1.4;
    margin: 8px 0;
}

.mr-categories {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    margin-bottom: 8px;
}

.mr-tag {
    padding: 3px 8px;
    background: rgba(0, 212, 255, 0.1);
    color: #00d4ff;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    text-transform: capitalize;
}

.mr-stats {
    display: flex;
    gap: 12px;
    font-size: 12px;
    color: var(--text-muted);
    align-items: center;
    flex-wrap: wrap;
}

.mr-version {
    background: var(--bg-main);
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 600;
    color: var(--text-main);
}

/* Pagination */
.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 16px;
    margin: 30px 0;
}

.page-btn {
    padding: 10px 20px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    text-decoration: none;
    color: var(--text-main);
    font-weight: 600;
    transition: all 0.2s;
}

.page-btn:hover {
    border-color: #00d4ff;
    transform: translateY(-2px);
}

.page-info {
    color: var(--text-muted);
    font-weight: 600;
}

.modrinth-credits {
    text-align: center;
    color: var(--text-muted);
    font-size: 13px;
    padding: 20px;
}

.modrinth-credits a {
    color: #00d4ff;
    text-decoration: none;
}

/* MR Project Page */
.mr-project {
    animation: fadeIn 0.4s ease-out;
}

.mr-project-header {
    display: flex;
    gap: 24px;
    background: var(--bg-card);
    padding: 32px;
    border-radius: 20px;
    border: 1px solid var(--border);
    margin: 16px 0 24px;
    flex-wrap: wrap;
}

.mr-project-icon {
    width: 140px;
    height: 140px;
    border-radius: 18px;
    overflow: hidden;
    flex-shrink: 0;
    background: var(--bg-main);
}

.mr-project-icon img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.mr-no-icon-big {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 70px;
    background: linear-gradient(135deg, #00d4ff, #00ff88);
}

.mr-project-info { flex: 1; min-width: 250px; }

.mr-project-info h1 {
    font-size: 32px;
    margin-bottom: 8px;
}

.mr-project-desc {
    color: var(--text-muted);
    font-size: 16px;
    line-height: 1.5;
    margin-bottom: 12px;
}

.mr-project-stats {
    display: flex;
    gap: 16px;
    margin: 12px 0;
    color: var(--text-muted);
    font-size: 14px;
    flex-wrap: wrap;
}

.mr-project-categories {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-top: 12px;
}

.mr-project-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 24px;
}

.mr-project-body {
    background: var(--bg-card);
    padding: 24px;
    border-radius: 16px;
    border: 1px solid var(--border);
}

.mr-body-content {
    line-height: 1.7;
    color: var(--text-main);
    word-wrap: break-word;
    overflow-wrap: break-word;
}

.mr-body-content img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    margin: 10px 0;
}

.mr-body-content h1, .mr-body-content h2, .mr-body-content h3 {
    margin: 16px 0 10px;
    color: var(--accent);
}

.mr-body-content a {
    color: #00d4ff;
    text-decoration: underline;
}

.mr-body-content code {
    background: var(--bg-main);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 13px;
}

.mr-body-content pre {
    background: var(--bg-main);
    padding: 14px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 10px 0;
}

.mr-project-sidebar {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.btn-modrinth {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 14px;
    background: linear-gradient(135deg, #00d4ff, #00ff88);
    color: #000;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 700;
    transition: all 0.2s;
}

.btn-modrinth:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 212, 255, 0.4);
}

.mr-versions-title {
    color: var(--accent);
    margin: 8px 0;
}

.mr-versions-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 400px;
    overflow-y: auto;
}

.mr-version-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 14px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    text-decoration: none;
    color: var(--text-main);
    transition: all 0.2s;
}

.mr-version-item:hover {
    border-color: #00d4ff;
    background: rgba(0, 212, 255, 0.05);
}

.mr-v-info { flex: 1; min-width: 0; }

.mr-v-name {
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.mr-v-meta {
    display: flex;
    gap: 8px;
    font-size: 11px;
    color: var(--text-muted);
    flex-wrap: wrap;
}

.mr-v-meta span {
    background: var(--bg-main);
    padding: 2px 6px;
    border-radius: 4px;
}

.mr-v-download {
    font-size: 20px;
    color: #00d4ff;
    margin-left: 12px;
}

.mr-extra-link {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    text-decoration: none;
    color: var(--text-main);
    transition: all 0.2s;
}

.mr-extra-link:hover {
    border-color: #00d4ff;
}

.mr-extra-link span {
    font-size: 18px;
}

@media (max-width: 900px) {
    .mr-project-grid { grid-template-columns: 1fr; }
    .modrinth-grid { grid-template-columns: 1fr; }
}
'''

css_path = "static/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    existing_css = f.read()

if "/* ===== MODRINTH ===== */" not in existing_css:
    with open(css_path, "a", encoding="utf-8") as f:
        f.write(extra_css)
    print(f"  ✅ {css_path}")
else:
    marker = "/* ===== MODRINTH ===== */"
    new_css = existing_css.split(marker)[0] + extra_css
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(new_css)
    print(f"  ✅ {css_path} (обновлено)")

print("\n🎉 ЭТАП 9 ГОТОВ!")
print("\n✨ Добавлено:")
print("   🌍 Поиск по Modrinth прямо на сайте")
print("   🔍 Фильтры (категория, версия MC)")
print("   📊 5 видов сортировки")
print("   📄 Пагинация результатов")
print("   📥 Скачивание .jar напрямую с Modrinth")
print("   🖼️ Иконки, скриншоты, описания")
print("   💬 Ссылки на Discord, Wiki, Issues")
print("   🎨 Красивая отдельная цветовая схема (голубой)")
print("\n📤 git add . && git commit -m 'v10: Modrinth API integration' && git push --force origin main")
print("На PA: cd ~/mysite && git fetch origin main && git reset --hard origin/main && Reload")
print("\n👉 После применения в меню появится пункт 🌍 Modrinth API")