"""Tiferet JSON utility."""

# *** imports

# ** app
from ..interfaces.file import FileService
from .file import FileLoader

# *** constants

# ** constant: invalid_json_file_id
INVALID_JSON_FILE_ID = 'INVALID_JSON_FILE'

# *** utils

# ** util: json_loader
class JsonLoader(FileLoader):
    '''
    Load JSON through the shared file stream.
    '''

    # * method: load
    def load(self):
        '''
        Load the JSON document.

        :return: The loaded document.
        :rtype: object
        '''

        # The document is the open path.
        return self
