# ============================================
# CHAT MANAGER — Система чатов для MYXA AI
# Версия: 1.0
# Безопасное расширение (не трогает основной код)
# ============================================

import json
import os
import tkinter as tk
from tkinter import simpledialog, messagebox

CHATS_FILE = "myxa_chats.json"

# ============================================
#         ЗАГРУЗКА / СОХРАНЕНИЕ ЧАТОВ
# ============================================

def load_chats():
    """Загружает список чатов из файла"""
    if os.path.exists(CHATS_FILE):
        try:
            with open(CHATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"Главный чат": []}
    return {"Главный чат": []}

def save_chats(chats):
    """Сохраняет чаты в файл"""
    with open(CHATS_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)

# ============================================
#         КЛАСС УПРАВЛЕНИЯ ЧАТАМИ
# ============================================

class ChatManager:
    def __init__(self, app_module):
        """
        app_module — ссылка на основной модуль myxa_ai
        Нужна чтобы доступаться к функциям: add_message, load_current_chat и т.д.
        """
        self.app = app_module
        self.chats = load_chats()
        self.current_chat = "Главный чат"
        
        # Синхронизируем с основным приложением
        self.app.chat_history = self.chats
        self.app.current_chat = self.current_chat
        
    def create_chat(self, name=None):
        """Создать новый чат"""
        if name is None:
            name = simpledialog.askstring("Новый чат", "Введите название чата:")
        
        if not name:
            return None
        
        if name in self.chats:
            messagebox.showwarning("Ошибка", f"Чат '{name}' уже существует!")
            return None
        
        self.chats[name] = []
        save_chats(self.chats)
        self.app.add_message("MYXA AI", f"✅ Чат '{name}' создан!")
        return name
    
    def switch_chat(self, name):
        """Переключиться на другой чат"""
        if name in self.chats:
            self.current_chat = name
            self.app.current_chat = name
            self.app.chat_history = self.chats
            self.app.load_current_chat()
            self.app.add_message("MYXA AI", f"📂 Переключено на: {name}")
            return True
        return False
    
    def delete_chat(self, name):
        """Удалить чат"""
        if len(self.chats) <= 1:
            messagebox.showwarning("Ошибка", "Нельзя удалить единственный чат!")
            return False
        
        if name not in self.chats:
            return False
        
        if messagebox.askyesno("Удалить чат", f"Вы уверены, что хотите удалить чат '{name}'?"):
            del self.chats[name]
            
            if self.current_chat == name:
                self.current_chat = list(self.chats.keys())[0]
                self.app.current_chat = self.current_chat
            
            save_chats(self.chats)
            self.app.chat_history = self.chats
            self.app.load_current_chat()
            self.app.add_message("MYXA AI", f"🗑 Чат '{name}' удалён")
            return True
        return False
    
    def rename_chat(self, old_name, new_name):
        """Переименовать чат"""
        if old_name not in self.chats:
            return False
        
        if new_name in self.chats:
            messagebox.showwarning("Ошибка", f"Чат '{new_name}' уже существует!")
            return False
        
        self.chats[new_name] = self.chats.pop(old_name)
        
        if self.current_chat == old_name:
            self.current_chat = new_name
            self.app.current_chat = new_name
        
        save_chats(self.chats)
        self.app.add_message("MYXA AI", f"✏ Чат '{old_name}' переименован в '{new_name}'")
        return True
    
    def get_chat_list(self):
        """Вернуть список всех чатов"""
        return list(self.chats.keys())
    
    def show_chat_menu(self):
        """Показать окно управления чатами"""
        menu = tk.Toplevel(self.app.root)
        menu.title("📁 Управление чатами")
        menu.geometry("350x500")
        menu.resizable(False, False)
        menu.configure(bg="#2c2c2c" if self.app.current_theme == "dark" else "#f0f0f0")
        
        # Заголовок
        title_color = "white" if self.app.current_theme == "dark" else "black"
        bg_color = "#2c2c2c" if self.app.current_theme == "dark" else "#f0f0f0"
        
        tk.Label(menu, text="📁 МОИ ЧАТЫ", font=("Arial", 14, "bold"), 
                 bg=bg_color, fg=title_color).pack(pady=15)
        
        # Фрейм для списка
        list_frame = tk.Frame(menu, bg=bg_color)
        list_frame.pack(fill="both", padx=20, pady=5, expand=True)
        
        # Список чатов
        listbox = tk.Listbox(list_frame, font=("Arial", 12), height=12,
                             bg="#3c3c3c" if self.app.current_theme == "dark" else "white",
                             fg="white" if self.app.current_theme == "dark" else "black")
        listbox.pack(side="left", fill="both", expand=True)
        
        # Скроллбар
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        
        # Заполняем список
        for chat in self.chats.keys():
            listbox.insert(tk.END, chat)
            if chat == self.current_chat:
                listbox.itemconfig(tk.END, bg="#4CAF50", fg="white")
        
        # Кнопки
        btn_frame = tk.Frame(menu, bg=bg_color)
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="➕ Новый", 
                  command=lambda: self._create_and_refresh(menu, listbox),
                  width=12, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=3)
        
        tk.Button(btn_frame, text="📂 Открыть", 
                  command=lambda: self._switch_and_close(menu, listbox),
                  width=12, bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=3)
        
        tk.Button(btn_frame, text="✏ Переим.", 
                  command=lambda: self._rename_and_refresh(listbox),
                  width=12, bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=3)
        
        tk.Button(btn_frame, text="🗑 Удалить", 
                  command=lambda: self._delete_and_refresh(listbox),
                  width=12, bg="#f44336", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=3)
        
        tk.Button(menu, text="Закрыть", command=menu.destroy, 
                  width=20, bg="#9E9E9E", fg="white", font=("Arial", 10)).pack(pady=10)
        
        # Двойной клик для открытия
        listbox.bind("<Double-Button-1>", lambda e: self._switch_and_close(menu, listbox))
    
    def _create_and_refresh(self, menu, listbox):
        name = self.create_chat()
        if name:
            menu.destroy()
            self.show_chat_menu()
    
    def _switch_and_close(self, menu, listbox):
        sel = listbox.curselection()
        if sel:
            name = listbox.get(sel[0])
            self.switch_chat(name)
            menu.destroy()
    
    def _delete_and_refresh(self, listbox):
        sel = listbox.curselection()
        if sel:
            name = listbox.get(sel[0])
            if self.delete_chat(name):
                self._refresh_listbox(listbox)
    
    def _rename_and_refresh(self, listbox):
        sel = listbox.curselection()
        if sel:
            old_name = listbox.get(sel[0])
            new_name = simpledialog.askstring("Переименовать", "Введите новое название:", initialvalue=old_name)
            if new_name and new_name != old_name:
                if self.rename_chat(old_name, new_name):
                    self._refresh_listbox(listbox)
    
    def _refresh_listbox(self, listbox):
        listbox.delete(0, tk.END)
        for chat in self.chats.keys():
            listbox.insert(tk.END, chat)
            if chat == self.current_chat:
                listbox.itemconfig(tk.END, bg="#4CAF50", fg="white")


