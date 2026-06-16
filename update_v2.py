# -*- coding: utf-8 -*-
import os

print("🚀 Обновление v2 — Лайки, Просмотры, Топ, Теги...")

# ============= APP.PY =============
app_py = '''# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import func, or_, text

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key_change_in_production_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mods.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ===== МОДЕЛИ =====
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
    likes = db.relationship('Like', backref='user', lazy=True)

class Mod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    version = db.Column(db.String(20), nullable=False)
    mc_version = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    downloads = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    tags = db.Column(db.String(300), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('Like', backref='mod', lazy=True, cascade='all, delete-orphan')

    @property
    def likes_count(self):
        return len(self.likes)

    @property
    def tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()] if self.tags else []

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return Like.query.filter_by(user_id=user.id, mod_id=self.id).first() is not None

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mod_id = db.Column(db.Integer, db.ForeignKey('mod.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

# ===== РОУТЫ =====
@app.route('/')
def index():
    search = request.args.get('q', '')
    category = request.args.get('category', '')
    mc_version = request.args.get('mc_version', '')
    sort = request.args.get('sort', 'new')  # new, popular, top

    query = Mod.query

    if search:
        query = query.filter(or_(
            Mod.title.ilike(f'%{search}%'),
            Mod.description.ilike(f'%{search}%'),
            Mod.tags.ilike(f'%{search}%')
        ))
    if category: query = query.filter_by(category=category)
    if mc_version: query = query.filter_by(mc_version=mc_version)

    if sort == 'popular':
        query = query.order_by(Mod.downloads.desc())
    elif sort == 'top':
        # Сортировка по лайкам
        query = query.outerjoin(Like).group_by(Mod.id).order_by(func.count(Like.id).desc())
    elif sort == 'views':
        query = query.order_by(Mod.views.desc())
    else:
        query = query.order_by(Mod.created_at.desc())

    mods = query.all()

    # Топ-3 мода для главной
    top_mods = Mod.query.order_by(Mod.downloads.desc()).limit(3).all() if not search and not category and not mc_version else []

    categories = ['Магия', 'Техника', 'Оружие', 'Мобы', 'Декор', 'Еда', 'Миры', 'Утилиты', 'Другое']
    versions = ['1.21', '1.20.4', '1.20.2', '1.20.1', '1.19.4', '1.19.2', '1.18.2', '1.16.5', '1.12.2']

    return render_template('index.html', mods=mods, top_mods=top_mods, categories=categories, versions=versions,
                           search=search, sel_category=category, sel_version=mc_version, sort=sort)

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
            tags=request.form.get('tags', ''),
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
    # Увеличиваем счётчик просмотров
    mod.views = (mod.views or 0) + 1
    db.session.commit()
    return render_template('mod.html', mod=mod)

@app.route('/download/<int:mod_id>')
def download(mod_id):
    mod = Mod.query.get_or_404(mod_id)
    mod.downloads += 1
    db.session.commit()
    return send_from_directory(app.config['UPLOAD_FOLDER'], mod.filename,
                               as_attachment=True, download_name=mod.filename.split('_', 2)[-1])

@app.route('/like/<int:mod_id>', methods=['POST'])
@login_required
def like_mod(mod_id):
    mod = Mod.query.get_or_404(mod_id)
    existing = Like.query.filter_by(user_id=current_user.id, mod_id=mod_id).first()
    if existing:
        db.session.delete(existing)
        liked = False
    else:
        like = Like(user_id=current_user.id, mod_id=mod_id)
        db.session.add(like)
        liked = True
    db.session.commit()
    return jsonify({'liked': liked, 'count': len(mod.likes)})

@app.route('/profile')
@login_required
def profile():
    mods = Mod.query.filter_by(user_id=current_user.id).order_by(Mod.created_at.desc()).all()
    total_likes = sum(m.likes_count for m in mods)
    total_views = sum(m.views or 0 for m in mods)
    return render_template('profile.html', mods=mods, total_likes=total_likes, total_views=total_views)

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
    # Миграции
    try:
        with db.engine.connect() as conn:
            for sql in [
                "ALTER TABLE user ADD COLUMN theme VARCHAR(20) DEFAULT 'green'",
                "ALTER TABLE user ADD COLUMN animations BOOLEAN DEFAULT 1",
                "ALTER TABLE user ADD COLUMN bio VARCHAR(300) DEFAULT ''",
                "ALTER TABLE mod ADD COLUMN views INTEGER DEFAULT 0",
                "ALTER TABLE mod ADD COLUMN tags VARCHAR(300) DEFAULT ''",
            ]:
                try: conn.execute(text(sql))
                except: pass
            conn.commit()
    except Exception as e:
        print(f"Migration: {e}")

if __name__ == '__main__':
    app.run(debug=True)
'''

