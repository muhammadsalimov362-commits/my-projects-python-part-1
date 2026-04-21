# ============================================
# GAME HUB — ИГРОВОЙ ЛАУНЧЕР
# Автор: Мухаммад
# Сохранение пользователя, 16 достижений, 5 игр
# ============================================
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import random
import time

# ============================================
# ----------- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ----------
# ============================================

APP_NAME = "🎮 GAME HUB"
STATS_FILE = "game_hub_stats.json"
USER_FILE = "game_hub_user.json"

user_name = None

# Статистика
stats = {
    "total_games": 0,
    "wins": 0,
    "losses": 0,
    "draws": 0,
    "coin_wins": 0,
    "rps_wins": 0,
    "guess_best": 999,
    "reaction_best": 999,
    "dice_wins": 0,
}

# Достижения (16 штук)
ACHIEVEMENTS = {
    "first_win": {"name": "🏆 Первая победа", "desc": "Выиграй любую игру", "unlocked": False},
    "coin_1": {"name": "🪙 Новичок", "desc": "Выиграй в монетку 1 раз", "unlocked": False},
    "coin_3": {"name": "🍀 Счастливчик", "desc": "Выиграй в монетку 3 раза", "unlocked": False},
    "coin_10": {"name": "💎 Легенда удачи", "desc": "Выиграй в монетку 10 раз", "unlocked": False},
    "rps_1": {"name": "✂️ Новичок", "desc": "Выиграй в КНБ 1 раз", "unlocked": False},
    "rps_5": {"name": "🧠 Стратег", "desc": "Выиграй в КНБ 5 раз", "unlocked": False},
    "rps_15": {"name": "👑 Мастер КНБ", "desc": "Выиграй в КНБ 15 раз", "unlocked": False},
    "guess_first": {"name": "🎯 Угадайка", "desc": "Угадай число с первой попытки", "unlocked": False},
    "guess_3": {"name": "🎯 Интуиция", "desc": "Угадай число за 1-2 попытки 3 раза", "unlocked": False, "counter": 0},
    "reaction_10": {"name": "⚡ Быстрый", "desc": "Набери 10 очков в реакции", "unlocked": False},
    "reaction_25": {"name": "⚡ Молния", "desc": "Набери 25 очков в реакции", "unlocked": False},
    "dice_1": {"name": "🎲 Игрок", "desc": "Выиграй в кости 1 раз", "unlocked": False},
    "dice_3": {"name": "🎲 Везунчик", "desc": "Выиграй в кости 3 раза", "unlocked": False},
    "dice_streak": {"name": "🔥 В ударе", "desc": "Выиграй в кости 3 раза подряд", "unlocked": False},
    "all_games": {"name": "🌟 Коллекционер", "desc": "Сыграй во все 5 игр", "unlocked": False, "played": []},
    "master": {"name": "🏅 Легенда", "desc": "Открой 10 достижений", "unlocked": False},
}

games_played = set()
dice_streak = 0

# ============================================
# ----------- ЗАГРУЗКА / СОХРАНЕНИЕ ----------
# ============================================

def load_user():
    global user_name
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                user_name = data.get("name")
        except:
            user_name = None

def save_user():
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump({"name": user_name}, f, ensure_ascii=False, indent=2)

def load_stats():
    global stats, ACHIEVEMENTS, games_played, dice_streak
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                stats.update(data.get("stats", {}))
                for key, value in data.get("achievements", {}).items():
                    if key in ACHIEVEMENTS:
                        ACHIEVEMENTS[key].update(value)
                games_played = set(data.get("games_played", []))
                dice_streak = data.get("dice_streak", 0)
        except:
            pass

def save_stats():
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "stats": stats,
            "achievements": ACHIEVEMENTS,
            "games_played": list(games_played),
            "dice_streak": dice_streak
        }, f, ensure_ascii=False, indent=2)

