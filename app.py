# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key_change_in_production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mods.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ====================== МОДЕЛИ ======================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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

# ====================== МАРШРУТЫ ======================
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
    versions = ['1.20.4', '1.20.2', '1.20.1', '1.19.4', '1.19.2', '1.18.2', '1.16.5', '1.12.2']

    return render_template('index.html', mods=mods, categories=categories, versions=versions,
                           search=search, sel_category=category, sel_version=mc_version)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Это имя пользователя уже занято', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Этот email уже используется', 'error')
            return redirect(url_for('register'))

        user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('index'))
        flash('Неверное имя пользователя или пароль', 'error')
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
    versions = ['1.20.4', '1.20.2', '1.20.1', '1.19.4', '1.19.2', '1.18.2', '1.16.5', '1.12.2']

    if request.method == 'POST':
        file = request.files.get('mod_file')
        if not file or not allowed_file(file.filename):
            flash('Пожалуйста, загрузите .jar файл', 'error')
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

@app.route('/delete/<int:mod_id>', methods=['POST'])
@login_required
def delete_mod(mod_id):
    mod = Mod.query.get_or_404(mod_id)
    if mod.user_id != current_user.id:
        flash('Нет доступа', 'error')
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

if __name__ == '__main__':
    app.run(debug=True)