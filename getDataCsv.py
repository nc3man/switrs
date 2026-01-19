import csv
from collections import defaultdict
from charset_normalizer import from_path


def getDataCsv( csvFile, delimiter, pivot=False, encoding='best_guess'):
    """
    Usage: data, header = getDataCsv( csvFile, delimiter, pivot=False )
    
    Purpose: reads a CSV file from Excel of SDCBC membership and contribution data
                                    
    Input:
      csvFile - Name of spreadsheet in CSV format. Assumptions:
                Strings may be quoted with double quotes '"'
                The delimiter is not in any column without double quotes.
      delimiter - Character used to uniquely separate the cells of the
                  spreadsheet by row.
      pivot   - If true, the data which is a single dictionary with keys for each csv column
                is pivoted to an array (length=nrows) of dicts with the same keys. 
                [default: False]
      encoding - Optional if the csv reader encounters weird characters. default utf-8
                 Can use the chardet python package to query for correct encoding.

    Output:
      data - Dictionary of CSV data. Keys are the header columns in the
             CSV file. Each key returns the column as a list of strings or numbers.
             If pivot = True, an array of dictionaries for each row, keys = header
      header  - Save header values in same order as input on CSV file. The keys
                in the members dictionary will match the header list, but in possibly
                different order.
    """

    data = defaultdict(list)
    
    # in case an unexpected charset was used for the text file
    if encoding=='best_guess':
        results = from_path(csvFile)
        best_guess = results.best()
        encoding = best_guess.encoding
    
    ## open the file and attach the CSV reader object
    
    with open(csvFile, encoding=encoding) as csvf:
        reader = csv.reader(csvf, delimiter=delimiter, quotechar='"')
        for row in reader:
            if reader.line_num==1:                     
                ## pull the header strings from the first line
                header = row
                ncols = len(header)
                
                while len(header[-1])==0:  # check to see if last field is nil
                    ncols = ncols-1
                    del(header[ncols])
                    
                # remove leading and trailing whitespace that could clutter header
                header = [h.strip() for h in header]

            else:
                ## append each row to a growing dictionary. Keys are the header 
                # fields and each column is just a list of strings to begin with
                for i in range(ncols):
                    data[header[i]].append(row[i])
    if not pivot:
        return(data, header)
    else:
        return(pivot_data(data,header), header)
        
def pivot_data(data,header):
        nrows = len(data[header[0]])
        ncols = len(header)
        data_pivot = [None] * nrows
        for n in range(nrows):
            row_dict = dict.fromkeys(header)
            for j in range(ncols):
                row_dict[header[j]] = data[header[j]][n]
            data_pivot[n] = row_dict
            
        return(data_pivot)
        
def rename_keys(data, old_keys, new_keys):
    key_map = dict(zip(old_keys, new_keys))
    
    return [
        {key_map[k]: v for k, v in d.items() if k!=None} for d in data
    ]

        
def getListDictCsv( csvFile, delimiter, encoding='best_guess'):
    """
    Usage: data, header = getDataCsv( csvFile, delimiter)
           This function is a more efficient version of getDataCSV with pivot=True
    
    Purpose: reads a CSV file from Excel of SDCBC membership and contribution data
                                    
    Input:
      csvFile - Name of spreadsheet in CSV format. Assumptions:
                Strings may be quoted with double quotes '"'
                The delimiter is not in any column without double quotes.
      delimiter - Character used to uniquely separate the cells of the
                  spreadsheet by row.
      encoding - Optional if the csv reader encounters weird characters. default utf-8
                 Can use the charset python package to query for correct encoding.

    Output:
      data - List (dictionaries of csv data). Output is one dictionary per row 
      header  - Keys for each row in the dictionary. Each row has the same keys
    """
    listDict = []
    
    # in case an unexpected charset was used for the text file
    if encoding=='best_guess':
        results = from_path(csvFile)
        best_guess = results.best()
        encoding = best_guess.encoding

    # use efficient DictReader method
    with open(csvFile, newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            listDict.append(row)
            
    header = list(listDict[0].keys())
    
    # there should be no leading / trailing whitespace (blanks and tabs) in header
    header_strip = [h.strip() for h in header]
    if header_strip != header:
        listDict = rename_keys(listDict, header, header_strip)
        header = header_strip

    return(listDict, header)
 
