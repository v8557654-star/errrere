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
    ('mod', 'Мод', 'package', '.jar'), ('shader', 'Шейдер', 'image', '.zip'),
    ('plugin', 'Плагин', 'zap', '.jar'), ('resourcepack', 'Ресурспак', 'image', '.zip'),
    ('modpack', 'Сборка', 'package', '.zip / .mrpack'), ('datapack', 'Датапак', 'file', '.zip'),
    ('map', 'Карта', 'globe', '.zip'),
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

# ---------------- SVG-иконки интерфейса (контурные, стиль Lucide/Feather) ----------------
_ICONS = {
    'home': '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    'news': '<path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-4 0V9"/><line x1="18" y1="14" x2="12" y2="14"/><line x1="18" y1="18" x2="12" y2="18"/><line x1="10" y1="6" x2="18" y2="6"/><line x1="18" y1="10" x2="10" y2="10"/>',
    'globe': '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    'github_fill': 'M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12',
    'rss': '<path d="M4 11a9 9 0 0 1 9 9"/><path d="M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="2"/>',
    'heart': '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>',
    'upload': '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>',
    'trophy': '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2z"/>',
    'bell': '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/>',
    'mail': '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
    'user': '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    'settings': '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    'calendar': '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    'search': '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    'download': '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    'eye': '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    'star': '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    'message': '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>',
    'tag': '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>',
    'x': '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
    'chevron': '<polyline points="6 9 12 15 18 9"/>',
    'arrow_right': '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
    'package': '<path d="M16.5 9.4 7.55 4.24"/><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
    'cube': '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><path d="M3.3 7 12 12l8.7-5"/><path d="M12 22V12"/>',
    'clock': '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    'camera': '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/>',
    'image': '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>',
    'zap': '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    'flame': '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    'sparkles': '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3z"/>',
    'shield': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    'lock': '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    'send': '<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>',
    'key': '<path d="m21 2-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0 3 3L22 7l-3-3m-3.5 3.5L19 4"/>',
    'edit': '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>',
    'file': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
    'target': '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    'refresh': '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
    'fork': '<circle cx="12" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><circle cx="18" cy="6" r="3"/><path d="M18 9v2c0 .6-.4 1-1 1H7c-.6 0-1-.4-1-1V9"/><path d="M12 12v3"/>',
    'check': '<polyline points="20 6 9 17 4 12"/>',
}
_FILL = {'github_fill'}


def ic(name, cls=''):
    """Inline SVG-иконка для статической вёрстки."""
    body = _ICONS[name]
    fill = name in _FILL
    inner = '<path d="%s"/>' % body if fill else body
    attrs = 'fill="currentColor"' if fill else 'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    return '<svg class="ic %s" viewBox="0 0 24 24" %s aria-hidden="true">%s</svg>' % (cls, attrs, inner)


