import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QToolTip
import json
import os
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer  

import resources_rc

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

#window dashboard
class Dashboard(QMainWindow):
    def __init__(self):
        super(Dashboard,self).__init__()
        loadUi("ui_files/dashboard.ui", self)
        # bikin central widget transparan supaya background di belakangnya kelihatan
        self.centralWidget().setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.centralWidget().setStyleSheet("background: transparent;")

        #fungsi buat mencet tombol
        # self.loginButton.clicked.connect(self.loginfunction)


#PEMBETULAN BARU SAMPE SINI

    def loginfunction(self):
        accounts=loadacc()

        username=self.name.text()
        password=self.password.text()

        if username in accounts and accounts[username]==password:
           print("Successfully Logged in!")
           QToolTip.showText(self.name.mapToGlobal(self.name.rect().bottomLeft()), "Successfully Logged in!")

        elif username in accounts and accounts[username]!=password:
           print("Invalid Password!")
           QToolTip.showText(self.password.mapToGlobal(self.password.rect().bottomLeft()), "Invalid Password!")

        else:
           print("This username have not registered yet!")
           QToolTip.showText(self.name.mapToGlobal(self.name.rect().bottomLeft()), "This username have not registered yet!")

    def createaccount(self): #mau sign up di halaman login
        widget.setCurrentIndex(1) #ini buat pindah halaman ke halaman 1(sign up page)



#execution blocks
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Login()
    widget=QtWidgets.QStackedWidget()
    widget.addWidget(ui)
    createacc=Signup()
    widget.addWidget(createacc)
    widget.showMaximized()

    # === Animated Gradient START ===
    widget._bg_step = 0
    widget._bg_timer = QTimer(widget)        # simpan sebagai atribut supaya tidak ter-garbage-collect
    widget._bg_timer.timeout.connect(lambda: (
        setattr(widget, "_bg_step", widget._bg_step + 1),
        widget.setStyleSheet(build_gradient_css(widget._bg_step))
    ))
    widget._bg_timer.start(30)  # 30ms ~ 33fps; bisa 16ms untuk lebih halus
    # === Animated Gradient END ===

    sys.exit(app.exec_())