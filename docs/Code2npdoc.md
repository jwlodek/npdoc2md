# code2npdoc

Python script meant to automate the creation of numpy-style docstrings.



Designed to be used to autocreate base np docs for python projects,
that are then used to create markdown docs for mkdocs with the npdoc2md
script.  

@author: Jakub Wlodek  
@created: Feb-25-2020

#### Classes

 Class  | Doc
-----|-----
 DocStringAttribute | Class representing a docstring attr table
 GenerationInstance | Class representing a function/class/method
 ModuleGenerationInstance | Top level instance class for module
 GenerationItem | Main Docstring generator
 DocGenerator | Main Driver object

#### Functions

 Function  | Doc
-----|-----
 generate_generation_item_list | Spawns generation item list given package path
 err_exit | Exits with error code
 check_input_output_valid | Checks if inputs are valid
 print_version_info | Prints version and copyright info
 parse_args | Parses arguments
 main | Main function




## DocStringAttribute

```python
class DocStringAttribute
```

Class representing a docstring attr table




#### Attributes

 Attribute  | Type  | Doc
-----|----------|-----
 attribute_name  |  str | Name of the attribute
 attribute_elements  |  List[str] | list of attribute elements




### __init__

```python
def __init__(self, attribute_name : str, elements : List[str])
```

Initializer for docstring attribute










## GenerationInstance

```python
class GenerationInstance
```

Class representing a function/class/method




#### Attributes

 Attribute  | Type  | Doc
-----|----------|-----
 name  |  str | Name of the instance
 descriptors  |  DocStringAttribute | Descriptors for instance (Returns, Parameters, etc.)
 doc_level  |  int | required tabs

#### Methods

 Method  | Doc
-----|-----
 add_descriptor | Adds new descriptor to the instance
 make_descriptor_string | Generates docstring for instance




### __init__

```python
def __init__(self, name : str, doc_level : int)
```

Initializer for GenerationInstance







### add_descriptor

```python
def add_descriptor(self, name : str, elements : List[str])
```

Adds new descriptor to the instance




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 name  |  str | Name of the descriptor
 elements  |  List[str] | Descriptor elements





### make_descriptor_string

```python
def make_descriptor_string(self)
```

Generates docstring for instance




#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 desc_string  |  str | String generated for descriptor








## ModuleGenerationInstance

```python
class ModuleGenerationInstance
```

Top level instance class for module




#### Attributes

 Attribute  | Type  | Doc
-----|----------|-----
 original_module_text  |  str | text from module
 sub_gen_items  |  GenerationInstance | instances parsed from module

#### Methods

 Method  | Doc
-----|-----
 get_generated | Writes new file with docstrings
 return_match | Matches line of original text to generation item for inserting docstring




### __init__

```python
def __init__(self, name : str, original_module_text : List[str])
```

Initializer for ModuleGenerationInstance







### get_generated

```python
def get_generated(self)
```

Writes new file with docstrings




#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 out  |  str | The original file text with docstrings





### return_match

```python
def return_match(self, line : str)
```

Matches line of original text to generation item for inserting docstring




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 line  |  str | line of text

#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 match  |  List[str, int, str] | Collects instance information for writing stage








## GenerationItem

```python
class GenerationItem
```

Main Docstring generator




#### Attributes

 Attribute  | Type  | Doc
-----|----------|-----
 target  |  str | target file path
 overwrite  |  bool | toggle for overriding target
 temp_file  |  str | temp file path
 module_gen_instance  |  ModuleGenerationInstance | the instance for the target module

#### Methods

 Method  | Doc
-----|-----
 create_module_gen_instance | Parses file into ModuleGenerationInstance
 generate_np_docs | Top level driver function for docstring generation




### __init__

```python
def __init__(self, target_file_path : os.PathLike, overwrite : bool)
```

Initializer for GenerationItem







### create_module_gen_instance

```python
def create_module_gen_instance(self) -> ModuleGenerationInstance
```

Parses file into ModuleGenerationInstance




#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 mod_instance  |  ModuleGenerationInstance | generated instance with subinstances added





### generate_np_docs

```python
def generate_np_docs(self) -> None
```

Top level driver function for docstring generation










## DocGenerator

```python
class DocGenerator
```

Main Driver object




#### Attributes

 Attribute  | Type  | Doc
-----|----------|-----
 target  |  str | target location
 ignore_list  |  List[str] | list of files to ignore

#### Methods

 Method  | Doc
-----|-----
 generate_docs | Top level driver function




### __init__

```python
def __init__(self, target : os.PathLike, ignore_list : List[str])
```

Initializer for DocGenerator







### generate_docs

```python
def generate_docs(self, overwrite)
```

Top level driver function




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 overwrite  |  bool | toggle for overwriting files








### generate_generation_item_list

```python
def generate_generation_item_list(target: os.PathLike, ignore_list: List[str], overwrite : bool) -> List[GenerationItem]
```

Spawns generation item list given package path




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 target |  os.PathLike | package path
 ignore_list |  List[str] | files to ignore
 overwrite  |  bool | overwrite files toggle

#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 generation_item_list  |  List[GenerationItem] | list of GenerationItems, with each representing one module





### err_exit

```python
def err_exit(message: str, code: int) -> None
```

Exits with error code




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 message |  str | Error message
 code |  int | Error code





### check_input_output_valid

```python
def check_input_output_valid(target: os.PathLike, ignore_list: List[str]) -> (bool, int, str)
```

Checks if inputs are valid




#### Parameters

 Parameter  | Type  | Doc
-----|----------|-----
 target |  os.PathLike | target file path
 ignore_list |  List[str] | list of files to ignore

#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 valid  |  bool | Are the inputs and outputs valid
 err_code  |  int | Error code to display if applicable
 err_message  |  str | Error message





### print_version_info

```python
def print_version_info() -> None
```

Prints version and copyright info







### parse_args

```python
def parse_args()
```

Parses arguments




#### Returns

 Return Variable  | Type  | Doc
-----|----------|-----
 generator  |  DocGenerator | Main Generator object
 not args['createtemp']  |  bool | Toggle for overwriting files





### main

```python
def main()
```

Main function







