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
            '<p class="mod-meta"><span>v' + MM.esc(m.version) + '</span> <span>•</span> <span>👤 ' +
                '<a href="user.html?u=' + encodeURIComponent(m.author) + '" class="author-link">' + MM.esc(m.author) + '</a></span></p>' +
            '<p class="mod-desc">' + MM.esc(m.desc) + '</p>' +
            (tags ? '<div class="mod-tags">' + tags + '</div>' : '') +
            '<div class="mod-footer">' +
                '<div class="mod-stats">' +
                    '<span class="stat-item">⬇ ' + MM.fmt(m.downloads) + '</span>' +
                    '<span class="stat-item">❤ ' + MM.fmt(m.likes) + '</span>' +
                    '<span class="stat-item">👁 ' + MM.fmt(m.views) + '</span>' +
                '</div>' +
                '<a href="mod.html?m=' + MM.esc(m.id) + '#download" class="btn-download">Скачать</a>' +
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
            '<a href="notifications.html" class="topbar-icon" title="Уведомления">🔔</a>' +
            '<a href="messages.html" class="topbar-icon" title="Сообщения">💌</a>' +
            '<div class="user-menu" role="menu">' +
                '<button class="user-menu-btn" id="userMenuBtn" aria-haspopup="true">' + avatar +
                    '<span class="user-menu-name">' + name + '</span>' +
                    '<span class="dropdown-arrow">▼</span>' +
                '</button>' +
                '<div class="user-dropdown" role="menu">' +
                    '<a href="profile.html" class="dropdown-item">👤 Профиль</a>' +
                    '<a href="settings.html" class="dropdown-item">⚙️ Настройки</a>' +
                    '<a href="activity.html" class="dropdown-item">📅 Активность</a>' +
                    '<div class="dropdown-divider"></div>' +
                    '<a href="#" class="dropdown-item logout" id="logoutBtn">🚪 Выйти</a>' +
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
            if (icon) icon.textContent = liked ? '❤' : '🤍';
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
                '<div class="stat-card"><div class="stat-num">' + mods.length + '</div><div class="stat-label">📦 Модов</div></div>' +
                '<div class="stat-card"><div class="stat-num">' + MM.fmt(dls) + '</div><div class="stat-label">⬇ Скачиваний</div></div>' +
                '<div class="stat-card"><div class="stat-num">' + MM.fmt(likes) + '</div><div class="stat-label">❤ Лайков</div></div>' +
                '<div class="stat-card"><div class="stat-num">0</div><div class="stat-label">👥 Подписчиков</div></div>' +
                '<div class="stat-card"><div class="stat-num">' + follows + '</div><div class="stat-label">📡 Подписок</div></div>' +
            '</div>' +
            '<h3 class="section-title">📦 Мои моды</h3>' +
            '<div class="my-mods-grid">' +
                (mods.length ? mods.map(function (m) {
                    return '<div class="my-mod-card">' +
                        '<div class="mod-category">' + MM.esc(m.category) + '</div>' +
                        '<a href="mod.html" class="my-mod-title">' + MM.esc(m.title) + '</a>' +
                        '<div class="my-mod-meta"><span>MC ' + MM.esc(m.mc) + '</span>' +
                        '<span>⬇ ' + MM.fmt(m.downloads) + ' ❤ ' + MM.fmt(m.likes) + ' 👁 ' + MM.fmt(m.views) + '</span></div>' +
                        '<button class="btn-delete" data-del="' + m.id + '">🗑 Удалить</button>' +
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
                    '<a href="chat.html?u=' + encodeURIComponent(name) + '" class="btn-subscribe" style="background:var(--bg-card);color:var(--text-main);border:2px solid var(--border)">💌 Написать</a>' +
                    '<a href="activity.html" class="btn-subscribe" style="background:var(--bg-card);color:var(--text-main);border:2px solid var(--border)">📅 Активность</a>' +
                '</div></div>' +
            '</div>' +
            '<div class="profile-stats">' +
                '<div class="stat-card"><div class="stat-num">' + mods.length + '</div><div class="stat-label">📦 Модов</div></div>' +
                '<div class="stat-card"><div class="stat-num">' + MM.fmt(dls) + '</div><div class="stat-label">⬇ Скачиваний</div></div>' +
                '<div class="stat-card"><div class="stat-num">' + MM.fmt(lk) + '</div><div class="stat-label">❤ Лайков</div></div>' +
            '</div>' +
            '<h3 class="section-title">📦 Моды автора</h3>' +
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
                var icon = m.icon_url ? '<img src="' + MM.esc(m.icon_url) + '" alt="">' : '<div class="mr-no-icon">📦</div>';
                return '<a class="mr-card" href="https://modrinth.com/project/' + MM.esc(m.slug) + '" target="_blank" rel="noopener">' +
                    '<div class="mr-card-icon">' + icon + '</div>' +
                    '<div class="mr-card-body">' +
                        '<div class="mr-card-header"><h3>' + MM.esc(m.title) + '</h3><span class="mr-author">' + MM.esc(m.author) + '</span></div>' +
                        '<p class="mr-desc">' + MM.esc(m.description).slice(0, 140) + '</p>' +
                        (cats ? '<div class="mr-categories">' + cats + '</div>' : '') +
                        (lastV ? '<div class="version-info"><span class="v-badge v-mc"><span class="v-label">MC:</span> <strong>' + MM.esc(lastV) + '</strong></span></div>' : '') +
                        '<div class="mr-stats"><span>⬇ ' + MM.fmt(m.downloads) + '</span><span>⭐ ' + MM.fmt(m.follows) + '</span></div>' +
                    '</div></a>';
            }).join('');
        }

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
                        '<div class="mr-stats"><span>⭐ ' + MM.fmt(r.stargazers_count) + '</span>' +
                        '<span>🍴 ' + MM.fmt(r.forks_count) + '</span>' +
                        (r.language ? '<span class="gh-lang">' + MM.esc(r.language) + '</span>' : '') +
                        '<span>📅 ' + MM.esc(String(r.updated_at || '').slice(0, 10)) + '</span></div>' +
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
            case 'github':        initGitHub(); break;
        }
    });
})();
