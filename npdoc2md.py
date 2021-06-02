#!/usr/bin/env python3

"""Script for autogenerating markdown documentation given path to python package with numpy-style comments  

@author: Jakub Wlodek  
@created: Feb-6-2020
"""

# Some standard lib imports
import os
import sys
import shutil
import argparse
import logging

# Import typing to use python3 typing features
from typing import List

# Current script version
__version__     = '0.0.1'
__copyright__   = '2020'
__author__      = 'Jakub Wlodek'
__url__         = 'https://github.com/jwlodek/npdoc2md'


# Descriptors possible in docstrings, used for table column names
docstring_descriptors = {
    'Classes'       : ['Class',             'Doc'],
    'Functions'     : ['Function',          'Doc'],
    'Attributes'    : ['Attribute',         'Type', 'Doc'],
    'Methods'       : ['Method',            'Doc'],
    'Returns'       : ['Return Variable',   'Type', 'Doc'],
    'Parameters'    : ['Parameter',         'Type', 'Doc'],
    'Raises'        : ['Error',             'Type', 'Doc'],
}


class DocStringAttribute:
    """Stores docstring attribute and its elements. Ex(Parameters)

    Attributes
    ----------
    attribute_name : str
        Name of the attribute
    attribute_elements : List[List[str]]
        List of elements assigned to the attribute for the current instance
    """

    def __init__(self, attribute_name : str):
        """constructor for DocstringAttribute
        """

        self.attribute_name         = attribute_name
        self.attribute_elements     = []


class ItemInstance:
    """Base class for encountered programmatic instances

    Attributes
    ----------
    name : str
        Name of the instance (function, class, module name)
    usage : str
        How to envoke function, method
    simple_description : str
        Base description
    detailed description : str
        Additional detailed description
    descriptiors : dict of str -> DocStringAttribute
        Map of all docstring attribute descriptors
    """
    
    def __init__(self, name: str, usage: str = None):
        """Constructor for ItemInstance
        """

        self.name                   = name
        self.usage                  = usage
        self.simple_description     = ''
        self.detailed_description   = ''
        self.descriptors            = {}


    def set_simple_description(self, simple_description: str) -> None:
        """Initializes the simple description

        Parameters
        ----------
        simple_description : str
            New simple description
        """

        self.simple_description = simple_description


    def add_to_detailed_description(self, detailed_description_line: str) -> None:
        """Appends to the detailed description
        
        Parameters
        ----------
        detailed_description_line : str
            New description line
        """

        self.detailed_description = f'{self.detailed_description}\n{detailed_description_line}'


    def add_descriptor(self, descriptor_type: str, descriptor_elements: List[str]):
        """Creates a new descriptor
        
        Parameters
        ----------
        descriptor_type : str
            New descriptor type
        descriptor_elements : list of str
            New descriptor elements
        """

        self.descriptors[descriptor_type] = descriptor_elements


    def generate_md_table_from_descriptor(self, descriptor: str) -> str:
        """Generates markdown table for descriptor
        
        Parameters
        ----------
        descriptor : str
            Descriptor type
        
        Returns
        -------
        md : str
            Markdown string
        """

        md = ''
        if descriptor not in self.descriptors.keys() or descriptor not in docstring_descriptors.keys():
            pass
        else:
            heading = f'#### {descriptor}\n\n'
            for category in docstring_descriptors[descriptor]:
                md = f' {md} | {category} '
            md = f'{heading}{md.strip()[1:]}\n{"-----|-----" * (len(docstring_descriptors[descriptor]) - 1)}'
            for descriptor_item in self.descriptors[descriptor]:
                temp = ''
                for item_category_value in descriptor_item:
                    temp = f' {temp} | {item_category_value}'
                temp = temp.strip()[1:]
                md = f'{md}\n{temp}'

        return md


    def get_usage_str(self) -> str:
        """Gets markdown usage string

        Returns
        -------
        md : str
            Markdown string
        """

        if self.usage is None:
            return ''
        else:
            return f'```python\n{self.usage}\n```\n\n'


    def convert_to_markdown(self, heading_level: int) -> str:
        """Generates markdown for instance

        Parameters
        ----------
        heading_level : int
            The heading emphasis for the instance
        
        Returns
        -------
        md : str
            Markdown string
        """

        md = f'{"#" * heading_level} {self.name}\n\n{self.get_usage_str()}{self.simple_description}\n\n{self.detailed_description}\n\n'
        for descriptor in self.descriptors.keys():
            md = f'{md}{self.generate_md_table_from_descriptor(descriptor)}\n\n'
        md = md + '\n'
        return md


    def __format__(self, fmt):
        """Override of standard format function

        Parameters
        ----------
        fmt : format
            The given format
        """

        return f'Instance: {self.name} - {self.simple_description} - {self.descriptors}\n'



