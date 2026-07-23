# -*- coding: utf-8 -*-
import os

print("🚀 Этап 5 — Админка, Статистика, Новости, Топбар...")

ADMIN_USERNAME = 'nehea664'  # ← ТЫ АДМИН

# ============= APP.PY =============
app_py = f'''# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import func, or_, and_, text
from functools import wraps

ADMIN_USERNAME = '{ADMIN_USERNAME}'

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
'''

# Дальше идёт обычный код с моделями и роутами
app_py += '''
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

def allowed_file(filename):
    return filename.lower().endswith('.jar')

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
    query = Mod.query
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
    versions = ['1.21', '1.20.4', '1.20.2', '1.20.1', '1.19.4', '1.19.2', '1.18.2', '1.16.5', '1.12.2']
    return render_template('index.html', mods=mods, top_mods=top_mods, latest_news=latest_news,
                           categories=categories, versions=versions, search=search,
                           sel_category=category, sel_version=mc_version, sort=sort)

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
            title=request.form['title'], description=request.form['description'],
            version=request.form['version'], mc_version=request.form['mc_version'],
            category=request.form['category'], tags=request.form.get('tags', ''),
            screenshots=','.join(screenshots), filename=unique_name, user_id=current_user.id
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
            ]:
                try: conn.execute(text(sql))
                except: pass
            conn.commit()
    except Exception as e:
        print(f"Migration: {e}")

if __name__ == '__main__':
    app.run(debug=True)
'''

# ============= BASE.HTML (с топбаром!) =============
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
            <a href="{{ url_for('news_list') }}" class="nav-item">
                <span class="nav-icon">📰</span><span>Новости</span>
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
            <a href="{{ url_for('achievements') }}" class="nav-item">
                <span class="nav-icon">🏅</span><span>Достижения</span>
            </a>
            {% if is_admin %}
            <div class="nav-divider">АДМИН</div>
            <a href="{{ url_for('admin_dashboard') }}" class="nav-item admin-item">
                <span class="nav-icon">📊</span><span>Статистика</span>
            </a>
            <a href="{{ url_for('admin_users') }}" class="nav-item admin-item">
                <span class="nav-icon">👥</span><span>Пользователи</span>
            </a>
            <a href="{{ url_for('admin_mods') }}" class="nav-item admin-item">
                <span class="nav-icon">📦</span><span>Все моды</span>
            </a>
            <a href="{{ url_for('admin_news') }}" class="nav-item admin-item">
                <span class="nav-icon">📰</span><span>Новости</span>
            </a>
            {% endif %}
            {% endif %}
        </nav>
    </aside>

    <main class="main-content">
        <header class="topbar">
            <button class="mobile-menu-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">☰</button>

            <div class="topbar-right">
                {% if current_user.is_authenticated %}
                    <a href="{{ url_for('notifications') }}" class="topbar-icon" title="Уведомления">
                        🔔
                        {% if unread_notif > 0 %}<span class="topbar-badge">{{ unread_notif }}</span>{% endif %}
                    </a>
                    <a href="{{ url_for('messages') }}" class="topbar-icon" title="Сообщения">
                        💌
                        {% if unread_msg > 0 %}<span class="topbar-badge">{{ unread_msg }}</span>{% endif %}
                    </a>

                    <div class="user-menu">
                        <button class="user-menu-btn" onclick="document.querySelector('.user-dropdown').classList.toggle('open')">
                            {% if current_user.avatar %}
                                <img src="{{ url_for('static', filename='avatars/' + current_user.avatar) }}" class="topbar-avatar" alt="avatar">
                            {% else %}
                                <div class="topbar-avatar-letter">{{ current_user.username[0]|upper }}</div>
                            {% endif %}
                            <span class="user-menu-name">{{ current_user.username }}{% if is_admin %} 👑{% endif %}</span>
                            <span class="dropdown-arrow">▼</span>
                        </button>
                        <div class="user-dropdown">
                            <a href="{{ url_for('profile') }}" class="dropdown-item">
                                <span>👤</span> Профиль
                            </a>
                            <a href="{{ url_for('settings') }}" class="dropdown-item">
                                <span>⚙️</span> Настройки
                            </a>
                            <a href="{{ url_for('activity', username=current_user.username) }}" class="dropdown-item">
                                <span>📅</span> Активность
                            </a>
                            {% if is_admin %}
                            <a href="{{ url_for('admin_dashboard') }}" class="dropdown-item">
                                <span>👑</span> Админ-панель
                            </a>
                            {% endif %}
                            <div class="dropdown-divider"></div>
                            <a href="{{ url_for('logout') }}" class="dropdown-item logout">
                                <span>🚪</span> Выйти
                            </a>
                        </div>
                    </div>
                {% else %}
                    <a href="{{ url_for('login') }}" class="topbar-btn">Войти</a>
                    <a href="{{ url_for('register') }}" class="topbar-btn topbar-btn-primary">Регистрация</a>
                {% endif %}
            </div>
        </header>

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
    const dropdown = document.querySelector('.user-dropdown');
    const menuBtn = document.querySelector('.user-menu-btn');
    if (dropdown && dropdown.classList.contains('open') && !dropdown.contains(e.target) && !menuBtn.contains(e.target)) {
        dropdown.classList.remove('open');
    }
});
</script>
</body>
</html>'''

# ============= INDEX.HTML с новостями =============
index_html = '''{% extends 'base.html' %}
{% block content %}

