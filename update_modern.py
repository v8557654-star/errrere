# -*- coding: utf-8 -*-
import os

print("🚀 Обновляю до современной версии...")

# ============= APP.PY =============
app_py = '''# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key_change_in_production_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mods.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    theme = db.Column(db.String(20), default='green')
    animations = db.Column(db.Boolean, default=True)
    bio = db.Column(db.String(300), default='')
    mods = db.relationship('Mod', backref='author', lazy=True)

class Mod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    version = db.Column(db.String(20), nullable=False)
    mc_version = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    downloads = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return filename.lower().endswith('.jar')

@app.context_processor
def inject_theme():
    if current_user.is_authenticated:
        return dict(user_theme=current_user.theme, user_animations=current_user.animations)
    return dict(user_theme='green', user_animations=True)

@app.route('/')
def index():
    search = request.args.get('q', '')
    category = request.args.get('category', '')
    mc_version = request.args.get('mc_version', '')

    query = Mod.query
    if search: query = query.filter(Mod.title.ilike(f'%{search}%'))
    if category: query = query.filter_by(category=category)
    if mc_version: query = query.filter_by(mc_version=mc_version)

    mods = query.order_by(Mod.created_at.desc()).all()
    categories = ['Магия', 'Техника', 'Оружие', 'Мобы', 'Декор', 'Еда', 'Миры', 'Утилиты', 'Другое']
    versions = ['1.21', '1.20.4', '1.20.2', '1.20.1', '1.19.4', '1.19.2', '1.18.2', '1.16.5', '1.12.2']

    return render_template('index.html', mods=mods, categories=categories, versions=versions,
                           search=search, sel_category=category, sel_version=mc_version)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Имя пользователя занято', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email уже используется', 'error')
            return redirect(url_for('register'))
        user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Регистрация успешна! Добро пожаловать!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            flash('С возвращением!', 'success')
            return redirect(url_for('index'))
        flash('Неверные данные', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    categories = ['Магия', 'Техника', 'Оружие', 'Мобы', 'Декор', 'Еда', 'Миры', 'Утилиты', 'Другое']
    versions = ['1.21', '1.20.4', '1.20.2', '1.20.1', '1.19.4', '1.19.2', '1.18.2', '1.16.5', '1.12.2']
    if request.method == 'POST':
        file = request.files.get('mod_file')
        if not file or not allowed_file(file.filename):
            flash('Загрузите .jar файл!', 'error')
            return redirect(url_for('upload'))
        filename = secure_filename(file.filename)
        unique_name = f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
        mod = Mod(
            title=request.form['title'],
            description=request.form['description'],
            version=request.form['version'],
            mc_version=request.form['mc_version'],
            category=request.form['category'],
            filename=unique_name,
            user_id=current_user.id
        )
        db.session.add(mod)
        db.session.commit()
        flash('Мод успешно опубликован!', 'success')
        return redirect(url_for('mod_page', mod_id=mod.id))
    return render_template('upload.html', categories=categories, versions=versions)

@app.route('/mod/<int:mod_id>')
def mod_page(mod_id):
    mod = Mod.query.get_or_404(mod_id)
    return render_template('mod.html', mod=mod)

@app.route('/download/<int:mod_id>')
def download(mod_id):
    mod = Mod.query.get_or_404(mod_id)
    mod.downloads += 1
    db.session.commit()
    return send_from_directory(app.config['UPLOAD_FOLDER'], mod.filename,
                               as_attachment=True, download_name=mod.filename.split('_', 2)[-1])

@app.route('/profile')
@login_required
def profile():
    mods = Mod.query.filter_by(user_id=current_user.id).order_by(Mod.created_at.desc()).all()
    return render_template('profile.html', mods=mods)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'theme':
            theme = request.form.get('theme', 'green')
            current_user.theme = theme
            db.session.commit()
            flash('Тема изменена!', 'success')
        elif action == 'animations':
            current_user.animations = 'animations' in request.form
            db.session.commit()
            flash('Настройки анимаций сохранены!', 'success')
        elif action == 'profile':
            current_user.bio = request.form.get('bio', '')[:300]
            new_email = request.form.get('email', '').strip()
            if new_email and new_email != current_user.email:
                if User.query.filter_by(email=new_email).first():
                    flash('Этот email уже занят', 'error')
                else:
                    current_user.email = new_email
            db.session.commit()
            flash('Профиль обновлён!', 'success')
        elif action == 'password':
            old = request.form.get('old_password')
            new = request.form.get('new_password')
            if not check_password_hash(current_user.password, old):
                flash('Неверный текущий пароль', 'error')
            elif len(new) < 6:
                flash('Пароль должен быть от 6 символов', 'error')
            else:
                current_user.password = generate_password_hash(new)
                db.session.commit()
                flash('Пароль изменён!', 'success')
        return redirect(url_for('settings'))
    return render_template('settings.html')

@app.route('/delete/<int:mod_id>', methods=['POST'])
@login_required
def delete_mod(mod_id):
    mod = Mod.query.get_or_404(mod_id)
    if mod.user_id != current_user.id:
        return redirect(url_for('index'))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], mod.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(mod)
    db.session.commit()
    flash('Мод удалён', 'success')
    return redirect(url_for('profile'))

with app.app_context():
    db.create_all()
    # Миграция: добавляем новые колонки если их нет
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            try: conn.execute(text("ALTER TABLE user ADD COLUMN theme VARCHAR(20) DEFAULT 'green'"))
            except: pass
            try: conn.execute(text("ALTER TABLE user ADD COLUMN animations BOOLEAN DEFAULT 1"))
            except: pass
            try: conn.execute(text("ALTER TABLE user ADD COLUMN bio VARCHAR(300) DEFAULT ''"))
            except: pass
            conn.commit()
    except Exception as e:
        print(f"Migration note: {e}")

if __name__ == '__main__':
    app.run(debug=True)
'''

