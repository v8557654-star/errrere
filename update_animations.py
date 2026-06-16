# -*- coding: utf-8 -*-
import os

print("✨ Добавляю анимации...")

style_css = '''* { margin: 0; padding: 0; box-sizing: border-box; }

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 5px rgba(34, 255, 136, 0.3); }
    50% { box-shadow: 0 0 20px rgba(34, 255, 136, 0.6); }
}

@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

body {
    font-family: 'Segoe UI', Tahoma, sans-serif;
    background: linear-gradient(-45deg, #0f1626, #1a2338, #0f1626, #16213e);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
    color: #e0e6ed;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.navbar {
    background: rgba(26, 35, 56, 0.95);
    backdrop-filter: blur(10px);
    padding: 15px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 20px rgba(0,0,0,0.5);
    position: sticky;
    top: 0;
    z-index: 100;
    animation: slideIn 0.5s ease-out;
}

.logo {
    font-size: 24px;
    font-weight: bold;
    background: linear-gradient(45deg, #22ff88, #00d4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-decoration: none;
    transition: transform 0.3s;
    display: inline-block;
}

.logo:hover {
    transform: scale(1.1) rotate(-5deg);
}

.nav-links a {
    color: #aab;
    text-decoration: none;
    margin-left: 20px;
    transition: all 0.3s;
    position: relative;
}

.nav-links a::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 0;
    height: 2px;
    background: #22ff88;
    transition: width 0.3s;
}

.nav-links a:hover {
    color: #22ff88;
}

.nav-links a:hover::after {
    width: 100%;
}

.btn-register {
    background: linear-gradient(45deg, #22ff88, #00d4ff);
    color: #0f1626 !important;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: bold;
    transition: all 0.3s;
}

.btn-register:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(34, 255, 136, 0.4);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    flex: 1;
    width: 100%;
    animation: fadeIn 0.6s ease-out;
}

.hero {
    text-align: center;
    padding: 60px 0 30px;
    animation: fadeIn 0.8s ease-out;
}

.hero h1 {
    font-size: 48px;
    background: linear-gradient(45deg, #22ff88, #00d4ff, #22ff88);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 15px;
    animation: gradient 3s linear infinite;
    display: inline-block;
}

.hero p {
    color: #889;
    font-size: 18px;
    animation: fadeIn 1s ease-out 0.3s backwards;
}

.search-bar {
    margin: 30px 0;
    animation: fadeIn 0.7s ease-out 0.2s backwards;
}

.search-bar form {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.search-bar input[type="text"] {
    flex: 1;
    min-width: 200px;
    padding: 14px 18px;
    border: 2px solid #233554;
    border-radius: 10px;
    background: rgba(26, 35, 56, 0.7);
    color: #fff;
    font-size: 16px;
    transition: all 0.3s;
}

.search-bar input[type="text"]:focus {
    border-color: #22ff88;
    outline: none;
    box-shadow: 0 0 15px rgba(34, 255, 136, 0.3);
    transform: translateY(-2px);
}

.search-bar select {
    padding: 14px;
    border: 2px solid #233554;
    border-radius: 10px;
    background: rgba(26, 35, 56, 0.7);
    color: #fff;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s;
}

.search-bar select:hover, .search-bar select:focus {
    border-color: #22ff88;
    transform: translateY(-2px);
}

.search-bar button {
    padding: 14px 32px;
    background: linear-gradient(45deg, #22ff88, #00d4ff);
    color: #0f1626;
    border: none;
    border-radius: 10px;
    font-weight: bold;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s;
    position: relative;
    overflow: hidden;
}

.search-bar button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(34, 255, 136, 0.4);
}

.search-bar button:active {
    transform: translateY(0);
}

.mods-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
}

.mod-card {
    background: rgba(26, 35, 56, 0.7);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 22px;
    border: 1px solid #233554;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    animation: fadeIn 0.6s ease-out backwards;
    position: relative;
    overflow: hidden;
}

.mod-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, #22ff88, transparent);
    transition: left 0.6s;
}

.mod-card:hover::before {
    left: 100%;
}

.mod-card:nth-child(1) { animation-delay: 0.1s; }
.mod-card:nth-child(2) { animation-delay: 0.15s; }
.mod-card:nth-child(3) { animation-delay: 0.2s; }
.mod-card:nth-child(4) { animation-delay: 0.25s; }
.mod-card:nth-child(5) { animation-delay: 0.3s; }
.mod-card:nth-child(6) { animation-delay: 0.35s; }
.mod-card:nth-child(7) { animation-delay: 0.4s; }
.mod-card:nth-child(8) { animation-delay: 0.45s; }
.mod-card:nth-child(n+9) { animation-delay: 0.5s; }

.mod-card:hover {
    transform: translateY(-8px) scale(1.02);
    border-color: #22ff88;
    box-shadow: 0 15px 40px rgba(34, 255, 136, 0.25);
}

.mod-category {
    display: inline-block;
    background: linear-gradient(45deg, #22ff88, #00d4ff);
    color: #0f1626;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
    margin-bottom: 12px;
    transition: transform 0.3s;
}

.mod-card:hover .mod-category {
    transform: scale(1.1);
}

.mod-card h3 a {
    color: #fff;
    text-decoration: none;
    font-size: 20px;
    transition: color 0.3s;
}

.mod-card:hover h3 a {
    color: #22ff88;
}

.mod-meta {
    color: #778;
    font-size: 13px;
    margin: 8px 0;
}

.mod-desc {
    color: #aab;
    font-size: 14px;
    margin: 12px 0;
    line-height: 1.5;
}

.mod-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #233554;
}

.btn-download {
    background: linear-gradient(45deg, #22ff88, #00d4ff);
    color: #0f1626;
    padding: 9px 20px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
    font-size: 14px;
    transition: all 0.3s;
    display: inline-block;
}

.btn-download:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 8px 20px rgba(34, 255, 136, 0.4);
}

.mod-detail {
    max-width: 800px;
    margin: 0 auto;
    animation: fadeIn 0.5s ease-out;
}

.mod-header h1 {
    font-size: 36px;
    margin: 12px 0;
    color: #fff;
    animation: slideIn 0.6s ease-out;
}

.mod-info table {
    width: 100%;
    margin: 20px 0;
    background: rgba(26, 35, 56, 0.7);
    border-radius: 12px;
    overflow: hidden;
    border-collapse: collapse;
    animation: fadeIn 0.7s ease-out 0.1s backwards;
}

.mod-info td {
    padding: 14px 18px;
    border-bottom: 1px solid #233554;
    transition: background 0.3s;
}

.mod-info tr:hover td {
    background: rgba(34, 255, 136, 0.05);
}

.mod-info td:first-child {
    color: #778;
    width: 40%;
}

.mod-description {
    margin: 30px 0;
    line-height: 1.7;
    background: rgba(26, 35, 56, 0.7);
    padding: 22px;
    border-radius: 12px;
    animation: fadeIn 0.7s ease-out 0.2s backwards;
}

.mod-description h3 {
    color: #22ff88;
    margin-bottom: 12px;
}

.btn-download-big {
    display: inline-block;
    background: linear-gradient(45deg, #22ff88, #00d4ff);
    background-size: 200% auto;
    color: #0f1626;
    padding: 18px 50px;
    border-radius: 12px;
    text-decoration: none;
    font-size: 18px;
    font-weight: bold;
    margin: 20px 0;
    transition: all 0.4s;
    animation: pulse 2s ease-in-out infinite;
}

.btn-download-big:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 15px 30px rgba(34, 255, 136, 0.5);
    background-position: right center;
    animation: none;
}

.form-page {
    max-width: 450px;
    margin: 40px auto;
    background: rgba(26, 35, 56, 0.8);
    backdrop-filter: blur(10px);
    padding: 35px;
    border-radius: 16px;
    border: 1px solid #233554;
    animation: fadeIn 0.5s ease-out;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.form-wide { max-width: 600px; }

.form-page h2 {
    text-align: center;
    margin-bottom: 25px;
    background: linear-gradient(45deg, #22ff88, #00d4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.form-page input,
.form-page select,
.form-page textarea {
    width: 100%;
    padding: 13px 15px;
    margin-bottom: 15px;
    border: 2px solid #233554;
    border-radius: 10px;
    background: #0f1626;
    color: #fff;
    font-size: 15px;
    font-family: inherit;
    transition: all 0.3s;
}

.form-page input:focus,
.form-page select:focus,
.form-page textarea:focus {
    border-color: #22ff88;
    outline: none;
    box-shadow: 0 0 15px rgba(34, 255, 136, 0.2);
    transform: translateY(-1px);
}

.form-page button {
    width: 100%;
    padding: 14px;
    background: linear-gradient(45deg, #22ff88, #00d4ff);
    color: #0f1626;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s;
}

.form-page button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(34, 255, 136, 0.4);
}

.form-page p {
    text-align: center;
    margin-top: 15px;
    color: #778;
}

.form-page p a {
    color: #22ff88;
    transition: color 0.3s;
}

.form-page p a:hover {
    color: #00d4ff;
}

.file-label {
    display: block;
    background: #0f1626;
    padding: 25px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 15px;
    cursor: pointer;
    border: 2px dashed #22ff88;
    color: #aab;
    transition: all 0.3s;
}

.file-label:hover {
    background: rgba(34, 255, 136, 0.05);
    border-color: #00d4ff;
    transform: scale(1.02);
}

.file-label input {
    margin-top: 10px;
}

.alert {
    padding: 14px 18px;
    border-radius: 10px;
    margin-bottom: 15px;
    animation: slideIn 0.4s ease-out;
}

.alert-success {
    background: rgba(30, 58, 47, 0.8);
    color: #4ade80;
    border-left: 4px solid #4ade80;
}

.alert-error {
    background: rgba(58, 30, 47, 0.8);
    color: #ff7777;
    border-left: 4px solid #ff7777;
}

.profile-page {
    animation: fadeIn 0.5s ease-out;
}

.profile-page h3 {
    margin-top: 30px;
    color: #22ff88;
    margin-bottom: 15px;
}

.my-mod {
    display: flex;
    align-items: center;
    gap: 15px;
    background: rgba(26, 35, 56, 0.7);
    padding: 14px 18px;
    border-radius: 10px;
    margin: 10px 0;
    transition: all 0.3s;
    animation: slideIn 0.4s ease-out backwards;
}

.my-mod:hover {
    transform: translateX(5px);
    background: rgba(26, 35, 56, 0.9);
    border-left: 3px solid #22ff88;
}

.my-mod a {
    flex: 1;
    color: #fff;
    text-decoration: none;
    font-weight: bold;
    transition: color 0.3s;
}

.my-mod a:hover {
    color: #22ff88;
}

.btn-delete {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    transition: transform 0.3s;
}

.btn-delete:hover {
    transform: scale(1.3) rotate(-10deg);
}

.no-mods {
    text-align: center;
    color: #778;
    padding: 60px 20px;
    font-size: 18px;
    grid-column: 1 / -1;
    animation: float 3s ease-in-out infinite;
}

footer {
    text-align: center;
    padding: 30px;
    color: #445;
    margin-top: 50px;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #0f1626;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(45deg, #22ff88, #00d4ff);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(45deg, #00d4ff, #22ff88);
}

/* Loader для кнопок */
.loading {
    position: relative;
    color: transparent !important;
}

.loading::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    top: 50%;
    left: 50%;
    margin: -10px 0 0 -10px;
    border: 3px solid rgba(15, 22, 38, 0.3);
    border-top-color: #0f1626;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@media (max-width: 600px) {
    .navbar { flex-direction: column; gap: 12px; }
    .search-bar form { flex-direction: column; }
    .mods-grid { grid-template-columns: 1fr; }
    .hero h1 { font-size: 32px; }
}
'''

os.makedirs("static/css", exist_ok=True)
with open("static/css/style.css", "w", encoding="utf-8") as f:
    f.write(style_css)

print("✅ Анимации добавлены!")
print("\n📤 Теперь залей на сайт:")
print("   git add .")
print('   git commit -m "Добавил анимации"')
print("   git push")
print("\nЗатем на PythonAnywhere в Bash:")
print("   cd ~/mysite")
print("   git pull")
print("\nИ нажми Reload на вкладке Web")
