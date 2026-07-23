# -*- coding: utf-8 -*-
import os

print("🚀 Этап 2 — Комментарии, Скриншоты, Страница автора...")

# ============= APP.PY =============
app_py = '''# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, abort
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
app.config['SCREENSHOTS_FOLDER'] = 'static/screenshots'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SCREENSHOTS_FOLDER'], exist_ok=True)

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
    comments = db.relationship('Comment', backref='user', lazy=True, cascade='all, delete-orphan')

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
    screenshots = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('Like', backref='mod', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='mod', lazy=True, cascade='all, delete-orphan')

    @property
    def likes_count(self):
        return len(self.likes)

    @property
    def comments_count(self):
        return len(self.comments)

    @property
    def tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()] if self.tags else []

    @property
    def screenshots_list(self):
        return [s.strip() for s in self.screenshots.split(',') if s.strip()] if self.screenshots else []

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return Like.query.filter_by(user_id=user.id, mod_id=self.id).first() is not None

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mod_id = db.Column(db.Integer, db.ForeignKey('mod.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mod_id = db.Column(db.Integer, db.ForeignKey('mod.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return filename.lower().endswith('.jar')

def allowed_image(filename):
    return filename.lower().rsplit('.', 1)[-1] in {'jpg', 'jpeg', 'png', 'gif', 'webp'}

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
    sort = request.args.get('sort', 'new')

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
        query = query.outerjoin(Like).group_by(Mod.id).order_by(func.count(Like.id).desc())
    elif sort == 'views':
        query = query.order_by(Mod.views.desc())
    else:
        query = query.order_by(Mod.created_at.desc())

    mods = query.all()
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
        flash('Регистрация успешна!', 'success')
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

        # Скриншоты
        screenshots = []
        for i in range(1, 6):
            screenshot = request.files.get(f'screenshot{i}')
            if screenshot and screenshot.filename and allowed_image(screenshot.filename):
                ext = screenshot.filename.rsplit('.', 1)[-1].lower()
                ss_name = f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{i}.{ext}"
                screenshot.save(os.path.join(app.config['SCREENSHOTS_FOLDER'], ss_name))
                screenshots.append(ss_name)

        mod = Mod(
            title=request.form['title'],
            description=request.form['description'],
            version=request.form['version'],
            mc_version=request.form['mc_version'],
            category=request.form['category'],
            tags=request.form.get('tags', ''),
            screenshots=','.join(screenshots),
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
    mod.views = (mod.views or 0) + 1
    db.session.commit()
    comments = Comment.query.filter_by(mod_id=mod_id).order_by(Comment.created_at.desc()).all()
    return render_template('mod.html', mod=mod, comments=comments)

@app.route('/mod/<int:mod_id>/comment', methods=['POST'])
@login_required
def add_comment(mod_id):
    mod = Mod.query.get_or_404(mod_id)
    text = request.form.get('text', '').strip()
    if not text:
        flash('Комментарий не может быть пустым', 'error')
        return redirect(url_for('mod_page', mod_id=mod_id))
    if len(text) > 1000:
        flash('Слишком длинный комментарий (макс 1000)', 'error')
        return redirect(url_for('mod_page', mod_id=mod_id))
    comment = Comment(text=text, user_id=current_user.id, mod_id=mod_id)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('mod_page', mod_id=mod_id) + '#comments')

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    mod_id = comment.mod_id
    if comment.user_id != current_user.id and comment.mod.user_id != current_user.id:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('mod_page', mod_id=mod_id) + '#comments')

@app.route('/user/<username>')
def user_page(username):
    user = User.query.filter_by(username=username).first_or_404()
    mods = Mod.query.filter_by(user_id=user.id).order_by(Mod.created_at.desc()).all()
    total_likes = sum(m.likes_count for m in mods)
    total_views = sum(m.views or 0 for m in mods)
    total_downloads = sum(m.downloads for m in mods)
    return render_template('user.html', user=user, mods=mods,
                           total_likes=total_likes, total_views=total_views, total_downloads=total_downloads)

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
            current_user.theme = request.form.get('theme', 'green')
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
    # Удаляем скриншоты
    for ss in mod.screenshots_list:
        ss_path = os.path.join(app.config['SCREENSHOTS_FOLDER'], ss)
        if os.path.exists(ss_path):
            os.remove(ss_path)
    db.session.delete(mod)
    db.session.commit()
    flash('Мод удалён', 'success')
    return redirect(url_for('profile'))

with app.app_context():
    db.create_all()
    try:
        with db.engine.connect() as conn:
            for sql in [
                "ALTER TABLE user ADD COLUMN theme VARCHAR(20) DEFAULT 'green'",
                "ALTER TABLE user ADD COLUMN animations BOOLEAN DEFAULT 1",
                "ALTER TABLE user ADD COLUMN bio VARCHAR(300) DEFAULT ''",
                "ALTER TABLE mod ADD COLUMN views INTEGER DEFAULT 0",
                "ALTER TABLE mod ADD COLUMN tags VARCHAR(300) DEFAULT ''",
                "ALTER TABLE mod ADD COLUMN screenshots TEXT DEFAULT ''",
            ]:
                try: conn.execute(text(sql))
                except: pass
            conn.commit()
    except Exception as e:
        print(f"Migration: {e}")

if __name__ == '__main__':
    app.run(debug=True)
'''

