# -*- coding: utf-8 -*-
import os

print("🚀 Этап 3 — Аватарки, Избранное, Достижения, Подписки...")

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
app.config['AVATARS_FOLDER'] = 'static/avatars'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SCREENSHOTS_FOLDER'], exist_ok=True)
os.makedirs(app.config['AVATARS_FOLDER'], exist_ok=True)

# ===== ДОСТИЖЕНИЯ =====
ACHIEVEMENTS = {
    'first_mod': {'name': 'Первый шаг', 'desc': 'Загрузил первый мод', 'icon': '🎯'},
    'mods_5': {'name': 'Моддер', 'desc': '5 модов опубликовано', 'icon': '🛠️'},
    'mods_10': {'name': 'Профи', 'desc': '10 модов опубликовано', 'icon': '⚡'},
    'mods_25': {'name': 'Мастер', 'desc': '25 модов опубликовано', 'icon': '🏆'},
    'downloads_10': {'name': 'Замечен', 'desc': '10 скачиваний', 'icon': '👀'},
    'downloads_100': {'name': 'Популярный', 'desc': '100 скачиваний', 'icon': '🔥'},
    'downloads_1000': {'name': 'Легенда', 'desc': '1000 скачиваний', 'icon': '👑'},
    'likes_10': {'name': 'Любимец', 'desc': '10 лайков', 'icon': '❤️'},
    'likes_50': {'name': 'Звезда', 'desc': '50 лайков', 'icon': '⭐'},
    'likes_100': {'name': 'Кумир', 'desc': '100 лайков', 'icon': '💎'},
    'first_comment': {'name': 'Социальный', 'desc': 'Первый комментарий', 'icon': '💬'},
    'comments_10': {'name': 'Болтун', 'desc': '10 комментариев', 'icon': '🗣️'},
    'first_like': {'name': 'Поддержка', 'desc': 'Поставил первый лайк', 'icon': '👍'},
    'subscriber': {'name': 'Подписчик', 'desc': 'Подписался на автора', 'icon': '🔔'},
    'popular_author': {'name': 'Известный', 'desc': '5 подписчиков', 'icon': '🌟'},
}

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
    avatar = db.Column(db.String(300), default='')
    mods = db.relationship('Mod', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True, cascade='all, delete-orphan')

    @property
    def avatar_url(self):
        if self.avatar:
            return url_for('static', filename='avatars/' + self.avatar)
        return None

    @property
    def total_downloads(self):
        return sum(m.downloads for m in self.mods)

    @property
    def total_likes(self):
        return sum(m.likes_count for m in self.mods)

    @property
    def followers_count(self):
        return Subscription.query.filter_by(author_id=self.id).count()

    @property
    def following_count(self):
        return Subscription.query.filter_by(follower_id=self.id).count()

    def is_subscribed_to(self, author):
        if not author or self.id == author.id:
            return False
        return Subscription.query.filter_by(follower_id=self.id, author_id=author.id).first() is not None

    def get_achievements(self):
        earned = []
        mods_count = len(self.mods)
        downloads = self.total_downloads
        likes_received = self.total_likes
        comments_count = len(self.comments)
        likes_given = len(self.likes)
        followers = self.followers_count
        following = self.following_count

        if mods_count >= 1: earned.append('first_mod')
        if mods_count >= 5: earned.append('mods_5')
        if mods_count >= 10: earned.append('mods_10')
        if mods_count >= 25: earned.append('mods_25')
        if downloads >= 10: earned.append('downloads_10')
        if downloads >= 100: earned.append('downloads_100')
        if downloads >= 1000: earned.append('downloads_1000')
        if likes_received >= 10: earned.append('likes_10')
        if likes_received >= 50: earned.append('likes_50')
        if likes_received >= 100: earned.append('likes_100')
        if comments_count >= 1: earned.append('first_comment')
        if comments_count >= 10: earned.append('comments_10')
        if likes_given >= 1: earned.append('first_like')
        if following >= 1: earned.append('subscriber')
        if followers >= 5: earned.append('popular_author')

        return earned

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
    def likes_count(self): return len(self.likes)
    @property
    def comments_count(self): return len(self.comments)
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

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return filename.lower().endswith('.jar')

def allowed_image(filename):
    return filename.lower().rsplit('.', 1)[-1] in {'jpg', 'jpeg', 'png', 'gif', 'webp'}

