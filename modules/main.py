import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox, QPushButton
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QToolTip, QLabel, QInputDialog
from PyQt5.QtGui import QFont, QPixmap
import json
import os
import subprocess
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from validtransaction import Trx,knowuser
from showtransaction import Listtrx
from calc_window import Kalku
from transaction import TransactionApp
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
import matplotlib.pyplot as plt
from transaction import SetDate, TransactionApp
import io
# Mengimpor fungsi baru
from prediction_ols import get_hist_and_pred_data
import pandas as pd
import matplotlib.dates as mdates

from saving import SavingWindow

from plus import PlusSavingWindow

activeuser = None

import resources_rc

#functions buat load dan save di dua class
def loadacc():
    if os.path.exists("accounts.json"):
        with open("accounts.json", "r") as f:
            return json.load(f)
    else:
        return {}

def saveacc(accounts):
    with open("accounts.json", "w") as f:
        json.dump(accounts, f, indent=4)

# data tabungan user
def load_savings():
    """Memuat data tabungan dari file savings.json."""
    if os.path.exists("savings.json"):
        with open("savings.json", "r") as f:
            return json.load(f)
    else:
        return {} # Mengembalikan dictionary kosong jika file tidak ada

def save_savings(data):
    """Menyimpan data tabungan ke file savings.json."""
    with open("savings.json", "w") as f:
        json.dump(data, f, indent=4)