NAV = [
    ('home', 'index.html', 'home', 'Каталог', False),
    ('news', 'news.html', 'news', 'Новости', False),
    ('modrinth', 'modrinth.html', 'globe', 'Modrinth', False),
    ('github', 'github.html', 'github_fill', 'GitHub', False),
    ('feed', 'feed.html', 'rss', 'Подписки', True),
    ('favorites', 'favorites.html', 'heart', 'Избранное', True),
    ('upload', 'upload.html', 'upload', 'Загрузить', True),
    ('achievements', 'achievements.html', 'trophy', 'Достижения', True),
]

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2322ff88' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E"
           "%3Cpath d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'/%3E"
           "%3Cpath d='M3.3 7 12 12l8.7-5'/%3E%3Cpath d='M12 22V12'/%3E%3C/svg%3E")

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
                <span class="logo-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#22ff88" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><path d="M3.3 7 12 12l8.7-5"/><path d="M12 22V12"/></svg></span>
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
            <button class="mobile-menu-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')" aria-label="Меню"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg></button>
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
    for key, href, icon_name, label, auth in NAV:
        cls = 'nav-item' + (' active' if key == active else '')
        style = ' class="%s"' % cls
        extra = ' style="display:none" class="nav-item auth-only"' if auth else style
        svg = ic(icon_name)
        if auth:
            rows.append('            <a href="%s"%s><span class="nav-icon" aria-hidden="true">%s</span><span>%s</span></a>'
                        % (href, extra, svg, label))
        else:
            rows.append('            <a href="%s"%s><span class="nav-icon" aria-hidden="true">%s</span><span>%s</span></a>'
                        % (href, style, svg, label))
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
            <p class="mod-meta"><span>v{version}</span> <span>•</span> <span><a href="user.html?u={author}" class="author-link">{ic_user} {author}</a></span></p>
            <p class="mod-desc">{desc}</p>
            <div class="mod-tags">{tags_h}</div>
            <div class="mod-footer">
                <div class="mod-stats">
                    <span class="stat-item">{ic_dl} {downloads}</span>
                    <span class="stat-item">{ic_heart} {likes}</span>
                    <span class="stat-item">{ic_eye} {views}</span>
                </div>
                <a href="mod.html?m={id}#download" class="btn-download">{ic_dl} Скачать</a>
            </div>
        </div>'''.format(tags_flat=' '.join(m['tags']), tags_h=tags_h,
                          ic_dl=ic('download', 'ic-sm'), ic_heart=ic('heart', 'ic-sm'), ic_eye=ic('eye', 'ic-sm'),
                          ic_user=ic('user', 'ic-sm'), **m)


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
                    <span>{ic_dl} {downloads}</span>
                    <span>{ic_heart} {likes}</span>
                    <span>{ic_eye} {views}</span>
                </div>
            </div>
        </a>
'''.format(i=i, ic_dl=ic('download', 'ic-sm'), ic_heart=ic('heart', 'ic-sm'), ic_eye=ic('eye', 'ic-sm'), **m)

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
    <div class="hero-blocks" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span></div>
    <h1 class="hero-title">Лучшие моды для Minecraft</h1>
    <p class="hero-subtitle">
        Откройте для себя тысячи модов, улучшающих ваш игровой опыт.
        От технологических чудес до магических приключений.
    </p>
    <div class="hero-actions">
        <a href="#mods" class="btn-hero btn-hero-primary">''' + ic('package') + ''' Смотреть моды</a>
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
    <h3>''' + ic('news') + ''' Последние новости</h3>
    <div class="news-strip">
        <a href="news.html" class="news-pill"><strong>MineMods 2.0 уже здесь</strong><span>15.08</span></a>
        <a href="news.html" class="news-pill"><strong>Конкурс модов — август</strong><span>08.08</span></a>
        <a href="news.html" class="news-pill"><strong>Новый раздел шейдеров</strong><span>01.08</span></a>
        <a href="news.html" class="news-all">Все ''' + ic('arrow_right', 'ic-sm') + '''</a>
    </div>
</div>

<div class="top-section animate-fade-in-up">
    <h2 class="section-title">''' + ic('trophy') + ''' Топ модов</h2>
    <div class="top-grid">
''' + top_cards + '''    </div>
</div>

<!-- Поиск и фильтры -->
<section class="mb-12 animate-fade-in-up">
    <div class="search-bar">
        <form id="modFilterForm" method="GET" action="#mods">
            <div class="search-input-wrap">
                <span class="search-icon">''' + ic('search') + '''</span>
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
    <button class="sort-tab active" data-sort="new">''' + ic('sparkles', 'ic-sm') + ''' Новые</button>
    <button class="sort-tab" data-sort="popular">''' + ic('flame', 'ic-sm') + ''' Популярные</button>
    <button class="sort-tab" data-sort="top">''' + ic('star', 'ic-sm') + ''' Лучшие</button>
    <button class="sort-tab" data-sort="views">''' + ic('eye', 'ic-sm') + ''' Просмотры</button>
</div>

