# -*- coding: utf-8 -*-
import os

print("🚀 Этап 7 — AMOLED тема + Toast снизу + Свежие версии MC...")

# ============= ПАТЧИМ app.py — версии MC =============
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

old_versions = "versions = ['1.21', '1.20.4', '1.20.2', '1.20.1', '1.19.4', '1.19.2', '1.18.2', '1.16.5', '1.12.2']"
new_versions = "versions = ['1.21.4', '1.21.3', '1.21.1', '1.21', '1.20.6', '1.20.4', '1.20.2', '1.20.1', '1.19.4', '1.19.2', '1.18.2', '1.17.1', '1.16.5', '1.12.2', '1.8.9', '1.7.10']"

app_code = app_code.replace(old_versions, new_versions)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)
print("  ✅ app.py (обновлены версии MC до 1.21.4)")

# ============= ОБНОВЛЯЕМ settings.html — добавляем AMOLED =============
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
                {% for tk, tn in [('green','Зелёный'),('blue','Синий'),('purple','Фиолетовый'),('orange','Оранжевый'),('pink','Розовый'),('light','Светлая'),('amoled','AMOLED 🖤')] %}
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

with open("templates/settings.html", "w", encoding="utf-8") as f:
    f.write(settings_html)
print("  ✅ templates/settings.html (добавлена AMOLED тема)")

