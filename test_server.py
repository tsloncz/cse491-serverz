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
    expected_return = "HTTP/1.0 200 OK\r\n" +\
                      "Content-type: text/html\r\n\r\n" +\
                      "<html>\n<body>\n\n\n<h1>Hello, world.</h1><br>\n" +\
                      "This is tsloncz's Web server.<br>\n" +\
                      "<a href='/content'>Content</a><br>\n" +\
                      "<a href='/file'>Files</a><br>\n" +\
                      "<a href='/image'>Images</a><br>\n" +\
                      "<a href='/form'>Form</a><br>\n\n\n</body>\n</html>" 

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_connection_content():
    conn = FakeConnection("GET /content HTTP/1.0\r\n\r\n")
    expected_return = "HTTP/1.0 200 OK\r\n" +\
                      "Content-type: text/html\r\n\r\n" +\
                      "<html>\n<body>\n\n\n<h1>Content Page</h1><br>\n" +\
                      "<a href='/'>home</a><br>\n\n\n</body>\n</html>"

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_connection_image():
    conn = FakeConnection("GET /image HTTP/1.0\r\n\r\n")
    expected_return = "HTTP/1.0 200 OK\r\n" +\
                      "Content-type: text/html\r\n\r\n" +\
                      "<html>\n<body>\n\n\n<h1>Images</h1><br>\n" +\
                      "<a href='/'>home</a><br>\n\n</body>\n</html>"
    
    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_connection_submit_get():
    conn = FakeConnection("GET /submit?firstname=R2&lastname=D2 +\
        HTTP/1.0\r\n\r\n")
    expected_return = "HTTP/1.0 200 OK\r\n" +\
                      "Content-type: text/html\r\n\r\n" +\
                      "<html>\n<body>\n\n\nHello Mr/Ms R2 D2.<br>\n" +\
                      "<a href='/'>home</a><br>\n\n\n</body>\n</html>"

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_connection_form():
    conn = FakeConnection("GET /form +\
        HTTP/1.0\r\n\r\n")
    expected_return = "HTTP/1.0 200 OK\r\n" +\
                      "Content-type: text/html\r\n\r\n" +\
                      "<html>\n<body>\n\n\n<form action=\'/submit\'" +\
                      "method=\'POST\' enctype='multipart/form-data'>\n" +\
                      "First name:\n<input type=\'text" +\
                      "\'name=\'firstname\'>\nLast name:\n" +\
                      "<input type=\'text\' name=\'lastname\'>\n" +\
                      "<input type=\'submit\'>\n</form>\n\n\n</body>\n</html>"

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_connection_submit_post_urlencode():
    conn = FakeConnection("POST /submit  +\
        HTTP/1.0\r\n +\
        Content-Type: application/x-www-form-urlencoded\r\n +\
        Content-Length: 26\r\n +\
        \r\nfirstname=R2&lastname=D2")
    expected_return = "HTTP/1.0 200 OK\r\n" +\
                      "Content-type: text/html\r\n\r\n" +\
                      "<html>\n<body>\n\n\nHello Mr/Ms R2 D2.<br>\n" +\
                      "<a href='/'>home</a><br>\n\n\n</body>\n</html>"

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_connection_submit_post_multi():
    conn = FakeConnection('POST /submit HTTP/1.1\r\nHost: arctic.cse.msu.edu:8614\r\nConnection: keep-alive\r\nContent-Length: 241\r\nCache-Control: max-age=0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nOrigin: http://arctic.cse.msu.edu:8614\r\nUser-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundaryZvAjeyANv4ugV83R\r\nReferer: http://arctic.cse.msu.edu:8614/form\r\nAccept-Encoding: gzip,deflate,sdch\r\nAccept-Language: en-US,en;q=0.8\r\nCookie: __utma=51441333.903583318.1382538374.1382538374.1382538374.2; __utmc=51441333; __utmz=51441333.1382538374.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __unam=453ac6a-14262b14268-18ca21ca-5; _ga=GA1.2.554274197.1379381990\r\n\r\n------WebKitFormBoundaryZvAjeyANv4ugV83R\r\nContent-Disposition: form-data; name="firstname"\r\n\r\nJoe\r\n------WebKitFormBoundaryZvAjeyANv4ugV83R\r\nContent-Disposition: form-data; name="lastname"\r\n\r\nMan\r\n------WebKitFormBoundaryZvAjeyANv4ugV83R--\r\n')
    expected_return = "HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n<html>\n<body>\n\n\nHello Mr. Joe Man.\n\n\n</body>\n</html>"

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_connection_404():
    conn = FakeConnection("GET /adghj HTTP/1.0\r\n\r\n")
    expected_return = "HTTP/1.0 404 Not Found\r\n"\
        +"Content-type: text/html\r\n"\
        +"\r\n"\
        +"<html>\n<body>\n\n\n"\
        +"<h1>404</h1>\n"\
        +"This page does not exist"\
        +"\n\n\n</body>\n</html>"

    server.handle_connection(conn)

    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)
