import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QToolTip, QMessageBox
from PyQt5.QtGui import QFont, QRegExpValidator, QPixmap
from PyQt5.QtCore import QTimer, QRegExp
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import json
import os
import resources_rc

# Impor kelas dan fungsi dari file lain
from plus import PlusSavingWindow
from database import initialize_database
from logic import sync_users_from_json, get_user_data, update_user_target, update_user_savings

# (Asumsi modul kustom lainnya)
try:
    from calc_window import Kalku
    from transaction import TransactionApp
except ImportError:
    print("Peringatan: Beberapa file modul kustom tidak ditemukan.")
    class Kalku(QWidget):
        def __init__(self, widget): super().__init__()
    class TransactionApp(QWidget):
        def __init__(self, user): super().__init__()


class SavingTargetWindow(QMainWindow):
    targetSet = pyqtSignal(float)

    def __init__(self, widget):
        super(SavingTargetWindow, self).__init__()
        uic.loadUi("ui_files/saving_target.ui", self)
        self.widget = widget
        self.saving_enter.clicked.connect(self.set_new_target)
        if hasattr(self, 'saving_back'):
            self.saving_back.clicked.connect(self.goToDashboard)
        
    # --- MODIFIKASI 1: Metode baru untuk menerima state dari dasbor ---
    def load_current_state(self, target, current_savings):
        """Menerima data terkini dari dasbor dan memperbarui tampilan."""
        if target > 0:
            percentage = (current_savings / target) * 100.0
            self.saving_bar.setValue(min(int(percentage), 100))
            self.saving_bar.setFormat(f'{percentage:.2f} %')
            self.saving_keterangan.setText(f"Rp {current_savings:,.0f} / Rp {target:,.0f}")
        else:
            self.saving_bar.setValue(0)
            self.saving_bar.setFormat("0.00 %")
            self.saving_keterangan.setText("Silakan masukkan target tabungan baru.")
        
        self.saving_input.clear() # Selalu kosongkan input field

    def set_new_target(self):
        target_text = self.saving_input.text()
        try:
            target_saving = float(target_text)
            if target_saving > 0:
                self.targetSet.emit(target_saving)
                self.goToDashboard()
            else:
                self.saving_keterangan.setText("Target tidak boleh nol.")
        except ValueError:
            self.saving_keterangan.setText("Input tidak valid, harap masukkan angka.")

    def goToDashboard(self):
        self.widget.setCurrentIndex(2)


