#-*- encoding: utf8 -*-
from io import BytesIO


def gen_text_file(text):
    text_file = BytesIO()
    text_file.write(text.encode('utf8'))
    text_file.seek(0)
    return text_file


def gen_result_text(result, code):
    print(result)
    """Generate text for file from checking result and code"""
    text_list = ["Check results",
                 "=============",
                 ""]
    text_list.extend(result.split(":::"))
    text_list.extend(["",
                      "Code",
                      "============="])
    text_list.append(code)
    print(text_list)
    return '\n'.join(text_list)

if __name__ == '__main__':
    pass
