# -*- coding: utf-8 -*-
import os

print("⛏ Добавляю анимацию кирки...")

extra_css = '''

/* ===== АНИМАЦИЯ КИРКИ ===== */
.logo {
    overflow: visible;
}

.logo-icon {
    display: inline-block;
    transform-origin: 70% 70%;
    transition: transform 0.3s ease;
    cursor: pointer;
}

/* При наведении на ВЕСЬ логотип — кирка шевелится */
.logo:hover .logo-icon {
    animation: pickaxeMine 0.6s ease-in-out infinite;
}

@keyframes pickaxeMine {
    0% {
        transform: rotate(0deg);
    }
    25% {
        transform: rotate(-25deg) translateY(-2px);
    }
    50% {
        transform: rotate(15deg) translateY(2px);
    }
    75% {
        transform: rotate(-10deg);
    }
    100% {
        transform: rotate(0deg);
    }
}

/* Эффект пыли при клике */
.logo:active .logo-icon {
    animation: pickaxeHit 0.3s ease-out;
}

@keyframes pickaxeHit {
    0% { transform: rotate(-30deg) translateY(-3px); }
    100% { transform: rotate(20deg) translateY(3px); }
}

/* Лёгкое покачивание текста при наведении */
.logo:hover .logo-text {
    animation: textShake 0.5s ease-in-out;
}

@keyframes textShake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-1px); }
    75% { transform: translateX(1px); }
}

/* Свечение вокруг логотипа при наведении */
.logo {
    position: relative;
    transition: all 0.3s;
}

.logo::before {
    content: '';
    position: absolute;
    top: -10px;
    left: -10px;
    right: -10px;
    bottom: -10px;
    background: radial-gradient(circle, rgba(34, 255, 136, 0.2), transparent 70%);
    opacity: 0;
    transition: opacity 0.4s;
    pointer-events: none;
    border-radius: 50%;
}

.logo:hover::before {
    opacity: 1;
}

/* Если анимации выключены */
[data-animations="off"] .logo:hover .logo-icon,
[data-animations="off"] .logo:active .logo-icon,
[data-animations="off"] .logo:hover .logo-text {
    animation: none !important;
}
'''

css_path = "static/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    existing_css = f.read()

if "/* ===== АНИМАЦИЯ КИРКИ ===== */" not in existing_css:
    with open(css_path, "a", encoding="utf-8") as f:
        f.write(extra_css)
    print(f"  ✅ {css_path}")
else:
    marker = "/* ===== АНИМАЦИЯ КИРКИ ===== */"
    new_css = existing_css.split(marker)[0] + extra_css
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(new_css)
    print(f"  ✅ {css_path} (обновлено)")

print("\n🎉 ГОТОВО!")
print("\n✨ Что добавлено:")
print("   ⛏ Кирка шевелится как будто копает при наведении")
print("   💫 Свечение вокруг логотипа")
print("   📝 Текст слегка покачивается")
print("   👆 Эффект удара при клике")
print("\n📤 git add . && git commit -m 'v14: pickaxe animation' && git push --force origin main")
print("На PA: cd ~/mysite && git fetch origin main && git reset --hard origin/main && Reload")