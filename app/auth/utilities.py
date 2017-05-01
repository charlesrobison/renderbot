import pandas as pd

def create_df(file, file_type):
    # Get file from server to process into data frame
    if file_type == 'csv':
        # Load CSV file type
        df = pd.DataFrame(pd.read_csv(file, encoding='ISO-8859-1'))
    elif file_type == 'tsv':
        df = pd.DataFrame(pd.read_csv(file, encoding='ISO-8859-1', sep='\t'))
    else:
        # Load files with excel based file extensions
        df = pd.DataFrame(pd.read_excel(file, encoding='ISO-8859-1'))
    return df

def create_df_with_parse_date(file, file_type, parse):
    if file_type == 'csv':
        # Load CSV file type
        df = pd.DataFrame(pd.read_csv(file, encoding='ISO-8859-1', parse_dates=[parse]))
    elif file_type == 'tsv':
        df = pd.DataFrame(pd.read_csv(file, encoding='ISO-8859-1', sep='\t', parse_dates=[parse]))
    else:
        # Load files with excel based file extensions
        df = pd.DataFrame(pd.read_excel(file, encoding='ISO-8859-1', parse_dates=[parse]))
    return df