<!-- Каталог -->
<section id="mods" class="mb-16">
    <h2 class="section-heading">''' + ic('package') + ''' Каталог модов</h2>
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
                <div class="feature-icon">''' + ic('zap') + '''</div>
                <h3>Быстрая загрузка</h3>
                <p>Оптимизированная система доставки файлов обеспечивает максимальную скорость скачивания.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">''' + ic('shield') + '''</div>
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
        <details class="faq-item" open>
            <summary><span>Как установить мод?</span><span class="faq-arrow">''' + ic('chevron', 'ic-sm') + '''</span></summary>
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
            <summary><span>Какие версии Minecraft поддерживаются?</span><span class="faq-arrow">''' + ic('chevron', 'ic-sm') + '''</span></summary>
            <div class="faq-body">
                Мы поддерживаем версии от 1.16.5 до последних релизов 1.21+. Каждый мод указывает совместимые версии в описании.
            </div>
        </details>
        <details class="faq-item">
            <summary><span>Безопасно ли скачивать моды здесь?</span><span class="faq-arrow">''' + ic('chevron', 'ic-sm') + '''</span></summary>
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
            <span><a href="user.html?u=TechWizard" class="author-link">''' + ic('user', 'ic-sm') + ''' TechWizard</a></span>
            <span>''' + ic('calendar', 'ic-sm') + ''' 12.08.2026</span>
            <span>''' + ic('download', 'ic-sm') + ''' <span id="dlCount" data-n="12840">12 840</span></span>
            <span>''' + ic('heart', 'ic-sm') + ''' 932</span>
            <span>''' + ic('eye', 'ic-sm') + ''' 40 210</span>
            <span>''' + ic('message', 'ic-sm') + ''' <span id="commentsCount">3</span></span>
        </div>
    </div>

    <div class="screenshots-section">
        <h3>''' + ic('camera') + ''' Скриншоты</h3>
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
                <h3>''' + ic('tag') + ''' Теги</h3>
                <div class="tags-row">
                    <span class="tag">#техника</span>
                    <span class="tag">#автоматизация</span>
                    <span class="tag">#энергия</span>
                </div>
            </div>

            <div class="mod-description">
                <h3>''' + ic('file') + ''' Описание</h3>
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
            <button onclick="openDownloadModal()" class="btn-download-big">''' + ic('download', 'ic-sm') + ''' Скачать .jar</button>
            <button class="btn-like" id="likeBtn">
                <span class="like-icon">''' + ic('heart') + '''</span>
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
        <h3>''' + ic('message') + ''' Комментарии (<span id="commentsCountLabel">3</span>)</h3>

        <form id="commentForm" class="comment-form">
            <textarea name="text" placeholder="Напиши комментарий..." rows="3" required maxlength="1000"></textarea>
            <button type="submit">''' + ic('send', 'ic-sm') + ''' Отправить</button>
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
            <h3>''' + ic('download') + ''' Скачать TechNova</h3>
            <button class="modal-close" onclick="closeDownloadModal(event)">''' + ic('x') + '''</button>
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
        ('15.08.2026 12:00', 'MineMods 2.0 уже здесь',
         'Большое обновление платформы: полностью статическая версия сайта, которая работает мгновенно и без сервера. '
         'Новый дизайн с SVG-иконками, скачивание модов с Modrinth прямо на сайте, живой поиск по Modrinth и GitHub.'),
        ('08.08.2026 10:30', 'Конкурс модов «Лето 2026»',
         'Запускаем ежегодный конкурс! Загружайте свои моды до 31 августа — авторы трёх лучших работ получат '
         'место на главной странице и уникальный значок профиля.'),
        ('01.08.2026 09:00', 'Открыт раздел шейдеров и ресурспаков',
         'Теперь на MineMods можно публиковать не только моды: шейдеры, ресурспаки, сборки, датапаки и карты. '
         'Выбирайте тип контента при загрузке.'),
        ('20.07.2026 18:45', '50 000 скачиваний!',
         'Спасибо каждому из вас — вместе мы прошли отметку в 50 тысяч скачиваний модов. Впереди ещё больше '
         'крутого контента и новых функций.'),
        ('05.07.2026 15:20', 'Запущена система достижений',
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
        <h1 class="page-title">''' + ic('news') + ''' Новости</h1>
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
    <div class="form-icon">''' + ic('key') + '''</div>
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
    <div class="form-icon">''' + ic('edit') + '''</div>
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
        '<span class="ut-name">%s</span><span class="ut-ext">%s</span></a>' % (k, k, ic(i), n, e)
        for k, n, i, e in UPLOAD_TYPES)
    cat_opts = '\n            '.join('<option value="%s">%s</option>' % (c, c) for c in CATEGORIES)
    ver_opts = '\n            '.join('<option value="%s">%s</option>' % (v, v) for v in MC_VERSIONS)
    content = '''
<div class="form-page form-wide">
    <div class="form-icon">''' + ic('upload') + '''</div>
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
            <div class="file-icon">''' + ic('file') + '''</div>
            <div class="file-text">Выбери файл мода</div>
            <div class="file-hint">Демо-режим: файл не отправляется на сервер</div>
            <input type="file" name="mod_file">
        </label>

        <label>''' + ic('camera', 'ic-sm') + ''' Скриншоты (необязательно, до 5)</label>
        <div class="screenshots-upload">
            <label class="ss-upload-box"><span>📷 1</span><input type="file" accept="image/*"></label>
            <label class="ss-upload-box"><span>📷 2</span><input type="file" accept="image/*"></label>
            <label class="ss-upload-box"><span>📷 3</span><input type="file" accept="image/*"></label>
            <label class="ss-upload-box"><span>📷 4</span><input type="file" accept="image/*"></label>
            <label class="ss-upload-box"><span>📷 5</span><input type="file" accept="image/*"></label>
        </div>

        <button type="submit">''' + ic('zap', 'ic-sm') + ''' Опубликовать</button>
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
        <h1 class="page-title">''' + ic('settings') + ''' Настройки</h1>
        <p class="page-subtitle">Настрой сайт под себя — всё сохраняется в браузере</p>
    </div>
</div>

<div class="settings-grid">

    <div class="settings-card">
        <h3>''' + ic('image') + ''' Аватарка</h3>
        <p class="settings-desc">Загрузи свою аватарку (jpg, png, gif) — хранится локально</p>
        <div class="avatar-upload">
            <div class="current-avatar-letter">''' + ic('user') + '''</div>
            <label class="file-label-small">
                ''' + ic('image', 'ic-sm') + ''' Выбрать файл
                <input type="file" id="avatarInput" accept="image/*">
            </label>
        </div>
    </div>

    <div class="settings-card">
        <h3>''' + ic('sparkles') + ''' Тема оформления</h3>
        <p class="settings-desc">Применяется мгновенно и запоминается</p>
        <div class="theme-grid" id="themeGrid">
                ''' + theme_opts + '''
        </div>
    </div>

    <div class="settings-card">
        <h3>''' + ic('zap') + ''' Анимации</h3>
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
        <h3>''' + ic('user') + ''' Профиль</h3>
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
        <h3>''' + ic('lock') + ''' Пароль</h3>
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
        <h1 class="page-title">''' + ic('heart') + ''' Избранное</h1>
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
        <h1 class="page-title">''' + ic('rss') + ''' Лента подписок</h1>
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
        <h1 class="page-title">''' + ic('trophy') + ''' Достижения</h1>
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
        <h1 class="page-title">''' + ic('mail') + ''' Сообщения</h1>
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
    <button type="submit">''' + ic('send') + '''</button>
</form>
'''
    page('chat.html', 'Чат — MineMods', '', content, page_name='chat', protected=True)


