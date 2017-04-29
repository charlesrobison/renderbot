from mimetypes import MimeTypes

class UploadedFile(file_path):
    """
    Convert file to pandas data frame or return error for invalid file
    """
    def __init__(self, file_path):
        self.file_path = file_path


    def detect_file_type(self):
        """
        Detect file type or raise an error if file type is unsupported
        """
        valid_file_types = ['text/csv': 'csv', 'text/tab-separated-values': 'tsv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx']
        mime = MimeTypes()
        file_type = mime.guess_type(self.file_path)[0]
        if file_type not in valid_file_types:
            raise TypeError
        else:
            self.file_type = valid_file_types[file_type]

    def convert_to_dataframe(self):
        
