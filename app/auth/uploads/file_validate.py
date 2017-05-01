from mimetypes import MimeTypes
import pandas as pd


def detect_file_type(file):
    """
    Detect file type or raise an error if file type is unsupported
    """
    valid_file_types = {'text/csv': 'csv', 'text/tab-separated-values': 'tsv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx'}
    mime = MimeTypes()
    file_type = mime.guess_type(file)
    print(file_type)
    if file_type[0] not in valid_file_types:
        raise TypeError
    else:
        file_type = valid_file_types[file_type]
    return file_type


def has_valid_headers(file, file_type, header_list):
    # this is a file obejct, it assumes a file path
    if file_type == 'csv':
        # print(pd.read_csv(file))
        headers = pd.read_csv(file, encoding='ISO-8859-1').columns.values.tolist()
    elif file_type == 'tsv':
        headers = pd.read_csv(file, encoding='ISO-8859-1', sep='\t').columns.values.tolist()
    elif file_type == 'xlsx':
        headers = pd.read_excel(file, encoding='ISO-8859-1').columns.values.tolist()
    for header in header_list:
        if header not in headers:
            return False
    return True