def check_achievements():
    # Первая победа
    if stats["wins"] >= 1 and not ACHIEVEMENTS["first_win"]["unlocked"]:
        ACHIEVEMENTS["first_win"]["unlocked"] = True
        messagebox.showinfo("🏆 Достижение!", "Первая победа!")
    
    # Монетка
    cw = stats.get("coin_wins", 0)
    if cw >= 1 and not ACHIEVEMENTS["coin_1"]["unlocked"]:
        ACHIEVEMENTS["coin_1"]["unlocked"] = True
        messagebox.showinfo("🏆 Достижение!", "Новичок (Монетка)!")
    if cw >= 3 and not ACHIEVEMENTS["coin_3"]["unlocked"]:
        ACHIEVEMENTS["coin_3"]["unlocked"] = True
        messagebox.showinfo("🏆 Достижение!", "Счастливчик!")
    if cw >= 10 and not ACHIEVEMENTS["coin_10"]["unlocked"]:
        ACHIEVEMENTS["coin_10"]["unlocked"] = True
        messagebox.showinfo("🏆 Достижение!", "Легенда удачи!")
    
    # КНБ
    rw = stats.get("rps_wins", 0)
    if rw >= 1 and not ACHIEVEMENTS["rps_1"]["unlocked"]:
        ACHIEVEMENTS["rps_1"]["unlocked"] = True
        messagebox.showinfo("🏆 Достижение!", "Новичок (КНБ)!")
    if rw >= 5 and not ACHIEVEMENTS["rps_5"]["unlocked"]:
        ACHIEVEMENTS["rps_5"]["unlocked"] = True
        messagebox.showinfo("🏆 Достижение!", "Стратег!")
    if rw >= 15 and not ACHIEVEMENTS["rps_15"]["unlocked"]:
        ACHIEVEMENTS["rps_15"]["unlocked"] = True
        messagebox.showinfo("🏆 Достижение!", "Мастер КНБ!")
    
    # Кости
    dw = stats.get("dice_wins", 0)
    if dw >= 1 and not ACHIEVEMENTS["dice_1"]["unlocked"]:
        ACHIEVEMENTS["dice_1"]["unlocked"] = True
        messagebox.showinfo("🏆 Достижение!", "Игрок в кости!")
    if dw >= 3 and not ACHIEVEMENTS["dice_3"]["unlocked"]:
        ACHIEVEMENTS["dice_3"]["unlocked"] = True
        messagebox.showinfo("🏆 Достижение!", "Везунчик!")
    if dice_streak >= 3 and not ACHIEVEMENTS["dice_streak"]["unlocked"]:
        ACHIEVEMENTS["dice_streak"]["unlocked"] = True
        messagebox.showinfo("🏆 Достижение!", "В ударе!")
    
    # Все игры
    if "all_games" in ACHIEVEMENTS:
        ACHIEVEMENTS["all_games"]["played"] = list(games_played)
        if len(games_played) >= 5 and not ACHIEVEMENTS["all_games"]["unlocked"]:
            ACHIEVEMENTS["all_games"]["unlocked"] = True
            messagebox.showinfo("🏆 Достижение!", "Коллекционер! Все 5 игр!")
    
    # Легенда (10 достижений)
    unlocked_count = sum(1 for a in ACHIEVEMENTS.values() if a.get("unlocked", False))
    if unlocked_count >= 10 and not ACHIEVEMENTS["master"]["unlocked"]:
        ACHIEVEMENTS["master"]["unlocked"] = True
        messagebox.showinfo("🏆 Достижение!", "ЛЕГЕНДА! 10 достижений!")
    
    save_stats()

load_user()
load_stats()

# ============================================
# ----------- ОКНО СТАТИСТИКИ ----------------
# ============================================

def show_stats():
    win = tk.Toplevel(root)
    win.title("📊 Статистика")
    win.geometry("400x550")
    win.resizable(False, False)
    
    total = stats["total_games"]
    wins = stats["wins"]
    winrate = (wins / total * 100) if total > 0 else 0
    
    text = f"""
👤 Игрок: {user_name or 'Не указан'}

📊 ОБЩАЯ СТАТИСТИКА
─────────────────────────
🎮 Всего игр: {total}
🏆 Побед: {wins}
💀 Поражений: {stats['losses']}
🤝 Ничьих: {stats['draws']}
📈 Винрейт: {winrate:.1f}%

🎯 РЕКОРДЫ
─────────────────────────
🪙 Монетка: {stats.get('coin_wins', 0)} побед
✂️ КНБ: {stats.get('rps_wins', 0)} побед
🎯 Угадай: лучший счёт {stats.get('guess_best', 999)} попыток
⚡ Реакция: {stats.get('reaction_best', 0)} очков
🎲 Кости: {stats.get('dice_wins', 0)} побед

🏅 ДОСТИЖЕНИЯ ({sum(1 for a in ACHIEVEMENTS.values() if a.get('unlocked', False))}/16)
─────────────────────────
"""
    for ach in ACHIEVEMENTS.values():
        status = "✅" if ach.get("unlocked", False) else "🔒"
        text += f"{status} {ach['name']} — {ach['desc']}\n"
    
    label = tk.Label(win, text=text, font=("Arial", 10), justify="left", padx=20, pady=10)
    label.pack()
    
    tk.Button(win, text="❌ Закрыть", command=win.destroy, width=15).pack(pady=10)

