import numpy as np
from collections import defaultdict

def dumpDictToCSV(dictList, csvFile, delimiter, header):
    """
    Purpose: dumps dictionary to CSV file

    Usage: dumpDictToCSV(dictList, csvFile, delimiter, header)

    Input:
        DictList- Dictionary of data. Each key points to a list of the same length
        csvFile - Name of CSV file to store the exploded structure, one column per
                key of dictList. For input later to Excel if desired.
        delimiter - Character used to uniquely separate the cells of the
                spreadsheet by row. This character must not exist in any
                of the string values contained in dictList or its keys.
        header  - list of keys in order for output columns. These must match the
                keys, but possibly in different order

    Output:
        The CSV file in cvsFile contains the dictionary data where the first
        row is a header line of dictionary keys for the columns.
    """

    ncols = len(header)
    nrows = len(dictList[header[0]])
    newline = '\n'

    # ensure header is enclosed in double quotes
    quote_header = []
    for n in range(ncols):
        quote_header.append(f'"{header[n]}"')

    fileObj=open(csvFile, 'w')
    fileObj.write(delimiter.join(quote_header)+newline)

    for row in range(nrows):
        dumpLine=[]
        for col in range(ncols):
            if isinstance(dictList[header[col]][row], str):
                dumpLine.append('"'+dictList[header[col]][row]+'"')
            else:
                dumpLine.append(str(dictList[header[col]][row]))

        fileObj.write(delimiter.join(dumpLine)+newline)

    fileObj.close
