# -*- coding: utf-8 -*-
import os

print("🔧 Создаю шаблоны...")

# ===================== base.html =====================
base_html = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MineMods — Моды для Minecraft</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <a href="{{ url_for('index') }}" class="logo">⛏ MineMods</a>
        <div class="nav-links">
            <a href="{{ url_for('index') }}">Каталог</a>
            {% if current_user.is_authenticated %}
                <a href="{{ url_for('upload') }}">+ Загрузить мод</a>
                <a href="{{ url_for('profile') }}">👤 {{ current_user.username }}</a>
                <a href="{{ url_for('logout') }}">Выйти</a>
            {% else %}
                <a href="{{ url_for('login') }}">Войти</a>
                <a href="{{ url_for('register') }}" class="btn-register">Регистрация</a>
            {% endif %}
        </div>
    </nav>

    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <footer>
        <p>⛏ MineMods © 2025 — Платформа модов Minecraft</p>
    </footer>
</body>
</html>'''

# ===================== index.html =====================
index_html = '''{% extends 'base.html' %}
{% block content %}
<div class="hero">
    <h1>🎮 Моды для Minecraft</h1>
    <p>Находи, скачивай и публикуй моды</p>
</div>

<div class="search-bar">
    <form method="GET" action="{{ url_for('index') }}">
        <input type="text" name="q" placeholder="🔍 Поиск модов..." value="{{ search }}">
        <select name="category">
            <option value="">Все категории</option>
            {% for cat in categories %}
                <option value="{{ cat }}" {% if sel_category == cat %}selected{% endif %}>{{ cat }}</option>
            {% endfor %}
        </select>
        <select name="mc_version">
            <option value="">Все версии</option>
            {% for v in versions %}
                <option value="{{ v }}" {% if sel_version == v %}selected{% endif %}>{{ v }}</option>
            {% endfor %}
        </select>
        <button type="submit">Найти</button>
    </form>
</div>

<div class="mods-grid">
    {% for mod in mods %}
    <div class="mod-card">
        <div class="mod-category">{{ mod.category }}</div>
        <h3><a href="{{ url_for('mod_page', mod_id=mod.id) }}">{{ mod.title }}</a></h3>
        <p class="mod-meta">MC {{ mod.mc_version }} · v{{ mod.version }} · 👤 {{ mod.author.username }}</p>
        <p class="mod-desc">{{ mod.description[:120] }}{% if mod.description|length > 120 %}...{% endif %}</p>
        <div class="mod-footer">
            <span>⬇ {{ mod.downloads }}</span>
            <a href="{{ url_for('download', mod_id=mod.id) }}" class="btn-download">Скачать</a>
        </div>
    </div>
    {% else %}
        <p class="no-mods">Пока нет ни одного мода. Будь первым! 🚀</p>
    {% endfor %}
</div>
{% endblock %}'''

# ===================== register.html =====================
register_html = '''{% extends 'base.html' %}
{% block content %}
<div class="form-page">
    <h2>📝 Регистрация</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Имя пользователя" required minlength="3" maxlength="30">
        <input type="email" name="email" placeholder="Email" required>
        <input type="password" name="password" placeholder="Пароль" required minlength="6">
        <button type="submit">Зарегистрироваться</button>
    </form>
    <p>Уже есть аккаунт? <a href="{{ url_for('login') }}">Войти</a></p>
</div>
{% endblock %}'''

# ===================== login.html =====================
login_html = '''{% extends 'base.html' %}
{% block content %}
<div class="form-page">
    <h2>🔑 Вход</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Имя пользователя" required>
        <input type="password" name="password" placeholder="Пароль" required>
        <button type="submit">Войти</button>
    </form>
    <p>Нет аккаунта? <a href="{{ url_for('register') }}">Регистрация</a></p>
</div>
{% endblock %}'''

# ===================== upload.html =====================
upload_html = '''{% extends 'base.html' %}
{% block content %}
<div class="form-page form-wide">
    <h2>📤 Загрузить мод</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="text" name="title" placeholder="Название мода" required>
        <textarea name="description" placeholder="Описание мода..." rows="5" required></textarea>
        <input type="text" name="version" placeholder="Версия мода (например 1.0)" required>
        <select name="mc_version" required>
            <option value="">Версия Minecraft</option>
            {% for v in versions %}
                <option value="{{ v }}">{{ v }}</option>
            {% endfor %}
        </select>
        <select name="category" required>
            <option value="">Категория</option>
            {% for cat in categories %}
                <option value="{{ cat }}">{{ cat }}</option>
            {% endfor %}
        </select>
        <label class="file-label">
            📁 Выберите .jar файл (макс 50 МБ)
            <input type="file" name="mod_file" accept=".jar" required>
        </label>
        <button type="submit">Опубликовать</button>
    </form>
