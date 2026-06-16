# -*- coding: utf-8 -*-
import os

print("🔧 Убираю из меню, добавляю в Modrinth и GitHub...")

# ============= ПАТЧИМ base.html — убираем лишние пункты =============
with open("templates/base.html", "r", encoding="utf-8") as f:
    base_html = f.read()

# Удаляем весь раздел КАТАЛОГ с типами контента
old_section = '''<div class="nav-section-title">КАТАЛОГ</div>
            <a href="{{ url_for('index', type='mod') }}" class="nav-item">
                <span class="nav-icon">⛏</span><span>Моды</span>
            </a>
            <a href="{{ url_for('index', type='shader') }}" class="nav-item">
                <span class="nav-icon">🌅</span><span>Шейдеры</span>
            </a>
            <a href="{{ url_for('index', type='plugin') }}" class="nav-item">
                <span class="nav-icon">🔌</span><span>Плагины</span>
            </a>
            <a href="{{ url_for('index', type='resourcepack') }}" class="nav-item">
                <span class="nav-icon">🎨</span><span>Ресурспаки</span>
            </a>
            <a href="{{ url_for('index', type='modpack') }}" class="nav-item">
                <span class="nav-icon">📦</span><span>Сборки</span>
            </a>
            <a href="{{ url_for('index', type='map') }}" class="nav-item">
                <span class="nav-icon">🗺️</span><span>Карты</span>
            </a>
            <a href="{{ url_for('index', type='datapack') }}" class="nav-item">
                <span class="nav-icon">📝</span><span>Датапаки</span>
            </a>
            <div class="nav-section-title">ПОИСК</div>
            <a href="{{ url_for('modrinth_search') }}" class="nav-item modrinth-item">
                <span class="nav-icon">🌍</span><span>Modrinth</span>
            </a>
            <a href="{{ url_for('github_search') }}" class="nav-item github-item">
                <span class="nav-icon">🦊</span><span>GitHub</span>
            </a>'''

new_section = '''<a href="{{ url_for('modrinth_search') }}" class="nav-item modrinth-item">
                <span class="nav-icon">🌍</span><span>Modrinth</span>
            </a>
            <a href="{{ url_for('github_search') }}" class="nav-item github-item">
                <span class="nav-icon">🦊</span><span>GitHub</span>
            </a>'''

base_html = base_html.replace(old_section, new_section)

with open("templates/base.html", "w", encoding="utf-8") as f:
    f.write(base_html)
print("  ✅ templates/base.html (меню очищено)")

# ============= ПАТЧИМ GitHub — добавляем переключатель типов =============
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# Обновляем github_search чтобы поддерживал тип контента
old_gh = '''@app.route('/github')
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
    }'''

new_gh = '''@app.route('/github')
@app.route('/github/<content_type>')
def github_search(content_type='mod'):
    query = request.args.get('q', '')
    sort = request.args.get('sort', 'stars')
    page = int(request.args.get('page', 1))

    # Ключевые слова для разных типов
    type_keywords = {
        'mod': 'minecraft mod',
        'shader': 'minecraft shader',
        'plugin': 'minecraft plugin spigot',
        'resourcepack': 'minecraft resourcepack',
        'modpack': 'minecraft modpack',
        'datapack': 'minecraft datapack',
        'map': 'minecraft map',
    }
    type_lang = {
        'mod': 'language:Java',
        'plugin': 'language:Java',
        'shader': 'language:GLSL OR language:Shaderlab',
        'resourcepack': '',
        'modpack': '',
        'datapack': 'language:mcfunction',
        'map': '',
    }

    valid_types = list(type_keywords.keys())
    if content_type not in valid_types:
        content_type = 'mod'

    base_kw = type_keywords[content_type]
    lang = type_lang[content_type]

    if query:
        search_q = f"{query} {base_kw}"
    else:
        search_q = base_kw

    if lang:
        search_q += f" {lang}"

    params = {
        'q': search_q,
        'sort': sort,
        'order': 'desc',
        'per_page': 20,
        'page': page,
    }'''

app_code = app_code.replace(old_gh, new_gh)

# Передаём content_type в шаблон GitHub
old_gh_render = '''return render_template('github_search.html',
        results=results, query=query, sort=sort,
        page=page, total=total, total_pages=total_pages)'''

