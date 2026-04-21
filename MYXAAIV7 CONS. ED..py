# ============================================
# MYXA AI — CONSOLE VERSION (ПОЛНАЯ)
# ============================================

import json
import os
import random
import re
import webbrowser
import urllib.parse
from datetime import datetime

# ============================================
# ----------- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ----------
# ============================================

PROFILE_FILE = "myxa_profile.json"
CHATS_FILE = "myxa_chats.json"

user_name = None
message_count = 0
current_chat = "Главный чат"
chats = {"Главный чат": []}
secret_number = None

# ============================================
# ----------- ЗАГРУЗКА / СОХРАНЕНИЕ ----------
# ============================================

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

def load_chats():
    global chats, current_chat
    if os.path.exists(CHATS_FILE):
        try:
            with open(CHATS_FILE, "r", encoding="utf-8") as f:
                chats = json.load(f)
                if "Главный чат" not in chats:
                    chats["Главный чат"] = []
        except:
            chats = {"Главный чат": []}

def save_chats():
    with open(CHATS_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)

# ============================================
# ----------- ЛОГИКА ИИ ----------------------
# ============================================

def fix_text(text):
    while "  " in text:
        text = text.replace("  ", " ")
    return text.strip()

def save_name(name):
    global user_name
    user_name = name.capitalize()
    save_profile(user_name)
    return f"Отлично! Теперь я знаю, что тебя зовут {user_name} 🔥"

# ============================================
# ----------- ИГРЫ ---------------------------
# ============================================

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
    return f"Ты: {choice}\nБот: {bot}\n{result}"

def game_coin():
    return f"🪙 Монетка подброшена!\nВыпало: {random.choice(['Орёл', 'Решка'])}"

def game_guess_start():
    global secret_number
    secret_number = random.randint(1, 10)
    return "🎯 Я загадал число от 1 до 10! Попробуй угадать!"

def game_guess_check(n):
    global secret_number
    if secret_number is None:
        return "Сначала напиши: игра угадай"
    if n == secret_number:
        secret_number = None
        return "🔥 Ты угадал! Красавчик!"
    return "Больше!" if n < secret_number else "Меньше!"

# ============================================
# ----------- ПОИСК --------------------------
# ============================================

def search_duckduckgo(query):
    if not query or not query.strip():
        return "❌ Введи запрос для поиска!"
    url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
    webbrowser.open(url)
    return f"🔍 Ищу в DuckDuckGo: {query}\nОткрываю браузер..."

# ============================================
# ----------- ОБРАБОТКА ВВОДА ----------------
# ============================================

