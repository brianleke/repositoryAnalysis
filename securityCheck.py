import os
import sys
import json
import subprocess

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
    matches = ['iml', 'target', 'mvnw', 'idea', 'test', '.git']
    if obtainedResults[0] != '':
        for obtainedResult in obtainedResults:
            if not any(condition in obtainedResult for condition in matches):
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
        filteredResult = subprocess.getoutput(commandString)
        modifiedFilter = addArrayElements(modifiedFilter, filteredResult)
    return modifiedFilter

def generateJSONOutputFile(filesWithResults):
    with open('results.json', 'w') as outputFile:
        json.dump(filesWithResults, outputFile, ensure_ascii=False)

def writeHeader(outputTextFileWriter):
    outputTextFileWriter.write("==========================================================\n")
    outputTextFileWriter.write("=================RESULTS OF ANALYSIS======================\n")
    outputTextFileWriter.write("==========================================================\n\n")

def writeObjectResult(outputTextFileWriter, filterObject):
    outputTextFileWriter.write("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    outputTextFileWriter.write("Issue: " + filterObject['caption'] + "\n")
    outputTextFileWriter.write("-----------------------POSSIBLE COMPROMISED FILES-----------------------\n")
    for result in filterObject['results']:
        outputTextFileWriter.write(result + "\n")
    outputTextFileWriter.write("\n-----------------END OF POSSIBLE COMPROMISED FILES----------------------\n")
    outputTextFileWriter.write("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n")

def generateTextFile(filesWithResults):
    with open('results.txt', 'w') as outputTextFile:
        writeHeader(outputTextFile)
        for filterObject in filesWithResults:
            if len(filterObject['results']) > 0:
                writeObjectResult(outputTextFile, filterObject)               

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
            modifiedFilter = getFilesThatMatchFilterForFilenameTypePattern(filters, args, filenameCondition, regexCondition)
            modifiedFilter = getFilesThatMatchFilterForFilenameTypePatternInWord(modifiedFilter, args, filenameCondition, regexCondition)
            modifiedFilter = getFilesThatMatchFilterExtensionExactly(modifiedFilter, args, extensionCondition, matchCondition)
            modifiedFilter = getFilesThatMatchFileNamesExactly(modifiedFilter, args, filenameCondition, matchCondition)

            generateJSONOutputFile(modifiedFilter)
            generateTextFile(modifiedFilter)

            os.system("python3 -m http.server 8080")

        except IndexError:
             raise Usage("Please ensure directory is specified.")
    except Usage as err:
        print >>sys.stderr, err.msg
        return 2

if __name__ == "__main__":
    sys.exit(main())