# ============================================
# ----------- ИГРА 1: МОНЕТКА (ОКНО) ---------
# ============================================

def play_coin():
    games_played.add("coin")
    coin_win = tk.Toplevel(root)
    coin_win.title("🪙 Монетка")
    coin_win.geometry("300x250")
    coin_win.resizable(False, False)
    
    result_label = tk.Label(coin_win, text="Выбери сторону:", font=("Arial", 14))
    result_label.pack(pady=15)
    
    def flip(choice):
        global stats
        result = random.choice(["Орёл", "Решка"])
        stats["total_games"] += 1
        
        if choice == result:
            stats["wins"] += 1
            stats["coin_wins"] = stats.get("coin_wins", 0) + 1
            outcome = "🎉 Ты выиграл!"
        else:
            stats["losses"] += 1
            outcome = "😅 Ты проиграл!"
        
        result_label.config(text=f"Ты: {choice}\nВыпало: {result}\n{outcome}")
        check_achievements()
    
    btn_frame = tk.Frame(coin_win)
    btn_frame.pack(pady=20)
    
    tk.Button(btn_frame, text="🦅 Орёл", width=10, command=lambda: flip("Орёл")).pack(side="left", padx=5)
    tk.Button(btn_frame, text="🪙 Решка", width=10, command=lambda: flip("Решка")).pack(side="left", padx=5)
    tk.Button(coin_win, text="❌ Закрыть", command=coin_win.destroy).pack(pady=10)

# ============================================
# ----------- ИГРА 2: КНБ (ОКНО) -------------
# ============================================

def play_rps():
    games_played.add("rps")
    rps_win = tk.Toplevel(root)
    rps_win.title("✂️ Камень-Ножницы-Бумага")
    rps_win.geometry("350x250")
    rps_win.resizable(False, False)
    
    result_label = tk.Label(rps_win, text="Выбери вариант:", font=("Arial", 14))
    result_label.pack(pady=15)
    
    def play(choice):
        global stats
        options = ["Камень", "Ножницы", "Бумага"]
        bot = random.choice(options)
        stats["total_games"] += 1
        
        if choice == bot:
            stats["draws"] += 1
            outcome = "🤝 Ничья!"
        elif (choice == "Камень" and bot == "Ножницы") or \
             (choice == "Ножницы" and bot == "Бумага") or \
             (choice == "Бумага" and bot == "Камень"):
            stats["wins"] += 1
            stats["rps_wins"] = stats.get("rps_wins", 0) + 1
            outcome = "🎉 Ты выиграл!"
        else:
            stats["losses"] += 1
            outcome = "😅 Ты проиграл!"
        
        result_label.config(text=f"Ты: {choice}\nБот: {bot}\n{outcome}")
        check_achievements()
    
    btn_frame = tk.Frame(rps_win)
    btn_frame.pack(pady=20)
    
    tk.Button(btn_frame, text="🪨 Камень", width=10, command=lambda: play("Камень")).pack(side="left", padx=3)
    tk.Button(btn_frame, text="✂️ Ножницы", width=10, command=lambda: play("Ножницы")).pack(side="left", padx=3)
    tk.Button(btn_frame, text="📄 Бумага", width=10, command=lambda: play("Бумага")).pack(side="left", padx=3)
    tk.Button(rps_win, text="❌ Закрыть", command=rps_win.destroy).pack(pady=10)

# ============================================
# ----------- ИГРА 3: УГАДАЙ ЧИСЛО -----------
# ============================================