# ============= BASE.HTML =============
base_html = '''<!DOCTYPE html>
<html lang="ru" data-theme="{{ user_theme }}" data-animations="{{ 'on' if user_animations else 'off' }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MineMods — Моды для Minecraft</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>

<div class="layout">
    <aside class="sidebar">
        <div class="sidebar-header">
            <a href="{{ url_for('index') }}" class="logo">
                <span class="logo-icon">⛏</span>
                <span class="logo-text">MineMods</span>
            </a>
        </div>

        <nav class="sidebar-nav">
            <a href="{{ url_for('index') }}" class="nav-item">
                <span class="nav-icon">🏠</span>
                <span>Каталог</span>
            </a>
            {% if current_user.is_authenticated %}
            <a href="{{ url_for('upload') }}" class="nav-item">
                <span class="nav-icon">📤</span>
                <span>Загрузить</span>
            </a>
            <a href="{{ url_for('profile') }}" class="nav-item">
                <span class="nav-icon">👤</span>
                <span>Профиль</span>
            </a>
            <a href="{{ url_for('settings') }}" class="nav-item">
                <span class="nav-icon">⚙️</span>
                <span>Настройки</span>
            </a>
            {% endif %}
        </nav>

        <div class="sidebar-footer">
            {% if current_user.is_authenticated %}
                <div class="user-card">
                    <div class="user-avatar">{{ current_user.username[0]|upper }}</div>
                    <div class="user-info">
                        <div class="user-name">{{ current_user.username }}</div>
                        <a href="{{ url_for('logout') }}" class="user-logout">Выйти</a>
                    </div>
                </div>
            {% else %}
                <a href="{{ url_for('login') }}" class="btn-sidebar">Войти</a>
                <a href="{{ url_for('register') }}" class="btn-sidebar btn-primary">Регистрация</a>
            {% endif %}
        </div>
    </aside>

    <main class="main-content">
        <button class="mobile-menu-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">☰</button>

        <div class="container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endwith %}

            {% block content %}{% endblock %}
        </div>
    </main>
</div>

<script>
    // Закрытие меню при клике вне него (на мобильных)
    document.addEventListener('click', function(e) {
        const sidebar = document.querySelector('.sidebar');
        const toggle = document.querySelector('.mobile-menu-toggle');
        if (window.innerWidth <= 900 && sidebar.classList.contains('open') 
            && !sidebar.contains(e.target) && e.target !== toggle) {
            sidebar.classList.remove('open');
        }
    });
</script>
</body>
</html>'''

# ============= INDEX.HTML =============
index_html = '''{% extends 'base.html' %}
{% block content %}
<div class="page-header">
    <div>
        <h1 class="page-title">Каталог модов</h1>
        <p class="page-subtitle">Найди лучшие моды для Minecraft</p>
    </div>
    <div class="stats-mini">
        <div class="stat-mini">
            <div class="stat-num">{{ mods|length }}</div>
            <div class="stat-label">Модов</div>
        </div>
    </div>
</div>

<div class="search-bar">
    <form method="GET" action="{{ url_for('index') }}">
        <div class="search-input-wrap">
            <span class="search-icon">🔍</span>
            <input type="text" name="q" placeholder="Поиск модов..." value="{{ search }}">
        </div>
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
        <div class="mod-card-header">
            <div class="mod-category">{{ mod.category }}</div>
            <div class="mod-mc-badge">MC {{ mod.mc_version }}</div>
        </div>
        <h3><a href="{{ url_for('mod_page', mod_id=mod.id) }}">{{ mod.title }}</a></h3>
        <p class="mod-meta">
            <span>v{{ mod.version }}</span>
            <span>•</span>
            <span>👤 {{ mod.author.username }}</span>
        </p>
        <p class="mod-desc">{{ mod.description[:120] }}{% if mod.description|length > 120 %}...{% endif %}</p>
        <div class="mod-footer">
            <span class="downloads-count">⬇ {{ mod.downloads }}</span>
            <a href="{{ url_for('download', mod_id=mod.id) }}" class="btn-download">Скачать</a>
        </div>
    </div>
    {% else %}
        <div class="empty-state">
            <div class="empty-icon">📦</div>
            <h3>Пока нет модов</h3>
            <p>Будь первым, кто загрузит мод!</p>
        </div>
    {% endfor %}
</div>
{% endblock %}'''