def process_input(text):
    global user_name, message_count, secret_number, current_chat, chats

    message_count += 1
    clean = fix_text(text).lower()
    
    if not clean:
        return ""

    # Поиск
    if clean.startswith("/search ") or clean.startswith("/искать "):
        query = text.replace("/search ", "").replace("/искать ", "").strip()
        return search_duckduckgo(query)
    for trigger in ["найди ", "поищи ", "загугли ", "найти ", "поиск "]:
        if clean.startswith(trigger):
            return search_duckduckgo(text[len(trigger):].strip())

    # Команды
    if clean.startswith("/name "):
        return save_name(text[6:].strip())
    if clean == "/clear":
        chats[current_chat] = []
        save_chats()
        return "🧹 Чат очищен"
    if clean == "/myname":
        return f"Тебя зовут {user_name}!" if user_name else "Ты ещё не сказал своё имя."
    if clean == "/help":
        return "📘 /name, /myname, /clear, /search, /stats, /gdz, /new, /switch, /delete, /chats, игры"
    if clean == "/stats":
        return f"📊 Всего сообщений: {message_count}\n👤 Пользователь: {user_name or 'не указан'}\n📁 Чат: {current_chat}"
    if clean == "/gdz":
        webbrowser.open("https://gdz.ru")
        return "📚 Открываю gdz.ru в браузере..."
    
    # Чаты
    if clean.startswith("/new "):
        name = text[5:].strip()
        if name and name not in chats:
            chats[name] = []
            save_chats()
            return f"✅ Чат '{name}' создан"
        return "❌ Чат уже существует или пустое имя"
    if clean.startswith("/switch "):
        name = text[8:].strip()
        if name in chats:
            current_chat = name
            return f"📂 Переключено на: {name}"
        return f"❌ Чат '{name}' не найден"
    if clean.startswith("/delete "):
        name = text[8:].strip()
        if name in chats and len(chats) > 1:
            del chats[name]
            if current_chat == name:
                current_chat = list(chats.keys())[0]
            save_chats()
            return f"🗑 Чат '{name}' удалён"
        return "❌ Нельзя удалить единственный чат или чат не найден"
    if clean == "/chats":
        return "📁 Чаты:\n" + "\n".join(chats.keys())

    # Представление
    if any(w in clean for w in ["меня зовут", "зови меня", "моё имя", "мое имя"]):
        name = clean.replace("меня зовут", "").replace("зови меня", "").replace("моё имя", "").replace("мое имя", "").strip()
        if len(name) > 0:
            return save_name(name)

    # ========================================
    #         ПРИВЕТСТВИЯ
    # ========================================
    if clean == "привет":
        answers = ["Привет!", "Здравствуй!", "Рад тебя видеть!", "Привет! Чем могу помочь?", "Здравствуй! Чем могу помочь?", "Рад тебя видеть! Чем могу помочь?"]
        return random.choice(answers)
    elif "ку" in clean:
        return "Ку! С чем помочь?"
    elif clean == "хай":
        return "Хай! С чем помочь?"
    elif clean == "здравствуй":
        return "Здравствуй! С чем помочь?"
    elif clean == "здарова":
        return "Здарова! С чем помочь?"

    # ========================================
    #         ВРЕМЯ
    # ========================================
    elif any(w in clean for w in ["сколько времени", "который час", "время"]):
        now = datetime.now()
        return f"Сейчас времени: {now.strftime('%H:%M')}"

    # ========================================
    #         ПОМОЩЬ / КОМАНДЫ
    # ========================================
    elif "какие ты знаешь команду" in clean or clean in ["помощь", "помогите"]:
        return "Привет, Как дела, Сколько времени, Кто ты, ты бот, Сколько сообщений, пока, все норм, настроение, что ты можешь"

    # ========================================
    #         СЧЁТЧИК СООБЩЕНИЙ
    # ========================================
    elif "сколько сообщений" in clean:
        return f"Мы написали {message_count} сообщений"

    # ========================================
    #         КАК ДЕЛА / НАСТРОЕНИЕ
    # ========================================
    elif "как дела" in clean or "как ты" in clean or "как жизнь" in clean:
        return "У меня все хорошо! А как у тебя дела?"
    elif any(w in clean for w in ["все норм", "все нормально", "у меня все хорошо", "у меня тоже все хорошо"]):
        return "Рад что у тебя тоже все хорошо! А как у тебя настроение?"
    elif any(w in clean for w in ["хорошее настроение", "настроение хорошее", "настроение норм", "нормальное настроение"]):
        return "Хорошо что ты сегодня на позитиве! Что будем делать?"

    # ========================================
    #         КТО ТЫ / ЧТО ТЫ
    # ========================================
    elif any(w in clean for w in ["кто ты", "что ты", "ты бот"]):
        if "бот" in clean:
            return "Да! Я твой ИИ MYXA AI. Могу болтать и с чем-нибудь помочь"
        else:
            return "Я твой ИИ MYXA AI. Могу болтать и с чем-нибудь помочь"
    elif "что ты можешь" in clean:
        return "Я могу определить время, сколько сообщений, таблицу умножения, и могу поболтать"

    # ========================================
    #         ТАБЛИЦА УМНОЖЕНИЯ
    # ========================================
    elif "таблица" in clean:
        nums = re.findall(r"\d+", clean)
        if nums:
            n = int(nums[0])
            out = [f"Таблица умножения на {n}:"]
            for i in range(1, 11):
                out.append(f"{n} × {i} = {n*i}")
            return "\n".join(out)
        else:
            return "Напиши число, например: Таблица 5"

    # ========================================
    #         ПРОЩАНИЕ
    # ========================================
    elif clean in ["пока", "бай", "до свидания", "увидимся"]:
        answers = ["До свидания!", "Бай! Заходи ещё!", "Увидимся!", "Пока!"]
        return random.choice(answers)

    # ========================================
    #         ПРОЧЕЕ
    # ========================================
    elif "не работает" in clean:
        return "Пиши точные команды. Напиши 'помощь' чтобы увидеть список!"
    elif any(w in clean for w in ["а теперь понял", "а теперь поняла"]):
        return "Рад что ты все понял! С чего начнем?"
    elif clean == "что нового":
        return "Больше функционала, дальше лучше :)"

    # ========================================
    #         ИГРЫ
    # ========================================
    if clean in ["камень", "ножницы", "бумага"]:
        return game_rps(clean)
    if "игра монетка" in clean or "подбрось монетку" in clean:
        return game_coin()
    if "игра угадай" in clean or "угадай число" in clean:
        return game_guess_start()
    if secret_number is not None:
        nums = re.findall(r"\d+", clean)
        if nums:
            return game_guess_check(int(nums[0]))

    # Счётчик
    if "сброс счётчика" in clean:
        message_count = 0
        return "🧹 Счётчик обнулён!"

    if not user_name:
        return "Бро, а как тебя зовут? 😊"

    # Базовые ответы
    if clean == "спасибо":
        return f"Всегда пожалуйста, {user_name}! 😊"
    if "анекдот" in clean:
        jokes = ["Колобок повесился.", "Идёт медведь по лесу, видит — машина горит. Сел в неё и сгорел.", "— Доктор, меня все игнорируют.\n— Следующий!"]
        return random.choice(jokes)

    if any(char.isdigit() for char in clean):
        return "Напиши число с командой, например: Таблица 5"

    return f"{user_name}, я тебя услышал. Напиши понятнее или спроси 'помощь' 😊"

# ============================================
# ----------- ЗАПУСК -------------------------
# ============================================

def main():
    load_profile()
    load_chats()
    
    print("========== 🤖 MYXA AI (CONSOLE) ==========")
    if user_name:
        print(f"С возвращением, {user_name}!")
    else:
        print("Привет! Как тебя зовут?")
    print("Введи 'выход' для завершения, '/help' для команд\n")
    
    while True:
        try:
            user_input = input("Ты: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Пока!")
            break
        
        if user_input.lower() == "выход":
            print(f"👋 До встречи, {user_name or 'друг'}!")
            break
        
        response = process_input(user_input)
        if response:
            print(f"MYXA AI: {response}")
        
        # Сохраняем в историю текущего чата
        chats[current_chat].append({"sender": "Ты", "text": user_input})
        chats[current_chat].append({"sender": "MYXA AI", "text": response})
        save_chats()

if __name__ == "__main__":
    main()