# -*- coding: utf-8 -*-
import os

print("🚀 Этап 4 — Уведомления, ЛС, Активность...")

# ============= APP.PY =============
app_py = '''# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import func, or_, and_, text

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
        if self.avatar: return url_for('static', filename='avatars/' + self.avatar)
        return None
    @property
    def total_downloads(self): return sum(m.downloads for m in self.mods)
    @property
    def total_likes(self): return sum(m.likes_count for m in self.mods)
    @property
    def followers_count(self): return Subscription.query.filter_by(author_id=self.id).count()
    @property
    def following_count(self): return Subscription.query.filter_by(follower_id=self.id).count()
    @property
    def unread_notifications(self):
        return Notification.query.filter_by(user_id=self.id, is_read=False).count()
    @property
    def unread_messages(self):
        return Message.query.filter_by(to_user_id=self.id, is_read=False).count()

    def is_subscribed_to(self, author):
        if not author or self.id == author.id: return False
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
    type = db.Column(db.String(50))  # like, comment, subscribe, new_mod
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
    type = db.Column(db.String(50))  # uploaded, liked, commented, subscribed
    text = db.Column(db.String(300))
    link = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return filename.lower().endswith('.jar')

def allowed_image(filename):
    return filename.lower().rsplit('.', 1)[-1] in {'jpg', 'jpeg', 'png', 'gif', 'webp'}

def notify(user_id, type, text, link='', from_user_id=None):
    """Создать уведомление"""
    if from_user_id == user_id:
        return  # Не уведомляем самих себя
    n = Notification(user_id=user_id, from_user_id=from_user_id, type=type, text=text, link=link)
    db.session.add(n)

def log_activity(user_id, type, text, link=''):
    """Записать активность"""
    a = Activity(user_id=user_id, type=type, text=text, link=link)
    db.session.add(a)

@app.context_processor
def inject_globals():
    if current_user.is_authenticated:
        return dict(
            user_theme=current_user.theme,
            user_animations=current_user.animations,
            ACHIEVEMENTS=ACHIEVEMENTS,
            unread_notif=current_user.unread_notifications,
            unread_msg=current_user.unread_messages
        )
    return dict(user_theme='green', user_animations=True, ACHIEVEMENTS=ACHIEVEMENTS, unread_notif=0, unread_msg=0)

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

@app.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(50).all()
    # Помечаем как прочитанные
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('notifications.html', notifs=notifs)

@app.route('/messages')
@login_required
def messages():
    # Список всех диалогов
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
    # Помечаем сообщения от другого как прочитанные
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
        db.session.add(mod)
        db.session.flush()
        # Активность
        log_activity(current_user.id, 'uploaded', f'Опубликовал мод "{mod.title}"', url_for('mod_page', mod_id=mod.id))
        # Уведомление подписчикам
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
    if comment.user_id != current_user.id and comment.mod.user_id != current_user.id:
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
                db.session.commit()
                flash('Аватарка обновлена!', 'success')
            else:
                flash('Выбери картинку', 'error')
        elif action == 'password':
            old = request.form.get('old_password')
            new = request.form.get('new_password')
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
    if mod.user_id != current_user.id: return redirect(url_for('index'))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], mod.filename)
    if os.path.exists(filepath): os.remove(filepath)
    for ss in mod.screenshots_list:
        ss_path = os.path.join(app.config['SCREENSHOTS_FOLDER'], ss)
        if os.path.exists(ss_path): os.remove(ss_path)
    db.session.delete(mod); db.session.commit()
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
            <a href="{{ url_for('notifications') }}" class="nav-item">
                <span class="nav-icon">🔔</span><span>Уведомления</span>
                {% if unread_notif > 0 %}<span class="badge-count">{{ unread_notif }}</span>{% endif %}
            </a>
            <a href="{{ url_for('messages') }}" class="nav-item">
                <span class="nav-icon">💌</span><span>Сообщения</span>
                {% if unread_msg > 0 %}<span class="badge-count">{{ unread_msg }}</span>{% endif %}
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

# ============= NOTIFICATIONS.HTML =============
notifications_html = '''{% extends 'base.html' %}
{% block content %}
<div class="page-header">
    <div>
        <h1 class="page-title">🔔 Уведомления</h1>
        <p class="page-subtitle">Все события на твоём аккаунте</p>
    </div>
