# -*- coding: utf-8 -*-
import os

print("🚀 Добавляю шейдеры, плагины, ресурспаки, карты, сборки, датапаки...")

# ============= ПАТЧИМ app.py — добавляем типы контента =============
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# Заменяем поле category в Mod на content_type + category
# Добавляем content_type в модель Mod
if 'content_type = db.Column' not in app_code:
    app_code = app_code.replace(
        "category = db.Column(db.String(50), nullable=False)",
        "content_type = db.Column(db.String(30), default='mod')\n    category = db.Column(db.String(50), nullable=False)",
        1
    )

# Заменяем роуты модринта - теперь они принимают тип контента
old_modrinth = '''@app.route('/modrinth')
def modrinth_search():
    query = request.args.get('q', '')
    mc_version = request.args.get('mc_version', '')
    category = request.args.get('category', '')
    sort = request.args.get('sort', 'relevance')  # relevance, downloads, follows, newest, updated
    page = int(request.args.get('page', 1))
    limit = 20
    offset = (page - 1) * limit

    # Формируем facets для фильтров
    facets = [["project_type:mod"]]'''

new_modrinth = '''@app.route('/modrinth')
@app.route('/modrinth/<project_type>')
def modrinth_search(project_type='mod'):
    query = request.args.get('q', '')
    mc_version = request.args.get('mc_version', '')
    category = request.args.get('category', '')
    sort = request.args.get('sort', 'relevance')
    page = int(request.args.get('page', 1))
    limit = 20
    offset = (page - 1) * limit

    # Валидация типа
    valid_types = ['mod', 'shader', 'plugin', 'resourcepack', 'modpack', 'datapack']
    if project_type not in valid_types:
        project_type = 'mod'

    facets = [[f"project_type:{project_type}"]]'''

app_code = app_code.replace(old_modrinth, new_modrinth)

# Добавляем передачу project_type в шаблон
old_render = '''return render_template('modrinth_search.html',
        results=results, query=query, mc_version=mc_version, category=category,
        sort=sort, page=page, total=total, total_pages=total_pages,
        mr_categories=mr_categories, versions=versions)'''

new_render = '''content_types = [
        ('mod', 'Моды', '⛏'),
        ('shader', 'Шейдеры', '🌅'),
        ('plugin', 'Плагины', '🔌'),
        ('resourcepack', 'Ресурспаки', '🎨'),
        ('modpack', 'Сборки', '📦'),
        ('datapack', 'Датапаки', '📝'),
    ]
    return render_template('modrinth_search.html',
        results=results, query=query, mc_version=mc_version, category=category,
        sort=sort, page=page, total=total, total_pages=total_pages,
        mr_categories=mr_categories, versions=versions,
        project_type=project_type, content_types=content_types)'''

app_code = app_code.replace(old_render, new_render)

# Обновляем upload — добавляем content_type
old_upload = '''@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    categories = ['Магия', 'Техника', 'Оружие', 'Мобы', 'Декор', 'Еда', 'Миры', 'Утилиты', 'Другое']'''

new_upload = '''@app.route('/upload', methods=['GET', 'POST'])
@app.route('/upload/<content_type>', methods=['GET', 'POST'])
@login_required
def upload(content_type='mod'):
    valid_types = ['mod', 'shader', 'plugin', 'resourcepack', 'modpack', 'datapack', 'map']
    if content_type not in valid_types:
        content_type = 'mod'
    categories = ['Магия', 'Техника', 'Оружие', 'Мобы', 'Декор', 'Еда', 'Миры', 'Утилиты', 'Другое']'''

app_code = app_code.replace(old_upload, new_upload)

# Передаём в шаблон upload
old_upload_render = '''return render_template('upload.html', categories=categories, versions=versions)'''
new_upload_render = '''content_types = [
        ('mod', 'Мод', '⛏', '.jar'),
        ('shader', 'Шейдер', '🌅', '.zip'),
        ('plugin', 'Плагин', '🔌', '.jar'),
        ('resourcepack', 'Ресурспак', '🎨', '.zip'),
        ('modpack', 'Сборка', '📦', '.zip / .mrpack'),
        ('datapack', 'Датапак', '📝', '.zip'),
        ('map', 'Карта', '🗺️', '.zip'),
    ]
    return render_template('upload.html', categories=categories, versions=versions,
                          content_type=content_type, content_types=content_types)'''

app_code = app_code.replace(old_upload_render, new_upload_render)

