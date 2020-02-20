# npdoc2md

Script for autogenerating markdown documentation given path to python package with numpy-style comments




@author: Jakub Wlodek  
@created: Feb-6-2020


#### Classes

 Class  | Doc
-----|-----
 DocStringAttribute | Stores docstring attribute and its elements. Ex(Parameters)
 ItemInstance | Base class for encountered programmatic instances
 FunctionInstance | Represents an encountered function or method
 ClassInstance | Represents an encountered class
 ModuleInstance | Represents an encountered module
 ConversionItem | Single file that needs to be converted. Corresponds to one ModuleInstance object
 MDConverter | Main conversion driver class

#### Functions

 Function  | Doc
-----|-----
 add_docstring_to_instance | Function that parses a docstring into data structures and adds it to instance object
 grab_module_instance | Function that takes a module, and generates all instance objects in a top level module instance
 generate_conversion_item_list | Generates conversion item objects given target
 err_exit | Exits program with an error
 check_input_output_valid | Checks if given inputs are valid
 parse_args | Parses user arguments




## DocStringAttribute

```python
class DocStringAttribute
```

Stores docstring attribute and its elements. Ex(Parameters)




#### Attributes

 Attribute  | Type  | Doc
-----|----------|-----
 attribute_name  |  str | Name of the attribute
 attribute_elements  |  list of list of str | List of elements assigned to the attribute for the current instance




### __init__

```python
def __init__(self, attribute_name)
```












## ItemInstance

```python
class ItemInstance
```

Base class for encountered programmatic instances




#### Attributes

 Attribute  | Type  | Doc
-----|----------|-----
 name  |  str | Name of the instance (function, class, module name)
 usage  |  str | How to envoke function, method
 simple_description  |  str | Base description
 detailed description  |  str | Additional detailed description
 descriptiors  |  dict of str -> DocStringAttribute | Map of all docstring attribute descriptors

#### Methods

 Method  | Doc
-----|-----
 set_simple_description | Initializes the simple description
 add_to_detailed_description | Appends to the detailed description
 add_descriptor | Adds a new descriptor
 generate_md_table_from_descriptor | Generates markdown table given descriptor
 get_usage_str | Generates usage markdown
 convert_to_markdown | Converts current instance state to markdown
 __format__ | Override of base format class




### __init__

```python
def __init__(self, name: str, usage: str = None)
```

Constructor for ItemInstance







### set_simple_description

```python
def set_simple_description(self, simple_description: str) -> None
```

Initializes the simple description




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 simple_description  |  str | New simple description





### add_to_detailed_description

```python
def add_to_detailed_description(self, detailed_description_line: str) -> None
```

Appends to the detailed description




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 detailed_description_line  |  str | New description line





### add_descriptor

```python
def add_descriptor(self, descriptor_type: str, descriptor_elements: StringList)
```

Creates a new descriptor




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 descriptor_type  |  str | New descriptor type
 descriptor_elements  |  list of str | New descriptor elements





### generate_md_table_from_descriptor

```python
def generate_md_table_from_descriptor(self, descriptor: str) -> str
```

Generates markdown table for descriptor




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 descriptor  |  str | Descriptor type

#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 md  |  str | Markdown string





### get_usage_str

```python
def get_usage_str(self) -> str
```

Gets markdown usage string




#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 md  |  str | Markdown string





### convert_to_markdown

```python
def convert_to_markdown(self, heading_level: int) -> str
```

Generates markdown for instance




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 heading_level  |  int | The heading emphasis for the instance

#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 md  |  str | Markdown string





### __format__

```python
def __format__(self, fmt)
```

Override of standard format function




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 fmt  |  format | The given format








## FunctionInstance(ItemInstance)

```python
class FunctionInstance(ItemInstance)
```

Class representing function instances






### __init__

```python
def __init__(self, name, usage)
```

Constructor for function instance










## ClassInstance(ItemInstance)

```python
class ClassInstance(ItemInstance)
```

Class representing class instances




#### Methods

 Method  | Doc
-----|-----
 add_sub_instance | Adds a sub-instance (methods)
 convert_to_markdown | Override of base class, returns its own markdown plus sub instances




### __init__

```python
def __init__(self, name, usage)
```

Constructor for Class instance







### add_sub_instance

```python
def add_sub_instance(self, instance: ItemInstance) -> None
```

Adds a sub-instance (methods)



instance : ItemInstance
item instance to add as sub-instance





### convert_to_markdown

```python
def convert_to_markdown(self, heading_level: int) -> str
```

Override of base class, returns its own markdown plus sub instances




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 heading_level  |  int | The heading emphasis for the instance

#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 md  |  str | Markdown string








