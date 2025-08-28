import sys
import numpy as np
import sqlite3
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QMessageBox, QInputDialog
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtGui import QFont
import json
import os
import subprocess
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer  
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime

def knowuser(activeuser):
    if activeuser:
        print(f"User yang aktif: {activeuser}")
        return activeuser
    else:
        print("Tidak ada user yang aktif")
        return None
    
class Trx(QMainWindow):
    def __init__(self, activeuser):
        super(Trx, self).__init__()
        loadUi("ui_files/inputtransaction.ui", self)
        self.activeuser = activeuser

        self.setup_database()
        self.create_tables()
        self.setup_category_system()

        #interaksi tombol di halaman
        self.addcategorybtn.clicked.connect(self.add_category_dialog)
        self.removecategorybtn.clicked.connect(self.remove_category_dialog)


    # FUNGSI FUNGSI DATABASE
    def setup_database(self):
        try:
            self.conn = sqlite3.connect('financedatabase.db')
            self.cursor = self.conn.cursor()
            print("Database connected successfully")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Gagal koneksi database: {e}")


    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             username TEXT NOT NULL,
             type TEXT NOT NULL,
             nominal REAL NOT NULL,
             category TEXT NOT NULL,
             date TEXT NOT NULL,
             startdate TEXT,
             enddate TEXT, 
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()

    def save_transaction(self):
        try:
            self.cursor.execute('''
                INSERT INTO transactions (username, type, nominal, category, date, startdate, enddate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.activeuser, self.type, self.nilai, self.category, 
                self.date, self.startdate, self.enddate
            ))
            self.conn.commit()
            print("Transaksi berhasil disimpan ke database")
            return True
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Gagal menyimpan transaksi: {e}")
            return False
        

    # FUNGSI CATEGORY MANAGEMENT
    def setup_category_system(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                category_name TEXT NOT NULL,
                UNIQUE(username, category_name)
            )
        ''')
        self.conn.commit()
        self.load_categories()

    def load_categories(self):
        try:
            self.cursor.execute(
                "SELECT category_name FROM categories WHERE username = ? ORDER BY category_name",
                (self.activeuser,)
            )
            categories = [row[0] for row in self.cursor.fetchall()]

            if "Others" not in categories:
                categories.append("Others")

            self.kategori.clear()
            self.kategori.addItems(categories)
            self.kategori.setCurrentText("Others")

        except sqlite3.Error as e:
            print(f"Error loading categories: {e}")

    def add_category_dialog(self):
        category_name, ok = QInputDialog.getText(
            self, 'Tambah Kategori', 'Masukkan kategori baru:'
        )
        
        if ok and category_name.strip():
            self.add_category(category_name.strip())

    def add_category(self, category_name):
            try:
                if not category_name or category_name == "Others":
                    QMessageBox.warning(self, "Error", "Nama Kategori tidak valid")
                    return
            
                self.cursor.execute(
                    "SELECT id FROM categories WHERE username = ? AND category_name = ?",
                    (self.activeuser, category_name)
                )

                if self.cursor.fetchone():
                    QMessageBox.warning(self, "Error", "Kategori sudah ada!")
                    return
            
                self.cursor.execute(
                    "INSERT INTO categories (username, category_name) VALUES (?, ?)",
                    (self.activeuser, category_name)
                )
                self.conn.commit()
                self.load_categories()
            
                QMessageBox.information(self, "Success", f"Kategori '{category_name}' berhasil ditambahkan!")
            
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"Gagal menambah kategori: {e}")

    
    def remove_category_dialog(self):
        current_category = self.kategori.currentText()

        if current_category == "Others":
            QMessageBox.warning(self, "Error", "Tidak dapat menghapus kategori 'Others'!")
            return
        
        reply = QMessageBox.question(
            self, 'Konfirmasi',
            f"Hapus kategori '{current_category}'? Semua transaksi akan diubah ke 'Others'",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.remove_category(current_category)

    def remove_category(self, category_name):
        try:
            self.cursor.execute('''
                UPDATE transactions SET category = 'Others' 
                WHERE username = ? AND category = ?
            ''', (self.activeuser, category_name))
            
            self.cursor.execute(
                "DELETE FROM categories WHERE username = ? AND category_name = ?",
                (self.activeuser, category_name)
            )
            
            self.conn.commit()
            self.load_categories()
            
            QMessageBox.information(
                self, "Success", 
                f"Kategori '{category_name}' dihapus. Transaksi diubah ke 'Others'."
            )
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Gagal menghapus kategori: {e}")


        # FUNGSI UTAMA UNTUK INPUT
    def knowinguser(self):
        try:
            # AMBIL INPUT DARI UI
            self.type = self.tipetransaksi.currentText()
            
            # Validasi nominal
            try:
                nominal_text = self.value.text().strip()
                if not nominal_text:
                    QMessageBox.warning(self, "Error", "Nominal tidak boleh kosong!")
                    return
                
                self.nilai = int(nominal_text)
                if self.nilai <= 0:
                    QMessageBox.warning(self, "Error", "Nominal harus lebih dari 0!")
                    return
                    
            except ValueError:
                QMessageBox.warning(self, "Error", "Nominal harus berupa angka!")
                return
            
            # Ambil category dari ComboBox
            self.category = self.categoryCombo.currentText()
            
            # Ambil tanggal utama
            inputdate = self.calendarWidget.selectedDate()
            self.date = inputdate.toString("yyyy-MM-dd")
            
            # Ambil startdate dan enddate (jika ada)
            self.startdate = None
            self.enddate = None
            
            # Jika ada calendar untuk start dan end date
            if hasattr(self, 'startcal'):
                start_date = self.startcal.selectedDate()
                if start_date.isValid():
                    self.startdate = start_date.toString("yyyy-MM-dd")
            
            if hasattr(self, 'endcal'):
                end_date = self.endcal.selectedDate()
                if end_date.isValid():
                    self.enddate = end_date.toString("yyyy-MM-dd")
            
            # KONDISI 1: Validasi field wajib
            if not all([self.type, self.nilai, self.date, self.category]):
                QMessageBox.warning(self, "Error", "Harap isi semua field yang wajib!")
                return
            
            # KONDISI 2 & 3: Validasi tanggal jika diisi
            if self.startdate and self.enddate:
                try:
                    start_dt = datetime.strptime(self.startdate, "%Y-%m-%d")
                    end_dt = datetime.strptime(self.enddate, "%Y-%m-%d")
                    
                    if end_dt < start_dt:
                        QMessageBox.warning(self, "Error", "End date harus setelah start date!")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Error", "Format tanggal tidak valid!")
                    return
            
            # SIMPAN KE DATABASE
            if self.save_transaction():
                QMessageBox.information(self, "Success", "Transaksi berhasil disimpan!")
                
                # Tampilkan di QLabel
                label_text = (
                    f"User: {self.activeuser}\n"
                    f"Type: {self.type}\n"
                    f"Nominal: Rp {self.nilai:,}\n"
                    f"Category: {self.category}\n"
                    f"Date: {self.date}"
                )
                
                if self.startdate:
                    label_text += f"\nStart: {self.startdate}"
                if self.enddate:
                    label_text += f"\nEnd: {self.enddate}"
                
                label = QLabel(label_text, self.otwusername)
                label.setStyleSheet("font-size: 12px; padding: 10px; background-color: #f0f0f0;")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan: {str(e)}")

    def close_database(self):
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except:
            pass

    def closeEvent(self, event):
        self.close_database()
        event.accept()


    #INI BISA ALHAMDULILLAHHHH