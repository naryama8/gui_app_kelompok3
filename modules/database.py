
# File: database.py

import sqlite3
from sqlite3 import Error

def create_connection(db_file="financedatabase.db"):
    """ Membuat koneksi ke database SQLite """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """ Membuat tabel dari statement SQL """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def initialize_database():
    """ Fungsi utama untuk inisialisasi database dan tabel """
    database = "financedatabase.db"

    # SQL statement untuk membuat tabel users jika belum ada
    # Menambahkan kolom savings_target dan current_savings
    sql_create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        savings_target REAL DEFAULT 0.0,
        current_savings REAL DEFAULT 0.0
    );
    """

    # Membuat koneksi database
    conn = create_connection(database)

    # Membuat tabel
    if conn is not None:
        create_table(conn, sql_create_users_table)
        print("Database dan tabel 'users' siap digunakan.")
        conn.close()
    else:
        print("Error! Tidak dapat membuat koneksi database.")

if __name__ == '__main__':
    initialize_database()
