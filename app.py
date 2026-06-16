# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, abort, Response, stream_with_context
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import func, or_, and_, text
from functools import wraps
import requests

ADMIN_USERNAME = 'nehea664'

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

ACHIEVEMENTS = {
    'first_mod': {'name': 'Первый шаг', 'desc': 'Загрузил первый мод', 'icon': '🎯'},
    'mods_5': {'name': 'Моддер', 'desc': '5 модов', 'icon': '🛠️'},
    'mods_10': {'name': 'Профи', 'desc': '10 модов', 'icon': '⚡'},
    'mods_25': {'name': 'Мастер', 'desc': '25 модов', 'icon': '🏆'},
    'downloads_10': {'name': 'Замечен', 'desc': '10 скачиваний', 'icon': '👀'},
    'downloads_100': {'name': 'Популярный', 'desc': '100 скачиваний', 'icon': '🔥'},
    'downloads_1000': {'name': 'Легенда', 'desc': '1000 скачиваний', 'icon': '👑'},
    'likes_10': {'name': 'Любимец', 'desc': '10 лайков', 'icon': '❤️'},
    'likes_50': {'name': 'Звезда', 'desc': '50 лайков', 'icon': '⭐'},
    'likes_100': {'name': 'Кумир', 'desc': '100 лайков', 'icon': '💎'},
    'first_comment': {'name': 'Социальный', 'desc': 'Первый коммент', 'icon': '💬'},
    'comments_10': {'name': 'Болтун', 'desc': '10 комментов', 'icon': '🗣️'},
    'first_like': {'name': 'Поддержка', 'desc': 'Первый лайк', 'icon': '👍'},
    'subscriber': {'name': 'Подписчик', 'desc': 'Подписался', 'icon': '🔔'},
    'popular_author': {'name': 'Известный', 'desc': '5 подписчиков', 'icon': '🌟'},
}

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
    is_banned = db.Column(db.Boolean, default=False)
    mods = db.relationship('Mod', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True, cascade='all, delete-orphan')

    @property
    def is_admin(self): return self.username == ADMIN_USERNAME
    @property
    def total_downloads(self): return sum(m.downloads for m in self.mods)
    @property
    def total_likes(self): return sum(m.likes_count for m in self.mods)
    @property
    def followers_count(self): return Subscription.query.filter_by(author_id=self.id).count()
    @property
    def following_count(self): return Subscription.query.filter_by(follower_id=self.id).count()
    @property
    def unread_notifications(self): return Notification.query.filter_by(user_id=self.id, is_read=False).count()
    @property
    def unread_messages(self): return Message.query.filter_by(to_user_id=self.id, is_read=False).count()

    def is_subscribed_to(self, author):
        if not author or self.id == author.id: return False
        return Subscription.query.filter_by(follower_id=self.id, author_id=author.id).first() is not None

    def get_achievements(self):
        earned = []
        mc = len(self.mods); dl = self.total_downloads; lr = self.total_likes
        cc = len(self.comments); lg = len(self.likes); fl = self.followers_count; fn = self.following_count
        if mc >= 1: earned.append('first_mod')
        if mc >= 5: earned.append('mods_5')
        if mc >= 10: earned.append('mods_10')
        if mc >= 25: earned.append('mods_25')
        if dl >= 10: earned.append('downloads_10')
        if dl >= 100: earned.append('downloads_100')
        if dl >= 1000: earned.append('downloads_1000')
        if lr >= 10: earned.append('likes_10')
        if lr >= 50: earned.append('likes_50')
        if lr >= 100: earned.append('likes_100')
        if cc >= 1: earned.append('first_comment')
        if cc >= 10: earned.append('comments_10')
        if lg >= 1: earned.append('first_like')
        if fn >= 1: earned.append('subscriber')
        if fl >= 5: earned.append('popular_author')
        return earned

class Mod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    version = db.Column(db.String(20), nullable=False)
    mc_version = db.Column(db.String(20), nullable=False)
    content_type = db.Column(db.String(30), default='mod')
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
        if not user or not user.is_authenticated: return False
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

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(50))
    text = db.Column(db.String(300))
    link = db.Column(db.String(300))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    @property
    def from_user(self):
        return User.query.get(self.from_user_id) if self.from_user_id else None

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    @property
    def from_user(self): return User.query.get(self.from_user_id)
    @property
    def to_user(self): return User.query.get(self.to_user_id)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50))
    text = db.Column(db.String(300))
    link = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated

