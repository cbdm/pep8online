#-*- encoding: utf8 -*-
from zipfile import ZipFile
from flask import flash
import io
import sys
import os
from os.path import join, exists
import tempfile
import re
from pylama.main import check_path, parse_options

def pylama_parser(error_list):
    """
    parses the error list returned by pylama
    """
    result_list = []

    for error in error_list:
        _text = error.get('text').split()
        _type = _text[0][0]
        _code = _text[0][1:]
        _linter = _text[-1][1:-1]
        _text = ' '.join(_text[1:-1])
        
        _error = {
                'type': _type,
                'code': _code,
                'line': error.get('lnum'),
                'place': error.get('col'),
                'text': _text,
                'linter': _linter
        }

        # checks if it's a new error
        # (i.e., another linter hasn't detected the same error at the same place)
        if  result_list == [] or \
            result_list[-1]['line'] != _error['line'] or \
            result_list[-1]['place'] != _error['place'] or \
            result_list[-1]['type']+result_list[-1]['code'] != _error['type']+_error['code']:
           
            result_list.append(_error)

    return result_list

def check_text(text, temp_root, logger=None):
    """
    check text for pycodestyle and pydocstyle requirements
    """
    # creates a new temporary directory to extract the submissions
    temp_dir = tempfile.TemporaryDirectory(dir=temp_root)
    #prepare code
    code_file, code_filename = tempfile.mkstemp(suffix='.py', dir=temp_dir.name)

    with open(code_filename, 'w') as code_file:
        code_file.write(text)
    
    pylama_options = {
    'linters': ['pep257', 'pydocstyle', 'pycodestyle', 'pyflakes', 'pylint']
    }
    pylama_path = temp_dir.name
    options = parse_options([pylama_path], **pylama_options)
    
    errors = check_path(options, rootdir='.')
    results = pylama_parser(errors)

    results.sort(key=lambda x: (int(x['line']), int(x["place"])))

    if logger:
        logger.debug(results)

    #clear all
    code_file.close()
    os.remove(code_filename)

    return results

def check_submissions(submissions, filename, temp_root):
    """
    checks all zybooks submissions in a zipfile
    """
    def _parse_student(current_sub, separator='_', domain='uci.edu'):
        """
        parses the student's net ID from the zybooks submission filename
        """
        data = current_sub.split(separator)
        for d in data:
            if d.endswith(domain):
                return d[:-len(domain)].lower()

    results = {}

    # creates a new temporary directory to extract the submissions
    temp_dir = tempfile.TemporaryDirectory(dir=temp_root)
    # updates the filename to look in the temporary dir
    filename = join(temp_dir.name, filename)
    if not is_py_extension(filename):
        filename += '.py'

    # creates a temporary file that can be extracted
    zip_file, zip_filename = tempfile.mkstemp(dir=temp_dir.name)

    with open(zip_filename, 'wb') as zip_file:
        zip_file.write(submissions)

    # extracts all students' submissions
    zip_ref = ZipFile(zip_filename, 'r')
    zip_ref.extractall(temp_dir.name)
    zip_ref.close()

    # removes the temp file
    zip_file.close()
    os.remove(zip_filename)

    valid_filename = True

    # loops through all submissions
    for submission in os.listdir(temp_dir.name):
        student = _parse_student(submission)

        if student == None: continue
    
        # unzips the code of current student
        zip_ref = ZipFile(join(temp_dir.name,submission), 'r')
        zip_ref.extractall(temp_dir.name)
        zip_ref.close()

        try:
            with open(filename, 'r') as code_file:
                res = check_text(code_file.read(),temp_dir.name)
                results[student] = res
        except:
            if valid_filename:
                valid_filename = False
                flash('Double check the python filename.', 'warning')

        # removes student's code that we just analyzed
        if exists(filename):
            os.remove(filename)

    return results

def is_py_extension(filename):
    return ('.' in filename) and (filename.split('.')[-1] == 'py')

if __name__ == '__main__':
    pass
