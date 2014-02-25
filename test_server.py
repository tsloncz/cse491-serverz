import server
import jinja2

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
    # this will test the index page
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-typetext/html\r\n' + \
                      '\r\n' + \
                      "<html>\n<title>tsloncz's server</title>" + \
                      "\n<body>\n\n\n"+ \
							 "<h1>Hello, world.</h1><br>\nThis is tsloncz's Web server.<br>\n" + \
                      "<a href='/content'>Content</a><br>\n" + \
                      "<a href='/file'>Files</a><br>\n" + \
                      "<a href='/image'>Images</a><br>\n" +\
							 "<a href='/form'>Form</a><br>\n\n\n" +\
                      "</body>\n</html>"
    server.handle_connection(conn)

    print "\nexpected_return is ", (expected_return, )

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_send_index():
    conn = FakeConnection("GET / HTTP/1.0\r\n\r\n")
    # this will test the index page
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-typetext/html\r\n' + \
                      '\r\n' + \
                      "<html>\n<title>tsloncz's server</title>" + \
                      "\n<body>\n\n\n"+ \
							 "<h1>Hello, world.</h1><br>\nThis is tsloncz's Web server.<br>\n" + \
                      "<a href='/content'>Content</a><br>\n" + \
                      "<a href='/file'>Files</a><br>\n" + \
                      "<a href='/image'>Images</a><br>\n" +\
							 "<a href='/form'>Form</a><br>\n\n\n" +\
                      "</body>\n</html>"
    server.handle_connection(conn)

    print "\nexpected_return is ", (expected_return, )

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_send_content():
    conn = FakeConnection("GET /content HTTP/1.0\r\n\r\n")
    expected_return = "HTTP/1.0 200 OK\r\n" + \
                      "Content-typetext/html\r\n\r\n" + \
                      "<html>\n<title>tsloncz's server</title>\n" + \
                      "<body>\n\n\n<h1>Content Page</h1><br>\n"+ \
							 "<a href='/'>home</a><br>\n\n\n</body>\n</html>"
    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_send_file():
    conn = FakeConnection("GET /file HTTP/1.0\r\n\r\n")
    # this will test the index page
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-typetext/plain\r\n' + \
                      '\r\n' + \
                      "<html>\n<title>tsloncz's server</title>" + \
                      "\n<body>\n\n\n"+ \
           '<h1>This is the file page</h1>' + \
                      "\n\n\n</body>\n</html>"
    server.handle_connection(conn)

    print "\nexpected_return is ", (expected_return, )

    # assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)
    assert '200 OK\r\nContent-typetext/plain' in conn.sent

def test_send_image():
    conn = FakeConnection("GET /image HTTP/1.0\r\n\r\n")
    # this will test the index page
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-typeimage/jpeg\r\n' + \
                      '\r\n' + \
                      "<html>\n<title>tsloncz's server</title>" + \
                      "\n<body>\n\n"+ \
'<h1>This is the image page</h1>' + \
                      "\n\n\n</body>\n</html>"
    server.handle_connection(conn)

    print "\nexpected_return is ", (expected_return, )

    # assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)
    assert '200 OK\r\nContent-typeimage/jpeg' in conn.sent

def test_send_form():
    conn = FakeConnection("GET /form HTTP/1.0\r\n\r\n")
    # this will test the index page
    expected_return = "HTTP/1.0 200 OK\r\n" + \
          "Content-typetext/html\r\n\r\n" + \
          "<html>\n<title>tsloncz's server</title>\n<body>\n\n\n" + \
          "<form action='/submit' method='POST' enctype='multipart/form-data'>\n" + \
          "First name:\n<input type='text' name='firstname'>\n"+ \
          "Last name:\n<input type='text' name='lastname'>\n"+ \
          "<input type='submit'>\n</form>\n\n\n"+ \
          "</body>\n</html>" 
          
    server.handle_connection(conn)

    print '\n\nexpected_return', (expected_return, )

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)


def test_send_404():
    conn = FakeConnection("GET /nothere HTTP/1.0\r\n\r\n")
    expected_return = "HTTP/1.0 404 Not Found\r\n" + \
                      "Content-typetext/html\r\n\r\n" + \
                      "<html>\n<title>tsloncz's server</title>\n" + \
                      "<body>\n\n\n<h1>404</h1>\n"+ \
							 "This page does not exist<br>\n" + \
                      "<a href='/'>Back</a><br>\n\n</body>\n</html>"
    server.handle_connection(conn)

    print '\n\nexpected_return', (expected_return, )

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_not_found_POST():
    conn = FakeConnection("POST / HTTP/1.0\r\n\r\n")
    # this will test the index page
    expected_return = "HTTP/1.0 404 Not Found\r\n" +\
							 "Content-typetext/html\r\n\r\n" +\
							 "<html>\n<title>tsloncz's server</title>\n" +\
							 "<body>\n\n\n<h1>404</h1>\nThis page does not exist<br>\n" +\
							 "<a href='/'>Back</a><br>\n\n</body>\n</html>"
    server.handle_connection(conn)

    print '\n\nexpected_return', (expected_return, )

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_GET_submit():
    conn = FakeConnection("GET /submit?firstname=R2&lastname=D2 HTTP/1.0\r\n\r\n")
    expected_return = "HTTP/1.0 200 OK\r\n" +\
							 "Content-typetext/html\r\n\r\n" +\
							 "<html>\n<title>tsloncz's server</title>\n" +\
							 "<body>\n\n\nHello Mr/Ms R2 D2.<br>\n" +\
							 "<a href='/'>home</a><br>\n\n\n</body>\n</html>"
    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)


