import csv

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

def dumpListDictToCSV(listDict, csvName, delimiter, header):
    """
    Purpose: dumps dictionary array to CSV file

    Usage: dumpListDictToCSV(dictList, csvName, delimiter, header)

    Input:
        listDict- Dictionary array, all with the same keys.
        csvName - Name of CSV file to store the exploded structure, one column per
                key in listDict. For input later to Excel if desired.
        delimiter - Character used to uniquely separate the cells of the
                spreadsheet by row. This character must not exist in any
                of the string values contained in dictList or its keys.
        header  - list of keys in order for output columns. These must match the
                keys, but possibly in different order

    Output:
        The CSV file in cvsFile contains the dictionary data where the first
        row is a header line of dictionary keys for the columns.
        To accommodate rare weird characters, output is encoded 'utf-8'
    """

    with open(csvName, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for dict in listDict:
            writer.writerow(dict)
