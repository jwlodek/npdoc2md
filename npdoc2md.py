#!/usr/bin/env python3

import os
import shutil
import argparse

import logging


from typing import List


__version__ = '0.0.1'

docstring_descriptors = {
    'Classes'       : ['Class',             'Doc'],
    'Functions'     : ['Function',          'Doc'],
    'Attributes'    : ['Attribute',         'Type', 'Doc'],
    'Methods'       : ['Method',            'Doc'],
    'Returns'       : ['Return Variable',   'Type', 'Doc'],
    'Parameters'    : ['Parameter',         'Type', 'Doc'],
}


class DocStringAttribute:

    def __init__(self, attribute_name):
        self.attribute_name = attribute_name
        self.attribute_elements = []


class ItemInstance:
    
    def __init__(self, name: str, usage: str = None):
        self.name = name
        self.usage = usage
        self.simple_description = ''
        self.detailed_description = ''
        self.descriptors = {}

    def set_simple_description(self, simple_description: str) -> None:
        self.simple_description = simple_description
    
    def add_to_detailed_description(self, detailed_description_line: str) -> None:
        self.detailed_description = f'{self.detailed_description}\n{detailed_description_line}'

    def add_descriptor(self, descriptor_type, descriptor_elements):
        self.descriptors[descriptor_type] = descriptor_elements


    def generate_md_table_from_descriptor(self, descriptor: str) -> str:
        md = ''
        if descriptor not in self.descriptors.keys() or descriptor not in docstring_descriptors.keys():
            pass
        else:
            heading = f'#### {descriptor}\n\n'
            for category in docstring_descriptors[descriptor]:
                md = f' {md} | {category} '
            md = f'{heading}{md.strip()[1:]}\n{"-----|-----" * len(docstring_descriptors[descriptor])}'
            for descriptor_item in self.descriptors[descriptor]:
                temp = ''
                for item_category_value in descriptor_item:
                    temp = f' {temp} | {item_category_value}'
                temp = temp.strip()[1:]
                md = f'{md}\n{temp}'

        return md

    def get_usage_str(self) -> str:
        if self.usage is None:
            return ''
        else:
            return f'```python\n{self.usage}\n```\n\n'


    def convert_to_markdown(self, heading_level: int) -> str:
        md = f'{"#" * heading_level} {self.name}\n\n{self.get_usage_str()}{self.simple_description}\n\n{self.detailed_description}\n\n'
        for descriptor in self.descriptors.keys():
            md = f'{md}{self.generate_md_table_from_descriptor(descriptor)}\n\n'
        md = md + '\n'
        return md

    def __format__(self, fmt):
        return f'Instance: {self.name} - {self.simple_description} - {self.descriptors}\n'



class FunctionInstance(ItemInstance):
    def __init__(self, name, usage):
        super().__init__(name, usage=usage)


class ClassInstance(ItemInstance):
    
    def __init__(self, name, usage):
        super().__init__(name[:-1], usage=usage)
        self.instance_list = []

    def add_sub_instance(self, instance: ItemInstance) -> None:
        self.instance_list.append(instance)

    def convert_to_markdown(self, heading_level: int) -> str:
        md = f'{super().convert_to_markdown(heading_level)}\n\n'
        for function_instance in self.instance_list:
            md = f'{md}{function_instance.convert_to_markdown(3)}\n\n\n'
        return md


class ModuleInstance(ItemInstance):
    def __init__(self, name):
        super().__init__(name[:-3])
        self.instance_list = []

    def add_sub_instance(self, instance: ItemInstance) -> None:
        self.instance_list.append(instance)

    def convert_to_markdown(self, heading_level: int) -> str:
        md = f'{super().convert_to_markdown(heading_level)}\n\n'
        for instance in self.instance_list:
            #print(instance.convert_to_markdown(3))
            if isinstance(instance, FunctionInstance):
                md = f'{md}{instance.convert_to_markdown(3)}\n\n\n'
            elif isinstance(instance, ClassInstance):
                md = f'{md}{instance.convert_to_markdown(2)}\n\n\n'
        return md


StringList = List[str]
InstanceList = List[ItemInstance]


def add_docstring_to_instance(instance: ItemInstance, doc_string: StringList) -> None:
    print(doc_string)
    current_descriptor = None
    i = 0
    while i < len(doc_string):
        left_stripped = doc_string[i].lstrip()
        stripped = doc_string[i].strip()
        if i == 0:
            instance.set_simple_description(stripped[3:])
        elif stripped not in docstring_descriptors.keys() and current_descriptor is None:
            instance.add_to_detailed_description(left_stripped)
        elif stripped in docstring_descriptors.keys():
            current_descriptor = stripped
        elif current_descriptor is not None and not stripped.startswith('---') and len(stripped) > 0:
            descriptor_elem = []
            if len(docstring_descriptors[current_descriptor]) == 3:
                descriptor_elem = descriptor_elem + stripped.split(':')
            else:
                descriptor_elem.append(stripped.split('(')[0])
            i = i + 1
            descriptor_elem.append(doc_string[i].strip())
            if current_descriptor not in instance.descriptors.keys():
                instance.descriptors[current_descriptor] = [descriptor_elem]
            else:
                instance.descriptors[current_descriptor].append(descriptor_elem)
        i = i + 1


