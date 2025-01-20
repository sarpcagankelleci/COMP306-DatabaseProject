# Imports for UI
import os

import customtkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import date
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Imports for database
import mysql.connector
import csv

# Database Connection
db_connection = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="Emsalinur12345",
  auth_plugin='mysql_native_password'
)
print(db_connection)
db_cursor = db_connection.cursor(buffered=True)

#deneme

# Helper Function: Populate Table from CSV
def populate_table(file_path, insert_query):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            # Convert 'NULL' strings to Python None
            row = [None if value == 'NULL' else value for value in row]
            db_cursor.execute(insert_query, row)
    db_connection.commit()



# Initialize Database
db_cursor.execute("DROP DATABASE IF EXISTS library")
db_cursor.execute("CREATE DATABASE IF NOT EXISTS library")
db_cursor.execute("USE library")

# Create Tables
db_cursor.execute("DROP TABLE IF EXISTS BorrowingHistory")

db_cursor.execute("""
    CREATE TABLE Admins (
        admin_id CHAR(6) PRIMARY KEY,
        password VARCHAR(50)
    )
""")

db_cursor.execute("""
    CREATE TABLE Books (
        book_id CHAR(6) PRIMARY KEY,
        title VARCHAR(100),
        author VARCHAR(50),
        genre VARCHAR(30),
        year_published INT,
        quantity INT,
        language VARCHAR(50),
        page_number INT
    )
""")
db_cursor.execute("""
    CREATE TABLE Members (
        member_id CHAR(6) PRIMARY KEY,
        first_name VARCHAR(30),
        last_name VARCHAR(30),
        phone_number VARCHAR(15),
        email VARCHAR(50)
    )
""")
# Create Borrowing Table
db_cursor.execute("""
    CREATE TABLE Borrowing (
        borrow_id INT AUTO_INCREMENT PRIMARY KEY,
        book_id CHAR(6),
        member_id CHAR(6),
        borrow_date DATE,
        planned_return_date DATE,
        actual_return_date DATE,
        FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE ON UPDATE NO ACTION,
        FOREIGN KEY (member_id) REFERENCES Members(member_id) ON DELETE CASCADE ON UPDATE NO ACTION
    )
""")



# Insert Admin Data
db_cursor.execute("""
    INSERT INTO Admins (admin_id, password) VALUES
    ('ADM001', '1234'),
    ('ADM002', '2345'),
    ('ADM003', '3456'),
    ('ADM004', '4567'),
    ('ADM005', '5678')
""")
db_connection.commit()

# Insert Data
insert_books_query = """
    INSERT INTO Books (book_id, title, author, genre, year_published, quantity, language, page_number)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""
populate_table("./data/Books.csv", insert_books_query)

insert_members_query = """
    INSERT INTO Members (member_id, first_name, last_name, phone_number, email)
    VALUES (%s, %s, %s, %s, %s)
"""
populate_table("./data/Members.csv", insert_members_query)

insert_borrowing_query = """
    INSERT INTO Borrowing (borrow_id, book_id, member_id, borrow_date, planned_return_date, actual_return_date)
    VALUES (%s, %s, %s, %s, %s, %s)