class FunctionInstance(ItemInstance):
    """Class representing function instances
    """

    def __init__(self, name, usage):
        """Constructor for function instance
        """

        super().__init__(name, usage=usage)


class ClassInstance(ItemInstance):
    """Class representing class instances
    """
    
    def __init__(self, name, usage):
        """Constructor for Class instance
        """

        super().__init__(name[:-1], usage=usage)
        self.instance_list = []


    def add_sub_instance(self, instance: ItemInstance) -> None:
        """Adds a sub-instance (methods)

        instance : ItemInstance
            item instance to add as sub-instance
        """

        self.instance_list.append(instance)


    def generate_method_descriptor(self):
        """Function that auto-generates the method descriptor from methods in class
        """

        method_descriptor_elems = []
        for item in self.instance_list:
            if isinstance(item, FunctionInstance) and item.name != '__init__':
                method_descriptor_elems.append([item.name, item.simple_description])
        
        if len(method_descriptor_elems) > 0:
            self.add_descriptor('Methods',      method_descriptor_elems)


    def convert_to_markdown(self, heading_level: int) -> str:
        """Override of base class, returns its own markdown plus sub instances

        Parameters
        ----------
        heading_level : int
            The heading emphasis for the instance
        
        Returns
        -------
        md : str
            Markdown string
        """

        self.generate_method_descriptor()
        md = f'{super().convert_to_markdown(heading_level)}\n\n'
        for function_instance in self.instance_list:
            md = f'{md}{function_instance.convert_to_markdown(3)}\n\n\n'
        return md


class ModuleInstance(ItemInstance):
    """Top Level module instance class
    """

    def __init__(self, name):
        """Constructor for module instance
        """

        super().__init__(name[:-3])
        self.instance_list = []


    def add_sub_instance(self, instance: ItemInstance) -> None:
        """Adds a sub-instance (methods)

        instance : ItemInstance
            item instance to add as sub-instance
        """

        self.instance_list.append(instance)


    def generate_class_function_descriptors(self):
        """Function that generates descriptors for included classes and functions in the module
        """

        class_descriptor_elems = []
        func_descriptor_elems = []
        for item in self.instance_list:
            if isinstance(item, ClassInstance):
                class_descriptor_elems.append([item.name, item.simple_description])
            elif isinstance(item, FunctionInstance):
                func_descriptor_elems.append([item.name, item.simple_description])
        
        if len(class_descriptor_elems) > 0:
            self.add_descriptor('Classes',      class_descriptor_elems)
        if len(func_descriptor_elems) > 0:
            self.add_descriptor('Functions',    func_descriptor_elems)


    def convert_to_markdown(self, heading_level: int) -> str:
        """Override of base class, returns its own markdown plus sub instances

        Parameters
        ----------
        heading_level : int
            The heading emphasis for the instance
        
        Returns
        -------
        md : str
            Markdown string
        """

        self.generate_class_function_descriptors()
        md = f'{super().convert_to_markdown(heading_level)}\n\n'
        for instance in self.instance_list:
            if isinstance(instance, FunctionInstance):
                md = f'{md}{instance.convert_to_markdown(3)}\n\n\n'
            elif isinstance(instance, ClassInstance):
                md = f'{md}{instance.convert_to_markdown(2)}\n\n\n'
        return md


# Some more definitions of types
InstanceList = List[ItemInstance]


