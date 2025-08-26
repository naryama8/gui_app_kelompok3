import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtGui import QFont
import json
import os
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer  
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import main

global username

username=main.activeuser

#fungsi load dari json
def loaddb():
    if os.path.exists("database.json"):
        with open("database.json", "r") as f:
            return json.load(f)
    return{}

#fungsi menyimpan ke json
def savedb(db):
    with open("database.json", "w") as f:
        json.dump(db, f, indent=4)

#fungsi tambah transaksi baru
def addtransaction(username, type, category, value, date, startdate, enddate):
    db = loaddb()

    db[username]["transactions"].append({
        "type": type,
        "category": category,
        "value": int(value),  
        "date": date,
        "start_date": startdate,
        "end_date": enddate
    })

    savedb(db)

#fungsi ngambil semua transasksi user saat ini
def gettransactions(username):
    db = loaddb()
    return db.get(username, {}).get("transactions",[])

#fungsi mengupdate start atau end date user
def updaterange(username, startdate=None, enddate=None):
    db = loaddb()

    for trx in db[username]["transactions"]:
        if startdate:
            trx["startdate"] = startdate
        if enddate:
            trx["enddate"] = enddate

    savedb(db)


class InputTransaction(QMainWindow):
    def __init__(self):
        super(InputTransaction,self).__init__()
        loadUi("ui_files/inputtransaction.ui", self)

    def savedata(self):

        type=self.transaksi.currentText()
        category=self.kategori.currentText()
        value=self.value.text()
        date = self.calendarWidget.selectedDate().toString("yyyy-MM-dd")
        startdate = self.startdate.selectedDate().toString("yyyy-MM-dd")
        enddate = self.enddate.selectedDate().toString("yyyy-MM-dd")

        #semua data harus masuk kecuali startdate sama enddate
        #startdate sama enddate boleh gak dimasukin kalo udah pernah dimasukin
        #kalo startdate sama enddate gak dimasukin, startdate sama enddate akan refer ke startdate smaa enddate sebelumnya

        #kasus 1: ada value yang tidak diisi

        if not type or not category or not value or not date:
            QToolTip.showText(self.savebutton.mapToGlobal(self.savebutton.rect().bottomLeft()), "Fill All Fields!")
            return
        
        #bagian pemeriksaan apakah pernah ngisi startdate dan enddate


        db=loaddb()
        userdata = db.get(username, {})

        #kasus 2: kalo sebelumnya belum pernah ada transaksi
        if not userdata or "transactions" not in userdata or len(userdata["transactions"])==0:
            if not startdate or not enddate:
                QToolTip.showText(self.savebtn.mapToGlobal(self.savebtn.rect().bottomLeft()), 
                          "Start date and End date must be filled at least once!")
                return

        #kasus 2: kalo sebelumnya udah pernah ada transaksi  
        else:
        # kalau udah ada transaksi → pake yang lama aja
            lasttransaction = userdata["transactions"][-1]
            if not startdate:
                startdate = lasttransaction.get("start_date")
            if not enddate:
                enddate = lasttransaction.get("end_date")

        #kasus 3: semua aman
        addtransaction(username, type, category, value, date, startdate, enddate)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    inputtrx = InputTransaction()
    inputtrx.showMaximized()
    sys.exit(app.exec_())

    
      