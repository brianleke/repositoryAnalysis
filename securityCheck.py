import os
import sys
import getopt
import json
from pprint import pprint
import commands

def get_filepaths(directory):
    file_paths = []

    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    return file_paths


def getRegexFilters():
    data = {}

    with open('patterns.json') as data_file:    
        data = json.load(data_file)
    return data

def getFilesThatMatchFilterForFilenameTypePattern(filters, path):
    results = []
    for filter in filters:
        modifiedFilter = filter;
        if filter['part'] == 'filename' and filter['type'] == 'regex':
            filteredResult = commands.getoutput('find ' + path + ' -iname "*'+ filter['pattern'] +'"')
            modifiedFilter['results'] = filteredResult.split('\n') if filteredResult.split('\n')[0] != '' else []
        else:
            modifiedFilter['results'] = []
        results.append(modifiedFilter)
    return results

def getFilesThatMatchFilterForFilenameTypePatternInWord(filters, path):
    results = []
    for filter in filters:
        modifiedFilter = filter;
        if filter['part'] == 'filename' and filter['type'] == 'regex':
            filteredResult = commands.getoutput('grep -l -R "' + filter['pattern'] + '" ' + path)
            modifiedFilter = addArrayElements(modifiedFilter, filteredResult)
        results.append(modifiedFilter)
    return results

def addArrayElements(modifiedFilterList, retrievedResults):
    obtainedResults = retrievedResults.split('\n')
    if obtainedResults[0] != '':
        for obtainedResult in obtainedResults:
            modifiedFilterList['results'].append(obtainedResult)
    return modifiedFilterList

def getFilesThatMatchFilterExtensionExactly(filters, path):
    results = []
    for filter in filters:
        modifiedFilter = filter;
        if filter['part'] == 'extension' and filter['type'] == 'match':
            filteredResult = commands.getoutput('find ' + path + ' -iname "*.'+ filter['pattern'] +'"')
            modifiedFilter['results'] = filteredResult.split('\n') if filteredResult.split('\n')[0] != '' else []
        results.append(modifiedFilter)
    return results

def getFilesThatMatchFileNamesExactly(filters, path):
    results = []
    for filter in filters:
        modifiedFilter = filter;
        if filter['part'] == 'filename' and filter['type'] == 'match':
            filteredResult = commands.getoutput('find ' + path + ' -type f -name "'+ filter['pattern'] +'"')
            modifiedFilter['results'] = filteredResult.split('\n') if filteredResult.split('\n')[0] != '' else []
        results.append(modifiedFilter)
    return results


def generateJSONOutputFile(filesWithResults):
    with open('results.json', 'w') as outputFile:
        json.dump(filesWithResults, outputFile, ensure_ascii=False)

def generateTextFile(filesWithResults):
    with open('results.txt', 'w') as outputTextFile:
        outputTextFile.write("==========================================================\n")
        outputTextFile.write("=================RESULTS OF ANALYSIS======================\n")
        outputTextFile.write("==========================================================\n\n")
        for filterObject in filesWithResults:
            if len(filterObject['results']) > 0:
                outputTextFile.write("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
                outputTextFile.write("Issue: " + filterObject['caption'] + "\n")
                outputTextFile.write("-----------------------POSSIBLE COMPROMISED FILES-----------------------\n")
                for result in filterObject['results']:
                    outputTextFile.write(result + "\n")
                outputTextFile.write("\n-----------------END OF POSSIBLE COMPROMISED FILES----------------------\n")
                outputTextFile.write("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n")

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    filters = getRegexFilters();

    if argv is None:
        argv = sys.argv
    try:
        try:
            args = argv[1]
            files = get_filepaths(args)
            modifiedFilter = getFilesThatMatchFilterForFilenameTypePattern(filters, args)
            modifiedFilter = getFilesThatMatchFilterForFilenameTypePatternInWord(modifiedFilter, args)
            modifiedFilter = getFilesThatMatchFilterExtensionExactly(modifiedFilter, args)
            modifiedFilter = getFilesThatMatchFileNamesExactly(modifiedFilter, args)

            generateJSONOutputFile(modifiedFilter)
            generateTextFile(modifiedFilter)
        except IndexError:
             raise Usage("Please ensure directory is specified.")
    except Usage, err:
        print >>sys.stderr, err.msg
        return 2

if __name__ == "__main__":
    sys.exit(main())

