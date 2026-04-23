# ============================================
# MYXA AI — FULL ULTRA GUI (ГОТОВАЯ ВЕРСИЯ)
# Автор: Мухаммад & ChatGPT
# ВСЁ РАБОТАЕТ: чаты, имя, темы, поиск, игры, счётчик, ГДЗ, МОДЕЛИ, МЫШЛЕНИЕ, МОНЕТКА, ВСЕ НЕЙРОСЕТИ
# ============================================
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import json
import os
import time
import threading
import random
import re
from datetime import datetime
import webbrowser
import urllib.parse
import urllib.request
import subprocess

# ============================================
# ----------- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ----------
# ============================================

APP_NAME = "MYXA AI"
DATA_FILE = "myxa_history.json"
SETTINGS_FILE = "myxa_settings.json"
PROFILE_FILE = "myxa_profile.json"

current_chat = "Главный чат"
chat_history = {}
internet_enabled = True
user_name = None
current_theme = "light"
message_count = 0

# === КОНТЕКСТ ===
last_user_action = None
last_bot_response = None
context_data = {}

# === ВЫБОР МОДЕЛИ ===
current_ai_model = "myxa"
deep_thinking = False

# === ТОКЕН GIGACHAT (ЗАМЕНИ НА СВОЙ) ===
GIGACHAT_TOKEN = "ТВОЙ_ТОКЕН_ОТ_СБЕРА"

# ============================================
# ----------------- ТЕМЫ ----------------------
# ============================================

THEMES = {
    "light": {
        "bg": "#ffffff", "fg": "#000000", "input_bg": "#f2f2f2", "input_fg": "#000000",
        "btn_bg": "#e0e0e0", "btn_fg": "#000"
    },
    "dark": {
        "bg": "#1f1f1f", "fg": "#ffffff", "input_bg": "#2a2a2a", "input_fg": "#ffffff",
        "btn_bg": "#3a3a3a", "btn_fg": "#fff"
    },
    "blue": {
        "bg": "#e6f0ff", "fg": "#003366", "input_bg": "#d4e2ff", "input_fg": "#001a33",
        "btn_bg": "#b5ccff", "btn_fg": "#001a33"
    },
    "green": {
        "bg": "#e8ffe8", "fg": "#003300", "input_bg": "#d8ffd8", "input_fg": "#002200",
        "btn_bg": "#b4ffb4", "btn_fg": "#002200"
    },
    "red": {
        "bg": "#ffe6e6", "fg": "#660000", "input_bg": "#ffd4d4", "input_fg": "#330000",
        "btn_bg": "#ffb3b3", "btn_fg": "#330000"
    }
}

# ============================================
# ----------- ЗАГРУЗКА / СОХРАНЕНИЕ ----------
# ============================================

def load_history():
    global chat_history
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                chat_history.update(json.load(f))
        except:
            chat_history.clear()
    if current_chat not in chat_history:
        chat_history[current_chat] = []

def save_history():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

def load_profile():
    global user_name
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                user_name = data.get("name")
        except:
            user_name = None

def save_profile(name):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump({"name": name}, f, ensure_ascii=False, indent=2)

def load_settings():
    global current_theme
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                current_theme = settings.get("theme", "light")
        except:
            pass

def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({"theme": current_theme}, f, ensure_ascii=False, indent=2)

load_profile()
load_settings()

# ============================================
# ----------- СОЗДАНИЕ ОСНОВНОГО ОКНА --------
# ============================================

root = tk.Tk()
root.title(APP_NAME)
root.geometry("1285x800")
root.resizable(False, False)

chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12), height=28)
chat_box.pack(fill="both", padx=5, pady=5)
chat_box.config(state=tk.DISABLED)

entry_box = tk.Entry(root, font=("Arial", 14))
entry_box.pack(fill="x", padx=5, pady=3)

button_frame = tk.Frame(root)
button_frame.pack(fill="x", padx=5)

bottom_buttons = []

