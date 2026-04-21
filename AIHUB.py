# ============================================
# AI HUB — ЧАТЫ С НЕЙРОСЕТЯМИ
# Автор: Мухаммад
# ============================================
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import json
import os
import threading
import time
import urllib.request
import subprocess

# ============================================
# ----------- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ----------
# ============================================

APP_NAME = "AI HUB"
DATA_FILE = "ai_hub_chats.json"
SETTINGS_FILE = "ai_hub_settings.json"

MODELS = {
    "phi3": "🤖 Phi-3 (Ollama)",
    "llama3.2": "🦙 Llama 3.2 (Ollama)",
    "deepseek-r1:7b": "🧠 DeepSeek-R1 (Ollama)",
    "mistral": "🌪️ Mistral (Ollama)",
    "dialogpt": "💬 DialoGPT (Бесплатно)",
    "saiga": "🇷🇺 Saiga (Бесплатно)",
    "flan-t5": "📚 Flan-T5 (Бесплатно)",
    "gigachat": "🤖 GigaChat (Сбер)"
}

current_model = "phi3"
current_theme = "light"
chat_history = {}
bottom_buttons = []

# === ПЕРЕКЛЮЧАТЕЛИ ===
internet_enabled = True   # Интернет вкл/выкл
deep_thinking = False     # Глубокое мышление

# Токен GigaChat (замени на свой)
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

def load_chats():
    global chat_history
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                chat_history = json.load(f)
        except:
            chat_history = {}
    for model in MODELS.keys():
        if model not in chat_history:
            chat_history[model] = []

def save_chats():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

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

load_chats()
load_settings()

# ============================================
# ----------- СОЗДАНИЕ ОКНА ------------------
# ============================================

root = tk.Tk()
root.title(APP_NAME)
root.geometry("900x700")
root.resizable(True, True)

# ============================================
# ----------- ПРИМЕНЕНИЕ ТЕМЫ ----------------
# ============================================

def apply_theme():
    theme = THEMES[current_theme]
    root.configure(bg=theme["bg"])
    try:
        chat_box.configure(bg=theme["bg"], fg=theme["fg"])
        entry_box.configure(bg=theme["input_bg"], fg=theme["input_fg"])
        model_menu.configure(bg=theme["btn_bg"], fg=theme["btn_fg"])
        for btn in bottom_buttons:
            btn.configure(bg=theme["btn_bg"], fg=theme["btn_fg"])
    except:
        pass

def next_theme():
    global current_theme
    themes_list = list(THEMES.keys())
    idx = themes_list.index(current_theme)
    current_theme = themes_list[(idx + 1) % len(themes_list)]
    save_settings()
    apply_theme()
    add_message("AI HUB", f"🎨 Тема: {current_theme}")

# ============================================
# ----------- ПЕРЕКЛЮЧАТЕЛИ ------------------
# ============================================

def toggle_internet():
    """Включение/выключение интернета"""
    global internet_enabled
    internet_enabled = not internet_enabled
    status = "🟢 ВКЛ" if internet_enabled else "🔴 ВЫКЛ"
    add_message("AI HUB", f"🌐 Интернет: {status}")

def toggle_deep_thinking():
    """Включение/выключение глубокого мышления"""
    global deep_thinking, current_model
    deep_thinking = not deep_thinking
    status = "🟢 ВКЛ" if deep_thinking else "🔴 ВЫКЛ"
    add_message("AI HUB", f"🧠 Глубокое мышление: {status}")
    
    # Автоматически переключаем на DeepSeek при включении
    if deep_thinking:
        current_model = "deepseek-r1:7b"
        model_var.set(MODELS["deepseek-r1:7b"])
        load_current_chat()
        add_message("AI HUB", "🤖 Модель изменена на DeepSeek-R1")
    else:
        # При выключении мышления сбрасываем модель на phi3
        current_model = "phi3"
        model_var.set(MODELS["phi3"])
        load_current_chat()

# ============================================
# ----------- ИНТЕРФЕЙС ----------------------
# ============================================

top_frame = tk.Frame(root)
top_frame.pack(fill="x", padx=5, pady=5)

tk.Label(top_frame, text="Модель:", font=("Arial", 12)).pack(side="left", padx=5)

model_var = tk.StringVar(value=MODELS[current_model])
model_menu = tk.OptionMenu(top_frame, model_var, *MODELS.values())
model_menu.pack(side="left", padx=5)

def on_model_change(*args):
    global current_model, deep_thinking
    display_name = model_var.get()
    for key, value in MODELS.items():
        if value == display_name:
            current_model = key
            break
    # Сбрасываем мышление при смене модели (если не DeepSeek)
    if current_model != "deepseek-r1:7b":
        deep_thinking = False
    load_current_chat()

model_var.trace("w", on_model_change)

# Чат
chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 11), height=25)
chat_box.pack(fill="both", padx=5, pady=5, expand=True)
chat_box.config(state=tk.DISABLED)

# Поле ввода
entry_frame = tk.Frame(root)
entry_frame.pack(fill="x", padx=5, pady=5)

entry_box = tk.Entry(entry_frame, font=("Arial", 13))
entry_box.pack(side="left", fill="x", expand=True)

