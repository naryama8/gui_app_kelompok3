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

class TransactionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        try:
            uic.loadUi('transaction.ui', self)
        except FileNotFoundError:
            QMessageBox.critical(None, "Error", "File transaction.ui tidak ditemukan!")
            sys.exit(1)
        
        self.transactions = []     
        self.setup_chart()
        self.pushButton.clicked.connect(self.add_transaction_dialog)
        self.setup_table()
        self.update_display()
        self.generate_sample_data()

    def setup_chart(self):
        """Setup matplotlib chart di QGraphicsView"""
        
        self.figure = Figure(figsize=(3, 4))
        self.canvas = FigureCanvas(self.figure)
        self.graphicsView.setScene(QtWidgets.QGraphicsScene())
        self.graphicsView.scene().addWidget(self.canvas)
        
    def setup_table(self):
        """Setup table widget"""

        headers = ["Date", "Amount", "Type", "Description"]
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 100)
        self.tableWidget.setColumnWidth(2, 80)
        self.tableWidget.setColumnWidth(3, 200)

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
            self.transactions.append(trans)
        
        self.update_display()

    def add_transaction_dialog(self):
        """Dialog untuk menambah transaksi baru"""
        dialog = AddTransactionDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            transaction = dialog.get_transaction()
            self.transactions.append(transaction)
            self.update_display()

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

    def update_chart(self):
        """Update chart menggunakan matplotlib dan numpy"""
        self.figure.clear()
        
        if not self.transactions:
            return
        
        amounts = np.array([t["amount"] for t in self.transactions])
        income_amounts = amounts[amounts > 0]
        expense_amounts = abs(amounts[amounts < 0])
        ax = self.figure.add_subplot(111)
        
        if len(income_amounts) > 0 and len(expense_amounts) > 0:
            labels = ['Income', 'Expense']
            sizes = [np.sum(income_amounts), np.sum(expense_amounts)]
            colors = ['#2ecc71', '#e74c3c']
            
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.set_title('Income vs Expense', fontsize=10)
        elif len(income_amounts) > 0:
            ax.pie([1], labels=['Income'], colors=['#2ecc71'], autopct='100%')
            ax.set_title('All Income', fontsize=10)
        elif len(expense_amounts) > 0:
            ax.pie([1], labels=['Expense'], colors=['#e74c3c'], autopct='100%')
            ax.set_title('All Expense', fontsize=10)
        
        self.canvas.draw()

class AddTransactionDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Transaction")
        self.setModal(True)
        self.resize(300, 200)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Date:"))
        self.date_edit = QtWidgets.QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.date_edit)
        layout.addWidget(QtWidgets.QLabel("Amount:"))
        self.amount_edit = QtWidgets.QLineEdit()
        self.amount_edit.setPlaceholderText("Enter amount (positive for income)")
        layout.addWidget(self.amount_edit)
        layout.addWidget(QtWidgets.QLabel("Type:"))
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["Income", "Expense"])
        layout.addWidget(self.type_combo)
        layout.addWidget(QtWidgets.QLabel("Description:"))
        self.desc_edit = QtWidgets.QLineEdit()
        self.desc_edit.setPlaceholderText("Enter description")
        layout.addWidget(self.desc_edit)
        button_layout = QtWidgets.QHBoxLayout()
        self.ok_button = QtWidgets.QPushButton("OK")
        self.cancel_button = QtWidgets.QPushButton("Cancel")   
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout) 
        self.setLayout(layout)

    def get_transaction(self):
        """Return transaction data dari dialog"""
        amount = float(self.amount_edit.text())
        if self.type_combo.currentText() == "Expense" and amount > 0:
            amount = -amount
        
        return {
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "amount": amount,
            "type": self.type_combo.currentText(),
            "description": self.desc_edit.text()
        }

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = TransactionApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()