def grab_module_instance(file_contents: StringList, file_name: str) -> InstanceList:

    top_module_instance = ModuleInstance(file_name)
    parent_instance = top_module_instance
    current_instance = None

    line_counter = 0

    while line_counter < len(file_contents):
        line = file_contents[line_counter]
        if line.strip().startswith('def'):
            if line.startswith('def'):
                parent_instance = top_module_instance
            current_instance = FunctionInstance(line.strip().split('(')[0].split(' ')[1], line.strip()[:-1])
            parent_instance.add_sub_instance(current_instance)
        
        elif line.startswith('class'):
            current_instance = ClassInstance(line.split(' ')[1][:-1], line.strip()[:-1])
            top_module_instance.add_sub_instance(current_instance)
            parent_instance = current_instance

        if line.strip().startswith('"""'):
            doc_string = line
            line_counter = line_counter + 1
            while not file_contents[line_counter].strip().endswith('"""'):
                doc_string = doc_string + file_contents[line_counter]
                line_counter = line_counter + 1
            if current_instance is not None:
                add_docstring_to_instance(current_instance, doc_string.splitlines())
            else:
                add_docstring_to_instance(top_module_instance, doc_string.splitlines())

        line_counter = line_counter + 1

    return top_module_instance


class ConversionItem:

    def __init__(self, file_path: os.PathLike):
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)
        if self.file_name == '__init__.py':
            self.file_name = os.path.dirname(self.file_path)
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


    def collect_docstrings(self):
        item_fp = open(self.file_path, 'r')
        file_contents = item_fp.readlines()
        self.module_instance = grab_module_instance(file_contents, os.path.basename(self.file_path))
        item_fp.close()


    def generate_markdown(self):
        self.converted_markdown = self.module_instance.convert_to_markdown(1)


ConversionList = List[ConversionItem]



class MDConverter:

    def __init__(self, conversion_item_list: ConversionList, output_loc: os.PathLike):
        self.conversion_item_list = conversion_item_list
        self.output_loc = output_loc
        


    def convert_doc_to_md(self, conversion_item: ConversionItem) -> None:
        conversion_item.collect_docstrings()
        conversion_item.generate_markdown()

    def generate_markdown_for_item(self, conversion_item: ConversionItem) -> None:
        md_fp = open(os.path.join(self.output_loc, conversion_item.md_file_name), 'w')
        print(f'Writing converted markdown file {conversion_item.md_file_name} from {os.path.basename(conversion_item.file_path)}')
        md_fp.write(conversion_item.converted_markdown)
        md_fp.close()


    def execute_conversion_process(self) -> None:
        for conversion_item in self.conversion_item_list:
            self.convert_doc_to_md(conversion_item)
            #print(f'{conversion_item.module_instance}')
            self.generate_markdown_for_item(conversion_item)




def generate_conversion_item_list(target: os.PathLike, ignore_list: StringList) -> ConversionList:
    conversion_item_list = []

    if os.path.isfile(target):
        conversion_item_list.append(ConversionItem(os.path.abspath(target)))
    else:
        for (root, _, files) in os.walk(target):
            for file in files:
                if file not in ignore_list and file.endswith('.py'):
                    conversion_item_list.append(ConversionItem(os.path.abspath(os.path.join(root, file))))

    return conversion_item_list



def err_exit(message: str, code: int) -> None:
    print(f'ERROR - {message}')
    exit(code)



def check_input_output_valid(target: os.PathLike, output: os.PathLike, ignore_list: StringList) -> (bool, int, str):

    valid = False
    err_code = -1
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




def parse_args() -> (MDConverter, bool):

    parser = argparse.ArgumentParser()
    parser.add_argument('target', help='The path to the target python project or file to convert.')
    parser.add_argument('output', help='The output directory where the markdown files should be placed.')
    parser.add_argument('-i', '--ignore', nargs='+', help='List of filenames/directories to ignore.')
    parser.add_argument('-d', '--debug', action='store_true', help='Add this flag to print detailed log messages during conversion.')
    args = vars(parser.parse_args())

    valid, err_code, err_message = check_input_output_valid(args['target'], args['output'], args['ignore'])
    if not valid:
        err_exit(err_message, err_code)

    if args['ignore'] is None:
        ignore_list = []
    else:
        ignore_list = args['ignore']

    conversion_list = generate_conversion_item_list(args['target'], ignore_list)
    if len(conversion_list) == 0:
        err_exit('No valid files detected for conversion.', -1)
    
    converter = MDConverter(conversion_list, args['output'])
    return converter, args['debug']




if __name__ == "__main__":
    md_converter, enable_logging = parse_args()
    
    #logger = logging.getLogger()
    #if not enable_logging():
    #    logger.disabled = True

    md_converter.execute_conversion_process()