def add_docstring_to_instance(instance: ItemInstance, doc_string: List[str]) -> None:
    """Function that parses docstring to data structures and adds to instance

    Parameters
    ----------
    instance : ItemInstance
        current instance
    doc_string : list of str
        Current instance's docstring as list of lines
    """

    current_descriptor = None
    i = 0
    while i < len(doc_string):
        left_stripped = doc_string[i].lstrip()
        stripped = doc_string[i].strip()
        if i == 0:
            instance.set_simple_description(stripped.replace('"""', ''))
        elif stripped not in docstring_descriptors.keys() and current_descriptor is None:
            instance.add_to_detailed_description(left_stripped)
        elif stripped in docstring_descriptors.keys():
            current_descriptor = stripped
        elif current_descriptor is not None and not stripped.startswith('---') and len(stripped) > 0:
            descriptor_elem = []
            if len(docstring_descriptors[current_descriptor]) == 3:
                name_type = stripped.split(':')
                if len(name_type) == 1:
                    name_type.insert(0, 'Unknown')
                descriptor_elem = descriptor_elem + name_type
            else:
                descriptor_elem.append(stripped.split('(')[0])
            i = i + 1
            try:
                descriptor_elem.append(doc_string[i].strip())
            except IndexError:
                descriptor_elem.append('Unknown')
            if current_descriptor not in instance.descriptors.keys():
                instance.descriptors[current_descriptor] = [descriptor_elem]
            else:
                instance.descriptors[current_descriptor].append(descriptor_elem)
        i = i + 1


def grab_module_instance(file_contents: List[str], file_name: str, parent_package: str=None) -> InstanceList:
    """Function that generates complete instance object for module

    Parameters
    ----------
    file_contents : List[str]
        Lines in python module file
    file_name : str
        Name of the file or module
    parent_package=None : str
        name of the parent package (if applicable)

    Returns
    -------
    top_module_instance : ModuleInstance
        module instance object at top level
    """


    if file_name == '__init__.py' and parent_package is not None:
        module_name = parent_package + '.py'
    else:
        module_name = file_name
    
    top_module_instance = ModuleInstance(module_name)
    parent_instance     = top_module_instance
    current_instance    = None

    line_counter = 0

    while line_counter < len(file_contents):
        line = file_contents[line_counter]
        if line.strip().startswith('def'):
            if line.startswith('def'):
                parent_instance = top_module_instance
            current_instance = FunctionInstance(line.strip().split('(')[0].split(' ')[1], line.strip()[:-1])
            parent_instance.add_sub_instance(current_instance)
        
        elif line.startswith('class'):
            current_instance = ClassInstance(line.split(' ', 1)[1][:-1], line.strip()[:-1])
            top_module_instance.add_sub_instance(current_instance)
            parent_instance = current_instance

        if line.strip().startswith('"""'):
            doc_string = ""
            while True:
                doc_string += file_contents[line_counter]
                if file_contents[line_counter].strip().endswith('"""'):
                    break
                else:
                    line_counter = line_counter + 1
            if current_instance is not None:
                add_docstring_to_instance(current_instance, doc_string.splitlines())
            else:
                add_docstring_to_instance(top_module_instance, doc_string.splitlines())

        line_counter = line_counter + 1

    return top_module_instance


class ConversionItem:
    """Class representing single file to convert

    Attributes
    ----------
    parent_package : str
        Parent package for file (if applicable)
    file_path : os.PathLike
        Source file path
    file_name : str
        Source file name
    md_file_name : str
        Output markdown file name
    converted_markdown : str
        Markdown for the module
    module_instance : ModuleInstance
        Converted module instance
    """

    def __init__(self, file_path: os.PathLike, parent_package: str=None):
        """Constructor for conversion item class
        """

        self.parent_package = parent_package
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)
        if self.file_name == '__init__.py':
            self.file_name = os.path.basename(os.path.dirname(self.file_path))
        self.md_file_name = ''
        if self.file_name.endswith('.py'):
            title_elements = self.file_name[:-3].split('_')
        else:
            title_elements = self.file_name.split('_')
        for elem in title_elements:
            self.md_file_name = self.md_file_name + elem.capitalize()
        self.md_file_name = self.md_file_name + '.md'
        self.converted_markdown = ''
        self.module_instance = None


    def collect_docstrings(self) -> None:
        """Collects docstrings from file
        """

        item_fp = open(self.file_path, 'r')
        file_contents = item_fp.readlines()
        self.module_instance = grab_module_instance(file_contents, os.path.basename(self.file_path), parent_package=self.parent_package)
        item_fp.close()


    def generate_markdown(self) -> None:
        """Generates markdown for file
        """

        self.converted_markdown = self.module_instance.convert_to_markdown(1)


# Define for type checking
ConversionList = List[ConversionItem]


