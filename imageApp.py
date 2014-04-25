import urlparse
import jinja2
import cgi
import time
import StringIO
import Cookie
import sqlite3
import uuid
import threading
from app import render_template, file_contents

# UUID hex to username mapping
sessions = {}

# How long a user has before being their session is over, in seconds
session_timeout = 600.0

# Lock for writing to sessions
update_sessions_rlock = threading.RLock()

# Gets called by timer to end user's session
def update_sessions(uuid_hex):
    with update_sessions_rlock:
        del sessions[uuid_hex]

def image_app(environ, start_response):
    method = environ['REQUEST_METHOD']
    path = environ['PATH_INFO']
    query_string = environ['QUERY_STRING']
    redirect = False
    # Set up jinja2
    loader = jinja2.FileSystemLoader('./templates/imageApp')
    env = jinja2.Environment(loader=loader)

    redirect_urls = ['/_image_upload', '/_login', '/_logout', '/_signup',
                     '/_latest_image']
    static_urls = ('/submit', '/login', '/signIn')

    db = sqlite3.connect('images.sqlite')
    db.text_factory = bytes
    c = db.cursor()

    # Our URL is one that will redirect to another when finished
    if path in redirect_urls or path.startswith('/_delete_image'):
        # Get content
        if 'CONTENT_TYPE' in environ:
            content_type = environ['CONTENT_TYPE']
            content_length = int(environ['CONTENT_LENGTH'])
            content = environ['wsgi.input'].read(content_length)

        if path == '/_image_upload':
            headers = {}
            for key, val in environ.iteritems():
                headers[key.lower().replace('_', '-')] = val
            fs = cgi.FieldStorage(fp=StringIO.StringIO(content),
                                  headers = headers, environ = environ)
            filename = fs['file'].filename
            image_type = filename.split('.')[-1]

            if image_type in {'png', 'jpg', 'tiff', 'jpeg'}:
                # data to be inserted into database
                r = fs['file'].value
                f = fs['file'].filename
                d = fs['description'].value
                if 'HTTP_COOKIE' in environ:
                    current_user_uuid_hex = environ['HTTP_COOKIE'].split('=')[-1]
                    current_user = sessions[current_user_uuid_hex]

                c.execute('SELECT uid FROM users WHERE username=?',
                          (current_user,))

                uid, = c.fetchone()

                # insert image into database
                db.execute('INSERT INTO image_store '
                           '(image, name, description, user_id) '
                           'VALUES (?, ?, ?, ?)',
                           (r, f, d, uid))
                db.commit()
            
                start_response('302 Moved Temporarily',
                           [('Content-type', 'text/html'),
                            ('Location', '/')])

        elif path == '/_login':
            parsed_query = urlparse.parse_qs(content)
            username = parsed_query['username'][0]
            password = parsed_query['password'][0]

            c.execute('SELECT username FROM users WHERE username=? '
                      'AND password=?', (username, password))
            user = c.fetchone()

            if user:
                user, = user
                uuid_hex = uuid.uuid4().hex
                with update_sessions_rlock:
                    sessions[uuid_hex] = user
                threading.Timer(session_timeout, update_sessions,
                                args=[uuid_hex]).start()
                start_response('302 Moved Temporarily',
                               [('Content-type', 'text/html'),
                                ('Set-Cookie', 'user=' + uuid_hex),
                                ('Location', '/')])
            else:
                start_response('302 Moved Temporarily',
                               [('Content-type', 'text/html'),
                                ('Location', '/')])

        elif path == '/_signup':
            parsed_query = urlparse.parse_qs(content)
            username = parsed_query['username'][0]
            password = parsed_query['password'][0]
            password_confirm = parsed_query['password_confirm'][0]

            if password == password_confirm:
                # Add user to database
                db.execute('INSERT INTO users (username, password) '
                           'VALUES (?, ?)', (username, password))
                db.commit()

                uuid_hex = uuid.uuid4().hex
                with update_sessions_rlock:
                    sessions[uuid_hex] = username
                threading.Timer(session_timeout, update_sessions,
                                args=[uuid_hex]).start()
                start_response('302 Moved Temporarily',
                               [('Content-type', 'text/html'),
                                ('Set-Cookie', 'user=' + uuid_hex),
                                ('Location', '/')])


        elif path == '/_logout':
             start_response('302 Moved Temporarily',
                           [('Content-type', 'text/html'),
                            ('Set-Cookie', 'user=logout; expires=Thu, '
                                           '01 Jan 1970 00:00:00 GMT'),
                            ('Location', '/')])


        elif path.startswith('/_latest_image'):
            # Get iid of most recent image
            c.execute('SELECT iid FROM image_store ORDER BY iid DESC LIMIT 1')
            iid, = c.fetchone()
            start_response('302 Moved Temporarily',
                           [('Content-type', 'text/plain'),
                            ('Location', '/image_raw/' + str(iid))])

        elif path.startswith('/_delete_image'):
            image_no = path.lstrip('/_delete_image/')

            # Delete image with iid=image_no
            c.execute('DELETE FROM image_store WHERE iid=?', (image_no,))
            db.commit()

            start_response('302 Moved Temporarily',
                           [('Content-type', 'text/html'),
                            ('Location', '/myImages')])

        return None
 
    # These URLs will not redirect
    else:
        # jinja variables
        vars = {}
        if 'HTTP_COOKIE' in environ:
            current_user_uuid_hex = environ['HTTP_COOKIE'].split('=')[-1]
            if current_user_uuid_hex in sessions:
                logged_in = True
                current_user = sessions[current_user_uuid_hex]
                vars['login_status'] = 'Logged in as '
                vars['login_status'] += current_user
                vars['login_status'] += '. <a href=\'_logout\'>Logout</a>'
            else:
                start_response('302 Moved Temporarily',
                              [('Content-type', 'text/html'),
                               ('Set-Cookie', 'user=logout; expires=Thu, '
                                '01 Jan 1970 00:00:00 GMT'),
                               ('Location', '/')])
                return None

        else:
            logged_in = False
            vars['login_status'] = 'You are not current logged in. '
            vars['login_status'] += '<a href=\'login\'>Login</a> | '
            vars['login_status'] += '<a href=\'signup\'>Signup</a>'

        if path in static_urls:
            start_response('200 OK', [('Content-type', 'text/html')])
            ret = render_template(env, path.lstrip('/') + '.html', vars)

        else:
            if path == '/':
                print "path = /"
                c.execute('SELECT iid, name, description, username FROM '
                          'image_store, users WHERE uid=user_id '
                          'ORDER BY iid DESC LIMIT 1')
                iid, name, description, upload_user = c.fetchone()

                vars['name'] = name
                vars['description'] = description
                vars['upload_user'] = upload_user
                vars['time'] = time.time()
                if logged_in:
                    vars['links'] = '<p><a href=\'submit\'>Submit an Image</a>'
                    vars['links'] += ' | <a href=\'myImages\'>My Images</a></p>'
                else:
                    vars['links'] = ''

                start_response('200 OK', [('Content-type', 'text/html')])
                ret = render_template(env, 'index.html', vars)
                
            elif path.startswith('/image_raw/'):
                image_no = path.lstrip('/image_raw/')

                # select image with iid=image_no
                c.execute('SELECT image, name FROM image_store '
                          'WHERE iid=?', (image_no,))

                image, name = c.fetchone()

                start_response('200 OK', [('Content-type',
                               'image/' + name.split('.')[-1])])
                ret = image

            elif path == '/myImages':
                c.execute('SELECT iid, name, description FROM '
                          'image_store, users WHERE user_id=uid AND '
                          'username=?', (current_user,))

                image_links = ''
                for row in c.fetchall():
                    iid, name, description = row
                    image_links += '<p>Name: ' + name + '<br/>'
                    image_links += 'Description: ' + description + '<br/>'
                    image_links += '<a href=\'_delete_image/' + str(iid) + '\'>'
                    image_links += 'Delete Image</a></p>'
                    image_links += '<a href=\'image_raw/' + str(iid) + '\'>'
                    image_links += '<img src=\'image_raw/' + str(iid) + '\' '
                    image_links += 'width="100" height="100"/></a>'
                pass

                vars['image_links'] = image_links
                start_response('200 OK', [('Content-type', 'text/html')])
                ret = render_template(env, 'myImages.html', vars)

            else:
                start_response('200 OK', [('Content-type', 'text/html')])
                return None
            
        # Needs to be a single-entry list for wsgi compliance
        return [ret]

def make_image_app():
    return image_app