</div>

<div class="notifications-list">
    {% for n in notifs %}
    <a href="{{ n.link or '#' }}" class="notif {% if not n.is_read %}new{% endif %}">
        <div class="notif-icon">
            {% if n.type == 'like' %}❤️
            {% elif n.type == 'comment' %}💬
            {% elif n.type == 'subscribe' %}🔔
            {% elif n.type == 'new_mod' %}🆕
            {% elif n.type == 'message' %}💌
            {% else %}📌
            {% endif %}
        </div>
        <div class="notif-body">
            <div class="notif-text">{{ n.text }}</div>
            <div class="notif-date">{{ n.created_at.strftime('%d.%m.%Y %H:%M') }}</div>
        </div>
    </a>
    {% else %}
    <div class="empty-state">
        <div class="empty-icon">🔕</div>
        <h3>Пока нет уведомлений</h3>
    </div>
    {% endfor %}
</div>
{% endblock %}'''

# ============= MESSAGES.HTML =============
messages_html = '''{% extends 'base.html' %}
{% block content %}
<div class="page-header">
    <div>
        <h1 class="page-title">💌 Сообщения</h1>
        <p class="page-subtitle">Личные сообщения</p>
    </div>
</div>

<div class="chats-list">
    {% for chat in chats %}
    <a href="{{ url_for('chat', username=chat.user.username) }}" class="chat-item">
        {% if chat.user.avatar %}
            <img src="{{ url_for('static', filename='avatars/' + chat.user.avatar) }}" class="chat-avatar" alt="">
        {% else %}
            <div class="chat-avatar-letter">{{ chat.user.username[0]|upper }}</div>
        {% endif %}
        <div class="chat-info">
            <div class="chat-name">{{ chat.user.username }}</div>
            {% if chat.last %}
            <div class="chat-last">
                {% if chat.last.from_user_id == current_user.id %}<span>Вы: </span>{% endif %}
                {{ chat.last.text[:60] }}{% if chat.last.text|length > 60 %}...{% endif %}
            </div>
            {% endif %}
        </div>
        <div class="chat-meta">
            {% if chat.last %}<div class="chat-date">{{ chat.last.created_at.strftime('%d.%m %H:%M') }}</div>{% endif %}
            {% if chat.unread > 0 %}<div class="chat-unread">{{ chat.unread }}</div>{% endif %}
        </div>
    </a>
    {% else %}
    <div class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>Нет диалогов</h3>
        <p>Зайди на страницу автора и напиши ему!</p>
    </div>
    {% endfor %}
</div>
{% endblock %}'''

# ============= CHAT.HTML =============
chat_html = '''{% extends 'base.html' %}
{% block content %}
<div class="chat-header">
    <a href="{{ url_for('messages') }}" class="back-btn">← Назад</a>
    <div class="chat-user">
        {% if other.avatar %}
            <img src="{{ url_for('static', filename='avatars/' + other.avatar) }}" class="chat-avatar" alt="">
        {% else %}
            <div class="chat-avatar-letter">{{ other.username[0]|upper }}</div>
        {% endif %}
        <a href="{{ url_for('user_page', username=other.username) }}" class="chat-username">{{ other.username }}</a>
    </div>
</div>

<div class="chat-messages" id="chat-messages">
    {% for m in msgs %}
    <div class="msg {% if m.from_user_id == current_user.id %}msg-mine{% else %}msg-other{% endif %}">
        <div class="msg-bubble">
            <div class="msg-text">{{ m.text }}</div>
            <div class="msg-time">{{ m.created_at.strftime('%H:%M') }}</div>
        </div>
    </div>
    {% else %}
    <div class="empty-state">
        <div class="empty-icon">💬</div>
        <h3>Начни диалог</h3>
    </div>
    {% endfor %}
</div>