def make_button(text, command):
    btn = tk.Button(button_frame, text=text, width=10, command=command)
    btn.pack(side="left", padx=2, pady=3)
    bottom_buttons.append(btn)
    return btn

# ============================================
# ----------- ПРИМЕНЕНИЕ ТЕМЫ ----------------
# ============================================

def apply_theme():
    theme = THEMES[current_theme]
    root.configure(bg=theme["bg"])
    try:
        chat_box.configure(bg=theme["bg"], fg=theme["fg"])
        entry_box.configure(bg=theme["input_bg"], fg=theme["input_fg"])
        for btn in bottom_buttons:
            btn.configure(bg=theme["btn_bg"], fg=theme["btn_fg"])
    except:
        pass

# ============================================
# ----------- СИСТЕМА СООБЩЕНИЙ --------------
# ============================================

def add_message(sender, text):
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, f"{sender}: {text}\n\n")
    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)

    if current_chat not in chat_history:
        chat_history[current_chat] = []
    chat_history[current_chat].append({"sender": sender, "text": text})
    save_history()

# ============================================
# ----------- ЛОГИКА ИИ (МОЗГ) --------------
# ============================================

message_history = []
max_history = 30

def fix_text(text):
    while "  " in text:
        text = text.replace("  ", " ")
    return text.strip()

def detect_emotion(text):
    sad = ["груст", "плохо", "печаль", "тяжело", "устал", "не хочу", "один", "страх"]
    happy = ["круто", "класс", "спасибо", "норм", "отлично", "хорошо", "ура"]
    low = text.lower()
    if any(w in low for w in sad): return "sad"
    if any(w in low for w in happy): return "happy"
    return "neutral"

def emotion_reply(em):
    if em == "sad": return "Бро… я с тобой. Ты сильный. Всё наладится 💪🔥"
    if em == "happy": return "Красавчик! Рад слышать такие эмоции! 😎"
    return None

def build_reply(main, extra=None):
    return main + "\n\n" + extra if extra else main

def remember(text):
    message_history.append(text)
    if len(message_history) > max_history:
        message_history.pop(0)

def save_name(name):
    global user_name
    user_name = name.capitalize()
    save_profile(user_name)
    return f"Отлично! Теперь я знаю, что тебя зовут {user_name} 🔥"

# ============================================
# ----------- ИГРЫ ---------------------------
# ============================================

secret_number = None

def game_rps(choice):
    options = ["камень", "ножницы", "бумага"]
    bot = random.choice(options)
    choice = choice.lower()
    if choice not in options:
        return "Выбери: камень / ножницы / бумага"
    if choice == bot:
        result = "Ничья!"
    elif (choice == "камень" and bot == "ножницы") or \
         (choice == "ножницы" and bot == "бумага") or \
         (choice == "бумага" and bot == "камень"):
        result = "Ты выиграл! 🔥"
    else:
        result = "Ты проиграл 😅"
    return f"Ты: {choice}\nБот: {bot}\n\n{result}"

def play_coin_gui():
    coin_win = tk.Toplevel(root)
    coin_win.title("🪙 Монетка")
    coin_win.geometry("300x250")
    coin_win.resizable(False, False)
    result_label = tk.Label(coin_win, text="Выбери сторону:", font=("Arial", 14))
    result_label.pack(pady=15)
    def play(choice):
        result = random.choice(["Орёл", "Решка"])
        outcome = "🎉 Ты выиграл!" if choice == result else "😅 Ты проиграл!"
        result_label.config(text=f"Ты выбрал: {choice}\nВыпало: {result}\n{outcome}")
        add_message("MYXA AI", f"🪙 Монетка: Ты — {choice}, Выпало — {result}. {outcome}")
    btn_frame = tk.Frame(coin_win)
    btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="🦅 Орёл", width=10, command=lambda: play("Орёл")).pack(side="left", padx=5)
    tk.Button(btn_frame, text="🪙 Решка", width=10, command=lambda: play("Решка")).pack(side="left", padx=5)
    tk.Button(coin_win, text="Закрыть", command=coin_win.destroy, width=15).pack(pady=10)