def allowed_file(filename, content_type='mod'):
    fn = filename.lower()
    if content_type in ('mod', 'plugin'):
        return fn.endswith('.jar')
    elif content_type in ('shader', 'resourcepack', 'datapack', 'map'):
        return fn.endswith('.zip')
    elif content_type == 'modpack':
        return fn.endswith('.zip') or fn.endswith('.mrpack')
    return fn.endswith('.jar') or fn.endswith('.zip') or fn.endswith('.mrpack')

def allowed_image(filename):
    return filename.lower().rsplit('.', 1)[-1] in {'jpg', 'jpeg', 'png', 'gif', 'webp'}

def notify(user_id, type, text, link='', from_user_id=None):
    if from_user_id == user_id: return
    n = Notification(user_id=user_id, from_user_id=from_user_id, type=type, text=text, link=link)
    db.session.add(n)

def log_activity(user_id, type, text, link=''):
    a = Activity(user_id=user_id, type=type, text=text, link=link)
    db.session.add(a)

@app.context_processor
def inject_globals():
    if current_user.is_authenticated:
        return dict(
            user_theme=current_user.theme, user_animations=current_user.animations,
            ACHIEVEMENTS=ACHIEVEMENTS,
            unread_notif=current_user.unread_notifications,
            unread_msg=current_user.unread_messages,
            is_admin=current_user.is_admin,
        )
    return dict(user_theme='green', user_animations=True, ACHIEVEMENTS=ACHIEVEMENTS,
                unread_notif=0, unread_msg=0, is_admin=False)

@app.before_request
def check_banned():
    if current_user.is_authenticated and current_user.is_banned and not current_user.is_admin:
        logout_user()
        flash('Ваш аккаунт заблокирован', 'error')
        return redirect(url_for('login'))

# ===== РОУТЫ =====
@app.route('/')
def index():
    search = request.args.get('q', '')
    category = request.args.get('category', '')
    mc_version = request.args.get('mc_version', '')
    sort = request.args.get('sort', 'new')
    content_type = request.args.get('type', '')
    query = Mod.query
    if content_type:
        query = query.filter_by(content_type=content_type)
    if search:
        query = query.filter(or_(Mod.title.ilike(f'%{search}%'), Mod.description.ilike(f'%{search}%'), Mod.tags.ilike(f'%{search}%')))
    if category: query = query.filter_by(category=category)
    if mc_version: query = query.filter_by(mc_version=mc_version)
    if sort == 'popular': query = query.order_by(Mod.downloads.desc())
    elif sort == 'top': query = query.outerjoin(Like).group_by(Mod.id).order_by(func.count(Like.id).desc())
    elif sort == 'views': query = query.order_by(Mod.views.desc())
    else: query = query.order_by(Mod.created_at.desc())
    mods = query.all()
    top_mods = Mod.query.order_by(Mod.downloads.desc()).limit(3).all() if not search and not category and not mc_version else []
    latest_news = News.query.order_by(News.created_at.desc()).limit(3).all()
    categories = ['Магия', 'Техника', 'Оружие', 'Мобы', 'Декор', 'Еда', 'Миры', 'Утилиты', 'Другое']
    versions = ['1.21.4', '1.21.3', '1.21.1', '1.21', '1.20.6', '1.20.4', '1.20.2', '1.20.1', '1.19.4', '1.19.2', '1.18.2', '1.17.1', '1.16.5', '1.12.2', '1.8.9', '1.7.10']
    content_types_list = [
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
                           content_type=content_type, content_types_list=content_types_list)

@app.route('/news')
def news_list():
    news = News.query.order_by(News.created_at.desc()).all()
    return render_template('news.html', news=news)

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

@app.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(50).all()
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('notifications.html', notifs=notifs)