<form method="POST" class="chat-form">
    <input type="text" name="text" placeholder="Написать сообщение..." required maxlength="2000" autofocus>
    <button type="submit">📤</button>
</form>

<script>
const m = document.getElementById('chat-messages');
if (m) m.scrollTop = m.scrollHeight;
</script>
{% endblock %}'''

# ============= ACTIVITY.HTML =============
activity_html = '''{% extends 'base.html' %}
{% block content %}
<div class="page-header">
    <div>
        <h1 class="page-title">📅 Активность {{ user.username }}</h1>
    </div>
</div>

<div class="activity-list">
    {% for a in acts %}
    <a href="{{ a.link or '#' }}" class="activity-item">
        <div class="act-icon">
            {% if a.type == 'uploaded' %}📤
            {% elif a.type == 'liked' %}❤️
            {% elif a.type == 'commented' %}💬
            {% elif a.type == 'subscribed' %}🔔
            {% else %}📌
            {% endif %}
        </div>
        <div class="act-body">
            <div class="act-text">{{ a.text }}</div>
            <div class="act-date">{{ a.created_at.strftime('%d.%m.%Y %H:%M') }}</div>
        </div>
    </a>
    {% else %}
    <div class="empty-state">
        <div class="empty-icon">📅</div>
        <h3>Нет активности</h3>
    </div>
    {% endfor %}
</div>
{% endblock %}'''

# ============= USER.HTML (с кнопкой "Написать") =============
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
            <a href="{{ url_for('chat', username=user.username) }}" class="btn-subscribe" style="background: var(--bg-card); color: var(--text-main); border: 2px solid var(--border);">
                💌 Написать
            </a>
            <a href="{{ url_for('activity', username=user.username) }}" class="btn-subscribe" style="background: var(--bg-card); color: var(--text-main); border: 2px solid var(--border);">
                📅 Активность
            </a>
            {% elif current_user.is_authenticated and current_user.id == user.id %}
            <a href="{{ url_for('activity', username=user.username) }}" class="btn-subscribe" style="background: var(--bg-card); color: var(--text-main); border: 2px solid var(--border);">
                📅 Моя активность
            </a>
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

# ============= ДОБАВЛЯЕМ CSS =============
extra_css = '''

/* ===== BADGE ===== */
.badge-count {
    background: #ff4757;
    color: white;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 800;
    margin-left: auto;
    min-width: 20px;
    text-align: center;
    animation: pulse 2s infinite;
}

/* ===== NOTIFICATIONS ===== */
.notifications-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.notif {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px;
    background: var(--bg-card);
    border-radius: 12px;
    text-decoration: none;
    color: inherit;
    border: 1px solid var(--border);
    transition: all 0.2s;
}

.notif:hover {
    transform: translateX(5px);
    border-color: var(--accent);
}

.notif.new {
    background: linear-gradient(90deg, rgba(34,255,136,0.1), var(--bg-card));
    border-left: 3px solid var(--accent);
}

.notif-icon {
    font-size: 28px;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-main);
    border-radius: 50%;
    flex-shrink: 0;
}

.notif-body { flex: 1; }
.notif-text { font-weight: 600; margin-bottom: 4px; }
.notif-date { font-size: 12px; color: var(--text-muted); }

/* ===== CHATS LIST ===== */
.chats-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.chat-item {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px;
    background: var(--bg-card);
    border-radius: 12px;
    text-decoration: none;
    color: inherit;
    border: 1px solid var(--border);
    transition: all 0.2s;
}

.chat-item:hover {
    border-color: var(--accent);
    transform: translateX(5px);
}

.chat-avatar {
    width: 50px; height: 50px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid var(--accent);
}

.chat-avatar-letter {
    width: 50px; height: 50px;
    border-radius: 50%;
    background: var(--gradient);
    color: #0f1626;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 22px;
}