def game_coin():
    return f"🪙 Монетка подброшена!\nВыпало: {random.choice(['Орёл', 'Решка'])}"

def game_guess_start():
    global secret_number
    secret_number = random.randint(1, 10)
    return "🎯 Я загадал число от 1 до 10! Попробуй угадать!"

def game_guess_check(n):
    global secret_number
    if secret_number is None: return "Сначала напиши: игра угадай"
    if n == secret_number:
        secret_number = None
        return "🔥 Ты угадал! Красавчик!"
    return "Больше!" if n < secret_number else "Меньше!"

# ============================================
# ----------- ПОИСК И ИНТЕРНЕТ ---------------
# ============================================

def toggle_inet():
    global internet_enabled
    internet_enabled = not internet_enabled
    add_message("MYXA AI", f"Интернет {'включен 🌐' if internet_enabled else 'выключен 📴'}")

def search_duckduckgo(query):
    if not query or not query.strip(): return "❌ Введи запрос для поиска!"
    url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
    webbrowser.open(url)
    return f"🔍 Ищу в DuckDuckGo: {query}\nОткрываю браузер..."

def search_handler(user_text):
    if not internet_enabled:
        text = user_text.lower()
        if any(text.startswith(t) for t in ["/search ", "/искать ", "найди ", "поищи ", "загугли ", "найти ", "поиск "]):
            return "📴 Интернет выключен!"
        return None
    text = user_text.lower()
    if text.startswith("/search ") or text.startswith("/искать "):
        return search_duckduckgo(user_text.replace("/search ", "").replace("/искать ", "").strip())
    for trigger in ["найди ", "поищи ", "загугли ", "найти ", "поиск "]:
        if text.startswith(trigger): return search_duckduckgo(user_text[len(trigger):].strip())
    return None

# ============================================
# ----------- ОБРАБОТКА КОМАНД ---------------
# ============================================

def handle_commands(text):
    t = text.lower()
    if t.startswith("/name "): return save_name(text[6:].strip())
    if t == "/clear": message_history.clear(); return "История очищена 🧹"
    if t == "/about": return "MYXA AI — оффлайн интеллектуальная система. Версия ULTRA+."
    if t == "/myname": return f"Тебя зовут {user_name}!" if user_name else "Ты ещё не сказал своё имя."
    if t == "/help": return "📘 /name, /myname, /clear, /about, /search, игры"
    if t == "/forget": message_history.clear(); return "🧠 Контекст очищен."
    if t == "/context":
        ctx = f"📝 Последнее действие: {last_user_action or 'нет'}\n💬 Мой последний ответ: {last_bot_response or 'нет'}"
        return ctx
    return None

# ============================================
# ----------- ВСЕ НЕЙРОСЕТИ -------------------
# ============================================

def ask_ollama(prompt, model):
    try:
        command = f'cmd /c "ollama run {model} {prompt}"'
        result = subprocess.run(command, capture_output=True, text=True, timeout=120, shell=True, encoding='utf-8', errors='ignore')
        return result.stdout.strip() or "🤖 Модель промолчала..."
    except: return f"❌ Ошибка Ollama"

def ask_huggingface(prompt, model_url):
    try:
        data = json.dumps({"inputs": prompt, "parameters": {"max_length": 200}}).encode('utf-8')
        req = urllib.request.Request(model_url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode('utf-8'))[0]['generated_text']
    except: return f"❌ Ошибка API"

def ask_gigachat(prompt):
    if GIGACHAT_TOKEN == "ТВОЙ_ТОКЕН_ОТ_СБЕРА": return "❌ Токен не указан"
    try:
        import requests
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GIGACHAT_TOKEN}", "Content-Type": "application/json"}
        r = requests.post(url, headers=headers, json={"model": "GigaChat", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}, timeout=30, verify=False)
        return r.json()['choices'][0]['message']['content'] if r.status_code == 200 else f"❌ Ошибка {r.status_code}"
    except: return f"❌ Ошибка GigaChat"