# ============= SETTINGS.HTML =============
settings_html = '''{% extends 'base.html' %}
{% block content %}
<div class="page-header">
    <div>
        <h1 class="page-title">⚙️ Настройки</h1>
        <p class="page-subtitle">Настрой сайт под себя</p>
    </div>
</div>

<div class="settings-grid">

    <div class="settings-card">
        <h3>🎨 Тема оформления</h3>
        <p class="settings-desc">Выбери цветовую схему сайта</p>
        <form method="POST">
            <input type="hidden" name="action" value="theme">
            <div class="theme-grid">
                <label class="theme-option theme-green {% if current_user.theme == 'green' %}active{% endif %}">
                    <input type="radio" name="theme" value="green" {% if current_user.theme == 'green' %}checked{% endif %}>
                    <div class="theme-preview">
                        <div class="tp-bar"></div>
                        <div class="tp-content"></div>
                    </div>
                    <div class="theme-name">Зелёный</div>
                </label>
                <label class="theme-option theme-blue {% if current_user.theme == 'blue' %}active{% endif %}">
                    <input type="radio" name="theme" value="blue" {% if current_user.theme == 'blue' %}checked{% endif %}>
                    <div class="theme-preview">
                        <div class="tp-bar"></div>
                        <div class="tp-content"></div>
                    </div>
                    <div class="theme-name">Синий</div>
                </label>
                <label class="theme-option theme-purple {% if current_user.theme == 'purple' %}active{% endif %}">
                    <input type="radio" name="theme" value="purple" {% if current_user.theme == 'purple' %}checked{% endif %}>
                    <div class="theme-preview">
                        <div class="tp-bar"></div>
                        <div class="tp-content"></div>
                    </div>
                    <div class="theme-name">Фиолетовый</div>
                </label>
                <label class="theme-option theme-orange {% if current_user.theme == 'orange' %}active{% endif %}">
                    <input type="radio" name="theme" value="orange" {% if current_user.theme == 'orange' %}checked{% endif %}>
                    <div class="theme-preview">
                        <div class="tp-bar"></div>
                        <div class="tp-content"></div>
                    </div>
                    <div class="theme-name">Оранжевый</div>
                </label>
                <label class="theme-option theme-pink {% if current_user.theme == 'pink' %}active{% endif %}">
                    <input type="radio" name="theme" value="pink" {% if current_user.theme == 'pink' %}checked{% endif %}>
                    <div class="theme-preview">
                        <div class="tp-bar"></div>
                        <div class="tp-content"></div>
                    </div>
                    <div class="theme-name">Розовый</div>
                </label>
                <label class="theme-option theme-light {% if current_user.theme == 'light' %}active{% endif %}">
                    <input type="radio" name="theme" value="light" {% if current_user.theme == 'light' %}checked{% endif %}>
                    <div class="theme-preview">
                        <div class="tp-bar"></div>
                        <div class="tp-content"></div>
                    </div>
                    <div class="theme-name">Светлая</div>
                </label>
            </div>
            <button type="submit" class="btn-save">Сохранить тему</button>
        </form>
    </div>

    <div class="settings-card">
        <h3>✨ Анимации</h3>
        <p class="settings-desc">Включи или выключи анимации интерфейса</p>
        <form method="POST">
            <input type="hidden" name="action" value="animations">
            <label class="switch-row">
                <span>Анимации интерфейса</span>
                <label class="switch">
                    <input type="checkbox" name="animations" {% if current_user.animations %}checked{% endif %}>
                    <span class="slider"></span>
                </label>
            </label>
            <button type="submit" class="btn-save">Сохранить</button>
        </form>
    </div>

    <div class="settings-card">
        <h3>👤 Профиль</h3>
        <p class="settings-desc">Информация о тебе</p>
        <form method="POST">
            <input type="hidden" name="action" value="profile">
            <label>Email</label>
            <input type="email" name="email" value="{{ current_user.email }}">
            <label>О себе</label>
            <textarea name="bio" rows="3" maxlength="300" placeholder="Расскажи о себе...">{{ current_user.bio }}</textarea>
            <button type="submit" class="btn-save">Сохранить профиль</button>
        </form>
    </div>

    <div class="settings-card">
        <h3>🔒 Пароль</h3>
        <p class="settings-desc">Смени пароль для безопасности</p>
        <form method="POST">
            <input type="hidden" name="action" value="password">
            <label>Текущий пароль</label>
            <input type="password" name="old_password" required>
            <label>Новый пароль</label>
            <input type="password" name="new_password" required minlength="6">
            <button type="submit" class="btn-save">Изменить пароль</button>
        </form>
    </div>

</div>
{% endblock %}'''

