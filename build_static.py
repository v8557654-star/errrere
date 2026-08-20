#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор статической версии сайта MineMods (чистый HTML/CSS/JS, без Flask).

Запуск:  python build_static.py
Результат: готовый сайт в папке docs/ — самодостаточный, отдельный от основного
проекта (можно копировать куда угодно или публиковать через GitHub Pages из /docs).

Скрипт генерирует HTML-страницы и копирует нужные ресурсы из static/ в
docs/static/, так что править стили/JS надо в основной папке static/:
  static/css/style.css        — основные стили (общие со старой версией)
  static/css/static-site.css  — доп. стили статической версии
  static/js/site.js           — вся клиентская логика (демо-режим, localStorage)
  static/js/main.js           — базовые утилиты
"""
import os
import shutil
from string import Template

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, 'docs')   # отдельная папка статического сайта

# Ресурсы, которые нужны статическому сайту (копируются из static/ в docs/static/)
STATIC_FILES = [
    'css/style.css',
    'css/static-site.css',
    'js/main.js',
    'js/site.js',
]
SCREENSHOTS_DIR = 'screenshots'

CATEGORIES = ['Магия', 'Техника', 'Оружие', 'Мобы', 'Декор', 'Еда', 'Миры', 'Утилиты', 'Другое']
MC_VERSIONS = ['1.21.4', '1.21.3', '1.21.1', '1.21', '1.20.6', '1.20.4', '1.20.2', '1.20.1',
               '1.19.4', '1.19.2', '1.18.2', '1.17.1', '1.16.5', '1.12.2', '1.8.9', '1.7.10']
UPLOAD_TYPES = [
    ('mod', 'Мод', '⛏', '.jar'), ('shader', 'Шейдер', '🌅', '.zip'),
    ('plugin', 'Плагин', '🔌', '.jar'), ('resourcepack', 'Ресурспак', '🎨', '.zip'),
    ('modpack', 'Сборка', '📦', '.zip / .mrpack'), ('datapack', 'Датапак', '📝', '.zip'),
    ('map', 'Карта', '🗺️', '.zip'),
]

MODS = [
    dict(id='dragon-mounts-2', title='Dragon Mounts II', category='Мобы', mc='1.20.4', version='1.6.3',
         author='SteveCraft', tags=['драконы', 'маунты', 'мобы'], downloads=15230, likes=1210, views=55800,
         date=20260728,
         desc='Выращивайте, приручайте и оседлайте девять видов драконов с уникальными способностями и окрасками.'),
    dict(id='technova', title='TechNova', category='Техника', mc='1.20.1', version='3.2.0',
         author='TechWizard', tags=['техника', 'автоматизация', 'энергия'], downloads=12840, likes=932, views=40210,
         date=20260812,
         desc='Продвинутая автоматизация: конвейеры, дробилки, энергосети и умные механизмы для больших фабрик.'),
    dict(id='utility-belt', title='Utility Belt', category='Утилиты', mc='1.20.6', version='3.0.5',
         author='TechWizard', tags=['утилиты', 'инструменты', 'hud'], downloads=11210, likes=980, views=33400,
         date=20260802,
         desc='Пояс с быстрым доступом к инструментам, расширенный HUD и умные горячие клавиши.'),
    dict(id='arcane-realms', title='Arcane Realms', category='Магия', mc='1.21.1', version='2.0.1',
         author='MageCraft', tags=['магия', 'ритуалы', 'rpg'], downloads=9560, likes=812, views=31200,
         date=20260805,
         desc='Система заклинаний, ритуалы, магические артефакты и древние подземелья с боссами.'),
    dict(id='deco-plus', title='DecoPlus', category='Декор', mc='1.21', version='4.1.2',
         author='AlexBuilds', tags=['декор', 'мебель', 'строительство'], downloads=8920, likes=745, views=26400,
         date=20260810,
         desc='Сотни блоков мебели и декора: стулья, лампы, полки и анимированные украшения.'),
    dict(id='sky-village', title='Sky Village', category='Миры', mc='1.21.4', version='2.2.0',
         author='SteveCraft', tags=['деревни', 'структуры', 'генерация'], downloads=7650, likes=620, views=21900,
         date=20260815,
         desc='Парящие в небе деревни с торговцами, воздушными кораблями и редкой добычей.'),
    dict(id='feastcraft', title='FeastCraft', category='Еда', mc='1.20.1', version='2.4.0',
         author='AlexBuilds', tags=['еда', 'фермерство', 'кулинария'], downloads=6840, likes=512, views=19800,
         date=20260720,
         desc='Более 120 новых блюд, кухонная утварь, фермерские культуры и система голода с бонусами.'),
    dict(id='void-dimensions', title='Void Dimensions', category='Миры', mc='1.19.2', version='1.3.0',
         author='VoidWalker', tags=['измерения', 'миры', 'приключения'], downloads=5430, likes=498, views=15700,
         date=20260630,
         desc='Четыре новых измерения с уникальными биомами, структурами и боссами.'),
    dict(id='royal-armory', title='Royal Armory', category='Оружие', mc='1.18.2', version='1.9.1',
         author='RoyalSmith', tags=['оружие', 'броня', 'бой'], downloads=4210, likes=365, views=12100,
         date=20260518,
         desc='60+ видов средневекового оружия и брони с уникальными свойствами и прокачкой.'),
]

NAV = [
    ('home', 'index.html', '🏠', 'Каталог', False),
    ('news', 'news.html', '📰', 'Новости', False),
    ('modrinth', 'modrinth.html', '🌍', 'Modrinth', False),
    ('github', 'github.html', '🦊', 'GitHub', False),
    ('feed', 'feed.html', '📡', 'Подписки', True),
    ('favorites', 'favorites.html', '❤️', 'Избранное', True),
    ('upload', 'upload.html', '📤', 'Загрузить', True),
    ('achievements', 'achievements.html', '🏅', 'Достижения', True),
]

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
           "%3Ctext y='.9em' font-size='90'%3E⛏%3C/text%3E%3C/svg%3E")

LAYOUT = Template(r'''<!DOCTYPE html>
<html lang="ru" data-theme="green" data-animations="on">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="MineMods — лучшая платформа для поиска и загрузки модов для Minecraft">
    <meta name="theme-color" content="#22ff88">
    <title>$title</title>
    <link rel="icon" href="$favicon">
    <script>(function(){function g(k,d){try{var v=localStorage.getItem(k);return v===null?d:JSON.parse(v);}catch(e){return d;}}
    var h=document.documentElement;h.setAttribute('data-theme',g('mm_theme','green'));
    h.setAttribute('data-animations',g('mm_animations','on')==='off'?'off':'on');})();</script>
    <link rel="stylesheet" href="static/css/style.css">
    <link rel="stylesheet" href="static/css/static-site.css">
    <link rel="preconnect" href="https://api.modrinth.com">
    <link rel="preconnect" href="https://api.github.com">
</head>
<body data-page="$page"$protected>
<a href="#main-content" class="skip-link">Перейти к основному контенту</a>

<div class="layout">
    <aside class="sidebar">
        <div class="sidebar-header">
            <a href="index.html" class="logo">
                <span class="logo-icon">⛏</span>
                <span class="logo-text">MineMods</span>
            </a>
        </div>
        <nav class="sidebar-nav" role="navigation" aria-label="Боковая навигация">
$nav_items
        </nav>
        <div class="sidebar-footer" id="sidebarAuth"></div>
    </aside>

    <main class="main-content" id="main-content">
        <header class="topbar" role="banner">
            <button class="mobile-menu-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')" aria-label="Меню">☰</button>
            <div class="topbar-right" id="topbarRight" role="navigation" aria-label="Основная навигация"></div>
        </header>

        <div class="container">
            <div id="pageContent">
$content
            </div>
        </div>
    </main>
</div>

<script>
document.addEventListener('click', function(e) {
    var sidebar = document.querySelector('.sidebar');
    var toggle = document.querySelector('.mobile-menu-toggle');
    if (window.innerWidth <= 900 && sidebar.classList.contains('open')
        && !sidebar.contains(e.target) && e.target !== toggle) {
        sidebar.classList.remove('open');
    }
    var dropdown = document.querySelector('.user-dropdown');
    var menuBtn = document.querySelector('.user-menu-btn');
    if (dropdown && dropdown.classList.contains('open') && menuBtn
        && !dropdown.contains(e.target) && !menuBtn.contains(e.target)) {
        dropdown.classList.remove('open');
    }
});
</script>
<script src="static/js/main.js"></script>
<script src="static/js/site.js"></script>
$extra_js
</body>
</html>
''')


def build_nav(active):
    rows = []
    for key, href, icon, label, auth in NAV:
        cls = 'nav-item' + (' active' if key == active else '')
        style = ' class="%s"' % cls
        extra = ' style="display:none" class="nav-item auth-only"' if auth else style
        if auth:
            rows.append('            <a href="%s"%s><span class="nav-icon" aria-hidden="true">%s</span><span>%s</span></a>'
                        % (href, extra, icon, label))
        else:
            rows.append('            <a href="%s"%s><span class="nav-icon" aria-hidden="true">%s</span><span>%s</span></a>'
                        % (href, style, icon, label))
    return '\n'.join(rows)


def page(filename, title, active, content, page_name='', protected=False, extra_js=''):
    html = LAYOUT.substitute(
        title=title, favicon=FAVICON, page=page_name,
        protected=' data-protected="1"' if protected else '',
        nav_items=build_nav(active), content=content, extra_js=extra_js)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, filename), 'w', encoding='utf-8') as f:
        f.write(html)
    print('✔ docs/' + filename)


def copy_assets():
    """Копирует нужные статические ресурсы в docs/static/ — папка docs/ становится
    самодостаточной и не зависит от остального проекта."""
    for rel in STATIC_FILES:
        src = os.path.join(ROOT, 'static', rel)
        dst = os.path.join(OUT_DIR, 'static', rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print('⧉ docs/static/' + rel)
    # Скриншоты модов (если есть — берём только изображения)
    src_dir = os.path.join(ROOT, 'static', SCREENSHOTS_DIR)
    dst_dir = os.path.join(OUT_DIR, 'static', SCREENSHOTS_DIR)
    if os.path.isdir(src_dir):
        os.makedirs(dst_dir, exist_ok=True)
        for name in sorted(os.listdir(src_dir)):
            if name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                shutil.copy2(os.path.join(src_dir, name), os.path.join(dst_dir, name))
                print('⧉ docs/static/%s/%s' % (SCREENSHOTS_DIR, name))


def mod_card(m):
    tags_h = ''.join('<span class="tag">#%s</span>' % t for t in m['tags'][:3])
    return '''        <div class="mod-card" data-title="{title}" data-desc="{desc}" data-category="{category}"
             data-mc="{mc}" data-tags="{tags_flat}" data-downloads="{downloads}" data-likes="{likes}"
             data-views="{views}" data-date="{date}">
            <div class="mod-card-header">
                <div class="mod-category">{category}</div>
                <div class="mod-mc-badge">MC {mc}</div>
            </div>
            <h3><a href="mod.html?m={id}">{title}</a></h3>
            <p class="mod-meta"><span>v{version}</span> <span>•</span> <span>👤 <a href="user.html?u={author}" class="author-link">{author}</a></span></p>
            <p class="mod-desc">{desc}</p>
            <div class="mod-tags">{tags_h}</div>
            <div class="mod-footer">
                <div class="mod-stats">
                    <span class="stat-item">⬇ {downloads}</span>
                    <span class="stat-item">❤ {likes}</span>
                    <span class="stat-item">👁 {views}</span>
                </div>
                <a href="mod.html?m={id}#download" class="btn-download">Скачать</a>
            </div>
        </div>'''.format(tags_flat=' '.join(m['tags']), tags_h=tags_h, **m)


# ======================================================================
# ГЛАВНАЯ
# ======================================================================
def build_index():
    top3 = sorted(MODS, key=lambda m: -m['downloads'])[:3]
    top_cards = ''
    for i, m in enumerate(top3, 1):
        top_cards += '''        <a href="mod.html?m={id}" class="top-card top-{i}">
            <div class="top-rank">#{i}</div>
            <div class="top-info">
                <div class="mod-category">{category}</div>
                <h3>{title}</h3>
                <div class="top-stats">
                    <span>⬇ {downloads}</span>
                    <span>❤ {likes}</span>
                    <span>👁 {views}</span>
                </div>
            </div>
        </a>
'''.format(i=i, **m)

    cat_opts = '\n'.join('                <option value="%s">%s</option>' % (c, c) for c in CATEGORIES)
    ver_opts = '\n'.join('                <option value="%s">%s</option>' % (v, v) for v in MC_VERSIONS)
    cards = '\n'.join(mod_card(m) for m in MODS)

    tag_filters = [('all', 'Все'), ('техника', 'Техника'), ('магия', 'Магия'), ('приключения', 'Приключения'),
                   ('мобы', 'Мобы'), ('декор', 'Декор'), ('еда', 'Еда')]
    tag_btns = '\n            '.join(
        '<button class="tag-btn%s" data-tag="%s">%s</button>' % (' active' if k == 'all' else '', k, n)
        for k, n in tag_filters)

    content = '''
<!-- Hero -->
<section class="hero-section mb-16 animate-fade-in">
    <h1 class="hero-title">Лучшие моды для Minecraft</h1>
    <p class="hero-subtitle">
        Откройте для себя тысячи модов, улучшающих ваш игровой опыт.
        От технологических чудес до магических приключений.
    </p>
    <div class="hero-actions">
        <a href="#mods" class="btn-hero btn-hero-primary">Смотреть моды</a>
        <a href="#about" class="btn-hero btn-hero-ghost">О проекте</a>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-num counter cnt-blue" data-target="9">0</div>
            <div class="stat-label">Модов</div>
        </div>
        <div class="stat-card">
            <div class="stat-num counter cnt-purple" data-target="50000">0</div>
            <div class="stat-label">Скачиваний</div>
        </div>
        <div class="stat-card">
            <div class="stat-num counter cnt-green" data-target="1200">0</div>
            <div class="stat-label">Пользователей</div>
        </div>
        <div class="stat-card">
            <div class="stat-num counter cnt-yellow" data-target="98">0</div>
            <div class="stat-label">% Положительных</div>
        </div>
    </div>
</section>

<div class="news-banner animate-fade-in-up">
    <h3>📰 Последние новости</h3>
    <div class="news-strip">
        <a href="news.html" class="news-pill"><strong>✨ MineMods 2.0 уже здесь</strong><span>15.08</span></a>
        <a href="news.html" class="news-pill"><strong>🏆 Конкурс модов — август</strong><span>08.08</span></a>
        <a href="news.html" class="news-pill"><strong>🚀 Новый раздел шейдеров</strong><span>01.08</span></a>
        <a href="news.html" class="news-all">Все →</a>
    </div>
</div>

<div class="top-section animate-fade-in-up">
    <h2 class="section-title">🏆 Топ модов</h2>
    <div class="top-grid">
''' + top_cards + '''    </div>
</div>

<!-- Поиск и фильтры -->
<section class="mb-12 animate-fade-in-up">
    <div class="search-bar">
        <form id="modFilterForm" method="GET" action="#mods">
            <div class="search-input-wrap">
                <span class="search-icon">🔍</span>
                <input type="text" id="fq" name="q" placeholder="Поиск по названию, описанию, тегам..." autocomplete="off">
            </div>
            <select id="fcat" name="category">
                <option value="">Все категории</option>
''' + cat_opts + '''
            </select>
            <select id="fver" name="mc_version">
                <option value="">Все версии</option>
''' + ver_opts + '''
            </select>
            <button type="submit">Найти</button>
        </form>
        <div class="tags-filter">
            ''' + tag_btns + '''
        </div>
    </div>
</section>

<!-- Сортировка -->
<div class="sort-tabs mb-12 animate-fade-in-up">
    <button class="sort-tab active" data-sort="new">🆕 Новые</button>
    <button class="sort-tab" data-sort="popular">🔥 Популярные</button>
    <button class="sort-tab" data-sort="top">⭐ Лучшие</button>
    <button class="sort-tab" data-sort="views">👁 Просмотры</button>
</div>

<!-- Каталог -->
<section id="mods" class="mb-16">
    <h2 class="section-heading">Каталог модов</h2>
    <div class="mods-grid" id="modsGrid">
''' + cards + '''
        <div class="empty-state" id="noResults" style="display:none;grid-column:1/-1">
            <div class="empty-icon">📦</div>
            <h3>Ничего не найдено</h3>
        </div>
    </div>
</section>

<!-- О проекте -->
<section id="about" class="mb-16 animate-fade-in-up">
    <div class="about-card">
        <h2 class="section-heading">О проекте</h2>
        <p>
            Наш сайт предоставляет удобный каталог модов для Minecraft с поддержкой различных версий игры и загрузчиков.
            Мы стремимся сделать процесс поиска и установки модов максимально простым и приятным.
        </p>
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3>Быстрая загрузка</h3>
                <p>Оптимизированная система доставки файлов обеспечивает максимальную скорость скачивания.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🛡️</div>
                <h3>Проверенные моды</h3>
                <p>Все моды проходят проверку на безопасность и совместимость перед публикацией.</p>
            </div>
        </div>
    </div>
</section>

<!-- FAQ -->
<section id="faq" class="mb-16 animate-fade-in-up">
    <h2 class="section-heading">Частые вопросы</h2>
    <div class="faq-list">
        <details class="faq-item">
            <summary><span>Как установить мод?</span><span class="faq-arrow">▼</span></summary>
            <div class="faq-body">
                <ol>
                    <li>Выберите нужную версию Minecraft и загрузчик (Forge/Fabric)</li>
                    <li>Скачайте файл мода</li>
                    <li>Поместите файл в папку <code>mods</code> в директории игры</li>
                    <li>Запустите Minecraft с выбранным загрузчиком</li>
                </ol>
            </div>
        </details>
        <details class="faq-item">
            <summary><span>Какие версии Minecraft поддерживаются?</span><span class="faq-arrow">▼</span></summary>
            <div class="faq-body">
                Мы поддерживаем версии от 1.16.5 до последних релизов 1.21+. Каждый мод указывает совместимые версии в описании.
            </div>
        </details>
        <details class="faq-item">
            <summary><span>Безопасно ли скачивать моды здесь?</span><span class="faq-arrow">▼</span></summary>
            <div class="faq-body">
                Да, все моды проходят проверку на вирусы и вредоносное ПО. Мы размещаем файлы только из проверенных источников.
            </div>
        </details>
    </div>
</section>
'''
    page('index.html', 'MineMods — Моды для Minecraft', 'home', content, page_name='index')


# ======================================================================
# СТРАНИЦА МОДА (демо на примере TechNova)
# ======================================================================
def build_mod():
    m = [x for x in MODS if x['id'] == 'technova'][0]
    content = '''
<div class="mod-detail">
    <div class="mod-detail-header">
        <span class="mod-category">Техника</span>
        <h1>TechNova</h1>
        <div class="mod-meta-row">
            <span>👤 <a href="user.html?u=TechWizard" class="author-link">TechWizard</a></span>
            <span>📅 12.08.2026</span>
            <span>⬇ <span id="dlCount" data-n="12840">12 840</span></span>
            <span>❤ 932</span>
            <span>👁 40 210</span>
            <span>💬 <span id="commentsCount">3</span></span>
        </div>
    </div>

    <div class="screenshots-section">
        <h3>📸 Скриншоты</h3>
        <div class="screenshots-grid">
            <img src="static/screenshots/technova-1.jpg" alt="Скриншот TechNova — фабрика" class="screenshot" loading="lazy"
                 onclick="openLightbox('static/screenshots/technova-1.jpg')">
            <img src="static/screenshots/technova-2.jpg" alt="Скриншот TechNova — конвейеры" class="screenshot" loading="lazy"
                 onclick="openLightbox('static/screenshots/technova-2.jpg')">
            <img src="static/screenshots/technova-3.jpg" alt="Скриншот TechNova — энергосеть" class="screenshot" loading="lazy"
                 onclick="openLightbox('static/screenshots/technova-3.jpg')">
        </div>
    </div>

    <div class="mod-detail-grid">
        <div class="mod-detail-info">
            <table class="info-table">
                <tr><td>Версия мода</td><td><strong>3.2.0</strong></td></tr>
                <tr><td>Minecraft</td><td><strong>1.20.1</strong></td></tr>
                <tr><td>Категория</td><td><strong>Техника</strong></td></tr>
                <tr><td>Загрузчики</td><td><strong>Forge / Fabric / NeoForge</strong></td></tr>
                <tr><td>Скачиваний</td><td><strong>12 840</strong></td></tr>
                <tr><td>Просмотров</td><td><strong>40 210</strong></td></tr>
                <tr><td>Лайков</td><td><strong>932</strong></td></tr>
            </table>

            <div class="tags-container">
                <h3>🏷️ Теги</h3>
                <div class="tags-row">
                    <span class="tag">#техника</span>
                    <span class="tag">#автоматизация</span>
                    <span class="tag">#энергия</span>
                </div>
            </div>

            <div class="mod-description">
                <h3>📖 Описание</h3>
                <p>
                    TechNova — продвинутый технический мод нового поколения. Стройте полностью автоматизированные
                    фабрики: конвейерные линии, дробилки руды, плавильни, сборочные станции и гибкая энергосеть
                    с аккумуляторами. Умные фильтры предметов, беспроводная передача энергии и интеграция
                    с популярными модами вроде FE-компатибельных генераторов.
                </p>
                <p>
                    В версии 3.2.0: квантовые батареи, новый интерфейс машин, поддержка MC 1.20.4
                    и ускорение симуляции конвейеров на 40%.
                </p>
            </div>
        </div>

        <div class="mod-detail-sidebar">
            <button onclick="openDownloadModal()" class="btn-download-big">⬇ Скачать .jar</button>
            <button class="btn-like" id="likeBtn">
                <span class="like-icon">🤍</span>
                <span class="like-text">Лайкнуть</span>
                <span class="like-count">932</span>
            </button>

            <div class="mod-quick-info">
                <div class="qi-row">
                    <span>Автор</span>
                    <a href="user.html?u=TechWizard" class="author-link"><strong>TechWizard</strong></a>
                </div>
                <div class="qi-row">
                    <span>Опубликовано</span>
                    <strong>12.08.2026</strong>
                </div>
            </div>
        </div>
    </div>

    <div class="comments-section" id="comments">
        <h3>💬 Комментарии (<span id="commentsCountLabel">3</span>)</h3>

        <form id="commentForm" class="comment-form">
            <textarea name="text" placeholder="Напиши комментарий..." rows="3" required maxlength="1000"></textarea>
            <button type="submit">Отправить</button>
        </form>

        <div class="comments-list" id="commentsList">
            <div class="comment">
                <div class="comment-avatar">A</div>
                <div class="comment-body">
                    <div class="comment-header">
                        <a href="user.html?u=AlexBuilds" class="comment-author">AlexBuilds</a>
                        <span class="comment-date">18.08.2026 14:32</span>
                    </div>
                    <div class="comment-text">Лучший тех-мод этого года. Конвейеры просто летают, а новый интерфейс машин — огонь!</div>
                </div>
            </div>
            <div class="comment">
                <div class="comment-avatar">S</div>
                <div class="comment-body">
                    <div class="comment-header">
                        <a href="user.html?u=SteveCraft" class="comment-author">SteveCraft</a>
                        <span class="comment-date">16.08.2026 09:15</span>
                    </div>
                    <div class="comment-text">Ставил на сервер с 60 модами — конфликтов нет. Автору респект 👏</div>
                </div>
            </div>
            <div class="comment">
                <div class="comment-avatar">V</div>
                <div class="comment-body">
                    <div class="comment-header">
                        <a href="user.html?u=VoidWalker" class="comment-author">VoidWalker</a>
                        <span class="comment-date">13.08.2026 21:47</span>
                    </div>
                    <div class="comment-text">Жду порт на 1.21. А в остальном — стабильно, красиво, удобно.</div>
                </div>
            </div>
        </div>
    </div>
</div>

<div id="lightbox" class="lightbox" onclick="closeLightbox()">
    <img id="lightbox-img" src="" alt="">
    <span class="lightbox-close">&times;</span>
</div>

<!-- Модальное окно скачивания -->
<div id="downloadModal" class="download-modal" onclick="closeDownloadModal(event)">
    <div class="download-modal-content" onclick="event.stopPropagation()">
        <div class="modal-header">
            <h3>⬇ Скачать TechNova</h3>
            <button class="modal-close" onclick="closeDownloadModal(event)">&times;</button>
        </div>
        <div class="modal-body">
            <div class="download-form-group">
                <label for="mcVersionSelect">Версия Minecraft:</label>
                <select id="mcVersionSelect" onchange="updateLoaderOptions()">
                    <option value="">Выберите версию MC</option>
                </select>
            </div>
            <div class="download-form-group">
                <label for="loaderSelect">Загрузчик (Loader):</label>
                <select id="loaderSelect" onchange="updateVersionOptions()" disabled>
                    <option value="">Сначала выберите MC</option>
                </select>
            </div>
            <div class="download-form-group">
                <label for="modVersionSelect">Версия мода:</label>
                <select id="modVersionSelect" disabled>
                    <option value="">Сначала выберите загрузчик</option>
                </select>
            </div>
            <a href="#" id="finalDownloadBtn" class="btn-download-big" style="margin-top:20px" disabled>
                Скачать выбранную версию
            </a>
        </div>
    </div>
</div>
'''
    extra_js = '''<script>
window.MOD_VERSIONS = [
    {mc:'1.20.4', loader:'NeoForge', version:'3.2.0', file:'technova-3.2.0-neoforge.jar'},
    {mc:'1.20.4', loader:'Forge',    version:'3.2.0', file:'technova-3.2.0-forge.jar'},
    {mc:'1.20.1', loader:'Forge',    version:'3.2.0', file:'technova-3.2.0-forge.jar'},
    {mc:'1.20.1', loader:'Fabric',   version:'3.1.4', file:'technova-3.1.4-fabric.jar'},
    {mc:'1.19.2', loader:'Forge',    version:'2.9.7', file:'technova-2.9.7-forge.jar'}
];
</script>'''
    page('mod.html', 'TechNova — MineMods', 'home', content, page_name='mod', extra_js=extra_js)


# ======================================================================
# НОВОСТИ
# ======================================================================
def build_news():
    items = [
        ('15.08.2026 12:00', '✨ MineMods 2.0 уже здесь',
         'Большое обновление платформы: полностью статическая версия сайта, которая работает мгновенно и без сервера. '
         'Новый дизайн, живой поиск по Modrinth и GitHub, а также переключение тем в один клик.'),
        ('08.08.2026 10:30', '🏆 Конкурс модов «Лето 2026»',
         'Запускаем ежегодный конкурс! Загружайте свои моды до 31 августа — авторы трёх лучших работ получат '
         'место на главной странице и уникальный значок профиля.'),
        ('01.08.2026 09:00', '🚀 Открыт раздел шейдеров и ресурспаков',
         'Теперь на MineMods можно публиковать не только моды: шейдеры, ресурспаки, сборки, датапаки и карты. '
         'Выбирайте тип контента при загрузке.'),
        ('20.07.2026 18:45', '🎉 50 000 скачиваний!',
         'Спасибо каждому из вас — вместе мы прошли отметку в 50 тысяч скачиваний модов. Впереди ещё больше '
         'крутого контента и новых функций.'),
        ('05.07.2026 15:20', '🏅 Запущена система достижений',
         'Зарабатывайте награды за активность: публикуйте моды, собирайте лайки и подписчиков. '
         'Всего доступно 15 достижений — соберите их все!'),
    ]
    rows = ''.join('''        <article class="news-item">
            <div class="news-date">%s</div>
            <h2>%s</h2>
            <div class="news-content">%s</div>
        </article>
''' % (d, t, c) for d, t, c in items)
    content = '''
<div class="page-header">
    <div>
        <h1 class="page-title">📰 Новости</h1>
        <p class="page-subtitle">Что нового на MineMods</p>
    </div>
</div>

<div class="news-list">
''' + rows + '''</div>
'''
    page('news.html', 'Новости — MineMods', 'news', content)


# ======================================================================
# ВХОД / РЕГИСТРАЦИЯ
# ======================================================================
def build_auth():
    login = '''
<div class="form-page">
    <div class="form-icon">🔑</div>
    <h2>Вход</h2>
    <p class="form-subtitle">Добро пожаловать обратно!</p>
    <div class="demo-hint">Демо-режим: введи любой ник — он сохранится в браузере (localStorage), сервер не нужен.</div>
    <form id="loginForm">
        <label>Имя пользователя</label>
        <input type="text" name="username" required minlength="3" maxlength="30" autocomplete="username">
        <label>Пароль</label>
        <input type="password" name="password" required autocomplete="current-password">
        <button type="submit">Войти</button>
    </form>
    <p class="form-link">Нет аккаунта? <a href="register.html">Регистрация</a></p>
</div>
'''
    page('login.html', 'Вход — MineMods', '', login)

    register = '''
<div class="form-page">
    <div class="form-icon">📝</div>
    <h2>Регистрация</h2>
    <p class="form-subtitle">Создай аккаунт и публикуй свои моды</p>
    <div class="demo-hint">Демо-режим: аккаунт хранится только в твоём браузере (localStorage).</div>
    <form id="registerForm">
        <label>Имя пользователя</label>
        <input type="text" name="username" placeholder="Например: minecraft_master" required minlength="3" maxlength="30" autocomplete="username">
        <label>Email</label>
        <input type="email" name="email" placeholder="email@example.com" required autocomplete="email">
        <label>Пароль</label>
        <input type="password" name="password" placeholder="Минимум 6 символов" required minlength="6" autocomplete="new-password">
        <button type="submit">Создать аккаунт</button>
    </form>
    <p class="form-link">Уже есть аккаунт? <a href="login.html">Войти</a></p>
</div>
'''
    page('register.html', 'Регистрация — MineMods', '', register)


# ======================================================================
# ЗАГРУЗКА
# ======================================================================
def build_upload():
    tabs = '\n        '.join(
        '<a href="upload.html?type=%s" class="ut-tab" data-type="%s"><span class="ut-icon">%s</span>'
        '<span class="ut-name">%s</span><span class="ut-ext">%s</span></a>' % (k, k, i, n, e)
        for k, n, i, e in UPLOAD_TYPES)
    cat_opts = '\n            '.join('<option value="%s">%s</option>' % (c, c) for c in CATEGORIES)
    ver_opts = '\n            '.join('<option value="%s">%s</option>' % (v, v) for v in MC_VERSIONS)
    content = '''
<div class="form-page form-wide">
    <div class="form-icon">📤</div>
    <h2>Загрузить контент</h2>
    <p class="form-subtitle">Поделись модом, шейдером, картой и др.</p>

    <div class="upload-type-tabs">
        ''' + tabs + '''
    </div>

    <form id="uploadForm">
        <label>Название</label>
        <input type="text" name="title" placeholder="Например: Complementary Shaders" required maxlength="80">

        <label>Описание</label>
        <textarea name="description" placeholder="Расскажи, что это и зачем нужно..." rows="5" required maxlength="1000"></textarea>

        <div class="form-row">
            <div>
                <label>Версия</label>
                <input type="text" name="version" placeholder="1.0.0" required maxlength="20">
            </div>
            <div>
                <label>Версия Minecraft</label>
                <select name="mc_version" required>
                    <option value="">Выбери</option>
                    ''' + ver_opts + '''
                </select>
            </div>
            <div>
                <label>Загрузчик (Loader)</label>
                <select name="loader" required>
                    <option value="">Выбери</option>
                    <option value="Forge">Forge</option>
                    <option value="Fabric">Fabric</option>
                    <option value="Quilt">Quilt</option>
                    <option value="NeoForge">NeoForge</option>
                    <option value="Vanilla">Vanilla</option>
                </select>
            </div>
        </div>

        <label>Категория</label>
        <select name="category" required>
            <option value="">Выбери категорию</option>
            ''' + cat_opts + '''
        </select>

        <label>Теги (через запятую)</label>
        <input type="text" name="tags" placeholder="реализм, оптимизация, RTX, ванильный" maxlength="120">

        <label class="file-label">
            <div class="file-icon">📁</div>
            <div class="file-text">Выбери файл мода</div>
            <div class="file-hint">Демо-режим: файл не отправляется на сервер</div>
            <input type="file" name="mod_file">
        </label>

        <label>📸 Скриншоты (необязательно, до 5)</label>
        <div class="screenshots-upload">
            <label class="ss-upload-box"><span>📷 1</span><input type="file" accept="image/*"></label>
            <label class="ss-upload-box"><span>📷 2</span><input type="file" accept="image/*"></label>
            <label class="ss-upload-box"><span>📷 3</span><input type="file" accept="image/*"></label>
            <label class="ss-upload-box"><span>📷 4</span><input type="file" accept="image/*"></label>
            <label class="ss-upload-box"><span>📷 5</span><input type="file" accept="image/*"></label>
        </div>

        <button type="submit">🚀 Опубликовать</button>
    </form>
</div>
'''
    page('upload.html', 'Загрузить мод — MineMods', 'upload', content, page_name='upload', protected=True)


# ======================================================================
# ПРОФИЛЬ / НАСТРОЙКИ
# ======================================================================
def build_profile():
    content = '''
<div id="profileBox"></div>
'''
    page('profile.html', 'Мой профиль — MineMods', '', content, page_name='profile', protected=True)


def build_settings():
    themes = [('green', 'Зелёный'), ('blue', 'Синий'), ('purple', 'Фиолетовый'), ('orange', 'Оранжевый'),
              ('pink', 'Розовый'), ('light', 'Светлая'), ('amoled', 'AMOLED 🖤')]
    theme_opts = '\n                '.join(
        '''<label class="theme-option theme-%s">
                    <input type="radio" name="theme" value="%s">
                    <div class="theme-preview"><div class="tp-bar"></div><div class="tp-content"></div></div>
                    <div class="theme-name">%s</div>
                </label>''' % (k, k, n) for k, n in themes)
    content = '''
<div class="page-header">
    <div>
        <h1 class="page-title">⚙️ Настройки</h1>
        <p class="page-subtitle">Настрой сайт под себя — всё сохраняется в браузере</p>
    </div>
</div>

<div class="settings-grid">

    <div class="settings-card">
        <h3>🖼️ Аватарка</h3>
        <p class="settings-desc">Загрузи свою аватарку (jpg, png, gif) — хранится локально</p>
        <div class="avatar-upload">
            <div class="current-avatar-letter">👤</div>
            <label class="file-label-small">
                📁 Выбрать файл
                <input type="file" id="avatarInput" accept="image/*">
            </label>
        </div>
    </div>

    <div class="settings-card">
        <h3>🎨 Тема оформления</h3>
        <p class="settings-desc">Применяется мгновенно и запоминается</p>
        <div class="theme-grid" id="themeGrid">
                ''' + theme_opts + '''
        </div>
    </div>

    <div class="settings-card">
        <h3>✨ Анимации</h3>
        <p class="settings-desc">Включи или выключи анимации интерфейса</p>
        <label class="switch-row">
            <span>Анимации интерфейса</span>
            <label class="switch">
                <input type="checkbox" id="animToggle" checked>
                <span class="slider"></span>
            </label>
        </label>
    </div>

    <div class="settings-card">
        <h3>👤 Профиль</h3>
        <p class="settings-desc">Информация о тебе</p>
        <form id="profileForm">
            <label>Email</label>
            <input type="email" name="email" placeholder="email@example.com">
            <label>О себе</label>
            <textarea name="bio" rows="3" maxlength="300" placeholder="Расскажи о себе..."></textarea>
            <button type="submit" class="btn-save">Сохранить профиль</button>
        </form>
    </div>

    <div class="settings-card">
        <h3>🔒 Пароль</h3>
        <p class="settings-desc">Смени пароль для безопасности</p>
        <form id="passwordForm">
            <label>Текущий пароль</label>
            <input type="password" name="old_password" required>
            <label>Новый пароль</label>
            <input type="password" name="new_password" required minlength="6">
            <button type="submit" class="btn-save">Изменить пароль</button>
        </form>
    </div>

</div>
'''
    page('settings.html', 'Настройки — MineMods', '', content, page_name='settings', protected=True)


# ======================================================================
# ИЗБРАННОЕ / ЛЕНТА / ДОСТИЖЕНИЯ
# ======================================================================
def build_favorites():
    content = '''
<div class="page-header">
    <div>
        <h1 class="page-title">❤️ Избранное</h1>
        <p class="page-subtitle">Моды, которые ты лайкнул</p>
    </div>
    <div class="stats-mini">
        <div class="stat-mini">
            <div class="stat-num" id="favCount">0</div>
            <div class="stat-label">Модов</div>
        </div>
    </div>
</div>

<div class="mods-grid" id="favGrid"></div>
'''
    page('favorites.html', 'Избранное — MineMods', 'favorites', content, page_name='favorites', protected=True)


def build_feed():
    content = '''
<div class="page-header">
    <div>
        <h1 class="page-title">📡 Лента подписок</h1>
        <p class="page-subtitle">Новые моды от авторов, на которых ты подписан</p>
    </div>
    <div class="stats-mini">
        <div class="stat-mini">
            <div class="stat-num" id="feedCount">0</div>
            <div class="stat-label">Модов</div>
        </div>
    </div>
</div>

<div class="mods-grid" id="feedGrid"></div>
'''
    page('feed.html', 'Лента подписок — MineMods', 'feed', content, page_name='feed', protected=True)


def build_achievements():
    content = '''
<div class="page-header">
    <div>
        <h1 class="page-title">🏅 Достижения</h1>
        <p class="page-subtitle" id="achSubtitle">Получено 0 из 15</p>
    </div>
    <div class="stats-mini">
        <div class="stat-mini">
            <div class="stat-num" id="achProgress">0%</div>
            <div class="stat-label">Прогресс</div>
        </div>
    </div>
</div>

<div class="achievements-grid" id="achGrid"></div>
'''
    page('achievements.html', 'Достижения — MineMods', 'achievements', content, page_name='achievements', protected=True)


# ======================================================================
# СООБЩЕНИЯ / ЧАТ / УВЕДОМЛЕНИЯ
# ======================================================================
def build_messages():
    content = '''
<div class="page-header">
    <div>
        <h1 class="page-title">💌 Сообщения</h1>
        <p class="page-subtitle">Личные сообщения</p>
    </div>
</div>

<div class="chats-list">
    <a href="chat.html?u=MageCraft" class="chat-item">
        <div class="chat-avatar-letter">M</div>
        <div class="chat-info">
            <div class="chat-name">MageCraft</div>
            <div class="chat-last">Спасибо за отзыв о моде!</div>
        </div>
        <div class="chat-meta">
            <div class="chat-date">19.08 20:14</div>
            <div class="chat-unread">1</div>
        </div>
    </a>
    <a href="chat.html?u=SteveCraft" class="chat-item">
        <div class="chat-avatar-letter">S</div>
        <div class="chat-info">
            <div class="chat-name">SteveCraft</div>
            <div class="chat-last">Вы: Когда обновление Sky Village?</div>
        </div>
        <div class="chat-meta">
            <div class="chat-date">18.08 16:40</div>
        </div>
    </a>
    <a href="chat.html?u=VoidWalker" class="chat-item">
        <div class="chat-avatar-letter">V</div>
        <div class="chat-info">
            <div class="chat-name">VoidWalker</div>
            <div class="chat-last">Измерение Туманностей почти готово 🌌</div>
        </div>
        <div class="chat-meta">
            <div class="chat-date">17.08 11:02</div>
        </div>
    </a>
</div>
'''
    page('messages.html', 'Сообщения — MineMods', '', content, protected=True)


def build_chat():
    content = '''
<div class="chat-header">
    <a href="messages.html" class="back-btn">← Назад</a>
    <div class="chat-user">
        <div class="chat-avatar-letter" id="chatAvatar">A</div>
        <a href="user.html" class="chat-username" id="chatUserLink"><span id="chatUsername">AlexBuilds</span></a>
    </div>
</div>

<div class="chat-messages" id="chatMessages"></div>

<form id="chatForm" class="chat-form">
    <input type="text" name="text" placeholder="Написать сообщение..." required maxlength="2000" autocomplete="off">
    <button type="submit">📤</button>
</form>
'''
    page('chat.html', 'Чат — MineMods', '', content, page_name='chat', protected=True)


def build_notifications():
    content = '''
<div class="page-header">
    <div>
        <h1 class="page-title">🔔 Уведомления</h1>
        <p class="page-subtitle">Все события на твоём аккаунте</p>
    </div>
    <div class="page-actions">
        <button class="btn-save" id="markAllRead">✔ Прочитать все</button>
    </div>
</div>

<div class="notifications-list">
    <a href="mod.html" class="notif new">
        <div class="notif-icon">❤️</div>
        <div class="notif-body">
            <div class="notif-text">SteveCraft лайкнул твой мод</div>
            <div class="notif-date">20.08.2026 09:12</div>
        </div>
    </a>
    <a href="mod.html#comments" class="notif new">
        <div class="notif-icon">💬</div>
        <div class="notif-body">
            <div class="notif-text">AlexBuilds прокомментировал: «Отличная работа, жду обновлений!»</div>
            <div class="notif-date">19.08.2026 22:41</div>
        </div>
    </a>
    <a href="user.html?u=MageCraft" class="notif">
        <div class="notif-icon">🔔</div>
        <div class="notif-body">
            <div class="notif-text">На тебя подписался MageCraft</div>
            <div class="notif-date">19.08.2026 15:03</div>
        </div>
    </a>
    <a href="feed.html" class="notif">
        <div class="notif-icon">🆕</div>
        <div class="notif-body">
            <div class="notif-text">SteveCraft опубликовал новый мод «Sky Village v2.2.0»</div>
            <div class="notif-date">15.08.2026 11:30</div>
        </div>
    </a>
    <a href="messages.html" class="notif">
        <div class="notif-icon">💌</div>
        <div class="notif-body">
            <div class="notif-text">Новое сообщение от VoidWalker</div>
            <div class="notif-date">14.08.2026 18:56</div>
        </div>
    </a>
</div>
'''
    page('notifications.html', 'Уведомления — MineMods', '', content, page_name='notifications', protected=True)


# ======================================================================
# ПОЛЬЗОВАТЕЛЬ / АКТИВНОСТЬ
# ======================================================================
def build_user():
    content = '''
<div id="userBox"></div>
'''
    page('user.html', 'Пользователь — MineMods', '', content, page_name='user')


def build_activity():
    content = '''
<div class="page-header">
    <div>
        <h1 class="page-title">📅 Активность</h1>
        <p class="page-subtitle">Последние события</p>
    </div>
</div>

<div class="activity-list" id="activityList"></div>
'''
    page('activity.html', 'Активность — MineMods', '', content, page_name='activity')


# ======================================================================
# MODRINTH (живой поиск)
# ======================================================================
def build_modrinth():
    types = [('mod', '⛏', 'Моды'), ('shader', '🌅', 'Шейдеры'), ('plugin', '🔌', 'Плагины'),
             ('resourcepack', '🎨', 'Ресурспаки'), ('modpack', '📦', 'Сборки'), ('datapack', '📝', 'Датапаки')]
    tabs = '\n        '.join(
        '<a href="#" class="ct-tab%s" data-type="%s"><span class="ct-icon">%s</span><span>%s</span></a>'
        % (' active' if k == 'mod' else '', k, i, n) for k, i, n in types)
    mr_cats = [('optimization', 'Оптимизация'), ('adventure', 'Приключения'), ('cursed', 'Cursed'),
               ('decoration', 'Декор'), ('equipment', 'Снаряжение'), ('food', 'Еда'),
               ('library', 'Библиотека'), ('magic', 'Магия'), ('mobs', 'Мобы'),
               ('storage', 'Хранилища'), ('technology', 'Технологии'), ('utility', 'Утилиты'),
               ('worldgen', 'Генерация мира')]
    cat_opts = '\n            '.join('<option value="%s">%s</option>' % (s, n) for s, n in mr_cats)
    ver_opts = '\n            '.join('<option value="%s">%s</option>' % (v, v) for v in MC_VERSIONS[:10])
    content = '''
<div class="content-type-tabs mr-type-tabs">
        ''' + tabs + '''
</div>

<div class="modrinth-header">
    <div class="modrinth-logo">
        <div class="mr-logo-icon">🌍</div>
        <div>
            <h1>Modrinth</h1>
            <p>Поиск по миллионам модов — данные загружаются напрямую с API Modrinth</p>
        </div>
    </div>
    <div class="modrinth-stats" id="mrTotal">…</div>
</div>

<div class="search-bar">
    <form id="mrForm" method="GET">
        <div class="search-input-wrap">
            <span class="search-icon">🔍</span>
            <input type="text" id="mrQ" name="q" placeholder="Поиск модов на Modrinth..." autocomplete="off">
        </div>
        <select id="mrCat" name="category">
            <option value="">Все категории</option>
            ''' + cat_opts + '''
        </select>
        <select id="mrVer" name="mc_version">
            <option value="">Все версии MC</option>
            ''' + ver_opts + '''
        </select>
        <button type="submit">Найти</button>
    </form>
</div>

<div class="sort-tabs">
    <button class="sort-tab active" data-sort="relevance">🎯 Релевантность</button>
    <button class="sort-tab" data-sort="downloads">🔥 Скачивания</button>
    <button class="sort-tab" data-sort="follow_count">⭐ Подписчики</button>
    <button class="sort-tab" data-sort="newest">🆕 Новые</button>
    <button class="sort-tab" data-sort="updated">🔄 Обновлённые</button>
</div>

<div class="modrinth-grid" id="mrResults"></div>
<div class="pagination" id="mrPagination"></div>

<div class="modrinth-credits">
    Данные предоставлены <a href="https://modrinth.com" target="_blank" rel="noopener">Modrinth</a>
</div>
'''
    page('modrinth.html', 'Modrinth — MineMods', 'modrinth', content, page_name='modrinth')


# ======================================================================
# GITHUB (живой поиск)
# ======================================================================
def build_github():
    types = [('mod', '⛏', 'Моды'), ('shader', '🌅', 'Шейдеры'), ('plugin', '🔌', 'Плагины'),
             ('resourcepack', '🎨', 'Ресурспаки'), ('modpack', '📦', 'Сборки'),
             ('datapack', '📝', 'Датапаки'), ('map', '🗺️', 'Карты')]
    tabs = '\n        '.join(
        '<a href="#" class="ct-tab%s" data-type="%s"><span class="ct-icon">%s</span><span>%s</span></a>'
        % (' active' if k == 'mod' else '', k, i, n) for k, i, n in types)
    content = '''
<div class="content-type-tabs mr-type-tabs">
        ''' + tabs + '''
</div>

<div class="github-header">
    <div class="gh-logo">
        <div class="gh-logo-icon">🦊</div>
        <div>
            <h1>GitHub</h1>
            <p>Open-source проекты Minecraft — данные с API GitHub</p>
        </div>
    </div>
    <div class="gh-stats" id="ghTotal">…</div>
</div>

<div class="search-bar">
    <form id="ghForm" method="GET">
        <div class="search-input-wrap">
            <span class="search-icon">🔍</span>
            <input type="text" id="ghQ" name="q" placeholder="Поиск (например: sodium, complementary, essentials)..." autocomplete="off">
        </div>
        <button type="submit">Найти</button>
    </form>
</div>

<div class="sort-tabs">
    <button class="sort-tab active" data-sort="stars">⭐ Звёзды</button>
    <button class="sort-tab" data-sort="forks">🍴 Форки</button>
    <button class="sort-tab" data-sort="updated">🔄 Обновлённые</button>
</div>

<div class="modrinth-grid" id="ghResults"></div>
<div class="pagination" id="ghPagination"></div>

<div class="modrinth-credits">
    Данные предоставлены <a href="https://github.com" target="_blank" rel="noopener">GitHub</a>
</div>
'''
    page('github.html', 'GitHub — MineMods', 'github', content, page_name='github')


# ======================================================================
def main():
    build_index()
    build_mod()
    build_news()
    build_auth()
    build_upload()
    build_profile()
    build_settings()
    build_favorites()
    build_feed()
    build_achievements()
    build_messages()
    build_chat()
    build_notifications()
    build_user()
    build_activity()
    build_modrinth()
    build_github()
    copy_assets()
    print('\nГотово! Статический сайт собран в папке docs/ (отдельно от всего проекта).')
    print('Открой docs/index.html в браузере или запусти:  cd docs && python3 -m http.server')


if __name__ == '__main__':
    main()
