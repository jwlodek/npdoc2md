#!/usr/bin/env python3

import os
import shutil
import argparse

import logging



class ConversionItem:

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)
        self.md_file_name = ''
        title_elements = self.file_name[:-3].split('_')
        for elem in title_elements:
            self.md_file_name = self.md_file_name + elem.capitalize()
        self.converted_markdown = ''



class MDConverter:

    def __init__(self, conversion_item_list, output_loc):
        


    def convert_doc_to_md(self, conversion_item):


    def generate_markdown_for_item(self, conversion_item):
        md_fp = open(os.path.join(self.output_loc, conversion_item.md_file_name), 'w')
        print('Writing ')
        md_fp.write(conversion_item.converted_markdown)
        md_fp.close()



def generate_conversion_item_list(target, ignore_list):
    conversion_item_list = []

    if os.path.isfile(target):
        conversion_item_list.append(ConversionItem(os.path.abspath(target)))
    else:
        for (root, dirs, files) in os.walk(target):
            for file in files:
                if file not in ignore_list:
                    conversion_item_list.append(ConversionItem(os.path.abspath(os.path.join(root, file))))

    return conversion_item_list



def err_exit(message, code):
    print(f'ERROR - {message}')
    exit(code)



def check_input_output_valid(target, output, ignore_list):

    valid = False
    err_code = -1
    err_message = None

    if not os.path.exists(target):
        err_message = 'The target path does not exist!'
    
    elif os.path.isfile(target) and os.path.basename(target) in ignore_list:
        err_message = 'The target path is a file that is being ignored!'

    elif os.path.exists(output) and not os.path.isdir(output):
        err_message = 'The output location exists, but is not a directory!'

    elif not os.path.exists(output):
        try:
            os.mkdir(output)
        except OSError:
            err_message = 'The output directory does not exist, and could not be created!'
        except PermissionError:
            err_message = 'The output directory does not exist, and you do not have permission to create it!'
    
    elif not os.access(output, os.W_OK):
        err_message = 'The output directory exists, but you do not have permission to write to it!'
    else:
        valid = True
        err_code = 0

    return valid, err_code, err_message




def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('target', help='The path to the target python project or file to convert.')
    parser.add_argument('output', help='The output directory where the markdown files should be placed.')
    parser.add_argument('-i', '--ignore', nargs='+', help='List of filenames/directories to ignore.')
    parser.add_argument('-d', '--debug', action='store_true', help='Add this flag to print detailed log messages during conversion.')
    args = vars(parser.parse_args())

    valid, err_code, err_message = check_input_output_valid(args['target'], args['output'])
    if not valid:
        err_exit(err_message, err_code)

    return converter




if __name__ == "__main__":
    md_converter = parse_args()
    md_converter.process()
