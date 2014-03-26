#init__.py is the top level file in a Python package.

from quixote.publish import Publisher
import sys

# this imports the class RootDirectory from the file 'root.py'

from apps import ChatApp


 
def setup(): # stuff that should be run once.
    chat_app = ChatApp('./html')
    return chat_app


    

def teardown(): # stuff that should be run once.
    pass