@app.context_processor
def inject_globals():
    if current_user.is_authenticated:
        return dict(user_theme=current_user.theme, user_animations=current_user.animations, ACHIEVEMENTS=ACHIEVEMENTS)
    return dict(user_theme='green', user_animations=True, ACHIEVEMENTS=ACHIEVEMENTS)

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

@app.route('/feed')
@login_required
def feed():
    sub_ids = [s.author_id for s in Subscription.query.filter_by(follower_id=current_user.id).all()]
    mods = Mod.query.filter(Mod.user_id.in_(sub_ids)).order_by(Mod.created_at.desc()).all() if sub_ids else []
    return render_template('feed.html', mods=mods)

@app.route('/favorites')
@login_required
def favorites():
    liked_ids = [l.mod_id for l in Like.query.filter_by(user_id=current_user.id).all()]
    mods = Mod.query.filter(Mod.id.in_(liked_ids)).order_by(Mod.created_at.desc()).all() if liked_ids else []
    return render_template('favorites.html', mods=mods)

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
        flash('Слишком длинный комментарий', 'error')
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
    return render_template('user.html', user=user, mods=mods)

@app.route('/subscribe/<int:user_id>', methods=['POST'])
@login_required
def subscribe(user_id):
    if user_id == current_user.id:
        return jsonify({'error': 'Нельзя подписаться на себя'})
    author = User.query.get_or_404(user_id)
    existing = Subscription.query.filter_by(follower_id=current_user.id, author_id=user_id).first()
    if existing:
        db.session.delete(existing)
        subscribed = False
    else:
        sub = Subscription(follower_id=current_user.id, author_id=user_id)
        db.session.add(sub)
        subscribed = True
    db.session.commit()
    return jsonify({'subscribed': subscribed, 'count': author.followers_count})

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
    return render_template('profile.html', mods=mods)

@app.route('/achievements')
@login_required
def achievements():
    earned = current_user.get_achievements()
    return render_template('achievements.html', earned=earned, all_achievements=ACHIEVEMENTS)

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
        elif action == 'avatar':
            avatar = request.files.get('avatar')
            if avatar and avatar.filename and allowed_image(avatar.filename):
                ext = avatar.filename.rsplit('.', 1)[-1].lower()
                # Удаляем старую
                if current_user.avatar:
                    old = os.path.join(app.config['AVATARS_FOLDER'], current_user.avatar)
                    if os.path.exists(old): os.remove(old)
                av_name = f"{current_user.id}_{int(datetime.utcnow().timestamp())}.{ext}"
                avatar.save(os.path.join(app.config['AVATARS_FOLDER'], av_name))
                current_user.avatar = av_name
                db.session.commit()
                flash('Аватарка обновлена!', 'success')
            else:
                flash('Выбери картинку (jpg, png, gif)', 'error')
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
                "ALTER TABLE user ADD COLUMN avatar VARCHAR(300) DEFAULT ''",
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
                <span class="nav-icon">🏠</span><span>Каталог</span>
            </a>
            {% if current_user.is_authenticated %}
            <a href="{{ url_for('feed') }}" class="nav-item">
                <span class="nav-icon">📡</span><span>Подписки</span>
            </a>
            <a href="{{ url_for('favorites') }}" class="nav-item">
                <span class="nav-icon">❤️</span><span>Избранное</span>
            </a>
            <a href="{{ url_for('upload') }}" class="nav-item">
                <span class="nav-icon">📤</span><span>Загрузить</span>
            </a>
            <a href="{{ url_for('profile') }}" class="nav-item">
                <span class="nav-icon">👤</span><span>Профиль</span>
            </a>
            <a href="{{ url_for('achievements') }}" class="nav-item">
                <span class="nav-icon">🏅</span><span>Достижения</span>
            </a>
            <a href="{{ url_for('settings') }}" class="nav-item">
                <span class="nav-icon">⚙️</span><span>Настройки</span>
            </a>
            {% endif %}
        </nav>

        <div class="sidebar-footer">
            {% if current_user.is_authenticated %}
                <div class="user-card">
                    {% if current_user.avatar %}
                        <img src="{{ url_for('static', filename='avatars/' + current_user.avatar) }}" class="user-avatar-img" alt="avatar">
                    {% else %}
                        <div class="user-avatar">{{ current_user.username[0]|upper }}</div>
                    {% endif %}
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