.chat-info { flex: 1; min-width: 0; }
.chat-name { font-weight: 700; margin-bottom: 4px; }
.chat-last { color: var(--text-muted); font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.chat-meta {
    text-align: right;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 6px;
}

.chat-date { font-size: 11px; color: var(--text-muted); }

.chat-unread {
    background: var(--gradient);
    color: #0f1626;
    border-radius: 10px;
    padding: 3px 9px;
    font-size: 11px;
    font-weight: 800;
}

/* ===== CHAT PAGE ===== */
.chat-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding-bottom: 16px;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--border);
}

.back-btn {
    color: var(--text-muted);
    text-decoration: none;
    font-weight: 600;
}

.back-btn:hover { color: var(--accent); }

.chat-user {
    display: flex;
    align-items: center;
    gap: 10px;
}

.chat-username {
    color: var(--text-main);
    text-decoration: none;
    font-weight: 700;
    font-size: 18px;
}

.chat-username:hover { color: var(--accent); }

.chat-messages {
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-height: 50vh;
    max-height: 60vh;
    overflow-y: auto;
    padding: 12px 0;
}

.msg {
    display: flex;
    max-width: 70%;
}

.msg-mine {
    align-self: flex-end;
}

.msg-other {
    align-self: flex-start;
}

.msg-bubble {
    padding: 10px 14px;
    border-radius: 14px;
    background: var(--bg-card);
    word-wrap: break-word;
}

.msg-mine .msg-bubble {
    background: var(--gradient);
    color: #0f1626;
    border-bottom-right-radius: 4px;
}

.msg-other .msg-bubble {
    border-bottom-left-radius: 4px;
}

.msg-text { font-size: 14px; line-height: 1.4; }

.msg-time {
    font-size: 10px;
    opacity: 0.7;
    margin-top: 4px;
    text-align: right;
}

.chat-form {
    display: flex;
    gap: 10px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border);
}

.chat-form input {
    flex: 1;
    padding: 12px 16px;
    border: 1px solid var(--border);
    border-radius: 25px;
    background: var(--bg-card);
    color: var(--text-main);
    font-size: 14px;
}

.chat-form input:focus {
    outline: none;
    border-color: var(--accent);
}

.chat-form button {
    width: 50px;
    height: 50px;
    background: var(--gradient);
    color: #0f1626;
    border: none;
    border-radius: 50%;
    font-size: 20px;
    cursor: pointer;
    transition: all 0.2s;
}

.chat-form button:hover {
    transform: scale(1.1);
}

/* ===== ACTIVITY ===== */
.activity-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.activity-item {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px;
    background: var(--bg-card);
    border-radius: 12px;
    text-decoration: none;
    color: inherit;
    border: 1px solid var(--border);
    transition: all 0.2s;
}

.activity-item:hover {
    border-color: var(--accent);
    transform: translateX(5px);
}

.act-icon {
    font-size: 24px;
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-main);
    border-radius: 50%;
    flex-shrink: 0;
}

.act-body { flex: 1; }
.act-text { font-weight: 600; }
.act-date { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
'''

# ============= ЗАПИСЫВАЕМ =============
files = {
    "app.py": app_py,
    "templates/base.html": base_html,
    "templates/notifications.html": notifications_html,
    "templates/messages.html": messages_html,
    "templates/chat.html": chat_html,
    "templates/activity.html": activity_html,
    "templates/user.html": user_html,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ {path}")

css_path = "static/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    existing_css = f.read()

if "/* ===== BADGE ===== */" not in existing_css:
    with open(css_path, "a", encoding="utf-8") as f:
        f.write(extra_css)
    print(f"  ✅ {css_path}")

print("\n🎉 ЭТАП 4 ГОТОВ!")
print("\n✨ Добавлено:")
print("   🔔 Уведомления (лайки, комменты, подписки, новые моды)")
print("   💌 Личные сообщения между пользователями")
print("   📅 Лента активности")
print("   🔴 Счётчики непрочитанных в меню")
print("\n📤 git add . && git commit -m 'v5: notifications + messages + activity' && git push --force origin main")
print("На PA: cd ~/mysite && git fetch origin main && git reset --hard origin/main && Reload")
print("\n👉 'готово' — финальный Этап 5 (Админ-панель + Статистика + Новости)")