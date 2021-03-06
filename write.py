#!/usr/bin/python3
import socket
import sys
from writerGUI import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
import time
import re
import wave
import linecache
import sys

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


readerIP = "192.168.240.131"
readerPort = 100
logDirectory = 'logs'

def writeData(data, readerIP, readerPort):
	print("WRITE DATA")
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
		print("Writing 2 bytes")
		cmd = bytearray([10, 255, 10, 137, 0, 0, 0, 0, 1, 7 - j, ord(b1) ,ord(b2), CheckDigit(7-j, ord(b1), ord(b2))])
		s.send(cmd)

		# Reading response...
		out = s.recv(2048)
		print("Response: " + " ".join("%02x" % b for b in out))
		if out[3] == 82:
			raise Exception('Write Error: Check if item placed on the writer.')	#happened when no tag was there on the device.
	
	return readData(readerIP, readerPort)


def readData(readerIP, readerPort):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
		s.connect((readerIP, readerPort))
	except:
		raise Exception('NetworkError: Socket creation failed.')

	print("Sending Read request.")
	cmd = bytearray([10, 255, 2, 128, 117])
	s.send(cmd)

	# Reading response
	out = s.recv(2048)
	cnt = out[5]
	print("Response: " + " ".join("%02x" % b for b in out))

	print("Sending get tag data request.")
	cmd = bytearray([10, 255, 3, 65, 16, 163])
	s.send(cmd)

	# Reading response
	out = s.recv(2048)
	print("Response: " + " ".join("%02x" % b for b in out))
	if out[4] > 1:
		raise Exception("WARNING: More than one tags in range!!!")
	elif out[4] == 0:
		raise Exception("WARNING: No tags in range!!!")
	out = out[7:7+12][::-1]
	if out[1] == 0x9e:
		raise Exception("WARNING: Attempted to read empty tag.")
	out = out.decode()
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
		global logDirectory
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
		self.pushButton_2.clicked.connect(self.patronWriteButton_callback)
		self.dataList = []
		try:
			self.count = 0
			with open(logDirectory + "/TagLog_" + time.strftime("%d%m%y") + ".csv") as fp:
				for line in fp:
					if re.search(r'\d{2}/\d{2}/\d{2}', line):  
						self.count += 1
						self.dataList.append(line.split(',')[0])
		except FileNotFoundError:
			self.textBrowser.setPlainText("Message: STARTING A NEW LOG")

		self.lcdNumber.display(self.count)
		self.lcdNumber.setStyleSheet("* { color: darkblue; background-color: black; }")

		
		
	def patronWriteButton_callback(self):
		global readerPort, readerIP, logDirectory
		try:
			data = chr(1) + self.lineEdit.text()
			ret = writeData(data, readerIP, readerPort)	
			if ret == data:
				output = "\nSUCCESSFULLY WORTE " + ret
				self.textBrowser.setPlainText(output)
			else:
				output = "WRITE ERROR! Debug: Wrote " + ret
				self.textBrowser.setPlainText('<p style="color:red;">' + output + "</p>")
		except Exception as ex:
			output = "Internal Exception: " + str(ex)
			self.textBrowser.setPlainText('<p style="color:red;"> ' + output + ' </p>')
			PrintException()	
		self.lineEdit.setFocus()
		self.lineEdit.clear()


	def readButton_callback(self):
		try:
			output = readData(readerIP, readerPort)
			self.textBrowser.setPlainText(output)
		except Exception as ex:
			output = "Internal Exception: " + str(ex)
			self.textBrowser.setPlainText('<p style="color:red;">' + output + '</p>')
			with open(logDirectory + "/ErrorLog.csv" + time.strftime("%d%m%y"), "a+") as fp:
				fp.write(output + "," + time.strftime("%d/%m/%y %H:%M:%S") + '\n')
			PrintException()	

	def writeButton_callback(self):
		global readerPort, readerIP, logDirectory
		try:
			data = self.lineEdit.text()
			if re.search(r'$\d{13}|\d{10}$', data):		#data entered is ISBN
				self.textBrowser.append("ISBN: " + data)
				with open(logDirectory + "/TagLog_" + time.strftime("%d%m%y") + ".csv", "a+") as fp:
					fp.write(data + "\n")
			else:
				data = self.removeZero(data)
				if not re.search(r'^[A-Z]{0,2}\d{1,5}$',data):
					self.textBrowser.append('<p style="color:r76778ed;">INVALID INPUT</p>')
				else:
					ret = writeData(data, readerIP, readerPort)	
					if ret == data:

						output = "\nSUCCESSFULLY WORTE " + ret
						self.textBrowser.setPlainText(output)

						if ret not in self.dataList:
							self.dataList.append(ret)
							self.count += 1
							with open(logDirectory + "/TagLog_" + time.strftime("%d%m%y") + ".csv", "a+") as fp:
								fp.write(data + "," + time.strftime("%d/%m/%y %H:%M:%S") + ',')
							self.lcdNumber.display(self.count)
						
					else:
						output = "WRITE ERROR! Debug: Wrote " + ret
						self.textBrowser.setPlainText('<p style="color:red;">' + output + "</p>")
						with open(logDirectory + "/ErrorLog.csv" + time.strftime("%d%m%y"), "a+") as fp:
							fp.write(output + "," + time.strftime("%d/%m/%y %H:%M:%S") + '\n')
		except Exception as ex:
			output = "Internal Exception: " + str(ex)
			self.textBrowser.setPlainText('<p style="color:red;"> ' + output + ' </p>')
			with open(logDirectory + "/ErrorLog.csv" + time.strftime("%d%m%y"), "a+") as fp:
				fp.write(output + "," + time.strftime("%d/%m/%y %H:%M:%S") + '\n')
			PrintException()	
		self.lineEdit.setFocus()
		self.lineEdit.clear()
				
	def removeZero(self, data):
		try:
			return ''.join(re.search(r'^([A-Z]*)[0 ]*(\d+)$', data).groups())
		except:
			return data
if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = MainWindow()	
	sys.exit(app.exec_())
