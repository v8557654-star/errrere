# -*- coding: utf-8 -*-
import os
import re

print("🗑️ Удаляю CurseForge...")

# ============= ПАТЧИМ app.py =============
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# 1. Убираем импорт CURSEFORGE_API_KEY
app_code = re.sub(
    r"try:\s*\n\s*from config import CURSEFORGE_API_KEY\s*\nexcept ImportError:\s*\n\s*CURSEFORGE_API_KEY = ''",
    "",
    app_code
)
app_code = app_code.replace(
    "from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET\ntry:\n    from config import CURSEFORGE_API_KEY\nexcept ImportError:\n    CURSEFORGE_API_KEY = ''",
    "from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET"
)

# 2. Удаляем весь блок CurseForge (от "# ===== CURSEFORGE API =====" до конца роутов CF)
# Находим начало и удаляем всё до следующего комментария или функции
cf_start = app_code.find("# ===== CURSEFORGE API =====")
if cf_start != -1:
    # Ищем конец — следующий блок (или with app.app_context, или другой комментарий верхнего уровня)
    cf_end = app_code.find("with app.app_context():", cf_start)
    if cf_end != -1:
        app_code = app_code[:cf_start] + app_code[cf_end:]
        print("  ✅ Удалён блок CurseForge из app.py")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)
print("  ✅ app.py обновлён")

# ============= ПАТЧИМ base.html =============
with open("templates/base.html", "r", encoding="utf-8") as f:
    base_html = f.read()

# Удаляем пункт меню CurseForge
old_cf_menu = '''
            <a href="{{ url_for('curseforge_search') }}" class="nav-item curseforge-item">
                <span class="nav-icon">🔥</span><span>CurseForge</span>
            </a>'''

base_html = base_html.replace(old_cf_menu, "")

with open("templates/base.html", "w", encoding="utf-8") as f:
    f.write(base_html)
print("  ✅ templates/base.html (убран пункт меню)")

# ============= УДАЛЯЕМ ШАБЛОНЫ CurseForge =============
for f in ["templates/curseforge_search.html", "templates/curseforge_mod.html"]:
    if os.path.exists(f):
        os.remove(f)
        print(f"  ✅ Удалён {f}")

# ============= ПОЧИСТИМ config.py от ключа CF =============
if os.path.exists("config.py"):
    with open("config.py", "r", encoding="utf-8") as f:
        cfg = f.read()
    # Удаляем строку с CURSEFORGE_API_KEY
    cfg = re.sub(r'\nCURSEFORGE_API_KEY\s*=\s*".*?"\n?', '\n', cfg)
    cfg = re.sub(r'CURSEFORGE_API_KEY\s*=\s*".*?"\n?', '', cfg)
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(cfg)
    print("  ✅ config.py очищен")

print("\n🎉 CurseForge полностью удалён!")
print("\n📤 Шаги:")
print("\n1. Залей на GitHub:")
print("   git add .")
print('   git commit -m "Remove CurseForge"')
print("   git push --force origin main")
print("\n2. На PythonAnywhere в Bash:")
print("   cd ~/mysite")
print("   git fetch origin main")
print("   git reset --hard origin/main")
print("\n3. ⚠️ Удали ключ из config.py на сервере:")
print("   nano ~/mysite/config.py")
print("   Удали строку: CURSEFORGE_API_KEY = ...")
print("   Сохрани: Ctrl+O, Enter, Ctrl+X")
print("\n4. Reload на вкладке Web 🟢")