# ============= MOD.HTML =============
mod_html = '''{% extends 'base.html' %}
{% block content %}
<div class="mod-detail">
    <div class="mod-detail-header">
        <span class="mod-category">{{ mod.category }}</span>
        <h1>{{ mod.title }}</h1>
        <div class="mod-meta-row">
            <span>👤 <a href="{{ url_for('user_page', username=mod.author.username) }}" class="author-link">{{ mod.author.username }}</a></span>
            <span>📅 {{ mod.created_at.strftime('%d.%m.%Y') }}</span>
            <span>⬇ {{ mod.downloads }}</span>
            <span>❤ {{ mod.likes_count }}</span>
            <span>👁 {{ mod.views or 0 }}</span>
            <span>💬 {{ mod.comments_count }}</span>
        </div>
    </div>

    {% if mod.screenshots_list %}
    <div class="screenshots-section">
        <h3>📸 Скриншоты</h3>
        <div class="screenshots-grid">
            {% for ss in mod.screenshots_list %}
                <img src="{{ url_for('static', filename='screenshots/' + ss) }}"
                     alt="Screenshot" class="screenshot"
                     onclick="openLightbox('{{ url_for('static', filename='screenshots/' + ss) }}')">
            {% endfor %}
        </div>
    </div>
    {% endif %}

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
                <span class="like-text">{% if mod.is_liked_by(current_user) %}В избранном{% else %}Лайкнуть{% endif %}</span>
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
                    <a href="{{ url_for('user_page', username=mod.author.username) }}" class="author-link"><strong>{{ mod.author.username }}</strong></a>
                </div>
                <div class="qi-row">
                    <span>Опубликовано</span>
                    <strong>{{ mod.created_at.strftime('%d.%m.%Y') }}</strong>
                </div>
            </div>
        </div>
    </div>

    <div class="comments-section" id="comments">
        <h3>💬 Комментарии ({{ comments|length }})</h3>

        {% if current_user.is_authenticated %}
        <form method="POST" action="{{ url_for('add_comment', mod_id=mod.id) }}" class="comment-form">
            <textarea name="text" placeholder="Напиши комментарий..." rows="3" required maxlength="1000"></textarea>
            <button type="submit">Отправить</button>
        </form>
        {% else %}
        <div class="login-to-comment">
            <a href="{{ url_for('login') }}">Войди</a> чтобы оставить комментарий
        </div>
        {% endif %}

        <div class="comments-list">
            {% for comment in comments %}
            <div class="comment">
                <div class="comment-avatar">{{ comment.user.username[0]|upper }}</div>
                <div class="comment-body">
                    <div class="comment-header">
                        <a href="{{ url_for('user_page', username=comment.user.username) }}" class="comment-author">
                            {{ comment.user.username }}
                        </a>
                        <span class="comment-date">{{ comment.created_at.strftime('%d.%m.%Y %H:%M') }}</span>
                    </div>
                    <div class="comment-text">{{ comment.text }}</div>
                    {% if current_user.is_authenticated and (current_user.id == comment.user_id or current_user.id == mod.user_id) %}
                    <form method="POST" action="{{ url_for('delete_comment', comment_id=comment.id) }}" style="display:inline">
                        <button type="submit" class="comment-delete" onclick="return confirm('Удалить комментарий?')">🗑</button>
                    </form>
                    {% endif %}
                </div>
            </div>
            {% else %}
            <div class="no-comments">Пока нет комментариев. Будь первым!</div>
            {% endfor %}
        </div>
    </div>
</div>

<div id="lightbox" class="lightbox" onclick="closeLightbox()">
    <img id="lightbox-img" src="" alt="">
    <span class="lightbox-close">&times;</span>
</div>

<script>
async function toggleLike(modId) {
    try {
        const response = await fetch(`/like/${modId}`, {method: 'POST'});
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
    } catch(e) { alert('Ошибка'); }
}

function openLightbox(src) {
    document.getElementById('lightbox-img').src = src;
    document.getElementById('lightbox').classList.add('active');
}

function closeLightbox() {
    document.getElementById('lightbox').classList.remove('active');
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

        <label>📸 Скриншоты (необязательно, до 5)</label>
        <div class="screenshots-upload">
            {% for i in range(1, 6) %}
            <label class="ss-upload-box">
                <span>📷 {{ i }}</span>
                <input type="file" name="screenshot{{ i }}" accept="image/*">
            </label>
            {% endfor %}
        </div>

        <button type="submit">🚀 Опубликовать мод</button>
    </form>
</div>
{% endblock %}'''

