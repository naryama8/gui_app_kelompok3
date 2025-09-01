import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QRegExpValidator
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QToolTip
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, QRegExp
from transaction import TransactionApp
import json
from datetime import datetime, timezone

class Kalku(QMainWindow):
    def __init__(self, widget, activeuser):
        super(Kalku, self).__init__()
        loadUi("ui_files/calc_window.ui", self)
        self.widget = widget
        self.activeuser = activeuser
        self.saldo = 0
        self.calculateButton.clicked.connect(self.calculate)
        self.backButton.clicked.connect(self.backtoDashboard)
        self.saveButton.clicked.connect(self.save)
        self.harga_barang.setValidator(QRegExpValidator(QRegExp("[0-9]*")))
        self.from_savings.setValidator(QRegExpValidator(QRegExp("[0-9]*")))
        self.target_perbulan.setValidator(QRegExpValidator(QRegExp("[0-9]*")))

    def display_balance(self):
        self.saldo = TransactionApp(self.activeuser).get_balance()
        self.label.setText(f"Saldo: Rp.{self.saldo:,}")

    def check_result(self):
        price = self.harga_barang.text()
        savings_amount = self.from_savings.text()
        monthly_savings = self.target_perbulan.text()

        try:
            price = int(price)
            savings_amount = int(savings_amount)
            monthly_savings = int(monthly_savings)
            print("True")
            return True

        except ValueError as e:
            print(f"Error: Cannot convert to an integer. {e}")
            print("False")
            return False

    def format_time(self, result):
        if result >= 12:
            years = int(result / 12)
            months = int(result % 12)
            if months == 0:
                return f"{years} Tahun"
            return f"{years} Tahun, {months} Bulan"
        elif result < 1:
            return "Kurang dari 1 Bulan"
        else:
            return f"{int(result)} Bulan"

    def calculate(self):
        print("Calculated Window")
        if self.check_result():
            self.bottomFrame.setStyleSheet("background-color: #6656be;")

            price = self.harga_barang.text()
            savings_amount = self.from_savings.text()
            monthly_savings = self.target_perbulan.text()

            price = int(price)
            savings_amount = int(savings_amount)
            monthly_savings = int(monthly_savings)

            result = (price - savings_amount) / monthly_savings
            upper_result = (price - savings_amount) / ((monthly_savings * 130) / 100)
            lower_result = (price - savings_amount) / ((monthly_savings * 70) / 100)

            result_str = self.format_time(result)
            upper_str = self.format_time(upper_result)
            lower_str = self.format_time(lower_result)

            self.target_hitung.setText("Sesuai Target Menabung: "+result_str)
            self.lower_target.setText("30% Di Bawah Target: "+lower_str)
            self.upper_target.setText("30% Di Atas Target: "+upper_str)

    def save(self):

        price = self.harga_barang.text()
        savings_amount = self.from_savings.text()
        monthly_savings = self.target_perbulan.text()

        price = int(price)
        savings_amount = int(savings_amount)
        monthly_savings = int(monthly_savings)

        result = int((price - savings_amount) / monthly_savings)
        in_seconds = result * 30 * 24 * 60 * 60

        date = datetime.now(timezone.utc).timestamp()
        finish_date = date + in_seconds
        with open('kalku.json') as json_file:
            data = json.load(json_file)

        data[self.activeuser] = [result, date, finish_date]
        with open('kalku.json', 'w') as json_file:
            json.dump(data, json_file)

        self.backtoDashboard()




    def backtoDashboard(self):
        self.widget.setCurrentIndex(2)