# ============= INDEX.HTML =============
index_html = '''{% extends 'base.html' %}
{% block content %}

{% if top_mods %}
<div class="top-section">
    <h2 class="section-title">🏆 Топ модов</h2>
    <div class="top-grid">
        {% for mod in top_mods %}
        <a href="{{ url_for('mod_page', mod_id=mod.id) }}" class="top-card top-{{ loop.index }}">
            <div class="top-rank">#{{ loop.index }}</div>
            <div class="top-info">
                <div class="mod-category">{{ mod.category }}</div>
                <h3>{{ mod.title }}</h3>
                <div class="top-stats">
                    <span>⬇ {{ mod.downloads }}</span>
                    <span>❤ {{ mod.likes_count }}</span>
                    <span>👁 {{ mod.views or 0 }}</span>
                </div>
            </div>
        </a>
        {% endfor %}
    </div>
</div>
{% endif %}

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
            <input type="text" name="q" placeholder="Поиск по названию, описанию, тегам..." value="{{ search }}">
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
        <input type="hidden" name="sort" value="{{ sort }}">
        <button type="submit">Найти</button>
    </form>
</div>

<div class="sort-tabs">
    <a href="{{ url_for('index', q=search, category=sel_category, mc_version=sel_version, sort='new') }}"
       class="sort-tab {% if sort == 'new' %}active{% endif %}">🆕 Новые</a>
    <a href="{{ url_for('index', q=search, category=sel_category, mc_version=sel_version, sort='popular') }}"
       class="sort-tab {% if sort == 'popular' %}active{% endif %}">🔥 Популярные</a>
    <a href="{{ url_for('index', q=search, category=sel_category, mc_version=sel_version, sort='top') }}"
       class="sort-tab {% if sort == 'top' %}active{% endif %}">⭐ Лучшие</a>
    <a href="{{ url_for('index', q=search, category=sel_category, mc_version=sel_version, sort='views') }}"
       class="sort-tab {% if sort == 'views' %}active{% endif %}">👁 Просмотры</a>
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

        {% if mod.tags_list %}
        <div class="mod-tags">
            {% for tag in mod.tags_list[:3] %}
                <span class="tag">#{{ tag }}</span>
            {% endfor %}
        </div>
        {% endif %}

        <div class="mod-footer">
            <div class="mod-stats">
                <span class="stat-item">⬇ {{ mod.downloads }}</span>
                <span class="stat-item">❤ {{ mod.likes_count }}</span>
                <span class="stat-item">👁 {{ mod.views or 0 }}</span>
            </div>
            <a href="{{ url_for('download', mod_id=mod.id) }}" class="btn-download">Скачать</a>
        </div>
    </div>
    {% else %}
        <div class="empty-state">
            <div class="empty-icon">📦</div>
            <h3>Ничего не найдено</h3>
            <p>Попробуй изменить параметры поиска</p>
        </div>
    {% endfor %}
</div>
{% endblock %}'''

