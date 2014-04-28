#insert an image into the database.

import sqlite3

# connect to the already existing database
db = sqlite3.connect('images.sqlite')

# configure to allow binary insertions
db.text_factory = bytes

# grab whatever it is you want to put in the database
r = open('dog.jpg', 'rb').read()

# insert!
db.execute('INSERT INTO image_store (image, name, description, user_id) VALUES '
    '(?,?,?,?)', (r,"dog.jpg","awesome dog","tim"))

db.execute('INSERT INTO image_store (image, name, description, user_id) VALUES '
    '(?,?,?,?)', (r,"dog.jpg","awesome dog","you"))
db.commit()
