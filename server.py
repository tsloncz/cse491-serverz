#!/usr/bin/env python
import random, socket, time
import urlparse
import StringIO
from app import make_app


def handle_connection(conn):

    initialHeaders = conn.recv(1)
    
    while initialHeaders[-4:] != '\r\n\r\n':
        initialHeaders += conn.recv(1)
    
    conn_data     = initialHeaders.split()
    req_method    = conn_data[0]
    path_with_query = conn_data[1]
    path_parse      = urlparse.urlparse(path_with_query)
    query_string    = path_parse.query
    path            = path_parse.path
    content_type    = ''
    content_length  = 0
    
    headerLines = initialHeaders.split('\r\n')
    for i in headerLines:
        if 'Content-Length' in i:
            content_length = int(i.strip("Content-Length: "))
        elif 'Content-Type' in i:
            content_type = i.strip('Content-Type: ')
    
    content = ''
    if req_method == 'POST':
        for i in range(content_length):
              content += conn.recv(1)
    wsgi_input = StringIO.StringIO(content)

    environ = {}

    environ['REQUEST_METHOD']  = req_method
    environ['PATH_INFO']       = path
    environ['QUERY_STRING']    = query_string
    environ['SCRIPT_NAME']     = ''
    environ['CONTENT_TYPE']    = content_type
    environ['CONTENT_LENGTH']  = content_length
    environ['wsgi.input']      = wsgi_input
    print 'environ: ', environ

    def start_response( status, response_headers ):
      conn.send('HTTP/1.0 %s\r\n' % status)
      for header in response_headers:
          conn.send('%s: %s\r\n' % header)
      conn.send('\r\n')
    
    wsgi_app = make_app()
    output = wsgi_app( environ, start_response )
    conn.send(output)
      
    conn.close()

def main():
    s = socket.socket() # Create a socket object
    host = socket.getfqdn() # Get local machine name
    port = random.randint(8000, 9999)
    s.bind((host, port)) # Bind to the port

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
