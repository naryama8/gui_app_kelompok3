import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow

class PlusSavingWindow(QMainWindow):
    # kirim jumlah uang yang baru ditambahkan ke dasbor
    savingsAdded = pyqtSignal(float)

    def __init__(self, widget):
        super(PlusSavingWindow, self).__init__()
        uic.loadUi("ui_files/plus_saving.ui", self)
        
        self.widget = widget
        self.target_amount = 0
        self.current_savings = 0

        self.saving_enter.clicked.connect(self.add_saving_amount)
        if hasattr(self, 'saving_back'):
            self.saving_back.clicked.connect(self.go_to_dashboard)

    def set_initial_state(self, target, current_savings):
        """Dipanggil oleh dasbor untuk memberikan data awal saat jendela ini dibuka."""
        self.target_amount = target
        self.current_savings = current_savings
        self.update_view()

    def add_saving_amount(self):
        """Fungsi yang dijalankan saat tombol ENTER ditekan."""
        try:
            amount_to_add = float(self.saving_input.text())
            if amount_to_add > 0:
                # Perbarui total tabungan sementara untuk ditampilkan
                self.current_savings += amount_to_add
                
                self.savingsAdded.emit(amount_to_add)
                
                # Perbarui tampilan di jendela ini
                self.update_view()
                
                # Kosongkan input field
                self.saving_input.clear()
            else:
                self.saving_keterangan.setText("Jumlah harus lebih dari nol.")
        
        except ValueError:
            self.saving_keterangan.setText("Input tidak valid, harap masukkan angka.")
    
    def update_view(self):
        """Memperbarui progress bar dan label di jendela ini."""
        if self.target_amount > 0:
            percentage = (self.current_savings / self.target_amount) * 100.0
            self.saving_bar.setValue(min(int(percentage), 100))
            self.saving_bar.setFormat(f'{percentage:.2f} %')
            keterangan_text = f"Anda telah menabung sebanyak Rp {self.current_savings:,.0f} dari target Rp {self.target_amount:,.0f}"
            self.saving_keterangan.setText(keterangan_text)
        else:
            self.saving_bar.setValue(0)
            self.saving_keterangan.setText("Target belum ditentukan. Silakan atur via 'Edit Target'.")

    def go_to_dashboard(self):
        """Kembali ke dasbor."""
        self.widget.setCurrentIndex(2)