# ============= MOD.HTML =============
mod_html = '''{% extends 'base.html' %}
{% block content %}
<div class="mod-detail">
    <div class="mod-detail-header">
        <span class="mod-category">{{ mod.category }}</span>
        <h1>{{ mod.title }}</h1>
        <div class="mod-meta-row">
            <span>👤 <a href="#" class="author-link">{{ mod.author.username }}</a></span>
            <span>📅 {{ mod.created_at.strftime('%d.%m.%Y') }}</span>
            <span>⬇ {{ mod.downloads }}</span>
            <span>❤ {{ mod.likes_count }}</span>
            <span>👁 {{ mod.views or 0 }}</span>
        </div>
    </div>

    <div class="mod-detail-grid">
        <div class="mod-detail-info">
            <table class="info-table">
                <tr><td>Версия мода</td><td><strong>{{ mod.version }}</strong></td></tr>
                <tr><td>Minecraft</td><td><strong>{{ mod.mc_version }}</strong></td></tr>
                <tr><td>Категория</td><td><strong>{{ mod.category }}</strong></td></tr>
                <tr><td>Скачиваний</td><td><strong>{{ mod.downloads }}</strong></td></tr>
                <tr><td>Просмотров</td><td><strong>{{ mod.views or 0 }}</strong></td></tr>
                <tr><td>Лайков</td><td><strong>{{ mod.likes_count }}</strong></td></tr>
            </table>

            {% if mod.tags_list %}
            <div class="tags-container">
                <h3>🏷️ Теги</h3>
                <div class="tags-row">
                    {% for tag in mod.tags_list %}
                        <span class="tag">#{{ tag }}</span>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            <div class="mod-description">
                <h3>📖 Описание</h3>
                <p>{{ mod.description }}</p>
            </div>
        </div>

        <div class="mod-detail-sidebar">
            <a href="{{ url_for('download', mod_id=mod.id) }}" class="btn-download-big">
                ⬇ Скачать .jar
            </a>

            {% if current_user.is_authenticated %}
            <button class="btn-like {% if mod.is_liked_by(current_user) %}liked{% endif %}"
                    onclick="toggleLike({{ mod.id }})" id="likeBtn">
                <span class="like-icon">{% if mod.is_liked_by(current_user) %}❤{% else %}🤍{% endif %}</span>
                <span class="like-text">
                    {% if mod.is_liked_by(current_user) %}В избранном{% else %}Лайкнуть{% endif %}
                </span>
                <span class="like-count">{{ mod.likes_count }}</span>
            </button>
            {% else %}
            <a href="{{ url_for('login') }}" class="btn-like">
                <span>🤍</span> Войди чтобы лайкнуть
            </a>
            {% endif %}

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

<script>
async function toggleLike(modId) {
    try {
        const response = await fetch(`/like/${modId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        const data = await response.json();
        const btn = document.getElementById('likeBtn');
        const icon = btn.querySelector('.like-icon');
        const text = btn.querySelector('.like-text');
        const count = btn.querySelector('.like-count');

        if (data.liked) {
            btn.classList.add('liked');
            icon.textContent = '❤';
            text.textContent = 'В избранном';
        } else {
            btn.classList.remove('liked');
            icon.textContent = '🤍';
            text.textContent = 'Лайкнуть';
        }
        count.textContent = data.count;
    } catch(e) {
        alert('Ошибка');
    }
}
</script>
{% endblock %}'''

# ============= UPLOAD.HTML =============
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

        <label>Теги (через запятую)</label>
        <input type="text" name="tags" placeholder="магия, оружие, рпг, выживание">

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

# ============= PROFILE.HTML =============
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
        <div class="stat-label">📦 Модов</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">{{ mods|sum(attribute='downloads') }}</div>
        <div class="stat-label">⬇ Скачиваний</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">{{ total_likes }}</div>
        <div class="stat-label">❤ Лайков</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">{{ total_views }}</div>
        <div class="stat-label">👁 Просмотров</div>
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
            <span>⬇ {{ mod.downloads }} ❤ {{ mod.likes_count }} 👁 {{ mod.views or 0 }}</span>
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

