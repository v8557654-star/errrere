# -*- coding: utf-8 -*-
import os

print("🚀 Добавляю GitHub поиск модов...")

# ============= ПАТЧИМ app.py =============
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# Добавляем роуты GitHub перед "with app.app_context():"
github_routes = '''
# ===== GITHUB API =====
GITHUB_API = "https://api.github.com"
GITHUB_HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "MineMods/1.0",
}

@app.route('/github')
def github_search():
    query = request.args.get('q', 'minecraft mod')
    sort = request.args.get('sort', 'stars')  # stars, forks, updated
    page = int(request.args.get('page', 1))

    # Добавляем minecraft если не указано
    search_q = query if 'minecraft' in query.lower() else f"{query} minecraft mod"

    params = {
        'q': search_q + ' language:Java',
        'sort': sort,
        'order': 'desc',
        'per_page': 20,
        'page': page,
    }

    try:
        r = requests.get(f"{GITHUB_API}/search/repositories", params=params,
                        headers=GITHUB_HEADERS, timeout=10)
        data = r.json()
        results = data.get('items', [])
        total = min(data.get('total_count', 0), 1000)  # GitHub лимит 1000
    except Exception as e:
        results = []
        total = 0
        flash(f'Ошибка GitHub: {str(e)}', 'error')

    total_pages = min((total + 19) // 20, 50)

    return render_template('github_search.html',
        results=results, query=query, sort=sort,
        page=page, total=total, total_pages=total_pages)

@app.route('/github/repo/<owner>/<repo>')
def github_repo(owner, repo):
    try:
        # Инфо о репозитории
        r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}",
                        headers=GITHUB_HEADERS, timeout=10)
        if r.status_code != 200:
            flash('Репозиторий не найден', 'error')
            return redirect(url_for('github_search'))
        repo_data = r.json()

        # Релизы
        rel = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/releases",
                          headers=GITHUB_HEADERS, timeout=10, params={'per_page': 10})
        releases = rel.json() if rel.status_code == 200 else []

        # README
        readme_text = ''
        try:
            rd = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/readme",
                            headers={**GITHUB_HEADERS, 'Accept': 'application/vnd.github.html'},
                            timeout=10)
            if rd.status_code == 200:
                readme_text = rd.text
        except: pass

    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('github_search'))

    return render_template('github_repo.html',
                          repo=repo_data, releases=releases, readme=readme_text)
'''

if "GITHUB_API = " not in app_code:
    app_code = app_code.replace(
        "with app.app_context():",
        github_routes + "\nwith app.app_context():"
    )

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)
print("  ✅ app.py")

# ============= ОБНОВЛЯЕМ base.html =============
with open("templates/base.html", "r", encoding="utf-8") as f:
    base_html = f.read()

if "github-item" not in base_html:
    old = '''<a href="{{ url_for('modrinth_search') }}" class="nav-item modrinth-item">
                <span class="nav-icon">🌍</span><span>Modrinth</span>
            </a>'''

    new = '''<a href="{{ url_for('modrinth_search') }}" class="nav-item modrinth-item">
                <span class="nav-icon">🌍</span><span>Modrinth</span>
            </a>
            <a href="{{ url_for('github_search') }}" class="nav-item github-item">
                <span class="nav-icon">🦊</span><span>GitHub</span>
            </a>'''

    base_html = base_html.replace(old, new)

with open("templates/base.html", "w", encoding="utf-8") as f:
    f.write(base_html)
print("  ✅ templates/base.html")