</div>
{% endblock %}'''

# ===================== mod.html =====================
mod_html = '''{% extends 'base.html' %}
{% block content %}
<div class="mod-detail">
    <div class="mod-header">
        <span class="mod-category">{{ mod.category }}</span>
        <h1>{{ mod.title }}</h1>
        <p class="mod-meta">
            👤 {{ mod.author.username }} ·
            📅 {{ mod.created_at.strftime('%d.%m.%Y') }} ·
            ⬇ {{ mod.downloads }} скачиваний
        </p>
    </div>

    <div class="mod-info">
        <table>
            <tr><td>Версия мода</td><td>{{ mod.version }}</td></tr>
            <tr><td>Minecraft</td><td>{{ mod.mc_version }}</td></tr>
            <tr><td>Категория</td><td>{{ mod.category }}</td></tr>
        </table>
    </div>

    <div class="mod-description">
        <h3>Описание</h3>
        <p>{{ mod.description }}</p>
    </div>

    <a href="{{ url_for('download', mod_id=mod.id) }}" class="btn-download-big">⬇ Скачать .jar</a>
</div>
{% endblock %}'''

# ===================== profile.html =====================
profile_html = '''{% extends 'base.html' %}
{% block content %}
<div class="profile-page">
    <h2>👤 {{ current_user.username }}</h2>
    <p>Email: {{ current_user.email }}</p>
    <p>Зарегистрирован: {{ current_user.created_at.strftime('%d.%m.%Y') }}</p>

    <h3>Мои моды ({{ mods|length }})</h3>

    {% for mod in mods %}
    <div class="my-mod">
        <a href="{{ url_for('mod_page', mod_id=mod.id) }}">{{ mod.title }}</a>
        <span>⬇ {{ mod.downloads }}</span>
        <form method="POST" action="{{ url_for('delete_mod', mod_id=mod.id) }}" style="display:inline">
            <button type="submit" class="btn-delete" onclick="return confirm('Удалить мод?')">🗑</button>
        </form>
    </div>
    {% else %}
        <p>Вы ещё не загрузили ни одного мода</p>
    {% endfor %}
</div>
{% endblock %}'''

# ===================== style.css =====================
style_css = '''* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Segoe UI', Tahoma, sans-serif;
    background: #0f1626;
    color: #e0e6ed;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.navbar {
    background: #1a2338;
    padding: 15px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 15px rgba(0,0,0,0.4);
    position: sticky;
    top: 0;
    z-index: 100;
}

.logo {
    font-size: 24px;
    font-weight: bold;
    color: #22ff88;
    text-decoration: none;
}

.nav-links a {
    color: #aab;
    text-decoration: none;
    margin-left: 20px;
    transition: color 0.3s;
}

