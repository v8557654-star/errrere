/* ============================================================
 * MineMods — статическая версия сайта (HTML/CSS/JS, без сервера)
 * Общая логика: демо-авторизация (localStorage), темы, каталог,
 * лайки/подписки, живой поиск по Modrinth и GitHub.
 * ============================================================ */
(function () {
    'use strict';

    var MM = window.MM = {};

    /* ---------------- Helpers ---------------- */
    MM.$  = function (s, r) { return (r || document).querySelector(s); };
    MM.$$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
    MM.get = function (k, d) {
        try { var v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); }
        catch (e) { return d; }
    };
    MM.set = function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} };
    MM.del = function (k)    { try { localStorage.removeItem(k); } catch (e) {} };
    MM.esc = function (s) {
        return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    };
    MM.fld = function (form, name) { return form.querySelector('[name="' + name + '"]'); };

    /* ---------------- SVG-иконки интерфейса ----------------
     * Стиль в духе Lucide/Feather: контурные, 24x24, currentColor.
     * Использование: MM.icon('download') / MM.icon('github', 'ic-fill')
     */
    var _IC = {
        home: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
        news: '<path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-4 0V9"/><line x1="18" y1="14" x2="12" y2="14"/><line x1="18" y1="18" x2="12" y2="18"/><line x1="10" y1="6" x2="18" y2="6"/><line x1="18" y1="10" x2="10" y2="10"/>',
        globe: '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
        github_fill: 'M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12',
        rss: '<path d="M4 11a9 9 0 0 1 9 9"/><path d="M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="2"/>',
        heart: '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>',
        upload: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>',
        trophy: '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2z"/>',
        bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/>',
        mail: '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
        user: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
        users: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
        calendar: '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
        logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
        search: '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
        download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
        eye: '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
        star: '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
        message: '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>',
        tag: '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>',
        x: '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        chevron: '<polyline points="6 9 12 15 18 9"/>',
        arrow_left: '<line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>',
        arrow_right: '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
        package: '<path d="M16.5 9.4 7.55 4.24"/><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
        cube: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><path d="M3.3 7 12 12l8.7-5"/><path d="M12 22V12"/>',
        clock: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
        folder: '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
        camera: '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/>',
        image: '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>',
        zap: '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
        flame: '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
        sparkles: '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3z"/>',
        shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
        lock: '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
        check: '<polyline points="20 6 9 17 4 12"/>',
        send: '<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>',
        menu: '<line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>',
        target: '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
        refresh: '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
        fork: '<circle cx="12" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><circle cx="18" cy="6" r="3"/><path d="M18 9v2c0 .6-.4 1-1 1H7c-.6 0-1-.4-1-1V9"/><path d="M12 12v3"/>',
        layers: '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
        file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
        gamepad: '<line x1="6" y1="12" x2="10" y2="12"/><line x1="8" y1="10" x2="8" y2="14"/><line x1="15" y1="13" x2="15.01" y2="13"/><line x1="18" y1="11" x2="18.01" y2="11"/><path d="M17.32 5H6.68a4 4 0 0 0-3.98 3.59C2.6 9.42 2 14.46 2 16a3 3 0 0 0 3 3c1 0 1.5-.5 2-1l1.41-1.41A2 2 0 0 1 9.83 16h4.34a2 2 0 0 1 1.41.59L17 18c.5.5 1 1 2 1a3 3 0 0 0 3-3c0-1.54-.6-6.58-.68-7.26A4 4 0 0 0 17.32 5z"/>'
    };
    var _FILL = { github_fill: 1 };
    MM.icon = function (name, cls) {
        var body = _IC[name];
        if (!body) return '';
        var fill = _FILL[name];
        var inner = fill ? '<path d="' + body + '"/>' : body;
        return '<svg class="ic ' + (cls || '') + '" viewBox="0 0 24 24" fill="' + (fill ? 'currentColor' : 'none') + '"' +
            (fill ? '' : ' stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"') +
            ' aria-hidden="true">' + inner + '</svg>';
    };
    MM.fmtBytes = function (b) {
        b = Number(b) || 0;
        if (b >= 1048576) return (b / 1048576).toFixed(1) + ' МБ';
        if (b >= 1024) return (b / 1024).toFixed(0) + ' КБ';
        return b + ' Б';
    };
    MM.fmtDate = function (iso) {
        var d = new Date(iso);
        if (isNaN(d)) return String(iso || '').slice(0, 10);
        return ('0' + d.getDate()).slice(-2) + '.' + ('0' + (d.getMonth() + 1)).slice(-2) + '.' + d.getFullYear();
    };
    MM.fmt = function (n) {
        n = Number(n) || 0;
        return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    };
    MM.user   = function () { return MM.get('mm_user', null); };
    MM.likes  = function () { return MM.get('mm_likes', []); };
    MM.follows= function () { return MM.get('mm_follows', []); };
    MM.myMods = function () { return MM.get('mm_mymods', []); };
    MM.qp     = function (name) { return new URLSearchParams(location.search).get(name) || ''; };

    MM.toast = function (msg, type) {
        var wrap = MM.$('#mmToasts');
        if (!wrap) {
            wrap = document.createElement('div');
            wrap.id = 'mmToasts';
            document.body.appendChild(wrap);
        }
        var el = document.createElement('div');
        el.className = 'mm-toast ' + (type ? 'mm-toast-' + type : '');
        el.textContent = msg;
        wrap.appendChild(el);
        setTimeout(function () { el.classList.add('show'); }, 16);
        setTimeout(function () {
            el.classList.remove('show');
            setTimeout(function () { el.remove(); }, 350);
        }, 3200);
    };

    /* ---------------- Modrinth: прямое скачивание ---------------- */
    // Качает файл прямо через сайт (CDN Modrinth), без перехода на modrinth.com
    MM.mrTriggerFile = function (url, filename) {
        var a = document.createElement('a');
        a.href = url;
        if (filename) a.setAttribute('download', filename);
        a.rel = 'noopener';
        document.body.appendChild(a);
        a.click();
        a.remove();
    };
    MM.mrDownloadLatest = function (slug, mc, loader) {
        var url = 'https://api.modrinth.com/v2/project/' + encodeURIComponent(slug) + '/version';
        return fetch(url).then(function (r) {
            if (!r.ok) throw new Error('http');
            return r.json();
        }).then(function (versions) {
            if (!versions || !versions.length) throw new Error('empty');
            var v = versions[0];
            // если заданы фильтры — ищем подходящую версию
            if (mc || loader) {
                var found = versions.filter(function (x) {
                    return (!mc || (x.game_versions || []).indexOf(mc) !== -1) &&
                           (!loader || (x.loaders || []).indexOf(loader) !== -1);
                })[0];
                if (found) v = found;
            }
            var files = (v.files || []).filter(function (f) { return f.primary; });
            var file = files[0] || (v.files || [])[0];
            if (!file) throw new Error('nofile');
            MM.mrTriggerFile(file.url, file.filename);
            MM.toast('⬇ Скачивается: ' + file.filename);
        }).catch(function () {
            MM.toast('Не удалось получить файл с Modrinth', 'warn');
        });
    };

    /* ---------------- Демо-каталог модов ---------------- */
    MM.CATALOG = [
        { id: 'dragon-mounts-2', title: 'Dragon Mounts II', category: 'Мобы',     mc: '1.20.4', version: '1.6.3', author: 'SteveCraft',
          desc: 'Выращивайте, приручайте и оседлайте девять видов драконов с уникальными способностями и окрасками.',
          tags: ['драконы', 'маунты', 'мобы'], downloads: 15230, likes: 1210, views: 55800, date: 20260728 },
        { id: 'technova', title: 'TechNova', category: 'Техника',                 mc: '1.20.1', version: '3.2.0', author: 'TechWizard',
          desc: 'Продвинутая автоматизация: конвейеры, дробилки, энергосети и умные механизмы для больших фабрик.',
          tags: ['техника', 'автоматизация', 'энергия'], downloads: 12840, likes: 932, views: 40210, date: 20260812 },
        { id: 'utility-belt', title: 'Utility Belt', category: 'Утилиты',         mc: '1.20.6', version: '3.0.5', author: 'TechWizard',
          desc: 'Пояс с быстрым доступом к инструментам, расширенный HUD и умные горячие клавиши.',
          tags: ['утилиты', 'инструменты', 'hud'], downloads: 11210, likes: 980, views: 33400, date: 20260802 },
        { id: 'arcane-realms', title: 'Arcane Realms', category: 'Магия',         mc: '1.21.1', version: '2.0.1', author: 'MageCraft',
          desc: 'Система заклинаний, ритуалы, магические артефакты и древние подземелья с боссами.',
          tags: ['магия', 'ритуалы', 'rpg'], downloads: 9560, likes: 812, views: 31200, date: 20260805 },
        { id: 'deco-plus', title: 'DecoPlus', category: 'Декор',                  mc: '1.21',   version: '4.1.2', author: 'AlexBuilds',
          desc: 'Сотни блоков мебели и декора: стулья, лампы, полки и анимированные украшения.',
          tags: ['декор', 'мебель', 'строительство'], downloads: 8920, likes: 745, views: 26400, date: 20260810 },
        { id: 'sky-village', title: 'Sky Village', category: 'Миры',              mc: '1.21.4', version: '2.2.0', author: 'SteveCraft',
          desc: 'Парящие в небе деревни с торговцами, воздушными кораблями и редкой добычей.',
          tags: ['деревни', 'структуры', 'генерация'], downloads: 7650, likes: 620, views: 21900, date: 20260815 },
        { id: 'feastcraft', title: 'FeastCraft', category: 'Еда',                 mc: '1.20.1', version: '2.4.0', author: 'AlexBuilds',
          desc: 'Более 120 новых блюд, кухонная утварь, фермерские культуры и система голода с бонусами.',
          tags: ['еда', 'фермерство', 'кулинария'], downloads: 6840, likes: 512, views: 19800, date: 20260720 },
        { id: 'void-dimensions', title: 'Void Dimensions', category: 'Миры',      mc: '1.19.2', version: '1.3.0', author: 'VoidWalker',
          desc: 'Четыре новых измерения с уникальными биомами, структурами и боссами.',
          tags: ['измерения', 'миры', 'приключения'], downloads: 5430, likes: 498, views: 15700, date: 20260630 },
        { id: 'royal-armory', title: 'Royal Armory', category: 'Оружие',          mc: '1.18.2', version: '1.9.1', author: 'RoyalSmith',
          desc: '60+ видов средневекового оружия и брони с уникальными свойствами и прокачкой.',
          tags: ['оружие', 'броня', 'бой'], downloads: 4210, likes: 365, views: 12100, date: 20260518 }
    ];

    MM.modCardHTML = function (m) {
        var tags = (m.tags || []).slice(0, 3).map(function (t) { return '<span class="tag">#' + MM.esc(t) + '</span>'; }).join('');
        return '' +
        '<div class="mod-card">' +
            '<div class="mod-card-header">' +
                '<div class="mod-category">' + MM.esc(m.category) + '</div>' +
                '<div class="mod-mc-badge">MC ' + MM.esc(m.mc) + '</div>' +
            '</div>' +
            '<h3><a href="mod.html?m=' + MM.esc(m.id) + '">' + MM.esc(m.title) + '</a></h3>' +
            '<p class="mod-meta"><span>v' + MM.esc(m.version) + '</span> <span>•</span> <span>' +
                '<a href="user.html?u=' + encodeURIComponent(m.author) + '" class="author-link">' + MM.icon('user', 'ic-sm') + ' ' + MM.esc(m.author) + '</a></span></p>' +
            '<p class="mod-desc">' + MM.esc(m.desc) + '</p>' +
            (tags ? '<div class="mod-tags">' + tags + '</div>' : '') +
            '<div class="mod-footer">' +
                '<div class="mod-stats">' +
                    '<span class="stat-item">' + MM.icon('download', 'ic-sm') + ' ' + MM.fmt(m.downloads) + '</span>' +
                    '<span class="stat-item">' + MM.icon('heart', 'ic-sm') + ' ' + MM.fmt(m.likes) + '</span>' +
                    '<span class="stat-item">' + MM.icon('eye', 'ic-sm') + ' ' + MM.fmt(m.views) + '</span>' +
                '</div>' +
                '<a href="mod.html?m=' + MM.esc(m.id) + '#download" class="btn-download">' + MM.icon('download', 'ic-sm') + ' Скачать</a>' +
            '</div>' +
        '</div>';
    };

    /* ---------------- Темы и анимации ---------------- */
    MM.applyTheme = function () {
        var t = MM.get('mm_theme', 'green');
        var a = MM.get('mm_animations', 'on');
        document.documentElement.setAttribute('data-theme', t);
        document.documentElement.setAttribute('data-animations', a === 'off' ? 'off' : 'on');
    };

    /* ---------------- Топбар (вход/профиль) ---------------- */
    function renderTopbar() {
        var box = MM.$('#topbarRight');
        if (!box) return;
        var u = MM.user();
        if (!u) {
            box.innerHTML =
                '<a href="login.html" class="topbar-btn">Войти</a>' +
                '<a href="register.html" class="topbar-btn topbar-btn-primary">Регистрация</a>';
            return;
        }
        var name = MM.esc(u.username);
        var avatar = u.avatar
            ? '<img src="' + u.avatar + '" class="topbar-avatar" alt="Аватар ' + name + '">'
            : '<div class="topbar-avatar-letter">' + MM.esc((u.username || '?')[0].toUpperCase()) + '</div>';
        box.innerHTML =
            '<a href="notifications.html" class="topbar-icon" title="Уведомления">' + MM.icon('bell') + '</a>' +
            '<a href="messages.html" class="topbar-icon" title="Сообщения">' + MM.icon('mail') + '</a>' +
            '<div class="user-menu" role="menu">' +
                '<button class="user-menu-btn" id="userMenuBtn" aria-haspopup="true">' + avatar +
                    '<span class="user-menu-name">' + name + '</span>' +
                    '<span class="dropdown-arrow">' + MM.icon('chevron', 'ic-xs') + '</span>' +
                '</button>' +
                '<div class="user-dropdown" role="menu">' +
                    '<a href="profile.html" class="dropdown-item">' + MM.icon('user') + ' Профиль</a>' +
                    '<a href="settings.html" class="dropdown-item">' + MM.icon('settings') + ' Настройки</a>' +
                    '<a href="activity.html" class="dropdown-item">' + MM.icon('calendar') + ' Активность</a>' +
                    '<div class="dropdown-divider"></div>' +
                    '<a href="#" class="dropdown-item logout" id="logoutBtn">' + MM.icon('logout') + ' Выйти</a>' +
                '</div>' +
            '</div>';
        var btn = MM.$('#userMenuBtn'), dd = MM.$('.user-dropdown', box);
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            dd.classList.toggle('open');
        });
        MM.$('#logoutBtn').addEventListener('click', function (e) {
            e.preventDefault();
            MM.del('mm_user');
            MM.toast('Вы вышли из аккаунта');
            setTimeout(function () { location.href = 'index.html'; }, 400);
        });
    }

    function renderSidebarFooter() {
        var box = MM.$('#sidebarAuth');
        if (!box) return;
        var u = MM.user();
        if (!u) {
            box.innerHTML =
                '<a href="login.html" class="btn-sidebar">Войти</a>' +
                '<a href="register.html" class="btn-sidebar btn-primary">Регистрация</a>';
        } else {
            var letter = MM.esc((u.username || '?')[0].toUpperCase());
            box.innerHTML =
                '<a href="profile.html" class="user-card" style="text-decoration:none;color:inherit">' +
                    '<div class="user-avatar">' + letter + '</div>' +
                    '<div class="user-info"><div class="user-name">' + MM.esc(u.username) + '</div>' +
                    '<span class="user-logout">Мой профиль</span></div>' +
                '</a>';
        }
        // Защищённые пункты меню видны только после входа
        MM.$$('.auth-only').forEach(function (el) {
            el.style.display = u ? '' : 'none';
        });
    }

    /* ---------------- Защита страниц ---------------- */
    function guardProtected() {
        if (document.body.getAttribute('data-protected') !== '1') return;
        if (MM.user()) return;
        var pc = MM.$('#pageContent');
        if (!pc) return;
        pc.innerHTML =
            '<div class="empty-state" style="margin-top:60px">' +
                '<div class="empty-icon">🔒</div>' +
                '<h3>Требуется вход</h3>' +
                '<p>Эта страница доступна только после входа в аккаунт (демо-режим).</p>' +
                '<a href="login.html" class="btn-download-big" style="display:inline-block;margin-right:12px">Войти</a>' +
                '<a href="register.html" class="btn-download-big" style="display:inline-block;filter:saturate(.6)">Регистрация</a>' +
            '</div>';
    }

    /* ---------------- Счётчики ---------------- */
    function initCounters() {
        var els = MM.$$('.counter[data-target]');
        if (!els.length) return;
        var animate = function (el) {
            var target = parseInt(el.getAttribute('data-target'), 10) || 0;
            var t0 = null, dur = 1400;
            var step = function (ts) {
                if (!t0) t0 = ts;
                var p = Math.min(1, (ts - t0) / dur);
                el.textContent = MM.fmt(Math.floor(target * (p * (2 - p))));
                if (p < 1) requestAnimationFrame(step);
            };
            requestAnimationFrame(step);
        };
        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (entries) {
                entries.forEach(function (en) {
                    if (en.isIntersecting) { animate(en.target); io.unobserve(en.target); }
                });
            });
            els.forEach(function (el) { io.observe(el); });
        } else { els.forEach(animate); }
    }

    /* ---------------- Формы входа/регистрации ---------------- */
    function initAuthForms() {
        var login = MM.$('#loginForm');
        if (login) login.addEventListener('submit', function (e) {
            e.preventDefault();
            var username = MM.fld(login, 'username').value.trim();
            if (!username) return;
            var old = MM.user() || {};
            MM.set('mm_user', {
                username: username,
                email: old.email || '',
                bio: old.bio || '',
                avatar: old.avatar || '',
                joined: old.joined || new Date().toISOString().slice(0, 10)
            });
            MM.toast('С возвращением, ' + username + '!');
            setTimeout(function () { location.href = 'index.html'; }, 500);
        });

        var reg = MM.$('#registerForm');
        if (reg) reg.addEventListener('submit', function (e) {
            e.preventDefault();
            var username = MM.fld(reg, 'username').value.trim();
            var email = MM.fld(reg, 'email').value.trim();
            if (!username) return;
            MM.set('mm_user', { username: username, email: email, bio: '', avatar: '', joined: new Date().toISOString().slice(0, 10) });
            MM.toast('Аккаунт создан! Добро пожаловать, ' + username + '!');
            setTimeout(function () { location.href = 'index.html'; }, 600);
        });
    }

    /* ================= ГЛАВНАЯ (каталог) ================= */
    function initIndex() {
        var grid = MM.$('#modsGrid');
        if (!grid) return;
        var qInput   = MM.$('#fq');
        var catSel   = MM.$('#fcat');
        var verSel   = MM.$('#fver');
        var form     = MM.$('#modFilterForm');
        var noRes    = MM.$('#noResults');
        var state = { q: '', cat: '', ver: '', tag: 'all', sort: 'new' };

        function apply() {
            var cards = MM.$$('.mod-card', grid);
            cards.sort(function (a, b) {
                var k = state.sort;
                var attr = k === 'popular' ? 'downloads' : k === 'top' ? 'likes' : k === 'views' ? 'views' : 'date';
                return (Number(b.getAttribute('data-' + attr)) || 0) - (Number(a.getAttribute('data-' + attr)) || 0);
            }).forEach(function (c) { grid.appendChild(c); });

            var shown = 0;
            var q = state.q.toLowerCase();
            cards.forEach(function (c) {
                var hay = (c.getAttribute('data-title') + ' ' + c.getAttribute('data-desc') + ' ' + c.getAttribute('data-tags')).toLowerCase();
                var ok = (!q || hay.indexOf(q) !== -1)
                    && (!state.cat || c.getAttribute('data-category') === state.cat)
                    && (!state.ver || c.getAttribute('data-mc') === state.ver)
                    && (state.tag === 'all' || (c.getAttribute('data-tags') || '').split(' ').indexOf(state.tag) !== -1);
                c.style.display = ok ? '' : 'none';
                if (ok) shown++;
            });
            if (noRes) noRes.style.display = shown ? 'none' : '';
        }

        if (form) form.addEventListener('submit', function (e) { e.preventDefault(); apply(); });
        if (qInput) qInput.addEventListener('input', function () { state.q = this.value; apply(); });
        if (catSel) catSel.addEventListener('change', function () { state.cat = this.value; apply(); });
        if (verSel) verSel.addEventListener('change', function () { state.ver = this.value; apply(); });

        MM.$$('.tag-btn[data-tag]').forEach(function (b) {
            b.addEventListener('click', function () {
                MM.$$('.tag-btn[data-tag]').forEach(function (x) { x.classList.remove('active'); });
                b.classList.add('active');
                state.tag = b.getAttribute('data-tag');
                apply();
            });
        });
        MM.$$('.sort-tab[data-sort]').forEach(function (b) {
            b.addEventListener('click', function (e) {
                e.preventDefault();
                MM.$$('.sort-tab[data-sort]').forEach(function (x) { x.classList.remove('active'); });
                b.classList.add('active');
                state.sort = b.getAttribute('data-sort');
                apply();
            });
        });

        // URL-параметры
        var sq = MM.qp('q'), sc = MM.qp('category'), sv = MM.qp('mc_version');
        if (sq && qInput) { qInput.value = sq; state.q = sq; }
        if (sc && catSel) { catSel.value = sc; state.cat = sc; }
        if (sv && verSel) { verSel.value = sv; state.ver = sv; }
        apply();
    }

    /* ================= СТРАНИЦА МОДА ================= */
    function initModPage() {
        var likeBtn = MM.$('#likeBtn');
        var modId = MM.qp('m') || document.body.getAttribute('data-mod') || 'technova';
        var mod = MM.CATALOG.filter(function (m) { return m.id === modId; })[0] || MM.CATALOG[1];
        var baseLikes = mod.likes;

        function paintLike() {
            if (!likeBtn) return;
            var liked = MM.likes().indexOf(modId) !== -1;
            likeBtn.classList.toggle('liked', liked);
            var icon = MM.$('.like-icon', likeBtn), text = MM.$('.like-text', likeBtn), count = MM.$('.like-count', likeBtn);
            if (icon) icon.innerHTML = MM.icon('heart', liked ? 'ic-fill liked-heart' : '');
            if (text) text.textContent = liked ? 'В избранном' : 'Лайкнуть';
            if (count) count.textContent = MM.fmt(baseLikes + (liked ? 1 : 0));
        }
        if (likeBtn) {
            likeBtn.addEventListener('click', function () {
                if (!MM.user()) { MM.toast('Войдите, чтобы лайкать (демо)', 'warn'); location.href = 'login.html'; return; }
                var l = MM.likes();
                var i = l.indexOf(modId);
                if (i === -1) { l.push(modId); MM.toast('Добавлено в избранное ❤'); } else { l.splice(i, 1); MM.toast('Убрано из избранного'); }
                MM.set('mm_likes', l);
                paintLike();
            });
            paintLike();
        }

        // Лайтбокс
        window.openLightbox = function (src) {
            var lb = MM.$('#lightbox'); if (!lb) return;
            MM.$('#lightbox-img').src = src;
            lb.classList.add('active');
        };
        window.closeLightbox = function () {
            var lb = MM.$('#lightbox'); if (lb) lb.classList.remove('active');
        };

        // Модалка скачивания
        var modal = MM.$('#downloadModal');
        var versions = window.MOD_VERSIONS || [];
        function opts(sel, first, list, valFn, txtFn) {
            sel.innerHTML = '<option value="">' + first + '</option>' + list.map(function (v, i) {
                return '<option value="' + (valFn ? valFn(v, i) : MM.esc(v)) + '">' + (txtFn ? txtFn(v) : MM.esc(v)) + '</option>';
            }).join('');
        }
        window.openDownloadModal = function () {
            if (!modal) return;
            var mcSel = MM.$('#mcVersionSelect');
            var mcs = [];
            versions.forEach(function (v) { if (mcs.indexOf(v.mc) === -1) mcs.push(v.mc); });
            opts(mcSel, 'Выберите версию MC', mcs);
            var ls = MM.$('#loaderSelect'), ms = MM.$('#modVersionSelect'), fb = MM.$('#finalDownloadBtn');
            opts(ls, 'Сначала выберите MC', []); ls.disabled = true;
            opts(ms, 'Сначала выберите загрузчик', []); ms.disabled = true;
            fb.setAttribute('disabled', 'disabled'); fb.removeAttribute('href');
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        };
        window.closeDownloadModal = function (e) {
            if (!modal) return;
            if (!e || e.target === modal) {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            }
        };
        window.updateLoaderOptions = function () {
            var mc = MM.$('#mcVersionSelect').value;
            var ls = MM.$('#loaderSelect'), ms = MM.$('#modVersionSelect');
            if (!mc) { opts(ls, 'Сначала выберите MC', []); ls.disabled = true; return; }
            var loaders = [];
            versions.forEach(function (v) { if (v.mc === mc && loaders.indexOf(v.loader) === -1) loaders.push(v.loader); });
            opts(ls, 'Выберите загрузчик', loaders); ls.disabled = false;
            opts(ms, 'Сначала выберите загрузчик', []); ms.disabled = true;
        };
        window.updateVersionOptions = function () {
            var mc = MM.$('#mcVersionSelect').value, ld = MM.$('#loaderSelect').value;
            var ms = MM.$('#modVersionSelect');
            if (!mc || !ld) { opts(ms, 'Сначала выберите загрузчик', []); ms.disabled = true; return; }
            var list = versions.filter(function (v) { return v.mc === mc && v.loader === ld; });
            opts(ms, 'Выберите версию мода', list, function (v, i) { return String(i); }, function (v) { return 'v' + v.version + ' (' + v.file + ')'; });
            ms.disabled = false;
        };
        var ms = MM.$('#modVersionSelect');
        if (ms) ms.addEventListener('change', function () {
            var fb = MM.$('#finalDownloadBtn');
            if (this.value !== '') { fb.removeAttribute('disabled'); fb.setAttribute('href', '#download'); }
            else { fb.setAttribute('disabled', 'disabled'); fb.removeAttribute('href'); }
        });
        var fb = MM.$('#finalDownloadBtn');
        if (fb) fb.addEventListener('click', function (e) {
            e.preventDefault();
            var dc = MM.$('#dlCount');
            if (dc) dc.textContent = MM.fmt((parseInt(dc.getAttribute('data-n'), 10) || mod.downloads) + 1);
            window.closeDownloadModal(e);
            MM.toast('⬇ Скачивание началось (демо-режим)');
        });
        // #download в URL — сразу открыть модалку
        if (location.hash === '#download') setTimeout(window.openDownloadModal, 300);

        // Комментарии
        var cf = MM.$('#commentForm');
        if (cf) cf.addEventListener('submit', function (e) {
            e.preventDefault();
            if (!MM.user()) { location.href = 'login.html'; return; }
            var ta = cf.querySelector('textarea');
            var text = ta.value.trim();
            if (!text) return;
            var u = MM.user();
            var list = MM.$('#commentsList');
            var noC = MM.$('.no-comments', list); if (noC) noC.remove();
            var div = document.createElement('div');
            div.className = 'comment';
            div.innerHTML =
                '<div class="comment-avatar">' + MM.esc((u.username || '?')[0].toUpperCase()) + '</div>' +
                '<div class="comment-body"><div class="comment-header">' +
                    '<span class="comment-author">' + MM.esc(u.username) + '</span>' +
                    '<span class="comment-date">только что</span></div>' +
                    '<div class="comment-text">' + MM.esc(text) + '</div></div>';
            list.insertBefore(div, list.firstChild);
            MM.set('mm_commented', true);
            MM.set('mm_comment_count', (MM.get('mm_comment_count', 0) || 0) + 1);
            ['#commentsCount', '#commentsCountLabel'].forEach(function (sel) {
                var cc = MM.$(sel);
                if (cc) cc.textContent = String((parseInt(cc.textContent, 10) || 0) + 1);
            });
            ta.value = '';
            MM.toast('Комментарий опубликован 💬');
        });
    }

    /* ================= ЗАГРУЗКА ================= */
    function initUpload() {
        var t = MM.qp('type') || 'mod';
        MM.$$('.ut-tab[data-type]').forEach(function (x) {
            x.classList.toggle('active', x.getAttribute('data-type') === t);
        });
        var f = MM.$('#uploadForm');
        if (!f) return;
        f.addEventListener('submit', function (e) {
            e.preventDefault();
            var mod = {
                id: 'my-' + Date.now(),
                title: MM.fld(f, 'title').value.trim(),
                desc: MM.fld(f, 'description').value.trim(),
                version: MM.fld(f, 'version').value.trim() || '1.0.0',
                mc: MM.fld(f, 'mc_version').value,
                loader: MM.fld(f, 'loader').value,
                category: MM.fld(f, 'category').value,
                tags: (MM.fld(f, 'tags').value || '').split(',').map(function (t) { return t.trim().replace(/^#/, ''); }).filter(Boolean),
                downloads: 0, likes: 0, views: 1, date: Number(new Date().toISOString().slice(0, 10).replace(/-/g, ''))
            };
            if (!mod.title || !mod.category) return;
            var arr = MM.myMods();
            arr.unshift(mod);
            MM.set('mm_mymods', arr);
            MM.toast('🚀 Мод «' + mod.title + '» опубликован (демо)!');
            setTimeout(function () { location.href = 'profile.html'; }, 700);
        });
    }

    /* ================= ПРОФИЛЬ ================= */
    function initProfile() {
        var u = MM.user();
        if (!u) return;
        var box = MM.$('#profileBox');
        if (!box) return;
        var mods = MM.myMods();
        var dls = mods.reduce(function (s, m) { return s + (m.downloads || 0); }, 0);
        var likes = mods.reduce(function (s, m) { return s + (m.likes || 0); }, 0);
        var follows = MM.follows().length;
        var letter = MM.esc((u.username || '?')[0].toUpperCase());
        var avatar = u.avatar ? '<img src="' + u.avatar + '" class="profile-avatar-img" alt="avatar">' : '<div class="profile-avatar-big">' + letter + '</div>';
        box.innerHTML =
            '<div class="profile-header">' + avatar +
                '<div class="profile-info"><h1>' + MM.esc(u.username) + '</h1>' +
                '<p class="profile-email">' + MM.esc(u.email || 'email не указан') + '</p>' +
                (u.bio ? '<p class="profile-bio">' + MM.esc(u.bio) + '</p>' : '') +
                '<p class="profile-date">📅 С нами с ' + MM.esc(u.joined || '—') + '</p></div>' +
            '</div>' +
            '<div class="profile-stats">' +
                '<div class="stat-card"><div class="stat-num">' + mods.length + '</div><div class="stat-label">' + MM.icon('package', 'ic-sm') + ' Модов</div></div>' +
                '<div class="stat-card"><div class="stat-num">' + MM.fmt(dls) + '</div><div class="stat-label">' + MM.icon('download', 'ic-sm') + ' Скачиваний</div></div>' +
                '<div class="stat-card"><div class="stat-num">' + MM.fmt(likes) + '</div><div class="stat-label">' + MM.icon('heart', 'ic-sm') + ' Лайков</div></div>' +
                '<div class="stat-card"><div class="stat-num">0</div><div class="stat-label">' + MM.icon('users', 'ic-sm') + ' Подписчиков</div></div>' +
                '<div class="stat-card"><div class="stat-num">' + follows + '</div><div class="stat-label">' + MM.icon('rss', 'ic-sm') + ' Подписок</div></div>' +
            '</div>' +
            '<h3 class="section-title">' + MM.icon('package') + ' Мои моды</h3>' +
            '<div class="my-mods-grid">' +
                (mods.length ? mods.map(function (m) {
                    return '<div class="my-mod-card">' +
                        '<div class="mod-category">' + MM.esc(m.category) + '</div>' +
                        '<a href="mod.html" class="my-mod-title">' + MM.esc(m.title) + '</a>' +
                        '<div class="my-mod-meta"><span>MC ' + MM.esc(m.mc) + '</span>' +
                        '<span>' + MM.icon('download', 'ic-sm') + ' ' + MM.fmt(m.downloads) + ' ' + MM.icon('heart', 'ic-sm') + ' ' + MM.fmt(m.likes) + ' ' + MM.icon('eye', 'ic-sm') + ' ' + MM.fmt(m.views) + '</span></div>' +
                        '<button class="btn-delete" data-del="' + m.id + '">Удалить</button>' +
                    '</div>';
                }).join('') :
                '<div class="empty-state"><div class="empty-icon">📦</div><h3>У тебя пока нет модов</h3>' +
                '<a href="upload.html" class="btn-download-big">Загрузить первый мод</a></div>') +
            '</div>';
        MM.$$('[data-del]', box).forEach(function (b) {
            b.addEventListener('click', function () {
                if (!confirm('Удалить мод?')) return;
                MM.set('mm_mymods', MM.myMods().filter(function (m) { return m.id !== b.getAttribute('data-del'); }));
                MM.toast('Мод удалён');
                initProfile();
            });
        });
    }

    /* ================= НАСТРОЙКИ ================= */
    function initSettings() {
        var u0 = MM.user();
        // Текущий аватар
        var avBox = MM.$('.current-avatar-letter');
        if (avBox && u0) {
            if (u0.avatar) {
                avBox.outerHTML = '<img src="' + u0.avatar + '" class="current-avatar" alt="avatar">';
            } else {
                avBox.textContent = (u0.username || '?')[0].toUpperCase();
            }
        }
        // Предзаполнение формы профиля
        var pf0 = MM.$('#profileForm');
        if (pf0 && u0) {
            MM.fld(pf0, 'email').value = u0.email || '';
            MM.fld(pf0, 'bio').value = u0.bio || '';
        }

        var grid = MM.$('#themeGrid');
        if (grid) {
            var cur = MM.get('mm_theme', 'green');
            MM.$$('input[name="theme"]', grid).forEach(function (r) {
                r.checked = r.value === cur;
                r.parentElement.classList.toggle('active', r.checked);
                r.addEventListener('change', function () {
                    MM.set('mm_theme', r.value);
                    MM.applyTheme();
                    MM.$$('input[name="theme"]', grid).forEach(function (x) { x.parentElement.classList.toggle('active', x.checked); });
                    var lbl = MM.$('label[for="theme-' + r.value + '"] .theme-name') || null;
                    MM.toast('Тема сохранена 🎨');
                });
            });
        }
        var an = MM.$('#animToggle');
        if (an) {
            an.checked = MM.get('mm_animations', 'on') !== 'off';
            an.addEventListener('change', function () {
                MM.set('mm_animations', an.checked ? 'on' : 'off');
                MM.applyTheme();
                MM.toast(an.checked ? 'Анимации включены ✨' : 'Анимации выключены');
            });
        }
        var av = MM.$('#avatarInput');
        if (av) av.addEventListener('change', function () {
            var file = av.files && av.files[0];
            if (!file) return;
            var img = new Image();
            img.onload = function () {
                var c = document.createElement('canvas');
                var s = Math.min(128 / img.width, 128 / img.height, 1);
                c.width = Math.round(img.width * s); c.height = Math.round(img.height * s);
                c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
                var u = MM.user() || { username: 'user', email: '', bio: '', joined: '' };
                u.avatar = c.toDataURL('image/png');
                MM.set('mm_user', u);
                MM.toast('Аватар обновлён 🖼️');
                location.reload();
            };
            img.src = URL.createObjectURL(file);
        });
        var pf = MM.$('#profileForm');
        if (pf) {
            pf.addEventListener('submit', function (e) {
                e.preventDefault();
                var u = MM.user() || { username: 'user', avatar: '', joined: '' };
                u.email = MM.fld(pf, 'email').value.trim();
                u.bio = MM.fld(pf, 'bio').value.trim();
                MM.set('mm_user', u);
                MM.toast('Профиль сохранён ✅');
            });
        }
        var pw = MM.$('#passwordForm');
        if (pw) pw.addEventListener('submit', function (e) {
            e.preventDefault();
            pw.reset();
            MM.toast('Пароль изменён 🔒 (демо)');
        });
    }

    /* ================= ИЗБРАННОЕ / ЛЕНТА ================= */
    function initFavorites() {
        var grid = MM.$('#favGrid');
        if (!grid) return;
        var ids = MM.likes();
        var mods = MM.CATALOG.filter(function (m) { return ids.indexOf(m.id) !== -1; });
        var cnt = MM.$('#favCount'); if (cnt) cnt.textContent = String(mods.length);
        grid.innerHTML = mods.length ? mods.map(MM.modCardHTML).join('') :
            '<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">💔</div><h3>В избранном пусто</h3>' +
            '<p>Лайкни понравившиеся моды!</p><a href="index.html" class="btn-download-big">К каталогу</a></div>';
    }

    function initFeed() {
        var grid = MM.$('#feedGrid');
        if (!grid) return;
        var u = MM.user();
        if (u && localStorage.getItem('mm_follows') === null) MM.set('mm_follows', ['SteveCraft']);
        var authors = MM.follows();
        var mods = MM.CATALOG.filter(function (m) { return authors.indexOf(m.author) !== -1; });
        mods.sort(function (a, b) { return b.date - a.date; });
        var cnt = MM.$('#feedCount'); if (cnt) cnt.textContent = String(mods.length);
        grid.innerHTML = mods.length ? mods.map(MM.modCardHTML).join('') :
            '<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">📡</div><h3>Лента пуста</h3>' +
            '<p>Подпишись на интересных авторов!</p><a href="index.html" class="btn-download-big">Найти авторов</a></div>';
    }

    /* ================= ДОСТИЖЕНИЯ ================= */
    function initAchievements() {
        var grid = MM.$('#achGrid');
        if (!grid) return;
        var mods = MM.myMods();
        var dls = mods.reduce(function (s, m) { return s + (m.downloads || 0); }, 0);
        var lk = mods.reduce(function (s, m) { return s + (m.likes || 0); }, 0);
        var earned = {
            first_mod: mods.length >= 1, mods_5: mods.length >= 5, mods_10: mods.length >= 10, mods_25: mods.length >= 25,
            downloads_10: dls >= 10, downloads_100: dls >= 100, downloads_1000: dls >= 1000,
            likes_10: lk >= 10, likes_50: lk >= 50, likes_100: lk >= 100,
            first_comment: !!MM.get('mm_commented', false), comments_10: (MM.get('mm_comment_count', 0) || 0) >= 10,
            first_like: MM.likes().length >= 1, subscriber: MM.follows().length >= 1, popular_author: false
        };
        var ALL = [
            ['first_mod', '🎯', 'Первый шаг', 'Загрузил первый мод'],
            ['mods_5', '🛠️', 'Моддер', '5 модов'],
            ['mods_10', '⚡', 'Профи', '10 модов'],
            ['mods_25', '🏆', 'Мастер', '25 модов'],
            ['downloads_10', '👀', 'Замечен', '10 скачиваний'],
            ['downloads_100', '🔥', 'Популярный', '100 скачиваний'],
            ['downloads_1000', '👑', 'Легенда', '1000 скачиваний'],
            ['likes_10', '❤️', 'Любимец', '10 лайков'],
            ['likes_50', '⭐', 'Звезда', '50 лайков'],
            ['likes_100', '💎', 'Кумир', '100 лайков'],
            ['first_comment', '💬', 'Социальный', 'Первый комментарий'],
            ['comments_10', '🗣️', 'Болтун', '10 комментариев'],
            ['first_like', '👍', 'Поддержка', 'Первый лайк'],
            ['subscriber', '🔔', 'Подписчик', 'Подписался на автора'],
            ['popular_author', '🌟', 'Известный', '5 подписчиков']
        ];
        var n = ALL.filter(function (a) { return earned[a[0]]; }).length;
        var st = MM.$('#achProgress');
        if (st) st.textContent = Math.round(n / ALL.length * 100) + '%';
        var sub = MM.$('#achSubtitle');
        if (sub) sub.textContent = 'Получено ' + n + ' из ' + ALL.length;
        grid.innerHTML = ALL.map(function (a) {
            var ok = earned[a[0]];
            return '<div class="achievement' + (ok ? ' earned' : '') + '">' +
                '<div class="ach-icon">' + a[1] + '</div>' +
                '<div class="ach-info"><div class="ach-name">' + a[2] + '</div><div class="ach-desc">' + a[3] + '</div></div>' +
                (ok ? '<div class="ach-badge">✓</div>' : '<div class="ach-lock">🔒</div>') +
            '</div>';
        }).join('');
    }

    /* ================= ПОЛЬЗОВАТЕЛЬ ================= */
    function initUserPage() {
        var box = MM.$('#userBox');
        if (!box) return;
        var name = MM.qp('u') || 'TechWizard';
        var mods = MM.CATALOG.filter(function (m) { return m.author === name; });
        var BIOS = {
            TechWizard: 'Автоматизирую всё, что движется. Forge/Fabric.',
            MageCraft: 'Магия, ритуалы и древние тайны ✨',
            SteveCraft: 'Строю миры и приручаю драконов 🐉',
            AlexBuilds: 'Декоратор-перфекционист. Еда и уют 🍰',
            VoidWalker: 'Исследователь пустоты. Новые измерения.',
            RoyalSmith: 'Мастер клинков ⚔️'
        };
        var dls = mods.reduce(function (s, m) { return s + m.downloads; }, 0);
        var lk = mods.reduce(function (s, m) { return s + m.likes; }, 0);
        var subs = MM.follows().indexOf(name) !== -1;
        function subBtn() {
            return '<button class="btn-subscribe' + (subs ? ' subscribed' : '') + '" id="subBtn">' +
                '<span class="sub-text">' + (subs ? '✓ Подписан' : '+ Подписаться') + '</span>' +
                '<span class="sub-count">' + (subs ? 1 : 0) + '</span></button>';
        }
        box.innerHTML =
            '<div class="profile-header">' +
                '<div class="profile-avatar-big">' + MM.esc(name[0].toUpperCase()) + '</div>' +
                '<div class="profile-info"><h1>' + MM.esc(name) + '</h1>' +
                '<p class="profile-bio">' + MM.esc(BIOS[name] || 'Моддер сообщества MineMods') + '</p>' +
                '<p class="profile-date">📅 С нами с 2025 года</p>' +
                '<div class="profile-actions">' + subBtn() +
                    '<a href="chat.html?u=' + encodeURIComponent(name) + '" class="btn-subscribe" style="background:var(--bg-card);color:var(--text-main);border:2px solid var(--border)">' + MM.icon('mail', 'ic-sm') + ' Написать</a>' +
                    '<a href="activity.html" class="btn-subscribe" style="background:var(--bg-card);color:var(--text-main);border:2px solid var(--border)">' + MM.icon('calendar', 'ic-sm') + ' Активность</a>' +
                '</div></div>' +
            '</div>' +
            '<div class="profile-stats">' +
                '<div class="stat-card"><div class="stat-num">' + mods.length + '</div><div class="stat-label">' + MM.icon('package', 'ic-sm') + ' Модов</div></div>' +
                '<div class="stat-card"><div class="stat-num">' + MM.fmt(dls) + '</div><div class="stat-label">' + MM.icon('download', 'ic-sm') + ' Скачиваний</div></div>' +
                '<div class="stat-card"><div class="stat-num">' + MM.fmt(lk) + '</div><div class="stat-label">' + MM.icon('heart', 'ic-sm') + ' Лайков</div></div>' +
            '</div>' +
            '<h3 class="section-title">' + MM.icon('package') + ' Моды автора</h3>' +
            '<div class="mods-grid">' +
                (mods.length ? mods.map(MM.modCardHTML).join('') :
                '<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">📦</div><h3>У автора пока нет модов</h3></div>') +
            '</div>';
        var sb = MM.$('#subBtn');
        if (sb) sb.addEventListener('click', function () {
            if (!MM.user()) { location.href = 'login.html'; return; }
            var f = MM.follows();
            var i = f.indexOf(name);
            if (i === -1) { f.push(name); MM.toast('Подписка оформлена 🔔'); } else { f.splice(i, 1); MM.toast('Подписка отменена'); }
            MM.set('mm_follows', f);
            initUserPage();
        });
    }

    /* ================= АКТИВНОСТЬ ================= */
    function initActivity() {
        var list = MM.$('#activityList');
        if (!list) return;
        var u = MM.user();
        var me = u ? u.username : 'Гость';
        var ev = [];
        MM.myMods().forEach(function (m) {
            ev.push({ icon: '📤', text: me + ' загрузил мод «' + m.title + '»', ts: m.date * 10000 });
        });
        MM.likes().forEach(function (id) {
            var m = MM.CATALOG.filter(function (x) { return x.id === id; })[0];
            if (m) ev.push({ icon: '❤️', text: me + ' лайкнул «' + m.title + '»', ts: 20260816 * 10000 });
        });
        MM.follows().forEach(function (a) {
            ev.push({ icon: '🔔', text: me + ' подписался на ' + a, ts: 20260814 * 10000 });
        });
        ev.push({ icon: '📦', text: 'SteveCraft обновил мод «Sky Village» до v2.2.0', ts: 20260815 * 10000 });
        ev.push({ icon: '📦', text: 'TechWizard опубликовал «TechNova v3.2.0» для MC 1.20.1', ts: 20260812 * 10000 });
        ev.push({ icon: '💬', text: 'MageCraft прокомментировал «Arcane Realms»', ts: 20260811 * 10000 });
        ev.sort(function (a, b) { return b.ts - a.ts; });
        function fmt(ts) {
            var s = String(Math.floor(ts / 10000));
            return s.slice(6, 8) + '.' + s.slice(4, 6) + '.' + s.slice(0, 4);
        }
        list.innerHTML = ev.length ? ev.map(function (a) {
            return '<div class="activity-item"><div class="act-icon">' + a.icon + '</div>' +
                '<div class="act-body"><div class="act-text">' + MM.esc(a.text) + '</div>' +
                '<div class="act-date">' + fmt(a.ts) + '</div></div></div>';
        }).join('') : '<div class="empty-state"><div class="empty-icon">📅</div><h3>Нет активности</h3></div>';
    }

    /* ================= ЧАТ ================= */
    function initChat() {
        var box = MM.$('#chatMessages');
        if (!box) return;
        var other = MM.qp('u') || 'AlexBuilds';
        var unameBox = MM.$('#chatUsername');
        if (unameBox) unameBox.textContent = other;
        var av = MM.$('#chatAvatar');
        if (av) av.textContent = other[0].toUpperCase();
        var link = MM.$('#chatUserLink');
        if (link) link.setAttribute('href', 'user.html?u=' + encodeURIComponent(other));

        var KEY = 'mm_chat_' + other;
        var msgs = MM.get(KEY, null);
        if (!msgs) {
            msgs = [
                { from: 'other', text: 'Привет! Видел мой новый мод?', ts: '18:20' },
                { from: 'other', text: 'Скажи, если найдёшь баги — быстро поправлю 🛠️', ts: '18:21' }
            ];
            MM.set(KEY, msgs);
        }
        function now() { var d = new Date(); return ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2); }
        function render() {
            box.innerHTML = msgs.map(function (m) {
                return '<div class="msg ' + (m.from === 'me' ? 'msg-mine' : 'msg-other') + '"><div class="msg-bubble">' +
                    '<div class="msg-text">' + MM.esc(m.text) + '</div>' +
                    '<div class="msg-time">' + MM.esc(m.ts) + '</div></div></div>';
            }).join('') || '<div class="empty-state"><div class="empty-icon">💬</div><h3>Начни диалог</h3></div>';
            box.scrollTop = box.scrollHeight;
        }
        render();
        var REPLIES = [
            'Круто! 👍', 'Спасибо за отзыв!', 'Проверю и отвечу чуть позже 🙌',
            'Кстати, вышла новая версия мода — посмотри!', '😄'
        ];
        var form = MM.$('#chatForm');
        if (form) form.addEventListener('submit', function (e) {
            e.preventDefault();
            var inp = form.querySelector('input');
            var t = inp.value.trim();
            if (!t) return;
            msgs.push({ from: 'me', text: t, ts: now() });
            MM.set(KEY, msgs);
            inp.value = '';
            render();
            setTimeout(function () {
                msgs.push({ from: 'other', text: REPLIES[Math.floor(Math.random() * REPLIES.length)], ts: now() });
                MM.set(KEY, msgs);
                render();
            }, 1200);
        });
    }

    /* ================= УВЕДОМЛЕНИЯ ================= */
    function initNotifications() {
        var btn = MM.$('#markAllRead');
        if (btn) btn.addEventListener('click', function () {
            MM.$$('.notif.new').forEach(function (n) { n.classList.remove('new'); });
            MM.toast('Все уведомления прочитаны ✔');
        });
    }

    /* ================= MODRINTH (живой API) ================= */
    function initModrinth() {
        var grid = MM.$('#mrResults');
        if (!grid) return;
        var state = {
            type: MM.qp('type') || 'mod',
            q: MM.qp('q') || '',
            category: MM.qp('category') || '',
            mc: MM.qp('mc_version') || '',
            index: MM.qp('sort') || 'relevance',
            page: parseInt(MM.qp('page'), 10) || 1
        };
        var form = MM.$('#mrForm');
        var totalEl = MM.$('#mrTotal');

        function urlToState() {
            var params = new URLSearchParams();
            if (state.type !== 'mod') params.set('type', state.type);
            if (state.q) params.set('q', state.q);
            if (state.category) params.set('category', state.category);
            if (state.mc) params.set('mc_version', state.mc);
            if (state.index !== 'relevance') params.set('sort', state.index);
            if (state.page > 1) params.set('page', state.page);
            history.replaceState(null, '', 'modrinth.html' + (params.toString() ? '?' + params.toString() : ''));
        }

        function render(items, total) {
            if (totalEl) totalEl.innerHTML = '<strong>' + MM.fmt(total) + '</strong> проектов найдено';
            if (!items.length) {
                grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">🔍</div><h3>Ничего не найдено</h3></div>';
                return;
            }
            grid.innerHTML = items.map(function (m) {
                var cats = (m.display_categories || m.categories || []).slice(0, 4)
                    .map(function (c) { return '<span class="mr-tag">' + MM.esc(c) + '</span>'; }).join('');
                var mcv = (m.versions || []).filter(function (v) { return /^\d+\.\d+(\.\d+)?$/.test(v); });
                var lastV = mcv.length ? mcv[mcv.length - 1] : '';
                var icon = m.icon_url ? '<img src="' + MM.esc(m.icon_url) + '" alt="" loading="lazy">' :
                    '<div class="mr-no-icon">' + MM.icon('package') + '</div>';
                var pageUrl = 'modrinth-project.html?slug=' + encodeURIComponent(m.slug || m.project_id);
                return '<div class="mr-card">' +
                    '<a class="mr-card-main" href="' + pageUrl + '">' +
                        '<div class="mr-card-icon">' + icon + '</div>' +
                        '<div class="mr-card-body">' +
                            '<div class="mr-card-header"><h3>' + MM.esc(m.title) + '</h3><span class="mr-author">' + MM.icon('user', 'ic-sm') + ' ' + MM.esc(m.author) + '</span></div>' +
                            '<p class="mr-desc">' + MM.esc(m.description).slice(0, 140) + '</p>' +
                            (cats ? '<div class="mr-categories">' + cats + '</div>' : '') +
                            (lastV ? '<div class="version-info"><span class="v-badge v-mc"><span class="v-label">MC:</span> <strong>' + MM.esc(lastV) + '</strong></span></div>' : '') +
                            '<div class="mr-stats"><span>' + MM.icon('download', 'ic-sm') + ' ' + MM.fmt(m.downloads) + '</span><span>' + MM.icon('star', 'ic-sm') + ' ' + MM.fmt(m.follows) + '</span></div>' +
                        '</div>' +
                    '</a>' +
                    '<button class="mr-dl" data-dl="' + MM.esc(m.slug || m.project_id) + '" title="Скачать последнюю версию">' + MM.icon('download') + '</button>' +
                '</div>';
            }).join('');
        }

        // Быстрая загрузка последней версии прямо с карточки
        grid.addEventListener('click', function (e) {
            var btn = e.target.closest('[data-dl]');
            if (!btn) return;
            e.preventDefault();
            btn.disabled = true;
            btn.classList.add('loading');
            MM.mrDownloadLatest(btn.getAttribute('data-dl')).finally(function () {
                btn.disabled = false;
                btn.classList.remove('loading');
            });
        });

        function renderPagination(totalPages) {
            var pg = MM.$('#mrPagination');
            if (!pg) return;
            if (totalPages <= 1) { pg.innerHTML = ''; return; }
            pg.innerHTML =
                (state.page > 1 ? '<button class="page-btn" id="mrPrev">← Назад</button>' : '') +
                '<span class="page-info">Страница ' + state.page + ' из ' + totalPages + '</span>' +
                (state.page < totalPages ? '<button class="page-btn" id="mrNext">Вперёд →</button>' : '');
            var p = MM.$('#mrPrev'); if (p) p.addEventListener('click', function () { state.page--; go(); });
            var n = MM.$('#mrNext'); if (n) n.addEventListener('click', function () { state.page++; go(); });
        }

        function go() {
            urlToState();
            MM.$$('.ct-tab[data-type]').forEach(function (t) { t.classList.toggle('active', t.getAttribute('data-type') === state.type); });
            MM.$$('.sort-tab[data-sort]').forEach(function (t) { t.classList.toggle('active', t.getAttribute('data-sort') === state.index); });
            var catSel = MM.$('#mrCat'); if (catSel) catSel.value = state.category;
            var verSel = MM.$('#mrVer'); if (verSel) verSel.value = state.mc;
            var qInp = MM.$('#mrQ'); if (qInp) qInp.value = state.q;

            grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">⏳</div><h3>Загрузка с Modrinth…</h3></div>';
            var facets = [['project_type:' + state.type]];
            if (state.category) facets.push(['categories:' + state.category]);
            if (state.mc) facets.push(['versions:' + state.mc]);
            var url = 'https://api.modrinth.com/v2/search?limit=20&offset=' + (state.page - 1) * 20 +
                '&index=' + encodeURIComponent(state.index) +
                '&query=' + encodeURIComponent(state.q) +
                '&facets=' + encodeURIComponent(JSON.stringify(facets));
            fetch(url).then(function (r) { return r.json(); }).then(function (data) {
                render(data.hits || [], data.total_hits || 0);
                renderPagination(Math.ceil((data.total_hits || 0) / 20));
            }).catch(function () {
                grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">⚠️</div><h3>Не удалось загрузить данные</h3><p>Проверь подключение к интернету.</p></div>';
            });
        }

        if (form) form.addEventListener('submit', function (e) {
            e.preventDefault();
            state.q = MM.$('#mrQ').value.trim();
            state.category = MM.$('#mrCat').value;
            state.mc = MM.$('#mrVer').value;
            state.page = 1;
            go();
        });
        MM.$$('.ct-tab[data-type]').forEach(function (t) {
            t.addEventListener('click', function (e) {
                e.preventDefault();
                state.type = t.getAttribute('data-type');
                state.page = 1;
                go();
            });
        });
        MM.$$('.sort-tab[data-sort]').forEach(function (t) {
            t.addEventListener('click', function (e) {
                e.preventDefault();
                state.index = t.getAttribute('data-sort');
                state.page = 1;
                go();
            });
        });
        go();
    }

    /* ================= MODRINTH: СТРАНИЦА ПРОЕКТА + СКАЧИВАНИЕ ================= */
    function initMrProject() {
        var box = MM.$('#mrpBox');
        if (!box) return;
        var slug = MM.qp('slug') || MM.qp('p') || 'sodium';
        var verBox = MM.$('#mrpVersions');
        var mcSel = MM.$('#mrpMc');
        var ldSel = MM.$('#mrpLoader');

        var project = null, versions = [], author = '';

        function mcVersions() {
            var set = [];
            versions.forEach(function (v) {
                (v.game_versions || []).forEach(function (g) {
                    if (set.indexOf(g) === -1) set.push(g);
                });
            });
            return set;
        }
        function loaders() {
            var set = [];
            versions.forEach(function (v) {
                (v.loaders || []).forEach(function (l) {
                    if (set.indexOf(l) === -1) set.push(l);
                });
            });
            return set;
        }
        function cap(s) { return s ? s[0].toUpperCase() + s.slice(1) : s; }

        function renderVersions() {
            var mc = mcSel ? mcSel.value : '';
            var ld = ldSel ? ldSel.value : '';
            var list = versions.filter(function (v) {
                return (!mc || (v.game_versions || []).indexOf(mc) !== -1) &&
                       (!ld || (v.loaders || []).indexOf(ld) !== -1);
            });
            var cnt = MM.$('#mrpVerCount');
            if (cnt) cnt.textContent = String(list.length);
            if (!list.length) {
                verBox.innerHTML = '<div class="empty-state"><div class="empty-icon">📦</div><h3>Нет версий под выбранные фильтры</h3></div>';
                return;
            }
            verBox.innerHTML = list.slice(0, 30).map(function (v, i) {
                var file = (v.files || []).filter(function (f) { return f.primary; })[0] || (v.files || [])[0] || {};
                var mcv = (v.game_versions || []).slice(0, 4).map(function (g) { return '<span class="v-badge v-mc">' + MM.esc(g) + '</span>'; }).join('');
                var more = (v.game_versions || []).length - 4;
                var lds = (v.loaders || []).map(function (l) { return '<span class="v-badge v-loader">' + MM.esc(l) + '</span>'; }).join('');
                return '<div class="ver-item">' +
                    '<div class="ver-main">' +
                        '<div class="ver-name">' + MM.esc(v.name || v.version_number) +
                            (v.version_type ? '<span class="ver-type ver-' + MM.esc(v.version_type) + '">' + MM.esc(v.version_type) + '</span>' : '') +
                        '</div>' +
                        '<div class="ver-meta">' +
                            '<span class="ver-chips">' + mcv + (more > 0 ? '<span class="v-badge">+' + more + '</span>' : '') + lds + '</span>' +
                        '</div>' +
                        '<div class="ver-sub">' +
                            '<span>' + MM.icon('calendar', 'ic-sm') + ' ' + MM.fmtDate(v.date_published) + '</span>' +
                            '<span>' + MM.icon('download', 'ic-sm') + ' ' + MM.fmt(v.downloads) + '</span>' +
                            (file.size ? '<span>' + MM.icon('file', 'ic-sm') + ' ' + MM.fmtBytes(file.size) + '</span>' : '') +
                        '</div>' +
                    '</div>' +
                    (file.url ?
                        '<button class="ver-dl" data-url="' + MM.esc(file.url) + '" data-file="' + MM.esc(file.filename || '') + '">' +
                            MM.icon('download') + '<span>Скачать</span>' +
                        '</button>' : '') +
                '</div>';
            }).join('');
        }

        function renderProject() {
            var icon = project.icon_url ? '<img src="' + MM.esc(project.icon_url) + '" alt="">' :
                '<div class="mrpp-noicon">' + MM.icon('package') + '</div>';
            var cats = (project.categories || []).map(function (c) { return '<span class="mr-tag">' + MM.esc(c) + '</span>'; }).join('');
            var lds = (project.loaders || []).map(function (l) { return '<span class="v-badge v-loader">' + MM.esc(l) + '</span>'; }).join('');
            var gallery = (project.gallery || []).slice(0, 6);
            box.innerHTML =
                '<a href="modrinth.html" class="back-btn">' + MM.icon('arrow_left', 'ic-sm') + ' К поиску Modrinth</a>' +
                '<div class="mrpp-head">' +
                    '<div class="mrpp-icon">' + icon + '</div>' +
                    '<div class="mrpp-info">' +
                        '<h1>' + MM.esc(project.title) + '</h1>' +
                        (author ? '<div class="mrpp-author">' + MM.icon('user', 'ic-sm') + ' ' + MM.esc(author) + '</div>' : '') +
                        '<p class="mrpp-desc">' + MM.esc(project.description || '') + '</p>' +
                        '<div class="mrpp-stats">' +
                            '<span>' + MM.icon('download', 'ic-sm') + ' <strong>' + MM.fmt(project.downloads) + '</strong> скачиваний</span>' +
                            '<span>' + MM.icon('heart', 'ic-sm') + ' <strong>' + MM.fmt(project.followers) + '</strong> подписчиков</span>' +
                            '<span>' + MM.icon('clock', 'ic-sm') + ' обновлён ' + MM.fmtDate(project.updated) + '</span>' +
                        '</div>' +
                        '<div class="mrpp-tags">' + cats + lds + '</div>' +
                        '<div class="mrpp-actions">' +
                            '<button class="btn-download-big" id="mrpLatest">' + MM.icon('download', 'ic-sm') + ' Скачать последнюю версию</button>' +
                            '<a class="btn-hero btn-hero-ghost mrp-ext" href="https://modrinth.com/project/' + MM.esc(project.slug || slug) + '" target="_blank" rel="noopener">На Modrinth ↗</a>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
                (gallery.length ?
                    '<div class="mrp-gallery">' + gallery.map(function (g) {
                        return '<img src="' + MM.esc(g.url) + '" alt="" loading="lazy" onclick="openLightbox(\'' + MM.esc(g.url) + '\')">';
                    }).join('') + '</div>' : '') +
                (project.body ? '' : '');

            document.title = project.title + ' — MineMods × Modrinth';
            var lat = MM.$('#mrpLatest');
            if (lat) lat.addEventListener('click', function () { MM.mrDownloadLatest(slug); });
        }

        // Фильтры версий
        function fillFilters() {
            if (mcSel) {
                mcSel.innerHTML = '<option value="">Все версии MC</option>' +
                    mcVersions().map(function (v) { return '<option value="' + MM.esc(v) + '">' + MM.esc(v) + '</option>'; }).join('');
            }
            if (ldSel) {
                ldSel.innerHTML = '<option value="">Все загрузчики</option>' +
                    loaders().map(function (l) { return '<option value="' + MM.esc(l) + '">' + MM.esc(cap(l)) + '</option>'; }).join('');
            }
        }
        if (mcSel) mcSel.addEventListener('change', renderVersions);
        if (ldSel) ldSel.addEventListener('change', renderVersions);

        // Клик по кнопке скачивания версии
        if (verBox) verBox.addEventListener('click', function (e) {
            var b = e.target.closest('.ver-dl');
            if (!b) return;
            MM.mrTriggerFile(b.getAttribute('data-url'), b.getAttribute('data-file'));
            MM.toast('⬇ Скачивается: ' + (b.getAttribute('data-file') || 'файл'));
        });

        // Лайтбокс для галереи
        window.openLightbox = window.openLightbox || function (src) {
            var lb = MM.$('#lightbox'); if (!lb) return;
            MM.$('#lightbox-img').src = src;
            lb.classList.add('active');
        };
        window.closeLightbox = window.closeLightbox || function () {
            var lb = MM.$('#lightbox'); if (lb) lb.classList.remove('active');
        };

        // Загрузка данных (проект + версии + автор параллельно)
        box.innerHTML = '<div class="empty-state"><div class="empty-icon">⏳</div><h3>Загрузка проекта…</h3></div>';
        if (verBox) verBox.innerHTML = '';
        var pProject = fetch('https://api.modrinth.com/v2/project/' + encodeURIComponent(slug)).then(function (r) {
            if (!r.ok) throw new Error('http');
            return r.json();
        });
        var pVersions = fetch('https://api.modrinth.com/v2/project/' + encodeURIComponent(slug) + '/version').then(function (r) { return r.ok ? r.json() : []; });
        var pAuthor = fetch('https://api.modrinth.com/v2/project/' + encodeURIComponent(slug) + '/members').then(function (r) { return r.ok ? r.json() : []; });

        Promise.all([pProject, pVersions, pAuthor]).then(function (arr) {
            project = arr[0];
            versions = (arr[1] || []);
            author = (arr[2] && arr[2][0] && arr[2][0].user && arr[2][0].user.username) || '';
            renderProject();
            fillFilters();
            renderVersions();
        }).catch(function () {
            box.innerHTML = '<div class="empty-state"><div class="empty-icon">⚠️</div>' +
                '<h3>Проект не найден или API недоступен</h3>' +
                '<p>Проверь ссылку или попробуй позже.</p>' +
                '<a href="modrinth.html" class="btn-download-big">← К поиску Modrinth</a></div>';
        });
    }

    /* ================= GITHUB (живой API) ================= */
    function initGitHub() {
        var grid = MM.$('#ghResults');
        if (!grid) return;
        var KEYWORDS = {
            mod: 'minecraft mod', shader: 'minecraft shaders', plugin: 'minecraft plugin',
            resourcepack: 'minecraft resource pack', modpack: 'minecraft modpack',
            datapack: 'minecraft datapack', map: 'minecraft map'
        };
        var state = {
            type: MM.qp('type') || 'mod',
            q: MM.qp('q') || '',
            sort: MM.qp('sort') || 'stars',
            page: parseInt(MM.qp('page'), 10) || 1
        };
        var form = MM.$('#ghForm');
        var totalEl = MM.$('#ghTotal');

        function urlToState() {
            var params = new URLSearchParams();
            if (state.type !== 'mod') params.set('type', state.type);
            if (state.q) params.set('q', state.q);
            if (state.sort !== 'stars') params.set('sort', state.sort);
            if (state.page > 1) params.set('page', state.page);
            history.replaceState(null, '', 'github.html' + (params.toString() ? '?' + params.toString() : ''));
        }

        function render(items, total) {
            if (totalEl) totalEl.innerHTML = '<strong>' + MM.fmt(total) + '</strong> репозиториев';
            if (!items.length) {
                grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">🔍</div><h3>Ничего не найдено</h3><p>Попробуй другой запрос</p></div>';
                return;
            }
            grid.innerHTML = items.map(function (r) {
                var topics = (r.topics || []).slice(0, 4).map(function (t) { return '<span class="mr-tag gh-tag">' + MM.esc(t) + '</span>'; }).join('');
                return '<a class="mr-card gh-card" href="' + MM.esc(r.html_url) + '" target="_blank" rel="noopener">' +
                    '<div class="mr-card-icon"><img src="' + MM.esc(r.owner.avatar_url) + '" alt=""></div>' +
                    '<div class="mr-card-body">' +
                        '<div class="mr-card-header"><h3>' + MM.esc(r.name) + '</h3><span class="gh-author">' + MM.esc(r.owner.login) + '</span></div>' +
                        '<p class="mr-desc">' + MM.esc((r.description || 'Без описания')).slice(0, 140) + '</p>' +
                        (topics ? '<div class="mr-categories">' + topics + '</div>' : '') +
                        '<div class="mr-stats"><span>' + MM.icon('star', 'ic-sm') + ' ' + MM.fmt(r.stargazers_count) + '</span>' +
                        '<span>' + MM.icon('fork', 'ic-sm') + ' ' + MM.fmt(r.forks_count) + '</span>' +
                        (r.language ? '<span class="gh-lang">' + MM.esc(r.language) + '</span>' : '') +
                        '<span>' + MM.icon('calendar', 'ic-sm') + ' ' + MM.esc(String(r.updated_at || '').slice(0, 10)) + '</span></div>' +
                    '</div></a>';
            }).join('');
        }

        function go() {
            urlToState();
            MM.$$('.ct-tab[data-type]').forEach(function (t) { t.classList.toggle('active', t.getAttribute('data-type') === state.type); });
            MM.$$('.sort-tab[data-sort]').forEach(function (t) { t.classList.toggle('active', t.getAttribute('data-sort') === state.sort); });
            var qInp = MM.$('#ghQ'); if (qInp) qInp.value = state.q;

            grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">⏳</div><h3>Загрузка с GitHub…</h3></div>';
            var q = (KEYWORDS[state.type] || 'minecraft') + (state.q ? ' ' + state.q : '');
            var url = 'https://api.github.com/search/repositories?q=' + encodeURIComponent(q) +
                '&sort=' + encodeURIComponent(state.sort) + '&order=desc&per_page=20&page=' + state.page;
            fetch(url, { headers: { 'Accept': 'application/vnd.github+json' } })
                .then(function (r) {
                    if (r.status === 403 || r.status === 429) throw new Error('rate');
                    return r.json();
                }).then(function (data) {
                    render(data.items || [], Math.min(data.total_count || 0, 1000));
                    var pg = MM.$('#ghPagination');
                    if (pg) {
                        var totalPages = Math.min(Math.ceil((data.total_count || 0) / 20), 50);
                        pg.innerHTML = totalPages > 1 ?
                            (state.page > 1 ? '<button class="page-btn" id="ghPrev">← Назад</button>' : '') +
                            '<span class="page-info">Страница ' + state.page + ' из ' + totalPages + '</span>' +
                            (state.page < totalPages ? '<button class="page-btn" id="ghNext">Вперёд →</button>' : '') : '';
                        var p = MM.$('#ghPrev'); if (p) p.addEventListener('click', function () { state.page--; go(); });
                        var n = MM.$('#ghNext'); if (n) n.addEventListener('click', function () { state.page++; go(); });
                    }
                }).catch(function () {
                    grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">⚠️</div>' +
                        '<h3>GitHub API недоступен</h3><p>Возможно, превышен лимит запросов (60/час без ключа). Попробуй позже.</p></div>';
                });
        }

        if (form) form.addEventListener('submit', function (e) {
            e.preventDefault();
            state.q = MM.$('#ghQ').value.trim();
            state.page = 1;
            go();
        });
        MM.$$('.ct-tab[data-type]').forEach(function (t) {
            t.addEventListener('click', function (e) {
                e.preventDefault();
                state.type = t.getAttribute('data-type');
                state.page = 1;
                go();
            });
        });
        MM.$$('.sort-tab[data-sort]').forEach(function (t) {
            t.addEventListener('click', function (e) {
                e.preventDefault();
                state.sort = t.getAttribute('data-sort');
                state.page = 1;
                go();
            });
        });
        go();
    }

    /* ---------------- Init ---------------- */
    document.addEventListener('DOMContentLoaded', function () {
        MM.applyTheme();
        renderTopbar();
        renderSidebarFooter();
        guardProtected();
        initCounters();
        initAuthForms();

        switch (document.body.getAttribute('data-page')) {
            case 'index':         initIndex(); break;
            case 'mod':           initModPage(); break;
            case 'upload':        initUpload(); break;
            case 'profile':       initProfile(); break;
            case 'settings':      initSettings(); break;
            case 'favorites':     initFavorites(); break;
            case 'feed':          initFeed(); break;
            case 'achievements':  initAchievements(); break;
            case 'user':          initUserPage(); break;
            case 'activity':      initActivity(); break;
            case 'chat':          initChat(); break;
            case 'notifications': initNotifications(); break;
            case 'modrinth':      initModrinth(); break;
            case 'mrproject':     initMrProject(); break;
            case 'github':        initGitHub(); break;
        }
    });
})();