def build_notifications():
    content = '''
<div class="page-header">
    <div>
        <h1 class="page-title">''' + ic('bell') + ''' Уведомления</h1>
        <p class="page-subtitle">Все события на твоём аккаунте</p>
    </div>
    <div class="page-actions">
        <button class="btn-save" id="markAllRead">''' + ic('check', 'ic-sm') + ''' Прочитать все</button>
    </div>
</div>

<div class="notifications-list">
    <a href="mod.html" class="notif new">
        <div class="notif-icon n-like">''' + ic('heart') + '''</div>
        <div class="notif-body">
            <div class="notif-text">SteveCraft лайкнул твой мод</div>
            <div class="notif-date">20.08.2026 09:12</div>
        </div>
    </a>
    <a href="mod.html#comments" class="notif new">
        <div class="notif-icon n-comment">''' + ic('message') + '''</div>
        <div class="notif-body">
            <div class="notif-text">AlexBuilds прокомментировал: «Отличная работа, жду обновлений!»</div>
            <div class="notif-date">19.08.2026 22:41</div>
        </div>
    </a>
    <a href="user.html?u=MageCraft" class="notif">
        <div class="notif-icon n-sub">''' + ic('bell') + '''</div>
        <div class="notif-body">
            <div class="notif-text">На тебя подписался MageCraft</div>
            <div class="notif-date">19.08.2026 15:03</div>
        </div>
    </a>
    <a href="feed.html" class="notif">
        <div class="notif-icon n-new">''' + ic('sparkles') + '''</div>
        <div class="notif-body">
            <div class="notif-text">SteveCraft опубликовал новый мод «Sky Village v2.2.0»</div>
            <div class="notif-date">15.08.2026 11:30</div>
        </div>
    </a>
    <a href="messages.html" class="notif">
        <div class="notif-icon n-msg">''' + ic('mail') + '''</div>
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
        <h1 class="page-title">''' + ic('calendar') + ''' Активность</h1>
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
    mr_cats = [('optimization', 'Оптимизация'), ('adventure', 'Приключения'), ('cursed', 'Cursed'),
               ('decoration', 'Декор'), ('equipment', 'Снаряжение'), ('food', 'Еда'),
               ('library', 'Библиотека'), ('magic', 'Магия'), ('mobs', 'Мобы'),
               ('storage', 'Хранилища'), ('technology', 'Технологии'), ('utility', 'Утилиты'),
               ('worldgen', 'Генерация мира')]
    types = [('mod', 'package', 'Моды'), ('shader', 'image', 'Шейдеры'), ('plugin', 'zap', 'Плагины'),
             ('resourcepack', 'image', 'Ресурспаки'), ('modpack', 'package', 'Сборки'), ('datapack', 'file', 'Датапаки')]
    tabs = '\n        '.join(
        '<a href="#" class="ct-tab%s" data-type="%s"><span class="ct-icon">%s</span><span>%s</span></a>'
        % (' active' if k == 'mod' else '', k, ic(i), n) for k, i, n in types)
    cat_opts = '\n            '.join('<option value="%s">%s</option>' % (s, n) for s, n in mr_cats)
    ver_opts = '\n            '.join('<option value="%s">%s</option>' % (v, v) for v in MC_VERSIONS[:10])
    content = '''
