import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import filedialog
import json
import os
from PIL import Image, ImageTk
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

root = tk.Tk()
root.title("Коллекция фильмов")
root.geometry("600x500")
root.resizable(False, False)
icon_img = Image.open(resource_path("icon.ico"))
icon_photo = ImageTk.PhotoImage(icon_img)
root.wm_iconphoto(True, icon_photo)

canvas = tk.Canvas(root, width=600, height=500, highlightthickness=0)
canvas.pack(fill="both", expand=True)

bg_image = Image.open(resource_path("bg.png"))
bg_image = bg_image.resize((600, 500))
bg_photo = ImageTk.PhotoImage(bg_image)

canvas.create_image(0, 0, image=bg_photo, anchor="nw")

FILENAME = "movies.json"

# -------- Загрузка данных --------------
if os.path.exists(FILENAME):
    with open(FILENAME, "r", encoding="utf8") as f:
        movies = json.load(f)

else:
    movies = {
        "Боевики": [{"name": "Терминатор", "path": ""}, {"name": "Рокки", "path": ""}],
        "Фантастика": [{"name": "Матрица", "path": ""}, {"name": "Начало", "path": ""}],
        "Комедии": []
    }

# ----------- Переменные --------------
current_category = tk.StringVar()
current_category.set(list(movies.keys())[0])

search_text = tk.StringVar()

display_map = []
# ------------------ Функции ------------------
def save_movies():
    with open(FILENAME, "w", encoding="utf8") as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)

def refresh():
    save_movies()
    update_listbox()

def update_category_menu():
    menu = category_menu["menu"]
    menu.delete(0, "end")
    for cat in movies:
        menu.add_command(
            label=cat,
            command=lambda c=cat: current_category.set(c)
        )

def update_listbox(*args):
    listbox.delete(0, tk.END)
    display_map.clear()
    query = search_text.get().lower()
    shown = 0

    if query:
        for cat, films in movies.items():
            for i, film in enumerate(films):
                if query in film["name"].lower():
                    listbox.insert(
                        tk.END,
                        f"{cat} - {film['name']}"
                    )
                    display_map.append((cat, i))
                    shown += 1

        count_label.config(text=f"Найдено: {shown}")

    else:
        cat = current_category.get()
        films = movies[cat]

        for i, film in enumerate(films):
            listbox.insert(tk.END, film["name"])
            display_map.append((cat, i))
            shown += 1

        count_label.config(
            text=f"{cat} - {shown} / {len(films)}"
        )

def add_movie():
    name = simpledialog.askstring("Добавить фильм", "Название фильма:")
    if not name:
        return
    
    name = name.strip()
    if not name:
        messagebox.showwarning("Ошибка", "Название фильма не может быть пустым")
        return
    
    path = filedialog.askopenfilename(
        title="Выберите файл фильма",
        filetypes=[
            ("Видео файлы", "*.mp4 *.mkv *avi *.mov"),
            ("Все файлы", "*.*")
        ]
    )

    if not path:
        messagebox.showwarning("Отмена", "Файл фильма не выбран")
        return
    
    for film in movies[current_category.get()]:
        if film["name"].lower() == name.lower():
            messagebox.showerror("Ошибка", "Такой фильм уже есть")
            return
        
    movies[current_category.get()].append({
        "name": name,
        "path": path
    })

    refresh()
    messagebox.showinfo("Готово", "Фильм добавлен")

def change_movie_path():
    sel = listbox.curselection()
    if not sel:
        messagebox.showwarning("Ошибка", "Выберите фильм")
        return

    cat, index = display_map[sel[0]]
    film = movies[cat][index]

    new_path = filedialog.askopenfilename(
        title=f"Выберите новый файл для '{film['name']}'",
        filetypes=[
            ("Видео файлы", "*.mp4 *.mkv *.avi *.mov"),
            ("Все файлы", "*.*")
        ]
    )

    if not new_path:
        return
    
    film["path"] = new_path
    save_movies()
    messagebox.showinfo("Готово", "Файл фильма обновлён")

def delete_movie():
    sel = listbox.curselection()
    if not sel:
        messagebox.showwarning("Удаление", "Выберите фильм для удаления")
        return
    
    if not messagebox.askyesno("Подтверждение", "Удалить выбранный фильм?"):
        return
    
    cat, index = display_map[sel[0]]
    del movies[cat][index]

    refresh()

def sort_movies():
    cat = current_category.get()
    movies[cat].sort(key=lambda f: f["name"])
    refresh()

def add_category():
    name = simpledialog.askstring("Новая категория", "Название категории:")
    if not name:
        return
    
    name = name.strip()
    if not name:
        messagebox.showwarning("Ошибка", "Название категории не может быть пустым")
        return
    
    if name in movies:
        messagebox.showerror("Ошибка", "Такая категория уже существует")
        return
    
    movies[name] = []
    refresh()
    update_category_menu()
    current_category.set(name)