# Меняем allowed_file — теперь принимает разные форматы
old_allowed = '''def allowed_file(filename):
    return filename.lower().endswith('.jar')'''

new_allowed = '''def allowed_file(filename, content_type='mod'):
    fn = filename.lower()
    if content_type in ('mod', 'plugin'):
        return fn.endswith('.jar')
    elif content_type in ('shader', 'resourcepack', 'datapack', 'map'):
        return fn.endswith('.zip')
    elif content_type == 'modpack':
        return fn.endswith('.zip') or fn.endswith('.mrpack')
    return fn.endswith('.jar') or fn.endswith('.zip') or fn.endswith('.mrpack')'''

app_code = app_code.replace(old_allowed, new_allowed)

# Обновляем сам upload POST — записываем content_type
old_save = '''        if not file or not allowed_file(file.filename):
            flash('Загрузите .jar файл!', 'error')
            return redirect(url_for('upload'))'''

new_save = '''        if not file or not allowed_file(file.filename, content_type):
            flash(f'Неверный формат файла для типа: {content_type}', 'error')
            return redirect(url_for('upload', content_type=content_type))'''

app_code = app_code.replace(old_save, new_save)

# Добавляем content_type в создание Mod
old_mod_create = '''        mod = Mod(
            title=request.form['title'], description=request.form['description'],
            version=request.form['version'], mc_version=request.form['mc_version'],
            category=request.form['category'], tags=request.form.get('tags', ''),
            screenshots=','.join(screenshots), filename=unique_name, user_id=current_user.id
        )'''

new_mod_create = '''        mod = Mod(
            title=request.form['title'], description=request.form['description'],
            version=request.form['version'], mc_version=request.form['mc_version'],
            category=request.form['category'], tags=request.form.get('tags', ''),
            screenshots=','.join(screenshots), filename=unique_name, user_id=current_user.id,
            content_type=content_type
        )'''

app_code = app_code.replace(old_mod_create, new_mod_create)

# Добавляем миграцию для content_type
old_migrations = '''                "ALTER TABLE mod ADD COLUMN screenshots TEXT DEFAULT ''",'''
new_migrations = '''                "ALTER TABLE mod ADD COLUMN screenshots TEXT DEFAULT ''",
                "ALTER TABLE mod ADD COLUMN content_type VARCHAR(30) DEFAULT 'mod'",'''

app_code = app_code.replace(old_migrations, new_migrations)

# Добавляем фильтр по content_type в каталог
old_index_query = '''    query = Mod.query
    if search:
        query = query.filter(or_(Mod.title.ilike(f'%{search}%'), Mod.description.ilike(f'%{search}%'), Mod.tags.ilike(f'%{search}%')))'''

new_index_query = '''    content_type = request.args.get('type', '')
    query = Mod.query
    if content_type:
        query = query.filter_by(content_type=content_type)
    if search:
        query = query.filter(or_(Mod.title.ilike(f'%{search}%'), Mod.description.ilike(f'%{search}%'), Mod.tags.ilike(f'%{search}%')))'''

app_code = app_code.replace(old_index_query, new_index_query)

# Передаём content_type в index
old_index_render = '''return render_template('index.html', mods=mods, top_mods=top_mods, latest_news=latest_news,
                           categories=categories, versions=versions, search=search,
                           sel_category=category, sel_version=mc_version, sort=sort)'''

new_index_render = '''content_types_list = [
        ('', 'Всё', '🎯'),
        ('mod', 'Моды', '⛏'),
        ('shader', 'Шейдеры', '🌅'),
        ('plugin', 'Плагины', '🔌'),
        ('resourcepack', 'Ресурспаки', '🎨'),
        ('modpack', 'Сборки', '📦'),
        ('datapack', 'Датапаки', '📝'),
        ('map', 'Карты', '🗺️'),
    ]
    return render_template('index.html', mods=mods, top_mods=top_mods, latest_news=latest_news,
                           categories=categories, versions=versions, search=search,
                           sel_category=category, sel_version=mc_version, sort=sort,
                           content_type=content_type, content_types_list=content_types_list)'''

app_code = app_code.replace(old_index_render, new_index_render)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)
print("  ✅ app.py")

# ============= ОБНОВЛЯЕМ base.html — меняем меню =============
with open("templates/base.html", "r", encoding="utf-8") as f:
    base_html = f.read()

