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
  passwd="ksu12345",
  auth_plugin='mysql_native_password'
)
print(db_connection)
db_cursor = db_connection.cursor(buffered=True)

# Helper Function: Populate Table from CSV
def populate_table(file_path, insert_query):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            db_cursor.execute(insert_query, row)
    db_connection.commit()



# Initialize Database
db_cursor.execute("DROP DATABASE IF EXISTS library")
db_cursor.execute("CREATE DATABASE IF NOT EXISTS library")
db_cursor.execute("USE library")

# Create Tables
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
db_cursor.execute("""
    CREATE TABLE Borrowing (
        borrow_id INT AUTO_INCREMENT PRIMARY KEY,
        book_id CHAR(6),
        member_id CHAR(6),
        borrow_date DATE,
        return_date DATE,
        FOREIGN KEY (book_id) REFERENCES Books(book_id),
        FOREIGN KEY (member_id) REFERENCES Members(member_id)
    )
""")

db_cursor.execute("""
    CREATE TABLE BorrowingHistory (
        borrow_id INT AUTO_INCREMENT PRIMARY KEY,
        book_id CHAR(6),
        member_id CHAR(6),
        borrow_date DATE,
        return_date DATE,
        FOREIGN KEY (book_id) REFERENCES Books(book_id),
        FOREIGN KEY (member_id) REFERENCES Members(member_id)
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
    INSERT INTO Borrowing (borrow_id, book_id, member_id, borrow_date, return_date)
    VALUES (%s, %s, %s, %s, %s)
"""

populate_table("./data/Borrowing.csv", insert_borrowing_query)

insert_borrowing_history_query = """
    INSERT INTO BorrowingHistory (borrow_id, book_id, member_id, borrow_date, return_date)
    VALUES (%s, %s, %s, %s, %s)
"""
populate_table("./data/BorrowingHistory.csv", insert_borrowing_history_query)

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

    # Books Tab
    books_tree_columns = (
    "Book ID", "Title", "Author", "Genre", "Year Published", "Quantity", "Language", "Page Number")
    books_tree = ttk.Treeview(tabview.tab("Books"), columns=books_tree_columns, show="headings", selectmode="browse")
    books_tree.pack(fill="both", expand=True)

    for col in books_tree_columns:
        books_tree.heading(col, text=col)

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
        refresh_books_tree()
        messagebox.showinfo("Success", f"Book with ID {book_id} has been deleted.")

    add_book_button = Button(tabview.tab("Books"), text="Add Book", command=open_add_book_window)
    add_book_button.pack(pady=5)

    delete_book_button = Button(tabview.tab("Books"), text="Delete Book", command=delete_book)
    delete_book_button.pack(pady=5)

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
    category_filter_button = Button(tabview.tab("Books"), text="Category Filter", command=open_category_filter_window)
    category_filter_button.pack(pady=5)

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
                column_name = "year_published" if sort_option == "Year Published" else "quantity"

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
    sort_button = Button(tabview.tab("Books"), text="Sort", command=open_sort_option_window)
    sort_button.pack(pady=5)

    ### Members Tab
    members_tree_columns = ("Member ID", "First Name", "Last Name", "Phone Number", "Email")
    members_tree = ttk.Treeview(tabview.tab("Members"), columns=members_tree_columns, show="headings", selectmode="browse")
    members_tree.pack(fill="both", expand=True)

    for col in members_tree_columns:
        members_tree.heading(col, text=col)

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

    def delete_member():
        selected_item = members_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No member selected.")
            return

        member_id = members_tree.item(selected_item, 'values')[0]
        db_cursor.execute("DELETE FROM Members WHERE member_id = %s", (member_id,))
        db_connection.commit()
        refresh_members_tree()
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

    def refresh_borrowing_tree():
        borrowing_tree.delete(*borrowing_tree.get_children())  # Clear current data

        # Fetch borrowing data from the database
        db_cursor.execute("SELECT borrow_id, book_id, member_id, borrow_date, return_date FROM Borrowing")
        borrowing_data = db_cursor.fetchall()

        for borrowing in borrowing_data:
            borrow_id, book_id, member_id, borrow_date, return_date = borrowing

            # Compare return_date with current date
            current_date = datetime.now().date()
            return_date_obj = datetime.strptime(str(return_date), "%Y-%m-%d").date()

            # Determine the color
            if return_date_obj > current_date:
                row_color = "green"  # Future return date
            elif return_date_obj == current_date:
                row_color = "yellow"  # Return date is today
            else:
                row_color = "red"  # Overdue return date

            # Insert row with a specific tag for color
            borrowing_tree.insert("", END, values=(borrow_id, book_id, member_id, borrow_date, return_date),
                                  tags=(row_color,))

        # Configure row colors based on tags
        borrowing_tree.tag_configure("green", background="lightgreen", foreground="black")
        borrowing_tree.tag_configure("yellow", background="lightyellow", foreground="black")
        borrowing_tree.tag_configure("red", background="lightcoral", foreground="black")

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
        add_borrowing_window.configure(bg="#f5f5f5")  # Arka plan rengi

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

        # Return Date Calendar
        return_date_label = Label(add_borrowing_window, text="Return Date", bg="#f5f5f5", font=("Arial", 12, "bold"))
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
            return_date = return_date_calendar.get_date()

            # Input validation
            if not book_id or not member_id or not borrow_date:
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
                db_cursor.execute(
                    "INSERT INTO Borrowing (borrow_id, book_id, member_id, borrow_date, return_date) VALUES (%s, %s, %s, %s, %s)",
                    (next_borrow_id, book_id, member_id, borrow_date, return_date)
                )
                # Update book quantity
                db_cursor.execute("UPDATE Books SET quantity = quantity - 1 WHERE book_id = %s", (book_id,))
                db_connection.commit()

                # Append the record to Borrowing.csv
                csv_file_path = "./data/Borrowing.csv"
                file_exists = os.path.isfile(csv_file_path)
                with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    if not file_exists:
                        writer.writerow(["borrow_id", "book_id", "member_id", "borrow_date", "return_date"])
                    writer.writerow([next_borrow_id, book_id, member_id, borrow_date, return_date])

                # Refresh the Borrowing and Books trees
                refresh_borrowing_tree()  # Refresh Borrowing tab
                refresh_books_tree()  # Refresh Books tab to update the quantity

                messagebox.showinfo("Success", "Borrowing record added successfully!")
                add_borrowing_window.destroy()  # Close the Add Borrowing window
            except Exception as e:
                db_connection.rollback()  # Rollback changes in case of error
                messagebox.showerror("Error", f"An error occurred: {e}")

        # Add Borrowing Button
        add_borrowing_button = Button(
            add_borrowing_window,
            text="Add Borrowing Record",
            command=add_borrowing,
            bg="#ff6666",
            fg="white",
            font=("Arial", 12, "bold")
        )
        add_borrowing_button.pack(pady=20)

    def delete_borrowing():
        selected_item = borrowing_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No borrowing record selected.")
            return

        borrow_id = borrowing_tree.item(selected_item, 'values')[0]
        db_cursor.execute("DELETE FROM Borrowing WHERE borrow_id = %s", (borrow_id,))
        db_connection.commit()
        refresh_borrowing_tree()
        messagebox.showinfo("Success", f"Borrowing record with ID {borrow_id} has been deleted.")

    def return_book():
        selected_item = borrowing_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No borrowing record selected.")
            return

        borrow_id = borrowing_tree.item(selected_item, 'values')[0]  # Get the selected borrow ID
        db_cursor.execute("SELECT * FROM Borrowing WHERE borrow_id = %s", (borrow_id,))
        borrow_record = db_cursor.fetchone()  # Set borrow_record as tuple borrowing tuple

        if not borrow_record:
            messagebox.showerror("Error", "Borrowing record not found.")
            return

        # Extract record details
        book_id, member_id, borrow_date, _ = borrow_record[1:]

        try:
            # Move record to BorrowingHistory with current date as return_date
            db_cursor.execute("""
                INSERT INTO BorrowingHistory (borrow_id, book_id, member_id, borrow_date, return_date)
                VALUES (%s, %s, %s, %s, %s)
            """, (borrow_id, book_id, member_id, borrow_date, date.today()))

            # Delete record from Borrowing
            db_cursor.execute("DELETE FROM Borrowing WHERE borrow_id = %s", (borrow_id,))

            # Update book quantity
            db_cursor.execute("""
                UPDATE Books SET quantity = quantity + 1 WHERE book_id = %s
            """, (book_id,))

            # Commit changes
            db_connection.commit()

            # Refresh UI
            refresh_borrowing_tree()  # Refresh Borrowing tab
            refresh_borrowing_history_tree()  # Refresh Borrowing History tab
            refresh_books_tree()  # Update book quantities in Books tab

            # Update BorrowingHistory CSV
            csv_file_path = "./data/BorrowingHistory.csv"
            file_exists = os.path.isfile(csv_file_path)
            with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(["borrow_id", "book_id", "member_id", "borrow_date", "return_date"])  # Write header
                writer.writerow([borrow_id, book_id, member_id, borrow_date, date.today()])  # Append new record

            messagebox.showinfo("Success", "Book returned successfully!")
        except Exception as e:
            db_connection.rollback()  # Rollback changes in case of error
            messagebox.showerror("Error", f"An error occurred: {e}")

    # Add Buttons to Borrowing Tab
    add_borrowing_button = Button(tabview.tab("Borrowing"), text="Add Borrowing", command=open_add_borrowing_window)
    add_borrowing_button.pack(pady=5)

    delete_borrowing_button = Button(tabview.tab("Borrowing"), text="Delete Borrowing", command=delete_borrowing)
    delete_borrowing_button.pack(pady=5)

    return_book_button = Button(tabview.tab("Borrowing"), text="Return Book", command=return_book)
    return_book_button.pack(pady=5)

    # Borrowing History Tab
    borrowing_history_tree_columns = ("Borrow ID", "Book ID", "Member ID", "Borrow Date", "Return Date")
    borrowing_history_tree = ttk.Treeview(tabview.tab("Borrowing History"),
                                          columns=borrowing_history_tree_columns,
                                          show="headings",
                                          selectmode="browse")
    borrowing_history_tree.pack(fill="both", expand=True)

    for col in borrowing_history_tree_columns:
        borrowing_history_tree.heading(col, text=col)

    def refresh_borrowing_history_tree():
        borrowing_history_tree.delete(*borrowing_history_tree.get_children())  # Clear current data
        db_cursor.execute("SELECT * FROM BorrowingHistory")
        for history in db_cursor.fetchall():
            borrowing_history_tree.insert("", END, values=history)

    refresh_borrowing_history_tree()
    ### Analytics Tab
    def refresh_analytics_tab():
        """
        Refreshes the analytics tab with four visualizations:
        1. Borrowed Book Statistics (Top-left, Pie Chart)
        2. Top 5 Most Borrowed Books (Top-right, Bar Chart)
        3. Books Borrowed by Members (Bottom-left, Bar Chart)
        4. Dummy Chart (Bottom-right, Pie Chart)
        """
        # Clear the current content
        for widget in tabview.tab("Analytics").winfo_children():
            widget.destroy()

        analytics_frame = Frame(tabview.tab("Analytics"))
        analytics_frame.pack(fill="both", expand=True)

        # Layout grid configuration
        analytics_frame.grid_rowconfigure(0, weight=1)
        analytics_frame.grid_rowconfigure(1, weight=1)
        analytics_frame.grid_columnconfigure(0, weight=1)
        analytics_frame.grid_columnconfigure(1, weight=1)

        ### Query 1: Borrowed Book Statistics ###
        db_cursor.execute("""
            SELECT genre, COUNT(*) AS count
            FROM BorrowingHistory
            INNER JOIN Books ON BorrowingHistory.book_id = Books.book_id
            GROUP BY genre
        """)
        genre_data = db_cursor.fetchall()

        if genre_data:
            genres, counts = zip(*genre_data)
            fig1, ax1 = plt.subplots(figsize=(4, 3))
            ax1.pie(counts, labels=genres, autopct="%1.1f%%", startangle=90)
            ax1.set_title("Borrowed Book Statistics", fontsize=10)

            canvas1 = FigureCanvasTkAgg(fig1, master=analytics_frame)
            canvas1.get_tk_widget().grid(row=0, column=0, padx=20, pady=20)

        ### Query 2: Top 5 Most Borrowed Books ###
        db_cursor.execute("""
            SELECT title, COUNT(*) AS count
            FROM BorrowingHistory
            INNER JOIN Books ON BorrowingHistory.book_id = Books.book_id
            GROUP BY title
            ORDER BY count DESC
            LIMIT 5
        """)
        top_books_data = db_cursor.fetchall()

        if top_books_data:
            titles, counts = zip(*top_books_data)
            fig2, ax2 = plt.subplots(figsize=(4, 3))
            ax2.barh(titles, counts, color="skyblue")
            ax2.set_xlabel("Number of Times Borrowed")
            ax2.set_title("Top 5 Most Borrowed Books", fontsize=10)
            ax2.invert_yaxis()

            canvas2 = FigureCanvasTkAgg(fig2, master=analytics_frame)
            canvas2.get_tk_widget().grid(row=0, column=1, padx=20, pady=20)

        ### Query 3: Books Borrowed by Members ###
        db_cursor.execute("""
            SELECT CONCAT(first_name, ' ', last_name) AS member_name, COUNT(*) AS count
            FROM BorrowingHistory
            INNER JOIN Members ON BorrowingHistory.member_id = Members.member_id
            GROUP BY member_name
            ORDER BY count DESC
            LIMIT 5
        """)
        members_data = db_cursor.fetchall()

        if members_data:
            member_names, borrow_counts = zip(*members_data)
            fig3, ax3 = plt.subplots(figsize=(4, 3))
            ax3.bar(member_names, borrow_counts, color="lightgreen")
            ax3.set_xlabel("Members")
            ax3.set_ylabel("Books Borrowed")
            ax3.set_title("Books Borrowed by Members", fontsize=10)

            canvas3 = FigureCanvasTkAgg(fig3, master=analytics_frame)
            canvas3.get_tk_widget().grid(row=1, column=0, padx=20, pady=20)

        ### Dummy Chart: Bottom-right ###
        labels = ["Category A", "Category B", "Category C"]
        sizes = [40, 30, 30]
        colors = ["gold", "lightcoral", "lightskyblue"]

        fig4, ax4 = plt.subplots(figsize=(4, 3))
        ax4.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors)
        ax4.set_title("Dummy Chart Example", fontsize=10)

        canvas4 = FigureCanvasTkAgg(fig4, master=analytics_frame)
        canvas4.get_tk_widget().grid(row=1, column=1, padx=20, pady=20)

    # Refresh Analytics when the tab is first loaded
    refresh_analytics_tab()

    main_app.mainloop()
def update_time_label(label):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    label.config(text=current_time)
    label.after(1000, lambda: update_time_label(label))  # Update every second


# Start the Application with Login
if __name__ == "__main__":
    login_screen()
