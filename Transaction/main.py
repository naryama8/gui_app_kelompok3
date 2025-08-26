import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                           QTableWidgetItem, QDialog, QFormLayout, 
                           QLineEdit, QComboBox, QDateEdit, QMessageBox, 
                           QHeaderView)
from PyQt5.QtCore import Qt, QDate
from PyQt5 import uic
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os


class TransactionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Transaksi")
        self.setModal(True)
        self.setFixedSize(350, 250)
        
        layout = QFormLayout()
        
        # Date input
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        layout.addRow("Tanggal:", self.date_edit)
        
        # Amount input
        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("Masukkan jumlah (Rp)")
        layout.addRow("Amount (Rp):", self.amount_edit)
        
        # Type input
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Pemasukan", "Pengeluaran"])
        layout.addRow("Tipe:", self.type_combo)
        
        # Description input
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Masukkan deskripsi")
        layout.addRow("Deskripsi:", self.description_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Batal")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def get_transaction_data(self):
        return {
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'amount': float(self.amount_edit.text()) if self.amount_edit.text() else 0.0,
            'type': self.type_combo.currentText(),
            'description': self.description_edit.text()
        }


class ChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        # MATPLOTLIB: Membuat figure dan canvas
        self.figure = Figure(figsize=(6, 5))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self.update_chart([])
    
    def update_chart(self, transactions):
        # MATPLOTLIB: Membersihkan figure sebelumnya
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not transactions:
            ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes, 
                   ha='center', va='center', fontsize=14)
        else:
            income_total = sum(t[2] for t in transactions if t[3] == 'Pemasukan')
            expense_total = sum(t[2] for t in transactions if t[3] == 'Pengeluaran')
            
            labels = []
            sizes = []
            colors = []
            
            if income_total > 0:
                labels.append(f'Pemasukan\nRp {income_total:,.0f}')
                sizes.append(income_total)
                colors.append('#4CAF50')   
            
            if expense_total > 0:
                labels.append(f'Pengeluaran\nRp {expense_total:,.0f}')
                sizes.append(expense_total)
                colors.append('#F44336') 
            
            if sizes:
                ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                      startangle=90, textprops={'fontsize': 12})
                ax.set_title('Pemasukan vs Pengeluaran', fontsize=16, fontweight='bold')
        
        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load UI file
        ui_file = "transaction_window.ui"
        if os.path.exists(ui_file):
            print(f"Loading UI file: {ui_file}")
            uic.loadUi(ui_file, self)
        else:
            QMessageBox.critical(self, "Error", f"File UI '{ui_file}' tidak ditemukan!")
            sys.exit(1)
        
        self.setWindowTitle("Personal Finance Tracker - Rupiah Version")
        self.init_database()
        
        # Debug: Print all available attributes
        print("Available attributes:")
        for attr in dir(self):
            if not attr.startswith('_') and ('btn' in attr.lower() or 'widget' in attr.lower() or 'label' in attr.lower()):
                print(f"  - {attr}")
        
        self.setup_ui_enhancements()
        self.connect_signals()
        self.load_transactions()
    
    def setup_ui_enhancements(self):
        """Setup additional UI enhancements that can't be done in .ui file"""
        
        print("Setting up UI enhancements...")
        
        # Check if widgets exist before using them
        if hasattr(self, 'ChartWidget'):
            # Replace the ChartWidget placeholder with actual ChartWidget
            old_chart = self.ChartWidget
            chart_geometry = old_chart.geometry()
            old_chart.setParent(None)
            
            self.ChartWidget = ChartWidget()
            self.ChartWidget.setParent(self.centralwidget)
            self.ChartWidget.setGeometry(chart_geometry)
            print("ChartWidget replaced successfully")
        else:
            print("Warning: ChartWidget not found in UI file")
        
        # Setup table headers if table exists
        if hasattr(self, 'tableWidget'):
            headers = ["Tanggal", "Jumlah (Rp)", "Tipe (Pemasukan/Pengeluaran)", "Deskripsi"]
            self.tableWidget.setColumnCount(4)
            for i, header in enumerate(headers):
                item = QTableWidgetItem()
                item.setText(header)
                self.tableWidget.setHorizontalHeaderItem(i, item)
            
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            print("Table headers set successfully")
        else:
            print("Warning: tableWidget not found in UI file")
        
        # Apply basic styles
        self.apply_basic_styles()
    
    def apply_basic_styles(self):
        """Apply basic styles to widgets"""
        
        # Button styles (check if buttons exist)
        if hasattr(self, 'btnAddTransaction'):
            self.btnAddTransaction.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            print("Add button styled")
        
        if hasattr(self, 'btnDeleteTransaction'):
            self.btnDeleteTransaction.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #D32F2F;
                }
            """)
            print("Delete button styled")
        
        # Table style
        if hasattr(self, 'tableWidget'):
            self.tableWidget.setStyleSheet("""
                QTableWidget {
                    gridline-color: #E0E0E0;
                    background-color: white;
                    font-size: 12px;
                    border: 1px solid #E0E0E0;
                }
                QHeaderView::section {
                    background-color: #F5F5F5;
                    padding: 8px;
                    border: none;
                    font-weight: bold;
                }
            """)
            print("Table styled")
    
    def connect_signals(self):
        """Connect button signals to their respective slots"""
        if hasattr(self, 'btnAddTransaction'):
            self.btnAddTransaction.clicked.connect(self.add_transaction)
            print("Add transaction button connected")
        else:
            print("Warning: btnAddTransaction not found")
        
        if hasattr(self, 'btnDeleteTransaction'):
            self.btnDeleteTransaction.clicked.connect(self.delete_transaction)
            print("Delete transaction button connected")
        else:
            print("Warning: btnDeleteTransaction not found")
    
    def init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect('transactions.db')
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                description TEXT
            )
        ''')
        self.conn.commit()
        print("Database initialized")
    
    def add_transaction(self):
        """Open dialog to add new transaction"""
        dialog = TransactionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_transaction_data()
                if data['amount'] <= 0:
                    QMessageBox.warning(self, "Jumlah Tidak Valid", "Silakan masukkan jumlah yang valid lebih dari 0.")
                    return
                
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO transactions (date, amount, type, description)
                    VALUES (?, ?, ?, ?)
                ''', (data['date'], data['amount'], data['type'], data['description']))
                self.conn.commit()
                
                self.load_transactions()
                QMessageBox.information(self, "Berhasil", "Transaksi berhasil ditambahkan!")
                
            except ValueError:
                QMessageBox.warning(self, "Input Tidak Valid", "Silakan masukkan jumlah yang valid.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menambahkan transaksi: {str(e)}")
    
    def delete_transaction(self):
        """Delete selected transaction"""
        if not hasattr(self, 'tableWidget'):
            QMessageBox.warning(self, "Error", "Table widget not found")
            return
            
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Tidak Ada Pilihan", "Silakan pilih transaksi yang akan dihapus.")
            return
        
        transaction_id = self.tableWidget.item(current_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(self, "Konfirmasi Hapus", 
                                   "Apakah Anda yakin ingin menghapus transaksi ini?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                cursor = self.conn.cursor()
                cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
                
                if cursor.rowcount > 0:
                    self.conn.commit()
                    self.load_transactions()
                    QMessageBox.information(self, "Berhasil", "Transaksi berhasil dihapus!")
                else:
                    QMessageBox.warning(self, "Error", "Transaksi tidak ditemukan dalam database.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus transaksi: {str(e)}")
    
    def load_transactions(self):
        """Load transactions from database and update UI"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM transactions ORDER BY date DESC')
        transactions = cursor.fetchall()
        
        print(f"Loaded {len(transactions)} transactions")
        
        # Update table if it exists
        if hasattr(self, 'tableWidget'):
            self.tableWidget.setRowCount(len(transactions))
            for row, transaction in enumerate(transactions):
                item = QTableWidgetItem(transaction[1])  
                item.setData(Qt.UserRole, transaction[0])  
                self.tableWidget.setItem(row, 0, item)
                
                self.tableWidget.setItem(row, 1, QTableWidgetItem(f"Rp {transaction[2]:,.0f}"))  
                self.tableWidget.setItem(row, 2, QTableWidgetItem(transaction[3]))  
                self.tableWidget.setItem(row, 3, QTableWidgetItem(transaction[4] or ""))  
        
        # Calculate totals
        total_income = sum(t[2] for t in transactions if t[3] == 'Pemasukan')
        total_expense = sum(t[2] for t in transactions if t[3] == 'Pengeluaran')
        balance = total_income - total_expense
        
        # Update value labels if they exist
        if hasattr(self, 'balance_value'):
            self.balance_value.setText(f"Rp {balance:,.0f}")
        if hasattr(self, 'expense_value'):
            self.expense_value.setText(f"Rp {total_expense:,.0f}")
        if hasattr(self, 'income_value'):
            self.income_value.setText(f"Rp {total_income:,.0f}")
        
        # Update chart if it exists
        if hasattr(self, 'ChartWidget') and hasattr(self.ChartWidget, 'update_chart'):
            self.ChartWidget.update_chart(transactions)
        
        # Update status bar if it exists
        if hasattr(self, 'statusbar'):
            self.statusbar.showMessage(f"Total Transaksi: {len(transactions)} | Saldo: Rp {balance:,.0f}")
        
        print("UI updated successfully")
    
    def closeEvent(self, event):
        """Close database connection when app closes"""
        self.conn.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    app.setApplicationName("DompetQ")
    app.setApplicationVersion("2.0") 
    
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()