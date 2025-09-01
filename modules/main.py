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
from datetime import datetime
import matplotlib.pyplot as plt
from transaction import SetDate, TransactionApp
import io
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
        dashboard.saldo = TransactionApp(activeuser).get_balance()
        dashboard.load_user_data(activeuser)
        dashboard.load_balance()
        dashboard.trendfunc()

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
        dashboard.saldo = TransactionApp(activeuser).get_balance()
        dashboard.load_user_data(activeuser)
        dashboard.load_balance()
        dashboard.trendfunc()


class Dashboard(QMainWindow):
    def __init__(self):
        super(Dashboard, self).__init__()
        loadUi("ui_files/dashboard.ui", self)
        self.saldo = 1
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

        # Hubungkan tombol 'addsavings' dari file .ui ke fungsinya
        # Pastikan nama objek di Qt Designer adalah 'addsavings'
        self.addsavings.clicked.connect(self.goToPlusSavingPage)

        # tombol withdraw
        self.withdraw.clicked.connect(self.manual_withdraw)

        outcome = 120000
        monthlyusage = outcome / self.saldo * 100
        self.monthlyusagebar.setValue(int(monthlyusage))
        self.monthlyusagebar.setMaximum(100)
        self.monthlyusagebar.setMinimum(0)

    def load_balance(self):
        layout = QtWidgets.QVBoxLayout(self.saldonum)
        print(self.saldo)
        self.saldonum.setLayout(layout)
        self.saldonum.setStyleSheet("font-size: 80px; font-weight: bold; background-color: #b2a7dd; border-radius: 40px; text-align: center;")
        self.saldonum.setText(f"Rp. {self.saldo:,}")

    # buat ngelola data tabungan
    def load_user_data(self, username):
        """Memuat data tabungan untuk pengguna yang sedang login."""
        print(f"Memuat data untuk pengguna: {username}")
        all_savings = load_savings()
        user_data = all_savings.get(username, {}) # Dapatkan data user, atau dict kosong jika user baru
        self.monthly_target = user_data.get('target', 0.0)
        self.current_savings = user_data.get('savings', 0.0)
        self.update_savings_display()
        self.check_for_auto_withdraw()

    def save_user_data(self):
        """Menyimpan data tabungan pengguna saat ini ke file JSON."""
        if not activeuser:
            return # Jangan simpan jika tidak ada user yang aktif
        
        all_savings = load_savings()
        all_savings[activeuser] = {
            'target': self.monthly_target,
            'savings': self.current_savings
        }
        save_savings(all_savings)
        print(f"Data untuk pengguna {activeuser} telah disimpan.")

    def trendfunc(self):
        try:
            # Hapus layout sebelumnya jika ada
            if self.trendchart.layout():
                layout = self.trendchart.layout()
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

            global activeuser
            if activeuser is None:
                activeuser = "hitam"

            # Tentukan rentang tanggal yang ingin ditampilkan
            # Contoh: 60 hari terakhir dari hari ini
            enddate = pd.to_datetime('today').date()
            startdate = enddate - pd.Timedelta(days=60)

            # Panggil fungsi baru yang sudah diubah dari prediction_ols.py
            hist_data, pred_data = get_hist_and_pred_data(activeuser, startdate, enddate)

            print(f"Hasil: {len(hist_data)} data historis, {len(pred_data)} data prediksi")

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

            # Plot data historis sebagai bar chart
            if not hist_data.empty:
                ax.bar(hist_data["date"], hist_data["amount"], width=0.8, label="Historical", alpha=0.6, color='#6656be')

            # Plot data prediksi sebagai bar chart
            if not pred_data.empty:
                ax.bar(pred_data["date"], pred_data["predicted_expense"], width=0.8, label="Predicted", alpha=0.8, color='#ff8c00')

            ax.set_xlabel("Tanggal")
            ax.set_ylabel("Pengeluaran")
            ax.set_title(f"Pengeluaran & Prediksi dari {startdate} sampai {enddate}")
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.7)

            # Format tanggal pada sumbu X agar tidak tumpang tindih
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            self.figure.autofmt_xdate(rotation=45)

            self.canvas.draw()

        except Exception as e:
            print(f"Error in trendfunc: {e}")
            import traceback
            traceback.print_exc()
            layout = QVBoxLayout(self.trendchart)
            label = QLabel("Terjadi kesalahan saat membuat grafik.")
            label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(label)

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
                # Perbarui variabel state dan panggil fungsi update tampilan
                self.monthly_target = float(text)
                self.update_savings_display()
                print("Target baru tersimpan")
                self.save_user_data() # Simpan data setelah diubah
        except (ValueError, TypeError):
            QMessageBox.warning(self, "Error", "Masukkan angka yang valid!")

    def switchacc(self):
        # reset data saat logout
        global activeuser
        print(f"Pengguna {activeuser} logout.")
        activeuser = None
        self.monthly_target = 0.0
        self.current_savings = 0.0
        self.update_savings_display()
        widget.setCurrentIndex(0)

    def settingdate(self):
        if activeuser:
            self.setdate_window = SetDate(activeuser)
            self.setdate_window.show()
        else:
            print("Error: Tidak ada user yang aktif")
            QtWidgets.QMessageBox.warning(self, "Error", "Silakan login terlebih dahulu")

    def addingtransaction(self):
        if activeuser:
            self.trxapp_window = TransactionApp(activeuser)
            self.trxapp_window.show()
        else:
            print("Error: Tidak ada user yang aktif")
            QtWidgets.QMessageBox.warning(self, "Error", "Silakan login terlebih dahulu")


    # bikinan naryama
    def kalkuWindow(self):
        kalku.activeuser = activeuser
        kalku.display_balance()
        widget.setCurrentIndex(3)
        
    # pindah window saving
    def goToSavingPage(self):
        print("Going to Saving Page")
        # kirim data target dan tabungan saat ini ke saving_page
        saving_page.set_current_state(self.monthly_target, self.current_savings)
        # The new saving page will be at index 4
        widget.setCurrentIndex(4)

    # fitur add savings
    def goToPlusSavingPage(self):
        """Membuka halaman tambah tabungan dan mengirim data saat ini."""
        plus_saving_page.set_initial_state(self.monthly_target, self.current_savings)
        widget.setCurrentIndex(5) # Pindah ke halaman plus_saving (indeks ke-5)

    def updateCurrentSavings(self, amount_added):
        """Slot untuk menerima sinyal dari PlusSavingWindow dan memperbarui data."""
        self.current_savings += amount_added
        self.add_saving_as_transaction(amount_added)
        self.save_user_data()
        self.update_savings_display()
        self.check_for_auto_withdraw()

    # catat tabungan sebagai transaksi
    def add_saving_as_transaction(self, amount):
        """Menambahkan transaksi 'Expense' ke database setiap kali menabung."""
        if not activeuser:
            return

        try:
            conn = sqlite3.connect('transactions.db')
            cursor = conn.cursor()
            new_transaction = {
                "username": activeuser,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "amount": -amount,
                "type": "Expense",
                "description": "Menabung"
            }
            cursor.execute(
                "INSERT INTO transactions (username, date, amount, type, description) VALUES (?, ?, ?, ?, ?)",
                (
                    new_transaction["username"],
                    new_transaction["date"],
                    new_transaction["amount"],
                    new_transaction["type"],
                    new_transaction["description"]
                )
            )
            conn.commit()
            print(f"Transaksi 'Menabung' sebesar Rp {amount:,.0f} berhasil dicatat.")
        except Exception as e:
            print(f"Gagal mencatat transaksi tabungan: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    def update_savings_display(self):
        """Memperbarui progress bar dan label tabungan di dasbor."""
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
    
    # terima target baru dari saving window
    def updateMonthlyTarget(self, new_target):
        """Slot untuk menerima sinyal dari SavingWindow dan memperbarui target."""
        self.monthly_target = new_target
        self.update_savings_display()
        self.save_user_data()
        self.check_for_auto_withdraw()

    # fungsi withdraw
    def manual_withdraw(self):
        """Fungsi untuk tombol withdraw manual."""
        if self.current_savings <= 0:
            QMessageBox.information(self, "Informasi", "Anda tidak memiliki tabungan untuk ditarik.")
            return

        reply = QMessageBox.question(self, 'Konfirmasi',
                                     f'Anda yakin ingin menarik seluruh tabungan sebesar Rp {self.current_savings:,.0f}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.perform_withdraw(self.current_savings)

    def check_for_auto_withdraw(self):
        """Memeriksa apakah target tabungan sudah tercapai."""
        if self.monthly_target > 0 and self.current_savings >= self.monthly_target:
            print("Target tercapai! Melakukan penarikan otomatis.")
            self.perform_withdraw(self.current_savings, is_auto=True)

    def perform_withdraw(self, amount, is_auto=False):
        """Logika inti untuk melakukan penarikan, baik manual maupun otomatis."""
        # 1. Catat sebagai transaksi pemasukan (Income)
        self.add_withdraw_as_transaction(amount)

        # 2. Reset tabungan saat ini menjadi 0
        self.current_savings = 0.0

        # 3. Simpan state tabungan yang baru (0)
        self.save_user_data()

        # 4. Perbarui tampilan di dasbor
        self.update_savings_display()

        # 5. Beri notifikasi kepada pengguna
        if is_auto:
            QMessageBox.information(self, "Selamat!",
                                    f"Target tabungan Anda tercapai! Sebesar Rp {amount:,.0f} telah ditarik dan ditambahkan ke saldo Anda.")
        else:
            QMessageBox.information(self, "Berhasil",
                                    f"Sebesar Rp {amount:,.0f} berhasil ditarik dan ditambahkan ke saldo Anda.")

    def add_withdraw_as_transaction(self, amount):
        """Menambahkan transaksi 'Income' ke database saat penarikan."""
        if not activeuser:
            return
        try:
            conn = sqlite3.connect('transactions.db')
            cursor = conn.cursor()
            new_transaction = {
                "username": activeuser,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "amount": amount,  # Penarikan dicatat sebagai pemasukan (positif)
                "type": "Income",
                "description": "Penarikan Tabungan"
            }
            cursor.execute(
                "INSERT INTO transactions (username, date, amount, type, description) VALUES (?, ?, ?, ?, ?)",
                (new_transaction["username"], new_transaction["date"], new_transaction["amount"],
                 new_transaction["type"], new_transaction["description"])
            )
            conn.commit()
            print(f"Transaksi 'Penarikan Tabungan' sebesar Rp {amount:,.0f} berhasil dicatat.")
        except Exception as e:
            print(f"Gagal mencatat transaksi penarikan: {e}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()


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
    
    # tambahkan halaman tabungan
    saving_page = SavingWindow(widget)
    widget.addWidget(saving_page)
    # hubungin sinyal dari saving_page ke slot di dasbor
    saving_page.targetSet.connect(dashboard.updateMonthlyTarget)
    
    # halaman plus & saving
    plus_saving_page = PlusSavingWindow(widget)
    widget.addWidget(plus_saving_page)
    
    # Hubungin sinyal dari plus_saving_page ke slot di dasbor
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