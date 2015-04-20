def handler(signum, frame):
    raise Exception()

def send2middleware(message, serverURL = None, testMode = False):
    import socket
    import platform
    import signal    
    try: from monitor.do import getServerUrl
    except:
        def getServerUrl():
            return(serverURL)
 
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

code=F - Force a log or attempt to rerun main loop (depends on state)

send2middleware("code=f", testMode = True) = ('Success', 'Forcing log...')

----------------------------------------------------------------

code=m&freq=n - Set the log period to n minutes

send2middleware("code=m&freq=1", testMode = True)   = ('Success', 'Changed now minLog=1')
send2middleware("code=m", testMode = True)          = ('Success', 'Log frequency=15')
send2middleware("code=m&freq=", testMode = True)    = ('Success', 'Log frequency=1')
send2middleware("code=m&freq=", testMode = True)    = ('Success', 'Log frequency=1')

----------------------------------------------------------------

code=r&var=var_name - Get the averages that are currently in memory for var_name

send2middleware("code=r&var=temp_amb", testMode = True)     = ('Success', 'temp_amb:75.8')
send2middleware("code=r", testMode = True)		            = ('Success', "{'temp_unit': 'F', 'inst")	#Attempts to return all vars; will come back truncated
send2middleware("code=r&var=light_beer", testMode = True)   = ('Fail', 'light_beer is not valid.')
send2middleware("code=r&var=", testMode = True)             = ('Fail', ' is not valid.')

----------------------------------------------------------------

code=c&dir=direction - Turns on/off data collection and logging

send2middleware("code=c&dir=off", testMode = True)      = ('Success', 'Data collection off.')
send2middleware("code=c&dir=off", testMode = True)      = ('Fail', 'Was already off.')
send2middleware("code=c&dir=on", testMode = True)       = ('Success', 'Data collection on.')
send2middleware("code=c&dir=on", testMode = True)       = ('Fail', 'Was already on.')
send2middleware("code=c&dir=toggle", testMode = True)   = ('Success', 'Data collection on.')
send2middleware("code=c&dir=toggle", testMode = True)   = ('Success', 'Data collection off.')
send2middleware("code=c&dir=", testMode = True)         = ('Success', 'Data collection off.') #Status report
send2middleware("code=c", testMode = True)              = ('Success', 'Data collection off.') #Status report

----------------------------------------------------------------

code=L&dir=direction - Turns on/off remote logging, continues to add logs to queue

send2middleware("code=L&dir=off", testMode = True)      = ('Success', 'Remote logging off.')
send2middleware("code=L&dir=off", testMode = True)      = ('Fail', 'Was already off.')
send2middleware("code=L&dir=on", testMode = True)       = ('Success', 'Remote logging on.')
send2middleware("code=L&dir=on", testMode = True)       = ('Fail', 'Was already on.')
send2middleware("code=L&dir=toggle", testMode = True)   = ('Success', 'Remote logging on.')
send2middleware("code=L&dir=toggle", testMode = True)   = ('Success', 'Remote logging off.')
send2middleware("code=L&dir=", testMode = True)         = ('Success', 'Remote logging off.') #Status report
send2middleware("code=L", testMode = True)              = ('Success', 'Remote logging off.') #Status report

----------------------------------------------------------------

code=a&var=var_name&min=min_val&max=max_val - Turns on audible alerts from the middleware for var_name when out of the min_val-max_val range
!!Do not exclude var, min, or max (unless sending 'off' as var) as it may lock up  server (needs to be tested in production to know for sure)!!

send2middleware("code=a&var=temp_beer&max=80&min=70", testMode = True)  = ('Success', 'Alert for temp_beer set to [70, 80]')
send2middleware("code=a&var=off", testMode = True)                      =( 'Success', 'Alerts turned off')

----------------------------------------------------------------

code=s&time=unixvalue - Changes the middleware's system clock to the unixtime (UTC seconds since epoch)

send2middleware("?code=s&time=1429548009", testMode = True) = ('Success', 'Time set to 2015-04-20 11:40:09')
send2middleware("?code=s", testMode = True)                 = ('Fail', 'Unknown error, time not set')

----------------------------------------------------------------
'''
