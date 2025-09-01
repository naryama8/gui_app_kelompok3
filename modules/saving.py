import sys
from PyQt5 import uic
# TAMBAHAN: Impor pyqtSignal untuk komunikasi antar jendela
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow

class SavingWindow(QMainWindow):
    # TAMBAHAN: Sinyal ini akan mengirimkan nilai target baru (float)
    targetSet = pyqtSignal(float)
    
    """
    A class to manage the saving target UI.
    It takes the main application's QStackedWidget as a parameter
    to allow navigation back to the dashboard.
    """
    def __init__(self, widget):
        super(SavingWindow, self).__init__()
        
        # Store a reference to the main QStackedWidget
        self.widget = widget
        
        # Load the UI from the 'saving_target.ui' file
        uic.loadUi("ui_files/saving_target.ui", self)
        
        # Initialize the current saving value to 0
        self.current_saving = 0
        self.target_amount = 0 # Tambahan untuk menyimpan target
        
        # Connect the 'ENTER' button to the update function
        self.saving_enter.clicked.connect(self.update_target_and_progress)
        # Connect the 'back' button to the navigation function
        self.saving_back.clicked.connect(self.go_back_to_dashboard)
        
        # Set the initial state of the progress bar and description label
        self.saving_bar.setValue(0)
        self.saving_bar.setFormat('0.00 %') 
        self.saving_keterangan.setText("Silakan masukkan target tabungan Anda.")
        
    # TAMBAHAN: Fungsi untuk menerima data dari dasbor saat jendela dibuka
    def set_current_state(self, target, current_savings):
        """Menerima data target dan tabungan saat ini dari dasbor."""
        self.target_amount = target
        self.current_saving = current_savings
        self.update_view() # Perbarui tampilan dengan data terbaru

    def update_target_and_progress(self):
        """
        Updates the progress bar and emits the new target to the dashboard.
        """
        target_text = self.saving_input.text()

        try:
            target_saving = float(target_text)
            if target_saving > 0:
                self.target_amount = target_saving
                # TAMBAHAN: Kirim sinyal berisi nilai target baru ke dasbor
                self.targetSet.emit(self.target_amount)
                
                # Perbarui tampilan di jendela ini
                self.update_view()
            else:
                self.saving_keterangan.setText("Target tidak boleh nol.")
        
        except ValueError:
            self.saving_keterangan.setText("Input tidak valid, harap masukkan angka.")

    # TAMBAHAN: Fungsi baru untuk memperbarui tampilan saja
    def update_view(self):
        """Memperbarui progress bar dan label di jendela ini."""
        if self.target_amount > 0:
            percentage = (self.current_saving / self.target_amount) * 100.0
            self.saving_bar.setValue(min(int(percentage), 100))
            self.saving_bar.setFormat(f'{percentage:.2f} %')
            # Ganti format teks sesuai permintaan
            keterangan_text = f"Anda telah menabung sebanyak Rp {self.current_saving:,.0f} dari target Rp {self.target_amount:,.0f}"
            self.saving_keterangan.setText(keterangan_text)
        else:
            self.saving_bar.setValue(0)
            self.saving_keterangan.setText(f"Tabungan saat ini: Rp {self.current_saving:,.0f}. Target belum diatur.")

    def go_back_to_dashboard(self):
        """
        Navigates back to the Dashboard screen (index 2) in the QStackedWidget.
        """
        if self.widget:
            self.widget.setCurrentIndex(2)