@app.route('/messages')
@login_required
def messages():
    sent = db.session.query(Message.to_user_id).filter_by(from_user_id=current_user.id).distinct()
    received = db.session.query(Message.from_user_id).filter_by(to_user_id=current_user.id).distinct()
    user_ids = set([r[0] for r in sent.all()] + [r[0] for r in received.all()])
    chats = []
    for uid in user_ids:
        user = User.query.get(uid)
        if not user: continue
        last_msg = Message.query.filter(or_(
            and_(Message.from_user_id == current_user.id, Message.to_user_id == uid),
            and_(Message.from_user_id == uid, Message.to_user_id == current_user.id)
        )).order_by(Message.created_at.desc()).first()
        unread = Message.query.filter_by(from_user_id=uid, to_user_id=current_user.id, is_read=False).count()
        chats.append({'user': user, 'last': last_msg, 'unread': unread})
    chats.sort(key=lambda x: x['last'].created_at if x['last'] else datetime.min, reverse=True)
    return render_template('messages.html', chats=chats)

@app.route('/messages/<username>', methods=['GET', 'POST'])
@login_required
def chat(username):
    other = User.query.filter_by(username=username).first_or_404()
    if other.id == current_user.id:
        flash('Нельзя писать самому себе', 'error')
        return redirect(url_for('messages'))
    if request.method == 'POST':
        text_msg = request.form.get('text', '').strip()
        if text_msg:
            msg = Message(from_user_id=current_user.id, to_user_id=other.id, text=text_msg[:2000])
            db.session.add(msg)
            notify(other.id, 'message', f'{current_user.username} написал сообщение',
                   url_for('chat', username=current_user.username), current_user.id)
            db.session.commit()
        return redirect(url_for('chat', username=username))
    Message.query.filter_by(from_user_id=other.id, to_user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    msgs = Message.query.filter(or_(
        and_(Message.from_user_id == current_user.id, Message.to_user_id == other.id),
        and_(Message.from_user_id == other.id, Message.to_user_id == current_user.id)
    )).order_by(Message.created_at).all()
    return render_template('chat.html', other=other, msgs=msgs)

@app.route('/activity/<username>')
def activity(username):
    user = User.query.filter_by(username=username).first_or_404()
    acts = Activity.query.filter_by(user_id=user.id).order_by(Activity.created_at.desc()).limit(50).all()
    return render_template('activity.html', user=user, acts=acts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Имя пользователя занято', 'error'); return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email уже используется', 'error'); return redirect(url_for('register'))
        user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(user); db.session.commit()
        login_user(user)
        flash('Регистрация успешна!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            if user.is_banned and user.username != ADMIN_USERNAME:
                flash('Ваш аккаунт заблокирован', 'error')
                return redirect(url_for('login'))
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
@app.route('/upload/<content_type>', methods=['GET', 'POST'])
@login_required
def upload(content_type='mod'):
    valid_types = ['mod', 'shader', 'plugin', 'resourcepack', 'modpack', 'datapack', 'map']
    if content_type not in valid_types:
        content_type = 'mod'
    categories = ['Магия', 'Техника', 'Оружие', 'Мобы', 'Декор', 'Еда', 'Миры', 'Утилиты', 'Другое']
    versions = ['1.21.4', '1.21.3', '1.21.1', '1.21', '1.20.6', '1.20.4', '1.20.2', '1.20.1', '1.19.4', '1.19.2', '1.18.2', '1.17.1', '1.16.5', '1.12.2', '1.8.9', '1.7.10']
    if request.method == 'POST':
        file = request.files.get('mod_file')
        if not file or not allowed_file(file.filename, content_type):
            flash(f'Неверный формат файла для типа: {content_type}', 'error')
            return redirect(url_for('upload', content_type=content_type))
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
            title=request.form['title'], description=request.form['description'],
            version=request.form['version'], mc_version=request.form['mc_version'],
            category=request.form['category'], tags=request.form.get('tags', ''),
            screenshots=','.join(screenshots), filename=unique_name, user_id=current_user.id,
            content_type=content_type
        )
        db.session.add(mod); db.session.flush()
        log_activity(current_user.id, 'uploaded', f'Опубликовал мод "{mod.title}"', url_for('mod_page', mod_id=mod.id))
        subs = Subscription.query.filter_by(author_id=current_user.id).all()
        for s in subs:
            notify(s.follower_id, 'new_mod', f'{current_user.username} опубликовал новый мод: {mod.title}',
                   url_for('mod_page', mod_id=mod.id), current_user.id)
        db.session.commit()
        flash('Мод успешно опубликован!', 'success')
        return redirect(url_for('mod_page', mod_id=mod.id))
    content_types = [
        ('mod', 'Мод', '⛏', '.jar'),
        ('shader', 'Шейдер', '🌅', '.zip'),
        ('plugin', 'Плагин', '🔌', '.jar'),
        ('resourcepack', 'Ресурспак', '🎨', '.zip'),
        ('modpack', 'Сборка', '📦', '.zip / .mrpack'),
        ('datapack', 'Датапак', '📝', '.zip'),
        ('map', 'Карта', '🗺️', '.zip'),
    ]
    return render_template('upload.html', categories=categories, versions=versions,
                          content_type=content_type, content_types=content_types)

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
    txt = request.form.get('text', '').strip()
    if not txt or len(txt) > 1000:
        flash('Неверный комментарий', 'error')
        return redirect(url_for('mod_page', mod_id=mod_id))
    comment = Comment(text=txt, user_id=current_user.id, mod_id=mod_id)
    db.session.add(comment)
    log_activity(current_user.id, 'commented', f'Прокомментировал "{mod.title}"', url_for('mod_page', mod_id=mod_id))
    notify(mod.user_id, 'comment', f'{current_user.username} прокомментировал ваш мод "{mod.title}"',
           url_for('mod_page', mod_id=mod_id), current_user.id)
    db.session.commit()
    return redirect(url_for('mod_page', mod_id=mod_id) + '#comments')

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    mod_id = comment.mod_id
    if comment.user_id != current_user.id and comment.mod.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    db.session.delete(comment); db.session.commit()
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
        db.session.delete(existing); subscribed = False
    else:
        sub = Subscription(follower_id=current_user.id, author_id=user_id)
        db.session.add(sub)
        log_activity(current_user.id, 'subscribed', f'Подписался на {author.username}', url_for('user_page', username=author.username))
        notify(user_id, 'subscribe', f'{current_user.username} подписался на вас',
               url_for('user_page', username=current_user.username), current_user.id)
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
        db.session.delete(existing); liked = False
    else:
        like = Like(user_id=current_user.id, mod_id=mod_id)
        db.session.add(like)
        log_activity(current_user.id, 'liked', f'Лайкнул "{mod.title}"', url_for('mod_page', mod_id=mod_id))
        notify(mod.user_id, 'like', f'{current_user.username} лайкнул ваш мод "{mod.title}"',
               url_for('mod_page', mod_id=mod_id), current_user.id)
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
            db.session.commit(); flash('Тема изменена!', 'success')
        elif action == 'animations':
            current_user.animations = 'animations' in request.form
            db.session.commit(); flash('Настройки сохранены!', 'success')
        elif action == 'profile':
            current_user.bio = request.form.get('bio', '')[:300]
            new_email = request.form.get('email', '').strip()
            if new_email and new_email != current_user.email:
                if User.query.filter_by(email=new_email).first():
                    flash('Этот email уже занят', 'error')
                else:
                    current_user.email = new_email
            db.session.commit(); flash('Профиль обновлён!', 'success')
        elif action == 'avatar':
            avatar = request.files.get('avatar')
            if avatar and avatar.filename and allowed_image(avatar.filename):
                ext = avatar.filename.rsplit('.', 1)[-1].lower()
                if current_user.avatar:
                    old = os.path.join(app.config['AVATARS_FOLDER'], current_user.avatar)
                    if os.path.exists(old): os.remove(old)
                av_name = f"{current_user.id}_{int(datetime.utcnow().timestamp())}.{ext}"
                avatar.save(os.path.join(app.config['AVATARS_FOLDER'], av_name))
                current_user.avatar = av_name
                db.session.commit(); flash('Аватарка обновлена!', 'success')
            else: flash('Выбери картинку', 'error')
        elif action == 'password':
            old = request.form.get('old_password'); new = request.form.get('new_password')
            if not check_password_hash(current_user.password, old):
                flash('Неверный пароль', 'error')
            elif len(new) < 6:
                flash('Пароль должен быть от 6 символов', 'error')
            else:
                current_user.password = generate_password_hash(new)
                db.session.commit(); flash('Пароль изменён!', 'success')
        return redirect(url_for('settings'))
    return render_template('settings.html')

@app.route('/delete/<int:mod_id>', methods=['POST'])
@login_required
def delete_mod(mod_id):
    mod = Mod.query.get_or_404(mod_id)
    if mod.user_id != current_user.id and not current_user.is_admin:
        return redirect(url_for('index'))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], mod.filename)
    if os.path.exists(filepath): os.remove(filepath)
    for ss in mod.screenshots_list:
        ss_path = os.path.join(app.config['SCREENSHOTS_FOLDER'], ss)
        if os.path.exists(ss_path): os.remove(ss_path)
    db.session.delete(mod); db.session.commit()
    flash('Мод удалён', 'success')
    return redirect(url_for('profile'))

