import tkinter as tk
from tkinter import messagebox
import random
from datetime import datetime
import os
import json

count = 0
user_name = None
PROFILE_FILE = "myxa_profile.json"

# ============================================
#         ЗАГРУЗКА ИМЕНИ
# ============================================

def load_name():
    global user_name
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                user_name = data.get("name")
        except:
            user_name = None

def save_name(name):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump({"name": name}, f, ensure_ascii=False)

load_name()

# ============================================
#         ИНТЕРФЕЙС
# ============================================

root = tk.Tk()
root.title("MYXAAI V1 TKINTER ED.")
root.geometry("700x500")

entry = tk.Entry(root, width=40, font=("Arial", 14))
entry.pack(pady=10)

output_label = tk.Label(root, text="MYXAAI", wraplength=300, font=("Arial", 12))
output_label.pack(pady=10)

# Приветствие при запуске
if user_name:
    output_label.config(text=f"С возвращением, {user_name}! Чем могу помочь?")
else:
    output_label.config(text="Привет! Как тебя зовут?")

# ============================================
#         ФУНКЦИИ
# ============================================

def show_time():
    now = datetime.now().strftime("%H:%M:%S")
    output_label.config(text=f"ИИ: На часах: {now}")
    messagebox.showinfo("Время", f"На часах: {now}")

def show_help_box():
    messagebox.showwarning("Помощь", "Напиши: привет, пока, таблица 5, как дела")

def show_info():
    messagebox.showinfo("Статистика", f"Вы отправили {count} сообщений")

