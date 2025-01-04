import customtkinter
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from tkinter import scrolledtext
from tkinter import ttk

# Imports for database
import mysql.connector
import csv
import pandas as pd

# Database connection
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Sultan9988",  # Replace with your MySQL password
    database="library_management",
    auth_plugin='mysql_native_password'
)
db_cursor = db_connection.cursor(buffered=True)

# UI setup
customtkinter.set_appearance_mode("Light")
customtkinter.set_default_color_theme("blue")

# Main application
main_app = customtkinter.CTk()
main_app.title("Library Management System")
main_app.geometry("1200x700+70+0")
main_app.resizable(width=None, height=None)

def initialize_database():
    db_cursor.execute("DROP DATABASE IF EXISTS library_management")
    db_cursor.execute("CREATE DATABASE library_management")
    db_cursor.execute("USE library_management")

    # Create Books table
    db_cursor.execute("""
        CREATE TABLE Books (
            book_id CHAR(6) PRIMARY KEY,
            title VARCHAR(100),
            author_id CHAR(6),
            category VARCHAR(50),
            available INT
        )
    """)

    # Create Authors table
    db_cursor.execute("""
        CREATE TABLE Authors (
            author_id CHAR(6) PRIMARY KEY,
            name VARCHAR(100)
        )
    """)

    # Create Members table
    db_cursor.execute("""
        CREATE TABLE Members (
            member_id CHAR(6) PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            phone_number VARCHAR(15)
        )
    """)

    # Create BorrowRecords table
    db_cursor.execute("""
        CREATE TABLE BorrowRecords (
            record_id CHAR(6) PRIMARY KEY,
            member_id CHAR(6),
            book_id CHAR(6),
            borrow_date DATE,
            return_date DATE,
            FOREIGN KEY (member_id) REFERENCES Members(member_id),
            FOREIGN KEY (book_id) REFERENCES Books(book_id)
        )
    """)

    db_connection.commit()

# Login window
def login_window():
    login_win = customtkinter.CTkToplevel(main_app)
    login_win.title("Login")
    login_win.geometry("500x300+500+300")
    main_app.withdraw()

    frame = customtkinter.CTkFrame(master=login_win)
    frame.pack(pady=20, padx=40, fill="both", expand=True)

    db_cursor.execute("SELECT member_id FROM Members")
    member_ids = [row[0] for row in db_cursor.fetchall()]

    member_id_combobox = ttk.Combobox(master=frame, values=member_ids, state="readonly", width=30)
    member_id_combobox.set("Member ID")
    member_id_combobox.pack(pady=12, padx=120)

    password_entry = customtkinter.CTkEntry(master=frame, placeholder_text="Password", show="*", width=180)
    password_entry.pack(pady=12, padx=10)

    def login():
        member_id = member_id_combobox.get()
        password = password_entry.get()

        db_cursor.execute("SELECT name FROM Members WHERE member_id = %s", (member_id,))
        member_name = db_cursor.fetchone()

        if member_name:
            main_app.deiconify()
            login_win.destroy()
        else:
            messagebox.showwarning("Login Error", "Invalid Member ID or Password")

    login_button = customtkinter.CTkButton(master=frame, text="Login", command=login)
    login_button.pack(pady=12, padx=10)

# Tabview setup
tabview = customtkinter.CTkTabview(master=main_app)
tabview.pack(pady=20, padx=20, fill="both", expand=True)

# Add tabs
tabs = ["Books", "Members", "Borrow Records"]
for tab_name in tabs:
    tabview.add(tab_name)

tabview.set("Books")

# Books Tab
books_label = customtkinter.CTkLabel(
    master=tabview.tab("Books"),
    text="BOOKS",
    font=("Courier", 30, "bold")
)
books_label.pack(pady=10, padx=10)

books_columns = ("Book ID", "Title", "Author ID", "Category", "Available")
books_tree = ttk.Treeview(master=tabview.tab("Books"), columns=books_columns, show="headings")
books_tree.pack(padx=10, pady=10)

for col in books_columns:
    books_tree.heading(col, text=col)

# Fetch and display books
def fetch_books():
    books_tree.delete(*books_tree.get_children())
    db_cursor.execute("SELECT * FROM Books")
    for row in db_cursor.fetchall():
        books_tree.insert("", END, values=row)

fetch_books()

# Add book function
def add_book():
    book_id = book_id_input.get()
    title = book_title_input.get()
    author_id = book_author_id_input.get()
    category = book_category_input.get()
    available = book_available_input.get()

    if not all([book_id, title, author_id, category, available]):
        messagebox.showwarning("Validation Error", "Please fill in all fields.")
        return

    db_cursor.execute("INSERT INTO Books (book_id, title, author_id, category, available) VALUES (%s, %s, %s, %s, %s)",
                      (book_id, title, author_id, category, available))
    db_connection.commit()
    fetch_books()

