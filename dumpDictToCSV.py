from collections import defaultdict

def dumpDictToCSV(dictList, csvFile, delimiter, header, encoding='utf-8'):
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
        encoding - Specify encoding if some characters are not utf-8

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

    fileObj=open(csvFile, 'w', encoding=encoding)
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

def dumpDictArrayToCSV(dictArray, csvFile, delimiter, header, encoding='utf-8'):
    """
    Purpose: dumps dictionary array to CSV file

    Usage: dumpDictArrayToCSV(dictList, csvFile, delimiter, header)

    Input:
        dictArray- Dictionary array, all with the same keys.
        csvFile - Name of CSV file to store the exploded structure, one column per
                key in DictArray. For input later to Excel if desired.
        delimiter - Character used to uniquely separate the cells of the
                spreadsheet by row. This character must not exist in any
                of the string values contained in dictList or its keys.
        header  - list of keys in order for output columns. These must match the
                keys, but possibly in different order
        encoding - Specify encoding if some characters are not utf-8

    Output:
        The CSV file in cvsFile contains the dictionary data where the first
        row is a header line of dictionary keys for the columns.
    """

    ncols = len(header)
    newline = '\n'

    # ensure header is enclosed in double quotes
    quote_header = []
    for n in range(ncols):
        quote_header.append(f'"{header[n]}"')

    fileObj=open(csvFile, 'w', encoding=encoding)
    fileObj.write(delimiter.join(quote_header)+newline)

    for dict in dictArray:
        dumpLine=[]
        for col in range(ncols):
            if isinstance(dict[header[col]], str):
                dumpLine.append('"'+dict[header[col]]+'"')
            else:
                dumpLine.append(str(dict[header[col]]))
        fileObj.write(delimiter.join(dumpLine)+newline)

    fileObj.close
