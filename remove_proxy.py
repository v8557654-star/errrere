# -*- coding: utf-8 -*-
import os

print("🗑️ Убираю прокси для скачивания...")

# ============= ПАТЧИМ modrinth_project.html =============
with open("templates/modrinth_project.html", "r", encoding="utf-8") as f:
    mr_html = f.read()

# Возвращаем прямые ссылки
old_link = '<a href="{{ url_for(\'modrinth_download\', url=f.url, filename=f.filename) }}" class="mr-version-item">'
new_link = '<a href="{{ f.url }}" class="mr-version-item" download target="_blank">'

mr_html = mr_html.replace(old_link, new_link)

with open("templates/modrinth_project.html", "w", encoding="utf-8") as f:
    f.write(mr_html)
print("  ✅ templates/modrinth_project.html (прямые ссылки)")

# ============= ПАТЧИМ app.py =============
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# Возвращаем простой redirect вместо stream
old_route = '''@app.route('/modrinth/download')
def modrinth_download():
    """Скачивание файла с Modrinth через прокси (без перехода)"""
    file_url = request.args.get('url', '')
    filename = request.args.get('filename', 'mod.jar')
    if not file_url.startswith('https://cdn.modrinth.com'):
        abort(400)
    try:
        r = requests.get(file_url, stream=True, headers=MODRINTH_HEADERS, timeout=60)
        if r.status_code != 200:
            abort(404)
        return Response(
            stream_with_context(r.iter_content(chunk_size=8192)),
            content_type='application/java-archive',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': r.headers.get('Content-Length', ''),
            }
        )
    except Exception as e:
        flash(f'Ошибка скачивания: {str(e)}', 'error')
        return redirect(url_for('modrinth_search'))'''

new_route = '''@app.route('/modrinth/download')
def modrinth_download():
    """Редирект на скачивание с Modrinth"""
    file_url = request.args.get('url', '')
    if not file_url.startswith('https://cdn.modrinth.com'):
        abort(400)
    return redirect(file_url)'''

app_code = app_code.replace(old_route, new_route)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)
print("  ✅ app.py (прокси удалён)")

print("\n🎉 ГОТОВО!")
print("\nТеперь скачивание идёт напрямую с серверов Modrinth (быстрее).")
print("\n📤 Шаги:")
print("\n1. git add . && git commit -m 'Remove proxy downloads' && git push --force origin main")
print("\n2. На PythonAnywhere в Bash:")
print("   cd ~/mysite")
print("   git fetch origin main")
print("   git reset --hard origin/main")
print("\n3. Reload на вкладке Web 🟢")