def play_guess():
    games_played.add("guess")
    secret = random.randint(1, 20)
    attempts = 0
    stats["total_games"] += 1
    won = False
    
    guess_win = tk.Toplevel(root)
    guess_win.title("🎯 Угадай число")
    guess_win.geometry("300x200")
    
    tk.Label(guess_win, text="Я загадал число от 1 до 20", font=("Arial", 12)).pack(pady=10)
    entry = tk.Entry(guess_win, font=("Arial", 14), width=10)
    entry.pack(pady=5)
    hint_label = tk.Label(guess_win, text="", font=("Arial", 11))
    hint_label.pack(pady=5)
    
    def check():
        nonlocal attempts, won
        try:
            guess = int(entry.get())
        except:
            hint_label.config(text="Введи число!")
            return
        
        attempts += 1
        if guess == secret:
            stats["wins"] += 1
            won = True
            if attempts == 1:
                ACHIEVEMENTS["guess_first"]["unlocked"] = True
                messagebox.showinfo("🏆 Достижение!", "Угадайка с первой попытки!")
            elif attempts <= 2:
                ach = ACHIEVEMENTS.get("guess_3")
                if ach:
                    ach["counter"] = ach.get("counter", 0) + 1
                    if ach["counter"] >= 3 and not ach["unlocked"]:
                        ach["unlocked"] = True
                        messagebox.showinfo("🏆 Достижение!", "Интуиция!")
            if attempts < stats.get("guess_best", 999):
                stats["guess_best"] = attempts
            hint_label.config(text=f"🎉 Правильно! Число: {secret}\nПопыток: {attempts}")
            entry.config(state="disabled")
            check_achievements()
        elif guess < secret:
            hint_label.config(text=f"📈 Больше! (попытка {attempts})")
        else:
            hint_label.config(text=f"📉 Меньше! (попытка {attempts})")
        entry.delete(0, tk.END)
    
    tk.Button(guess_win, text="Проверить", command=check).pack(pady=5)
    tk.Button(guess_win, text="❌ Закрыть", command=guess_win.destroy).pack(pady=5)

# ============================================
# ----------- ИГРА 4: РЕАКЦИЯ ----------------
# ============================================

def play_reaction():
    games_played.add("reaction")
    react_win = tk.Toplevel(root)
    react_win.title("⚡ Реакция")
    react_win.geometry("350x250")
    
    score = 0
    best = stats.get("reaction_best", 0)
    
    status_label = tk.Label(react_win, text=f"Рекорд: {best}\nОчки: 0", font=("Arial", 14))
    status_label.pack(pady=15)
    
    click_button = tk.Button(react_win, text="ЖМИ!", font=("Arial", 20, "bold"), bg="red", fg="white", width=10, height=2, state="disabled")
    click_button.pack(pady=10)
    
    start_button = tk.Button(react_win, text="СТАРТ", font=("Arial", 14), bg="green", fg="white", width=15)
    start_button.pack(pady=5)
    
    timer_label = tk.Label(react_win, text="", font=("Arial", 12))
    timer_label.pack()
    
    game_active = False
    start_time = 0
    
    def start_game():
        nonlocal game_active, score
        game_active = True
        score = 0
        status_label.config(text=f"Рекорд: {best}\nОчки: {score}")
        start_button.config(state="disabled")
        next_round()
    
    def next_round():
        nonlocal game_active, start_time
        if not game_active:
            return
        click_button.config(state="disabled", bg="red", text="ЖДИ...")
        delay = random.randint(1000, 3000)
        root.after(delay, activate_button)
    
    def activate_button():
        nonlocal start_time
        if not game_active:
            return
        start_time = time.time()
        click_button.config(state="normal", bg="lime", fg="black", text="ЖМИ СЕЙЧАС!")
        timer_label.config(text="⏰ ЖМИ!")
        root.after(800, timeout)
    
    def timeout():
        if game_active and click_button["state"] == "normal":
            click_button.config(state="disabled", bg="red", text="ЖДИ...")
            timer_label.config(text="💀 Слишком медленно!")
            root.after(1000, next_round)
    
    def click():
        nonlocal score
        if game_active and click_button["state"] == "normal":
            reaction = time.time() - start_time
            score += 1
            status_label.config(text=f"Рекорд: {best}\nОчки: {score}")
            timer_label.config(text=f"⚡ {reaction:.2f} сек!")
            click_button.config(state="disabled", bg="red", text="ЖДИ...")
            root.after(500, next_round)
    
    def end_game():
        nonlocal game_active
        game_active = False
        stats["total_games"] += 1
        if score > best:
            stats["reaction_best"] = score
        if score >= 10 and not ACHIEVEMENTS["reaction_10"]["unlocked"]:
            ACHIEVEMENTS["reaction_10"]["unlocked"] = True
            messagebox.showinfo("🏆 Достижение!", "Быстрый!")
        if score >= 25 and not ACHIEVEMENTS["reaction_25"]["unlocked"]:
            ACHIEVEMENTS["reaction_25"]["unlocked"] = True
            messagebox.showinfo("🏆 Достижение!", "Молния!")
        check_achievements()
        start_button.config(state="normal")
        click_button.config(state="disabled", text="ЖМИ!", bg="red")
        status_label.config(text=f"Рекорд: {stats['reaction_best']}\nИгра окончена! Очки: {score}")
    
    click_button.config(command=click)
    start_button.config(command=start_game)
    
    tk.Button(react_win, text="ЗАКОНЧИТЬ", command=end_game).pack(pady=5)
    tk.Button(react_win, text="❌ Закрыть", command=lambda: [end_game(), react_win.destroy()]).pack(pady=5)

