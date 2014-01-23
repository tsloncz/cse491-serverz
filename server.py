#!/usr/bin/env python
import random
import socket
import time
#for hw2 use 4 test functions

def main():
  s = socket.socket()         # Create a socket object
  host = socket.getfqdn()     # Get local machine name
  port = random.randint(8000, 9999)
  s.bind((host, port))        # Bind to the port

  print 'Starting server on', host, port
  print 'The Web server URL for this would be http://%s:%d/' % (host, port)

  s.listen(5)                 # Now wait for client connection.

  print 'Entering infinite loop; hit CTRL-C to exit'
  while True:
    # Establish connection with client.
    c, (client_host, client_port) = s.accept()  
    handle_connection(c)

def handle_connection(conn):
    url = conn.recv(1000)
    url = url.split("\n")
    url = url[0]
    url = url.split(" ")
    getPost = url[0]
    url = url[1]
    print 'url:',url,"getPost:",getPost
    #print 'Got connection from', client_host, client_port
    conn.send('HTTP/1.0 200 OK\r\n')               #HTTP 1.0 response
    conn.send("Content-type: text/html\r\n")   #Header
    conn.send('\r\n')
    conn.send('<h1>Hello, world.</h1>')
    conn.send('This is tsloncz\'s Web server.<br />')
    if getPost =='POST':
      conn.send('<h1>POST!</h1>')
    elif url == '/':
      conn.send('<a href="/content">/content</a><br />')
      conn.send('<a href="/file">/file</a><br />')
      conn.send('<a href="/image">/image</a><br />')
    elif url == '/content':
      conn.send("<h1>Content</h1>")
    elif url == '/file':
      conn.send("<h1>File</h1>")
    else:
      conn.send("<h1>Image</h1>")
    conn.close()

if __name__ == '__main__':
  main()
