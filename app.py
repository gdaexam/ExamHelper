import g4f
import tkinter as tk
from tkinter import messagebox
import threading
import tempfile
import os

MESSAGES = []
CURRENT_MODE = "chat"

def get_response(query):
    MESSAGES.append({"role": "user", "content": query})
    response = g4f.ChatCompletion.create(model=g4f.models.gpt_4, messages=MESSAGES)
    MESSAGES.append({"role": "assistant", "content": response})
    return response

def switch_mode():
    global CURRENT_MODE
    if CURRENT_MODE == "chat":
        CURRENT_MODE = "mp3"
        show_mp3_player()
    else:
        CURRENT_MODE = "chat"

def show_mp3_player():
    label.pack_forget()
    entry.pack_forget()
    send_button.pack_forget()
    text_frame.pack_forget()
    mode_button.forget()
    
    mp3_frame.pack(pady=10, expand=True, fill='both')

def select_mp3_file():
    from tkinter import filedialog
    filename = filedialog.askopenfilename(
        title="Выберите MP3 файл",
        filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
    )
    if filename:
        file_label.config(text=f"Выбран файл: {filename.split('/')[-1]}")
        messagebox.showerror("MP3 Плеер", f"Ошибка! {filename} не может быть вопспроизведен!")

def paste_text(event=None):
    try:
        clipboard_text = window.clipboard_get()
        entry.insert(tk.INSERT, clipboard_text)
        return "break"
    except tk.TclError:
        pass

def on_key_press(event):
    if event.state & 0x4 and event.keysym == 'v':
        paste_text()
        return "break"
    elif event.state & 0x4 and event.keycode == 86:
        paste_text()
        return "break"

def create_icon():
    try:
        import requests
        from PIL import Image, ImageTk
        
        url = "https://images.icon-icons.com/47/PNG/128/mp3_9838.png"
        response = requests.get(url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        
        temp_icon_path = os.path.join(tempfile.gettempdir(), "mp3_player_icon.ico")
        img.save(temp_icon_path, format="ICO")
        
        return temp_icon_path
    except:
        return None

def main():
    global window, frame, text_frame, chat_display, scrollbar
    global label, entry, send_button, mode_button, mp3_frame, file_label
    
    window = tk.Tk()
    window.title("MP3 PLAYER")
    window.geometry("450x425")

    icon_path = create_icon()
    if icon_path and os.path.exists(icon_path):
        window.iconbitmap(icon_path)

    frame = tk.Frame(window)
    frame.pack(expand=True, fill='both')

    mode_button = tk.Button(frame, text="MP3 Плеер", command=switch_mode, width=10, height=1, font=("Arial", 8))
    mode_button.pack(anchor='ne', padx=5, pady=5)

    text_frame = tk.Frame(frame)

    chat_display = tk.Text(text_frame, wrap='word', width=40, height=15, state='disabled', font=("Arial", 10))
    chat_display.pack(side='left', fill='both', expand=True)

    scrollbar = tk.Scrollbar(text_frame, command=chat_display.yview)
    scrollbar.pack(side='right', fill='y')
    chat_display['yscrollcommand'] = scrollbar.set

    chat_display.tag_config("user_tag", foreground="blue", justify="left")
    chat_display.tag_config("assistant_tag", foreground="green", justify="left")
    chat_display.tag_config("thinking_tag", foreground="gray", justify="left", font=("Arial", 9, "italic"))

    mp3_frame = tk.Frame(frame)
    
    mp3_title = tk.Label(mp3_frame, text="MP3 Плеер", font=("Arial", 16, "bold"))
    mp3_title.pack(pady=20)
    
    select_button = tk.Button(mp3_frame, text="Выбрать MP3 файл", command=select_mp3_file, width=20, height=2)
    select_button.pack(pady=10)
    
    file_label = tk.Label(mp3_frame, text="Файл не выбран", wraplength=300)
    file_label.pack(pady=10)
    
    controls_frame = tk.Frame(mp3_frame)
    controls_frame.pack(pady=20)
    
    play_button = tk.Button(controls_frame, text="▶", font=("Arial", 12), width=3)
    play_button.pack(side='left', padx=5)
    
    pause_button = tk.Button(controls_frame, text="⏸", font=("Arial", 12), width=3)
    pause_button.pack(side='left', padx=5)
    
    stop_button = tk.Button(controls_frame, text="⏹", font=("Arial", 12), width=3)
    stop_button.pack(side='left', padx=5)
    
    copyright_label = tk.Label(mp3_frame, text="©️MP3 Technologies, 2025")
    copyright_label.pack(pady=70)
    
    text_frame.pack(pady=10, expand=True, fill='both')

    def update_chat_display(role, content, tag=None):
        chat_display.config(state='normal')
        if role == "user":
            chat_display.insert(tk.END, "Вы: " + content + "\n", "user_tag")
        elif role == "assistant":
            chat_display.insert(tk.END, "AI: " + content + "\n", "assistant_tag")
        elif role == "thinking":
             chat_display.insert(tk.END, content + "\n", "thinking_tag")

        chat_display.config(state='disabled')
        chat_display.see(tk.END)

    def on_send_button_click():
        query = entry.get().strip()

        if not query:
            messagebox.showwarning("Предупреждение", "запрос не может быть пустым")
            return

        update_chat_display("user", query)
        entry.delete(0, tk.END)

        entry.config(state='disabled')
        send_button.config(state='disabled')
        update_chat_display("thinking", "Нейросеть думает...", "thinking_tag")

        threading.Thread(target=lambda: process_g4f_response(query)).start()

    def process_g4f_response(query):
        response_text = get_response(query)
        window.after(0, lambda: handle_response_in_main_thread(response_text))

    def handle_response_in_main_thread(response_text):
        idx_start = chat_display.search("Нейросеть думает...", "1.0", tk.END, backwards=True, nocase=True, regexp=False)
        if idx_start:
            idx_end = chat_display.index(f"{idx_start} lineend")
            chat_display.config(state='normal')
            chat_display.delete(idx_start, f"{idx_end}+1c")
            chat_display.config(state='disabled')
            chat_display.see(tk.END)

        update_chat_display("assistant", response_text)
        entry.config(state='normal')
        send_button.config(state='normal')
        entry.focus_set()

    label = tk.Label(frame, text="Введите запрос:")
    entry = tk.Entry(frame, width=50)
    
    entry.bind('<Control-KeyPress>', on_key_press)
    entry.bind('<Control-v>', paste_text)
    entry.bind('<Control-V>', paste_text)
    
    send_button = tk.Button(frame, text="Отправить", command=on_send_button_click)

    label.pack(pady=5)
    entry.pack(pady=5)
    send_button.pack(pady=5)

    window.mainloop()

if __name__ == "__main__":
    from io import BytesIO
    main()