"""


populate_table("./data/Borrowing.csv", insert_borrowing_query)


def sort_treeview(tree, column, is_numeric=False):

    data = [(tree.set(child, column), child) for child in tree.get_children("")]

    # Determine sort order
    if is_numeric:
        data.sort(key=lambda item: float(item[0]) if item[0].isdigit() else 0, reverse=sort_treeview.descending)
    else:
        data.sort(key=lambda item: item[0], reverse=sort_treeview.descending)

    for index, (val, child) in enumerate(data):
        tree.move(child, "", index)

    # Toggle order for next click
    sort_treeview.descending = not sort_treeview.descending


# Set default sorting order
sort_treeview.descending = False

def setup_sorting(tree, columns, numeric_columns=None):

    if numeric_columns is None:
        numeric_columns = set()

    for col_index, col_name in enumerate(columns):
        is_numeric = col_index in numeric_columns  # Determine if the column is numeric
        tree.heading(col_name, text=col_name, command=lambda col=col_name, num=is_numeric: sort_treeview(tree, col, num))


# Login Screen
def login_screen():
    login_window = customtkinter.CTk()
    login_window.title("Admin Login")
    login_window.geometry("400x300")

    # Fetch Admin IDs for dropdown
    db_cursor.execute("SELECT admin_id FROM Admins")
    admin_ids = [row[0] for row in db_cursor.fetchall()]

    # Admin ID Dropdown
    admin_id_label = customtkinter.CTkLabel(login_window, text="Select Admin ID:")
    admin_id_label.pack(pady=10)
    admin_id_combo = ttk.Combobox(login_window, values=admin_ids, state="readonly")
    admin_id_combo.pack(pady=10)

    # Password Entry
    password_label = customtkinter.CTkLabel(login_window, text="Password:")
    password_label.pack(pady=10)
    password_entry = customtkinter.CTkEntry(login_window, show="*")
    password_entry.pack(pady=10)

    # Validate Login Function
    def validate_login():
        admin_id = admin_id_combo.get()
        password = password_entry.get()

        if not admin_id or not password:
            messagebox.showwarning("Input Error", "Please select Admin ID and enter Password.")
            return

        db_cursor.execute("SELECT * FROM Admins WHERE admin_id = %s AND password = %s", (admin_id, password))
        admin = db_cursor.fetchone()

        if admin:
            messagebox.showinfo("Login Successful", f"Welcome, {admin_id}!")
            login_window.destroy()
            start_main_app()  # Ana uygulamayı başlat
        else:
            messagebox.showerror("Login Failed", "Invalid Admin ID or Password.")

    # Login Button
    login_button = customtkinter.CTkButton(login_window, text="Login", command=validate_login)
    login_button.pack(pady=20)

    login_window.mainloop()


# Main App
def start_main_app():
    customtkinter.set_appearance_mode("Light")
    main_app = customtkinter.CTk()
    main_app.title("Library Management System")
    main_app.geometry("1200x700+70+0")
    main_app.resizable(False, False)

    # Time Label
    time_label = Label(main_app, font=("Arial", 10), fg="grey")
    time_label.pack(side="bottom", anchor="e", pady=5)
    update_time_label(time_label)  # Start updating time

    # Tabview Setup
    tabview = customtkinter.CTkTabview(master=main_app)
    tabview.pack(pady=10, padx=10, fill="both", expand=True)

    # Define Tabs
    tabs = ["Books", "Members", "Borrowing", "Borrowing History", "Analytics"]
    for tab in tabs:
        tabview.add(tab)
    tabview.set("Books")

    # Create a Frame for buttons in the Books tab
    button_frame = Frame(tabview.tab("Books"))
    button_frame.pack(pady=10, padx=10, fill="x")  # Centered horizontally

    # Books Tab
    books_tree_columns = (
    "Book ID", "Title", "Author", "Genre", "Year Published", "Quantity", "Language", "Page Number")
    books_tree = ttk.Treeview(tabview.tab("Books"), columns=books_tree_columns, show="headings", selectmode="browse")
    books_tree.pack(fill="both", expand=True)

    for col in books_tree_columns:
        books_tree.heading(col, text=col)

    setup_sorting(books_tree, books_tree_columns, numeric_columns={4, 5, 7})

    def refresh_books_tree():
        books_tree.delete(*books_tree.get_children())
        db_cursor.execute("SELECT * FROM Books")
        for book in db_cursor.fetchall():
            books_tree.insert("", END, values=book)

    refresh_books_tree()

    def open_add_book_window():
        add_book_window = Toplevel(main_app)
        add_book_window.title("Add Book")
        add_book_window.geometry("400x700")

        book_id_label = Label(add_book_window, text="Book ID")
        book_id_label.pack(pady=5)
        book_id_entry = Entry(add_book_window)
        book_id_entry.pack(pady=5)

        title_label = Label(add_book_window, text="Title")
        title_label.pack(pady=5)
        title_entry = Entry(add_book_window)
        title_entry.pack(pady=5)

        author_label = Label(add_book_window, text="Author")
        author_label.pack(pady=5)
        author_entry = Entry(add_book_window)
        author_entry.pack(pady=5)

        genre_label = Label(add_book_window, text="Genre")
        genre_label.pack(pady=5)
        genre_entry = Entry(add_book_window)
        genre_entry.pack(pady=5)

        year_label = Label(add_book_window, text="Year Published")
        year_label.pack(pady=5)
        year_entry = Entry(add_book_window)
        year_entry.pack(pady=5)

        quantity_label = Label(add_book_window, text="Quantity")
        quantity_label.pack(pady=5)
        quantity_entry = Entry(add_book_window)
        quantity_entry.pack(pady=5)

        language_label = Label(add_book_window, text="Language")
        language_label.pack(pady=5)
        language_entry = Entry(add_book_window)
        language_entry.pack(pady=5)

        page_number_label = Label(add_book_window, text="Page Number")
        page_number_label.pack(pady=5)
        page_number_entry = Entry(add_book_window)
        page_number_entry.pack(pady=5)

        def add_book():
            book_id = book_id_entry.get()
            title = title_entry.get()
            author = author_entry.get()
            genre = genre_entry.get()
            year_published = year_entry.get()
            quantity = quantity_entry.get()
            language= language_entry.get()
            page_number = page_number_entry.get()

            # Book ID formatını kontrol et
            if not book_id.startswith("BK"):
                messagebox.showwarning("Invalid Book ID", "Book ID must start with 'BK'.")
                return

            # Title, Author ve Genre için minimum 3 karakter kontrolü
            if len(title) < 3:
                messagebox.showwarning("Invalid Title", "Title must contain at least 3 characters.")
                return
            if len(author) < 3:
                messagebox.showwarning("Invalid Author", "Author must contain at least 3 characters.")
                return
            if len(genre) < 3:
                messagebox.showwarning("Invalid Genre", "Genre must contain at least 3 characters.")
                return
            if len(language) < 3:
                messagebox.showwarning("Invalid language", "language must contain at least 3 characters.")
                return

            # Year Published kontrolü (4 rakamlı sayı)
            if not year_published.isdigit() or len(year_published) != 4 or int(year_published)> 2025:
                messagebox.showwarning("Invalid Year", "Year Published must be a 4-digit number.")
                return

            if not page_number.isdigit() or int(page_number) <= 0:
                messagebox.showwarning("Invalid page number", "Year Published must be bigger than 0.")
                return


            # Diğer alanların boş olup olmadığını kontrol et
            if not all([book_id, title, author, genre, year_published, quantity, language, page_number]):
                messagebox.showwarning("Input Error", "Please fill all fields.")
                return

            try:
                # Veritabanına ekleme işlemi
                db_cursor.execute(insert_books_query,
                                  (book_id, title, author, genre, int(year_published), int(quantity), language, int(page_number) ))
                db_connection.commit()
                refresh_books_tree()
                messagebox.showinfo("Success", "Book added successfully!")

                csv_file_path = "./data/Books.csv"
                file_exists = os.path.isfile(csv_file_path)

                with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)

                    # Write the header if the file is new
                    if not file_exists:
                        writer.writerow(
                            ['book_id', 'title', 'author', 'genre', 'year_published', 'quantity', 'language',
                             'page_number'])

                    # Append the new book
                    writer.writerow([book_id, title, author, genre, year_published, quantity, language, page_number])

                add_book_window.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}")

        add_book_button = Button(add_book_window, text="Add Book", command=add_book)
        add_book_button.pack(pady=10)

    def delete_book():
        selected_item = books_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No book selected.")
            return

        book_id = books_tree.item(selected_item, 'values')[0]
        db_cursor.execute("DELETE FROM Books WHERE book_id = %s", (book_id,))
        db_connection.commit()
        refresh_tabs()
        messagebox.showinfo("Success", f"Book with ID {book_id} has been deleted.")

    add_book_button = Button(button_frame, text="Add Book", command=open_add_book_window)
    add_book_button.pack(side=LEFT, padx=5)

    delete_book_button = Button(button_frame, text="Delete Book", command=delete_book)
    delete_book_button.pack(side=LEFT, padx=5)

    def open_update_book_window():
        selected_item = books_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No book selected.")
            return

        book_values = books_tree.item(selected_item, 'values')
        book_id = book_values[0]

        update_book_window = Toplevel(main_app)
        update_book_window.title("Update Book")
        update_book_window.geometry("400x700")

        # Labels and Entries
        fields = ["Title", "Author", "Genre", "Year Published", "Quantity", "Language", "Page Number"]
        entries = {}

        for field, value in zip(fields, book_values[1:]):
            Label(update_book_window, text=field).pack(pady=5)
            entry = Entry(update_book_window)
            entry.insert(0, value)
            entry.pack(pady=5)
            entries[field] = entry

        def update_book():
            title = entries["Title"].get()
            author = entries["Author"].get()
            genre = entries["Genre"].get()
            year_published = entries["Year Published"].get()
            quantity = entries["Quantity"].get()
            language = entries["Language"].get()
            page_number = entries["Page Number"].get()

            if not all([title, author, genre, year_published, quantity, language, page_number]):
                messagebox.showwarning("Input Error", "Please fill all fields.")
                return

            try:
                db_cursor.execute("""
                    UPDATE Books
                    SET title=%s, author=%s, genre=%s, year_published=%s, quantity=%s, language=%s, page_number=%s
                    WHERE book_id=%s
                """, (title, author, genre, int(year_published), int(quantity), language, int(page_number), book_id))

                db_connection.commit()
                refresh_tabs()
                messagebox.showinfo("Success", "Book updated successfully!")
                update_book_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

        update_book_button = Button(update_book_window, text="Update Book", command=update_book)
        update_book_button.pack(pady=10)

    update_book_button = Button(button_frame, text="Update Book", command=open_update_book_window)
    update_book_button.pack(side=LEFT, padx=5)

    ### Search Books Feature
    def search_books():
        # Yeni bir pencere oluştur
        search_window = Toplevel(main_app)
        search_window.title("Search Books")
        search_window.geometry("400x400")

        # Kitap arama kriterleri için label ve entry bölümleri
        title_label = Label(search_window, text="Title")
        title_label.pack(pady=5)
        title_entry = Entry(search_window)
        title_entry.pack(pady=5)

        author_label = Label(search_window, text="Author")
        author_label.pack(pady=5)
        author_entry = Entry(search_window)
        author_entry.pack(pady=5)

        genre_label = Label(search_window, text="Genre")
        genre_label.pack(pady=5)
        genre_entry = Entry(search_window)
        genre_entry.pack(pady=5)

        year_label = Label(search_window, text="Year Published")
        year_label.pack(pady=5)
        year_entry = Entry(search_window)
        year_entry.pack(pady=5)

        # Arama Fonkisyonu
        def perform_search():
            # Kullanıcı kriterlerini oku
            title = title_entry.get()
            author = author_entry.get()
            genre = genre_entry.get()
            year_published = year_entry.get()

            # Dinamik SQL Query oluştur
            query = "SELECT * FROM Books WHERE 1=1"
            params = []

            if title:
                query += " AND title LIKE %s"
                params.append(f"%{title}%")
            if author:
                query += " AND author LIKE %s"
                params.append(f"%{author}%")
            if genre:
                query += " AND genre LIKE %s"
                params.append(f"%{genre}%")
            if year_published:
                if year_published.isdigit():
                    query += " AND year_published = %s"
                    params.append(year_published)
                else:
                    messagebox.showwarning("Input Error", "Year Published should be a number.")
                    return

            # Veritabanında sorguyu çalıştır ve kitap ağacını güncelle
            db_cursor.execute(query, tuple(params))
            results = db_cursor.fetchall()

            # Mevcut tabloda sonuçları göster
            books_tree.delete(*books_tree.get_children())
            for book in results:
                books_tree.insert("", END, values=book)

            # Kullanıcıya bilgi ver
            messagebox.showinfo("Search Complete", f"{len(results)} results found.")
            search_window.destroy()

        # Arama butonu
        search_button = Button(search_window, text="Search", command=perform_search)
        search_button.pack(pady=20)

    def reset_books():
        """Resets the book list to show all books."""
        books_tree.delete(*books_tree.get_children())
        db_cursor.execute("SELECT * FROM Books")
        for book in db_cursor.fetchall():
            books_tree.insert("", END, values=book)
        messagebox.showinfo("Reset", "Book list has been reset.")

    # Search Books Button
    search_books_button = Button(button_frame, text="Search Books", command=search_books)
    search_books_button.pack(side=LEFT, padx=5)

    reset_button = Button(button_frame, text="Reset", command=reset_books)
    reset_button.pack(side=LEFT, padx=5)

    def open_category_filter_window():
        """
        Opens a new window to allow filtering books by their genre/category and adds a reset button.
        """
        filter_window = Toplevel(main_app)
        filter_window.title("Category Filter")
        filter_window.geometry("400x300")

        # Fetch distinct categories
        db_cursor.execute("SELECT DISTINCT genre FROM Books")
        categories = [row[0] for row in db_cursor.fetchall()]

        if not categories:
            messagebox.showinfo("No Categories", "No categories found in the database.")
            filter_window.destroy()
            return

        # Dropdown for category selection
        category_label = Label(filter_window, text="Select Category:")
        category_label.pack(pady=10)

        category_combo = ttk.Combobox(filter_window, values=categories, state="readonly")
        category_combo.pack(pady=10)

        def filter_books_by_category():
            selected_category = category_combo.get()
            if not selected_category:
                messagebox.showwarning("Input Error", "Please select a category.")
                return

            # Refresh Books Tree with filtered data
            books_tree.delete(*books_tree.get_children())
            db_cursor.execute("SELECT * FROM Books WHERE genre = %s", (selected_category,))
            filtered_books = db_cursor.fetchall()

            if not filtered_books:
                messagebox.showinfo("No Results", f"No books found in the category '{selected_category}'.")
            else:
                for book in filtered_books:
                    books_tree.insert("", END, values=book)

            filter_window.destroy()

        def reset_books_table():
            """
            Resets the filter and loads all books into the Books Tree.
            """
            books_tree.delete(*books_tree.get_children())
            db_cursor.execute("SELECT * FROM Books")
            for book in db_cursor.fetchall():
                books_tree.insert("", END, values=book)
            filter_window.destroy()

        # Filter Button
        filter_button = Button(filter_window, text="Filter", command=filter_books_by_category)
        filter_button.pack(pady=10)

        # Reset Button
        reset_button = Button(filter_window, text="Reset", command=reset_books_table)
        reset_button.pack(pady=10)

    # Add Category Filter Button to the Books Tab
    category_filter_button = Button(button_frame, text="Category Filter", command=open_category_filter_window)
    category_filter_button.pack(side=LEFT, padx=5)

    def open_sort_option_window():
        """
        Opens the first window to allow users to select the column to sort by.
        """
        sort_option_window = Toplevel(main_app)
        sort_option_window.title("Sort Option")
        sort_option_window.geometry("400x200")

        # Instruction label
        Label(sort_option_window, text="Select Sort Option:", font=("Arial", 12, "bold")).pack(pady=10)

        # Sort options
        sort_option_var = StringVar(value="Year Published")
        Radiobutton(sort_option_window, text="Year Published", variable=sort_option_var, value="Year Published").pack(
            pady=5)
        Radiobutton(sort_option_window, text="Quantity", variable=sort_option_var, value="Quantity").pack(pady=5)
        Radiobutton(sort_option_window, text="Page Number", variable=sort_option_var, value="Page Number").pack(pady=5)

        def open_sort_order_window():
            """
            Opens the second window to allow users to select the sort order and closes the first window.
            """
            # Close the first window
            sort_option_window.destroy()

            # Open the second window
            sort_order_window = Toplevel(main_app)
            sort_order_window.title("Sort Order")
            sort_order_window.geometry("400x200")

            # Instruction label
            Label(sort_order_window, text="Choose Sort Order:", font=("Arial", 12, "bold")).pack(pady=10)

            # Sort order options
            sort_order_var = StringVar(value="Ascending")
            Radiobutton(sort_order_window, text="Ascending", variable=sort_order_var, value="Ascending").pack(pady=5)
            Radiobutton(sort_order_window, text="Descending", variable=sort_order_var, value="Descending").pack(pady=5)

            def sort_books():
                """
                Sorts the books based on the selected column and order.
                """
                sort_option = sort_option_var.get()
                sort_order = sort_order_var.get()

                # Determine column name
                if sort_option == "Year Published":
                    column_name = "year_published"
                elif sort_option == "Quantity":
                    column_name = "quantity"
                else:
                    column_name = "page_number"

                # Construct and execute query
                query = f"SELECT * FROM Books ORDER BY {column_name} {'ASC' if sort_order == 'Ascending' else 'DESC'}"
                books_tree.delete(*books_tree.get_children())
                db_cursor.execute(query)
                for book in db_cursor.fetchall():
                    books_tree.insert("", END, values=book)

                # Close the sort order window
                sort_order_window.destroy()

            # Sort Button
            Button(sort_order_window, text="Sort", command=sort_books).pack(pady=20)

        # Next Button to open the sort order window
        Button(sort_option_window, text="Next", command=open_sort_order_window).pack(pady=20)

    # Add the Sort Button to the Books Tab
    sort_button = Button(button_frame, text="Sort", command=open_sort_option_window)
    sort_button.pack(side=LEFT, padx=5)

    ### Members Tab
    members_tree_columns = ("Member ID", "First Name", "Last Name", "Phone Number", "Email")
    members_tree = ttk.Treeview(tabview.tab("Members"), columns=members_tree_columns, show="headings", selectmode="browse")
    members_tree.pack(fill="both", expand=True)

    for col in members_tree_columns:
        members_tree.heading(col, text=col)

    setup_sorting(members_tree, members_tree_columns)

    def refresh_members_tree():
        members_tree.delete(*members_tree.get_children())
        db_cursor.execute("SELECT * FROM Members")
        for member in db_cursor.fetchall():
            members_tree.insert("", END, values=member)

    refresh_members_tree()

    def open_add_member_window():
        add_member_window = Toplevel(main_app)
        add_member_window.title("Add Member")
        add_member_window.geometry("400x400")

        member_id_label = Label(add_member_window, text="Member ID")
        member_id_label.pack(pady=5)
        member_id_entry = Entry(add_member_window)
        member_id_entry.pack(pady=5)

        first_name_label = Label(add_member_window, text="First Name")
        first_name_label.pack(pady=5)
        first_name_entry = Entry(add_member_window)
        first_name_entry.pack(pady=5)

        last_name_label = Label(add_member_window, text="Last Name")
        last_name_label.pack(pady=5)
        last_name_entry = Entry(add_member_window)
        last_name_entry.pack(pady=5)

        phone_number_label = Label(add_member_window, text="Phone Number")
        phone_number_label.pack(pady=5)
        phone_number_entry = Entry(add_member_window)
        phone_number_entry.pack(pady=5)

        email_label = Label(add_member_window, text="Email")
        email_label.pack(pady=5)
        email_entry = Entry(add_member_window)
        email_entry.pack(pady=5)

        def add_member():
            member_id = member_id_entry.get()
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            phone_number = phone_number_entry.get()
            email = email_entry.get()

            if not all([member_id, first_name, last_name, phone_number, email]):
                messagebox.showwarning("Input Error", "Please fill all fields.")
                return

            db_cursor.execute(insert_members_query, (member_id, first_name, last_name, phone_number, email))
            db_connection.commit()
            refresh_members_tree()
            messagebox.showinfo("Success", "Member added successfully!")
            add_member_window.destroy()

        add_member_button = Button(add_member_window, text="Add Member", command=add_member)
        add_member_button.pack(pady=10)

    def open_update_member_window():
        selected_item = members_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No member selected.")
            return

        member_values = members_tree.item(selected_item, 'values')
        member_id = member_values[0]

        update_member_window = Toplevel(main_app)
        update_member_window.title("Update Member")
        update_member_window.geometry("400x500")

        fields = ["First Name", "Last Name", "Phone Number", "Email"]
        entries = {}

        for field, value in zip(fields, member_values[1:]):
            Label(update_member_window, text=field).pack(pady=5)
            entry = Entry(update_member_window)
            entry.insert(0, value)
            entry.pack(pady=5)
            entries[field] = entry

        def update_member():
            first_name = entries["First Name"].get()
            last_name = entries["Last Name"].get()
            phone_number = entries["Phone Number"].get()
            email = entries["Email"].get()

            if not all([first_name, last_name, phone_number, email]):
                messagebox.showwarning("Input Error", "Please fill all fields.")
                return

            try:
                db_cursor.execute("""
                    UPDATE Members
                    SET first_name=%s, last_name=%s, phone_number=%s, email=%s
                    WHERE member_id=%s
                """, (first_name, last_name, phone_number, email, member_id))

                db_connection.commit()
                refresh_tabs()
                messagebox.showinfo("Success", "Member updated successfully!")
                update_member_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

        update_member_button = Button(update_member_window, text="Update Member", command=update_member)
        update_member_button.pack(pady=10)

    update_member_button = Button(tabview.tab("Members"), text="Update Member", command=open_update_member_window)
    update_member_button.pack(pady=5)

    def delete_member():
        selected_item = members_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No member selected.")
            return

        member_id = members_tree.item(selected_item, 'values')[0]
        db_cursor.execute("DELETE FROM Members WHERE member_id = %s", (member_id,))
        db_connection.commit()
        refresh_tabs()
        messagebox.showinfo("Success", f"Member with ID {member_id} has been deleted.")

    add_member_button = Button(tabview.tab("Members"), text="Add Member", command=open_add_member_window)
    add_member_button.pack(pady=5)

    delete_member_button = Button(tabview.tab("Members"), text="Delete Member", command=delete_member)
    delete_member_button.pack(pady=5)

    # Borrowing Tab
    # Borrowing Tab
    borrowing_tree_columns = ("Borrow ID", "Book ID", "Member ID", "Borrow Date", "Return Date")
    borrowing_tree = ttk.Treeview(tabview.tab("Borrowing"), columns=borrowing_tree_columns, show="headings",
                                  selectmode="browse")
    borrowing_tree.pack(fill="both", expand=True)

    for col in borrowing_tree_columns:
        borrowing_tree.heading(col, text=col)

    setup_sorting(borrowing_tree, borrowing_tree_columns, numeric_columns={0})

    def refresh_borrowing_tree():
        """
        Refreshes the Borrowing tab to show only books that have not been returned.
        Color-coded rows:
        - Red: Overdue and not returned
        - Yellow: Due today
        - Green: Not yet due
        """
        borrowing_tree.delete(*borrowing_tree.get_children())  # Clear current data

        # Fetch borrowing data where actual_return_date is NULL
        db_cursor.execute("""
            SELECT borrow_id, book_id, member_id, borrow_date, planned_return_date 
            FROM Borrowing
            WHERE actual_return_date IS NULL
        """)
        borrowing_data = db_cursor.fetchall()

        current_date = datetime.now().date()

        for borrowing in borrowing_data:
            borrow_id, book_id, member_id, borrow_date, planned_return_date = borrowing

            # Determine the color for the row
            planned_return_date_obj = datetime.strptime(str(planned_return_date), "%Y-%m-%d").date()
            if current_date > planned_return_date_obj:  # Overdue
                tag = "overdue"
            elif current_date == planned_return_date_obj:  # Due today
                tag = "due_today"
            else:  # Not overdue
                tag = "not_due"

            # Insert the row into the treeview with the determined tag
            borrowing_tree.insert("", END, values=(borrow_id, book_id, member_id, borrow_date, planned_return_date),
                                  tags=(tag,))

        # Configure tags for color coding
        borrowing_tree.tag_configure("overdue", background="lightcoral", foreground="black")  # Red for overdue
        borrowing_tree.tag_configure("due_today", background="lightyellow", foreground="black")  # Yellow for today
        borrowing_tree.tag_configure("not_due", background="lightgreen", foreground="black")  # Green for future

    refresh_borrowing_tree()
    # Add explanatory label for colors
    explanation_label = Label(
        tabview.tab("Borrowing"),
        text="Color Codes:\n"
             "Green: Return date is in the future.\n"
             "Yellow: Return date is today.\n"
             "Red: Return date has passed, the book has not been returned.",
        font=("Arial", 10),
        justify="left",
        fg="black"
    )
    explanation_label.pack(pady=10, anchor="w")

    def open_add_borrowing_window():
        add_borrowing_window = Toplevel(main_app)
        add_borrowing_window.title("Add Borrowing Record")
        add_borrowing_window.geometry("450x550")
        add_borrowing_window.configure(bg="#f5f5f5")  # Background color

        # Fetch Book IDs and Member IDs for dropdowns
        db_cursor.execute("SELECT book_id FROM Books WHERE quantity > 0")
        available_books = [row[0] for row in db_cursor.fetchall()]

        db_cursor.execute("SELECT member_id FROM Members")
        available_members = [row[0] for row in db_cursor.fetchall()]

        # Book ID Dropdown
        book_id_label = Label(add_borrowing_window, text="Book ID", bg="#f5f5f5", font=("Arial", 12, "bold"))
        book_id_label.pack(pady=5)
        book_id_combo = ttk.Combobox(add_borrowing_window, values=available_books, state="readonly")
        book_id_combo.pack(pady=5)

        # Member ID Dropdown
        member_id_label = Label(add_borrowing_window, text="Member ID", bg="#f5f5f5", font=("Arial", 12, "bold"))
        member_id_label.pack(pady=5)
        member_id_combo = ttk.Combobox(add_borrowing_window, values=available_members, state="readonly")
        member_id_combo.pack(pady=5)

        # Borrow Date Calendar
        borrow_date_label = Label(add_borrowing_window, text="Borrow Date", bg="#f5f5f5", font=("Arial", 12, "bold"))
        borrow_date_label.pack(pady=5)
        borrow_date_calendar = Calendar(
            add_borrowing_window,
            date_pattern="yyyy-mm-dd",
            selectmode="day",
            background="#ffcccc",
            disabledbackground="#f5f5f5",
            bordercolor="#ff6666",
            headersbackground="#ff6666",
            headersforeground="white",
            foreground="black",
            weekendforeground="#ff6666",
            font=("Arial", 10)
        )
        borrow_date_calendar.pack(pady=10)

        # Planned Return Date Calendar
        return_date_label = Label(add_borrowing_window, text="Planned Return Date", bg="#f5f5f5",
                                  font=("Arial", 12, "bold"))
        return_date_label.pack(pady=5)
        return_date_calendar = Calendar(
            add_borrowing_window,
            date_pattern="yyyy-mm-dd",
            selectmode="day",
            background="#ccffcc",
            disabledbackground="#f5f5f5",
            bordercolor="#66ff66",
            headersbackground="#66ff66",
            headersforeground="white",
            foreground="black",
            weekendforeground="#66ff66",
            font=("Arial", 10)
        )
        return_date_calendar.pack(pady=10)

        # Add Borrowing Record Function
        def add_borrowing():
            book_id = book_id_combo.get()
            member_id = member_id_combo.get()
            borrow_date = borrow_date_calendar.get_date()
            planned_return_date = return_date_calendar.get_date()

            # Input validation
            if not book_id or not member_id or not borrow_date or not planned_return_date:
                messagebox.showwarning("Input Error", "Please fill all required fields.")
                return

            # Check book availability
            db_cursor.execute("SELECT quantity FROM Books WHERE book_id = %s", (book_id,))
            result = db_cursor.fetchone()

            if result is None or result[0] <= 0:
                messagebox.showwarning("Error", "Book is not available.")
                return

            try:
                # Get the next available borrow_id
                db_cursor.execute("SELECT MAX(borrow_id) FROM Borrowing")
                next_borrow_id = db_cursor.fetchone()[0]
                if next_borrow_id is None:
                    next_borrow_id = 1
                else:
                    next_borrow_id += 1

                # Insert borrowing record into the database
                db_cursor.execute("""
                    INSERT INTO Borrowing (borrow_id, book_id, member_id, borrow_date, planned_return_date, actual_return_date)
                    VALUES (%s, %s, %s, %s, %s, NULL)
                """, (next_borrow_id, book_id, member_id, borrow_date, planned_return_date))

                # Update book quantity
                db_cursor.execute("UPDATE Books SET quantity = quantity - 1 WHERE book_id = %s", (book_id,))
                db_connection.commit()

                # Refresh the Borrowing and Books trees
                refresh_tabs()

                messagebox.showinfo("Success", "Borrowing record added successfully!")
                add_borrowing_window.destroy()  # Close the Add Borrowing window
            except Exception as e:
                db_connection.rollback()  # Rollback changes in case of error
                messagebox.showerror("Error", f"An error occurred: {e}")

        # Add Borrow Button
        add_borrow_button = Button(add_borrowing_window, text="Add Borrow", command=add_borrowing, bg="lightblue",
                                   font=("Arial", 12, "bold"))
        add_borrow_button.pack(pady=20)

    def open_update_borrowing_window():
        selected_item = borrowing_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No borrowing record selected.")
            return

        borrowing_values = borrowing_tree.item(selected_item, 'values')
        borrow_id = borrowing_values[0]

        update_borrowing_window = Toplevel(main_app)
        update_borrowing_window.title("Update Borrowing")
        update_borrowing_window.geometry("400x300")

        # Planned Return Date Calendar
        Label(update_borrowing_window, text="Planned Return Date").pack(pady=5)
        return_date_calendar = Calendar(update_borrowing_window, date_pattern="yyyy-mm-dd", selectmode="day")
        return_date_calendar.pack(pady=10)

        def update_borrowing():
            planned_return_date = return_date_calendar.get_date()

            if not planned_return_date:
                messagebox.showwarning("Input Error", "Please select a return date.")
                return

            try:
                db_cursor.execute("""
                    UPDATE Borrowing
                    SET planned_return_date=%s
                    WHERE borrow_id=%s
                """, (planned_return_date, borrow_id))

                db_connection.commit()
                refresh_tabs()
                messagebox.showinfo("Success", "Borrowing record updated successfully!")
                update_borrowing_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

        update_borrowing_button = Button(update_borrowing_window, text="Update Borrowing", command=update_borrowing)
        update_borrowing_button.pack(pady=10)

    update_borrowing_button = Button(tabview.tab("Borrowing"), text="Update Borrowing",
                                     command=open_update_borrowing_window)
    update_borrowing_button.pack(pady=5)

    def delete_borrowing():
        selected_item = borrowing_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No borrowing record selected.")
            return

        borrow_id = borrowing_tree.item(selected_item, 'values')[0]
        db_cursor.execute("DELETE FROM Borrowing WHERE borrow_id = %s", (borrow_id,))
        db_connection.commit()
        refresh_tabs()
        messagebox.showinfo("Success", f"Borrowing record with ID {borrow_id} has been deleted.")

    def return_book():
        selected_item = borrowing_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No borrowing record selected.")
            return

        borrow_id = borrowing_tree.item(selected_item, 'values')[0]  # Seçili borrow_id'yi al
        db_cursor.execute("SELECT * FROM Borrowing WHERE borrow_id = %s", (borrow_id,))
        borrow_record = db_cursor.fetchone()

        if not borrow_record:
            messagebox.showerror("Error", "Borrowing record not found.")
            return

        try:
            # actual_return_date alanını güncelle
            db_cursor.execute("""
                UPDATE Borrowing SET actual_return_date = %s WHERE borrow_id = %s
            """, (date.today(), borrow_id))

            # Kitap stoğunu güncelle
            book_id = borrow_record[1]
            db_cursor.execute("UPDATE Books SET quantity = quantity + 1 WHERE book_id = %s", (book_id,))

            db_connection.commit()

            # UI'yi yenile
            refresh_tabs()

            messagebox.showinfo("Success", "Book returned successfully!")
        except Exception as e:
            db_connection.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")

    # Add Buttons to Borrowing Tab
    add_borrowing_button = Button(tabview.tab("Borrowing"), text="Add Borrowing", command=open_add_borrowing_window)
    add_borrowing_button.pack(pady=5)

    delete_borrowing_button = Button(tabview.tab("Borrowing"), text="Delete Borrowing", command=delete_borrowing)
    delete_borrowing_button.pack(pady=5)

    return_book_button = Button(tabview.tab("Borrowing"), text="Return Book", command=return_book)
    return_book_button.pack(pady=5)

    # Borrowing History Tab
    # Borrowing History Tab
    borrowing_history_tree_columns = (
        "Borrow ID", "Book ID", "Member ID", "Borrow Date", "Planned Return Date", "Actual Return Date", "Fine ($)")
    borrowing_history_tree = ttk.Treeview(
        tabview.tab("Borrowing History"),
        columns=borrowing_history_tree_columns,
        show="headings",
        selectmode="browse"
    )
    borrowing_history_tree.pack(fill="both", expand=True)

    for col in borrowing_history_tree_columns:
        borrowing_history_tree.heading(col, text=col)

    setup_sorting(borrowing_history_tree, borrowing_history_tree_columns, numeric_columns={0})

    def refresh_borrowing_history_tree():
        """
        Refreshes the Borrowing History tab with all records where actual_return_date is NOT NULL,
        and calculates the fine dynamically for late returns.
        """
        borrowing_history_tree.delete(*borrowing_history_tree.get_children())  # Clear current data

        # Fetch records with actual_return_date NOT NULL
        db_cursor.execute("""
            SELECT borrow_id, book_id, member_id, borrow_date, planned_return_date, actual_return_date
            FROM Borrowing
            WHERE actual_return_date IS NOT NULL
        """)
        borrowing_data = db_cursor.fetchall()

        for borrowing in borrowing_data:
            borrow_id, book_id, member_id, borrow_date, planned_return_date, actual_return_date = borrowing
            actual_return_date_obj = datetime.strptime(str(actual_return_date), "%Y-%m-%d").date()
            planned_return_date_obj = datetime.strptime(str(planned_return_date), "%Y-%m-%d").date()

            # Calculate fine if the book was returned late
            fine = 0
            if actual_return_date_obj > planned_return_date_obj:
                fine = (actual_return_date_obj - planned_return_date_obj).days  # $1 for each late day

            # Determine the color for late or on-time returns
            row_color = "red" if fine > 0 else "green"

            # Insert row into the treeview with the calculated fine
            borrowing_history_tree.insert(
                "",
                END,
                values=(borrow_id, book_id, member_id, borrow_date, planned_return_date, actual_return_date, fine),
                tags=(row_color,)
            )

        # Configure row colors based on tags
        borrowing_history_tree.tag_configure("green", background="lightgreen", foreground="black")
        borrowing_history_tree.tag_configure("red", background="lightcoral", foreground="black")

    # Add explanatory label for Borrowing History
    history_explanation_label = Label(
        tabview.tab("Borrowing History"),
        text="Color Codes:\n"
             "Green: Returned on or before the planned return date.\n"
             "Red: Returned late.\n"
             "Fine ($): Calculated dynamically as $1 per late day.",
        font=("Arial", 10),
        justify="left",
        fg="black"
    )
    history_explanation_label.pack(pady=10, anchor="w")


    refresh_borrowing_history_tree()

    def refresh_analytics_tab():
        """
        Refreshes the analytics tab with updated visualizations, divided into pages with navigation buttons.
        Each page contains two graphs side by side, with navigation buttons centered at the bottom.
        """
        # Clear the current content
        for widget in tabview.tab("Analytics").winfo_children():
            widget.destroy()

        # Fetch the data for all graphs
        db_cursor.execute("""
            SELECT genre, COUNT(*) AS borrow_count
            FROM Borrowing
            JOIN Books ON Borrowing.book_id = Books.book_id
            GROUP BY genre;
        """)
        genre_data = db_cursor.fetchall()

        db_cursor.execute("""
            SELECT Books.title, COUNT(*) AS borrow_count
            FROM Borrowing
            JOIN Books ON Borrowing.book_id = Books.book_id
            GROUP BY Books.title
            ORDER BY borrow_count DESC
            LIMIT 5;
        """)
        most_borrowed_data = db_cursor.fetchall()

        db_cursor.execute("""
            SELECT CONCAT(Members.first_name, ' ', Members.last_name) AS member_name, COUNT(*) AS borrow_count
            FROM Borrowing
            JOIN Members ON Borrowing.member_id = Members.member_id
            GROUP BY Members.member_id
            ORDER BY borrow_count DESC;
        """)
        member_borrow_data = db_cursor.fetchall()

        db_cursor.execute("""
            SELECT Books.genre, COUNT(*) AS borrow_count
            FROM Borrowing
            JOIN Books ON Borrowing.book_id = Books.book_id
            GROUP BY Books.genre
            ORDER BY borrow_count DESC;
        """)
        genre_borrow_data = db_cursor.fetchall()

        db_cursor.execute("""
            SELECT Books.language, COUNT(*) AS borrow_count
            FROM Borrowing
            JOIN Books ON Borrowing.book_id = Books.book_id
            GROUP BY Books.language
            ORDER BY borrow_count DESC;
        """)
        language_borrow_data = db_cursor.fetchall()

        db_cursor.execute("""
            SELECT YEAR(borrow_date) AS year, COUNT(*) AS borrow_count
            FROM Borrowing
            GROUP BY year
            ORDER BY year;
        """)
        yearly_borrow_data = db_cursor.fetchall()

        # Prepare the data for the pages
        pages = []

        # Create figures and group them into pages (two figures per page)
        figures = []

        if genre_data:
            genres, counts = zip(*genre_data)
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.pie(counts, labels=genres, autopct="%1.1f%%", startangle=90, textprops={'fontsize': 8})
            ax.set_title("Borrowed Book Statistics", fontsize=10)
            figures.append(fig)

        if most_borrowed_data:
            titles, borrow_counts = zip(*most_borrowed_data)
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.barh(titles, borrow_counts, color="lightblue" )
            ax.tick_params(axis='y', labelsize=5)
            ax.set_yticklabels(titles, rotation=45, ha='right', fontsize=6)  # Çapraz yazılar ve sağa hizalama
            ax.set_title("Top 5 Most Borrowed Books", fontsize=10)
            ax.invert_yaxis()
            figures.append(fig)

        if member_borrow_data:
            member_names, borrow_counts = zip(*member_borrow_data)
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.bar(member_names, borrow_counts, color="lightgreen")
            ax.set_title("Books Borrowed by Members", fontsize=10)
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            figures.append(fig)

        if genre_borrow_data:
            genres, borrow_counts = zip(*genre_borrow_data)
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.bar(genres, borrow_counts, color="orange")
            ax.set_title("Most Borrowed Genres", fontsize=10)
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            figures.append(fig)

        if language_borrow_data:
            languages, counts = zip(*language_borrow_data)
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.bar(languages, counts, color="purple")
            ax.set_title("Books Borrowed by Language", fontsize=10)
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            figures.append(fig)

        if yearly_borrow_data:
            years, counts = zip(*yearly_borrow_data)
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.plot(years, counts, marker='o', color="teal")
            ax.set_title("Yearly Borrowing Trend", fontsize=10)
            ax.set_xlabel("Year")
            ax.set_ylabel("Number of Borrows")
            ax.grid(True, linestyle='--', alpha=0.7)
            figures.append(fig)

        # Group figures into pages (two per page)
        for i in range(0, len(figures), 2):
            pages.append(figures[i:i + 2])

        # State for the current page
        current_page = [0]

        def show_page():
            for widget in tabview.tab("Analytics").winfo_children():
                widget.destroy()

            page = pages[current_page[0]]

            frame = Frame(tabview.tab("Analytics"))
            frame.pack(expand=True, fill="both")

            for fig in page:
                canvas = FigureCanvasTkAgg(fig, master=frame)
                widget = canvas.get_tk_widget()
                widget.pack(side="left", expand=True, fill="both", padx=10, pady=10)

            navigation_frame = Frame(tabview.tab("Analytics"))
            navigation_frame.pack(fill="x", side="bottom")

            prev_button = Button(navigation_frame, text="Previous", command=lambda: change_page(-1), bg="black",
                                 fg="black")
            next_button = Button(navigation_frame, text="Next", command=lambda: change_page(1), bg="black", fg="black")

            prev_button.pack(side="left", padx=20, pady=10)
            next_button.pack(side="right", padx=20, pady=10)

            if current_page[0] == 0:
                prev_button.config(state=DISABLED)
            if current_page[0] == len(pages) -1:
                next_button.config(state=DISABLED)

        def change_page(direction):
            current_page[0] += direction
            show_page()

        if pages:
            show_page()
        else:
            Label(tabview.tab("Analytics"), text="No data available for analytics.", font=("Arial", 12)).pack(pady=20)

    # Refresh the Analytics tab with the updated functionality
    refresh_analytics_tab()

    #Refreshes All Tabs
    def refresh_tabs():
        refresh_books_tree()
        refresh_members_tree()
        refresh_borrowing_tree()
        refresh_borrowing_history_tree()
        refresh_analytics_tab()

    main_app.mainloop()
def update_time_label(label):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    label.config(text=current_time)
    label.after(1000, lambda: update_time_label(label))  # Update every second


# Start the Application with Login
if __name__ == "__main__":
    login_screen()
