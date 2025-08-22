import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QToolTip
import json
import os

import resources_rc


def loadacc():
    if os.path.exists("accounts.json"):
        with open("accounts.json", "r") as f:
            return json.load(f)
    else:
        return{}

def saveacc(accounts):
    with open("accounts.json", "w") as f:
        json.dump(accounts, f, indent=4)

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
        accounts=loadacc()

        username=self.name.text()
        password=self.password.text()

        if username in accounts and accounts[username]==password:
           print("Successfully Logged in!")
           QToolTip.showText(self.name.mapToGlobal(self.name.rect().bottomLeft()), "Successfully Logged in!")

        if username in accounts and accounts[username]!=password:
           print("Invalid Password!")
           QToolTip.showText(self.password.mapToGlobal(self.password.rect().bottomLeft()), "Invalid Password!")

        else:
           print("This username have not registered yet!")
           QToolTip.showText(self.name.mapToGlobal(self.name.rect().bottomLeft()), "This username have not registered yet!")

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

        accounts=loadacc()

        username=self.name.text()
        password=self.password.text()
        confirmpass=self.confirmpass.text()
        
        # if self.password.text() == self.confirmpass.text(): #Kasus pass=confirmpass
        #     password=self.password.text()
        #     print("Successfully Signed Up!")
        # else:                                            #Kasus pass!=confirmpass   
        #     print("Invalid. Input the same password!")

        # if self.password.text() != self.confirmpass.text():
        #     QToolTip.showText(self.confirmpass.mapToGlobal(self.confirmpass.rect().bottomLeft()), "Passwords do not match")
       
       #Kasus 1: Ada yang gak keisi dari tiga line edits

        if not username or not password or not confirmpass:
         print("Fill All Boxes!")
         QToolTip.showText(self.confirmpass.mapToGlobal(self.confirmpass.rect().bottomLeft()), "Fill All Boxes!")

         
       #Kasus 2: pass != confirmpass

        if password != confirmpass:
         print("Passwords do not match")
         QToolTip.showText(self.confirmpass.mapToGlobal(self.confirmpass.rect().bottomLeft()), "Password do not match!")

      #Kasus 3: Udah pernah Sign up refer ke usernamenya
        if username in accounts:
         print("You Already Have an Account!")
         QToolTip.showText(self.confirmpass.mapToGlobal(self.confirmpass.rect().bottomLeft()), "You Already Have an Account!")

       #Kasus 4: Belum pernah Sign Up, semua box udah diisi, dan pass=confirmpass
        else:
         accounts[username]=password
         saveacc(accounts)
         print("Successfully Signed Up!")
         QToolTip.showText(self.confirmpass.mapToGlobal(self.confirmpass.rect().bottomLeft()), "Successfully Signed Up!")


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