# ============= СТРАНИЦА ПОИСКА GitHub =============
github_search_html = '''{% extends 'base.html' %}
{% block content %}

<div class="github-header">
    <div class="gh-logo">
        <div class="gh-logo-icon">🦊</div>
        <div>
            <h1>GitHub</h1>
            <p>Open-source моды и проекты</p>
        </div>
    </div>
    <div class="gh-stats">
        <strong>{{ total }}</strong> репозиториев найдено
    </div>
</div>

<div class="search-bar">
    <form method="GET" action="{{ url_for('github_search') }}">
        <div class="search-input-wrap">
            <span class="search-icon">🔍</span>
            <input type="text" name="q" placeholder="Поиск (например: sodium, optifine, create)..." value="{{ query }}" autofocus>
        </div>
        <button type="submit">Найти</button>
    </form>
</div>

<div class="sort-tabs">
    <a href="{{ url_for('github_search', q=query, sort='stars') }}"
       class="sort-tab {% if sort == 'stars' %}active{% endif %}">⭐ Звёзды</a>
    <a href="{{ url_for('github_search', q=query, sort='forks') }}"
       class="sort-tab {% if sort == 'forks' %}active{% endif %}">🍴 Форки</a>
    <a href="{{ url_for('github_search', q=query, sort='updated') }}"
       class="sort-tab {% if sort == 'updated' %}active{% endif %}">🔄 Обновлённые</a>
</div>

<div class="modrinth-grid">
    {% for repo in results %}
    <a href="{{ url_for('github_repo', owner=repo.owner.login, repo=repo.name) }}" class="mr-card gh-card">
        <div class="mr-card-icon">
            <img src="{{ repo.owner.avatar_url }}" alt="{{ repo.owner.login }}">
        </div>
        <div class="mr-card-body">
            <div class="mr-card-header">
                <h3>{{ repo.name }}</h3>
                <span class="gh-author">{{ repo.owner.login }}</span>
            </div>
            <p class="mr-desc">{{ (repo.description or 'Без описания')[:140] }}{% if repo.description and repo.description|length > 140 %}...{% endif %}</p>

            {% if repo.topics %}
            <div class="mr-categories">
                {% for topic in repo.topics[:4] %}
                    <span class="mr-tag gh-tag">{{ topic }}</span>
                {% endfor %}
            </div>
            {% endif %}

            <div class="mr-stats">
                <span>⭐ {{ "{:,}".format(repo.stargazers_count).replace(",", " ") }}</span>
                <span>🍴 {{ repo.forks_count }}</span>
                {% if repo.language %}<span class="gh-lang">{{ repo.language }}</span>{% endif %}
                <span>📅 {{ repo.updated_at[:10] }}</span>
            </div>
        </div>
    </a>
    {% else %}
        <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <h3>Ничего не найдено</h3>
            <p>Попробуй другой запрос</p>
        </div>
    {% endfor %}
</div>

{% if total_pages > 1 %}
<div class="pagination">
    {% if page > 1 %}
        <a href="{{ url_for('github_search', q=query, sort=sort, page=page-1) }}" class="page-btn">← Назад</a>
    {% endif %}
    <span class="page-info">Страница {{ page }} из {{ total_pages }}</span>
    {% if page < total_pages %}
        <a href="{{ url_for('github_search', q=query, sort=sort, page=page+1) }}" class="page-btn">Вперёд →</a>
    {% endif %}
</div>
{% endif %}

<div class="modrinth-credits">
    Данные предоставлены <a href="https://github.com" target="_blank">GitHub</a>
</div>
{% endblock %}'''

with open("templates/github_search.html", "w", encoding="utf-8") as f:
    f.write(github_search_html)
print("  ✅ templates/github_search.html")

# ============= СТРАНИЦА РЕПОЗИТОРИЯ =============
github_repo_html = '''{% extends 'base.html' %}
{% block content %}

<a href="{{ url_for('github_search') }}" class="back-btn">← К поиску GitHub</a>

<div class="mr-project gh-project">

    <div class="mr-project-header">
        <div class="mr-project-icon">
            <img src="{{ repo.owner.avatar_url }}" alt="{{ repo.owner.login }}">
        </div>
        <div class="mr-project-info">
            <h1>{{ repo.name }}</h1>
            <p class="mr-project-desc">{{ repo.description or 'Без описания' }}</p>
            <div class="mr-project-stats">
                <span>⭐ {{ "{:,}".format(repo.stargazers_count).replace(",", " ") }}</span>
                <span>🍴 {{ repo.forks_count }}</span>
                <span>👁 {{ repo.watchers_count }}</span>
                {% if repo.language %}<span class="gh-lang">{{ repo.language }}</span>{% endif %}
                <span>📅 {{ repo.updated_at[:10] }}</span>
            </div>

            {% if repo.topics %}
            <div class="mr-project-categories">
                {% for topic in repo.topics %}
                    <span class="mr-tag gh-tag">{{ topic }}</span>
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>

    <div class="mr-project-grid">
        <div class="mr-project-body">
            <div class="mod-description">
                <h3>📖 README</h3>
                {% if readme %}
                <div class="mr-body-content gh-readme">{{ readme|safe }}</div>
                {% else %}
                <p>README не найден</p>
                {% endif %}
            </div>
        </div>

        <div class="mr-project-sidebar">
            <a href="{{ repo.html_url }}" target="_blank" class="btn-github">
                🦊 Открыть на GitHub
            </a>

            {% if releases %}
            <h3 class="mr-versions-title">📥 Скачать .jar</h3>
            <div class="mr-versions-list">
                {% for release in releases %}
                    {% for asset in release.assets %}
                        {% if asset.name.endswith('.jar') %}
                        <a href="{{ asset.browser_download_url }}" class="mr-version-item gh-version-item" download target="_blank">
                            <div class="mr-v-info">
                                <div class="mr-v-name">{{ release.name or release.tag_name }}</div>
                                <div class="mr-v-meta">
                                    <span>{{ asset.name[:40] }}</span>
                                    <span>⬇ {{ "{:,}".format(asset.download_count).replace(",", " ") }}</span>
                                    <span>{{ (asset.size / 1024 / 1024)|round(1) }} МБ</span>
                                </div>
                            </div>
                            <div class="mr-v-download">⬇</div>
                        </a>
                        {% endif %}
                    {% endfor %}
                {% endfor %}
            </div>
            {% else %}
            <div class="no-releases">
                <p>📦 Нет релизов с .jar файлами</p>
                <p style="font-size: 12px; color: var(--text-muted); margin-top: 8px;">Можешь склонировать репозиторий и собрать сам</p>
            </div>
            {% endif %}

            <a href="{{ repo.clone_url }}" class="mr-extra-link" onclick="navigator.clipboard.writeText('{{ repo.clone_url }}'); event.preventDefault(); this.querySelector('.copy-text').textContent='✓ Скопировано'">
                <span>📋</span>
                <span class="copy-text">Copy git clone URL</span>
            </a>

            {% if repo.homepage %}
            <a href="{{ repo.homepage }}" target="_blank" class="mr-extra-link">
                <span>🌐</span> Веб-сайт
            </a>
            {% endif %}

            <a href="{{ repo.html_url }}/issues" target="_blank" class="mr-extra-link">
                <span>🐛</span> Issues ({{ repo.open_issues_count }})
            </a>

            <a href="{{ repo.html_url }}/wiki" target="_blank" class="mr-extra-link">
                <span>📚</span> Wiki
            </a>

            {% if repo.license %}
            <div class="gh-license">
                <span>⚖️ Лицензия:</span>
                <strong>{{ repo.license.name }}</strong>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}'''