# ============================================
# ----------- ИГРА 5: КОСТИ ------------------
# ============================================

def play_dice():
    global dice_streak
    games_played.add("dice")
    dice_win = tk.Toplevel(root)
    dice_win.title("🎲 Кости")
    dice_win.geometry("300x250")
    
    result_label = tk.Label(dice_win, text="Брось кости!", font=("Arial", 14))
    result_label.pack(pady=15)
    
    streak_label = tk.Label(dice_win, text=f"🔥 Серия: {dice_streak}", font=("Arial", 11))
    streak_label.pack()
    
    def roll():
        global dice_streak, stats
        player = random.randint(1, 6) + random.randint(1, 6)
        bot = random.randint(1, 6) + random.randint(1, 6)
        stats["total_games"] += 1
        
        if player > bot:
            stats["wins"] += 1
            stats["dice_wins"] = stats.get("dice_wins", 0) + 1
            dice_streak += 1
            outcome = f"🎉 Ты выиграл! ({player} > {bot})"
        elif player < bot:
            stats["losses"] += 1
            dice_streak = 0
            outcome = f"😅 Ты проиграл! ({player} < {bot})"
        else:
            stats["draws"] += 1
            outcome = f"🤝 Ничья! ({player} = {bot})"
        
        result_label.config(text=f"Ты: {player}\nБот: {bot}\n{outcome}")
        streak_label.config(text=f"🔥 Серия: {dice_streak}")
        check_achievements()
    
    tk.Button(dice_win, text="🎲 БРОСИТЬ", font=("Arial", 14), width=15, command=roll).pack(pady=10)
    tk.Button(dice_win, text="❌ Закрыть", command=dice_win.destroy).pack(pady=5)

# ============================================
# ----------- ГЛАВНОЕ МЕНЮ -------------------
# ============================================

root = tk.Tk()
root.title(APP_NAME)
root.geometry("400x500")
root.resizable(False, False)

if not user_name:
    name = simpledialog.askstring("👤 Привет!", "Как тебя зовут?")
    if name:
        user_name = name
        save_user()

tk.Label(root, text=f"🎮 GAME HUB", font=("Arial", 20, "bold")).pack(pady=10)
tk.Label(root, text=f"Игрок: {user_name or 'Гость'}", font=("Arial", 12)).pack()

frame = tk.Frame(root)
frame.pack(pady=20)

tk.Button(frame, text="🪙 Монетка", width=20, height=2, command=play_coin).pack(pady=5)
tk.Button(frame, text="✂️ Камень-Ножницы-Бумага", width=20, height=2, command=play_rps).pack(pady=5)
tk.Button(frame, text="🎯 Угадай число", width=20, height=2, command=play_guess).pack(pady=5)
tk.Button(frame, text="⚡ Реакция", width=20, height=2, command=play_reaction).pack(pady=5)
tk.Button(frame, text="🎲 Кости", width=20, height=2, command=play_dice).pack(pady=5)

tk.Button(root, text="📊 Статистика и достижения", width=25, command=show_stats).pack(pady=10)
tk.Button(root, text="👤 Сменить имя", command=lambda: change_name()).pack()

def change_name():
    global user_name
    name = simpledialog.askstring("👤 Имя", "Новое имя:")
    if name:
        user_name = name
        save_user()
        root.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

import sys
root.mainloop()