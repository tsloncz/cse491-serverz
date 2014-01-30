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
                      'Content-type: text/html\r\n' + \
                      '\r\n' + \
                      '<a href="/content">/content</a><br />' + \
                      '<a href="/file">/file</a><br />' + \
                      '<a href="/image">/image</a><br />' +\
                      "<form action='/submit' method='GET'>" +\
                      "First Name: <input type='text' name='firstname'><br />"+\
                      "Last Name: <input type='text' name='lastname'><br />" +\
                      " <input type='submit' value='Submit'></form><br />"
    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_content():
    conn = FakeConnection("GET /content HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n' +\
                      '\r\n' + \
                      '<h1>Content</h1>' 

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_file():
    conn = FakeConnection("GET /file HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n' +\
                      '\r\n' + \
                      '<h1>File</h1>' 

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)


def test_handle_image():
    conn = FakeConnection("GET /image HTTP/1.0\r\n\r\n")
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-type: text/html\r\n' +\
                      '\r\n' + \
                      '<h1>Image</h1>' 
                
    server.handle_connection(conn)
        
    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)


def test_handle_post():
  conn = FakeConnection("POST /server.py HTTP/1.0\r\n\r\n")
  expected_return = 'HTTP/1.0 200 OK\r\n' +\
                    'Content-type: text/html\r\n' +\
                    '\r\n' +\
                    '<h1>POST!</h1>'

  server.handle_connection(conn)

  assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)


def test_handle_submit():
      conn = FakeConnection("GET /submit?firstname=r2&lastname=d2 HTTP/1.0\r\n\r\n")
      expected_return = 'HTTP/1.0 200 OK\r\n' + \
                        'Content-type: text/html\r\n' +\
                        '\r\n' + \
                        'Hello r2 d2<br / >'

      server.handle_connection(conn)

      assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)