# ============= ДОБАВЛЯЕМ CSS =============
extra_css = '''

/* ===== TOP SECTION ===== */
.top-section {
    margin-bottom: 32px;
}

.top-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.top-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    text-decoration: none;
    color: inherit;
    transition: all 0.3s;
    position: relative;
    overflow: hidden;
}

.top-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: var(--gradient);
}

.top-card:hover {
    transform: translateY(-4px);
    border-color: var(--accent);
}

.top-rank {
    font-size: 32px;
    font-weight: 900;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    min-width: 60px;
}

.top-card.top-1 .top-rank { font-size: 40px; }

.top-info { flex: 1; }

.top-info h3 {
    font-size: 16px;
    margin: 6px 0;
}

.top-stats {
    display: flex;
    gap: 10px;
    font-size: 12px;
    color: var(--text-muted);
}

/* ===== SORT TABS ===== */
.sort-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.sort-tab {
    padding: 10px 18px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    text-decoration: none;
    color: var(--text-muted);
    font-weight: 600;
    font-size: 14px;
    transition: all 0.2s;
}

.sort-tab:hover {
    color: var(--text-main);
    border-color: var(--accent);
}

.sort-tab.active {
    background: var(--gradient);
    color: #0f1626;
    border-color: transparent;
}

/* ===== TAGS ===== */
.mod-tags {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin: 10px 0;
}

.tag {
    padding: 3px 10px;
    background: rgba(34, 255, 136, 0.1);
    color: var(--accent);
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}

.tags-container {
    background: var(--bg-card);
    padding: 16px;
    border-radius: 12px;
    margin: 16px 0;
}

.tags-container h3 {
    color: var(--accent);
    margin-bottom: 10px;
    font-size: 16px;
}

.tags-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

/* ===== MOD STATS ===== */
.mod-stats {
    display: flex;
    gap: 10px;
    font-size: 13px;
    color: var(--text-muted);
}

.stat-item {
    font-weight: 600;
}

/* ===== LIKE BUTTON ===== */
.btn-like {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 14px;
    background: var(--bg-card);
    border: 2px solid var(--border);
    border-radius: 12px;
    color: var(--text-main);
    text-decoration: none;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    width: 100%;
    font-size: 15px;
}

.btn-like:hover {
    border-color: #ff4757;
    transform: translateY(-2px);
}

.btn-like.liked {
    background: linear-gradient(135deg, #ff4757, #ff6b81);
    color: white;
    border-color: transparent;
}

.btn-like .like-icon {
    font-size: 20px;
}

.btn-like .like-count {
    background: rgba(255,255,255,0.2);
    padding: 2px 10px;
    border-radius: 10px;
    font-size: 13px;
}

.btn-like.liked .like-icon {
    animation: heartBeat 0.6s;
}

@keyframes heartBeat {
    0%, 100% { transform: scale(1); }
    25% { transform: scale(1.3); }
    50% { transform: scale(0.9); }
    75% { transform: scale(1.15); }
}

/* Адаптив */
@media (max-width: 768px) {
    .top-grid { grid-template-columns: 1fr; }
}
'''

# ============= ЗАПИСЫВАЕМ ФАЙЛЫ =============
files = {
    "app.py": app_py,
    "templates/index.html": index_html,
    "templates/mod.html": mod_html,
    "templates/upload.html": upload_html,
    "templates/profile.html": profile_html,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ {path}")

# Добавляем CSS к существующему style.css
css_path = "static/css/style.css"
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        existing_css = f.read()

    # Проверяем, не добавлены ли уже эти стили
    if "/* ===== TOP SECTION ===== */" not in existing_css:
        with open(css_path, "a", encoding="utf-8") as f:
            f.write(extra_css)
        print(f"  ✅ {css_path} (добавлены новые стили)")
    else:
        # Заменяем старые на новые
        marker = "/* ===== TOP SECTION ===== */"
        new_css = existing_css.split(marker)[0] + extra_css
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(new_css)
        print(f"  ✅ {css_path} (обновлены стили)")

print("\n🎉 ЭТАП 1 ГОТОВ!")
print("\n✨ Добавлено:")
print("   ⭐ Лайки на моды")
print("   👁️ Счётчик просмотров")
print("   🏆 Топ-3 мода на главной")
print("   🔍 Расширенный поиск (по описанию и тегам)")
print("   🏷️ Теги для модов")
print("   🎨 Сортировка (новые/популярные/лучшие/просмотры)")
print("\n📤 Залей на GitHub:")
print("   git add .")
print('   git commit -m "v2: лайки, просмотры, топ, теги"')
print("   git push --force origin main")
print("\nЗатем на PythonAnywhere в Bash:")
print("   cd ~/mysite")
print("   git fetch origin main")
print("   git reset --hard origin/main")
print("\nИ нажми Reload на вкладке Web")
print("\n👉 После запуска напиши 'готово' — продолжим Этап 2!")