# ============================================
#         ФУНКЦИЯ ИНТЕГРАЦИИ
# ============================================

def integrate_chats(app_module):
    """
    Подключает систему чатов к основному приложению.
    Вызови эту функцию в myxa_ai.py после создания интерфейса.
    
    Пример:
        import sys
        chat_manager = integrate_chats(sys.modules[__name__])
    """
    manager = ChatManager(app_module)
    app_module.chat_manager = manager
    return manager


# ============================================
#         КОМАНДЫ ДЛЯ ЧАТА (ОПЦИОНАЛЬНО)
# ============================================

def process_chat_commands(app, text):
    """
    Обработчик команд чата для вставки в process_ai.
    Вызови в начале process_ai:
    
        chat_cmd = process_chat_commands(app, clean)
        if chat_cmd:
            return chat_cmd
    """
    t = text.lower()
    manager = app.chat_manager
    
    if t.startswith("/newchat") or t == "новый чат":
        name = text.replace("/newchat", "").strip()
        if name:
            created = manager.create_chat(name)
        else:
            created = manager.create_chat()
        return f"✅ Чат '{created}' создан!" if created else "❌ Не удалось создать чат"
    
    if t.startswith("/switch "):
        name = text[8:].strip()
        if manager.switch_chat(name):
            return f"📂 Переключено на: {name}"
        return f"❌ Чат '{name}' не найден"
    
    if t == "/chats" or t == "список чатов":
        chats = manager.get_chat_list()
        return "📁 Чаты:\n" + "\n".join(f"• {c}" for c in chats)
    
    if t.startswith("/deletechat "):
        name = text[12:].strip()
        if manager.delete_chat(name):
            return f"🗑 Чат '{name}' удалён"
        return f"❌ Не удалось удалить чат '{name}'"
    
    if t.startswith("/renamechat "):
        parts = text[12:].strip().split(" ", 1)
        if len(parts) == 2:
            old, new = parts
            if manager.rename_chat(old, new):
                return f"✏ Чат '{old}' переименован в '{new}'"
        return "❌ Формат: /renamechat старое_название новое_название"
    
    return None