def delete_category():
    cat = current_category.get()

    if movies[cat]:
        messagebox.showerror(
            "Ошибка",
            "Нельзя удалить категорию с фильмами"
        )
        return
    
    if not messagebox.askyesno(
        "Подтверждение",
        f"Удалить категорию '{cat}'?"
    ):
        return
    
    del movies[cat]

    current_category.set(next(iter(movies)))
    refresh()
    update_category_menu()

def on_double_click(event):
    sel = listbox.curselection()
    if not sel:
        return
    
    cat, index = display_map[sel[0]]
    film = movies[cat][index]

    old_name = film["name"]
    new_name = simpledialog.askstring("Переименовать фильм", f"Новое название для '{old_name}':")

    if not new_name:
        return
    new_name = new_name.strip()
    if not new_name:
        messagebox.showwarning("Ошибка", "Название фильма не может быть пустым")
        return
    if any(f["name"] == new_name for f in movies[cat]):
        messagebox.showerror("Ошибка", "Такой фильм уже есть")
        return
    
    film["name"] = new_name
    refresh()
    messagebox.showinfo("Готово", f"Фильм '{old_name}' переименован в '{new_name}'")

def open_movie():
    sel = listbox.curselection()
    if not sel:
        return
    
    cat, index = display_map[sel[0]]
    film = movies[cat][index]

    path = film.get("path", "")
    if not path or not os.path.exists(path):
        messagebox.showerror(
            "Ошибка",
            "Файл фильма не найден"
        )
        return
    
    os.startfile(path)


def show_context_menu(event):
    index = listbox.nearest(event.y)
    if index >= 0:
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(index)
        context_menu.tk_popup(event.x_root, event.y_root)

# ---------------Интерфейс ----------------
#заголовок
canvas.create_text(
    142, 12,
    text="Моя коллекция фильмов",
    font=("Arial", 18, "bold"),
    fill="#000000",
    anchor="nw"
)
canvas.create_text(
    140, 10, 
    text="Моя коллекция фильмов",
    font=("Arial", 18, "bold"),
    fill="#ffffff",
    anchor="nw"
)
#счётчик
count_label = tk.Label(
    root, 
    text="", 
    font=("Arial", 10), 
    bg="#d3d3d3", 
    relief="ridge",
    borderwidth=1,
    padx=10,
    pady=4
    )
canvas.create_window(100, 60, window=count_label)
#категории
category_menu = tk.OptionMenu(root, current_category, *movies.keys())
category_menu.config(width=15, bg="#ffffff", fg="#000000")
category_menu["menu"].config(bg="#ffffff", fg="#000000")
canvas.create_window(300, 100, window=category_menu)

current_category.trace_add("write", update_listbox)
search_text.trace_add("write", update_listbox)
#поиск
tk.Label(root, text="Поиск", bg="#f0f0f0").pack()
search_entry = tk.Entry(root, textvariable=search_text, bg="#ffffff", fg="#000000")
canvas.create_window(500, 60, window=search_entry)
#список фильмов
listbox_frame = tk.Frame(root, padx=6, pady=6)
listbox = tk.Listbox(
    listbox_frame,
    height=10,
    bg="#f0f0f0",
    fg="#000000",
    selectbackground="#E20D0D",
    relief="flat",
    bd=0
)

listbox.pack()
canvas.create_window(300, 200, window=listbox_frame)
listbox.bind("<Double-1>", lambda e: open_movie())
listbox.bind("<Delete>", lambda e: delete_movie())
listbox.bind("<Button-3>", show_context_menu)

context_menu = tk.Menu(root, tearoff=0)

context_menu.add_command(label="▶ Открыть", command=open_movie)
context_menu.add_command(label="✏ Переименовать", command=on_double_click)
context_menu.add_command(label="📁 Изменить файл", command=change_movie_path)
context_menu.add_separator()
context_menu.add_command(label="🗑 Удалить", command=delete_movie)

btn_params = {"width": 20, "bg": "#0078d7", "fg": "white"}
add_button = tk.Button(root, text="Добавить фильм", command=add_movie, **btn_params)
canvas.create_window(300, 320, window=add_button)
sort_button = tk.Button(root, text="Сортировать А-Я", command=sort_movies, **btn_params)
canvas.create_window(300, 360, window=sort_button)
add_cat_button = tk.Button(root, text="Добавить категорию", command=add_category, **btn_params)
canvas.create_window(300, 400, window=add_cat_button)
del_cat_button = tk.Button(root, text="Удалить категорию", command=delete_category, **btn_params)
canvas.create_window(300,440, window=del_cat_button)


update_listbox()
root.bind("<Return>", lambda e: add_movie())
root.bind("<Control-f>", lambda e: search_entry.focus())
root.mainloop()