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

def addArrayElements(modifiedFilterList, retrievedResults):
    obtainedResults = retrievedResults.split('\n')
    if obtainedResults[0] != '':
        for obtainedResult in obtainedResults:
            modifiedFilterList['results'].append(obtainedResult)
    return modifiedFilterList


def getFilesThatMatchFilterForFilenameTypePattern(filters, path, firstCondition, secondCondition):
    results = []
    for filter in filters:
        filter['results'] = []
        commandString = 'find ' + path + ' -iname "*'+ filter['pattern'] +'"'
        results.append(populateFilterResults(filter, commandString, firstCondition, secondCondition))
    return results

def getFilesThatMatchFilterForFilenameTypePatternInWord(filters, path, firstCondition, secondCondition):
    results = []
    for filter in filters:
        commandString = 'grep -l -R "' + filter['pattern'] + '" ' + path
        results.append(populateFilterResults(filter, commandString, firstCondition, secondCondition))
    return results


def getFilesThatMatchFilterExtensionExactly(filters, path, firstCondition, secondCondition):
    results = []
    for filter in filters:
        commandString = 'find ' + path + ' -iname "*.'+ filter['pattern'] +'"'
        results.append(populateFilterResults(filter, commandString, firstCondition, secondCondition))
    return results

def getFilesThatMatchFileNamesExactly(filters, path, firstCondition, secondCondition):
    results = []
    for filter in filters:
        commandString = 'find ' + path + ' -type f -name "'+ filter['pattern'] +'"'
        results.append(populateFilterResults(filter, commandString, firstCondition, secondCondition))
    return results

def populateFilterResults(filter, commandString, firstCondition, secondCondition):
    modifiedFilter = filter;
    if filter['part'] == firstCondition and filter['type'] == secondCondition:
        filteredResult = commands.getoutput(commandString)
        modifiedFilter = addArrayElements(modifiedFilter, filteredResult)
    return modifiedFilter

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
    filenameCondition = 'filename'
    extensionCondition = 'extension'
    matchCondition = 'match'
    regexCondition = 'regex'

    if argv is None:
        argv = sys.argv
    try:
        try:
            args = argv[1]
            files = get_filepaths(args)
            modifiedFilter = getFilesThatMatchFilterForFilenameTypePattern(filters, args, filenameCondition, regexCondition)
            modifiedFilter = getFilesThatMatchFilterForFilenameTypePatternInWord(modifiedFilter, args, filenameCondition, regexCondition)
            modifiedFilter = getFilesThatMatchFilterExtensionExactly(modifiedFilter, args, extensionCondition, matchCondition)
            modifiedFilter = getFilesThatMatchFileNamesExactly(modifiedFilter, args, filenameCondition, matchCondition)

            generateJSONOutputFile(modifiedFilter)
            generateTextFile(modifiedFilter)
        except IndexError:
             raise Usage("Please ensure directory is specified.")
    except Usage, err:
        print >>sys.stderr, err.msg
        return 2

if __name__ == "__main__":
    sys.exit(main())