book_id_input = customtkinter.CTkEntry(tabview.tab("Books"), placeholder_text="Book ID")
book_title_input = customtkinter.CTkEntry(tabview.tab("Books"), placeholder_text="Title")
book_author_id_input = customtkinter.CTkEntry(tabview.tab("Books"), placeholder_text="Author ID")
book_category_input = customtkinter.CTkEntry(tabview.tab("Books"), placeholder_text="Category")
book_available_input = customtkinter.CTkEntry(tabview.tab("Books"), placeholder_text="Available Copies")

book_id_input.place(x=50, y=300)
book_title_input.place(x=200, y=300)
book_author_id_input.place(x=350, y=300)
book_category_input.place(x=500, y=300)
book_available_input.place(x=650, y=300)

add_book_button = customtkinter.CTkButton(tabview.tab("Books"), text="Add Book", command=add_book)
add_book_button.place(x=800, y=300)

# Members Tab
members_label = customtkinter.CTkLabel(
    master=tabview.tab("Members"),
    text="MEMBERS",
    font=("Courier", 30, "bold")
)
members_label.pack(pady=10, padx=10)

members_columns = ("Member ID", "Name", "Email", "Phone Number")
members_tree = ttk.Treeview(master=tabview.tab("Members"), columns=members_columns, show="headings")
members_tree.pack(padx=10, pady=10)

for col in members_columns:
    members_tree.heading(col, text=col)

# Fetch and display members
def fetch_members():
    members_tree.delete(*members_tree.get_children())
    db_cursor.execute("SELECT * FROM Members")
    for row in db_cursor.fetchall():
        members_tree.insert("", END, values=row)

fetch_members()

# Borrow Records Tab
records_label = customtkinter.CTkLabel(
    master=tabview.tab("Borrow Records"),
    text="BORROW RECORDS",
    font=("Courier", 30, "bold")
)
records_label.pack(pady=10, padx=10)

records_columns = ("Record ID", "Member ID", "Book ID", "Borrow Date", "Return Date")
records_tree = ttk.Treeview(master=tabview.tab("Borrow Records"), columns=records_columns, show="headings")
records_tree.pack(padx=10, pady=10)

for col in records_columns:
    records_tree.heading(col, text=col)

# Fetch and display records
def fetch_records():
    records_tree.delete(*records_tree.get_children())
    db_cursor.execute("SELECT * FROM BorrowRecords")
    for row in db_cursor.fetchall():
        records_tree.insert("", END, values=row)

fetch_records()

# Add record function
def add_record():
    record_id = record_id_input.get()
    member_id = record_member_id_input.get()
    book_id = record_book_id_input.get()
    borrow_date = record_borrow_date_input.get()
    return_date = record_return_date_input.get()

    if not all([record_id, member_id, book_id, borrow_date]):
        messagebox.showwarning("Validation Error", "Please fill in all required fields.")
        return

    db_cursor.execute("INSERT INTO BorrowRecords (record_id, member_id, book_id, borrow_date, return_date) VALUES (%s, %s, %s, %s, %s)",
                      (record_id, member_id, book_id, borrow_date, return_date))
    db_cursor.execute("UPDATE Books SET available = available - 1 WHERE book_id = %s", (book_id,))
    db_connection.commit()
    fetch_records()

record_id_input = customtkinter.CTkEntry(tabview.tab("Borrow Records"), placeholder_text="Record ID")
record_member_id_input = customtkinter.CTkEntry(tabview.tab("Borrow Records"), placeholder_text="Member ID")
record_book_id_input = customtkinter.CTkEntry(tabview.tab("Borrow Records"), placeholder_text="Book ID")
record_borrow_date_input = customtkinter.CTkEntry(tabview.tab("Borrow Records"), placeholder_text="Borrow Date (YYYY-MM-DD)")
record_return_date_input = customtkinter.CTkEntry(tabview.tab("Borrow Records"), placeholder_text="Return Date (YYYY-MM-DD)")

record_id_input.place(x=50, y=300)
record_member_id_input.place(x=200, y=300)
record_book_id_input.place(x=350, y=300)
record_borrow_date_input.place(x=500, y=300)
record_return_date_input.place(x=650, y=300)

add_record_button = customtkinter.CTkButton(tabview.tab("Borrow Records"), text="Add Record", command=add_record)
add_record_button.place(x=800, y=300)

# Start application
initialize_database()
login_window()
main_app.mainloop()