{% if latest_news %}
<div class="news-banner">
    <h3>📰 Последние новости</h3>
    <div class="news-strip">
        {% for n in latest_news %}
        <a href="{{ url_for('news_list') }}" class="news-pill">
            <strong>{{ n.title }}</strong>
            <span>{{ n.created_at.strftime('%d.%m') }}</span>
        </a>
        {% endfor %}
        <a href="{{ url_for('news_list') }}" class="news-all">Все →</a>
    </div>
</div>
{% endif %}

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
            {% for tag in mod.tags_list[:3] %}<span class="tag">#{{ tag }}</span>{% endfor %}
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
        </div>
    {% endfor %}
</div>
{% endblock %}'''

# ============= NEWS.HTML =============
news_html = '''{% extends 'base.html' %}
{% block content %}
<div class="page-header">
    <div>
        <h1 class="page-title">📰 Новости</h1>
        <p class="page-subtitle">Что нового на MineMods</p>
    </div>
</div>

<div class="news-list">
    {% for n in news %}
    <article class="news-item">
        <div class="news-date">{{ n.created_at.strftime('%d.%m.%Y %H:%M') }}</div>
        <h2>{{ n.title }}</h2>
        <div class="news-content">{{ n.content }}</div>
    </article>
    {% else %}
    <div class="empty-state">
        <div class="empty-icon">📰</div>
        <h3>Новостей пока нет</h3>
    </div>
    {% endfor %}
</div>
{% endblock %}'''

# ============= ADMIN DASHBOARD =============
admin_dashboard_html = '''{% extends 'base.html' %}
{% block content %}
<div class="page-header">
    <div>
        <h1 class="page-title">👑 Админ-панель</h1>
        <p class="page-subtitle">Статистика сайта</p>
    </div>
</div>

<div class="admin-stats">
    <div class="admin-stat-card">
        <div class="as-icon">👥</div>
        <div class="as-num">{{ total_users }}</div>
        <div class="as-label">Пользователей</div>
        <div class="as-extra">+{{ new_users_week }} за неделю</div>
    </div>
    <div class="admin-stat-card">
        <div class="as-icon">📦</div>
        <div class="as-num">{{ total_mods }}</div>
        <div class="as-label">Модов</div>
        <div class="as-extra">+{{ new_mods_week }} за неделю</div>
    </div>
    <div class="admin-stat-card">
        <div class="as-icon">⬇️</div>
        <div class="as-num">{{ total_downloads }}</div>
        <div class="as-label">Скачиваний</div>
    </div>
    <div class="admin-stat-card">
        <div class="as-icon">❤️</div>
        <div class="as-num">{{ total_likes }}</div>
        <div class="as-label">Лайков</div>
    </div>
    <div class="admin-stat-card">
        <div class="as-icon">💬</div>
        <div class="as-num">{{ total_comments }}</div>
        <div class="as-label">Комментариев</div>
    </div>
    <div class="admin-stat-card">
        <div class="as-icon">👁️</div>
        <div class="as-num">{{ total_views }}</div>
        <div class="as-label">Просмотров</div>
    </div>
