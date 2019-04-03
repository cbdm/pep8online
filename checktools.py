#-*- encoding: utf8 -*-
import pycodestyle
from pydocstyle import check
import io
import sys
import os
import tempfile
import re


def template_pycode(temp):
    return {'type': temp[3][1],
            'code': temp[3][2:5],
            'line': temp[1],
            'place': temp[2],
            'text': temp[3][6:]}


def template_results(temp):
    return {'type': temp[0][0],
            'code': temp[0][1:],
            'line': temp[1],
            'place': temp[2],
            'text': temp[3]}


def pycodestyle_parser(strings, temp_dict_f=template_pycode):
    """
    Convert strings from pycodestyle results to list of dictionaries
    """
    result_list = []

    for s in strings.split('\n'):
        temp = re.findall(r"(.+?):(.+?):(.+?):(.*)", s)
        if temp and len(temp[0]) >= 4:
            result_list.append(temp_dict_f(temp[0]))
    return result_list

def pydocstyle_parser(errors, filename, temp_dict_f=template_pycode):
    """
    Convert strings from pydocstyle results to list of dictionaries
    """

    result_list = []
    
    for e in errors:
        line, msg = str(e).split('\n')
        line, msg = line.strip(), msg.strip()
        
        # finds the line number where the function is defined
        colon = line.index(':')
        line = line[colon+1:].split()[0]

        # finds the error number and text       
        code, text = msg.split(': ')
        result_list.append({
            'type': code[0],
            'code': code[1:],
            'line': line,
            'place': 0,
            'text': text
        })

    return result_list

def check_text(text, temp_dir, logger=None):
    """
    check text for pycodestyle and pydocstyle requirements
    """
    #prepare code
    code_file, code_filename = tempfile.mkstemp(dir=temp_dir)
    with open(code_filename, 'w') as code_file:
        code_file.write(text)
    #initialize pycodestyle checker
    pep8style = pycodestyle.StyleGuide(parse_argv=False, config_file=False)
    options = pep8style.options
    #redirect print and get result for codestyle
    temp_outfile = io.StringIO()
    sys.stdout = temp_outfile
    checker = pycodestyle.Checker(code_filename, options=options)
    checker.check_all()
    sys.stdout = sys.__stdout__
    result = temp_outfile.getvalue()
    #checks for pydocstyle
    # checking only for selected errors.
    # List with all possible ones found at http://www.pydocstyle.org/en/stable/error_codes.html
    docstrings_selected_errors = ['D103', 'D200', 'D201', 'D205', 'D209',
            'D210', 'D213', 'D300', 'D301', 'D302', 'D400', 'D402', 'D403', 'D404']
    doc_errors = check([code_filename], select=docstrings_selected_errors)

    fullResultList = pycodestyle_parser(result) +\
        pydocstyle_parser(doc_errors, code_filename)
    fullResultList.sort(key=lambda x: (int(x['line']), int(x["place"])))
    if logger:
        logger.debug(result)

    #clear all
    temp_outfile.close()
    code_file.close()
    os.remove(code_filename)

    return fullResultList


def is_py_extension(filename):
    return ('.' in filename) and (filename.split('.')[-1] == 'py')

if __name__ == '__main__':
    pass
