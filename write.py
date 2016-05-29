import socket
import sys
from writerGUI import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow

readerIP = ""
readerPort = 30

def writeData():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
	s.connect((readerIP, readerPort))

class MainWindow(Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.window = QMainWindow()
		self.setupUi(self.window)
		self.pushButton.connect(self.button_callback)
		window.show()

	def button_callback(self):
		print("Worked!")

if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = MainWindow()	
	sys.exit(app.exec_())