</div>

<div class="admin-grid">
    <div class="admin-block">
        <h3>📈 Новые моды за неделю</h3>
        <div class="chart">
            {% set max_count = chart_data | map(attribute='count') | max %}
            {% for d in chart_data %}
            <div class="chart-bar">
                <div class="bar-value">{{ d.count }}</div>
                <div class="bar" style="height: {{ (d.count / max_count * 100) if max_count > 0 else 0 }}%"></div>
                <div class="bar-label">{{ d.day }}</div>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="admin-block">
        <h3>🏆 Топ авторов</h3>
        <div class="top-authors">
            {% for author in top_authors %}
            <a href="{{ url_for('user_page', username=author.username) }}" class="top-author">
                <span class="ta-rank">#{{ loop.index }}</span>
                {% if author.avatar %}
                    <img src="{{ url_for('static', filename='avatars/' + author.avatar) }}" class="ta-avatar">
                {% else %}
                    <div class="ta-avatar-letter">{{ author.username[0]|upper }}</div>
                {% endif %}
                <div class="ta-info">
                    <div class="ta-name">{{ author.username }}</div>
                    <div class="ta-mods">{{ author.mods|length }} модов</div>
                </div>
            </a>
            {% endfor %}
        </div>
    </div>
</div>

<div class="admin-actions">
    <a href="{{ url_for('admin_users') }}" class="admin-action-btn">
        <span>👥</span> Управление пользователями
    </a>
    <a href="{{ url_for('admin_mods') }}" class="admin-action-btn">
        <span>📦</span> Все моды
    </a>
    <a href="{{ url_for('admin_news') }}" class="admin-action-btn">
        <span>📰</span> Управление новостями
    </a>
</div>
{% endblock %}'''

# ============= ADMIN USERS =============
admin_users_html = '''{% extends 'base.html' %}
{% block content %}
<div class="page-header">
    <div>
        <h1 class="page-title">👥 Пользователи ({{ users|length }})</h1>
    </div>
</div>

<div class="admin-table-wrap">
    <table class="admin-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Юзер</th>
                <th>Email</th>
                <th>Моды</th>
                <th>Дата</th>
                <th>Статус</th>
                <th>Действия</th>
            </tr>
        </thead>
        <tbody>
            {% for u in users %}
            <tr class="{% if u.is_banned %}banned-row{% endif %}">
                <td>{{ u.id }}</td>
                <td>
                    <a href="{{ url_for('user_page', username=u.username) }}" class="author-link">
                        {{ u.username }}{% if u.username == 'nehea664' %} 👑{% endif %}
                    </a>
                </td>
                <td>{{ u.email }}</td>
                <td>{{ u.mods|length }}</td>
                <td>{{ u.created_at.strftime('%d.%m.%Y') }}</td>
                <td>
                    {% if u.is_banned %}
                        <span class="status-banned">🚫 Бан</span>
                    {% else %}
                        <span class="status-active">✓ Активен</span>
                    {% endif %}
                </td>
                <td>
                    {% if u.username != 'nehea664' %}
                    <form method="POST" action="{{ url_for('admin_ban_user', user_id=u.id) }}" style="display:inline">
                        <button type="submit" class="admin-btn">
                            {% if u.is_banned %}✓ Разбан{% else %}🚫 Бан{% endif %}
                        </button>
                    </form>
                    <form method="POST" action="{{ url_for('admin_delete_user', user_id=u.id) }}" style="display:inline">
                        <button type="submit" class="admin-btn danger" onclick="return confirm('Удалить пользователя и все его моды?')">🗑</button>
                    </form>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}'''

# ============= ADMIN MODS =============
admin_mods_html = '''{% extends 'base.html' %}
{% block content %}
<div class="page-header">
    <div>
        <h1 class="page-title">📦 Все моды ({{ mods|length }})</h1>
    </div>
</div>