class MDConverter:
    """Main Driver class for script

    Attributes
    ----------
    conversion_item_list : ConversionList
        list of items to convert
    output_loc : os.PathLike
        Output location for markdown
    """

    def __init__(self, conversion_item_list: ConversionList, output_loc: os.PathLike):
        """Constructor for MDConverter
        """

        self.conversion_item_list = conversion_item_list
        self.output_loc = output_loc


    def convert_doc_to_md(self, conversion_item: ConversionItem) -> None:
        """Converts docstrings to markdown internally
        """

        conversion_item.collect_docstrings()
        conversion_item.generate_markdown()


    def generate_markdown_for_item(self, conversion_item: ConversionItem) -> None:
        """Generates a markdown file for given conversion item

        Parameters
        ----------
        conversion_item : ConversionItem
            Conversion item for which to create markdown file
        """

        md_fp = open(os.path.join(self.output_loc, conversion_item.md_file_name), 'w')
        print(f'Writing converted markdown file {conversion_item.md_file_name} from {os.path.basename(conversion_item.file_path)}')
        md_fp.write(conversion_item.converted_markdown)
        md_fp.close()


    def execute_conversion_process(self) -> None:
        """Main Driver function for converter
        """

        for conversion_item in self.conversion_item_list:
            self.convert_doc_to_md(conversion_item)
            #print(f'{conversion_item.module_instance}')
            self.generate_markdown_for_item(conversion_item)




def generate_conversion_item_list(target: os.PathLike, ignore_list: List[str]) -> ConversionList:
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
    conversion_item_list = []

    if os.path.isfile(target):
        conversion_item_list.append(ConversionItem(os.path.abspath(target)))
    else:
        for (root, _, files) in os.walk(target):
            for file in files:
                if file not in ignore_list and file.endswith('.py'):
                    conversion_item_list.append(ConversionItem(os.path.abspath(os.path.join(root, file)), parent_package=os.path.basename(target)))

    return conversion_item_list


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



def check_input_output_valid(target: os.PathLike, output: os.PathLike, ignore_list: List[str]) -> (bool, int, str):
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

    valid       = False
    err_code    = -1
    err_message = None

    if not os.path.exists(target):
        err_message = 'The target path does not exist!'
    
    elif os.path.isfile(target) and ignore_list is not None and os.path.basename(target) in ignore_list:
        err_message = 'The target path is a file that is being ignored!'

    elif os.path.exists(output) and not os.path.isdir(output):
        err_message = 'The output location exists, but is not a directory!'

    elif not os.path.exists(output):
        try:
            os.mkdir(output)
            valid = True
            err_code = 0
        except PermissionError:
            err_message = 'The output directory does not exist, and you do not have permission to create it!'
        except OSError:
            err_message = 'The output directory does not exist, and could not be created!'
    elif not os.access(output, os.W_OK):
        err_message = 'The output directory exists, but you do not have permission to write to it!'
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



def parse_args() -> (MDConverter, bool):
    """Function that parses user arguments

    Returns
    -------
    converter : MDConverter
        Main converter object
    debug : bool
        toggle for debug printing
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version',  action='store_true', help='Use this flag to print out npdoc2md version info.')
    is_version = ('-v' in sys.argv or '--version' in sys.argv)
    parser.add_argument('-i', '--input',    required=not is_version, help='The path to the target python project or file to convert.')
    parser.add_argument('-o', '--output',   required=not is_version, help='The output directory where the markdown files should be placed.')
    parser.add_argument('-s', '--skip',     nargs='+', help='List of filenames/directories to skip.')
    parser.add_argument('-d', '--debug', action='store_true', help='Add this flag to print detailed log messages during conversion.')
    args = vars(parser.parse_args())

    if args['version']:
        print_version_info()
        exit()

    valid, err_code, err_message = check_input_output_valid(args['input'], args['output'], args['skip'])
    if not valid:
        err_exit(err_message, err_code)

    if args['skip'] is None:
        ignore_list = []
    else:
        ignore_list = args['skip']

    conversion_list = generate_conversion_item_list(args['input'], ignore_list)
    if len(conversion_list) == 0:
        err_exit('No valid files detected for conversion.', -1)
    
    converter = MDConverter(conversion_list, args['output'])
    return converter, args['debug']


def main():
    """Main runner function
    """

    md_converter, enable_logging = parse_args()
    
    #logger = logging.getLogger()
    #if not enable_logging():
    #    logger.disabled = True

    md_converter.execute_conversion_process()


if __name__ == "__main__":
    main()
