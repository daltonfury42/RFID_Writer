import socket
import sys
from writerGUI import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow

readerIP = "192.168.240.110"
readerPort = 100

def writeData(data, readerIP, readerPort):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
		s.connect((readerIP, readerPort))
	except:
		raise Exception('NetworkError: Socket creation failed.')
	dataLength = len(data)
	for i in range(12-len(data)):
		data = data + chr(0)
	for j in range(6):
		b2 = (data[j*2])
		b1 = (data[j*2+1])

		# Sending Write request... 10,255,10,137,0,0,0,0,1, 7 - position to write in, byte1, byte2, CheckDigitValue

		cmd = bytearray([10, 255, 10, 137, 0, 0, 0, 0, 1, 7 - j, ord(b1) ,ord(b2), CheckDigit(7-j, ord(b1), ord(b2))])
		s.send(cmd)

		# Reading response...
		out = s.recv(2048)

		if out[3] == 82:
			raise Exception('Write Error')

	# Sending Read request...
	cmd = bytearray([10, 255, 2, 128, 117])
	s.send(cmd)

	# Reading response
	out = s.recv(2048)
	cnt = out[5]

	# Sending get tag data request...
	cmd = bytearray([10, 255, 3, 65, 16, 163])
	s.send(cmd)

	# Reading response
	out = s.recv(2048)
	out = out[::-1][1:dataLength+1].decode()
	#hex_string = "".join("%02x" % b for b in out)
	#final_string = hex_string[::-1][2:len(data)]
	
	return out
	

def CheckDigit(a, b, c):
	i = a + b + c + 413
	
	if i < 255:
		i = 256 - i
	elif i < 511:
		i = 512 - i
	elif i < 1023:
		i = 1024 - i
	
	if i > 255:
		i = i - 256
	
	return i

class MainWindow(Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.window = QMainWindow()
		self.setupUi(self.window)
		self.pushButton.clicked.connect(self.button_callback)
		self.window.show()

		self.count = 0

	def button_callback(self):
		global readerPort, readerIP
		data = self.lineEdit.text();
		try:
			if self.sane(data):
				ret = writeData(data, readerIP, readerPort)
			if ret == data:
				output = "SUCCESSFULLY WORTE " + ret
				self.textBrowser.setPlainText(output)
			else:
				output = "WRITE ERROR! Debug: Wrote " + ret
				self.textBrowser.setPlainText(output)
		except Exception as ex:
			output = "Internal Exception: " + str(ex)
			self.textBrowser.setPlainText(output)

	def sane(self, data):
		"""Checks if the data is sane or not. Yet to be implimented."""
		return True

if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = MainWindow()	
	sys.exit(app.exec_())