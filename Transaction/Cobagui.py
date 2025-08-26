from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont

def main():
    app = QApplication([])
    window = QWidget()
    window.setGeometry(200, 200, 200, 300)
    window.setWindowTitle("My Simple GUI")
                          
    layout = QVBoxLayout()
    
    label = QLabel("")
    button = QPushButton("Press Me!")

    layout.addWidget(label)
    layout.addWidget(button)

    window.setLayout(layout)

    label = QLabel(window)
    label.setText("Irell Gaje")
    label.setFont(QFont("Arial", 12))
    label.move(50, 100)

    window.show()
    app.exec_()

if __name__ == '__main__':
    main()