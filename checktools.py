#-*- encoding: utf8 -*-
from zipfile import ZipFile
from flask import flash
import io
import sys
import os
from os.path import join, exists
from ignored import ignored_errors
import tempfile
import re
from pylama.main import check_path, parse_options
from py_compile import compile

class DisplayError(object):
    def __init__(self, error):
        _text = error.get('text').split()
        self.type = _text[0][0]
        self.code = _text[0][1:]
        self.linter = _text[-1][1:-1]
        self.text = ' '.join(_text[1:-1])
        self.line = error.get('lnum')
        self.place =  error.get('col')

    def merge(self, other):
        if isinstance(other, DisplayError):
            self.linter += ', ' + other.linter

    def __eq__(self, other):
        if not isinstance(other, DisplayError):
            return False
        
        return self.type == other.type and self.code == other.code and self.line == other.line and self.place == self.place
    
    def __gt__(self, other):
        if not isinstance(other, DisplayError):
            return False
        
        if self.line > other.line:
            return True
        elif self.line == other.line and self.place > other.place:
            return True
        
        return False

    def __hash__(self):
        return '{}/{}/{}'.format(self.type+self.code, self.line, self.place)

def repeated_error(error_list, new_error):
    """
    checks if the detected error is not repeated

    i.e., another linter hasn't detected the same error at the same place
    if it is repeated, update the list of linters that encountered the error
    """
    # starts at the last index as the new error is going to be added after that
    i = len(error_list)-1
    
    while i >= 0:
        # checks if the error was caught on the same line
        if error_list[i]['line'] == new_error['line']:
            
            # checks if it's the same error
            if error_list[i]['type']+error_list[i]['code'] == new_error['type']+new_error['code']:
                
                # if it is, update the list of linters that encountered it
                # and then returns True to indicate that's a repeated one
                error_list[i]['linter'] += ', ' + new_error['linter']
                return True

            # if it's not the same error, go back one index to check the previous error
            i -= 1
        
        # if we are above the new error's line, then it's not a repeated error
        else:
            break
    
    # if reached the end, we haven't encountered a repeated error
    return False

def pylama_parser(error_list, compiled):
    """
    parses the error list returned by pylama
    """
    result_list = []
    
    # custom error in case the student's file could not be parsed
    if not compiled:
        result_list.append({
            'type': 'SYN',
            'code': '000',
            'line': 0,
            'place': 0,
            'text': 'Cannot parse your file! Fix any syntax errors and try again.'
        })

    # parses the information of each detected error
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

        # adds the current error if it wasn't detected before by another linter
        if not repeated_error(result_list, _error):
            result_list.append(_error)

    return result_list

def check_text(text, temp_root, logger=None):
    """
    check code for style requirements using PyLama
    """
    # creates a new temporary directory to extract the submission
    with tempfile.TemporaryDirectory(dir=temp_root) as temp_dir:
        
        # creates a temporary file to write the code to
        code_file, code_filename = tempfile.mkstemp(suffix='.py', dir=temp_dir)

        # writes the code to the file
        with open(code_filename, 'w') as code_file:
            code_file.write(text)
        
        # first checks if the file can be compiled
        # i.e., there are no syntax errors in the file
        compiled = True
        try:
            compile(code_filename, doraise=True)
        except:
            compiled = False

        # configures and runs pylama to analyze the temp file
        global ignored_errors
        pylama_options = {
            'linters': ['pep257', 'pydocstyle', 'pycodestyle', 'pyflakes', 'pylint'],
            'ignore' : list(ignored_errors.keys())
        }
        pylama_path = temp_dir
        options = parse_options([pylama_path], **pylama_options)
        errors = check_path(options, rootdir='.')

        # parses and sorts the errors received
        results = pylama_parser(errors, compiled)
        results.sort(key=lambda x: (int(x['line']), int(x['place'])))

        if logger:
            logger.debug(results)

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
    with tempfile.TemporaryDirectory(dir=temp_root) as temp_dir:
        # updates the filename to look in the temporary dir
        filename = join(temp_dir, filename)
        if not is_py_extension(filename):
            filename += '.py'

        # creates a temporary file that can be extracted
        zip_file, zip_filename = tempfile.mkstemp(dir=temp_dir)

        with open(zip_filename, 'wb') as zip_file:
            zip_file.write(submissions)

        # extracts all students' submissions
        zip_ref = ZipFile(zip_filename, 'r')
        zip_ref.extractall(temp_dir)
        zip_ref.close()

        # removes the temp file
        zip_file.close()
        os.remove(zip_filename)

        valid_filename = True

        # loops through all submissions
        for submission in os.listdir(temp_dir):
            student = _parse_student(submission)

            if student == None: continue
        
            # unzips the code of current student
            zip_ref = ZipFile(join(temp_dir,submission), 'r')
            zip_ref.extractall(temp_dir)
            zip_ref.close()

            try:
                with open(filename, 'r') as code_file:
                    res = check_text(code_file.read(),temp_dir)
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
