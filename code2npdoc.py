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

    def __init__(self, attribute_name : str, elements):
        self.attribute_name = attribute_name
        self.attribute_elements = elements

class GenerationInstance:

    def __init__(self, name, doc_level):
        self.name = name
        self.descriptors = []
        self.doc_level = doc_level


    def add_descriptor(self, name, elements):
        self.descriptors.append(DocStringAttribute(name, elements))

    def make_descriptor_string(self):
        desc_string = ''
        tabs = '    ' * self.doc_level
        for descriptor in self.descriptors:
            desc_string = f'{desc_string}{tabs}{descriptor.attribute_name}\n{"-" * len(descriptor.attribute_name)}\n'
            for elem in descriptor.attribute_element:
                desc_string = f'{desc_string}{tabs}{elem}\n{tabs}    TODO describe {elem}\n'
            desc_string = f'{desc_string}\n'
        return desc_string


class ModuleGenerationInstance:

    def __init__(self, name, original_module_text):
        self.original_module_text = original_module_text
        self.sub_gen_items = []

    def get_generated(self):
        out = ''
        line_counter = 0
        while line_counter < len(original_module_text):
            line = original_module_text[line_counter]
            match = self.return_match(line)
            if match is None or original_module_text[line_counter + 1].strip().startswith('"""'):
                out = f'{out}{line}'
            else:
                out = f'{out}{line}{match[0]}"""TODO - describe {match[1]}\n{match[2]}\n"""'

        return out


    def return_match(self, line):
        match = None
        for item in self.sub_gen_items:
            if line.strip.startswith(item.name) or line.strip.startswith(f'def {item.name}'):
                match = [item.name, item.doc_level, item.make_descriptor_string()]
        return match


class GenerationItem:

    def __init__(self, target_file_path : os.PathLike, overwrite):
        self.target = target_file_path
        self.overwrite = overwrite
        self.temp_file = os.path.join(os.dirname(self.target), '__code2npdoc_temp__')
        self.module_gen_instance = self.create_module_gen_instance()


    def create_module_gen_instance(self) -> ModuleGenerationInstance:
        target_fp = open(self.target, 'r')
        contents = target_fp.readlines()
        mod_instance = ModuleGenerationInstance(os.path.basename(self.target), contents)
        for line in contents:
            stripped = line.strip()
            if line.startswith('class'):
                mod_instance.sub_gen_items.append(GenerationInstance(stripped.split(' ')[1][:-1], 1))
            elif line.startswith('def'):
                mod_instance.sub_gen_items.append(GenerationInstance(stripped.split(' ')[1].split('(')[0], 1))
            elif stripped.startswith('def'):
                mod_instance.sub_gen_items.append(GenerationInstance(stripped.split(' ')[1].split('(')[0], 2))

        return mod_instance


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

    def __init__(self):
        pass

    def generate_docs(self):
        for item in self.generate_generation_item_list():
            item.generate_np_docs()



def generate_generation_item_list(target: os.PathLike, ignore_list: StringList, overwrite : bool) -> ConversionList:
    """Generates list of all conversion items

    Parameters
    ----------
    target : os.PathLike
        target of python module or package
    ignore_list : list of str
        List of filenames to ignore
    
    Returns
    -------
    conversion_item_list : ConversionList
        List of all discovered files as conversion items
    """
    generation_item_list = []

    if os.path.isfile(target):
        generation_item_list.append(GenerationItem(os.path.abspath(target)))
    else:
        for (root, _, files) in os.walk(target):
            for file in files:
                if file not in ignore_list and file.endswith('.py'):
                    generation_item_list.append(GenerationItem(os.path.abspath(os.path.join(root, file)), overwrite))

    return generation_item_list


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