new_gh_render = '''content_types = [
        ('mod', 'Моды', '⛏'),
        ('shader', 'Шейдеры', '🌅'),
        ('plugin', 'Плагины', '🔌'),
        ('resourcepack', 'Ресурспаки', '🎨'),
        ('modpack', 'Сборки', '📦'),
        ('datapack', 'Датапаки', '📝'),
        ('map', 'Карты', '🗺️'),
    ]
    return render_template('github_search.html',
        results=results, query=query, sort=sort,
        page=page, total=total, total_pages=total_pages,
        content_type=content_type, content_types=content_types)'''

app_code = app_code.replace(old_gh_render, new_gh_render)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)
print("  ✅ app.py")

# ============= ОБНОВЛЯЕМ github_search.html — добавляем вкладки =============
github_search_html = '''{% extends 'base.html' %}
{% block content %}

<div class="content-type-tabs mr-type-tabs">
    {% for tk, tn, ti in content_types %}
    <a href="{{ url_for('github_search', content_type=tk) }}" class="ct-tab {% if content_type == tk %}active{% endif %}">
        <span class="ct-icon">{{ ti }}</span>
        <span>{{ tn }}</span>
    </a>
    {% endfor %}
</div>

<div class="github-header">
    <div class="gh-logo">
        <div class="gh-logo-icon">🦊</div>
        <div>
            <h1>GitHub</h1>
            <p>Open-source проекты Minecraft</p>
        </div>
    </div>
    <div class="gh-stats">
        <strong>{{ total }}</strong> репозиториев
    </div>
</div>

<div class="search-bar">
    <form method="GET" action="{{ url_for('github_search', content_type=content_type) }}">
        <div class="search-input-wrap">
            <span class="search-icon">🔍</span>
            <input type="text" name="q" placeholder="Поиск (например: sodium, complementary, essentials)..." value="{{ query }}" autofocus>
        </div>
        <button type="submit">Найти</button>
    </form>
</div>

<div class="sort-tabs">
    <a href="{{ url_for('github_search', content_type=content_type, q=query, sort='stars') }}"
       class="sort-tab {% if sort == 'stars' %}active{% endif %}">⭐ Звёзды</a>
    <a href="{{ url_for('github_search', content_type=content_type, q=query, sort='forks') }}"
       class="sort-tab {% if sort == 'forks' %}active{% endif %}">🍴 Форки</a>
    <a href="{{ url_for('github_search', content_type=content_type, q=query, sort='updated') }}"
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
        <a href="{{ url_for('github_search', content_type=content_type, q=query, sort=sort, page=page-1) }}" class="page-btn">← Назад</a>
    {% endif %}
    <span class="page-info">Страница {{ page }} из {{ total_pages }}</span>
    {% if page < total_pages %}
        <a href="{{ url_for('github_search', content_type=content_type, q=query, sort=sort, page=page+1) }}" class="page-btn">Вперёд →</a>
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

# ============= УБИРАЕМ ВКЛАДКИ ТИПОВ С ГЛАВНОЙ =============
with open("templates/index.html", "r", encoding="utf-8") as f:
    index_html = f.read()

# Удаляем вкладки content-type-tabs с главной
old_tabs = '''<div class="content-type-tabs">
    {% for tk, tn, ti in content_types_list %}
    <a href="{{ url_for('index', type=tk) }}" class="ct-tab {% if content_type == tk %}active{% endif %}">
        <span class="ct-icon">{{ ti }}</span>
        <span>{{ tn }}</span>
    </a>
    {% endfor %}
</div>

<div class="search-bar">'''

new_tabs = '<div class="search-bar">'

index_html = index_html.replace(old_tabs, new_tabs)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)
print("  ✅ templates/index.html (убраны вкладки)")

print("\n🎉 ГОТОВО!")
print("\n✨ Что изменилось:")
print("   🗑️ Убраны из бокового меню: Шейдеры, Плагины, Ресурспаки, Сборки, Карты, Датапаки")
print("   🌍 На Modrinth — переключатель типов сверху")
print("   🦊 На GitHub — переключатель типов сверху")
print("   📋 GitHub теперь ищет шейдеры, плагины и т.д. с умными ключевыми словами")
print("\n📤 git add . && git commit -m 'v16: cleanup menu, add types to GitHub' && git push --force origin main")
print("На PA: cd ~/mysite && git fetch origin main && git reset --hard origin/main && Reload")