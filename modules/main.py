import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QToolTip
import json

import resources_rc

class Login(QMainWindow):
    def __init__(self):
        super(Login,self).__init__()
        loadUi("ui_files/loginpage.ui", self)

        self.loginButton.clicked.connect(self.loginfunction)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signupButton.clicked.connect(self.createaccount)

        # load gambar ke label
        from PyQt5.QtGui import QPixmap
        pixmap = QPixmap(":/images/logodompetq.png")
        self.logo.setPixmap(pixmap)
        self.logo.setScaledContents(True)

    def loginfunction(self):
        username=self.name.text()
        password=self.password.text()
        print("Successfully Logged in!")

    def createaccount(self): #mau sign up di halaman login
        widget.setCurrentIndex(1) #ini buat pindah halaman ke halaman 1(sign up page)

class Signup(QMainWindow):
    def __init__(self):
        super(Signup,self).__init__()
        loadUi("ui_files/signuppage.ui", self)

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
        username=self.name.text()
        if self.password.text() == self.confirmpass.text():
            password=self.password.text()
            print("Successfully Signed Up!")
        else:
            print("Invalid. Input the same password!")

        if self.password.text() != self.confirmpass.text():
            QToolTip.showText(self.confirmpass.mapToGlobal(self.confirmpass.rect().bottomLeft()), "Passwords do not match")
       

    def backtologin(self):
        widget.setCurrentIndex(0)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Login()
    widget=QtWidgets.QStackedWidget()
    widget.addWidget(ui)
    createacc=Signup()
    widget.addWidget(createacc)
    widget.resize(ui.size()) 
    widget.showMaximized()
    sys.exit(app.exec_())