<div class="admin-table-wrap">
    <table class="admin-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Название</th>
                <th>Автор</th>
                <th>Категория</th>
                <th>MC</th>
                <th>⬇</th>
                <th>❤</th>
                <th>👁</th>
                <th>Дата</th>
                <th>Действия</th>
            </tr>
        </thead>
        <tbody>
            {% for m in mods %}
            <tr>
                <td>{{ m.id }}</td>
                <td><a href="{{ url_for('mod_page', mod_id=m.id) }}" class="author-link">{{ m.title }}</a></td>
                <td><a href="{{ url_for('user_page', username=m.author.username) }}" class="author-link">{{ m.author.username }}</a></td>
                <td>{{ m.category }}</td>
                <td>{{ m.mc_version }}</td>
                <td>{{ m.downloads }}</td>
                <td>{{ m.likes_count }}</td>
                <td>{{ m.views or 0 }}</td>
                <td>{{ m.created_at.strftime('%d.%m.%Y') }}</td>
                <td>
                    <form method="POST" action="{{ url_for('admin_delete_mod', mod_id=m.id) }}" style="display:inline">
                        <button type="submit" class="admin-btn danger" onclick="return confirm('Удалить мод?')">🗑</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}'''

# ============= ADMIN NEWS =============
admin_news_html = '''{% extends 'base.html' %}
{% block content %}
<div class="page-header">
    <div>
        <h1 class="page-title">📰 Новости</h1>
    </div>
</div>

<div class="settings-card">
    <h3>➕ Новая новость</h3>
    <form method="POST">
        <label>Заголовок</label>
        <input type="text" name="title" required maxlength="200">
        <label>Текст</label>
        <textarea name="content" rows="6" required></textarea>
        <button type="submit" class="btn-save">📢 Опубликовать</button>
    </form>
</div>

<h3 class="section-title">Все новости</h3>

<div class="news-list">
    {% for n in news %}
    <article class="news-item">
        <div class="news-date">{{ n.created_at.strftime('%d.%m.%Y %H:%M') }}</div>
        <h2>{{ n.title }}</h2>
        <div class="news-content">{{ n.content }}</div>
        <form method="POST" action="{{ url_for('admin_delete_news', news_id=n.id) }}" style="margin-top:10px;">
            <button type="submit" class="admin-btn danger" onclick="return confirm('Удалить?')">🗑 Удалить</button>
        </form>
    </article>
    {% endfor %}
</div>
{% endblock %}'''

# ============= ДОБАВЛЯЕМ CSS =============
extra_css = '''

/* ===== TOPBAR ===== */
.topbar {
    height: 64px;
    background: rgba(20, 27, 45, 0.7);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
    padding: 0 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 90;
}

[data-theme="light"] .topbar {
    background: rgba(255, 255, 255, 0.85);
}

.topbar-right {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-left: auto;
}

.topbar-icon {
    position: relative;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-card);
    border-radius: 50%;
    text-decoration: none;
    font-size: 18px;
    transition: all 0.2s;
    border: 1px solid var(--border);
}

.topbar-icon:hover {
    transform: translateY(-2px);
    border-color: var(--accent);
}

.topbar-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    background: #ff4757;
    color: white;
    border-radius: 10px;
    padding: 1px 6px;
    font-size: 10px;
    font-weight: 800;
    min-width: 18px;
    text-align: center;
    border: 2px solid var(--bg-main);
}

.topbar-btn {
    padding: 8px 18px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    text-decoration: none;
    color: var(--text-main);
    font-weight: 600;
    transition: all 0.2s;
}

.topbar-btn:hover { border-color: var(--accent); }

.topbar-btn-primary {
    background: var(--gradient);
    color: #0f1626;
    border: none;
}

/* ===== USER MENU ===== */
.user-menu { position: relative; }

.user-menu-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 4px 14px 4px 4px;
    border-radius: 30px;
    cursor: pointer;
    color: var(--text-main);
    transition: all 0.2s;
}

.user-menu-btn:hover {
    border-color: var(--accent);
}

.topbar-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
}

.topbar-avatar-letter {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--gradient);
    color: #0f1626;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 14px;
}

.user-menu-name {
    font-weight: 600;
    font-size: 14px;
}

