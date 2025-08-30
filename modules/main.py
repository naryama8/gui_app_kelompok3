import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtGui import QFont, QRegExpValidator
import json
import os
import subprocess
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, QRegExp
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from validtransaction import Trx,knowuser
from showtransaction import Listtrx
from calc_window import Kalku
from transaction import TransactionApp
import sqlite3
from collections import defaultdict
from datetime import datetime

import resources_rc

#functions buat load dan save di dua class
def loadacc():
    if os.path.exists("accounts.json"):
        with open("accounts.json", "r") as f:
            return json.load(f)
    else:
        return{}

def saveacc(accounts):
    with open("accounts.json", "w") as f:
        json.dump(accounts, f, indent=4)

#variabel active user
activeuser = None

#fungsi penghubung ke fungsi trend
def trendfunc(x):
   return x**2 #masih dummy

#functions buat animated background
def _mix(a, b, t):
    # linear interpolation per channel (0..255)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def build_gradient_css(step):
    """
    Membangun stylesheet background gradient yang berubah setiap 'step'.
    'step' biasanya dinaikkan terus oleh QTimer (animasi).
    """
    # Palet warna dasar (boleh diganti):
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

    D = 60  # durasi (dalam tick) untuk transisi dari satu warna ke warna berikutnya
    n = len(palette)

    # Tentukan tiga warna bertetangga berdasarkan step saat ini:
    i  = (step // D) % n        # indeks warna "awal" fase
    j  = (i + 1) % n            # warna setelah i
    k  = (i + 2) % n            # warna setelah j
    t  = (step % D) / D         # progress 0..1 di transisi i -> j

    # Dua warna stop gradient adalah hasil blend:
    # - c1: di antara i dan j (posisi sekarang)
    # - c2: di antara j dan k (selangkah di depan), supaya gradasinya terasa "bergerak"
    c1 = _mix(palette[i], palette[j], t)
    c2 = _mix(palette[j], palette[k], t)

    r1, g1, b1 = c1
    r2, g2, b2 = c2

    # Orientasi gradient: diagonal dari kiri-atas (0,0) ke kanan-bawah (1,1).
    # Jika mau horizontal: x1=0,y1=0 -> x2=1,y2=0
    # Jika mau vertikal:   x1=0,y1=0 -> x2=0,y2=1
    return f"""
    QStackedWidget {{
        background: qlineargradient(
            spread:pad,
            x1:0, y1:0,
            x2:1, y2:1,
            stop:0   rgb({r1},{g1},{b1}),
            stop:1   rgb({r2},{g2},{b2})
        );
    }}
    """

class Login(QMainWindow):
    def __init__(self):
        super(Login,self).__init__()
        loadUi("ui_files/loginpage.ui", self)
        # bikin central widget transparan supaya background di belakangnya kelihatan
        self.centralWidget().setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.centralWidget().setStyleSheet("background: transparent;")

        self.loginButton.clicked.connect(self.loginfunction)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signupButton.clicked.connect(self.createaccount)


    def loginfunction(self):
        accounts=loadacc()

        username=self.name.text()
        password=self.password.text()

        if username in accounts and accounts[username]==password:
           print("Successfully Logged in!")
           global activeuser
           activeuser=username
           self.loginButton.clicked.connect(self.gotodashboard)
           

        elif username in accounts and accounts[username]!=password:
           print("Invalid Password!")
           QToolTip.showText(self.password.mapToGlobal(self.password.rect().bottomLeft()), "Invalid Password!")

        else:
           print("This username have not registered yet!")
           QToolTip.showText(self.name.mapToGlobal(self.name.rect().bottomLeft()), "This username have not registered yet!")

    def createaccount(self): #mau sign up di halaman login
        widget.setCurrentIndex(1) #ini buat pindah halaman ke halaman 1(sign up page)

    def gotodashboard(self):
        widget.setCurrentIndex(2)

class Signup(QMainWindow):
    def __init__(self):
        super(Signup,self).__init__()
        loadUi("ui_files/signuppage.ui", self)
        # bikin central widget transparan supaya background di belakangnya kelihatan
        self.centralWidget().setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.centralWidget().setStyleSheet("background: transparent;")

        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.wannasignup.clicked.connect(self.signupfunction)
        self.wannalogin.clicked.connect(self.backtologin)

        # load gambar ke label
        from PyQt5.QtGui import QPixmap
        pixmap = QPixmap(":/images/logodompetq.png")
        self.logo.setPixmap(pixmap)
        self.logo.setScaledContents(True)

    def signupfunction(self):

        accounts=loadacc()

        username=self.name.text()
        password=self.password.text()
        confirmpass=self.confirmpass.text()
      
       #Kasus 1: Ada yang gak keisi dari tiga line edits

        if not username or not password or not confirmpass:
         print("Fill All Boxes!")
         QToolTip.showText(self.confirmpass.mapToGlobal(self.confirmpass.rect().bottomLeft()), "Fill All Boxes!")

        #Kasus 2: Udah pernah Sign up refer ke usernamenya
        elif username in accounts:
         print("You Already Have an Account!")
         QToolTip.showText(self.confirmpass.mapToGlobal(self.confirmpass.rect().bottomLeft()), "You Already Have an Account!")

       #Kasus 3: pass != confirmpass

        elif password != confirmpass:
         print("Passwords do not match")
         QToolTip.showText(self.confirmpass.mapToGlobal(self.confirmpass.rect().bottomLeft()), "Password do not match!")

      
       #Kasus 4: Belum pernah Sign Up, semua box udah diisi, dan pass=confirmpass
        else:
         accounts[username]=password
         saveacc(accounts)
         print("Successfully Signed Up!")
         global activeuser
         activeuser=username
         self.wannasignup.clicked.connect(self.gotodashboard)


    def backtologin(self):
        widget.setCurrentIndex(0)

    def gotodashboard(self):
        widget.setCurrentIndex(2)


class Dashboard(QMainWindow):
    def __init__(self):
        super(Dashboard,self).__init__()
        loadUi("ui_files/dashboard.ui", self)
        # bikin central widget transparan supaya background di belakangnya kelihatan
        self.centralWidget().setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.centralWidget().setStyleSheet("background: transparent;")
        self.usernamecik.clicked.connect(self.switchacc)
        self.addtransaction.clicked.connect(self.transaction)
        self.kalkutarget.clicked.connect(self.kalkuWindow)

        # Setup database untuk mengambil data transaksi
        self.init_database()

        #untuk label saldo: saldonum
        saldo = 150000
        layout = QtWidgets.QVBoxLayout(self.saldonum)  
        label = QtWidgets.QLabel(f"Rp {saldo:,}")  
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("font-size: 80px; font-weight: bold;")
        layout.addWidget(label)
        self.saldonum.setLayout(layout)


        #untuk monthly usage progress bar
        outcome=120000  #perlu diganti fungsi outcome
        monthlyusage = outcome/saldo * 100

        self.monthlyusagebar.setValue(int(monthlyusage))
        self.monthlyusagebar.setMaximum(100)
        self.monthlyusagebar.setMinimum(0)

        #untuk grafik trend outcome
        
        layout = QVBoxLayout(self.trendchart)

        x = np.arange(1,6)
        y = [trendfunc(i) for i in x]

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        ax = self.figure.add_subplot(111)
        ax.bar(x, y, color="#7b6fcc")
        ax.set_title("Your Outcome Trend")
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")


        self.canvas.draw()

        #untuk monthly target progress bar
        forsavings=100000  #perlu diganti fungsi for savings
        target_savings=120000
        progresssavings = forsavings/target_savings * 100

        self.targetsavings.setValue(int(progresssavings))
        self.targetsavings.setMaximum(100)
        self.targetsavings.setMinimum(0)

        # Setup pie chart untuk outcome
        self.setup_pie_chart()
        
        # Load dan tampilkan data
        self.load_and_display_data()

    def init_database(self):
        """Initialize database connection"""
        try:
            self.conn = sqlite3.connect('transactions.db')
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"Database connection error: {e}")
            self.conn = None
            self.cursor = None

    def load_user_transactions(self):
        """Load transaksi untuk user yang aktif"""
        if not self.conn or not activeuser:
            return []
            
        try:
            self.cursor.execute("SELECT date, amount, type, description FROM transactions WHERE username = ? ORDER BY date DESC", (activeuser,))
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
        except Exception as e:
            print(f"Error loading transactions: {e}")
            return []

    def setup_pie_chart(self):
        """Setup pie chart untuk outcome categories"""
        if not hasattr(self, 'piechart'):
            print("Widget 'piechart' tidak ditemukan. Pastikan nama widget sesuai dengan UI file.")
            return
        if self.piechart.layout():
            QtWidgets.QWidget().setLayout(self.piechart.layout())
            
        layout = QVBoxLayout(self.piechart)
        layout.setContentsMargins(5, 5, 5, 5)
        self.pie_figure = Figure(figsize=(4, 3), facecolor='#aaaaff')
        self.pie_canvas = FigureCanvas(self.pie_figure)
        layout.addWidget(self.pie_canvas)

    def update_pie_chart(self, transactions):
        """Update pie chart dengan data transaksi real"""
        if not hasattr(self, 'pie_figure'):
            return
            
        self.pie_figure.clear()
        
        if not transactions:
            # Tampilkan pesan jika tidak ada data
            ax = self.pie_figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No Expense Data\nStart adding transactions!', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=10, color='white')
            ax.set_facecolor('#aaaaff')
            self.pie_canvas.draw()
            return
        
        # Kelompokkan pengeluaran berdasarkan kategori
        expense_categories = defaultdict(float)
        
        for trans in transactions:
            if trans["amount"] < 0:
                desc = trans["description"].lower()
                category = self.categorize_expense(desc)
                expense_categories[category] += abs(trans["amount"])
        
        if not expense_categories:
            # Tidak ada pengeluaran
            ax = self.pie_figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No Expense Data', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=10, color='white')
            ax.set_facecolor('#aaaaff')
            self.pie_canvas.draw()
            return
        
        labels = list(expense_categories.keys())
        sizes = list(expense_categories.values())
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dda0dd', '#98d8c8', '#f7dc6f']
        ax = self.pie_figure.add_subplot(111)
        ax.set_facecolor('#aaaaff')
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors[:len(labels)], 
                                        autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8, 'color': 'white'})
    
        ax.set_title('Expense Categories', fontsize=10, color='white', pad=10)
        self.pie_figure.tight_layout()
        self.pie_canvas.draw()

    def categorize_expense(self, description):
        """Kategorikan pengeluaran berdasarkan description"""
        desc_lower = description.lower()
        
        # Mapping keywords ke kategori
        categories = {
            'food': ['makan', 'food', 'resto', 'restaurant', 'snack', 'groceries', 'grocery'],
            'transport': ['bensin', 'transport', 'fuel', 'gas', 'motor', 'car', 'taxi', 'bus'],
            'shopping': ['belanja', 'shopping', 'online', 'shop', 'beli', 'buy'],
            'housing': ['kost', 'rent', 'sewa', 'listrik', 'air', 'utility'],
            'entertainment': ['hiburan', 'movie', 'game', 'entertainment', 'nonton'],
            'health': ['obat', 'doctor', 'hospital', 'health', 'medical'],
            'education': ['buku', 'course', 'training', 'education', 'school'],
        }
        
        # Cek setiap kategori
        for category, keywords in categories.items():
            if any(keyword in desc_lower for keyword in keywords):
                return category.title()
        
        # Default kategori jika tidak cocok
        return 'Others'

    def load_and_display_data(self):
        """Load dan display data untuk pie chart"""
        # Load transaksi user
        transactions = self.load_user_transactions()
        
        # Update pie chart untuk outcome categories
        self.update_pie_chart(transactions)

    def switchacc(self):
        widget.setCurrentIndex(0)


    def transaction(self):
        """Fungsi untuk membuka window Trx"""
        # Pastikan activeuser sudah diset
        if activeuser:
            currentuser = knowuser(activeuser)
            # Buat instance TransactionApp dan kirim activeuser sebagai parameter
            self.transaction_window = TransactionApp(activeuser)
            self.transaction_window.show()
        else:
            print("Error: Tidak ada user yang aktif")
            QtWidgets.QMessageBox.warning(self, "Error", "Silakan login terlebih dahulu")


    # bikinan naryama
    def kalkuWindow(self):
        print("Kalku Window")
        widget.setCurrentIndex(3)

    def showEvent(self, event):
        """Override showEvent untuk refresh data ketika dashboard ditampilkan"""
        super().showEvent(event)
        # Refresh data setiap kali dashboard ditampilkan
        self.load_and_display_data()

    def closeEvent(self, event):
        """Override close event untuk menutup koneksi database"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        event.accept()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Login()
    widget=QtWidgets.QStackedWidget()
    widget.addWidget(ui)
    createacc=Signup()
    widget.addWidget(createacc)
    dashboard=Dashboard()
    widget.addWidget(dashboard)
    kalku=Kalku(widget)
    widget.addWidget(kalku)
    widget.showMaximized()

    # === Animated Gradient START ===
    widget._bg_step = 0
    widget._bg_timer = QTimer(widget)        
    widget._bg_timer.timeout.connect(lambda: (
        setattr(widget, "_bg_step", widget._bg_step + 1),
        widget.setStyleSheet(build_gradient_css(widget._bg_step))
    ))
    widget._bg_timer.start(30)  
    

    sys.exit(app.exec_())


#Ini kode udah selesai yan bener buat halaman login sama signup, jangan diapa2in!
