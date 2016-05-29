import socket
import sys
from writerGUI import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow

readerIP = ""
readerPort = 30

def writeData():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
	s.connect((readerIP, readerPort))

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(window)

	window.show()
	sys.exit(app.exec_())