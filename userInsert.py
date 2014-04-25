#insert an image into the database.

import sqlite3

# connect to the already existing database
db = sqlite3.connect('images.sqlite')

# configure to allow binary insertions
db.text_factory = bytes


# insert!
db.execute('INSERT INTO users (username, password ) VALUES '
    '(?,?)', ("tim","timtim"))
db.commit()