# ============= REGISTER, LOGIN, UPLOAD, MOD, PROFILE =============
register_html = '''{% extends 'base.html' %}
{% block content %}
<div class="form-page">
    <div class="form-icon">📝</div>
    <h2>Регистрация</h2>
    <p class="form-subtitle">Создай аккаунт и публикуй свои моды</p>
    <form method="POST">
        <label>Имя пользователя</label>
        <input type="text" name="username" placeholder="Например: minecraft_master" required minlength="3" maxlength="30">
        <label>Email</label>
        <input type="email" name="email" placeholder="email@example.com" required>
        <label>Пароль</label>
        <input type="password" name="password" placeholder="Минимум 6 символов" required minlength="6">
        <button type="submit">Создать аккаунт</button>
    </form>
    <p class="form-link">Уже есть аккаунт? <a href="{{ url_for('login') }}">Войти</a></p>
</div>
{% endblock %}'''

login_html = '''{% extends 'base.html' %}
{% block content %}
<div class="form-page">
    <div class="form-icon">🔑</div>
    <h2>Вход</h2>
    <p class="form-subtitle">Добро пожаловать обратно!</p>
    <form method="POST">
        <label>Имя пользователя</label>
        <input type="text" name="username" required>
        <label>Пароль</label>
        <input type="password" name="password" required>
        <button type="submit">Войти</button>
    </form>
    <p class="form-link">Нет аккаунта? <a href="{{ url_for('register') }}">Регистрация</a></p>
</div>
{% endblock %}'''

upload_html = '''{% extends 'base.html' %}
{% block content %}
<div class="form-page form-wide">
    <div class="form-icon">📤</div>
    <h2>Загрузить мод</h2>
    <p class="form-subtitle">Поделись своим модом с сообществом</p>
    <form method="POST" enctype="multipart/form-data">
        <label>Название мода</label>
        <input type="text" name="title" placeholder="Например: Magic Wands" required>
        <label>Описание</label>
        <textarea name="description" placeholder="Расскажи что делает мод..." rows="5" required></textarea>
        <div class="form-row">
            <div>
                <label>Версия мода</label>
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
        <label class="file-label">
            <div class="file-icon">📁</div>
            <div class="file-text">Выбери .jar файл</div>
            <div class="file-hint">Максимум 50 МБ</div>
            <input type="file" name="mod_file" accept=".jar" required>
        </label>
        <button type="submit">🚀 Опубликовать мод</button>
    </form>
</div>
{% endblock %}'''

mod_html = '''{% extends 'base.html' %}
{% block content %}
<div class="mod-detail">
    <div class="mod-detail-header">
        <span class="mod-category">{{ mod.category }}</span>
        <h1>{{ mod.title }}</h1>
        <div class="mod-meta-row">
            <span>👤 {{ mod.author.username }}</span>
            <span>📅 {{ mod.created_at.strftime('%d.%m.%Y') }}</span>
            <span>⬇ {{ mod.downloads }}</span>
        </div>
    </div>

    <div class="mod-detail-grid">
        <div class="mod-detail-info">
            <table class="info-table">
                <tr><td>Версия мода</td><td><strong>{{ mod.version }}</strong></td></tr>
                <tr><td>Minecraft</td><td><strong>{{ mod.mc_version }}</strong></td></tr>
                <tr><td>Категория</td><td><strong>{{ mod.category }}</strong></td></tr>
                <tr><td>Скачиваний</td><td><strong>{{ mod.downloads }}</strong></td></tr>
            </table>

            <div class="mod-description">
                <h3>📖 Описание</h3>
                <p>{{ mod.description }}</p>
            </div>
        </div>

        <div class="mod-detail-sidebar">
            <a href="{{ url_for('download', mod_id=mod.id) }}" class="btn-download-big">
                ⬇ Скачать .jar
            </a>
            <div class="mod-quick-info">
                <div class="qi-row">
                    <span>Автор</span>
                    <strong>{{ mod.author.username }}</strong>
                </div>
                <div class="qi-row">
                    <span>Опубликовано</span>
                    <strong>{{ mod.created_at.strftime('%d.%m.%Y') }}</strong>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

profile_html = '''{% extends 'base.html' %}
{% block content %}
<div class="profile-header">
    <div class="profile-avatar-big">{{ current_user.username[0]|upper }}</div>
    <div>
        <h1>{{ current_user.username }}</h1>
        <p class="profile-email">{{ current_user.email }}</p>
        {% if current_user.bio %}
            <p class="profile-bio">{{ current_user.bio }}</p>
        {% endif %}
        <p class="profile-date">📅 С нами с {{ current_user.created_at.strftime('%d.%m.%Y') }}</p>
    </div>
</div>

<div class="profile-stats">
    <div class="stat-card">
        <div class="stat-num">{{ mods|length }}</div>
        <div class="stat-label">Модов</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">{{ mods|sum(attribute='downloads') }}</div>
        <div class="stat-label">Скачиваний</div>
    </div>
</div>

<h3 class="section-title">📦 Мои моды</h3>

