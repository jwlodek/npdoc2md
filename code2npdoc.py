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
import time

# Import typing to use python3 typing features
from typing import List
StringList = List[str]

# Current script version
__version__     = '0.0.1'
__copyright__   = '2020'
__author__      = 'Jakub Wlodek'
__url__         = 'https://github.com/jwlodek/npdoc2md'


class DocStringAttribute:

    def __init__(self, attribute_name : str, elements : List[str]):
        self.attribute_name = attribute_name
        self.attribute_elements = elements

class GenerationInstance:

    def __init__(self, name : str, doc_level : int):
        self.name = name
        self.descriptors = []
        self.doc_level = doc_level


    def add_descriptor(self, name : str, elements : List[str]):
        self.descriptors.append(DocStringAttribute(name, elements))

    def make_descriptor_string(self):
        desc_string = ''
        tabs = '    ' * self.doc_level
        descriptor_counter = 0
        for descriptor in self.descriptors:
            desc_string = f'{desc_string}{tabs}{descriptor.attribute_name}\n{tabs}{"-" * len(descriptor.attribute_name)}\n'
            for elem in descriptor.attribute_elements:
                desc_string = f'{desc_string}{tabs}{elem.strip()}\n{tabs}    TODO\n'
            
            descriptor_counter += 1
            if descriptor_counter < len(self.descriptors):
                desc_string = f'{desc_string}\n'

        return desc_string


class ModuleGenerationInstance:

    def __init__(self, name : str, original_module_text : List[str]):
        self.original_module_text = original_module_text
        self.sub_gen_items = []

    def get_generated(self):
        out = ''
        line_counter = 0
        while line_counter < len(self.original_module_text):
            line = self.original_module_text[line_counter]
            match = self.return_match(line)
            if match is None:
                out = f'{out}{line}'
            elif line_counter < len(self.original_module_text) - 1 and self.original_module_text[line_counter + 1].strip().startswith('"""'):
                    out = f'{out}{line}'
            else:
                out = f'{out}{line}{"    " * match[1]}"""TODO\n\n{match[2]}{"    " * match[1]}"""\n\n'


            line_counter = line_counter + 1

        return out


    def return_match(self, line : str):
        match = None
        for item in self.sub_gen_items:
            if len(line.strip().split(' ', 1)) > 1:
                if line.strip().split(' ', 1)[1].startswith(item.name):
                    print('Matched!')
                    if item.name == '__init__':
                        match = [item.name, item.doc_level, '']
                    else:
                        match = [item.name, item.doc_level, item.make_descriptor_string()]
        return match


class GenerationItem:

    def __init__(self, target_file_path : os.PathLike, overwrite : bool):
        self.target = target_file_path
        self.overwrite = overwrite
        self.temp_file = os.path.join(os.path.dirname(self.target), '__code2npdoc_temp__')
        self.module_gen_instance = self.create_module_gen_instance()


    def create_module_gen_instance(self) -> ModuleGenerationInstance:
        target_fp = open(self.target, 'r')
        contents = target_fp.readlines()
        mod_instance = ModuleGenerationInstance(os.path.basename(self.target), contents)
        class_instance = None
        class_attributes = []
        current_instance = None
        for line in contents:
            stripped = line.strip()
            if line.startswith('class'):
                current_instance = GenerationInstance(stripped.split(' ')[1][:-1], 1)
                class_instance = current_instance
                mod_instance.sub_gen_items.append(current_instance)
            elif line.startswith('def'):
                if class_instance is not None:
                    class_instance.add_descriptor('Attributes', class_attributes)
                    class_instance = None
                    class_attributes = []
                current_instance = GenerationInstance(stripped.split(' ')[1].split('(')[0], 1)
                params = line.split('(', 1)[1].split(')', 1)[0].split(',')
                if len(params) > 0 and len(params[0].strip()) > 0:
                    current_instance.add_descriptor('Parameters', params)
                mod_instance.sub_gen_items.append(current_instance)
            elif stripped.startswith('def'):
                current_instance = GenerationInstance(stripped.split(' ')[1].split('(')[0], 2)
                params = line.split('(', 1)[1].split(')', 1)[0].split(',')
                print(params)
                if len(params) > 1:
                    current_instance.add_descriptor('Parameters', params[1:])
                mod_instance.sub_gen_items.append(current_instance)
            elif stripped.startswith('return'):
                current_instance.add_descriptor('Returns', stripped.split(' ', 1)[1].split(','))
            elif stripped.startswith('self') and class_instance is not None:
                attr = stripped.split('=')[0].split('.',1)[1]
                if attr not in class_attributes:
                    class_attributes.append(attr)

        if class_instance is not None:
            class_instance.add_descriptor('Attributes', class_attributes)

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

    def __init__(self, target : os.PathLike, ignore_list : List[str]):
        self.target = target
        self.ignore_list = ignore_list

    def generate_docs(self, overwrite):
        for item in generate_generation_item_list(self.target, self.ignore_list, overwrite):
            item.generate_np_docs()



def generate_generation_item_list(target: os.PathLike, ignore_list: List[str], overwrite : bool) -> List[GenerationItem]:
    generation_item_list = []

    if os.path.isfile(target):
        generation_item_list.append(GenerationItem(os.path.abspath(target), overwrite))
    else:
        for (root, _, files) in os.walk(target):
            for file in files:
                if file not in ignore_list and file.endswith('.py'):
                    generation_item_list.append(GenerationItem(os.path.abspath(os.path.join(root, file)), overwrite))

    return generation_item_list


def err_exit(message: str, code: int) -> None:

    print(f'ERROR - {message}')
    exit(code)


def check_input_output_valid(target: os.PathLike, ignore_list: List[str]) -> (bool, int, str):

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

    valid, err_code, err_message = check_input_output_valid(args['input'], args['skip'])
    if not valid:
        err_exit(err_message, err_code)

    if args['skip'] is None:
        ignore_list = []
    else:
        ignore_list = args['skip']

    generator = DocGenerator(args['input'], ignore_list)
    return generator, not args['createtemp']

def main():
    generator, overwrite = parse_args()
    generator.generate_docs(overwrite)


if __name__ == '__main__':
    main()