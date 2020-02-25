#!/usr/bin/env python3

"""Python script meant to automate the creation of numpy-style docstrings.  

Designed to be used to autocreate base np docs for python projects,
that are then used to create markdown docs for mkdocs with the npdoc2md
script.  

@author: Jakub Wlodek  
@created: Feb-25-2020
"""

# Some standard lib imports
import os
import sys
import shutil
import argparse
import logging

# Import typing to use python3 typing features
from typing import List
StringList = List[str]

# Current script version
__version__     = '0.0.1'
__copyright__   = '2020'
__author__      = 'Jakub Wlodek'
__url__         = 'https://github.com/jwlodek/npdoc2md'


# Descriptors possible in docstrings, used for tables
docstring_descriptors = {
    'Classes'       : ['Class',             'Doc'],
    'Functions'     : ['Function',          'Doc'],
    'Attributes'    : ['Attribute',         'Type', 'Doc'],
    'Methods'       : ['Method',            'Doc'],
    'Returns'       : ['Return Variable',   'Type', 'Doc'],
    'Parameters'    : ['Parameter',         'Type', 'Doc'],
}


class DocStringAttribute:

    def __init__(self, attribute_name : str):
        self.attribute_name = attribute_name
        self.attribute_elements = []

class GenerationInstance:

    def __init__(self, name):
        self.name = name
        self.descriptors = []

class ClassGenerationInstance(GenerationInstance):

    def __init__(self, name):
        super().__init__(name)

class FunctionGenerationInstance(GenerationInstance):

    def __init__(self, name):
        super().__init__(name)

class ModuleGenerationInstance(GenerationInstance):

    def __init__(self, name, original_module_text):
        super().__init__(name)
        self.original_module_text = original_module_text



class GenerationItem:

    def __init__(self, target_file_path : os.PathLike, overwrite):
        self.target = target_file_path
        self.overwrite = overwrite
        self.temp_file = os.path.join(os.dirname(self.target), '__code2npdoc_temp__')
        self.module_gen_instance = self.create_module_gen_instance()


    def create_module_gen_instance(self) -> ModuleGenerationInstance:
        pass


    def generate_np_docs(self) -> None:
        temp_fp = open(self.temp_file, 'w')
        temp_fp.write(self.module_gen_instance.get_generated())
        temp_fp.close()
        print(f'Generated template np docs for file {os.path.basename(self.target)}')
        if self.overwrite:
            os.remove(self.target)
            os.rename(self.temp_file, self.target)
        else:
            pass


class DocGenerator:


def err_exit(message: str, code: int) -> None:
    """Exits program with error

    Parameters
    ----------
    message : str
        error message
    code : int
        exit code
    """

    print(f'ERROR - {message}')
    exit(code)


def check_input_output_valid(target: os.PathLike, ignore_list: StringList) -> (bool, int, str):
    """Checks if given input was valid

    Parameters
    ----------
    target : os.PathLike
        target input location
    output : os.PathLike
        Markdown output location
    ignore_list : list of str
        list of filenames to ignore

    Returns
    -------
    valid : bool
        True if valid, false otherwise
    err_code : int
        Error code if applicable
    err_message : str
        Error message if applicable
    """

    valid = False
    err_code = -1
    err_message = None

    if not os.path.exists(target):
        err_message = 'The target path does not exist!'
    
    elif os.path.isfile(target) and ignore_list is not None and os.path.basename(target) in ignore_list:
        err_message = 'The target path is a file that is being ignored!'

    elif not os.access(target, os.W_OK):
        err_message = 'The target exists, but you do not have permission to write to it!'
    else:
        valid = True
        err_code = 0

    return valid, err_code, err_message


def print_version_info() -> None:
    """Function that prints version, copyright, and author information
    """

    print(f'npdoc2md v{__version__}\n')
    print(f'Copyright (c) {__copyright__}')
    print(f'Author: {__author__}')
    print(f'{__url__}')
    print('MIT License\n')


def parse_args():
    parser = argparse.ArgumentParser(description='A utility for auto-creating base numpy style docstrings for an entire python project.')
    parser.add_argument('-v', '--version', action='store_true', help='Add this flag for displaying version information.')
    parser.add_argument('-i', '--input', required= not ('-v' in sys.argv or '--version' in sys.argv), help='Path to target python project or file')
    parser.add_argument('-c', '--createtemp', action='store_true', help='If this flag is set, code2npdoc will create a temporary conversion folder without overriding your sources.')
    parser.add_argument('-s', '--skip', nargs='+', help='List of filenames/directories to skip.')
    parser.add_argument('-d', '--debug', action='store_true', help='Add this flag to print detailed log messages during conversion.')
    args = vars(parser.parse_args())

    if args['version']:
        print_version_info()
        exit()

    valid, err_code, err_message = check_input_output_valid(args['target'], args['output'], args['ignore'])
    if not valid:
        err_exit(err_message, err_code)

    if args['skip'] is None:
        ignore_list = []
    else:
        ignore_list = args['skip']

def main():
    pass