<div class="content-type-tabs mr-type-tabs">
        ''' + tabs + '''
</div>

<div class="modrinth-header">
    <div class="modrinth-logo">
        <div class="mr-logo-icon">''' + ic('globe') + '''</div>
        <div>
            <h1>Modrinth</h1>
            <p>Поиск по миллионам модов — скачивание прямо на сайте</p>
        </div>
    </div>
    <div class="modrinth-stats" id="mrTotal">…</div>
</div>

<div class="search-bar">
    <form id="mrForm" method="GET">
        <div class="search-input-wrap">
            <span class="search-icon">''' + ic('search') + '''</span>
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
    <button class="sort-tab active" data-sort="relevance">''' + ic('target', 'ic-sm') + ''' Релевантность</button>
    <button class="sort-tab" data-sort="downloads">''' + ic('download', 'ic-sm') + ''' Скачивания</button>
    <button class="sort-tab" data-sort="follow_count">''' + ic('star', 'ic-sm') + ''' Подписчики</button>
    <button class="sort-tab" data-sort="newest">''' + ic('sparkles', 'ic-sm') + ''' Новые</button>
    <button class="sort-tab" data-sort="updated">''' + ic('refresh', 'ic-sm') + ''' Обновлённые</button>
</div>

<div class="modrinth-grid" id="mrResults"></div>
<div class="pagination" id="mrPagination"></div>

