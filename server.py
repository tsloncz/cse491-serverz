#!/usr/bin/env python
import random
import socket
import time
from urlparse import urlparse, parse_qs
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
    parsed = urlparse(url)
    url = url.split("\n")
    url = url[0]
    url = url.split(" ")
    getPost = url[0]
    url = url[1]
    print ''
    print 'url:',url
    print "getPost:",getPost
    parsed = urlparse(url)
    path = parsed.path
    query = parsed.query
    values = parse_qs(query)
    print 'parsed.path:',path
    print 'parsed.query:',query 
    print 'values',values    
#print 'Got connection from', client_host, client_port
    conn.send('HTTP/1.0 200 OK\r\n')           #HTTP 1.0 response
    conn.send("Content-type: text/html\r\n")   #Header
    conn.send('\r\n')
    if getPost =='POST':
        conn.send("<form action='/submit' method='POST'>")
        conn.send("First Name: <input type='text' name='firstname'><br />")
        conn.send("Last Name: <input type='text' name='lastname'><br />")
        conn.send(" <input type='submit' value='Submit'></form><br />")
    elif path == '/submit':
#handle_submit(values, conn)
      fName = values.get('firstname',[''])[0]
      lName = values.get('lastname',[''])[0]
      conn.send("Hello "+fName+" "+lName+"<br / >")
    elif path == '/':
      conn.send('<a href="/content">/content</a><br />')
      conn.send('<a href="/file">/file</a><br />')
      conn.send('<a href="/image">/image</a><br />')
      conn.send("<form action='/submit' method='GET'>")
      conn.send("First Name: <input type='text' name='firstname'><br />")
      conn.send("Last Name: <input type='text' name='lastname'><br />")
      conn.send(" <input type='submit' value='Submit'></form><br />")
    elif path == '/content':
      conn.send("<h1>Content</h1>")
#conn.send(index.html)
    elif url == '/file':
      conn.send("<h1>File</h1>")
    else:
      conn.send("<h1>Image</h1>")
    conn.close()

if __name__ == '__main__':
  main()


def handle_submit(vals, conn):
    fName = vals.get('firstname',[''])[0]
    lName = vals.get('lastname',[''])[0]
    conn.send("Hello "+fName+" "+lName+"<br / >")
