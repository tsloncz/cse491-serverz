import server

class FakeConnection(object):
    """
    A fake connection class that mimics a real TCP socket for the purpose
    of testing socket I/O.
    """
    def __init__(self, to_recv):
        self.to_recv = to_recv
        self.sent = ""
        self.is_closed = False

    def recv(self, n):
        if n > len(self.to_recv):
            r = self.to_recv
            self.to_recv = ""
            return r
            
        r, self.to_recv = self.to_recv[:n], self.to_recv[n:]
        return r

    def send(self, s):
        self.sent += s

    def close(self):
        self.is_closed = True

# Test a basic GET call.

def test_handle_connection():
    conn = FakeConnection("GET / HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n\r\n' + \
                      '<html><body><h1>Hello, world.</h1>' +\
                      'This is tsloncz\'s Web server.<br>' +\
                      '<a href="/content">/Content</a><br>' + \
                      '<a href="/file">/Files</a><br>' + \
                      '<a href="/image">/Images</a><br>' +\
                      "<a href='/form'>Form</a><br></body></html>"

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_content():
    conn = FakeConnection("GET /content HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n\r\n' + \
                      '<html><body><h1>Content Page</h1></body></html>' 

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_file():
    conn = FakeConnection("GET /file HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n\r\n' + \
                      '<html><body><h1>File Page</h1>' +\
                      'Files</body></html>' 

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)


def test_handle_image():
    conn = FakeConnection("GET /image HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n\r\n' + \
                      '<html><body><h1>Image Page</h1></body></html>'
                
    server.handle_connection(conn)
        
    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)


def test_handle_connection_submit_get():
	conn = FakeConnection("GET /submit?firstname=R2&lastname=D2 "\
       	 +"HTTP/1.0\r\n\r\n")
	expected_return = "HTTP/1.0 200 OK\r\n"\
       	 +"Content-type: text/html\r\n\r\n"\
       	 +"<html><body>"\
       	 +"Hello Mr/Ms R2 D2."\
       	 +"</body></html>"

	server.handle_connection(conn)

    	assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_submit_post():
	conn = FakeConnection("POST /submit "\
      	  +"HTTP/1.0\r\n\r\n"\
      	  +"firstname=R2&lastname=D2")
	expected_return = "HTTP/1.0 200 OK\r\n"\
       	 +"Content-type: text/html\r\n\r\n"\
       	 +"<html><body>"\
       	 +"Hello Mr/Ms R2 D2."\
         +"</body></html>"

	server.handle_connection(conn)

	assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)




