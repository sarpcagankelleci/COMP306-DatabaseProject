# Imports for UI
import os

import customtkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import date

# Imports for database
import mysql.connector
import csv

# Database Connection
db_connection = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="faruk123",
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

    # Tabview Setup
    tabview = customtkinter.CTkTabview(master=main_app)
    tabview.pack(pady=10, padx=10, fill="both", expand=True)

    # Define Tabs
    tabs = ["Books", "Members", "Borrowing", "Borrowing History"]
    for tab in tabs:
        tabview.add(tab)
    tabview.set("Books")

    ### Books Tab
    books_tree_columns = ("Book ID", "Title", "Author", "Genre", "Year Published", "Quantity", "Language", "Page Number")
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
        db_cursor.execute("SELECT * FROM Borrowing")
        for borrow in db_cursor.fetchall():
            borrowing_tree.insert("", END, values=borrow)

    refresh_borrowing_tree()

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

            if not book_id or not member_id or not borrow_date:
                messagebox.showwarning("Input Error", "Please fill all required fields.")
                return

            # Check if the book exists and has a positive quantity
            db_cursor.execute("SELECT quantity FROM Books WHERE book_id = %s", (book_id,))
            result = db_cursor.fetchone()

            if result is None:
                messagebox.showerror("Error", "Book not found.")
                return

            quantity = result[0]

            if quantity <= 0:
                messagebox.showwarning("Out of Stock", "The selected book is out of stock.")
                return

            try:
                # Insert borrowing record
                db_cursor.execute(
                    "INSERT INTO Borrowing (book_id, member_id, borrow_date, return_date) VALUES (%s, %s, %s, %s)",
                    (book_id, member_id, borrow_date, return_date)
                )

                # Update book quantity
                db_cursor.execute(
                    "UPDATE Books SET quantity = quantity - 1 WHERE book_id = %s AND quantity > 0",
                    (book_id,)
                )

                # Commit changes
                db_connection.commit()

                # Refresh borrowing tree
                refresh_borrowing_tree()
                refresh_books_tree()  # Books ekranını da güncelle

                messagebox.showinfo("Success", "Borrowing record added successfully!")
                add_borrowing_window.destroy()
            except Exception as e:
                db_connection.rollback()
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
        borrow_record = db_cursor.fetchone() # Set borrow_record as tuple borrowing tuple

        if not borrow_record:
            messagebox.showerror("Error", "Borrowing record not found.")
            return

        book_id, member_id, borrow_date, _ = borrow_record[1:]  # Extract record details

        # Move record to BorrowingHistory with current date as return_date
        db_cursor.execute("""
            INSERT INTO BorrowingHistory (book_id, member_id, borrow_date, return_date)
            VALUES (%s, %s, %s, %s)
        """, (book_id, member_id, borrow_date, date.today()))

        # Delete record from Borrowing
        db_cursor.execute("DELETE FROM Borrowing WHERE borrow_id = %s", (borrow_id,))

        # Update book quantity
        db_cursor.execute("""
            UPDATE Books SET quantity = quantity + 1 WHERE book_id = %s
        """, (book_id,))

        # Commit changes
        db_connection.commit()
        refresh_borrowing_tree()  # Refresh Borrowing tab
        refresh_borrowing_history_tree()  # Refresh Borrowing History tab
        refresh_books_tree()  # Update book quantities in Books tab

        messagebox.showinfo("Success", "Book returned successfully!")

    add_borrowing_button = Button(tabview.tab("Borrowing"), text="Add Borrowing", command=open_add_borrowing_window)
    add_borrowing_button.pack(pady=5)

    delete_borrowing_button = Button(tabview.tab("Borrowing"), text="Delete Borrowing", command=delete_borrowing)
    delete_borrowing_button.pack(pady=5)

    return_book_button = Button(tabview.tab("Borrowing"), text="Return Book", command=return_book)
    return_book_button.pack(pady=5)

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

    main_app.mainloop()

# Start the Application with Login
if __name__ == "__main__":
    login_screen()
