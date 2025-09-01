import sys
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow

class SavingWindow(QMainWindow):
    # buat kirim sinyal berisi target baru ke dasbor
    targetSet = pyqtSignal(float)
    
    """
    A class to manage the saving target UI.
    It takes the main application's QStackedWidget as a parameter
    to allow navigation back to the dashboard.
    """
    def __init__(self, widget):
        super(SavingWindow, self).__init__()
        
        # simpan referensi ke QStackedWidget utama
        self.widget = widget
        
        # memuat file .ui
        uic.loadUi("ui_files/saving_target.ui", self)
        
        # difinisikan variabel untuk menyimpan data target dan tabungan saat ini
        self.current_saving = 0
        self.target_amount = 0 
        
        # hubungin tombol 'enter'
        self.saving_enter.clicked.connect(self.update_target_and_progress)
        # hubungin tombol 'back'
        self.saving_back.clicked.connect(self.go_back_to_dashboard)
        
        # ngatur tampilan awal
        self.saving_bar.setValue(0)
        self.saving_bar.setFormat('0.00 %') 
        self.saving_keterangan.setText("Silakan masukkan target tabungan Anda.")
        
    # nerima data dari dasbor saat jendela dibuka
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
                # kirim target baru ke dasbor
                self.targetSet.emit(self.target_amount)
                
                # Perbarui tampilan
                self.update_view()
            else:
                self.saving_keterangan.setText("Target tidak boleh nol.")
        
        except ValueError:
            self.saving_keterangan.setText("Input tidak valid, harap masukkan angka.")

    # untuk perbarui tampilan
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