with open("templates/github_repo.html", "w", encoding="utf-8") as f:
    f.write(github_repo_html)
print("  ✅ templates/github_repo.html")

# ============= CSS =============
extra_css = '''

/* ===== GITHUB ===== */
.github-item {
    color: #a855f7 !important;
    position: relative;
}

.github-item::after {
    content: 'API';
    position: absolute;
    right: 12px;
    background: linear-gradient(135deg, #a855f7, #ec4899);
    color: #fff;
    font-size: 9px;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 800;
}

.github-item:hover {
    background: rgba(168, 85, 247, 0.1) !important;
}

.github-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(236, 72, 153, 0.1));
    border: 1px solid rgba(168, 85, 247, 0.2);
    padding: 24px;
    border-radius: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 16px;
}

.gh-logo {
    display: flex;
    align-items: center;
    gap: 16px;
}

.gh-logo-icon {
    font-size: 48px;
    animation: floatIcon 3s ease-in-out infinite;
}

.gh-logo h1 {
    font-size: 28px;
    background: linear-gradient(135deg, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.gh-logo p {
    color: var(--text-muted);
    font-size: 14px;
}

.gh-stats {
    background: var(--bg-card);
    padding: 12px 20px;
    border-radius: 12px;
    border: 1px solid var(--border);
}

.gh-stats strong {
    color: #a855f7;
    font-size: 20px;
}

.gh-card:hover {
    border-color: #a855f7 !important;
    box-shadow: 0 12px 30px rgba(168, 85, 247, 0.15) !important;
}

.gh-author {
    color: #a855f7 !important;
}

.gh-tag {
    background: rgba(168, 85, 247, 0.1) !important;
    color: #a855f7 !important;
}

.gh-lang {
    background: rgba(168, 85, 247, 0.15) !important;
    color: #a855f7 !important;
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 600;
}

.btn-github {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 14px;
    background: linear-gradient(135deg, #a855f7, #ec4899);
    color: #fff;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 700;
    transition: all 0.2s;
}

.btn-github:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(168, 85, 247, 0.4);
}

.gh-version-item:hover {
    border-color: #a855f7 !important;
    background: rgba(168, 85, 247, 0.05) !important;
}

.no-releases {
    background: var(--bg-card);
    border: 1px dashed var(--border);
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: var(--text-muted);
}

.gh-license {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 12px 14px;
    border-radius: 10px;
    font-size: 13px;
}

.gh-license span {
    color: var(--text-muted);
}

.gh-license strong {
    color: #a855f7;
    margin-left: 6px;
}

.gh-readme {
    max-height: 800px;
    overflow-y: auto;
    padding-right: 10px;
}

.gh-readme img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
}

.gh-readme pre {
    background: var(--bg-main) !important;
    overflow-x: auto;
    padding: 12px;
    border-radius: 8px;
}

.gh-readme table {
    border-collapse: collapse;
    margin: 10px 0;
}

.gh-readme table td, .gh-readme table th {
    border: 1px solid var(--border);
    padding: 8px 12px;
}
'''

css_path = "static/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    existing_css = f.read()

if "/* ===== GITHUB ===== */" not in existing_css:
    with open(css_path, "a", encoding="utf-8") as f:
        f.write(extra_css)
    print(f"  ✅ {css_path}")

print("\n🎉 GitHub интеграция готова!")
print("\n✨ Что нового:")
print("   🦊 Поиск по GitHub репозиториям")
print("   ⭐ Сортировка: звёзды, форки, обновлённые")
print("   📥 Прямое скачивание .jar из релизов")
print("   📖 README прямо на странице")
print("   📋 Копирование git clone URL")
print("   ⚖️ Информация о лицензии")
print("   🎨 Фиолетовая цветовая схема")
print("\n📤 git add . && git commit -m 'v12: GitHub integration' && git push --force origin main")
print("На PA: cd ~/mysite && git fetch origin main && git reset --hard origin/main && Reload")
print("\n💡 Попробуй найти: 'sodium', 'iris', 'create', 'fabric api'")