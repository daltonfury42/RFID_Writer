import socket


readerIP = "192.168.240.132"
readerPort = 100

def command(cmd):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
		s.connect((readerIP, readerPort))
	except:
		raise Exception('NetworkError: Socket creation failed.')
	
	s.send(cmd)
	return s.recv(2048)

	
