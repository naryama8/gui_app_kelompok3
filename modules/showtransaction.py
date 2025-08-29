import sys
import numpy as np
import sqlite3
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QMessageBox, QInputDialog, QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtGui import QFont
import json
import os
import subprocess
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, Qt  
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
    
class Listtrx(QMainWindow):
    def __init__(self, activeuser):
        super(Listtrx,self).__init__()
        loadUi("ui_files/showtransaction.ui", self)
        self.activeuser=activeuser

        self.showdata()

        self.removebtn.clicked.connect(self.removetrx)

    def showdata(self):
        try:
            conn = sqlite3.connect('financedatabase.db')
            cursor = conn.cursor()

            #buat bangun query
            if self.activeuser:
                query = """
                SELECT id, type, nominal, category, date
                FROM transactions
                WHERE username = ?
                ORDER BY date DESC
                """
                cursor.execute(query, (self.activeuser,))

            data = cursor.fetchall()

            self.tabeltrx.setColumnCount(5)
            self.tabeltrx.setHorizontalHeaderLabels(
            ["ID", "Type", "Nominal", "Category", "Date"])

            self.tabeltrx.setRowCount(len(data))

            #buat bangun tabelnya
            for row_index, row_data in enumerate(data):
                for col_index, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tabeltrx.setItem(row_index, col_index, item)
                    
            self.tabeltrx.resizeColumnsToContents()

            conn.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Gagal koneksi database: {e}")



    def removetrx(self): #fungsi removing isi list
        otwremove_row = self.tabeltrx.currentRow()
        if otwremove_row < 0:
            QMessageBox.warning(self, "Warning", "Pilih transaksi yang mau dihapus!")
            return
        
        id_otwhapus = self.tabeltrx.item(otwremove_row, 0).text()

        confirm = QMessageBox.question(
            self,
            "Konfirmasi",
            "Hapus transaksi?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                conn = sqlite3.connect("financedatabase.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions WHERE id = ?", (id_otwhapus,))
                conn.commit()
                conn.close()

                self.tabeltrx.removeRow(otwremove_row)

                QMessageBox.information(self, "Hapus Transaksi", "Transaksi berhasil dihapus!")

            except Exception as e:
                QMessageBox.critical(self, "Error", "Data gagal dihapus")