# ============================================
# ----------- ГЛАВНЫЙ МОЗГ -------------------
# ============================================

def process_ai(text):
    global user_name, message_count, secret_number, current_ai_model, deep_thinking

    if current_ai_model != "myxa":
        if current_ai_model in ["phi3", "llama3.2", "mistral", "deepseek-r1:7b"]:
            prompt = f"Think step by step: {text}" if deep_thinking and current_ai_model == "deepseek-r1:7b" else text
            return ask_ollama(prompt, current_ai_model)
        if current_ai_model == "dialogpt": return ask_huggingface(text, "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium")
        if current_ai_model == "flan-t5": return ask_huggingface(text, "https://api-inference.huggingface.co/models/google/flan-t5-small")
        if current_ai_model == "saiga": return ask_huggingface(text, "https://api-inference.huggingface.co/models/IlyaGusev/saiga_llama3_8b")
        if current_ai_model == "gigachat": return ask_gigachat(text)

    message_count += 1
    clean = fix_text(text)
    remember(clean)
    global last_user_action, context_data

    if any(w in clean for w in ["камень", "ножницы", "бумага"]): last_user_action = "играли в КНБ"
    elif "таблица" in clean:
        last_user_action = "считали таблицу умножения"
        nums = re.findall(r"\d+", clean)
        if nums: context_data["last_table"] = int(nums[0])
    elif any(w in clean for w in ["погода", "дождь", "солнце"]): last_user_action = "говорили о погоде"
    elif any(w in clean for w in ["как дела", "настроение"]): last_user_action = "обсуждали настроение"
    elif "игра угадай" in clean: last_user_action = "угадывали число"
    elif "анекдот" in clean: last_user_action = "рассказывали анекдот"

    search_result = search_handler(clean)
    if search_result: return search_result
    cmd = handle_commands(clean)
    if cmd: return cmd

    if any(w in clean for w in ["меня зовут", "зови меня", "моё имя", "мое имя"]):
        name = clean.replace("меня зовут", "").replace("зови меня", "").replace("моё имя", "").replace("мое имя", "").strip()
        if len(name) > 0: return save_name(name)

    emotion = detect_emotion(clean)
    emo_reply = emotion_reply(emotion)

    # === ПРИВЕТСТВИЯ ===
    if clean == "привет":
        answers = ["Привет!", "Здравствуй!", "Рад тебя видеть!", "Привет! Чем могу помочь?", "Здравствуй! Чем могу помочь?", "Рад тебя видеть! Чем могу помочь?"]
        return build_reply(random.choice(answers), emo_reply)
    elif "ку" in clean: return build_reply("Ку! С чем помочь?", emo_reply)
    elif clean == "хай": return build_reply("Хай! С чем помочь?", emo_reply)
    elif clean == "здравствуй": return build_reply("Здравствуй! С чем помочь?", emo_reply)
    elif clean == "здарова": return build_reply("Здарова! С чем помочь?", emo_reply)

    # === КОНТЕКСТ ===
    if any(w in clean for w in ["что я говорил", "что я сказал", "помнишь", "напомни"]):
        if message_history:
            for msg in reversed(message_history):
                if not msg.startswith("MYXA AI:"): return build_reply(f"Ты говорил: «{msg}»", emo_reply)
        return build_reply("Я пока ничего не помню.", emo_reply)
    if clean in ["повтори", "ещё", "еще"]:
        return build_reply(last_bot_response, emo_reply) if last_bot_response else build_reply("А что повторить?", emo_reply)
    if clean == "что мы делали":
        return build_reply(f"Мы с тобой {last_user_action}. Продолжим?", emo_reply) if last_user_action else build_reply("Ничего особенного.", emo_reply)

    # === ВРЕМЯ ===
    if any(w in clean for w in ["сколько времени", "который час", "время"]):
        return f"Сейчас времени: {datetime.now().strftime('%H:%M')}"
    # === ПОМОЩЬ ===
    if "какие ты знаешь команду" in clean or clean in ["помощь", "помогите"]:
        return build_reply("Привет, Как дела, Сколько времени, Кто ты, ты бот, Сколько сообщений, пока, все норм, настроение, что ты можешь", emo_reply)
    # === СЧЁТЧИК ===
    if "сколько сообщений" in clean: return f"Мы написали {message_count} сообщений"
    # === КАК ДЕЛА / НАСТРОЕНИЕ ===
    if "как дела" in clean or "как ты" in clean or "как жизнь" in clean:
        return build_reply("У меня все хорошо! А как у тебя дела?", emo_reply)
    if any(w in clean for w in ["все норм", "все нормально", "у меня все хорошо"]):
        return build_reply("Рад что у тебя тоже все хорошо! А как у тебя настроение?", emo_reply)
    if any(w in clean for w in ["хорошее настроение", "настроение хорошее", "настроение норм"]):
        return build_reply("Хорошо что ты сегодня на позитиве! Что будем делать?", emo_reply)
    # === КТО ТЫ ===
    if any(w in clean for w in ["кто ты", "что ты", "ты бот"]):
        return build_reply("Я твой ИИ MYXA AI. Могу болтать и с чем-нибудь помочь", emo_reply)
    if "что ты можешь" in clean:
        return build_reply("Я могу определить время, сколько сообщений, таблицу умножения, и могу поболтать", emo_reply)
    # === ТАБЛИЦА ===
    if "таблица" in clean:
        nums = re.findall(r"\d+", clean)
        if nums:
            n = int(nums[0])
            return "\n".join([f"Таблица умножения на {n}:"] + [f"{n} × {i} = {n*i}" for i in range(1, 11)])
        return "Напиши число, например: Таблица 5"
    # === ПРОЩАНИЕ ===
    if clean in ["пока", "бай", "до свидания", "увидимся"]:
        return random.choice(["До свидания!", "Бай! Заходи ещё!", "Увидимся!", "Пока!"])
    # === ПРОЧЕЕ ===
    if "не работает" in clean: return build_reply("Пиши точные команды. Напиши 'помощь'!", emo_reply)
    if any(w in clean for w in ["а теперь понял", "а теперь поняла"]): return build_reply("Рад что ты все понял! С чего начнем?", emo_reply)
    if clean == "что нового": return build_reply("Больше функционала, дальше лучше :)", emo_reply)

    # === ИГРЫ ===
    if clean in ["камень", "ножницы", "бумага"]: return game_rps(clean)
    if "игра монетка" in clean or "подбрось монетку" in clean:
        play_coin_gui(); return "🪙 Открываю монетку..."
    if "игра угадай" in clean or "угадай число" in clean: return game_guess_start()
    if secret_number is not None:
        nums = re.findall(r"\d+", clean)
        if nums: return game_guess_check(int(nums[0]))

    if "сброс счётчика" in clean: message_count = 0; return "🧹 Счётчик обнулён!"
    if not user_name: return build_reply("Бро, а как тебя зовут? 😊", emo_reply)

    if clean == "спасибо": return f"Всегда пожалуйста, {user_name}! 😊"
    if "анекдот" in clean:
        return random.choice(["Колобок повесился.", "Идёт медведь по лесу, видит — машина горит. Сел в неё и сгорел."])

    if any(char.isdigit() for char in clean): return "Напиши число с командой, например: Таблица 5"
    return build_reply(f"{user_name}, я тебя услышал. Напиши понятнее или спроси 'помощь' 😊", emo_reply)

