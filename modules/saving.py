import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Asumsi file UI bernama 'UI Target.ui'
        uic.loadUi("UI Target.ui", self)
        
        # --- PERUBAHAN ---
        # Nilai referensi diubah dari 215000 menjadi 0
        self.current_saving = 0
        
        self.saving_enter.clicked.connect(self.update_progress_bar)
        self.saving_bar.setValue(0)
        self.saving_bar.setFormat('0.00 %') 
        self.saving_keterangan.setText("Silakan masukkan target tabungan Anda.")

    def update_progress_bar(self):
        target_text = self.saving_input.text()

        try:
            target_saving = float(target_text)
            if target_saving > 0:
                # Rumus progres bar akan dihitung berdasarkan current_saving yang dimulai dari 0
                percentage = (self.current_saving / target_saving) * 100.0
                
                self.saving_bar.setValue(min(int(percentage), 100))
                self.saving_bar.setFormat(f'{percentage:.2f} %')

                keterangan_text = f"Rp {self.current_saving:,.0f} / Rp {target_saving:,.0f}"
                self.saving_keterangan.setText(keterangan_text)
            else:
                self.saving_bar.setValue(0)
                self.saving_bar.setFormat('0.00 %')
                self.saving_keterangan.setText("Target tidak boleh nol.")
        
        except ValueError:
            self.saving_keterangan.setText("Input tidak valid, harap masukkan angka.")
            self.saving_bar.setValue(0)
            self.saving_bar.setFormat('0.00 %')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()