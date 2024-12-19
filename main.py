import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3  # Модуль для работы с SQLite

def initialize_database():
    conn = sqlite3.connect("autoshop.db")  # Файл базы данных
    cursor = conn.cursor()
    
    # Создаем таблицу товаров, если она не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        price REAL NOT NULL,
                        quantity INTEGER NOT NULL
                      )''')
    
    conn.commit()
    conn.close()


# Создаем главное окно
root = tk.Tk()
root.title("Система магазина автозапчастей")
root.geometry("800x600")


def search_products(tree, name_entry, category_entry, min_price_entry, max_price_entry):
    """Фильтрация товаров на основе заданных критериев."""
    name = name_entry.get()
    category = category_entry.get()
    min_price = min_price_entry.get()
    max_price = max_price_entry.get()

    # Формируем SQL-запрос с фильтрацией
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    if category:
        query += " AND category LIKE ?"
        params.append(f"%{category}%")
    if min_price:
        try:
            min_price = float(min_price)
            query += " AND price >= ?"
            params.append(min_price)
        except ValueError:
            messagebox.showerror("Ошибка", "Минимальная цена должна быть числом!")
            return
    if max_price:
        try:
            max_price = float(max_price)
            query += " AND price <= ?"
            params.append(max_price)
        except ValueError:
            messagebox.showerror("Ошибка", "Максимальная цена должна быть числом!")
            return

    # Выполняем запрос и обновляем таблицу
    conn = sqlite3.connect("autoshop.db")
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    # Очищаем таблицу
    for row in tree.get_children():
        tree.delete(row)

    # Заполняем таблицу результатами поиска
    for row in rows:
        tree.insert("", "end", values=row)


def delete_product(tree):
    """Удаление выбранного товара из базы данных и таблицы."""
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите товар для удаления!")
        return

    # Получаем ID выбранного товара
    item = tree.item(selected_item)
    product_id = item["values"][0]

    # Удаляем запись из базы данных
    conn = sqlite3.connect("autoshop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

    # Удаляем строку из таблицы интерфейса
    tree.delete(selected_item)

    messagebox.showinfo("Успех", "Товар успешно удален!")


def edit_product(tree, name_entry, category_entry, price_entry, quantity_entry):
    """Редактирование выбранного товара."""
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите товар для редактирования!")
        return

    # Получаем ID выбранного товара
    item = tree.item(selected_item)
    product_id = item["values"][0]

    # Получаем новые значения из полей ввода
    name = name_entry.get()
    category = category_entry.get()
    price = price_entry.get()
    quantity = quantity_entry.get()

    # Проверка на заполненность полей
    if not (name and category and price and quantity):
        messagebox.showerror("Ошибка", "Заполните все поля!")
        return

    try:
        price = float(price)
        quantity = int(quantity)
    except ValueError:
        messagebox.showerror("Ошибка", "Цена должна быть числом, а количество — целым числом!")
        return

    # Обновляем запись в базе данных
    conn = sqlite3.connect("autoshop.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name = ?, category = ?, price = ?, quantity = ? WHERE id = ?",
                   (name, category, price, quantity, product_id))
    conn.commit()
    conn.close()

    # Обновляем данные в таблице интерфейса
    tree.item(selected_item, values=(product_id, name, category, price, quantity))

    # Очищаем поля ввода
    name_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)

    messagebox.showinfo("Успех", "Товар успешно обновлен!")


# Функция для выхода
def exit_app():
    root.quit()

# Функция для окна "О программе"
def show_about():
    messagebox.showinfo("О программе", "Система магазина автозапчастей\nВерсия 1.0")


def open_products_window():
    products_window = tk.Toplevel(root)
    products_window.title("Управление товарами")
    products_window.geometry("800x600")

    # Заголовок окна
    label = tk.Label(products_window, text="Управление товарами", font=("Arial", 14))
    label.pack(pady=10)

    # Поля для фильтрации товаров
    filter_frame = tk.Frame(products_window)
    filter_frame.pack(pady=10)

    tk.Label(filter_frame, text="Search by Name:").grid(row=0, column=0, padx=5)
    search_name = tk.Entry(filter_frame)
    search_name.grid(row=0, column=1, padx=5)

    tk.Label(filter_frame, text="Category:").grid(row=0, column=2, padx=5)
    search_category = tk.Entry(filter_frame)
    search_category.grid(row=0, column=3, padx=5)

    tk.Label(filter_frame, text="Min Price:").grid(row=1, column=0, padx=5)
    min_price = tk.Entry(filter_frame)
    min_price.grid(row=1, column=1, padx=5)

    tk.Label(filter_frame, text="Max Price:").grid(row=1, column=2, padx=5)
    max_price = tk.Entry(filter_frame)
    max_price.grid(row=1, column=3, padx=5)

    # Кнопка для выполнения поиска
    btn_search = tk.Button(filter_frame, text="Search",
                           command=lambda: search_products(tree, search_name, search_category, min_price, max_price))
    btn_search.grid(row=2, column=0, columnspan=4, pady=10)

    # Таблица для отображения товаров
    tree = ttk.Treeview(products_window, columns=("ID", "Name", "Category", "Price", "Quantity"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Category", text="Category")
    tree.heading("Price", text="Price")
    tree.heading("Quantity", text="Quantity")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Поля для добавления или редактирования товара
    add_frame = tk.Frame(products_window)
    add_frame.pack(pady=10)

    tk.Label(add_frame, text="Name:").grid(row=0, column=0, padx=5)
    entry_name = tk.Entry(add_frame)
    entry_name.grid(row=0, column=1, padx=5)

    tk.Label(add_frame, text="Category:").grid(row=0, column=2, padx=5)
    entry_category = tk.Entry(add_frame)
    entry_category.grid(row=0, column=3, padx=5)

    tk.Label(add_frame, text="Price:").grid(row=1, column=0, padx=5)
    entry_price = tk.Entry(add_frame)
    entry_price.grid(row=1, column=1, padx=5)

    tk.Label(add_frame, text="Quantity:").grid(row=1, column=2, padx=5)
    entry_quantity = tk.Entry(add_frame)
    entry_quantity.grid(row=1, column=3, padx=5)

    # Кнопка для добавления товара
    btn_add = tk.Button(add_frame, text="Add Product", command=lambda: add_product(entry_name, entry_category, entry_price, entry_quantity, tree))
    btn_add.grid(row=2, column=0, columnspan=4, pady=10)

    # Кнопка для редактирования товара
    btn_edit = tk.Button(add_frame, text="Edit Product",
                         command=lambda: edit_product(tree, entry_name, entry_category, entry_price, entry_quantity))
    btn_edit.grid(row=3, column=0, columnspan=4, pady=10)

    # Кнопка для удаления товара
    btn_delete = tk.Button(add_frame, text="Delete Product", command=lambda: delete_product(tree))
    btn_delete.grid(row=4, column=0, columnspan=4, pady=10)

        # Кнопка для сброса фильтров
    btn_reset = tk.Button(filter_frame, text="Reset Filters", command=lambda: load_products(tree))
    btn_reset.grid(row=2, column=4, padx=10)


    # Загружаем товары в таблицу
    load_products(tree)


def load_products(tree):
    """Загружает товары из базы данных в таблицу."""
    conn = sqlite3.connect("autoshop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()

    # Очищаем таблицу
    for row in tree.get_children():
        tree.delete(row)

    # Заполняем таблицу
    for row in rows:
        tree.insert("", "end", values=row)


def add_product(name_entry, category_entry, price_entry, quantity_entry, tree):
    """Добавление товара в базу данных и обновление таблицы."""
    name = name_entry.get()
    category = category_entry.get()
    price = price_entry.get()
    quantity = quantity_entry.get()

    # Проверка на заполненность полей
    if not (name and category and price and quantity):
        messagebox.showerror("Ошибка", "Заполните все поля!")
        return

    try:
        price = float(price)
        quantity = int(quantity)
    except ValueError:
        messagebox.showerror("Ошибка", "Цена должна быть числом, а количество — целым числом!")
        return

    # Добавляем данные в базу данных
    conn = sqlite3.connect("autoshop.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, category, price, quantity) VALUES (?, ?, ?, ?)",
                   (name, category, price, quantity))
    conn.commit()
    conn.close()

    # Обновляем таблицу интерфейса
    tree.insert("", "end", values=(cursor.lastrowid, name, category, price, quantity))

    # Очищаем поля ввода
    name_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)

    messagebox.showinfo("Успех", "Товар добавлен!")

# Меню
menu = tk.Menu(root)
root.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Файл", menu=file_menu)
file_menu.add_command(label="Выход", command=exit_app)

manage_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Управление", menu=manage_menu)
manage_menu.add_command(label="Товары", command=open_products_window)

help_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Справка", menu=help_menu)
help_menu.add_command(label="О программе", command=show_about)

# Заголовок в главном окне
label = tk.Label(root, text="Добро пожаловать в систему магазина автозапчастей!", font=("Arial", 16))
label.pack(pady=20)

# Инициализация базы данных перед запуском главного окна
if __name__ == "__main__":
    initialize_database()  # Создаем таблицы в базе данных, если они не существуют
    root.mainloop()        # Запускаем главное окно приложения