<div class="my-mods-grid">
    {% for mod in mods %}
    <div class="my-mod-card">
        <div class="mod-category">{{ mod.category }}</div>
        <a href="{{ url_for('mod_page', mod_id=mod.id) }}" class="my-mod-title">{{ mod.title }}</a>
        <div class="my-mod-meta">
            <span>MC {{ mod.mc_version }}</span>
            <span>⬇ {{ mod.downloads }}</span>
        </div>
        <form method="POST" action="{{ url_for('delete_mod', mod_id=mod.id) }}">
            <button type="submit" class="btn-delete" onclick="return confirm('Удалить мод?')">🗑 Удалить</button>
        </form>
    </div>
    {% else %}
        <div class="empty-state">
            <div class="empty-icon">📦</div>
            <h3>У тебя пока нет модов</h3>
            <a href="{{ url_for('upload') }}" class="btn-download-big">Загрузить первый мод</a>
        </div>
    {% endfor %}
</div>
{% endblock %}'''

# ============= STYLE.CSS =============
style_css = ''':root {
    --bg-main: #0f1626;
    --bg-card: rgba(26, 35, 56, 0.7);
    --bg-sidebar: rgba(20, 27, 45, 0.95);
    --text-main: #e0e6ed;
    --text-muted: #889;
    --border: #233554;
    --accent: #22ff88;
    --accent-2: #00d4ff;
    --gradient: linear-gradient(135deg, #22ff88, #00d4ff);
}

[data-theme="blue"] {
    --accent: #3b82f6;
    --accent-2: #06b6d4;
    --gradient: linear-gradient(135deg, #3b82f6, #06b6d4);
}

[data-theme="purple"] {
    --accent: #a855f7;
    --accent-2: #ec4899;
    --gradient: linear-gradient(135deg, #a855f7, #ec4899);
}

[data-theme="orange"] {
    --accent: #f97316;
    --accent-2: #fbbf24;
    --gradient: linear-gradient(135deg, #f97316, #fbbf24);
}

[data-theme="pink"] {
    --accent: #ec4899;
    --accent-2: #f43f5e;
    --gradient: linear-gradient(135deg, #ec4899, #f43f5e);
}

[data-theme="light"] {
    --bg-main: #f3f4f6;
    --bg-card: rgba(255, 255, 255, 0.9);
    --bg-sidebar: rgba(255, 255, 255, 0.95);
    --text-main: #1f2937;
    --text-muted: #6b7280;
    --border: #e5e7eb;
    --accent: #10b981;
    --accent-2: #3b82f6;
    --gradient: linear-gradient(135deg, #10b981, #3b82f6);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideIn { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
@keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
@keyframes gradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

[data-animations="off"] * {
    animation: none !important;
    transition: none !important;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg-main);
    color: var(--text-main);
    min-height: 100vh;
    overflow-x: hidden;
}

[data-theme="light"] body {
    background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
}

[data-theme]:not([data-theme="light"]) body {
    background: linear-gradient(-45deg, #0f1626, #1a2338, #0f1626, #16213e);
    background-size: 400% 400%;
    animation: gradient 20s ease infinite;
}

.layout {
    display: flex;
    min-height: 100vh;
}

/* ===== SIDEBAR ===== */
.sidebar {
    width: 260px;
    background: var(--bg-sidebar);
    backdrop-filter: blur(20px);
    border-right: 1px solid var(--border);
    padding: 24px 16px;
    display: flex;
    flex-direction: column;
    position: fixed;
    height: 100vh;
    z-index: 100;
    transition: transform 0.3s;
}

.sidebar-header {
    padding: 0 8px 24px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 20px;
}

.logo {
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
    font-size: 22px;
    font-weight: 800;
}

.logo-icon {
    font-size: 28px;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.logo-text {
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sidebar-nav {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    border-radius: 10px;
    text-decoration: none;
    color: var(--text-muted);
    font-weight: 500;
    transition: all 0.2s;
}

.nav-item:hover {
    background: rgba(255,255,255,0.05);
    color: var(--text-main);
    transform: translateX(4px);
}

.nav-icon { font-size: 20px; }

.sidebar-footer {
    border-top: 1px solid var(--border);
    padding-top: 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.user-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px;
    border-radius: 10px;
    background: rgba(255,255,255,0.03);
}

.user-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--gradient);
    color: #0f1626;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 18px;
}

.user-info { flex: 1; }
.user-name { font-weight: 600; font-size: 14px; }
.user-logout { color: var(--text-muted); font-size: 12px; text-decoration: none; }
.user-logout:hover { color: var(--accent); }

.btn-sidebar {
    padding: 10px 14px;
    border-radius: 10px;
    text-align: center;
    text-decoration: none;
    color: var(--text-main);
    background: rgba(255,255,255,0.05);
    font-weight: 600;
    transition: all 0.2s;
}

.btn-sidebar:hover { background: rgba(255,255,255,0.1); }

.btn-sidebar.btn-primary {
    background: var(--gradient);
    color: #0f1626;
}

.btn-sidebar.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(34, 255, 136, 0.3);
}

/* ===== MAIN ===== */
.main-content {
    flex: 1;
    margin-left: 260px;
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 32px;
    animation: fadeIn 0.5s ease-out;
}

.mobile-menu-toggle {
    display: none;
    position: fixed;
    top: 16px;
    left: 16px;
    z-index: 200;
    background: var(--bg-card);
    border: 1px solid var(--border);
    color: var(--text-main);
    width: 44px;
    height: 44px;
    border-radius: 10px;
    font-size: 20px;
    cursor: pointer;
}

/* ===== PAGE HEADER ===== */
.page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 32px;
    flex-wrap: wrap;
    gap: 20px;
}

.page-title {
    font-size: 36px;
    font-weight: 800;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.page-subtitle { color: var(--text-muted); font-size: 16px; }

.stats-mini { display: flex; gap: 12px; }
.stat-mini {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 12px 20px;
    border-radius: 12px;
    text-align: center;
}
.stat-num { font-size: 24px; font-weight: 800; color: var(--accent); }
.stat-label { font-size: 12px; color: var(--text-muted); }

/* ===== SEARCH ===== */
.search-bar { margin-bottom: 32px; }
.search-bar form {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.search-input-wrap {
    flex: 1;
    min-width: 200px;
    position: relative;
}

.search-icon {
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 18px;
}

.search-input-wrap input {
    width: 100%;
    padding: 14px 16px 14px 46px;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: var(--bg-card);
    color: var(--text-main);
    font-size: 15px;
    transition: all 0.2s;
}

.search-input-wrap input:focus {
    border-color: var(--accent);
    outline: none;
    box-shadow: 0 0 0 3px rgba(34, 255, 136, 0.1);
}

.search-bar select {
    padding: 14px;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: var(--bg-card);
    color: var(--text-main);
    cursor: pointer;
    min-width: 150px;
}

.search-bar button {
    padding: 14px 28px;
    background: var(--gradient);
    color: #0f1626;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
}

.search-bar button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(34, 255, 136, 0.3);
}

/* ===== MODS GRID ===== */
.mods-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
}

.mod-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    transition: all 0.3s;
    animation: fadeIn 0.4s ease-out backwards;
    backdrop-filter: blur(10px);
}

.mod-card:nth-child(1) { animation-delay: 0.05s; }
.mod-card:nth-child(2) { animation-delay: 0.1s; }
.mod-card:nth-child(3) { animation-delay: 0.15s; }
.mod-card:nth-child(4) { animation-delay: 0.2s; }
.mod-card:nth-child(5) { animation-delay: 0.25s; }
.mod-card:nth-child(6) { animation-delay: 0.3s; }

.mod-card:hover {
    transform: translateY(-4px);
    border-color: var(--accent);
    box-shadow: 0 12px 30px rgba(0,0,0,0.3);
}

.mod-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.mod-category {
    display: inline-block;
    background: var(--gradient);
    color: #0f1626;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
}

.mod-mc-badge {
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    color: var(--text-muted);
    font-weight: 600;
}

.mod-card h3 a {
    color: var(--text-main);
    text-decoration: none;
    font-size: 18px;
    font-weight: 700;
}

.mod-card h3 a:hover { color: var(--accent); }

.mod-meta {
    display: flex;
    gap: 8px;
    color: var(--text-muted);
    font-size: 13px;
    margin: 8px 0;
}

.mod-desc {
    color: var(--text-muted);
    font-size: 14px;
    line-height: 1.5;
    margin: 12px 0;
}

.mod-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 16px;
    border-top: 1px solid var(--border);
}

.downloads-count {
    color: var(--text-muted);
    font-size: 14px;
    font-weight: 600;
}

.btn-download {
    background: var(--gradient);
    color: #0f1626;
    padding: 8px 18px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 700;
    font-size: 13px;
    transition: all 0.2s;
}

.btn-download:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 6px 15px rgba(34, 255, 136, 0.4);
}

/* ===== EMPTY STATE ===== */
.empty-state {
    grid-column: 1 / -1;
    text-align: center;
    padding: 60px 20px;
    background: var(--bg-card);
    border-radius: 16px;
    border: 2px dashed var(--border);
}

.empty-icon { font-size: 64px; margin-bottom: 16px; }
.empty-state h3 { margin-bottom: 8px; }
.empty-state p { color: var(--text-muted); margin-bottom: 16px; }

/* ===== FORMS ===== */
.form-page {
    max-width: 480px;
    margin: 40px auto;
    background: var(--bg-card);
    backdrop-filter: blur(10px);
    padding: 40px;
    border-radius: 20px;
    border: 1px solid var(--border);
}

.form-wide { max-width: 640px; }

.form-icon {
    font-size: 48px;
    text-align: center;
    margin-bottom: 12px;
}

.form-page h2 {
    text-align: center;
    margin-bottom: 8px;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.form-subtitle {
    text-align: center;
    color: var(--text-muted);
    margin-bottom: 24px;
}

.form-page label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-muted);
    margin-bottom: 6px;
    margin-top: 12px;
}

.form-page input,
.form-page select,
.form-page textarea {
    width: 100%;
    padding: 12px 14px;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--bg-main);
    color: var(--text-main);
    font-size: 15px;
    font-family: inherit;
    transition: all 0.2s;
}

