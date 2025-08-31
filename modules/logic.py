
# File: logic.py

import sqlite3
import json
from database import create_connection

def sync_users_from_json():
    """
    Menyinkronkan pengguna dari accounts.json ke database SQLite.
    Fungsi ini menambahkan pengguna jika belum ada di database.
    """
    try:
        with open('accounts.json', 'r') as f:
            accounts = json.load(f)
        
        conn = create_connection()
        if conn is None:
            return

        cursor = conn.cursor()
        for username, password in accounts.items():
            # Periksa apakah pengguna sudah ada
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone() is None:
                # Jika tidak ada, masukkan pengguna baru
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                print(f"Pengguna '{username}' ditambahkan ke database.")
        
        conn.commit()
        conn.close()
    except FileNotFoundError:
        print("File accounts.json tidak ditemukan.")
    except Exception as e:
        print(f"Terjadi error saat sinkronisasi: {e}")

def get_user_data(username):
    """ Mengambil data target dan tabungan dari database untuk pengguna tertentu """
    conn = create_connection()
    if conn is None:
        return {'target': 0.0, 'savings': 0.0}

    cursor = conn.cursor()
    cursor.execute("SELECT savings_target, current_savings FROM users WHERE username = ?", (username,))
    data = cursor.fetchone()
    conn.close()

    if data:
        return {'target': data[0], 'savings': data[1]}
    else:
        # Jika pengguna tidak ditemukan di db (kasus jarang), kembalikan default
        return {'target': 0.0, 'savings': 0.0}

def update_user_target(username, new_target):
    """ Memperbarui target tabungan untuk pengguna tertentu di database """
    sql = "UPDATE users SET savings_target = ? WHERE username = ?"
    conn = create_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    cursor.execute(sql, (new_target, username))
    conn.commit()
    conn.close()
    print(f"Target untuk '{username}' diperbarui menjadi {new_target}.")

def update_user_savings(username, new_savings_total):
    """ Memperbarui total tabungan untuk pengguna tertentu di database """
    sql = "UPDATE users SET current_savings = ? WHERE username = ?"
    conn = create_connection()
    if conn is None:
        return
        
    cursor = conn.cursor()
    cursor.execute(sql, (new_savings_total, username))
    conn.commit()
    conn.close()
    print(f"Total tabungan untuk '{username}' diperbarui menjadi {new_savings_total}.")
