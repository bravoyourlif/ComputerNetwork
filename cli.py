'''
2018 Yonsei CS - Computer Network
Simple Multiuser TCP chat Program Project 
2015147508 Chae Yeon Han 
'''

import socket, sys, select
import termios, copy

#linux os prompt control
fd = sys.stdin.fileno()
termios_before = termios.tcgetattr(fd)
termios_after = copy.deepcopy(termios_before)
termios_after[3] = termios_after[3] & ~termios.ECHO

#read host IP and port number
host = sys.argv[1]
port = sys.argv[2]
port_int = int(port)
size = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (host, port_int)
#connect to server socket
client_socket.connect(server_address)
input_list = [sys.stdin,client_socket]
print('> Connected to the chat server (%s user online)'%(len(input_list)-1))
sys.stdout.write('[You] ')
sys.stdout.flush()

try: 
	termios.tcsetattr(fd, termios.TCSADRAIN, termios_after)
	while True:
		sr, sw, se = select.select(input_list,[],[]) 
		for s in sr:
			if s == client_socket:
			#when server sent client something 
				data = client_socket.recv(size)
				if not data:
					#server_socket has been closed
					print('\n< You have been disconnected. \n')
					s.close()
					sys.exit()	
				else:
					sys.stdout.write(data.decode())
					sys.stdout.write('[You] ')
					sys.stdout.flush()										
			else:
			#when client is entering a message
				msg = sys.stdin.readline()
				if msg == "\n":
					print('\n< You have been disconnected. \n')
					s.close()
					sys.exit()
				client_socket.send(msg.encode())

except KeyboardInterrupt:
	pass
finally:
	termios.tcsetattr(fd, termios.TCSADRAIN, termios_before)
	print('\r\nKeyboardInterrupt')
	client_socket.close()
	sys.exit()