# ============================================
# ----------- ОТПРАВКА СООБЩЕНИЙ -------------
# ============================================

def send_message():
    user_text = entry_box.get().strip()
    if not user_text: return
    entry_box.delete(0, tk.END)
    add_message("Ты", user_text)
    threading.Thread(target=ai_answer_thread, args=(user_text,)).start()

def ai_answer_thread(text):
    time.sleep(0.2)
    response = process_ai(text)
    global last_bot_response
    last_bot_response = response
    add_message(APP_NAME, response)

# ============================================
# ----------- ФУНКЦИИ КНОПОК -----------------
# ============================================

def next_theme():
    global current_theme
    themes_list = list(THEMES.keys())
    idx = themes_list.index(current_theme)
    current_theme = themes_list[(idx + 1) % len(themes_list)]
    save_settings()
    apply_theme()
    add_message("MYXA AI", f"🎨 Тема: {current_theme}")

def clear_current_chat():
    global chat_history
    if current_chat in chat_history: chat_history[current_chat] = []
    save_history()
    chat_box.config(state=tk.NORMAL); chat_box.delete("1.0", tk.END); chat_box.config(state=tk.DISABLED)
    entry_box.delete(0, tk.END)
    add_message("MYXA AI", "🧹 Чат очищен")

def load_current_chat():
    chat_box.config(state=tk.NORMAL); chat_box.delete("1.0", tk.END)
    if current_chat in chat_history:
        for msg in chat_history[current_chat]: chat_box.insert(tk.END, f"{msg['sender']}: {msg['text']}\n\n")
    chat_box.config(state=tk.DISABLED); chat_box.see(tk.END)