# ===== АДМИН =====
@app.route('/admin')
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_mods = Mod.query.count()
    total_downloads = db.session.query(func.sum(Mod.downloads)).scalar() or 0
    total_likes = Like.query.count()
    total_comments = Comment.query.count()
    total_views = db.session.query(func.sum(Mod.views)).scalar() or 0

    # За последние 7 дней
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = User.query.filter(User.created_at >= week_ago).count()
    new_mods_week = Mod.query.filter(Mod.created_at >= week_ago).count()

    # График активности (последние 7 дней)
    chart_data = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day)
        day_end = day_start + timedelta(days=1)
        cnt = Mod.query.filter(Mod.created_at >= day_start, Mod.created_at < day_end).count()
        chart_data.append({'day': day.strftime('%d.%m'), 'count': cnt})

    # Топ юзеров
    top_authors = User.query.outerjoin(Mod).group_by(User.id).order_by(func.count(Mod.id).desc()).limit(5).all()

    return render_template('admin/dashboard.html',
        total_users=total_users, total_mods=total_mods, total_downloads=total_downloads,
        total_likes=total_likes, total_comments=total_comments, total_views=total_views,
        new_users_week=new_users_week, new_mods_week=new_mods_week,
        chart_data=chart_data, top_authors=top_authors)

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/mods')
@admin_required
def admin_mods():
    mods = Mod.query.order_by(Mod.created_at.desc()).all()
    return render_template('admin/mods.html', mods=mods)

