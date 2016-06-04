#!/usr/bin/python3
import socket
import sys
from writerGUI import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
import time
import re

readerIP = "192.168.240.132"
readerPort = 100
logDirectory = 'logs'

def writeData(data, readerIP, readerPort):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
		s.connect((readerIP, readerPort))
	except:
		raise Exception('NetworkError: Socket creation failed.')

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
			raise Exception('Write Error: Check if item placed on the writer.')	#happened when no tag was there on the device.
	
	return readData(readerIP, readerPort)


def readData(readerIP, readerPort):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
		s.connect((readerIP, readerPort))
	except:
		raise Exception('NetworkError: Socket creation failed.')

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
	out = out[::-1][1:12+1].decode()
	out = ''.join([c if ord(c) != 0 else '' for c in out])

	
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
		self.window.show()
		self.window.move(300,300)

		self.pushButton.setDefault(True)
		self.pushButton.setAutoDefault(True)
		self.pushButton.clicked.connect(self.writeButton_callback)
		self.enterShortcut = QShortcut(QKeySequence(Qt.Key_Return), self.window)
		self.enterShortcut.activated.connect(self.writeButton_callback)

		self.readButton.clicked.connect(self.readButton_callback)
		
		self.count = 0
		self.lcdNumber.setStyleSheet("* { color: darkblue; background-color: black; }")

		self.dataList = []
		
	def readButton_callback(self):
		output = readData(readerIP, readerPort)
		self.textBrowser.setPlainText(output)

	def writeButton_callback(self):
		global readerPort, readerIP, logDirectory
		try:
			data = self.lineEdit.text()
			data = self.removeZero(data)
			ret = writeData(data, readerIP, readerPort)	
			if ret == data:
				output = "SUCCESSFULLY WORTE " + ret
				self.textBrowser.setPlainText(output)
				if ret not in self.dataList:
					self.dataList.append(ret)
					self.count += 1
					with open(logDirectory + "/TagLog_" + time.strftime("%d%m%y") + ".csv", "a+") as fp:
						fp.write(data + "," + time.strftime("%d/%m/%y %H:%M:%S") + '\n')
					self.lcdNumber.display(self.count)
				
			else:
				output = "WRITE ERROR! Debug: Wrote " + ret
				self.textBrowser.setPlainText(output)
				with open(logDirectory + "/ErrorLog.csv" + time.strftime("%d%m%y"), "a+") as fp:
					fp.write(output + "," + time.strftime("%d/%m/%y %H:%M:%S") + '\n')
		except Exception as ex:
			output = "Internal Exception: " + str(ex)
			self.textBrowser.setPlainText(output)
			with open(logDirectory + "/ErrorLog.csv" + time.strftime("%d%m%y"), "a+") as fp:
				fp.write(output + "," + time.strftime("%d/%m/%y %H:%M:%S") + '\n')
		self.lineEdit.setFocus()
		self.lineEdit.clear()
				
	def removeZero(self, data):
		return ''.join(re.search(r'^(\D*)0*(.*)$', data).groups())

if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = MainWindow()	
	sys.exit(app.exec_())
