import random
import socket
import time
import os
import cgi
import urlparse
import argparse
import StringIO
from wsgiref.validate import validator
from sys import stderr
from app import make_app
import imageapp
import quixote
from quixote.demo.altdemo import create_publisher
from quotes.apps import QuotesApp
from chat.apps import ChatApp
import cookieapp

# Server interface for quixote demos and imageapp
class Server:
    def  __init__(self, host, port, app):
        if host:
            self.host = host
        else:
            self.host = socket.getfqdn() # Get local machine name
        self.port = port
        self.app = app
    def serve_forever(self):
        s = socket.socket()         # Create a socket object

        s.bind((self.host, self.port))

        print 'Starting server on', self.host, self.port
        print 'The Web server URL for this would be http://%s:%d/' % (self.host, self.port)

        s.listen(5)                 # Now wait for client connection

        print 'Entering infinite loop; hit CTRL-C to exit'
        while True:
            # Establish connection with client.    
            c, (client_host, client_port) = s.accept()
            print 'Got connection from', client_host, client_port

            self.handle_connection(c)
    def handle_connection(self, conn):
        receive = conn.recv(1)

        if not receive:
            print('Error: Client did not send any data')
            return

        # Receive data until end of headers
        while receive[-4:] != '\r\n\r\n':
            receive += conn.recv(1)
        request, headers = receive.split('\r\n', 1)

        # Put headers into a dictionary
        headers_dict = {}
        for line in headers.split('\r\n')[:-2]:
            k, v = line.split(':', 1)
            headers_dict[k.lower()] = v.strip(' ')

        request = request.split(' ')
        method = request[0]
        parsed_url = urlparse.urlparse(request[1])
        path = parsed_url.path
        query = parsed_url.query

        content_type = headers_dict.get('content-type')
        content_length = headers_dict.get('content-length')
        cookie_header = headers_dict.get('cookie')

        # Set environment information for wsgi app
        environ = {}
        environ['REQUEST_METHOD'] = method
        environ['PATH_INFO'] = path
        environ['QUERY_STRING'] = query

        # Add CONTENT_TYPE to environ
        if not (content_type is None):
            environ['CONTENT_TYPE'] = content_type

        # Add CONTENT_LENGTH to environ
        if not(content_length is None):
            environ['CONTENT_LENGTH'] = content_length
            content = conn.recv(1000)
            total = len(content)
            while True:
                if total >= int(content_length):
                    break
                new_content = conn.recv(1000)
                content += new_content
                total += len(new_content)
            environ['wsgi.input'] = StringIO.StringIO(content)
        else:
            content = ''
            environ['CONTENT_LENGTH'] = '0'
            environ['wsgi.input'] = StringIO.StringIO()

        # Add HTTP_COOKIE to environ
        if not(cookie_header is None):
            environ['HTTP_COOKIE'] = cookie_header

        environ['SERVER_PORT'] = str(self.port)
        environ['SCRIPT_NAME'] = ''
        environ['SERVER_NAME'] = self.host
        environ['wsgi.version'] = (1, 0)
        environ['wsgi.errors'] = stderr
        environ['wsgi.multithread'] = False
        environ['wsgi.multiprocess'] = False
        environ['wsgi.run_once'] = False
        environ['wsgi.url_scheme'] = 'http'

        # Passed into wsgi app
        def start_response(status, headers):
            conn.send('HTTP/1.0 ')
            conn.send(status)
            conn.send('\r\n')

            # Send the headers
            for header in headers:
                key, val = header
                conn.send(key + ': ' + val + '\r\n')
            conn.send('\r\n')
        result = self.app(environ, start_response)
        if result:
            for data in result:
                conn.send(data)

        conn.close()

def main():
    parser = argparse.ArgumentParser(description = 'A server with lots of interesting things')

    parser.add_argument('-A', help = 'The app to be run')
    parser.add_argument('-p', help = 'Port number on which to run server', default = random.randint(8000, 9999))
    parser.add_argument('--heroku', help = 'Heroku deployment flag',
                        action = 'store_true')
    args = parser.parse_args()

    if args.heroku:
        port = os.environ.get('PORT')
    else:
        port = args.p

    if args.A == 'myapp':
        app = make_app()
    elif args.A == 'image':
        app = imageapp.make_image_app()
    elif args.A == 'altdemo':
        quixote.demo.altdemo.create_publisher()
        app = quixote.get_wsgi_app()
    elif args.A == 'quotes':
        app = QuotesApp('quotes/quotes.txt', './quotes/html')
    elif args.A == 'chat':
        app = ChatApp('./chat/html')
    elif args.A == 'cookie':
        app = cookieapp.get_wsgi_app()
    else:
        print('App unspecified or unrecognized, running myapp')
        app = make_app()

    httpd = Server('', int(port), app)
    httpd.serve_forever()

if __name__ == '__main__':
   main()