def check_question():
    global count, user_name
    
    question = entry.get().lower().strip()
    entry.delete(0, tk.END)
    
    if question == "":
        return
        
    count += 1
    processed = False

    # ========================================
    #         ЗАПОМИНАНИЕ ИМЕНИ
    # ========================================
    
    if "меня зовут" in question:
        name = question.replace("меня зовут", "").strip()
        if len(name) >= 2:
            user_name = name.capitalize()
            save_name(user_name)
            output_label.config(text=f"ИИ: Приятно познакомиться, {user_name}! Чем могу помочь?")
            processed = True
            return
    
    if "зови меня" in question:
        name = question.replace("зови меня", "").strip()
        if len(name) >= 2:
            user_name = name.capitalize()
            save_name(user_name)
            output_label.config(text=f"ИИ: Хорошо, буду звать тебя {user_name}!")
            processed = True
            return

    if question == "как меня зовут":
        if user_name:
            output_label.config(text=f"ИИ: Тебя зовут {user_name}!")
        else:
            output_label.config(text="ИИ: Ты ещё не представился!")
        processed = True
        return

    if question == "забудь меня":
        user_name = None
        if os.path.exists(PROFILE_FILE):
            os.remove(PROFILE_FILE)
        output_label.config(text="ИИ: Я забыл твоё имя 😢")
        processed = True
        return

    # ========================================
    #         ПРИВЕТСТВИЯ
    # ========================================
    
    if question == "привет":
        answers = ["Привет!", "Здравствуй!", "Рад тебя видеть!"]
        if user_name:
            output_label.config(text=f"ИИ: {random.choice(answers)} {user_name}!")
        else:
            output_label.config(text="ИИ: " + random.choice(answers) + " Как тебя зовут?")
        processed = True

    elif "ку" in question:
        if user_name:
            output_label.config(text=f"ИИ: Ку, {user_name}! С чем помочь?")
        else:
            output_label.config(text="ИИ: Ку! Как тебя зовут?")
        processed = True

    elif question == "хай":
        if user_name:
            output_label.config(text=f"ИИ: Хай, {user_name}! С чем помочь?")
        else:
            output_label.config(text="ИИ: Хай! Как тебя зовут?")
        processed = True

    elif question == "здравствуй":
        if user_name:
            output_label.config(text=f"ИИ: Здравствуй, {user_name}! С чем помочь?")
        else:
            output_label.config(text="ИИ: Здравствуй! Как тебя зовут?")
        processed = True

    elif question == "здарова":
        if user_name:
            output_label.config(text=f"ИИ: Здарова, {user_name}! С чем помочь?")
        else:
            output_label.config(text="ИИ: Здарова! Как тебя зовут?")
        processed = True

    # ========================================
    #         ВРЕМЯ
    # ========================================
    
    elif any(w in question for w in ["сколько времени", "который час", "время"]):
        now = datetime.now().strftime("%H:%M")
        if user_name:
            output_label.config(text=f"ИИ: {user_name}, сейчас {now}")
        else:
            output_label.config(text=f"ИИ: Сейчас {now}")
        processed = True

    # ========================================
    #         ПОМОЩЬ / КОМАНДЫ
    # ========================================
    
    elif "какие ты знаешь команду" in question or question in ["помощь", "помогите"]:
        output_label.config(text="ИИ: Привет, Как дела, Время, Таблица, Пока, Меня зовут..., Как меня зовут, Забудь меня")
        processed = True

    # ========================================
    #         СЧЁТЧИК СООБЩЕНИЙ
    # ========================================
    
    elif "сколько сообщений" in question:
        if user_name:
            output_label.config(text=f"ИИ: {user_name}, мы написали {count} сообщений")
        else:
            output_label.config(text=f"ИИ: Мы написали {count} сообщений")
        processed = True

    # ========================================
    #         КАК ДЕЛА / НАСТРОЕНИЕ
    # ========================================
    
    elif "как дела" in question or "как ты" in question:
        if user_name:
            output_label.config(text=f"ИИ: У меня всё хорошо, {user_name}! А у тебя?")
        else:
            output_label.config(text="ИИ: У меня всё хорошо! А у тебя?")
        processed = True

    elif any(w in question for w in ["все норм", "все нормально", "у меня все хорошо"]):
        if user_name:
            output_label.config(text=f"ИИ: Рад за тебя, {user_name}! А настроение как?")
        else:
            output_label.config(text="ИИ: Рад за тебя! А как тебя зовут?")
        processed = True

    # ========================================
    #         КТО ТЫ
    # ========================================
    
    elif any(w in question for w in ["кто ты", "что ты", "ты бот"]):
        if user_name:
            output_label.config(text=f"ИИ: Я MYXA AI, {user_name}. Твой помощник!")
        else:
            output_label.config(text="ИИ: Я MYXA AI. А как тебя зовут?")
        processed = True

    # ========================================
    #         ТАБЛИЦА УМНОЖЕНИЯ
    # ========================================
    
    elif "таблица" in question:
        words = question.split()
        found = False
        for word in words:
            if word.isdigit():
                num = int(word)
                result = f"Таблица умножения на {num}:\n"
                for i in range(1, 11):
                    result += f"{num} × {i} = {num*i}\n"
                output_label.config(text=result)
                found = True
                processed = True
                break
        if not found:
            output_label.config(text="ИИ: Напиши число, например: Таблица 5")
            processed = True

    # ========================================
    #         ПРОЩАНИЕ
    # ========================================
    
    elif question in ["пока", "бай", "до свидания"]:
        answers = ["До свидания!", "Бай! Заходи ещё!", "Пока!"]
        if user_name:
            output_label.config(text=f"ИИ: {random.choice(answers)} Рад был помочь, {user_name}!")
        else:
            output_label.config(text="ИИ: " + random.choice(answers))
        processed = True

    # ========================================
    #         ПО УМОЛЧАНИЮ
    # ========================================
    
    if not processed:
        if user_name:
            output_label.config(text=f"ИИ: {user_name}, я пока не понимаю. Напиши 'помощь'!")
        else:
            output_label.config(text="ИИ: Я пока не понимаю. Напиши 'помощь' или представься (меня зовут...)")

# ============================================
#         КНОПКИ
# ============================================

btn_send = tk.Button(root, text="Отправить", command=check_question)
btn_send.pack(pady=5)

btn_stats = tk.Button(root, text="Статистика", command=show_info)
btn_stats.pack(pady=5)

btn_help = tk.Button(root, text="Справка", command=show_help_box)
btn_help.pack(pady=5)

btn_time = tk.Button(root, text="Время", command=show_time)
btn_time.pack(pady=5)

root.mainloop()