.nav-links a:hover { color: #22ff88; }

.btn-register {
    background: #22ff88;
    color: #0f1626 !important;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: bold;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    flex: 1;
    width: 100%;
}

.hero {
    text-align: center;
    padding: 40px 0 20px;
}

.hero h1 {
    font-size: 40px;
    color: #22ff88;
    margin-bottom: 10px;
}

.hero p { color: #889; font-size: 18px; }

.search-bar { margin: 30px 0; }

.search-bar form {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.search-bar input[type="text"] {
    flex: 1;
    min-width: 200px;
    padding: 12px 16px;
    border: 2px solid #233554;
    border-radius: 8px;
    background: #1a2338;
    color: #fff;
    font-size: 16px;
}

.search-bar select {
    padding: 12px;
    border: 2px solid #233554;
    border-radius: 8px;
    background: #1a2338;
    color: #fff;
    font-size: 14px;
    cursor: pointer;
}

.search-bar button {
    padding: 12px 28px;
    background: #22ff88;
    color: #0f1626;
    border: none;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
    font-size: 16px;
}

.search-bar button:hover { background: #1dd672; }

.mods-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
}

.mod-card {
    background: #1a2338;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #233554;
    transition: all 0.3s;
}

.mod-card:hover {
    transform: translateY(-5px);
    border-color: #22ff88;
    box-shadow: 0 10px 30px rgba(34, 255, 136, 0.15);
}

.mod-category {
    display: inline-block;
    background: #22ff88;
    color: #0f1626;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
    margin-bottom: 12px;
}

.mod-card h3 a {
    color: #fff;
    text-decoration: none;
    font-size: 20px;
}

.mod-card h3 a:hover { color: #22ff88; }

.mod-meta {
    color: #778;
    font-size: 13px;
    margin: 8px 0;
}

.mod-desc {
    color: #aab;
    font-size: 14px;
    margin: 12px 0;
    line-height: 1.5;
}

.mod-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #233554;
}

.btn-download {
    background: #22ff88;
    color: #0f1626;
    padding: 8px 18px;
    border-radius: 6px;
    text-decoration: none;
    font-weight: bold;
    font-size: 14px;
}

.btn-download:hover { background: #1dd672; }

.mod-detail { max-width: 800px; margin: 0 auto; }

.mod-header h1 {
    font-size: 36px;
    margin: 12px 0;
    color: #fff;
}

.mod-info table {
    width: 100%;
    margin: 20px 0;
    background: #1a2338;
    border-radius: 8px;
    overflow: hidden;
    border-collapse: collapse;
}

.mod-info td {
    padding: 14px 18px;
    border-bottom: 1px solid #233554;
}

.mod-info td:first-child {
    color: #778;
    width: 40%;
}

.mod-description {
    margin: 30px 0;
    line-height: 1.7;
    background: #1a2338;
    padding: 20px;
    border-radius: 8px;
}

.mod-description h3 {
    color: #22ff88;
    margin-bottom: 12px;
}

.btn-download-big {
    display: inline-block;
    background: #22ff88;
    color: #0f1626;
    padding: 18px 50px;
    border-radius: 10px;
    text-decoration: none;
    font-size: 18px;
    font-weight: bold;
    margin: 20px 0;
}

.btn-download-big:hover { background: #1dd672; }

.form-page {
    max-width: 450px;
    margin: 40px auto;
    background: #1a2338;
    padding: 35px;
    border-radius: 12px;
    border: 1px solid #233554;
}

.form-wide { max-width: 600px; }

.form-page h2 {
    text-align: center;
    margin-bottom: 25px;
    color: #22ff88;
}

.form-page input,
.form-page select,
.form-page textarea {
    width: 100%;
    padding: 12px 14px;
    margin-bottom: 15px;
    border: 2px solid #233554;
    border-radius: 8px;
    background: #0f1626;
    color: #fff;
    font-size: 15px;
    font-family: inherit;
}

.form-page input:focus,
.form-page select:focus,
.form-page textarea:focus {
    border-color: #22ff88;
    outline: none;
}

.form-page button {
    width: 100%;
    padding: 14px;
    background: #22ff88;
    color: #0f1626;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

.form-page button:hover { background: #1dd672; }

.form-page p {
    text-align: center;
    margin-top: 15px;
    color: #778;
}

.form-page p a { color: #22ff88; }

.file-label {
    display: block;
    background: #0f1626;
    padding: 25px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 15px;
    cursor: pointer;
    border: 2px dashed #22ff88;
    color: #aab;
}

.file-label input { margin-top: 10px; }

.alert {
    padding: 14px 18px;
    border-radius: 8px;
    margin-bottom: 15px;
}

.alert-success { background: #1e3a2f; color: #4ade80; }
.alert-error { background: #3a1e2f; color: #ff7777; }

.profile-page h3 {
    margin-top: 30px;
    color: #22ff88;
    margin-bottom: 15px;
}

.my-mod {
    display: flex;
    align-items: center;
    gap: 15px;
    background: #1a2338;
    padding: 14px 18px;
    border-radius: 8px;
    margin: 10px 0;
}

.my-mod a {
    flex: 1;
    color: #fff;
    text-decoration: none;
    font-weight: bold;
}

.my-mod a:hover { color: #22ff88; }

.btn-delete {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
}

.no-mods {
    text-align: center;
    color: #778;
    padding: 60px 20px;
    font-size: 18px;
    grid-column: 1 / -1;
}

footer {
    text-align: center;
    padding: 30px;
    color: #445;
    margin-top: 50px;
}

@media (max-width: 600px) {
    .navbar { flex-direction: column; gap: 12px; }
    .search-bar form { flex-direction: column; }
    .mods-grid { grid-template-columns: 1fr; }
}
'''

# ============= ЗАПИСЫВАЕМ ВСЕ ФАЙЛЫ =============
files_to_write = {
    "templates/base.html": base_html,
    "templates/index.html": index_html,
    "templates/register.html": register_html,
    "templates/login.html": login_html,
    "templates/upload.html": upload_html,
    "templates/mod.html": mod_html,
    "templates/profile.html": profile_html,
    "static/css/style.css": style_css,
}

for path, content in files_to_write.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ {path}")

print("\n🎉 Готово! Все шаблоны созданы.")
print("Теперь запусти сайт командой: python app.py")
print("И открой: http://127.0.0.1:5000")