.form-page input:focus,
.form-page select:focus,
.form-page textarea:focus {
    border-color: var(--accent);
    outline: none;
    box-shadow: 0 0 0 3px rgba(34, 255, 136, 0.1);
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.form-page button {
    width: 100%;
    padding: 14px;
    background: var(--gradient);
    color: #0f1626;
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    margin-top: 20px;
    transition: all 0.2s;
}

.form-page button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(34, 255, 136, 0.3);
}

.form-link {
    text-align: center;
    margin-top: 20px;
    color: var(--text-muted);
}

.form-link a {
    color: var(--accent);
    text-decoration: none;
    font-weight: 600;
}

.file-label {
    display: block;
    background: var(--bg-main);
    padding: 30px;
    border-radius: 12px;
    text-align: center;
    cursor: pointer;
    border: 2px dashed var(--accent);
    margin: 12px 0;
    transition: all 0.2s;
}

.file-label:hover {
    background: rgba(34, 255, 136, 0.05);
    transform: scale(1.01);
}

.file-icon { font-size: 36px; margin-bottom: 8px; }
.file-text { font-weight: 600; }
.file-hint { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.file-label input { margin-top: 12px; }

/* ===== ALERTS ===== */
.alert {
    padding: 14px 18px;
    border-radius: 10px;
    margin-bottom: 16px;
    animation: slideIn 0.3s ease-out;
}

.alert-success {
    background: rgba(34, 255, 136, 0.1);
    color: #4ade80;
    border-left: 3px solid #4ade80;
}

.alert-error {
    background: rgba(255, 100, 100, 0.1);
    color: #ff7777;
    border-left: 3px solid #ff7777;
}

/* ===== MOD DETAIL ===== */
.mod-detail { max-width: 1000px; margin: 0 auto; }

.mod-detail-header { margin-bottom: 24px; }
.mod-detail-header h1 {
    font-size: 36px;
    margin: 12px 0;
}

.mod-meta-row {
    display: flex;
    gap: 16px;
    color: var(--text-muted);
    font-size: 14px;
    flex-wrap: wrap;
}

.mod-detail-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 24px;
}

