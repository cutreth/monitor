def handler(signum, frame):
    raise Exception()

def send2middleware(message, testMode = False):
    import socket
    import platform
    import signal    
    from monitor.do import getServerUrl
 
    if platform.system() != 'Windows': 
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(10)
 
    r = None
    msg = None
 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if testMode == False:
        server_url = getServerUrl()
        server_ip = socket.gethostbyname(server_url)
        server_address = (server_ip, 6005)
    else: server_address = ('localhost', 6005)
    
    try: 
        sock.connect(server_address)
    except: 
        r = 'Timeout'

    if not bool(r):
        try:
            # Send data
            sock.sendall(message.encode())
            # Look for the response
            data = sock.recv(64).decode()
            sock.close()
            r,msg = data.split("|")
        except:
            sock.close()
            r= 'No response'
            
    if not bool(r):
        r = 'Unknown'
    
    if platform.system() != 'Windows': 
        signal.alarm(0)
        
    return((r, msg))

'''
+-----------------------------------------------+
|send2middleware(msg, testMode = False)		|
| -msg (command) to send to middleware		|
| -testMode = True means you're running locally	|
+-----------------------------------------------+


Msg - Description

Example call = Response

----------------------------------------------------------------

F - Force a log or attempt to rerun main loop (depends on state)

send2middleware("f") = ('Success', 'Forcing log...')

----------------------------------------------------------------

M=n - Set the log period to n minutes

send2middleware("m=1")	= ('Success', 'Changed now minLog=1')	#Returns new minLog value
send2middleware("m")	= ('Success', 'Log frequency=15')		#Returns current minLog value
send2middleware("m=")	= ('Fail', 'Number needed. minLog=15')	#Returns current minLog value

----------------------------------------------------------------

R=var_name - Get the averages that are currently in memory for var_name

send2middleware("r=temp_amb")	= ('Success', 'temp_amb:75.8')
send2middleware("r")		= ('Success', "{'temp_unit': 'F', 'inst")	#Attempts to return all vars; will come back truncated
send2middleware("r=light_beer")	= ('Fail', 'light_beer is not valid.')
send2middleware("r=")		= ('Fail', ' is not valid.')

----------------------------------------------------------------

O - Turns off data collection and logging

send2middleware("O")	= ('Success', 'Data collection off.')
send2middleware("O")	= ('Fail', 'Was already off.')
----------------------------------------------------------------

L - Turns off data collection and logging

send2middleware("L")	= ('Success', 'Data collection on.')
send2middleware("L")	= ('Fail', 'Was already on.')

----------------------------------------------------------------

E - Turns off remote logging, continues to add logs to queue

send2middleware("E")	= ('Success', 'Remote logging off.')
send2middleware("E")	= ('Fail', 'Remote logging was already off.')
----------------------------------------------------------------

D - Turns on remote logging

send2middleware("D")	= ('Success', 'Remote logging on.')
send2middleware("D")	= ('Fail', 'Remote logging was already on.')

----------------------------------------------------------------
!!DEFUNCT!!
C - Turns off server permanently, will require access to the server to turn it back on

send2middleware("c", True)	= ('Success', 'Cancelled.')

----------------------------------------------------------------
'''