# ============= USER.HTML =============
user_html = '''{% extends 'base.html' %}
{% block content %}
<div class="profile-header">
    {% if user.avatar %}
        <img src="{{ url_for('static', filename='avatars/' + user.avatar) }}" class="profile-avatar-img" alt="avatar">
    {% else %}
        <div class="profile-avatar-big">{{ user.username[0]|upper }}</div>
    {% endif %}
    <div class="profile-info">
        <h1>{{ user.username }}</h1>
        {% if user.bio %}
            <p class="profile-bio">{{ user.bio }}</p>
        {% endif %}
        <p class="profile-date">📅 С нами с {{ user.created_at.strftime('%d.%m.%Y') }}</p>

        <div class="profile-actions">
            {% if current_user.is_authenticated and current_user.id != user.id %}
            <button class="btn-subscribe {% if current_user.is_subscribed_to(user) %}subscribed{% endif %}"
                    onclick="toggleSubscribe({{ user.id }})" id="subBtn">
                <span class="sub-text">
                    {% if current_user.is_subscribed_to(user) %}✓ Подписан{% else %}+ Подписаться{% endif %}
                </span>
                <span class="sub-count">{{ user.followers_count }}</span>
            </button>
            {% elif not current_user.is_authenticated %}
            <a href="{{ url_for('login') }}" class="btn-subscribe">+ Подписаться</a>
            {% endif %}
        </div>
    </div>
</div>

<div class="profile-stats">
    <div class="stat-card">
        <div class="stat-num">{{ mods|length }}</div>
        <div class="stat-label">📦 Модов</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">{{ user.total_downloads }}</div>
        <div class="stat-label">⬇ Скачиваний</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">{{ user.total_likes }}</div>
        <div class="stat-label">❤ Лайков</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">{{ user.followers_count }}</div>
        <div class="stat-label">👥 Подписчиков</div>
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

<script>
async function toggleSubscribe(userId) {
    try {
        const response = await fetch(`/subscribe/${userId}`, {method: 'POST'});
        const data = await response.json();
        if (data.error) { alert(data.error); return; }
        const btn = document.getElementById('subBtn');
        const text = btn.querySelector('.sub-text');
        const count = btn.querySelector('.sub-count');
        if (data.subscribed) {
            btn.classList.add('subscribed');
            text.textContent = '✓ Подписан';
        } else {
            btn.classList.remove('subscribed');
            text.textContent = '+ Подписаться';
        }
        count.textContent = data.count;
    } catch(e) { alert('Ошибка'); }
}
</script>
{% endblock %}'''

# ============= PROFILE.HTML =============
profile_html = '''{% extends 'base.html' %}
{% block content %}
<div class="profile-header">
    {% if current_user.avatar %}
        <img src="{{ url_for('static', filename='avatars/' + current_user.avatar) }}" class="profile-avatar-img" alt="avatar">
    {% else %}
        <div class="profile-avatar-big">{{ current_user.username[0]|upper }}</div>
    {% endif %}
    <div class="profile-info">
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
        <div class="stat-num">{{ current_user.total_downloads }}</div>
        <div class="stat-label">⬇ Скачиваний</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">{{ current_user.total_likes }}</div>
        <div class="stat-label">❤ Лайков</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">{{ current_user.followers_count }}</div>
        <div class="stat-label">👥 Подписчиков</div>
    </div>
    <div class="stat-card">
        <div class="stat-num">{{ current_user.following_count }}</div>
        <div class="stat-label">📡 Подписок</div>
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

# ============= ACHIEVEMENTS.HTML =============
achievements_html = '''{% extends 'base.html' %}
{% block content %}
<div class="page-header">
    <div>
        <h1 class="page-title">🏅 Достижения</h1>
        <p class="page-subtitle">Получено {{ earned|length }} из {{ all_achievements|length }}</p>
    </div>
    <div class="stats-mini">
        <div class="stat-mini">
            <div class="stat-num">{{ ((earned|length / all_achievements|length) * 100)|int }}%</div>
            <div class="stat-label">Прогресс</div>
        </div>
    </div>
</div>

<div class="achievements-grid">
    {% for key, ach in all_achievements.items() %}
    <div class="achievement {% if key in earned %}earned{% endif %}">
        <div class="ach-icon">{{ ach.icon }}</div>
        <div class="ach-info">
            <div class="ach-name">{{ ach.name }}</div>
            <div class="ach-desc">{{ ach.desc }}</div>
        </div>
        {% if key in earned %}
            <div class="ach-badge">✓</div>
        {% else %}
            <div class="ach-lock">🔒</div>
        {% endif %}
    </div>
    {% endfor %}