# Заменяем Modrinth + GitHub на красивый раздел с категориями
old_section = '''<a href="{{ url_for('modrinth_search') }}" class="nav-item modrinth-item">
                <span class="nav-icon">🌍</span><span>Modrinth</span>
            </a>
            <a href="{{ url_for('github_search') }}" class="nav-item github-item">
                <span class="nav-icon">🦊</span><span>GitHub</span>
            </a>'''

new_section = '''<div class="nav-section-title">КАТАЛОГ</div>
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

base_html = base_html.replace(old_section, new_section)

with open("templates/base.html", "w", encoding="utf-8") as f:
    f.write(base_html)
print("  ✅ templates/base.html")

# ============= ОБНОВЛЯЕМ index.html — добавляем фильтр типа =============
with open("templates/index.html", "r", encoding="utf-8") as f:
    index_html = f.read()

# Добавляем переключатель типов после page-header
old_search = '<div class="search-bar">'
new_search = '''<div class="content-type-tabs">
    {% for tk, tn, ti in content_types_list %}
    <a href="{{ url_for('index', type=tk) }}" class="ct-tab {% if content_type == tk %}active{% endif %}">
        <span class="ct-icon">{{ ti }}</span>
        <span>{{ tn }}</span>
    </a>
    {% endfor %}
</div>

<div class="search-bar">'''

if 'content-type-tabs' not in index_html:
    index_html = index_html.replace(old_search, new_search, 1)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)
print("  ✅ templates/index.html")

# ============= ОБНОВЛЯЕМ upload.html — выбор типа =============
upload_html = '''{% extends 'base.html' %}
{% block content %}
<div class="form-page form-wide">
    <div class="form-icon">📤</div>
    <h2>Загрузить контент</h2>
    <p class="form-subtitle">Поделись модом, шейдером, картой и др.</p>

    <div class="upload-type-tabs">
        {% for tk, tn, ti, ext in content_types %}
        <a href="{{ url_for('upload', content_type=tk) }}" class="ut-tab {% if content_type == tk %}active{% endif %}">
            <span class="ut-icon">{{ ti }}</span>
            <span class="ut-name">{{ tn }}</span>
            <span class="ut-ext">{{ ext }}</span>
        </a>
        {% endfor %}
    </div>

    <form method="POST" enctype="multipart/form-data">
        <label>Название</label>
        <input type="text" name="title" placeholder="Например: Complementary Shaders" required>

        <label>Описание</label>
        <textarea name="description" placeholder="Расскажи что это и зачем нужно..." rows="5" required></textarea>

        <div class="form-row">
            <div>
                <label>Версия</label>
                <input type="text" name="version" placeholder="1.0.0" required>
            </div>
            <div>
                <label>Версия Minecraft</label>
                <select name="mc_version" required>
                    <option value="">Выбери</option>
                    {% for v in versions %}
                        <option value="{{ v }}">{{ v }}</option>
                    {% endfor %}
                </select>
            </div>
        </div>

        <label>Категория</label>
        <select name="category" required>
            <option value="">Выбери категорию</option>
            {% for cat in categories %}
                <option value="{{ cat }}">{{ cat }}</option>
            {% endfor %}
        </select>

        <label>Теги (через запятую)</label>
        <input type="text" name="tags" placeholder="реализм, оптимизация, RTX, ванильный">

        <label class="file-label">
            <div class="file-icon">📁</div>
            <div class="file-text">
                Выбери файл
                {% for tk, tn, ti, ext in content_types %}
                    {% if content_type == tk %}({{ ext }}){% endif %}
                {% endfor %}
            </div>
            <div class="file-hint">Максимум 50 МБ</div>
            <input type="file" name="mod_file" required>
        </label>

        <label>📸 Скриншоты (необязательно, до 5)</label>
        <div class="screenshots-upload">
            {% for i in range(1, 6) %}
            <label class="ss-upload-box">
                <span>📷 {{ i }}</span>
                <input type="file" name="screenshot{{ i }}" accept="image/*">
            </label>
            {% endfor %}
        </div>

        <button type="submit">🚀 Опубликовать</button>
    </form>