#functions buat animated background
def _mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def build_gradient_css(step):
    palette = [
        (236, 238, 240),
        (90, 79, 241),
        (183, 176, 221),
        (201, 177, 235),
        (236, 238, 240),
        (90, 79, 241),
        (183, 176, 221),
        (201, 177, 235),
    ]

    D = 60
    n = len(palette)
    i = (step // D) % n
    j = (i + 1) % n
    k = (i + 2) % n
    t = (step % D) / D
    c1 = _mix(palette[i], palette[j], t)
    c2 = _mix(palette[j], palette[k], t)
    r1, g1, b1 = c1
    r2, g2, b2 = c2

    return f"""
    QStackedWidget {{
        background: qlineargradient(
            spread:pad,
            x1:0, y1:0,
            x2:1, y2:1,
            stop:0  rgb({r1},{g1},{b1}),
            stop:1  rgb({r2},{g2},{b2})
        );
    }}
    """

class Login(QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        loadUi("ui_files/loginpage.ui", self)
        self.centralWidget().setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.centralWidget().setStyleSheet("background: transparent;")
        self.loginButton.clicked.connect(self.loginfunction)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signupButton.clicked.connect(self.createaccount)

    def loginfunction(self):
        accounts = loadacc()
        username = self.name.text()
        password = self.password.text()

        if username in accounts and accounts[username] == password:
            print("Successfully Logged in!")
            global activeuser
            activeuser = username
            self.gotodashboard()
        elif username in accounts and accounts[username] != password:
            print("Invalid Password!")
            QToolTip.showText(self.password.mapToGlobal(self.password.rect().bottomLeft()), "Invalid Password!")
        else:
            print("This username has not been registered yet!")
            QToolTip.showText(self.name.mapToGlobal(self.name.rect().bottomLeft()), "This username has not been registered yet!")

    def createaccount(self):
        widget.setCurrentIndex(1)

    def gotodashboard(self):
        widget.setCurrentIndex(2)
        # data masing masing user setelah login
        dashboard.load_user_data(activeuser)
        dashboard.trendfunc()
        dashboard.update_estimation()

class Signup(QMainWindow):
    def __init__(self):
        super(Signup, self).__init__()
        loadUi("ui_files/signuppage.ui", self)
        self.centralWidget().setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.centralWidget().setStyleSheet("background: transparent;")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.wannasignup.clicked.connect(self.signupfunction)
        self.wannalogin.clicked.connect(self.backtologin)
        pixmap = QPixmap(":/images/logodompetq.png")
        self.logo.setPixmap(pixmap)
        self.logo.setScaledContents(True)

    def signupfunction(self):
        accounts = loadacc()
        username = self.name.text()
        password = self.password.text()
        confirmpass = self.confirmpass.text()

        if not username or not password or not confirmpass:
            print("Fill All Boxes!")
            QToolTip.showText(self.confirmpass.mapToGlobal(self.confirmpass.rect().bottomLeft()), "Fill All Boxes!")
        elif username in accounts:
            print("You Already Have an Account!")
            QToolTip.showText(self.confirmpass.mapToGlobal(self.confirmpass.rect().bottomLeft()), "You Already Have an Account!")
        elif password != confirmpass:
            print("Passwords do not match")
            QToolTip.showText(self.confirmpass.mapToGlobal(self.confirmpass.rect().bottomLeft()), "Password do not match!")
        else:
            accounts[username] = password
            saveacc(accounts)
            print("Successfully Signed Up!")
            global activeuser
            activeuser = username
            self.gotodashboard()

    def backtologin(self):
        widget.setCurrentIndex(0)

    def gotodashboard(self):
        widget.setCurrentIndex(2)
        # data tabungan masing masing user setelah login
        dashboard.load_user_data(activeuser)
        dashboard.trendfunc()
        dashboard.update_estimation()


class Dashboard(QMainWindow):
    def __init__(self):
        super(Dashboard, self).__init__()
        loadUi("ui_files/dashboard.ui", self)
        self.centralWidget().setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.centralWidget().setStyleSheet("background: transparent;")
        self.usernamecik.clicked.connect(self.switchacc)
        self.addtransaction.clicked.connect(self.addingtransaction)
        self.setpoint.clicked.connect(self.settingdate)
        self.showpiechart(self.piechart)
        self.edittargetm.clicked.connect(self.goToSavingPage)
        self.kalkutarget.clicked.connect(self.kalkuWindow)

        # Variabel untuk menyimpan data target dan tabungan saat ini
        self.monthly_target = 0.0
        self.current_savings = 0.0
        self.update_savings_display() # Melakukan setup awal tampilan

        self.addsavings.clicked.connect(self.goToPlusSavingPage)

        # tombol withdraw
        self.withdraw.clicked.connect(self.manual_withdraw)

        # Atur ulang tampilan saldo agar dinamis
        self.saldonum.setText("Rp 0")
        self.saldonum.setAlignment(QtCore.Qt.AlignCenter)
        self.saldonum.setStyleSheet("font-size: 80px; font-weight: bold; background-color: #a099d1; border: 1px solid #a099d1; border-radius: 50px; color: white;")

        self.monthlyusagebar.setValue(0)
        self.monthlyusagebar.setMaximum(100)
        self.monthlyusagebar.setMinimum(0)

    def update_saldo_display(self):
        """Menghitung total saldo dari database dan memperbarui tampilan di dashboard."""
        if not activeuser:
            self.saldonum.setText("Rp 0")
            return

        balance = 0
        try:
            conn = sqlite3.connect('transactions.db')
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE username = ?", (activeuser,))
            result = cursor.fetchone()[0]
            balance = result if result is not None else 0.0

            # Update saldo
            self.saldonum.setText(f"Rp {balance:,.0f}")
            print(f"Tampilan saldo untuk {activeuser} diperbarui: Rp {balance:,.0f}")

        except Exception as e:
            print(f"Gagal memperbarui saldo: {e}")
            self.saldonum.setText("Error")
        finally:
            if 'conn' in locals() and conn:
                conn.close()

        # Hitung dan perbarui monthly usage bar
        self.update_monthly_usage(balance)

    def update_monthly_usage(self, current_balance):
        """Menghitung dan memperbarui progress bar Monthly Usage."""
        if not activeuser:
            self.monthlyusagebar.setValue(0)
            return

        total_expense_this_month = 0
        try:
            conn = sqlite3.connect('transactions.db')
            cursor = conn.cursor()
            current_month = datetime.now().strftime("%Y-%m")

            # Ambil total pengeluaran bulan ini
            cursor.execute("""
                SELECT SUM(amount) FROM transactions 
                WHERE username = ? AND type = 'Expense' AND strftime('%Y-%m', date) = ?
            """, (activeuser, current_month))

            result = cursor.fetchone()[0]
            total_expense_this_month = abs(result) if result is not None else 0

            if current_balance + total_expense_this_month > 0:
                usage_percentage = (total_expense_this_month / (current_balance + total_expense_this_month)) * 100
                self.monthlyusagebar.setValue(min(int(usage_percentage), 100))
            else:
                self.monthlyusagebar.setValue(0)

        except Exception as e:
            print(f"Gagal menghitung monthly usage: {e}")
            self.monthlyusagebar.setValue(0)
        finally:
            if 'conn' in locals() and conn:
                conn.close()


    # buat ngelola data tabungan
    def load_user_data(self, username):
        """Memuat data tabungan untuk pengguna yang sedang login."""
        print(f"Memuat data untuk pengguna: {username}")
        all_savings = load_savings()
        user_data = all_savings.get(username, {})
        self.monthly_target = user_data.get('target', 0.0)
        self.current_savings = user_data.get('savings', 0.0)
        self.update_savings_display()
        self.check_for_auto_withdraw()
        self.update_saldo_display()

    def save_user_data(self):
        """Menyimpan data tabungan pengguna saat ini ke file JSON."""
        if not activeuser:
            return
        
        all_savings = load_savings()
        all_savings[activeuser] = {
            'target': self.monthly_target,
            'savings': self.current_savings
        }
        save_savings(all_savings)
        print(f"Data untuk pengguna {activeuser} telah disimpan.")

    def trendfunc(self):
        try:
            if self.trendchart.layout():
                layout = self.trendchart.layout()
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

            global activeuser
            if activeuser is None:
                activeuser = "hitam"

            enddate = pd.to_datetime('today').date()
            startdate = enddate - pd.Timedelta(days=60)
            hist_data, pred_data = get_hist_and_pred_data(activeuser, startdate, enddate)

            layout = QVBoxLayout(self.trendchart)

            if hist_data.empty and pred_data.empty:
                label = QLabel("Tidak ada data yang cukup untuk ditampilkan")
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setStyleSheet("font-size: 16px; color: gray;")
                layout.addWidget(label)
                return

            self.figure = Figure(figsize=(12, 5))
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)
            ax = self.figure.add_subplot(111)

            if not hist_data.empty:
                ax.bar(hist_data["date"], hist_data["amount"], width=0.8, label="Historical", alpha=0.6, color='#6656be')
            if not pred_data.empty:
                ax.bar(pred_data["date"], pred_data["predicted_expense"], width=0.8, label="Predicted", alpha=0.8, color='#ff8c00')

            ax.set_xlabel("Tanggal")
            ax.set_ylabel("Pengeluaran")
            ax.set_title(f"Pengeluaran & Prediksi dari {startdate} sampai {enddate}")
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            self.figure.autofmt_xdate(rotation=45)
            self.canvas.draw()
        except Exception as e:
            print(f"Error in trendfunc: {e}")

    def showpiechart(self, piechart):
        categories = ["Makanan", "Minuman"]
        values = [20, 80]
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(values, labels=categories, autopct='%1.1f%%', startangle=90, colors=['#6656be', '#b2a7dd'])
        canvas = FigureCanvas(fig)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(canvas)
        piechart.setLayout(layout)

    def edit_monthlytarget(self):
        text, ok = QInputDialog.getText(self, "Edit Target", "New Target: ")
        try:
            if ok and text:
                self.monthly_target = float(text)
                self.update_savings_display()
                self.save_user_data()
        except (ValueError, TypeError):
            QMessageBox.warning(self, "Error", "Masukkan angka yang valid!")

    def switchacc(self):
        global activeuser
        activeuser = None
        self.monthly_target = 0.0
        self.current_savings = 0.0
        self.update_savings_display()
        self.update_saldo_display() # Reset saldo ke 0
        widget.setCurrentIndex(0)

    def settingdate(self):
        if activeuser:
            self.setdate_window = SetDate(activeuser)
            self.setdate_window.show()

    def addingtransaction(self):
        if activeuser:
            self.trxapp_window = TransactionApp(activeuser, dashboard_reference=self)
            self.trxapp_window.show()

    # bikinan naryama
    def kalkuWindow(self):
        kalku.activeuser = activeuser
        kalku.display_balance()
        widget.setCurrentIndex(3)

    def update_estimation(self):
        time = datetime.now(timezone.utc).timestamp()
        with open('kalku.json') as json_file:
            data = json.load(json_file)

        if activeuser in data:
            array = data[activeuser]
            seconds_left = array[2] - time
            months_left = seconds_left / 2592000
            self.estday.display(months_left)


    def goToSavingPage(self):
        saving_page.set_current_state(self.monthly_target, self.current_savings)
        widget.setCurrentIndex(4)

    def goToPlusSavingPage(self):
        plus_saving_page.set_initial_state(self.monthly_target, self.current_savings)
        widget.setCurrentIndex(5)

    def updateCurrentSavings(self, amount_added):
        self.current_savings += amount_added
        self.add_saving_as_transaction(amount_added)
        self.save_user_data()
        self.update_savings_display()
        self.update_saldo_display() # Perbarui saldo setelah menabung
        self.check_for_auto_withdraw()

    def add_saving_as_transaction(self, amount):
        if not activeuser: return
        try:
            conn = sqlite3.connect('transactions.db')
            cursor = conn.cursor()
            new_transaction = { "username": activeuser, "date": datetime.now().strftime("%Y-%m-%d"), "amount": -amount, "type": "Expense", "description": "Menabung" }
            cursor.execute("INSERT INTO transactions (username, date, amount, type, description) VALUES (?, ?, ?, ?, ?)", (new_transaction["username"], new_transaction["date"], new_transaction["amount"], new_transaction["type"], new_transaction["description"]))
            conn.commit()
        finally:
            if conn: conn.close()

    def update_savings_display(self):
        if self.monthly_target > 0:
            percentage = (self.current_savings / self.monthly_target) * 100
            self.targetsavings.setValue(min(int(percentage), 100))
            self.targetsavings.setFormat(f'{percentage:.2f} %')
        else:
            self.targetsavings.setValue(0)
            self.targetsavings.setFormat('0.00 %')

        if not hasattr(self, 'savings_label'):
            layout = QVBoxLayout(self.namatarget)
            layout.setContentsMargins(0,0,0,0)
            self.savings_label = QLabel()
            self.savings_label.setAlignment(QtCore.Qt.AlignCenter)
            self.savings_label.setStyleSheet("font-size: 14px; color: white; background-color: transparent;")
            layout.addWidget(self.savings_label)
            self.namatarget.setLayout(layout)

        if self.monthly_target > 0:
            text = f"Anda telah menabung:\nRp {self.current_savings:,.0f}\ndari target Rp {self.monthly_target:,.0f}"
        else:
            text = "Target belum diatur"
        self.savings_label.setText(text)

    def updateMonthlyTarget(self, new_target):
        self.monthly_target = new_target
        self.update_savings_display()
        self.save_user_data()
        self.check_for_auto_withdraw()

    def manual_withdraw(self):
        if self.current_savings <= 0:
            QMessageBox.information(self, "Informasi", "Anda tidak memiliki tabungan untuk ditarik.")
            return

        reply = QMessageBox.question(self, 'Konfirmasi', f'Anda yakin ingin menarik seluruh tabungan sebesar Rp {self.current_savings:,.0f}?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.perform_withdraw(self.current_savings)

    def check_for_auto_withdraw(self):
        if self.monthly_target > 0 and self.current_savings >= self.monthly_target:
            self.perform_withdraw(self.current_savings, is_auto=True)

    def perform_withdraw(self, amount, is_auto=False):
        self.add_withdraw_as_transaction(amount)
        self.current_savings = 0.0
        self.save_user_data()
        self.update_savings_display()
        self.update_saldo_display() # Perbarui saldo setelah withdraw

        if is_auto:
            QMessageBox.information(self, "Selamat!", f"Target tabungan Anda tercapai! Sebesar Rp {amount:,.0f} telah ditarik dan ditambahkan ke saldo Anda.")
        else:
            QMessageBox.information(self, "Berhasil", f"Sebesar Rp {amount:,.0f} berhasil ditarik dan ditambahkan ke saldo Anda.")

    def add_withdraw_as_transaction(self, amount):
        if not activeuser: return
        try:
            conn = sqlite3.connect('transactions.db')
            cursor = conn.cursor()
            new_transaction = { "username": activeuser, "date": datetime.now().strftime("%Y-%m-%d"), "amount": amount, "type": "Income", "description": "Penarikan Tabungan" }
            cursor.execute("INSERT INTO transactions (username, date, amount, type, description) VALUES (?, ?, ?, ?, ?)", (new_transaction["username"], new_transaction["date"], new_transaction["amount"], new_transaction["type"], new_transaction["description"]))
            conn.commit()
        finally:
            if conn: conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Login()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(ui)
    createacc = Signup()
    widget.addWidget(createacc)

    global dashboard
    dashboard = Dashboard()
    widget.addWidget(dashboard)
    kalku=Kalku(widget, activeuser)
    widget.addWidget(kalku)

    saving_page = SavingWindow(widget)
    widget.addWidget(saving_page)
    saving_page.targetSet.connect(dashboard.updateMonthlyTarget)

    plus_saving_page = PlusSavingWindow(widget)
    widget.addWidget(plus_saving_page)
    plus_saving_page.savingsAdded.connect(dashboard.updateCurrentSavings)

    widget.showMaximized()

    widget._bg_step = 0
    widget._bg_timer = QTimer(widget)
    widget._bg_timer.timeout.connect(lambda: (
        setattr(widget, "_bg_step", widget._bg_step + 1),
        widget.setStyleSheet(build_gradient_css(widget._bg_step))
    ))
    widget._bg_timer.start(30)

    sys.exit(app.exec_())

#Ini kode udah selesai yan bener buat halaman login sama signup, jangan diapa2in!