import pytest
import npdoc2md


def test_generate_md_table_from_descriptor():
    instance = npdoc2md.ItemInstance('test')
    instance.descriptors = {
        'Attributes' : [['attrA', 'int', 'This is attrA'], ['attrB', 'str', 'This is attrB']]
    }
    md = instance.generate_md_table_from_descriptor('Attributes')
    expected = ' Attributes  | Type  | Doc\n-----|----------|----------|-----\n attrA | int | This is attrA\n attrB | str | This is attrB'
    assert md == expected


def test_assign_docstring_to_instance():
    instance = npdoc2md.FunctionInstance('test', 'def test()')
    doc_string_lines = ['    """Shows loading bar popup.', 
                        '    \n', 
                        "    Use 'increment_loading_bar' to show progress", 
                        '    \n',
                        '    Parameters', 
                        '    ----------', 
                        '    title : str',
                        '        Message title',
                        '    num_items : int',
                        '        Number of items to iterate through for loading',
                        '    callback=None : Function',
                        '        If not none, fired after loading is completed. Must be a no-arg function',
                        ]
    npdoc2md.add_docstring_to_instance(instance, doc_string_lines)
    print(f'{instance.convert_to_markdown(3)}')
    assert False
