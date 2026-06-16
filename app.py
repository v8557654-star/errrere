# -*- coding: utf-8 -*-
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
