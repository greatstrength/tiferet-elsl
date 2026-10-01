"""Tiferet YAML utility."""

# *** imports

# ** app
from ..interfaces.file import FileService
from .file import FileLoader

# *** constants

# ** constant: invalid_yaml_file_id
INVALID_YAML_FILE_ID = 'INVALID_YAML_FILE'

# *** utils

# ** util: yaml_loader
class YamlLoader(FileLoader):
    '''
    Load YAML through the shared file stream.
    '''

    # * method: load
    def load(self):
        '''
        Load the YAML document.

        :return: The loaded document.
        :rtype: object
        '''

        # The document is the open path.
        return self