.info-table {
    width: 100%;
    background: var(--bg-card);
    border-radius: 12px;
    overflow: hidden;
    border-collapse: collapse;
    margin-bottom: 20px;
}

.info-table td {
    padding: 14px 18px;
    border-bottom: 1px solid var(--border);
}

.info-table td:first-child { color: var(--text-muted); width: 40%; }

.mod-description {
    background: var(--bg-card);
    padding: 24px;
    border-radius: 12px;
    line-height: 1.7;
}

.mod-description h3 {
    color: var(--accent);
    margin-bottom: 12px;
}

.mod-detail-sidebar {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.btn-download-big {
    display: block;
    background: var(--gradient);
    color: #0f1626;
    padding: 18px;
    border-radius: 12px;
    text-decoration: none;
    font-size: 16px;
    font-weight: 700;
    text-align: center;
    transition: all 0.2s;
}

.btn-download-big:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 30px rgba(34, 255, 136, 0.4);
}

.mod-quick-info {
    background: var(--bg-card);
    padding: 16px;
    border-radius: 12px;
}

.qi-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    font-size: 14px;
}

.qi-row span { color: var(--text-muted); }

/* ===== PROFILE ===== */
.profile-header {
    display: flex;
    gap: 24px;
    align-items: center;
    background: var(--bg-card);
    padding: 32px;
    border-radius: 20px;
    margin-bottom: 24px;
}

.profile-avatar-big {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: var(--gradient);
    color: #0f1626;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
    font-weight: 800;
}

.profile-header h1 { font-size: 28px; margin-bottom: 4px; }
.profile-email { color: var(--text-muted); font-size: 14px; }
.profile-bio { margin: 8px 0; }
.profile-date { color: var(--text-muted); font-size: 13px; margin-top: 8px; }

.profile-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
}

.stat-card {
    background: var(--bg-card);
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    border: 1px solid var(--border);
}

.section-title {
    font-size: 22px;
    margin-bottom: 16px;
    color: var(--text-main);
}

.my-mods-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 16px;
}

.my-mod-card {
    background: var(--bg-card);
    padding: 20px;
    border-radius: 14px;
    border: 1px solid var(--border);
}

.my-mod-title {
    display: block;
    color: var(--text-main);
    text-decoration: none;
    font-weight: 700;
    font-size: 16px;
    margin: 10px 0;
}

.my-mod-title:hover { color: var(--accent); }

.my-mod-meta {
    display: flex;
    justify-content: space-between;
    color: var(--text-muted);
    font-size: 13px;
    margin-bottom: 12px;
}

.btn-delete {
    width: 100%;
    background: rgba(255, 100, 100, 0.1);
    color: #ff7777;
    border: 1px solid rgba(255, 100, 100, 0.3);
    padding: 8px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
}