<div class="modrinth-credits">
    Данные предоставлены <a href="https://modrinth.com" target="_blank" rel="noopener">Modrinth</a>
    <span class="credits-sep">•</span> файлы скачиваются напрямую с CDN Modrinth
</div>
'''
    page('modrinth.html', 'Modrinth — MineMods', 'modrinth', content, page_name='modrinth')


# ======================================================================
# СТРАНИЦА ПРОЕКТА MODRINTH (скачивание версий прямо на сайте)
# ======================================================================
def build_modrinth_project():
    content = '''
<div id="mrpBox"></div>

<div class="mrp-versions" id="mrpVersionsWrap">
    <div class="mrp-ver-header">
        <h2 class="section-title" style="text-align:left;margin-bottom:0">''' + ic('download') + ''' Версии — скачать прямо с сайта</h2>
        <div class="stats-mini">
            <div class="stat-mini">
                <div class="stat-num" id="mrpVerCount">0</div>
                <div class="stat-label">версий</div>
            </div>
        </div>
    </div>
    <div class="mrp-filters">
        <select id="mrpMc"><option value="">Все версии MC</option></select>
        <select id="mrpLoader"><option value="">Все загрузчики</option></select>
    </div>
    <div class="ver-list" id="mrpVersions"></div>
</div>

<div id="lightbox" class="lightbox" onclick="closeLightbox()">
    <img id="lightbox-img" src="" alt="">
    <span class="lightbox-close">&times;</span>
</div>

<div class="modrinth-credits">
    Данные и файлы предоставлены <a href="https://modrinth.com" target="_blank" rel="noopener">Modrinth</a>
</div>
'''
    page('modrinth-project.html', 'Проект Modrinth — MineMods', 'modrinth', content, page_name='mrproject')


# ======================================================================
# GITHUB (живой поиск)
# ======================================================================
def build_github():
    types = [('mod', 'package', 'Моды'), ('shader', 'image', 'Шейдеры'), ('plugin', 'zap', 'Плагины'),
             ('resourcepack', 'image', 'Ресурспаки'), ('modpack', 'package', 'Сборки'),
             ('datapack', 'file', 'Датапаки'), ('map', 'globe', 'Карты')]
    tabs = '\n        '.join(
        '<a href="#" class="ct-tab%s" data-type="%s"><span class="ct-icon">%s</span><span>%s</span></a>'
        % (' active' if k == 'mod' else '', k, ic(i), n) for k, i, n in types)
    content = '''
<div class="content-type-tabs mr-type-tabs">
        ''' + tabs + '''
</div>

<div class="github-header">
    <div class="gh-logo">
        <div class="gh-logo-icon">''' + ic('github_fill') + '''</div>
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
            <span class="search-icon">''' + ic('search') + '''</span>
            <input type="text" id="ghQ" name="q" placeholder="Поиск (например: sodium, complementary, essentials)..." autocomplete="off">
        </div>
        <button type="submit">Найти</button>
    </form>
</div>

<div class="sort-tabs">
    <button class="sort-tab active" data-sort="stars">''' + ic('star', 'ic-sm') + ''' Звёзды</button>
    <button class="sort-tab" data-sort="forks">''' + ic('fork', 'ic-sm') + ''' Форки</button>
    <button class="sort-tab" data-sort="updated">''' + ic('refresh', 'ic-sm') + ''' Обновлённые</button>
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
    build_modrinth_project()
    build_github()
    copy_assets()
    print('\nГотово! Статический сайт собран в папке docs/ (отдельно от всего проекта).')
    print('Открой docs/index.html в браузере или запусти:  cd docs && python3 -m http.server')


if __name__ == '__main__':
    main()