def open_help():
    help_window = tk.Toplevel(root); help_window.title("Помощь"); help_window.geometry("400x500")
    tk.Label(help_window, text="📘 MYXA AI — СПРАВКА\n\n💬 КОМАНДЫ:\n/name, /myname, /clear, /help\n🔍 ПОИСК\n🎮 ИГРЫ\n📊 СЧЁТЧИК\n📚 ШКОЛА\n🧠 НЕЙРО", font=("Arial", 11), justify="left", padx=15, pady=15).pack(expand=True, fill="both")

def search_dialog():
    query = simpledialog.askstring("🔍 Поиск", "Введите запрос:")
    if query and query.strip():
        webbrowser.open(f"https://duckduckgo.com/?q={urllib.parse.quote(query)}")
        add_message("MYXA AI", f"🔍 Ищу: {query}")

def show_games_help():
    games_win = tk.Toplevel(root); games_win.title("🎮 Игры"); games_win.geometry("350x300")
    tk.Label(games_win, text="🎮 ИГРЫ:\n1️⃣ Монетка\n2️⃣ Угадай число\n3️⃣ КНБ", font=("Arial", 12), justify="left", padx=20, pady=20).pack()

def play_rps_gui():
    rps_win = tk.Toplevel(root); rps_win.title("✂️ КНБ"); rps_win.geometry("350x250")
    result_label = tk.Label(rps_win, text="Выбери вариант:", font=("Arial", 14)); result_label.pack(pady=15)
    def play(c):
        bot = random.choice(["камень", "ножницы", "бумага"])
        if c == bot: res = "Ничья!"
        elif (c == "камень" and bot == "ножницы") or (c == "ножницы" and bot == "бумага") or (c == "бумага" and bot == "камень"): res = "Ты выиграл! 🔥"
        else: res = "Ты проиграл 😅"
        result_label.config(text=f"Ты: {c} | Бот: {bot}\n{res}")
        add_message("MYXA AI", f"🎮 КНБ: Ты — {c}, Бот — {bot}. {res}")
    btn_frame = tk.Frame(rps_win); btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="🪨 Камень", width=10, command=lambda: play("камень")).pack(side="left", padx=5)
    tk.Button(btn_frame, text="✂️ Ножницы", width=10, command=lambda: play("ножницы")).pack(side="left", padx=5)
    tk.Button(btn_frame, text="📄 Бумага", width=10, command=lambda: play("бумага")).pack(side="left", padx=5)

