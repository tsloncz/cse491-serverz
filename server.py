#!/usr/bin/env python
import random
import socket
import time
import urlparse
import signal
import cgi
import StringIO


def handle_submit(conn,url):
          query = urlparse.parse_qs(url.query)
          conn.send("Hello Mr/Ms ")
          conn.send(query['firstname'][0])
          conn.send(" ")
          conn.send(query['lastname'][0])
          conn.send('.')
          conn.send('</body></html>')

def handle_form(conn,url):
          conn.send("<form action='/submit' method='POST'>")
          conn.send("First name:")
          conn.send("<input type='text' name='firstname'>")
          conn.send("Last name:")
          conn.send("<input type='text' name='lastname'>")
          conn.send("<input type='submit'>")
          conn.send("</form>")
          conn.send('</body></html>')

def handle_root(conn, url):
          conn.send('<h1>Hello, world.</h1>')
          conn.send("This is tsloncz's Web server.<br>")
          conn.send("<a href='/content'>Content</a><br>")
          conn.send("<a href='/file'>Files</a><br>")
          conn.send("<a href='/image'>Images</a><br>")
          conn.send("<a href='/form'>Form</a><br>")
          conn.send('</body></html>')

def handle_content(conn, url):
          conn.send('<h1>Content Page</h1>')
          conn.send('</body></html>')

def handle_file(conn, url):
          conn.send('<h1>File Page</h1>')
          conn.send('Files')
          conn.send('</body></html>')

def handle_image(conn, url):
          conn.send("<h1>Image Page</h1>")
          conn.send('</body></html>')

def handle_404(conn, url):
          conn.send('HTTP/1.0 404 Not Found\r\n')
          conn.send('Content-Type: text/html\r\n\r\n')
          conn.send('<html><body>')
          conn.send('<h1>404</h1>')
          conn.send('This page does not exist')
          conn.send('</body></html>')

def handle_post(conn,content):
	  query = urlparse.parse_qs(content)
          conn.send('HTTP/1.0 200 OK\r\n')
    	  conn.send('Content-Type: text/html\r\n\r\n')
    	  conn.send('<html><body>')
    	  conn.send("Hello Mr/Ms ")
    	  conn.send(query['firstname'][0])
    	  conn.send(" ")
    	  conn.send(query['lastname'][0])
    	  conn.send('.')
    	  conn.send('</body></html>')

def handle_get( conn, url):
    path = url.path
    conn.send('HTTP/1.0 200 OK\r\n')
    conn.send('Content-Type: text/html\r\n\r\n')
    conn.send('<html><body>')
    if path == '/':
        handle_root(conn,url)
    elif path == '/form':
        handle_form(conn,url)
    elif path =='/content':
        handle_content(conn, url)
    elif path == '/submit':
        handle_submit(conn,url)
    elif path == '/file':
        handle_file(conn,url)
    elif path == '/image':
        handle_image(conn,url)
    else:
        handle_404(conn,url)

def handle_connection(conn):
    req = conn.recv(1000)
    lineSplit = req.split( '\r\n')
    req = lineSplit[0].split(' ')
    reqType = req[0]  #extract GET or POS
    
    if reqType == 'GET':  
        path = req[1]
        url = urlparse.urlparse(path)
        handle_get(conn, url)
    elif reqType == 'POST':
        content = lineSplit[-1]
        print req
        handle_post(conn,content)
#print 'Got connection from', client_host, client_port
    conn.close()

def main():
      s = socket.socket()         # Create a socket object
      host = socket.getfqdn() # Get local machine name
      port = random.randint(8000, 9999)
      s.bind((host, port))        # Bind to the port

      print 'Starting server on', host, port
      print 'The Web server URL for this would be http://%s:%d/' %(host, port)

      s.listen(5)                 # Now wait for client connection.

      print 'Entering infinite loop; hit CTRL-C to exit'
      while True:
          # Establish connection with client.    
          c, (client_host, client_port) = s.accept()
          print 'Got connection from', client_host, client_port
          handle_connection(c)

if __name__ == '__main__':
  main()


