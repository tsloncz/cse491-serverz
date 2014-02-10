#!/usr/bin/env python
import random, socket, time
from urlparse import urlparse # credit to Jason Lefler code
import signal # to control execution time
import cgi # to parse post data
import jinja2 # for html template
import StringIO # for string buffer

# jinja file path
JinjaTemplateDir = './templates'

# buffer size for conn.recv
BuffSize = 128

# timeout for conn.recv (in seconds)
ConnTimeout = .1

def main(socketModule = None):
    if socketModule == None:
        socketModule = socket

    s = socketModule.socket() # Create a socket object
    host = socketModule.getfqdn() # Get local machine name
    port = random.randint(8000,8009)
    s.bind((host, port)) # Bind to the port
    
    print 'Starting server on', host, port
    print 'The Web server URL for this would be http://%s:%d/' % (host, port)

    s.listen(5) # Now wait for client connection.

    print 'Entering infinite loop; hit CTRL-C to exit'
    while True:
        # Establish connection with client.
        conn, (client_host, client_port) = s.accept()
        print 'Got connection from', client_host, client_port
        handle_connection(conn)

# raise error when time out
def signal_handler(signum, frame):
    raise Exception("Timed out!")

def handle_connection(conn):
    jLoader = jinja2.FileSystemLoader(JinjaTemplateDir)
    jEnv = jinja2.Environment(loader=jLoader)
    
    reqData = getData(conn)
    reqPage = getPage(reqData)
    reqFS = createFS(reqData)
    
    try:
        serverResponse = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n'
        serverResponse += jEnv.get_template(reqPage).render(reqFS)
    except jinja2.exceptions.TemplateNotFound:
        serverResponse = error404(jEnv, reqData)
 
    conn.send(serverResponse)
    conn.close()

# handle getting data from connection with arbitrary size
def getData(conn):
    # Note: can use global reqData to get rid of error
    reqData = ""
    # signal is used to control execution time
    signal.signal(signal.SIGALRM, signal_handler)
    signal.setitimer(signal.ITIMER_REAL, ConnTimeout, ConnTimeout) # set timeout

    try:
        while True:
            reqData += conn.recv(BuffSize)
    except Exception, msg:
        signal.alarm(0) # turn off signal
    return reqData

# Get page name from request data
def getPage(reqData):
    path = urlparse(reqData.split()[1])[2].lstrip('/') # credit to Jason Lefler

    if path == '':
        path = 'index'
    if not '.' in path:
        path += '.html'

    return path

# initialize field storage object based on request data
# work with both GET and POST method
def createFS(reqData):
    buf = StringIO.StringIO(reqData)
    line = buf.readline()
    env = {'REQUEST_METHOD' : line.split()[0], 'QUERY_STRING' : ''}

    # create query string to work with GET method
    uri = line.split()[1]
    if "?" in uri:
        env['QUERY_STRING'] = uri.split('?',1)[1]

    # seperate headers data
    # defaul content-type to make fieldstorage work with GET
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    while True:
        line = buf.readline()
        if line == '\r\n' or line == '':
            break # empty line = end of headers section
        key, value = line.strip('\r\n').split(": ",1)
        headers[key.lower()] = value # credit to Ben Taylor
    
    # credit to Maxwell Brown
    return cgi.FieldStorage(fp = buf, headers=headers, environ=env)

def error404(jEnv, reqData):
    svrRes = 'HTTP/1.0 404 Not Found\r\nContent-type: text/html\r\n\r\n'
    svrRes += jEnv.get_template('404.html').render()
    return svrRes

if __name__ == '__main__':
    main()
