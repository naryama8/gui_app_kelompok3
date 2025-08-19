import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi

import resources_rc

class Login(QMainWindow):
    def __init__(self):
        super(Login,self).__init__()
        loadUi("ui_files/loginpage.ui", self)

        self.loginButton.clicked.connect(self.loginfunction)

        # load gambar ke label
        from PyQt5.QtGui import QPixmap
        pixmap = QPixmap(":/images/logodompetq.png")
        self.logo.setPixmap(pixmap)
        self.logo.setScaledContents(True)

    def loginfunction(self):
        username=self.name.text()
        password=self.password.text()
        print("Successfully Logged in!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Login()
    widget=QtWidgets.QStackedWidget()
    widget.addWidget(ui)
    widget.resize(ui.size()) 
    widget.showMaximized()
    sys.exit(app.exec_())
