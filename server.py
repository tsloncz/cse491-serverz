#!/usr/bin/env python
import random, socket, time
import urlparse
from app import make_app
import cStringIO

# import quixote
# #from quixote.demo import create_publisher
# from quixote.demo.mini_demo import create_publisher
# # from quixote.demo.altdemo import create_publisher
# _the_app = None

# def make_app():
# global _the_app
# if _the_app is None:
# p = create_publisher()
# _the_app = quixote.get_wsgi_app()

# return _the_app

# valadation stuff
# from wsgiref.validate import validator
# from wsgiref.simple_server import make_server


def handle_connection(conn):

	headers = conn.recv(1)
	while headers[-4:] != '\r\n\r\n':
	  headers += conn.recv(1)

	# get the fields for environ
	conn_data 			= headers.split()
	req_method			= conn_data[0]
	path_with_query 	= conn_data[1]
	path_parse 		= urlparse.urlparse(path_with_query)
	query_string 		= path_parse.query
	path 				= path_parse.path
	content_type 		= ''
	content_length 	= 0

	header_lines = headers.split('\r\n')
	for s in header_lines:
		if 'Content-Length' in s:
			#content_length = int(s.split()[1])
			content_length = int(s.strip('Content-Length: '))
		elif 'Content-Type' in s:
			# content_type = s.split()[1]
			# leaves boundry info in content_type
			content_type = s.strip('Content-Type: ')

	content = ''
	if req_method == 'POST':
		for i in range(content_length):
			content += conn.recv(1)


	wsgi_input = cStringIO.StringIO(content)
	port = 0

	environ = {}
	environ['REQUEST_METHOD'] = req_method
	environ['PATH_INFO']			= path
	environ['QUERY_STRING'] 	= query_string
	environ['SCRIPT_NAME'] 		= ''
	environ['CONTENT_TYPE'] 	= content_type
	environ['CONTENT_LENGTH'] 	= str(content_length)
	environ['wsgi.input'] 		= wsgi_input
	# added after validation below this
	environ['SERVER_NAME'] 		= "tsloncz's server"
	environ['SERVER_PORT'] 		= str(port)
	environ['wsgi.version'] 	= (1, 0)
	environ['wsgi.errors'] 		= cStringIO.StringIO()
	environ['wsgi.multithread'] 	= False
	environ['wsgi.multiprocess']	= False
	environ['wsgi.run_once'] 		= False
	environ['wsgi.url_scheme'] 	= 'http'



	def start_response(status, response_headers):
	  conn.send('HTTP/1.0 ')
	  conn.send(status)
	  conn.send('\r\n')
	  for k, v in response_headers:
		       conn.send(k)
		       conn.send(v)
	  conn.send('\r\n\r\n')

	wsgi_app = make_app()

	output = wsgi_app( environ, start_response )

	for line in output:
		conn.send( line )

	conn.close()

def main():
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
