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

def gen_report(results, sep=','):
    csv = 'student'
    all_errors = set()
    summary = {}
    
    # first we get a list of all the errors that happened
    for student, result in results.items():
        summary[student] = {}
        for error in result:
            code = error['type'].lower() + error['code']
            all_errors.add(code)

            summary[student][code] = summary[student].get(code,0) + 1
            
    all_errors = sorted(list(all_errors))

    # and add all errors to the csv header
    for error in all_errors:
        csv += sep + error
    csv += sep + 'total'

    # now we add each student's result on the csv
    for student, counts in summary.items():
        csv += '\n' + student + sep
        
        for error in all_errors:
           csv += str(counts.get(error, 0)) + sep

        csv += str(sum(counts.values()))

    return BytesIO(csv.encode('utf8'))

if __name__ == '__main__':
    pass