.btn-delete:hover {
    background: rgba(255, 100, 100, 0.2);
}

/* ===== SETTINGS ===== */
.settings-grid {
    display: grid;
    gap: 20px;
}

.settings-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 24px;
    border-radius: 16px;
}

.settings-card h3 {
    margin-bottom: 4px;
    font-size: 18px;
}

.settings-desc {
    color: var(--text-muted);
    font-size: 14px;
    margin-bottom: 16px;
}

.settings-card label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-muted);
    margin-bottom: 6px;
    margin-top: 12px;
}

.settings-card input,
.settings-card textarea {
    width: 100%;
    padding: 12px 14px;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--bg-main);
    color: var(--text-main);
    font-family: inherit;
}

.btn-save {
    background: var(--gradient);
    color: #0f1626;
    border: none;
    padding: 12px 24px;
    border-radius: 10px;
    font-weight: 700;
    cursor: pointer;
    margin-top: 16px;
    transition: all 0.2s;
}

.btn-save:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(34, 255, 136, 0.3);
}

/* ===== THEMES ===== */
.theme-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
    margin-bottom: 20px;
}

.theme-option {
    cursor: pointer;
    padding: 12px;
    border-radius: 12px;
    border: 2px solid var(--border);
    transition: all 0.2s;
    text-align: center;
}

.theme-option input { display: none; }

.theme-option:hover { transform: translateY(-3px); }

.theme-option.active {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(34, 255, 136, 0.1);
}

.theme-preview {
    width: 100%;
    height: 80px;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 8px;
    background: #0f1626;
    display: flex;
    flex-direction: column;
}

.tp-bar { height: 25%; }
.tp-content { flex: 1; background: #1a2338; }

.theme-green .tp-bar { background: linear-gradient(135deg, #22ff88, #00d4ff); }
.theme-blue .tp-bar { background: linear-gradient(135deg, #3b82f6, #06b6d4); }
.theme-purple .tp-bar { background: linear-gradient(135deg, #a855f7, #ec4899); }
.theme-orange .tp-bar { background: linear-gradient(135deg, #f97316, #fbbf24); }
.theme-pink .tp-bar { background: linear-gradient(135deg, #ec4899, #f43f5e); }
.theme-light .tp-bar { background: linear-gradient(135deg, #10b981, #3b82f6); }
.theme-light .tp-content { background: #f3f4f6; }
.theme-light .theme-preview { background: #fff; }

.theme-name { font-size: 13px; font-weight: 600; }

/* ===== SWITCH ===== */
.switch-row {
    display: flex !important;
    justify-content: space-between;
    align-items: center;
    margin: 12px 0 !important;
}

.switch {
    position: relative;
    display: inline-block;
    width: 50px;
    height: 26px;
}

.switch input { display: none; }

.slider {
    position: absolute;
    cursor: pointer;
    top: 0; left: 0; right: 0; bottom: 0;
    background: var(--border);
    transition: 0.3s;
    border-radius: 26px;
}

.slider:before {
    position: absolute;
    content: "";
    height: 20px;
    width: 20px;
    left: 3px;
    bottom: 3px;
    background: white;
    transition: 0.3s;
    border-radius: 50%;
}

.switch input:checked + .slider {
    background: var(--gradient);
}

.switch input:checked + .slider:before {
    transform: translateX(24px);
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-track { background: var(--bg-main); }
::-webkit-scrollbar-thumb {
    background: var(--gradient);
    border-radius: 5px;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 900px) {
    .sidebar {
        transform: translateX(-100%);
        box-shadow: 5px 0 30px rgba(0,0,0,0.5);
    }
    .sidebar.open { transform: translateX(0); }
    .main-content { margin-left: 0; }
    .mobile-menu-toggle { display: block; }
    .container { padding: 70px 16px 24px; }
    .mod-detail-grid { grid-template-columns: 1fr; }
    .form-row { grid-template-columns: 1fr; }
    .profile-header { flex-direction: column; text-align: center; }
}
'''

# ===== ЗАПИСЫВАЕМ ВСЕ ФАЙЛЫ =====
files = {
    "app.py": app_py,
    "templates/base.html": base_html,
    "templates/index.html": index_html,
    "templates/settings.html": settings_html,
    "templates/register.html": register_html,
    "templates/login.html": login_html,
    "templates/upload.html": upload_html,
    "templates/mod.html": mod_html,
    "templates/profile.html": profile_html,
    "static/css/style.css": style_css,
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ {path}")

print("\n🎉 ГОТОВО! Современный интерфейс установлен.")
print("\n📤 Теперь залей на сайт:")
print("   git add .")
print('   git commit -m "Современный UI + темы + настройки"')
print("   git push")
print("\nЗатем на PythonAnywhere в Bash:")
print("   cd ~/mysite")
print("   git pull")
print("\n⚠️  ВАЖНО: после git pull нужно перезапустить сайт!")
print("На вкладке 'Web' нажми зелёную кнопку 'Reload'")