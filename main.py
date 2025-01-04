# Imports for UI
import customtkinter
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

# Imports for database
import mysql.connector
import csv

# Database Connection
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Sultan9988",
    auth_plugin='mysql_native_password'
)
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
    CREATE TABLE Books (
        book_id CHAR(6) PRIMARY KEY,
        title VARCHAR(100),
        author VARCHAR(50),
        genre VARCHAR(30),
        year_published INT,
        quantity INT
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

# Insert Data
insert_books_query = """
    INSERT INTO Books (book_id, title, author, genre, year_published, quantity)
    VALUES (%s, %s, %s, %s, %s, %s)
"""
populate_table("./data/Books.csv", insert_books_query)

insert_members_query = """
    INSERT INTO Members (member_id, first_name, last_name, phone_number, email)
    VALUES (%s, %s, %s, %s, %s)
"""
populate_table("./data/Members.csv", insert_members_query)

# Initialize GUI
customtkinter.set_appearance_mode("Light")
main_app = customtkinter.CTk()
main_app.title("Library Management System")
main_app.geometry("1200x700+70+0")
main_app.resizable(False, False)

# Tabview Setup
tabview = customtkinter.CTkTabview(master=main_app)
tabview.pack(pady=20, padx=20, fill="both", expand=True)

# Define Tabs
tabs = ["Books", "Members", "Borrowing"]
for tab in tabs:
    tabview.add(tab)
tabview.set("Books")

### Books Tab
books_tree_columns = ("Book ID", "Title", "Author", "Genre", "Year Published", "Quantity")
books_tree = ttk.Treeview(tabview.tab("Books"), columns=books_tree_columns, show="headings", selectmode="browse")
books_tree.pack(fill="both", expand=True)

for col in books_tree_columns:
    books_tree.heading(col, text=col)

def refresh_books_tree():
    books_tree.delete(*books_tree.get_children())  # Clear current data
    db_cursor.execute("SELECT * FROM Books")
    for book in db_cursor.fetchall():
        books_tree.insert("", END, values=book)

refresh_books_tree()

def open_add_book_window():
    add_book_window = Toplevel(main_app)
    add_book_window.title("Add Book")
    add_book_window.geometry("400x400")

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

    def add_book():
        book_id = book_id_entry.get()
        title = title_entry.get()
        author = author_entry.get()
        genre = genre_entry.get()
        year_published = year_entry.get()
        quantity = quantity_entry.get()

        if not all([book_id, title, author, genre, year_published, quantity]):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        db_cursor.execute(insert_books_query, (book_id, title, author, genre, int(year_published), int(quantity)))
        db_connection.commit()
        refresh_books_tree()
        messagebox.showinfo("Success", "Book added successfully!")
        add_book_window.destroy()

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
    members_tree.delete(*members_tree.get_children())  # Clear current data
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
borrowing_tree_columns = ("Borrow ID", "Book ID", "Member ID", "Borrow Date", "Return Date")
borrowing_tree = ttk.Treeview(tabview.tab("Borrowing"), columns=borrowing_tree_columns, show="headings", selectmode="browse")
borrowing_tree.pack(fill="both", expand=True)

for col in borrowing_tree_columns:
    borrowing_tree.heading(col, text=col)

db_cursor.execute("SELECT * FROM Borrowing")
for borrow in db_cursor.fetchall():
    borrowing_tree.insert("", END, values=borrow)

# Start the Application
main_app.mainloop()