</div>
{% endblock %}'''

with open("templates/upload.html", "w", encoding="utf-8") as f:
    f.write(upload_html)
print("  ✅ templates/upload.html")

# ============= ОБНОВЛЯЕМ modrinth_search.html — переключатель типов =============
with open("templates/modrinth_search.html", "r", encoding="utf-8") as f:
    mr_html = f.read()

old_mr_header = '''<div class="modrinth-header">'''
new_mr_header = '''<div class="content-type-tabs mr-type-tabs">
    {% for tk, tn, ti in content_types %}
    <a href="{{ url_for('modrinth_search', project_type=tk) }}" class="ct-tab {% if project_type == tk %}active{% endif %}">
        <span class="ct-icon">{{ ti }}</span>
        <span>{{ tn }}</span>
    </a>
    {% endfor %}
</div>

<div class="modrinth-header">'''

if 'mr-type-tabs' not in mr_html:
    mr_html = mr_html.replace(old_mr_header, new_mr_header, 1)

with open("templates/modrinth_search.html", "w", encoding="utf-8") as f:
    f.write(mr_html)
print("  ✅ templates/modrinth_search.html")

# ============= CSS =============
extra_css = '''

/* ===== ВКЛАДКИ ТИПОВ КОНТЕНТА ===== */
.content-type-tabs {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding: 4px;
    margin-bottom: 20px;
    scrollbar-width: thin;
}

.ct-tab {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 12px 18px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    text-decoration: none;
    color: var(--text-muted);
    font-weight: 600;
    font-size: 13px;
    transition: all 0.2s;
    white-space: nowrap;
    min-width: 90px;
}

.ct-tab:hover {
    color: var(--text-main);
    border-color: var(--accent);
    transform: translateY(-2px);
}

.ct-tab.active {
    background: var(--gradient);
    color: #0f1626;
    border-color: transparent;
    box-shadow: 0 4px 15px rgba(34, 255, 136, 0.3);
}

.ct-icon {
    font-size: 24px;
    transition: transform 0.3s;
}

.ct-tab:hover .ct-icon {
    transform: scale(1.2);
}

.ct-tab.active .ct-icon {
    transform: scale(1.1);
}

/* Разделитель в меню */
.nav-section-title {
    padding: 14px 14px 6px;
    font-size: 10px;
    color: var(--text-muted);
    font-weight: 800;
    letter-spacing: 1.5px;
    opacity: 0.6;
}

/* ===== ВКЛАДКИ В ЗАГРУЗКЕ ===== */
.upload-type-tabs {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
    gap: 8px;
    margin-bottom: 24px;
    padding: 12px;
    background: var(--bg-main);
    border-radius: 14px;
    border: 1px solid var(--border);
}

.ut-tab {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 12px 6px;
    background: var(--bg-card);
    border: 2px solid var(--border);
    border-radius: 10px;
    text-decoration: none;
    color: var(--text-muted);
    transition: all 0.2s;
    text-align: center;
}

.ut-tab:hover {
    border-color: var(--accent);
    transform: translateY(-3px);
}

.ut-tab.active {
    background: var(--gradient);
    color: #0f1626;
    border-color: transparent;
}

.ut-icon {
    font-size: 28px;
}

.ut-name {
    font-weight: 700;
    font-size: 13px;
}

.ut-ext {
    font-size: 10px;
    opacity: 0.7;
    font-family: monospace;
}

@media (max-width: 600px) {
    .content-type-tabs {
        gap: 6px;
    }
    .ct-tab {
        padding: 10px 14px;
        font-size: 12px;
        min-width: 70px;
    }
    .ct-icon {
        font-size: 20px;
    }
}
'''

css_path = "static/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    existing_css = f.read()

if "/* ===== ВКЛАДКИ ТИПОВ КОНТЕНТА ===== */" not in existing_css:
    with open(css_path, "a", encoding="utf-8") as f:
        f.write(extra_css)
    print(f"  ✅ {css_path}")

print("\n🎉 ГОТОВО!")
print("\n✨ Что добавлено:")
print("   🎮 7 типов контента: Моды, Шейдеры, Плагины, Ресурспаки, Сборки, Карты, Датапаки")
print("   📋 Красивые вкладки в каталоге")
print("   📤 Выбор типа при загрузке")
print("   🌍 Modrinth теперь ищет ВСЁ (моды/шейдеры/плагины/...)")
print("   📂 В меню — раздел КАТАЛОГ с типами")
print("   📦 Каждый тип принимает свой формат файла")
print("\n📤 git add . && git commit -m 'v15: add shaders, plugins, resourcepacks, maps, packs' && git push --force origin main")
print("На PA: cd ~/mysite && git fetch origin main && git reset --hard origin/main && Reload")