def test_POST_app_type():
    conn = FakeConnection("POST /submit HTTP/1.0\r\n" +\
      "Content-Length: 200\r\n"
      "Content-Type: application/x-www-form-urlencoded\r\n\r\n"+\
      "firstname=r2&lastname=d2")
    expected_return = "HTTP/1.0 200 OK\r\n" +\
							 "Content-typetext/html\r\n\r\n" +\
							 "<html>\n<title>tsloncz's server</title>\n" +\
							 "<body>\n\n\nHello Mr/Ms r2 d2.<br>\n" +\
							 "<a href='/'>home</a><br>\n\n\n</body>\n</html>"

    server.handle_connection(conn)
    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_POST_multi_type():
    conn = FakeConnection('POST /submit HTTP/1.1\r\nHost: localhost.localdomain:9945\r\n' +\
      'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0\r\n' +\
      'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n' +\
      'Accept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\n' +\
      'Referer: http://localhost.localdomain:9945/form\r\nConnection: keep-alive\r\n'+ \
      'Content-Type: multipart/form-data; boundary=---------------------------1392556327' + \
      '694557745636086249\r\nContent-Length: 296\r\n\r\n-----------------------------1392' +\
      '556327694557745636086249\r\nContent-Disposition: form-data; name="firstname"\r\n\r\n' +\
      'fancy\r\n-----------------------------1392556327694557745636086249\r\n' +\
      'Content-Disposition: form-data; name="lastname"\r\n\r\npants\r\n--------' +\
      '---------------------1392556327694557745636086249--\r\n')
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-typetext/html\r\n' + \
                      '\r\n' + \
                      "<html>\n<title>tsloncz's server</title>" + \
                      "\n<body>\n\n\n"+ \
                      '<h1>Hello Mr. fancy pants.</h1>' + \
                      "\n\n\n</body>\n</html>"
    server.handle_connection(conn)

    print '\n\n\n\nexpected_return is ', (expected_return,)
    
    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_POST_multi_type_BAD():
    #tests if there is an exception in the form data
    conn = FakeConnection('POST /submit HTTP/1.1\r\nHost: localhost.localdomain:9945\r\n' +\
      'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0\r\n' +\
      'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n' +\
      'Accept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\n' +\
      'Referer: http://localhost.localdomain:9945/form\r\nConnection: keep-alive\r\n'+ \
      'Content-Type: multipart/form-data; boundary=---------------------------1392556327' + \
      '694557745636086249\r\nContent-Length: 296\r\n\r\n-----------------------------1392' +\
      '556327694557745636086249\r\nContent-Disposition: form-data; name="not_firstname"\r\n\r\n' +\
      'r2\r\n-----------------------------1392556327694557745636086249\r\n' +\
      'Content-Disposition: form-data; name="not_lastname"\r\n\r\nd2\r\n--------' +\
      '---------------------1392556327694557745636086249--\r\n')
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-typetext/html\r\n' + \
                      '\r\n' + \
                      "<html>\n<title>This is tsloncz's server</title>\n" + \
                      "<body>\n\n\n<h1>Hello Mr. .</h1>\n\n\n</body>\n</html>"
    server.handle_connection(conn)

    print '\n\n\n\nexpected_return is ', (expected_return,)
    
    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_normal_POST():
    conn = FakeConnection("POST /not_submit HTTP/1.0\r\n" +\
                          "Content-Length: 200\r\n"
                          "Content-Type: application/x-www-form-urlencoded\r\n\r\n")
    
    expected_return = 'HTTP/1.0 200 OK\r\n' + \
                      'Content-typetext/html\r\n' + \
                      '\r\n' + \
                      "<html>\n<title>tsloncz's server</title>" + \
                      "\n<body>\n\n\n"+ \
                      '<h1>Hello, POST</h1>' + \
                      "\n\n\n</body>\n</html>"
    server.handle_connection(conn)

    print '\n\n\n\nexpected_return is ', (expected_return,)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)
