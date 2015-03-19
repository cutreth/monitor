def send2middleware(message):
	import socket	
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_ip = socket.gethostbyname('benjeye.ddns.net')
	server_address = (server_ip, 6005)
	
	#COMMENT THIS TO RUN OVER INTERNET
	#server_address = ('localhost', 6005)
	
	try: sock.connect(server_address)
	except: return(("Timeout", None))

	try:
		# Send data
		sock.sendall(message.encode())
		# Look for the response
		data = sock.recv(32).decode()
		sock.close()
		return(("Success", data))
	except:
		sock.close()
		return(("No response", None))
	return(("Unknown", None))

# messages:
## F - force a log or attempt to rerun main loop (depends on state)
## M=1 - set the log period to 1 minutes (value required)
## C - turns off server permanently
## B - perform a 'test break' that restarts the main loop

# Example usage:
## response, value = send2middleware("f")
## response, value = send2middleware("m=1")