def send_message():
    text = entry_box.get().strip()
    if not text:
        return
    entry_box.delete(0, tk.END)
    add_message("Вы", text)
    threading.Thread(target=ai_thread, args=(text,)).start()

def ai_thread(text):
    response = ask_ai(text, current_model)
    add_message(MODELS[current_model], response)

entry_box.bind("<Return>", lambda e: send_message())

# Кнопки
button_frame = tk.Frame(root)
button_frame.pack(fill="x", padx=5, pady=5)

def make_button(text, command):
    btn = tk.Button(button_frame, text=text, width=10, command=command)
    btn.pack(side="left", padx=2, pady=3)
    bottom_buttons.append(btn)
    return btn

send_btn = tk.Button(entry_frame, text="➤", width=5, command=send_message)
send_btn.pack(side="right", padx=5)

make_button("🎨 Темы", next_theme)
make_button("🧹 Очистить", lambda: clear_chat())
make_button("📁 Чаты", lambda: show_chats_list())
make_button("🌐 Инет", toggle_internet)
make_button("🧠 Мышление", toggle_deep_thinking)

# ============================================
# ----------- ЛОГИКА ЧАТА --------------------
# ============================================

def add_message(sender, text):
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, f"{sender}: {text}\n\n")
    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)
    
    if current_model in chat_history:
        chat_history[current_model].append({"sender": sender, "text": text})
    else:
        chat_history[current_model] = [{"sender": sender, "text": text}]
    save_chats()

def load_current_chat():
    chat_box.config(state=tk.NORMAL)
    chat_box.delete("1.0", tk.END)
    if current_model in chat_history:
        for msg in chat_history[current_model]:
            chat_box.insert(tk.END, f"{msg['sender']}: {msg['text']}\n\n")
    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)

def clear_chat():
    if current_model in chat_history:
        chat_history[current_model] = []
    save_chats()
    load_current_chat()
    add_message("AI HUB", "🧹 Чат очищен")

def show_chats_list():
    win = tk.Toplevel(root)
    win.title("📁 Чаты")
    win.geometry("300x400")
    
    listbox = tk.Listbox(win, font=("Arial", 12))
    listbox.pack(fill="both", expand=True, padx=10, pady=10)
    
    for model, display in MODELS.items():
        listbox.insert(tk.END, display)
    
    def switch_chat():
        sel = listbox.curselection()
        if sel:
            idx = sel[0]
            model_key = list(MODELS.keys())[idx]
            global current_model, deep_thinking
            current_model = model_key
            if current_model != "deepseek-r1:7b":
                deep_thinking = False
            model_var.set(MODELS[model_key])
            load_current_chat()
            win.destroy()
    
    tk.Button(win, text="📂 Открыть", command=switch_chat).pack(pady=5)
    tk.Button(win, text="❌ Закрыть", command=win.destroy).pack(pady=5)

# ============================================
# ----------- НЕЙРОСЕТИ ----------------------
# ============================================

def ask_ai(prompt, model):
    # Проверка интернета для онлайн-моделей
    if not internet_enabled and model in ["dialogpt", "saiga", "flan-t5", "gigachat"]:
        return "🔴 Интернет выключен! Нажми кнопку '🌐 Инет'."
    
    # Ollama
    if model in ["phi3", "llama3.2", "deepseek-r1:7b", "mistral"]:
        try:
            # Если включено мышление и модель DeepSeek
            if deep_thinking and model == "deepseek-r1:7b":
                prompt = f"Think step by step: {prompt}"
            
            command = f'cmd /c "ollama run {model} {prompt}"'
            result = subprocess.run(command, capture_output=True, text=True, shell=True, timeout=120, encoding='utf-8', errors='ignore')
            return result.stdout.strip() or "🤖 Модель промолчала..."
        except Exception as e:
            return f"❌ Ошибка Ollama: {str(e)[:50]}"
    
    # Hugging Face
    if model in ["dialogpt", "saiga", "flan-t5"]:
        urls = {
            "dialogpt": "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
            "saiga": "https://api-inference.huggingface.co/models/IlyaGusev/saiga_llama3_8b",
            "flan-t5": "https://api-inference.huggingface.co/models/google/flan-t5-small"
        }
        try:
            data = json.dumps({"inputs": prompt, "parameters": {"max_length": 200}}).encode('utf-8')
            req = urllib.request.Request(urls[model], data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=45) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result[0]['generated_text']
        except Exception as e:
            return f"❌ Ошибка API: {str(e)[:50]}"
    
    # GigaChat
    if model == "gigachat":
        if GIGACHAT_TOKEN == "ТВОЙ_ТОКЕН_ОТ_СБЕРА":
            return "❌ Токен GigaChat не указан."
        try:
            import requests
            url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GIGACHAT_TOKEN}", "Content-Type": "application/json"}
            payload = {"model": "GigaChat", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
            response = requests.post(url, headers=headers, json=payload, timeout=30, verify=False)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"❌ Ошибка API: {response.status_code}"
        except Exception as e:
            return f"❌ Ошибка: {str(e)[:50]}"
    
    return "❌ Неизвестная модель"

# ============================================
# ----------- ЗАПУСК -------------------------
# ============================================

apply_theme()
load_current_chat()
root.mainloop()