#!/usr/bin/environ python
import random, socket, time
import sys
import urlparse
import Cookie
import quixote
import argparse
import chat
import cookieApp

import imageApp
from quixote.demo.altdemo import create_publisher
from urlparse import urlparse
from StringIO import StringIO
from quotes.apps import QuotesApp

from app import make_app
from wsgiref.validate import validator

def handle_connection(conn, application):
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
    environ['HTTP_COOKIE'] = headers['cookie'] if 'cookie' in headers.keys() else ''

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
    #being strange validator_app = validator(application)
    result = application(environ, start_response)
    if result:
      for data in result:
        conn.send(data)

    conn.close()

def main():
	#Command line args parse
    parser = argparse.ArgumentParser()
    parser.add_argument("-A",help="What application to run")
    parser.add_argument("-p",help="What port to use",type=int)
    args = parser.parse_args()

    if not args.A:
        print "Please specify an app with -A"
        return -1;
    if args.p:
        port = args.p
    else:
        port = random.randint(8000, 9999)

    if args.A == "image":
        wsgi_app = imageApp.make_image_app()
    elif args.A == "altdemo":
        p = quixote.demo.altdemo.create_publisher()
        wsgi_app = quixote.get_wsgi_app()
    elif args.A == "myapp":
        wsgi_app = make_app()
    elif args.A == "quotes":
        wsgi_app = QuotesApp('quotes/quotes.txt', './quotes/html')
    elif args.A == "chat":
	      wsgi_app = chat.setup()
    elif args.A == "cookie":
	      wsgi_app = cookieApp.get_wsgi_app()
    else:
        print "App not found"
        return -1;

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
        handle_connection(c, wsgi_app)


if __name__ == '__main__':
    main()
