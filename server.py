#!/usr/bin/env python
import random, socket, time
import urlparse
import cgi
import jinja2

from StringIO import StringIO

def handle_submit(conn,url,env):
    query = urlparse.parse_qs(url.query)
    conn.send('HTTP/1.0 200 OK\r\n')
    conn.send('Content-type: text/html\r\n\r\n')
    vars = dict(firstname = query['firstname'][0],lastname = query['lastname'][0])
    conn.send(env.get_template("submit.html").render(vars))
def handle_form(conn,url,env):
    conn.send('HTTP/1.0 200 OK\r\n')
    conn.send('Content-type: text/html\r\n\r\n')
    conn.send(env.get_template('form.html').render())

def handle_root(conn, url,env):
    conn.send('HTTP/1.0 200 OK\r\n')
    conn.send('Content-type: text/html\r\n\r\n')
    conn.send(env.get_template('index.html').render())

def handle_content(conn, url,env):
    conn.send('HTTP/1.0 200 OK\r\n')
    conn.send('Content-type: text/html\r\n\r\n')
    conn.send(env.get_template('content.html').render())

def handle_file(conn, url,env):
    conn.send('HTTP/1.0 200 OK\r\n')
    conn.send('Content-type: text/html\r\n\r\n')
    conn.send(env.get_template('file.html').render())
def handle_image(conn, url,env):
    conn.send('HTTP/1.0 200 OK\r\n')
    conn.send('Content-type: text/html\r\n\r\n')
    conn.send(env.get_template('image.html').render())
def handle_404(conn, url, env):
    conn.send('HTTP/1.0 404 Not Found\r\n')
    conn.send('Content-type: text/html\r\n\r\n')
    conn.send(env.get_template("404.html").render())

def handle_get(conn, url, env):
    path = url.path
    if path == '/':
        handle_root(conn,url,env)
    elif path == '/form':
        handle_form(conn,url,env)
    elif path == '/submit':
        handle_submit(conn,url,env)
    elif path == '/content':
        handle_content(conn, url,env)
    elif path == '/file':
        handle_file(conn, url,env)
    elif path == '/image':
        handle_image(conn, url,env)
    else:
        handle_404(conn,url,env)

def handle_post(conn,content,env):
    conn.send('HTTP/1.0 200 OK\r\n')
    conn.send('Content-type: text/html\r\n\r\n')
    conn.send(env.get_template("submit.html").render(content))
def read_head(conn):
    message = ''
    while '\r\n\r\n' not in message:
        message += conn.recv(1)
    return message.rstrip()

def handle_connection(conn):
    loader = jinja2.FileSystemLoader('./templates')
    env = jinja2.Environment(loader=loader)


    rawHead = read_head(conn)
    headList = rawHead.split('\r\n')
    contentType = [s for s in headList if 'Content-Type' in s]
    req = headList[0].split(' ')
    reqType = req[0]
    if reqType == 'GET':
        path = req[1]
        url = urlparse.urlparse(path)
        handle_get(conn, url, env)
    elif reqType == 'POST':
        requestLine, raw_headers = rawHead.split('\r\n',1)
        headers = raw_headers.split('\r\n')

        headDict = {}
        for line in headers:
            k, v = line.split(': ', 1)
            headDict[k.lower()] = v

        content = conn.recv(int(headDict['content-length']))
        contentType = headDict['content-type']

        if contentType == 'application/x-www-form-urlencoded':
            content = urlparse.parse_qs(content)
            content['firstname'] = content['firstname'][0]
            content['lastname'] = content['lastname'][0]
        elif 'multipart/form-data' in contentType:
            environ = {}
            environ['REQUEST_METHOD'] = 'POST'

            form = cgi.FieldStorage(headers=headDict, fp=StringIO(content), environ=environ)

            content = {}
            content['firstname'] = form['firstname'].value
            content['lastname'] = form['lastname'].value
        handle_post(conn,content,env)
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