class Login(QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        uic.loadUi("ui_files/loginpage.ui", self)
        self.centralWidget().setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.centralWidget().setStyleSheet("background: transparent;")
        self.loginButton.clicked.connect(self.loginfunction)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signupButton.clicked.connect(self.createaccount)

    def loginfunction(self):
        accounts = loadacc()
        username = self.name.text()
        password = self.password.text()
        if username in accounts and accounts.get(username) == password:
            print(f"Login berhasil untuk pengguna: {username}")
            global activeuser
            activeuser = username
            dashboard_page.load_user_data(username)
            widget.setCurrentIndex(2)
        else:
            QToolTip.showText(self.password.mapToGlobal(self.password.rect().bottomLeft()), "Username atau Password Salah!")

    def createaccount(self):
        widget.setCurrentIndex(1)
        
class Signup(QMainWindow):
    def __init__(self):
        super(Signup, self).__init__()
        uic.loadUi("ui_files/signuppage.ui", self)
        self.centralWidget().setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.centralWidget().setStyleSheet("background: transparent;")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.wannasignup.clicked.connect(self.signupfunction)
        self.wannalogin.clicked.connect(lambda: widget.setCurrentIndex(0))

    def signupfunction(self):
        accounts = loadacc()
        username = self.name.text()
        password = self.password.text()
        confirmpass = self.confirmpass.text()
        if not username or not password or not confirmpass:
            QToolTip.showText(self.confirmpass.mapToGlobal(self.confirmpass.rect().bottomLeft()), "Isi semua kolom!")
        elif password != confirmpass:
            QToolTip.showText(self.confirmpass.mapToGlobal(self.confirmpass.rect().bottomLeft()), "Password tidak cocok!")
        else:
            accounts[username] = password
            saveacc(accounts)
            print("Berhasil Daftar!")
            sync_users_from_json()
            global activeuser
            activeuser = username
            dashboard_page.load_user_data(username)
            widget.setCurrentIndex(2)


class Dashboard(QMainWindow):
    def __init__(self):
        super(Dashboard, self).__init__()
        uic.loadUi("ui_files/dashboard.ui", self)
        
        self.username = None
        self.target_amount = 0.0
        self.current_savings = 0.0

        self.centralWidget().setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.centralWidget().setStyleSheet("background: transparent;")
        
        self.usernamecik.clicked.connect(lambda: widget.setCurrentIndex(0))
        self.addtransaction.clicked.connect(self.transaction)
        self.kalkutarget.clicked.connect(lambda: widget.setCurrentIndex(3))

        if hasattr(self, 'edittargetm'):
            self.edittargetm.clicked.connect(self.openSavingWindow)
        if hasattr(self, 'addsavings'):
            self.addsavings.clicked.connect(self.openAddSavingWindow)

        saldo = 150000
        layout = QtWidgets.QVBoxLayout(self.saldonum)
        label = QtWidgets.QLabel(f"Rp {saldo:,}")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("font-size: 80px; font-weight: bold; background: transparent; color: white;")
        layout.addWidget(label)
        self.update_dashboard_progress()

    def load_user_data(self, username):
        self.username = username
        user_data = get_user_data(username)
        self.target_amount = user_data.get('target', 0.0)
        self.current_savings = user_data.get('savings', 0.0)
        print(f"Data untuk {username} dimuat: Target={self.target_amount}, Tabungan={self.current_savings}")
        self.update_dashboard_progress()

    # --- MODIFIKASI 2: Mengirim state ke halaman "Edit Target" ---
    def openSavingWindow(self):
        # Sebelum menampilkan halaman, kirim data progres saat ini
        saving_page.load_current_state(self.target_amount, self.current_savings)
        widget.setCurrentIndex(4)

    def openAddSavingWindow(self):
        plus_saving_page.set_initial_state(self.target_amount, self.current_savings)
        widget.setCurrentIndex(5)

    def update_target(self, new_target):
        if self.username:
            print(f"Target baru ditetapkan: {new_target}")
            self.target_amount = new_target
            update_user_target(self.username, self.target_amount)
            self.update_dashboard_progress()

    def add_savings(self, amount_added):
        if not self.username:
            return

        print(f"Tabungan ditambahkan: {amount_added}")
        self.current_savings += amount_added

        if self.target_amount > 0 and self.current_savings >= self.target_amount:
            print("Target tercapai!")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("✨ Selamat, Target Tabungan Anda Tercapai! ✨")
            msg.setInformativeText("Target dan tabungan Anda akan direset. Silakan atur target baru.")
            msg.setWindowTitle("Target Tercapai")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

            update_user_target(self.username, 0.0)
            update_user_savings(self.username, 0.0)
            self.target_amount = 0.0
            self.current_savings = 0.0
            self.update_dashboard_progress()
            self.openSavingWindow()
        else:
            update_user_savings(self.username, self.current_savings)
            self.update_dashboard_progress()

    def update_dashboard_progress(self):
        if self.target_amount > 0:
            percentage = (self.current_savings / self.target_amount) * 100.0
            self.targetsavings.setValue(min(int(percentage), 100))
            self.targetsavings.setFormat(f'{percentage:.2f} %')
        else:
            self.targetsavings.setValue(0)
            self.targetsavings.setFormat("Target belum diatur")

    def transaction(self):
        pass

# (Fungsi bantuan tidak berubah)
def loadacc():
    if not os.path.exists("accounts.json"): return {}
    with open("accounts.json", "r") as f: return json.load(f)
def saveacc(accounts):
    with open("accounts.json", "w") as f: json.dump(accounts, f, indent=4)
activeuser = None
def _mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def build_gradient_css(step):
    palette = [(236, 238, 240), (90, 79, 241), (183, 176, 221), (201, 177, 235)] * 2
    D, n = 60, len(palette)
    i, j, k = (step // D) % n, (step // D + 1) % n, (step // D + 2) % n
    t = (step % D) / D
    c1, c2 = _mix(palette[i], palette[j], t), _mix(palette[j], palette[k], t)
    r1, g1, b1, r2, g2, b2 = *c1, *c2
    return f"QStackedWidget {{ background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgb({r1},{g1},{b1}), stop:1 rgb({r2},{g2},{b2})); }}"

if __name__ == "__main__":
    initialize_database()
    sync_users_from_json()

    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()

    login_page = Login()
    signup_page = Signup()
    dashboard_page = Dashboard()
    kalku_page = Kalku(widget)
    saving_page = SavingTargetWindow(widget)
    plus_saving_page = PlusSavingWindow(widget)

    saving_page.targetSet.connect(dashboard_page.update_target)
    plus_saving_page.savingsAdded.connect(dashboard_page.add_savings)

    widget.addWidget(login_page)
    widget.addWidget(signup_page)
    widget.addWidget(dashboard_page)
    widget.addWidget(kalku_page)
    widget.addWidget(saving_page)
    widget.addWidget(plus_saving_page)

    widget.showMaximized()
    
    widget._bg_step = 0
    widget._bg_timer = QTimer(widget)
    widget._bg_timer.timeout.connect(lambda: (
        setattr(widget, "_bg_step", widget._bg_step + 1),
        widget.setStyleSheet(build_gradient_css(widget._bg_step))
    ))
    widget._bg_timer.start(30)
    
    sys.exit(app.exec_())