# ============= ДОБАВЛЯЕМ CSS =============
extra_css = '''

/* ===== AMOLED THEME ===== */
[data-theme="amoled"] {
    --bg-main: #000000;
    --bg-card: #0a0a0a;
    --bg-sidebar: #050505;
    --text-main: #ffffff;
    --text-muted: #6b6b6b;
    --border: #1a1a1a;
    --accent: #00ff88;
    --accent-2: #00d4ff;
    --gradient: linear-gradient(135deg, #00ff88, #00d4ff);
}

[data-theme="amoled"] body {
    background: #000000 !important;
    animation: none !important;
}

[data-theme="amoled"] .sidebar,
[data-theme="amoled"] .topbar,
[data-theme="amoled"] .mod-card,
[data-theme="amoled"] .settings-card,
[data-theme="amoled"] .admin-stat-card,
[data-theme="amoled"] .form-page,
[data-theme="amoled"] .news-item,
[data-theme="amoled"] .comment,
[data-theme="amoled"] .achievement,
[data-theme="amoled"] .my-mod-card,
[data-theme="amoled"] .stat-card,
[data-theme="amoled"] .top-card,
[data-theme="amoled"] .notif,
[data-theme="amoled"] .chat-item,
[data-theme="amoled"] .activity-item,
[data-theme="amoled"] .admin-table-wrap,
[data-theme="amoled"] .admin-block,
[data-theme="amoled"] .empty-state,
[data-theme="amoled"] .toast,
[data-theme="amoled"] .user-dropdown,
[data-theme="amoled"] .news-banner,
[data-theme="amoled"] .news-pill {
    background: #0a0a0a !important;
    border-color: #1a1a1a !important;
}

[data-theme="amoled"] .mod-card:hover,
[data-theme="amoled"] .top-card:hover,
[data-theme="amoled"] .notif:hover,
[data-theme="amoled"] .chat-item:hover,
[data-theme="amoled"] .activity-item:hover,
[data-theme="amoled"] .admin-stat-card:hover,
[data-theme="amoled"] .admin-action-btn:hover {
    border-color: #00ff88 !important;
    box-shadow: 0 0 20px rgba(0, 255, 136, 0.15);
}

[data-theme="amoled"] .search-bar input,
[data-theme="amoled"] .search-bar select,
[data-theme="amoled"] .form-page input,
[data-theme="amoled"] .form-page select,
[data-theme="amoled"] .form-page textarea,
[data-theme="amoled"] .settings-card input,
[data-theme="amoled"] .settings-card textarea,
[data-theme="amoled"] .comment-form textarea,
[data-theme="amoled"] .chat-form input,
[data-theme="amoled"] .file-label {
    background: #000000 !important;
    border-color: #1a1a1a !important;
    color: #ffffff !important;
}

[data-theme="amoled"] .sort-tab,
[data-theme="amoled"] .topbar-icon,
[data-theme="amoled"] .topbar-btn,
[data-theme="amoled"] .btn-sidebar,
[data-theme="amoled"] .admin-btn,
[data-theme="amoled"] .admin-action-btn,
[data-theme="amoled"] .stat-mini {
    background: #0a0a0a !important;
    border-color: #1a1a1a !important;
}

[data-theme="amoled"] .user-menu-btn {
    background: #0a0a0a !important;
    border-color: #1a1a1a !important;
}

[data-theme="amoled"] .nav-item:hover {
    background: #1a1a1a !important;
}

[data-theme="amoled"] .info-table,
[data-theme="amoled"] .mod-info table {
    background: #0a0a0a !important;
}

[data-theme="amoled"] .mod-info td,
[data-theme="amoled"] .info-table td {
    border-color: #1a1a1a !important;
}

[data-theme="amoled"] .admin-table th {
    background: #000000 !important;
}

[data-theme="amoled"] .admin-table td {
    border-color: #1a1a1a !important;
}

[data-theme="amoled"] ::-webkit-scrollbar-track {
    background: #000000;
}

[data-theme="amoled"] .msg-other .msg-bubble {
    background: #1a1a1a !important;
}

[data-theme="amoled"] .ach-icon,
[data-theme="amoled"] .notif-icon,
[data-theme="amoled"] .act-icon {
    background: #000000 !important;
}

/* AMOLED preview в настройках */
.theme-amoled .tp-bar { background: linear-gradient(135deg, #00ff88, #00d4ff); }
.theme-amoled .tp-content { background: #000000; }
.theme-amoled .theme-preview { background: #000000; }

/* ===== TOAST В ПРАВЫЙ НИЖНИЙ УГОЛ ===== */
.toast-container {
    position: fixed !important;
    top: auto !important;
    bottom: 24px !important;
    right: 24px !important;
    z-index: 9999;
    display: flex;
    flex-direction: column-reverse !important;
    gap: 10px;
    max-width: 400px;
    pointer-events: none;
}

.toast {
    transform: translateX(450px) !important;
    opacity: 0;
}

.toast.show {
    transform: translateX(0) !important;
    opacity: 1;
}

.toast.hide {
    transform: translateX(450px) !important;
    opacity: 0;
}

@media (max-width: 600px) {
    .toast-container {
        right: 12px !important;
        left: 12px !important;
        bottom: 12px !important;
        max-width: none;
    }
}
'''

css_path = "static/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    existing_css = f.read()

if "/* ===== AMOLED THEME ===== */" not in existing_css:
    with open(css_path, "a", encoding="utf-8") as f:
        f.write(extra_css)
    print(f"  ✅ {css_path} (добавлена AMOLED + toast снизу)")
else:
    # Уже есть — обновим
    marker = "/* ===== AMOLED THEME ===== */"
    new_css = existing_css.split(marker)[0] + extra_css
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(new_css)
    print(f"  ✅ {css_path} (обновлены стили)")

print("\n🎉 ЭТАП 7 ГОТОВ!")
print("\n✨ Добавлено:")
print("   🖤 AMOLED тема (настоящий чёрный)")
print("   📍 Toast уведомления в правом НИЖНЕМ углу")
print("   🆕 Версии MC до 1.21.4")
print("\n📤 git add . && git commit -m 'v8: AMOLED + bottom toasts + MC 1.21.4' && git push --force origin main")
print("На PA: cd ~/mysite && git fetch origin main && git reset --hard origin/main && Reload")
print("\n👉 После применения зайди в Настройки → Тема → AMOLED 🖤")