@app.route('/admin/user/<int:user_id>/ban', methods=['POST'])
@admin_required
def admin_ban_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == ADMIN_USERNAME:
        flash('Нельзя забанить админа', 'error')
        return redirect(url_for('admin_users'))
    user.is_banned = not user.is_banned
    db.session.commit()
    flash(f'{"Забанен" if user.is_banned else "Разбанен"}: {user.username}', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == ADMIN_USERNAME:
        flash('Нельзя удалить админа', 'error')
        return redirect(url_for('admin_users'))
    # Удаляем все его моды и файлы
    for mod in user.mods:
        fp = os.path.join(app.config['UPLOAD_FOLDER'], mod.filename)
        if os.path.exists(fp): os.remove(fp)
        for ss in mod.screenshots_list:
            sp = os.path.join(app.config['SCREENSHOTS_FOLDER'], ss)
            if os.path.exists(sp): os.remove(sp)
        db.session.delete(mod)
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь удалён', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/mod/<int:mod_id>/delete', methods=['POST'])
@admin_required
def admin_delete_mod(mod_id):
    mod = Mod.query.get_or_404(mod_id)
    fp = os.path.join(app.config['UPLOAD_FOLDER'], mod.filename)
    if os.path.exists(fp): os.remove(fp)
    for ss in mod.screenshots_list:
        sp = os.path.join(app.config['SCREENSHOTS_FOLDER'], ss)
        if os.path.exists(sp): os.remove(sp)
    db.session.delete(mod); db.session.commit()
    flash('Мод удалён', 'success')
    return redirect(url_for('admin_mods'))

@app.route('/admin/news', methods=['GET', 'POST'])
@admin_required
def admin_news():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if title and content:
            n = News(title=title, content=content)
            db.session.add(n); db.session.commit()
            flash('Новость опубликована!', 'success')
        return redirect(url_for('admin_news'))
    news = News.query.order_by(News.created_at.desc()).all()
    return render_template('admin/news.html', news=news)

@app.route('/admin/news/<int:news_id>/delete', methods=['POST'])
@admin_required
def admin_delete_news(news_id):
    n = News.query.get_or_404(news_id)
    db.session.delete(n); db.session.commit()
    flash('Новость удалена', 'success')
    return redirect(url_for('admin_news'))



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
        if _re_versions.match(r'^1\.\d+(\.\d+)?$', str(v)):
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


# ===== MODRINTH API =====
MODRINTH_API = "https://api.modrinth.com/v2"
MODRINTH_HEADERS = {"User-Agent": "MineMods/1.0 (contact@minemods.local)"}

