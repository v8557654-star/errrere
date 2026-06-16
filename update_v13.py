# -*- coding: utf-8 -*-
import os
import re

print("🔧 Исправляю отображение версий мода и Minecraft...")

# ============= ПАТЧИМ app.py — добавляем умный парсер версий =============
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# Добавляем функцию парсинга версий перед роутами Modrinth
version_parser = '''
# ===== УТИЛИТЫ ДЛЯ ВЕРСИЙ =====
import re as _re_versions

def parse_mc_versions(versions_list):
    """Извлекает версии Minecraft из списка (отсеивает loader и snapshot)"""
    if not versions_list:
        return []
    mc_versions = []
    for v in versions_list:
        # Пропускаем не-MC версии (loader, snapshot и т.д.)
        if any(x in str(v).lower() for x in ['forge-', 'fabric-', 'quilt-', 'neoforge-', 'snapshot', 'pre', 'rc']):
            continue
        # Берём только версии формата 1.X.X или 1.X
        if _re_versions.match(r'^1\\.\\d+(\\.\\d+)?$', str(v)):
            mc_versions.append(v)
    return mc_versions

def format_mc_versions(versions_list, max_show=3):
    """Красиво форматирует список версий MC"""
    mc = parse_mc_versions(versions_list)
    if not mc:
        return "—"
    # Сортируем (новые впереди)
    try:
        mc_sorted = sorted(mc, key=lambda v: [int(x) for x in v.split('.')], reverse=True)
    except:
        mc_sorted = mc

    if len(mc_sorted) <= max_show:
        return ", ".join(mc_sorted)
    return f"{mc_sorted[0]} ... {mc_sorted[-1]} ({len(mc_sorted)} версий)"

def detect_mod_loader(versions_list, loaders_list=None):
    """Определяет загрузчик (Forge/Fabric/Quilt)"""
    loaders = set()
    if loaders_list:
        for l in loaders_list:
            loaders.add(l.title())
    if versions_list:
        for v in versions_list:
            vl = str(v).lower()
            if 'forge' in vl: loaders.add('Forge')
            if 'fabric' in vl: loaders.add('Fabric')
            if 'quilt' in vl: loaders.add('Quilt')
            if 'neoforge' in vl: loaders.add('NeoForge')
    return list(loaders)

# Делаем доступными в шаблонах
app.jinja_env.globals['parse_mc_versions'] = parse_mc_versions
app.jinja_env.globals['format_mc_versions'] = format_mc_versions
app.jinja_env.globals['detect_mod_loader'] = detect_mod_loader

'''

if "def parse_mc_versions" not in app_code:
    app_code = app_code.replace(
        "# ===== MODRINTH API =====",
        version_parser + "\n# ===== MODRINTH API =====",
        1
    )

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)
print("  ✅ app.py (добавлены парсеры версий)")

# ============= ОБНОВЛЯЕМ modrinth_search.html =============
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
            <option value="">Все версии MC</option>
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

            <div class="version-info">
                {% set mc_vers = parse_mc_versions(mod.versions) %}
                {% if mc_vers %}
                <span class="v-badge v-mc">
                    <span class="v-label">MC:</span>
                    <strong>{{ format_mc_versions(mod.versions, 2) }}</strong>
                </span>
                {% endif %}

                {% set loaders = detect_mod_loader(mod.versions, mod.loaders if mod.loaders else []) %}
                {% if loaders %}
                <span class="v-badge v-loader">
                    {% for l in loaders[:2] %}{{ l }}{% if not loop.last %}/{% endif %}{% endfor %}
                </span>
                {% endif %}
            </div>

            <div class="mr-stats">
                <span>⬇ {{ "{:,}".format(mod.downloads).replace(",", " ") }}</span>
                <span>⭐ {{ "{:,}".format(mod.follows).replace(",", " ") }}</span>
            </div>
        </div>
    </a>
    {% else %}
        <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <h3>Ничего не найдено</h3>
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