# ============= USER.HTML =============
user_html = '''{% extends 'base.html' %}
{% block content %}
<div class="profile-header">
    <div class="profile-avatar-big">{{ user.username[0]|upper }}</div>
    <div>
        <h1>{{ user.username }}</h1>
        {% if user.bio %}
            <p class="profile-bio">{{ user.bio }}</p>
        {% endif %}
        <p class="profile-date">📅 С нами с {{ user.created_at.strftime('%d.%m.%Y') }}</p>
    </div>
</div>

<div class="profile-stats">
    <div class="stat-card">
        <div class="stat-num">{{ mods|length }}</div>
        <div class="stat-label">📦 Модов</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">{{ total_downloads }}</div>
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

<h3 class="section-title">📦 Моды автора</h3>

<div class="mods-grid">
    {% for mod in mods %}
    <div class="mod-card">
        <div class="mod-card-header">
            <div class="mod-category">{{ mod.category }}</div>
            <div class="mod-mc-badge">MC {{ mod.mc_version }}</div>
        </div>
        <h3><a href="{{ url_for('mod_page', mod_id=mod.id) }}">{{ mod.title }}</a></h3>
        <p class="mod-meta"><span>v{{ mod.version }}</span></p>
        <p class="mod-desc">{{ mod.description[:120] }}{% if mod.description|length > 120 %}...{% endif %}</p>
        <div class="mod-footer">
            <div class="mod-stats">
                <span>⬇ {{ mod.downloads }}</span>
                <span>❤ {{ mod.likes_count }}</span>
                <span>👁 {{ mod.views or 0 }}</span>
            </div>
            <a href="{{ url_for('download', mod_id=mod.id) }}" class="btn-download">Скачать</a>
        </div>
    </div>
    {% else %}
        <div class="empty-state">
            <div class="empty-icon">📦</div>
            <h3>У автора пока нет модов</h3>
        </div>
    {% endfor %}
</div>
{% endblock %}'''