</div>
{% endblock %}'''

# ============= FAVORITES.HTML =============
favorites_html = '''{% extends 'base.html' %}
{% block content %}
<div class="page-header">
    <div>
        <h1 class="page-title">❤️ Избранное</h1>
        <p class="page-subtitle">Моды которые ты лайкнул</p>
    </div>
    <div class="stats-mini">
        <div class="stat-mini">
            <div class="stat-num">{{ mods|length }}</div>
            <div class="stat-label">Модов</div>
        </div>
    </div>
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
            <span>v{{ mod.version }}</span> • <span>👤 {{ mod.author.username }}</span>
        </p>
        <p class="mod-desc">{{ mod.description[:120] }}{% if mod.description|length > 120 %}...{% endif %}</p>
        <div class="mod-footer">
            <div class="mod-stats">
                <span>⬇ {{ mod.downloads }}</span>
                <span>❤ {{ mod.likes_count }}</span>
            </div>
            <a href="{{ url_for('download', mod_id=mod.id) }}" class="btn-download">Скачать</a>
        </div>
    </div>
    {% else %}
        <div class="empty-state">
            <div class="empty-icon">💔</div>
            <h3>В избранном пусто</h3>
            <p>Лайкни понравившиеся моды!</p>
            <a href="{{ url_for('index') }}" class="btn-download-big">К каталогу</a>
        </div>
    {% endfor %}
</div>
{% endblock %}'''

# ============= FEED.HTML =============
feed_html = '''{% extends 'base.html' %}
{% block content %}
<div class="page-header">
    <div>
        <h1 class="page-title">📡 Лента подписок</h1>
        <p class="page-subtitle">Новые моды от авторов, на которых ты подписан</p>
    </div>
    <div class="stats-mini">
        <div class="stat-mini">
            <div class="stat-num">{{ mods|length }}</div>
            <div class="stat-label">Модов</div>
        </div>
    </div>
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
            <span>v{{ mod.version }}</span> • <span>👤 {{ mod.author.username }}</span>
        </p>
        <p class="mod-desc">{{ mod.description[:120] }}{% if mod.description|length > 120 %}...{% endif %}</p>
        <div class="mod-footer">
            <div class="mod-stats">
                <span>⬇ {{ mod.downloads }}</span>
                <span>❤ {{ mod.likes_count }}</span>
            </div>
            <a href="{{ url_for('download', mod_id=mod.id) }}" class="btn-download">Скачать</a>
        </div>
    </div>
    {% else %}
        <div class="empty-state">
            <div class="empty-icon">📡</div>
            <h3>Лента пуста</h3>
            <p>Подпишись на интересных авторов!</p>
            <a href="{{ url_for('index') }}" class="btn-download-big">Найти авторов</a>
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
        <h3>🖼️ Аватарка</h3>
        <p class="settings-desc">Загрузи свою аватарку (jpg, png, gif)</p>
        <form method="POST" enctype="multipart/form-data">
            <input type="hidden" name="action" value="avatar">
            <div class="avatar-upload">
                {% if current_user.avatar %}
                    <img src="{{ url_for('static', filename='avatars/' + current_user.avatar) }}" class="current-avatar" alt="avatar">
                {% else %}
                    <div class="current-avatar-letter">{{ current_user.username[0]|upper }}</div>
                {% endif %}
                <label class="file-label-small">
                    📁 Выбрать файл
                    <input type="file" name="avatar" accept="image/*" required onchange="this.form.submit()">
                </label>
            </div>
        </form>
    </div>

    <div class="settings-card">
        <h3>🎨 Тема оформления</h3>
        <p class="settings-desc">Выбери цветовую схему сайта</p>
        <form method="POST">
            <input type="hidden" name="action" value="theme">
            <div class="theme-grid">
                {% for tk, tn in [('green','Зелёный'),('blue','Синий'),('purple','Фиолетовый'),('orange','Оранжевый'),('pink','Розовый'),('light','Светлая')] %}
                <label class="theme-option theme-{{ tk }} {% if current_user.theme == tk %}active{% endif %}">
                    <input type="radio" name="theme" value="{{ tk }}" {% if current_user.theme == tk %}checked{% endif %}>
                    <div class="theme-preview">
                        <div class="tp-bar"></div>
                        <div class="tp-content"></div>
                    </div>
                    <div class="theme-name">{{ tn }}</div>
                </label>
                {% endfor %}
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

