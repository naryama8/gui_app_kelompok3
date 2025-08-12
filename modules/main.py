import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.uic import loadUi

import resources_rc

class Login(QDialog):
    def __init__(self):
        super(Login,self).__init__()
        loadUi("loginpage.ui",self)

        self.loginButton.clicked.connect(self.loginfunction)

    def loginfunction(self):
        username=self.name.text()
        password=self.password.text()
        print("Successfully Logged in!")