# ============= ОБНОВЛЯЕМ modrinth_project.html =============
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

            <div class="project-versions-info">
                {% if project.game_versions %}
                <div class="pvi-block">
                    <div class="pvi-label">🎮 Версии Minecraft</div>
                    <div class="pvi-versions">
                        {% set mc_sorted = parse_mc_versions(project.game_versions) %}
                        {% for v in mc_sorted[:8] %}
                            <span class="pvi-chip">MC {{ v }}</span>
                        {% endfor %}
                        {% if mc_sorted|length > 8 %}
                            <span class="pvi-chip-more">+{{ mc_sorted|length - 8 }}</span>
                        {% endif %}
                    </div>
                </div>
                {% endif %}

                {% if project.loaders %}
                <div class="pvi-block">
                    <div class="pvi-label">⚙️ Загрузчики</div>
                    <div class="pvi-versions">
                        {% for l in project.loaders %}
                            <span class="pvi-chip pvi-loader">{{ l|title }}</span>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}
            </div>

            {% if project.categories %}
            <div class="mr-project-categories">
                {% for cat in project.categories %}
                    <span class="mr-tag">{{ cat }}</span>
                {% endfor %}
            </div>
            {% endif %}
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
                {% for v in versions[:15] %}
                    {% for f in v.files %}
                        {% if f.primary %}
                        <a href="{{ f.url }}" class="mr-version-item" download target="_blank">
                            <div class="mr-v-info">
                                <div class="mr-v-name">{{ v.name }}</div>
                                <div class="mr-v-meta">
                                    {% set v_mc = parse_mc_versions(v.game_versions) %}
                                    {% if v_mc %}
                                        <span class="meta-mc">🎮 MC {{ v_mc[0] }}{% if v_mc|length > 1 %}+{% endif %}</span>
                                    {% endif %}
                                    {% if v.loaders %}
                                        <span class="meta-loader">⚙️ {{ v.loaders[0]|title }}</span>
                                    {% endif %}
                                    {% if v.version_type %}
                                        <span class="meta-type type-{{ v.version_type }}">{{ v.version_type|title }}</span>
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

/* ===== ВЕРСИИ — ЧИПЫ И БЕЙДЖИ ===== */
.version-info {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin: 8px 0;
}

.v-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    background: var(--bg-main);
    border: 1px solid var(--border);
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
}

.v-badge .v-label {
    color: var(--text-muted);
    font-weight: 500;
}

.v-mc {
    border-color: rgba(0, 212, 255, 0.3);
    color: #00d4ff;
}

.v-mc strong {
    color: var(--text-main);
}

.v-loader {
    border-color: rgba(168, 85, 247, 0.3);
    color: #a855f7;
    text-transform: capitalize;
}

/* Информация о версиях в карточке проекта */
.project-versions-info {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin: 16px 0;
    background: var(--bg-main);
    padding: 14px;
    border-radius: 12px;
}

.pvi-block {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.pvi-label {
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.pvi-versions {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.pvi-chip {
    padding: 4px 10px;
    background: rgba(0, 212, 255, 0.1);
    color: #00d4ff;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
    border: 1px solid rgba(0, 212, 255, 0.2);
}

.pvi-chip-more {
    padding: 4px 10px;
    background: var(--bg-card);
    color: var(--text-muted);
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
    border: 1px solid var(--border);
}

.pvi-chip.pvi-loader {
    background: rgba(168, 85, 247, 0.1);
    color: #a855f7;
    border-color: rgba(168, 85, 247, 0.2);
}

/* Метки в списке файлов */
.mr-v-meta .meta-mc {
    background: rgba(0, 212, 255, 0.15) !important;
    color: #00d4ff !important;
    font-weight: 700;
}

.mr-v-meta .meta-loader {
    background: rgba(168, 85, 247, 0.15) !important;
    color: #a855f7 !important;
    font-weight: 600;
}

.mr-v-meta .meta-type {
    font-weight: 700;
    font-size: 10px !important;
    text-transform: uppercase;
    padding: 2px 6px !important;
}

.meta-type.type-release {
    background: rgba(74, 222, 128, 0.15) !important;
    color: #4ade80 !important;
}

.meta-type.type-beta {
    background: rgba(251, 191, 36, 0.15) !important;
    color: #fbbf24 !important;
}

.meta-type.type-alpha {
    background: rgba(239, 68, 68, 0.15) !important;
    color: #ef4444 !important;
}

@media (max-width: 600px) {
    .pvi-versions { gap: 4px; }
    .pvi-chip { padding: 3px 8px; font-size: 11px; }
}
'''

css_path = "static/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    existing_css = f.read()

if "/* ===== ВЕРСИИ — ЧИПЫ И БЕЙДЖИ ===== */" not in existing_css:
    with open(css_path, "a", encoding="utf-8") as f:
        f.write(extra_css)
    print(f"  ✅ {css_path}")

print("\n🎉 ГОТОВО!")
print("\n✨ Что исправлено:")
print("   🎮 На карточках мода — версия MC видна отдельно")
print("   ⚙️ Видно загрузчик (Forge / Fabric / Quilt / NeoForge)")
print("   🏷️ На странице мода — все версии MC чипами")
print("   📥 В списке файлов — конкретная MC версия и загрузчик")
print("   🎨 Цветные метки типа: Release (зелёный), Beta (жёлтый), Alpha (красный)")
print("\n📤 git add . && git commit -m 'v13: fix version display' && git push --force origin main")
print("На PA: cd ~/mysite && git fetch origin main && git reset --hard origin/main && Reload")