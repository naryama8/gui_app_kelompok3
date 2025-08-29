import sys
import os
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QDate, Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime, timedelta
import random
import sqlite3
import rsc_rc

class TransactionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        try:
            uic.loadUi('transaction otak atik.ui', self)
        except FileNotFoundError:
            QMessageBox.critical(None, "Error", "File transaction.ui tidak ditemukan!")
            sys.exit(1)
        
        # Inisialisasi database
        self.init_database()
        
        # Load data dari database
        self.transactions = self.load_transactions()
        
        self.setup_chart()
        self.pushButton.clicked.connect(self.add_transaction_dialog)
        self.setup_table()
        self.update_display()
        
        # Jika tidak ada data, generate sample data
        if not self.transactions:
            self.generate_sample_data()

    def init_database(self):
        """Initialize database dan buat tabel jika belum ada"""
        self.conn = sqlite3.connect('transactions.db')
        self.cursor = self.conn.cursor()
        
        # Buat tabel transactions jika belum ada
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                description TEXT
            )
        ''')
        self.conn.commit()

    def load_transactions(self):
        """Load semua transaksi dari database"""
        self.cursor.execute("SELECT date, amount, type, description FROM transactions ORDER BY date DESC")
        rows = self.cursor.fetchall()
        
        transactions = []
        for row in rows:
            transactions.append({
                "date": row[0],
                "amount": row[1],
                "type": row[2],
                "description": row[3]
            })
        
        return transactions

    def save_transaction(self, transaction):
        """Simpan transaksi baru ke database"""
        self.cursor.execute(
            "INSERT INTO transactions (date, amount, type, description) VALUES (?, ?, ?, ?)",
            (transaction["date"], transaction["amount"], transaction["type"], transaction["description"])
        )
        self.conn.commit()
        
        # Dapatkan ID terakhir yang dimasukkan
        last_id = self.cursor.lastrowid
        return last_id

    def delete_transaction(self, index):
        """Hapus transaksi dari database berdasarkan index"""
        if 0 <= index < len(self.transactions):
            # Dapatkan data transaksi yang akan dihapus
            transaction = self.transactions[index]
            
            # Hapus dari database
            self.cursor.execute(
                "DELETE FROM transactions WHERE date = ? AND amount = ? AND type = ? AND description = ?",
                (transaction["date"], transaction["amount"], transaction["type"], transaction["description"])
            )
            self.conn.commit()
            
            # Hapus dari list
            del self.transactions[index]
            return True
        return False

    def setup_chart(self):
        """Setup matplotlib chart di QGraphicsView"""
        
        self.figure = Figure(figsize=(3, 4))
        self.canvas = FigureCanvas(self.figure)
        self.graphicsView.setScene(QtWidgets.QGraphicsScene())
        self.graphicsView.scene().addWidget(self.canvas)
        
    def setup_table(self):
        """Setup table widget"""

        headers = ["Date", "Amount", "Type", "Description", "Actions"]
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 100)
        self.tableWidget.setColumnWidth(2, 80)
        self.tableWidget.setColumnWidth(3, 200)
        self.tableWidget.setColumnWidth(4, 100)

    def generate_sample_data(self):
        """Generate sample transaction data untuk demo"""
        sample_transactions = [
            {"date": "2024-01-15", "amount": 5000000, "type": "Income", "description": "Gaji Bulanan"},
            {"date": "2024-01-16", "amount": -500000, "type": "Expense", "description": "Belanja Groceries"},
            {"date": "2024-01-20", "amount": -200000, "type": "Expense", "description": "Bensin Motor"},
            {"date": "2024-01-25", "amount": 1000000, "type": "Income", "description": "Freelance Project"},
            {"date": "2024-02-01", "amount": -1500000, "type": "Expense", "description": "Bayar Kost"},
            {"date": "2024-02-05", "amount": -300000, "type": "Expense", "description": "Makan di Resto"},
            {"date": "2024-02-10", "amount": 2000000, "type": "Income", "description": "Bonus Kerja"},
            {"date": "2024-02-15", "amount": -800000, "type": "Expense", "description": "Belanja Online"},
        ]
        
        for trans in sample_transactions:
            self.save_transaction(trans)
            self.transactions.append(trans)
        
        self.update_display()

    def add_transaction_dialog(self):
        """Dialog untuk menambah transaksi baru"""
        dialog = AddTransactionDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            transaction = dialog.get_transaction()
            if transaction:  # Pastikan transaction tidak None
                # Simpan ke database
                self.save_transaction(transaction)
                # Tambahkan ke list
                self.transactions.append(transaction)
                self.update_display()

    def delete_selected_transaction(self, row):
        """Hapus transaksi yang dipilih"""
        reply = QMessageBox.question(self, 'Konfirmasi', 
                                    'Apakah Anda yakin ingin menghapus transaksi ini?',
                                    QMessageBox.Yes | QMessageBox.No, 
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.delete_transaction(row):
                self.update_display()
                QMessageBox.information(self, "Sukses", "Transaksi berhasil dihapus!")
            else:
                QMessageBox.warning(self, "Error", "Gagal menghapus transaksi!")

    def update_display(self):
        """Update semua display (labels, table, chart)"""
        self.update_summary_labels()
        self.update_table()
        self.update_chart()

    def update_summary_labels(self):
        """Update label summary dengan data terbaru menggunakan numpy"""
        if not self.transactions:
            return
        
        amounts = np.array([t["amount"] for t in self.transactions])
        total_income = np.sum(amounts[amounts > 0])
        total_expense = abs(np.sum(amounts[amounts < 0]))
        balance = total_income - total_expense
        monthly_income = []
        monthly_expense = []
        
        for trans in self.transactions:
            month = trans["date"][:7] 
            if trans["amount"] > 0:
                monthly_income.append((month, trans["amount"]))
            else:
                monthly_expense.append((month, abs(trans["amount"])))
        
        if monthly_income:
            avg_monthly_income = np.mean([amt for _, amt in monthly_income])
        else:
            avg_monthly_income = 0
            
        if monthly_expense:
            avg_monthly_expense = np.mean([amt for _, amt in monthly_expense])
        else:
            avg_monthly_expense = 0
    
        self.label.setText(f"Rp {balance:,.0f}")
        self.label_2.setText(f"Rp {total_income:,.0f}")
        self.label_3.setText(f"Rp {total_expense:,.0f}")
        self.label_4.setText(f"Rp {avg_monthly_income:,.0f}")
        self.label_5.setText(f"Rp {avg_monthly_expense:,.0f}")

    def update_table(self):
        """Update table dengan data transaksi"""
        self.tableWidget.setRowCount(len(self.transactions))
        
        for row, trans in enumerate(self.transactions):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(trans["date"]))
            amount_text = f"Rp {abs(trans['amount']):,.0f}"
            if trans["amount"] < 0:
                amount_text = f"-{amount_text}"
            self.tableWidget.setItem(row, 1, QTableWidgetItem(amount_text))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(trans["type"]))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(trans["description"]))
            
            # Tambahkan tombol hapus
            delete_button = QtWidgets.QPushButton("Hapus")
            delete_button.clicked.connect(lambda checked, r=row: self.delete_selected_transaction(r))
            self.tableWidget.setCellWidget(row, 4, delete_button)

    def update_chart(self):
        """Update chart menggunakan matplotlib dan numpy"""
        self.figure.clear()
        
        if not self.transactions:
            return
        
        amounts = np.array([t["amount"] for t in self.transactions])
        income_amounts = amounts[amounts > 0]
        expense_amounts = abs(amounts[amounts < 0])
        
        # Set background color untuk figure dan canvas
        self.figure.patch.set_facecolor('#dddbe9')
        self.canvas.setStyleSheet("background-color: #dddbe9;")
        
        ax = self.figure.add_subplot(111)
        
        # Set background color untuk axes/plot area
        ax.set_facecolor('#dddbe9')
        
        if len(income_amounts) > 0 and len(expense_amounts) > 0:
            labels = ['Income', 'Expense']
            sizes = [np.sum(income_amounts), np.sum(expense_amounts)]
            colors = ['#2ecc71', '#e74c3c']
            
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.set_title('Income vs Expense', fontsize=10)
        elif len(income_amounts) > 0:
            # Perbaikan di sini: gunakan format string yang benar
            ax.pie([np.sum(income_amounts)], labels=['Income'], colors=['#2ecc71'], autopct='%1.1f%%')
            ax.set_title('All Income', fontsize=10)
        elif len(expense_amounts) > 0:
            # Perbaikan di sini: gunakan format string yang benar
            ax.pie([np.sum(expense_amounts)], labels=['Expense'], colors=['#e74c3c'], autopct='%1.1f%%')
            ax.set_title('All Expense', fontsize=10)
        
        # Pastikan layout tight agar tidak ada whitespace berlebih
        self.figure.tight_layout()
        self.canvas.draw()
    
    def closeEvent(self, event):
        """Override close event untuk menutup koneksi database"""
        self.conn.close()
        event.accept()

class AddTransactionDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Transaction")
        self.setModal(True)
        self.setFixedSize(350, 280)
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Date section
        date_layout = QtWidgets.QVBoxLayout()
        date_layout.setSpacing(5)
        date_label = QtWidgets.QLabel("Date:")
        self.date_edit = QtWidgets.QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        
        # Amount section
        amount_layout = QtWidgets.QVBoxLayout()
        amount_layout.setSpacing(5)
        amount_label = QtWidgets.QLabel("Amount:")
        self.amount_edit = QtWidgets.QLineEdit()
        self.amount_edit.setPlaceholderText("Enter amount (e.g., 100000)")
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount_edit)
        
        # Type section
        type_layout = QtWidgets.QVBoxLayout()
        type_layout.setSpacing(5)
        type_label = QtWidgets.QLabel("Type:")
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["Income", "Expense"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        
        # Description section
        desc_layout = QtWidgets.QVBoxLayout()
        desc_layout.setSpacing(5)
        desc_label = QtWidgets.QLabel("Description:")
        self.desc_edit = QtWidgets.QLineEdit()
        self.desc_edit.setPlaceholderText("Enter description (optional)")
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_edit)
        
        # Button section
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 15, 0, 0)
        
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.ok_button = QtWidgets.QPushButton("Add Transaction")
        
        # Connect signals
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Add buttons
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        
        # Add all to main layout
        main_layout.addLayout(date_layout)
        main_layout.addLayout(amount_layout)
        main_layout.addLayout(type_layout)
        main_layout.addLayout(desc_layout)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)

    def get_transaction(self):
        """Return transaction data dari dialog"""
        try:
            amount_text = self.amount_edit.text().strip()
            if not amount_text:
                QMessageBox.warning(self, "Invalid Input", "Please enter an amount!")
                return None
                
            amount = float(amount_text)
            if self.type_combo.currentText() == "Expense" and amount > 0:
                amount = -amount
            
            return {
                "date": self.date_edit.date().toString("yyyy-MM-dd"),
                "amount": amount,
                "type": self.type_combo.currentText(),
                "description": self.desc_edit.text() if self.desc_edit.text().strip() else "No description"
            }
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for amount!")
            return None

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = TransactionApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()