## ModuleInstance(ItemInstance)

```python
class ModuleInstance(ItemInstance)
```

Top Level module instance class




#### Methods

 Method  | Doc
-----|-----
 add_sub_instance | Adds a sub-instance (methods)
 convert_to_markdown | Override of base class, returns its own markdown plus sub instances




### __init__

```python
def __init__(self, name)
```

Constructor for module instance







### add_sub_instance

```python
def add_sub_instance(self, instance: ItemInstance) -> None
```

Adds a sub-instance (methods)



instance : ItemInstance
item instance to add as sub-instance





### convert_to_markdown

```python
def convert_to_markdown(self, heading_level: int) -> str
```

Override of base class, returns its own markdown plus sub instances




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 heading_level  |  int | The heading emphasis for the instance

#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 md  |  str | Markdown string








### add_docstring_to_instance

```python
def add_docstring_to_instance(instance: ItemInstance, doc_string: StringList) -> None
```

Function that parses docstring to data structures and adds to instance




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 instance  |  ItemInstance | current instance
 doc_string  |  list of str | Current instance's docstring as list of lines





### grab_module_instance

```python
def grab_module_instance(file_contents: StringList, file_name: str, parent_package=None) -> InstanceList
```

Function that generates complete instance object for module




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 file_contents  |  list of str | Lines in python module file
 file_name  |  str | Name of the file or module
 parent_package=None  |  str | name of the parent package (if applicable)

#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 top_module_instance  |  ModuleInstance | module instance object at top level





## ConversionItem

```python
class ConversionItem
```

Class representing single file to convert




#### Attributes

 Attribute  | Type  | Doc
-----|----------|-----
 parent_package  |  str | Parent package for file (if applicable)
 file_path  |  os.PathLike | Source file path
 file_name  |  str | Source file name
 md_file_name  |  str | Output markdown file name
 converted_markdown  |  str | Markdown for the module
 module_instance  |  ModuleInstance | Converted module instance

#### Methods

 Method  | Doc
-----|-----
 collect_docstrings | Collects docstrings from file
 generate_markdown | Generates markdown for file




### __init__

```python
def __init__(self, file_path: os.PathLike, parent_package: str=None)
```

Constructor for conversion item class







### collect_docstrings

```python
def collect_docstrings(self) -> None
```

Collects docstrings from file







### generate_markdown

```python
def generate_markdown(self) -> None
```

Generates markdown for file










## MDConverter

```python
class MDConverter
```

Main Driver class for script




#### Attributes

 Attribute  | Type  | Doc
-----|----------|-----
 conversion_item_list  |  ConversionList | list of items to convert
 output_loc  |  os.PathLike | Output location for markdown

#### Methods

 Method  | Doc
-----|-----
 convert_doc_to_md | Converts all docstrings to markdown
 generate_markdown_for_item | Writes generated markdown to file
 execute_conversion_process | Main driver function




### __init__

```python
def __init__(self, conversion_item_list: ConversionList, output_loc: os.PathLike)
```

Constructor for MDConverter







### convert_doc_to_md

```python
def convert_doc_to_md(self, conversion_item: ConversionItem) -> None
```

Converts docstrings to markdown internally







### generate_markdown_for_item

```python
def generate_markdown_for_item(self, conversion_item: ConversionItem) -> None
```

Generates a markdown file for given conversion item




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 conversion_item  |  ConversionItem | Conversion item for which to create markdown file





### execute_conversion_process

```python
def execute_conversion_process(self) -> None
```

Main Driver function for converter










### generate_conversion_item_list

```python
def generate_conversion_item_list(target: os.PathLike, ignore_list: StringList) -> ConversionList
```

Generates list of all conversion items




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 target  |  os.PathLike | target of python module or package
 ignore_list  |  list of str | List of filenames to ignore

#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 conversion_item_list  |  ConversionList | List of all discovered files as conversion items





### err_exit

```python
def err_exit(message: str, code: int) -> None
```

Exits program with error




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 message  |  str | error message
 code  |  int | exit code





### check_input_output_valid

```python
def check_input_output_valid(target: os.PathLike, output: os.PathLike, ignore_list: StringList) -> (bool, int, str)
```

Checks if given input was valid




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 target  |  os.PathLike | target input location
 output  |  os.PathLike | Markdown output location
 ignore_list  |  list of str | list of filenames to ignore

#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 valid  |  bool | True if valid, false otherwise
 err_code  |  int | Error code if applicable
 err_message  |  str | Error message if applicable





### parse_args

```python
def parse_args() -> (MDConverter, bool)
```

Function that parses user arguments




#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 converter  |  MDConverter | Main converter object
 debug  |  bool | toggle for debug printing





