'''
2018 Yonsei CS - Computer Network
Simple Multiuser TCP chat Program Project 
2015147508 Chae Yeon Han 
'''
import socket, sys, select, queue
import termios, copy

fd = sys.stdin.fileno()
termios_before = termios.tcgetattr(fd)
termios_after = copy.deepcopy(termios_before)
termios_after[3] = termios_after[3] & ~termios.ECHO

#read host IP and port number
host = sys.argv[1]
port = sys.argv[2]
port_int = int(port)
size = 1024

#create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
#set blocking 0 to accept more than 1 client
server_socket.setblocking(0)

#bind the socket to the port
server_address = (host,port_int) 
print ('Chat Server started on port '+port)
server_socket.bind(server_address)

#listen for incoming connections
server_socket.listen(1)
input_list = [sys.stdin,server_socket]
output_list = []
message = {}

try :
	termios.tcsetattr(fd, termios.TCSADRAIN, termios_after)
	while True:
		sr, sw, se = select.select(input_list, output_list, input_list)
		for s in sr:
			if s == server_socket:
				#when client came into server socket, 
				#create a new client socket and make it non-blocking
				client_socket, client_address = server_socket.accept()
				client_socket.setblocking(0)
				input_list.append(client_socket)
				message[client_socket] = queue.Queue()
				#broadcast to other client_sockets that new client has entered
				mesg = '> New user %s:%s entered.' %client_address+'( %s users online)'%(len(input_list)-2)+'\n'
				sys.stdout.write(mesg)
				mesg = '\n'+mesg
				for sockets in input_list:
					if sockets != server_socket and sockets != client_socket and sockets != sys.stdin:
						try:
							sockets.send(mesg.encode())
						except:
							sockets.close()
							input_list.remove(sockets)
					
			else:
				#when something came into client socket
				data = s.recv(size)
				if data:
					#if it is a message
					message[s].put(data)
					if s not in output_list:
						output_list.append(s)
					#broadcast other client_sockets that other client has entered a message
					mesg = '\n['+str(s.getpeername()[0])+':'+str(s.getpeername()[1])+'] '+data.decode()+'\n'
					for sockets in input_list:
						if sockets != server_socket and sockets != s and sockets != sys.stdin:
							try:
								sockets.send(mesg.encode())
							except:
								sockets.close()
								input_list.remove(sockets)
				else: 
					#if client closed the socket
					if s in output_list:
						output_list.remove(s)
					input_list.remove(s)
					#broadcast to clients that the client left the chat room
					mesg = '< The user %s:%s left' %client_address+'(%s users left)'%(len(input_list)-2)+'\n'
					sys.stdout.write(mesg)
					mesg = '\n'+mesg
					for sockets in input_list:
						if sockets != server_socket and sockets != client_socket and sockets != sys.stdin:
							try:
								sockets.send(mesg.encode())
							except:
								sockets.close()
								input_list.remove(sockets)
					s.close()
					del message[s]
		for s in sw: 
			#when the socket is writable, which means they have something to send
			try: 
				next_msg = message[s].get_nowait()
			except queue.Empty: 
			#when the socket has no more to output
				output_list.remove(s)
			else: 
			#send the message to the client socket
				print('['+str(s.getpeername()[0])+':'+str(s.getpeername()[1])+']'+data.decode())
				s.send(next_msg)
		for s in se:
			#when the socket is an error
			input_list.remove(s)
			if s in output_list:
				output_list.remove(s)
			s.close()
			del message[s]
	server_socket.close()
	sys.exit()
except KeyboardInterrupt:
	pass
finally:
	termios.tcsetattr(fd, termios.TCSADRAIN, termios_before)
	print('\r\nKeyboardInterrupt')
	server_socket.close()
	sys.exit()