.dropdown-arrow {
    font-size: 9px;
    opacity: 0.6;
}

.user-dropdown {
    position: absolute;
    top: calc(100% + 8px);
    right: 0;
    background: var(--bg-sidebar);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 12px;
    min-width: 200px;
    padding: 8px;
    opacity: 0;
    pointer-events: none;
    transform: translateY(-10px);
    transition: all 0.2s;
    z-index: 100;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.user-dropdown.open {
    opacity: 1;
    pointer-events: all;
    transform: translateY(0);
}

.dropdown-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    text-decoration: none;
    color: var(--text-main);
    font-size: 14px;
    font-weight: 500;
    transition: background 0.2s;
}

.dropdown-item:hover {
    background: rgba(255,255,255,0.05);
}

.dropdown-item.logout:hover {
    background: rgba(255, 100, 100, 0.1);
    color: #ff7777;
}

.dropdown-divider {
    height: 1px;
    background: var(--border);
    margin: 6px 0;
}

/* Скрываем старый user-card в сайдбаре */
.sidebar-footer { display: none; }
.sidebar {
    padding-bottom: 16px;
}

/* ===== ADMIN ===== */
.nav-divider {
    padding: 16px 14px 4px;
    font-size: 11px;
    color: var(--text-muted);
    font-weight: 800;
    letter-spacing: 1px;
}

.admin-item {
    color: #ffa726 !important;
}

.admin-item:hover {
    background: rgba(255, 167, 38, 0.1) !important;
    color: #ffa726 !important;
}

.admin-stats {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 14px;
    margin-bottom: 24px;
}

.admin-stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 20px;
    border-radius: 14px;
    text-align: center;
    transition: all 0.2s;
}

.admin-stat-card:hover {
    transform: translateY(-4px);
    border-color: var(--accent);
}

.as-icon { font-size: 32px; margin-bottom: 8px; }
.as-num { font-size: 28px; font-weight: 800; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.as-label { color: var(--text-muted); font-size: 13px; margin-top: 4px; }
.as-extra { font-size: 11px; color: var(--accent); margin-top: 6px; font-weight: 600; }

.admin-grid {
    display: grid;
    grid-template-columns: 1.5fr 1fr;
    gap: 20px;
    margin-bottom: 24px;
}

.admin-block {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 24px;
    border-radius: 16px;
}

.admin-block h3 {
    margin-bottom: 20px;
    color: var(--accent);
}

/* Chart */
.chart {
    display: flex;
    align-items: flex-end;
    justify-content: space-around;
    height: 200px;
    gap: 12px;
}

.chart-bar {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 100%;
    justify-content: flex-end;
}

.bar {
    width: 100%;
    background: var(--gradient);
    border-radius: 8px 8px 0 0;
    min-height: 4px;
    transition: all 0.5s ease-out;
}

.bar-value {
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 6px;
    color: var(--accent);
}

.bar-label {
    margin-top: 8px;
    font-size: 11px;
    color: var(--text-muted);
    font-weight: 600;
}

/* Top authors */
.top-authors {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.top-author {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px;
    border-radius: 10px;
    text-decoration: none;
    color: inherit;
    transition: all 0.2s;
}

.top-author:hover {
    background: rgba(255,255,255,0.05);
    transform: translateX(5px);
}

.ta-rank {
    font-weight: 800;
    color: var(--accent);
    min-width: 30px;
}

.ta-avatar, .ta-avatar-letter {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    object-fit: cover;
}

.ta-avatar-letter {
    background: var(--gradient);
    color: #0f1626;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
}

.ta-info { flex: 1; }
.ta-name { font-weight: 600; font-size: 14px; }
.ta-mods { font-size: 12px; color: var(--text-muted); }

.admin-actions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
}

.admin-action-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    text-decoration: none;
    color: var(--text-main);
    font-weight: 600;
    transition: all 0.2s;
}

.admin-action-btn:hover {
    border-color: #ffa726;
    transform: translateY(-2px);
}

.admin-action-btn span {
    font-size: 24px;
}

/* Admin table */
.admin-table-wrap {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow-x: auto;
}

.admin-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

