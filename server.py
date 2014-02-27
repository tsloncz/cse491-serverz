#!/usr/bin/environ python
import random, socket, time
import sys
import urlparse
import Cookie
import quixote
import imageapp

from quixote.demo.altdemo import create_publisher
from urlparse import urlparse
from StringIO import StringIO

from app import make_app
from wsgiref.validate import validator

def handle_connection(conn):
    # Start reading in data from the connection
    req = conn.recv(1)
    count = 0
    environ = {}
    while req[-4:] != '\r\n\r\n':
        req += conn.recv(1)

    # Parse the headers we've received
    req, data = req.split('\r\n',1)
    headers = {}
    for line in data.split('\r\n')[:-2]:
        k, v = line.split(': ', 1)
        headers[k.lower()] = v

    # Parse out the path and related info
    path = urlparse(req.split(' ', 3)[1])
    environ['REQUEST_METHOD'] = 'GET'
    environ['PATH_INFO'] = path[2]
    environ['QUERY_STRING'] = path[4]
    environ['CONTENT_TYPE'] = 'text/html'
    environ['CONTENT_LENGTH'] = '0'
    environ['SCRIPT_NAME'] = ''
    environ['SERVER_NAME'] = 'tSloncz Server'
    environ['SERVER_PORT'] = conn.getsockname()[0]
    environ['wsgi.version'] = (1, 0)
    environ['wsgi.errors'] = sys.stderr
    environ['wsgi.multithread'] = False
    environ['wsgi.multiprocess'] = False
    environ['wsgi.run_once'] = False
    environ['wsgi.url_scheme'] = 'http'
    environ['HTTP_COOKIE'] = headers['cookie']

    def start_response(status, response_headers):
        conn.send('HTTP/1.0 ')
        conn.send(status)
        conn.send('\r\n')
        for pair in response_headers:
            key, header = pair
            conn.send(key + ': ' + header + '\r\n')
        conn.send('\r\n')

    content = ''
    if req.startswith('POST '):
        environ['REQUEST_METHOD'] = 'POST'
        environ['CONTENT_LENGTH'] = headers['content-length']
        environ['CONTENT_TYPE'] = headers['content-type']
        print headers['content-length']

        while len(content) < int(headers['content-length']):
            content += conn.recv(1)

    environ['wsgi.input'] = StringIO(content)
    qx_app = quixote.get_wsgi_app()
    #appl = make_app()
    #validator_app = validator(appl)
    result = qx_app(environ, start_response)
    for data in result:
        conn.send(data)

    conn.close()

def main():
    imageapp.setup()
    p = imageapp.create_publisher()
    s = socket.socket()     # Create a socket object
    host = socket.getfqdn() # Get local machine name
    port = random.randint(8000, 9999)
    s.bind((host, port))    # Bind to the port

    print 'Starting server on', host, port
    print 'The Web server URL for this would be http://%s:%d/' % (host, port)

    s.listen(5) # Now wait for client connection.

    print 'Entering infinite loop; hit CTRL-C to exit'
    while True:
        # Establish connection with client.
        c, (client_host, client_port) = s.accept()
        print 'Got connection from', client_host, client_port
        handle_connection(c)


if __name__ == '__main__':
    main()