@app.route('/modrinth')
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

    facets = [[f"project_type:{project_type}"]]
    if mc_version:
        facets.append([f"versions:{mc_version}"])
    if category:
        facets.append([f"categories:{category}"])

    params = {
        'query': query,
        'facets': str(facets).replace("'", '"'),
        'limit': limit,
        'offset': offset,
        'index': sort,
    }

    try:
        r = requests.get(f"{MODRINTH_API}/search", params=params, headers=MODRINTH_HEADERS, timeout=10)
        data = r.json()
        results = data.get('hits', [])
        total = data.get('total_hits', 0)
    except Exception as e:
        results = []
        total = 0
        flash(f'Ошибка соединения с Modrinth: {str(e)}', 'error')

    # Категории Modrinth
    mr_categories = [
        ('adventure', 'Приключения 🗺️'),
        ('cursed', 'Проклятые 👻'),
        ('decoration', 'Декор 🪴'),
        ('economy', 'Экономика 💰'),
        ('equipment', 'Снаряжение ⚔️'),
        ('food', 'Еда 🍖'),
        ('game-mechanics', 'Механики 🎮'),
        ('library', 'Библиотеки 📚'),
        ('magic', 'Магия ✨'),
        ('management', 'Менеджмент 📊'),
        ('minigame', 'Мини-игры 🎯'),
        ('mobs', 'Мобы 🐺'),
        ('optimization', 'Оптимизация ⚡'),
        ('social', 'Социальные 💬'),
        ('storage', 'Хранение 📦'),
        ('technology', 'Технологии ⚙️'),
        ('transportation', 'Транспорт 🚗'),
        ('utility', 'Утилиты 🔧'),
        ('worldgen', 'Генерация миров 🌍'),
    ]

    versions = ['1.21.4', '1.21.3', '1.21.1', '1.21', '1.20.6', '1.20.4', '1.20.2', '1.20.1',
                '1.19.4', '1.19.2', '1.18.2', '1.17.1', '1.16.5', '1.12.2', '1.8.9', '1.7.10']

    total_pages = (total + limit - 1) // limit if total else 1

    content_types = [
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
        project_type=project_type, content_types=content_types)

@app.route('/modrinth/project/<slug>')
def modrinth_project(slug):
    try:
        # Информация о проекте
        r = requests.get(f"{MODRINTH_API}/project/{slug}", headers=MODRINTH_HEADERS, timeout=10)
        if r.status_code != 200:
            flash('Мод не найден на Modrinth', 'error')
            return redirect(url_for('modrinth_search'))
        project = r.json()

        # Версии мода
        v = requests.get(f"{MODRINTH_API}/project/{slug}/version", headers=MODRINTH_HEADERS, timeout=10)
        versions_list = v.json() if v.status_code == 200 else []

    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return redirect(url_for('modrinth_search'))

    return render_template('modrinth_project.html', project=project, versions=versions_list)

@app.route('/modrinth/download')
def modrinth_download():
    """Редирект на скачивание с Modrinth"""
    file_url = request.args.get('url', '')
    if not file_url.startswith('https://cdn.modrinth.com'):
        abort(400)
    return redirect(file_url)


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

with app.app_context():
    db.create_all()
    try:
        with db.engine.connect() as conn:
            for sql in [
                "ALTER TABLE user ADD COLUMN theme VARCHAR(20) DEFAULT 'green'",
                "ALTER TABLE user ADD COLUMN animations BOOLEAN DEFAULT 1",
                "ALTER TABLE user ADD COLUMN bio VARCHAR(300) DEFAULT ''",
                "ALTER TABLE user ADD COLUMN avatar VARCHAR(300) DEFAULT ''",
                "ALTER TABLE user ADD COLUMN is_banned BOOLEAN DEFAULT 0",
                "ALTER TABLE mod ADD COLUMN views INTEGER DEFAULT 0",
                "ALTER TABLE mod ADD COLUMN tags VARCHAR(300) DEFAULT ''",
                "ALTER TABLE mod ADD COLUMN screenshots TEXT DEFAULT ''",
                "ALTER TABLE mod ADD COLUMN content_type VARCHAR(30) DEFAULT 'mod'",
            ]:
                try: conn.execute(text(sql))
                except: pass
            conn.commit()
    except Exception as e:
        print(f"Migration: {e}")

if __name__ == '__main__':
    app.run(debug=True)