# ============= ДОБАВЛЯЕМ CSS =============
extra_css = '''

/* ===== COMMENTS ===== */
.comments-section {
    margin-top: 40px;
    padding-top: 30px;
    border-top: 1px solid var(--border);
}

.comments-section h3 {
    margin-bottom: 20px;
    font-size: 22px;
}

.comment-form {
    background: var(--bg-card);
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 20px;
}

.comment-form textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--bg-main);
    color: var(--text-main);
    font-family: inherit;
    font-size: 14px;
    resize: vertical;
    transition: all 0.2s;
}

.comment-form textarea:focus {
    outline: none;
    border-color: var(--accent);
}

.comment-form button {
    margin-top: 12px;
    background: var(--gradient);
    color: #0f1626;
    border: none;
    padding: 10px 24px;
    border-radius: 10px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
}

.comment-form button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(34, 255, 136, 0.3);
}

.login-to-comment {
    background: var(--bg-card);
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: var(--text-muted);
    margin-bottom: 20px;
}

.login-to-comment a {
    color: var(--accent);
    font-weight: 700;
    text-decoration: none;
}

.comments-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.comment {
    background: var(--bg-card);
    padding: 16px;
    border-radius: 12px;
    display: flex;
    gap: 12px;
    animation: fadeIn 0.4s ease-out;
}

.comment-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--gradient);
    color: #0f1626;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    flex-shrink: 0;
}

.comment-body { flex: 1; }

.comment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
    flex-wrap: wrap;
    gap: 8px;
}

.comment-author {
    color: var(--accent);
    font-weight: 700;
    text-decoration: none;
}

.comment-author:hover {
    text-decoration: underline;
}

.comment-date {
    color: var(--text-muted);
    font-size: 12px;
}

.comment-text {
    color: var(--text-main);
    line-height: 1.5;
    word-wrap: break-word;
}

.comment-delete {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 16px;
    margin-top: 8px;
    opacity: 0.5;
    transition: opacity 0.2s;
}

.comment-delete:hover {
    opacity: 1;
    color: #ff7777;
}

.no-comments {
    text-align: center;
    padding: 40px;
    color: var(--text-muted);
    background: var(--bg-card);
    border-radius: 12px;
}

/* ===== SCREENSHOTS ===== */
.screenshots-section {
    margin-bottom: 24px;
}

.screenshots-section h3 {
    margin-bottom: 12px;
    color: var(--accent);
}

.screenshots-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 12px;
}

.screenshot {
    width: 100%;
    height: 130px;
    object-fit: cover;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s;
    border: 2px solid var(--border);
}

.screenshot:hover {
    transform: scale(1.03);
    border-color: var(--accent);
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
}

/* ===== LIGHTBOX ===== */
.lightbox {
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.9);
    z-index: 9999;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}

.lightbox.active {
    display: flex;
    animation: fadeIn 0.2s;
}

.lightbox img {
    max-width: 90%;
    max-height: 90%;
    border-radius: 10px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}

.lightbox-close {
    position: absolute;
    top: 20px;
    right: 30px;
    color: white;
    font-size: 50px;
    cursor: pointer;
    line-height: 1;
}

/* ===== UPLOAD SCREENSHOTS ===== */
.screenshots-upload {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 8px;
    margin-bottom: 16px;
}

.ss-upload-box {
    background: var(--bg-main);
    border: 2px dashed var(--border);
    border-radius: 10px;
    padding: 20px 10px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 13px;
    color: var(--text-muted);
}

.ss-upload-box:hover {
    border-color: var(--accent);
    color: var(--accent);
}

.ss-upload-box input {
    display: none;
}

/* ===== AUTHOR LINK ===== */
.author-link {
    color: var(--accent);
    text-decoration: none;
    font-weight: 600;
}

.author-link:hover {
    text-decoration: underline;
}

@media (max-width: 768px) {
    .screenshots-upload { grid-template-columns: repeat(2, 1fr); }
}
'''

# ============= ЗАПИСЫВАЕМ =============
files = {
    "app.py": app_py,
    "templates/mod.html": mod_html,
    "templates/upload.html": upload_html,
    "templates/user.html": user_html,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ {path}")

# Добавляем CSS
css_path = "static/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    existing_css = f.read()

if "/* ===== COMMENTS ===== */" not in existing_css:
    with open(css_path, "a", encoding="utf-8") as f:
        f.write(extra_css)
    print(f"  ✅ {css_path} (добавлены новые стили)")

# Создаём папку для скриншотов
os.makedirs("static/screenshots", exist_ok=True)
# Создаём .gitkeep чтобы папка попала в git
with open("static/screenshots/.gitkeep", "w") as f:
    f.write("")
print("  ✅ static/screenshots/ (папка создана)")

print("\n🎉 ЭТАП 2 ГОТОВ!")
print("\n✨ Добавлено:")
print("   💬 Комментарии под модами")
print("   📸 Скриншоты (до 5 на мод)")
print("   👥 Страница автора (/user/имя)")
print("   🖼️ Lightbox для скриншотов")
print("\n📤 Залей на GitHub:")
print("   git add .")
print('   git commit -m "v3: комментарии, скриншоты, страница автора"')
print("   git push --force origin main")
print("\nНа PythonAnywhere в Bash:")
print("   cd ~/mysite")
print("   git fetch origin main")
print("   git reset --hard origin/main")
print("\nИ нажми Reload на вкладке Web")
print("\n👉 После запуска напиши 'готово' — продолжим Этап 3!")