.admin-table th {
    background: var(--bg-main);
    padding: 12px;
    text-align: left;
    color: var(--text-muted);
    font-weight: 700;
    font-size: 12px;
    text-transform: uppercase;
}

.admin-table td {
    padding: 12px;
    border-top: 1px solid var(--border);
}

.admin-table tr:hover {
    background: rgba(255,255,255,0.02);
}

.banned-row {
    opacity: 0.5;
}

.status-active {
    color: #4ade80;
    font-weight: 600;
}

.status-banned {
    color: #ff7777;
    font-weight: 600;
}

.admin-btn {
    background: var(--bg-main);
    border: 1px solid var(--border);
    color: var(--text-main);
    padding: 6px 12px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 12px;
    font-weight: 600;
    margin: 2px;
    transition: all 0.2s;
}

.admin-btn:hover { border-color: var(--accent); }

.admin-btn.danger {
    color: #ff7777;
    border-color: rgba(255, 100, 100, 0.3);
}

.admin-btn.danger:hover {
    background: rgba(255, 100, 100, 0.1);
}

/* News */
.news-banner {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 16px 20px;
    border-radius: 14px;
    margin-bottom: 24px;
}

.news-banner h3 {
    margin-bottom: 12px;
    color: var(--accent);
    font-size: 16px;
}

.news-strip {
    display: flex;
    gap: 10px;
    overflow-x: auto;
    align-items: center;
}

.news-pill {
    display: flex;
    flex-direction: column;
    padding: 8px 14px;
    background: var(--bg-main);
    border-radius: 10px;
    text-decoration: none;
    color: var(--text-main);
    border: 1px solid var(--border);
    transition: all 0.2s;
    white-space: nowrap;
    flex-shrink: 0;
}

.news-pill:hover {
    border-color: var(--accent);
}

.news-pill strong { font-size: 13px; }
.news-pill span { font-size: 11px; color: var(--text-muted); }

.news-all {
    color: var(--accent);
    text-decoration: none;
    font-weight: 700;
    padding: 0 12px;
    white-space: nowrap;
}

.news-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.news-item {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 24px;
    border-radius: 16px;
}

.news-date {
    color: var(--text-muted);
    font-size: 12px;
    margin-bottom: 8px;
}

.news-item h2 {
    margin-bottom: 12px;
    color: var(--accent);
}

.news-content {
    line-height: 1.6;
    white-space: pre-wrap;
}

@media (max-width: 900px) {
    .admin-grid { grid-template-columns: 1fr; }
    .user-menu-name { display: none; }
    .topbar { padding: 0 12px; }
}
'''

# ============= ЗАПИСЫВАЕМ =============
os.makedirs("templates/admin", exist_ok=True)

files = {
    "app.py": app_py,
    "templates/base.html": base_html,
    "templates/index.html": index_html,
    "templates/news.html": news_html,
    "templates/admin/dashboard.html": admin_dashboard_html,
    "templates/admin/users.html": admin_users_html,
    "templates/admin/mods.html": admin_mods_html,
    "templates/admin/news.html": admin_news_html,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ {path}")

css_path = "static/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    existing_css = f.read()

if "/* ===== TOPBAR ===== */" not in existing_css:
    with open(css_path, "a", encoding="utf-8") as f:
        f.write(extra_css)
    print(f"  ✅ {css_path}")

print("\n🎉 ЭТАП 5 — ФИНАЛЬНЫЙ — ГОТОВ!")
print("\n✨ Добавлено:")
print("   👑 Админ-панель (только для nehea664)")
print("   📊 Статистика сайта + графики")
print("   👥 Управление пользователями (бан, удаление)")
print("   📦 Управление модами")
print("   📰 Новости (создание/удаление)")
print("   🎯 Топбар сверху справа с иконками 🔔 💌 + меню профиля")
print("   📱 Выпадающее меню профиля (Профиль/Настройки/Активность/Выйти)")
print("\n📤 git add . && git commit -m 'v6: admin + topbar + news' && git push --force origin main")
print("На PA: cd ~/mysite && git fetch origin main && git reset --hard origin/main && Reload")
print("\n👑 Теперь у тебя (nehea664) есть админка!")
print("Открой http://nehea664.pythonanywhere.com/admin")