# ============= ДОБАВЛЯЕМ CSS =============
extra_css = '''

/* ===== AVATAR ===== */
.user-avatar-img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid var(--accent);
}

.profile-avatar-img {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid var(--accent);
}

.profile-info { flex: 1; }

.profile-actions {
    margin-top: 12px;
}

/* ===== SUBSCRIBE ===== */
.btn-subscribe {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 10px 20px;
    background: var(--gradient);
    color: #0f1626;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.2s;
    font-size: 14px;
}

.btn-subscribe:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(34, 255, 136, 0.3);
}

.btn-subscribe.subscribed {
    background: var(--bg-card);
    color: var(--text-main);
    border: 2px solid var(--accent);
}

.sub-count {
    background: rgba(255,255,255,0.2);
    padding: 2px 10px;
    border-radius: 10px;
    font-size: 12px;
}

.btn-subscribe.subscribed .sub-count {
    background: var(--accent);
    color: #0f1626;
}

/* ===== AVATAR UPLOAD ===== */
.avatar-upload {
    display: flex;
    align-items: center;
    gap: 20px;
}

.current-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid var(--accent);
}

.current-avatar-letter {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: var(--gradient);
    color: #0f1626;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    font-weight: 800;
}

.file-label-small {
    background: var(--bg-main);
    border: 2px dashed var(--accent);
    padding: 10px 20px;
    border-radius: 10px;
    cursor: pointer;
    color: var(--accent);
    font-weight: 600;
    transition: all 0.2s;
}

.file-label-small:hover {
    background: rgba(34, 255, 136, 0.1);
}

.file-label-small input {
    display: none;
}

/* ===== ACHIEVEMENTS ===== */
.achievements-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 14px;
}

.achievement {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 18px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    gap: 14px;
    opacity: 0.5;
    transition: all 0.3s;
    position: relative;
    overflow: hidden;
}

.achievement.earned {
    opacity: 1;
    border-color: var(--accent);
    background: linear-gradient(135deg, var(--bg-card), rgba(34, 255, 136, 0.05));
}

.achievement.earned::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px;
    height: 100%;
    background: var(--gradient);
}

.ach-icon {
    font-size: 40px;
    filter: grayscale(100%);
    transition: filter 0.3s;
}

.achievement.earned .ach-icon {
    filter: none;
    animation: bounce 0.5s ease;
}

@keyframes bounce {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.2); }
}

.ach-info { flex: 1; }

.ach-name {
    font-weight: 700;
    margin-bottom: 4px;
}

.ach-desc {
    font-size: 13px;
    color: var(--text-muted);
}

.ach-badge {
    background: var(--gradient);
    color: #0f1626;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 16px;
}

.ach-lock {
    font-size: 24px;
    opacity: 0.5;
}

@media (max-width: 600px) {
    .avatar-upload { flex-direction: column; align-items: flex-start; }
}
'''

# ============= ЗАПИСЫВАЕМ =============
files = {
    "app.py": app_py,
    "templates/base.html": base_html,
    "templates/user.html": user_html,
    "templates/profile.html": profile_html,
    "templates/achievements.html": achievements_html,
    "templates/favorites.html": favorites_html,
    "templates/feed.html": feed_html,
    "templates/settings.html": settings_html,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ {path}")

css_path = "static/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    existing_css = f.read()

if "/* ===== AVATAR ===== */" not in existing_css:
    with open(css_path, "a", encoding="utf-8") as f:
        f.write(extra_css)
    print(f"  ✅ {css_path}")

os.makedirs("static/avatars", exist_ok=True)
with open("static/avatars/.gitkeep", "w") as f:
    f.write("")
print("  ✅ static/avatars/")

print("\n🎉 ЭТАП 3 ГОТОВ!")
print("\n✨ Добавлено:")
print("   🖼️ Загрузка аватарок")
print("   ❤️ Страница Избранное (лайкнутые моды)")
print("   🏅 15 достижений с автополучением")
print("   👥 Подписки на авторов")
print("   📡 Лента подписок")
print("\n📤 git add . && git commit -m 'v4: avatars+favs+achievements+subs' && git push --force origin main")
print("На PA: cd ~/mysite && git fetch origin main && git reset --hard origin/main")
print("Reload на вкладке Web")
print("\n👉 Напиши 'готово' — продолжим Этап 4 (уведомления, ЛС, активность)")