def open_chats_window():
    CHATS_FILE = "myxa_chats.json"
    chats = json.load(open(CHATS_FILE, encoding="utf-8")) if os.path.exists(CHATS_FILE) else {"Главный чат": []}
    def save_chats(): json.dump(chats, open(CHATS_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    win = tk.Toplevel(root); win.title("📁 Чаты"); win.geometry("300x400")
    listbox = tk.Listbox(win, font=("Arial", 12)); listbox.pack(fill="both", expand=True, padx=10, pady=10)
    for chat in chats: listbox.insert(tk.END, chat)
    def new_chat():
        name = simpledialog.askstring("Новый чат", "Название:")
        if name and name.strip():
            name = name.strip()
            if name in chats: messagebox.showwarning("Ошибка", "Такой чат уже есть!")
            else: chats[name] = []; save_chats(); listbox.insert(tk.END, name); add_message("MYXA AI", f"✅ Чат '{name}' создан")
    def open_chat():
        sel = listbox.curselection()
        if sel:
            global current_chat, chat_history
            current_chat = listbox.get(sel[0]); chat_history = chats; load_current_chat()
            add_message("MYXA AI", f"📂 Переключено: {current_chat}"); win.destroy()
    def delete_chat():
        sel = listbox.curselection()
        if sel and len(chats) > 1:
            name = listbox.get(sel[0])
            if messagebox.askyesno("Удалить", f"Удалить чат '{name}'?"):
                del chats[name]; save_chats(); listbox.delete(sel[0])
                global current_chat
                if current_chat == name: current_chat = list(chats.keys())[0]; chat_history = chats; load_current_chat()
    btn_frame = tk.Frame(win); btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="➕ Новый", command=new_chat, width=10).pack(side="left", padx=3)
    tk.Button(btn_frame, text="📂 Открыть", command=open_chat, width=10).pack(side="left", padx=3)
    tk.Button(btn_frame, text="🗑 Удалить", command=delete_chat, width=10).pack(side="left", padx=3)

def open_gdz():
    webbrowser.open("https://gdz-raketa.ru")
    add_message("MYXA AI", "📚 Открываю Гдз-Ракета!")

def show_stats():
    stats_win = tk.Toplevel(root); stats_win.title("📊 Статистика"); stats_win.geometry("300x200")
    tk.Label(stats_win, text=f"📊 СТАТИСТИКА\n\nВсего сообщений: {message_count}\nПользователь: {user_name or 'не указан'}\nЧат: {current_chat}\nТема: {current_theme}", font=("Arial", 12), justify="left", padx=20, pady=20).pack()

def show_time_window():
    time_win = tk.Toplevel(root); time_win.title("⏰ Время и дата"); time_win.geometry("350x200")
    date_label = tk.Label(time_win, font=("Arial", 14)); date_label.pack(pady=10)
    time_label = tk.Label(time_win, font=("Arial", 18, "bold"), fg="blue"); time_label.pack(pady=10)
    def update():
        now = datetime.now()
        time_label.config(text=now.strftime("%H:%M:%S"))
        date_label.config(text=now.strftime("%d.%m.%Y (%A)"))
        time_win.after(1000, update)
    update()

def choose_neural_model():
    win = tk.Toplevel(root); win.title("🧠 Выбор нейросети"); win.geometry("350x450")
    tk.Label(win, text="ВЫБЕРИ НЕЙРОСЕТЬ", font=("Arial", 14, "bold")).pack(pady=15)
    def set_model(model):
        global current_ai_model, deep_thinking
        current_ai_model = model; deep_thinking = False
        names = {"myxa": "🧠 MYXA", "phi3": "🤖 Phi-3", "llama3.2": "🦙 Llama3.2", "mistral": "🌪️ Mistral", "deepseek-r1:7b": "🧠 DeepSeek-R1", "dialogpt": "💬 DialoGPT", "flan-t5": "📚 Flan-T5", "saiga": "🇷🇺 Saiga", "gigachat": "🤖 GigaChat"}
        add_message("MYXA AI", f"✅ Нейросеть: {names.get(model, model)}"); win.destroy()
    models = [("🧠 MYXA", "myxa"), ("🤖 Phi-3", "phi3"), ("🦙 Llama3.2", "llama3.2"), ("🌪️ Mistral", "mistral"), ("🧠 DeepSeek-R1", "deepseek-r1:7b"), ("💬 DialoGPT", "dialogpt"), ("📚 Flan-T5", "flan-t5"), ("🇷🇺 Saiga", "saiga"), ("🤖 GigaChat", "gigachat")]
    for text, model in models: tk.Button(win, text=text, width=30, command=lambda m=model: set_model(m)).pack(pady=3)

def toggle_deep_thinking():
    global deep_thinking, current_ai_model
    deep_thinking = not deep_thinking
    add_message("MYXA AI", f"🧠 Глубокое мышление: {'🟢 ВКЛ' if deep_thinking else '⚪ ВЫКЛ'}")
    if deep_thinking: current_ai_model = "deepseek-r1:7b"; add_message("MYXA AI", "🤖 Модель изменена на DeepSeek-R1")

def open_calculator():
    calc_win = tk.Toplevel(root); calc_win.title("🧮 Калькулятор"); calc_win.geometry("280x380"); calc_win.configure(bg="#2c2c2c")
    entry = tk.Entry(calc_win, font=("Arial", 20), justify="right", bg="#1e1e1e", fg="white"); entry.pack(fill="x", padx=10, pady=10)
    def click(c): entry.insert(tk.END, c)
    def clear(): entry.delete(0, tk.END)
    def backspace(): entry.delete(len(entry.get())-1)
    def calc():
        try:
            expr = entry.get().replace("×", "*").replace("÷", "/")
            result = eval(expr); entry.delete(0, tk.END); entry.insert(0, str(result))
        except: entry.delete(0, tk.END); entry.insert(0, "Ошибка")
    buttons = [('C', '⌫', '%', '÷'), ('7', '8', '9', '×'), ('4', '5', '6', '-'), ('1', '2', '3', '+'), ('+/-', '0', '.', '=')]
    for row in buttons:
        frame = tk.Frame(calc_win, bg="#2c2c2c"); frame.pack(fill="x", padx=5, pady=2)
        for char in row:
            bg = "#ff5252" if char == 'C' else "#ffa500" if char == '⌫' else "#4CAF50" if char == '=' else "#555" if char in '+-×÷%' else "#333"
            cmd = clear if char == 'C' else backspace if char == '⌫' else calc if char == '=' else (lambda c=char: click(c))
            tk.Button(frame, text=char, width=5, height=2, command=cmd, bg=bg, fg="white").pack(side="left", expand=True, fill="both", padx=1)

# ============================================
# ----------- КНОПКИ -------------------------
# ============================================

send_btn = tk.Button(button_frame, text="➤ Отправить", width=12, command=send_message)
send_btn.pack(side="right", padx=2, pady=3)
bottom_buttons.append(send_btn)

make_button("Help", open_help)
make_button("Поиск", search_dialog)
make_button("Темы", next_theme)
make_button("ГДЗ", open_gdz)
make_button("Стат", show_stats)
make_button("Время", show_time_window)
make_button("Очистить", clear_current_chat)
make_button("Чаты", open_chats_window)
make_button("Игры", show_games_help)
make_button("КНБ", play_rps_gui)
make_button("Монетка", play_coin_gui)
make_button("🧠 Нейро", choose_neural_model)
make_button("🧠 Мышление", toggle_deep_thinking)
make_button("🧮 Calc", open_calculator)

# ============================================
# ----------- ПРИВЯЗКИ И ЗАПУСК ---------------
# ============================================

entry_box.bind("<Return>", lambda event: send_message())
load_history()
apply_theme()
load_current_chat()
root.mainloop()