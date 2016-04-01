# -*- coding: utf-8 -*-
from __future__ import print_function
from alchemyapi import AlchemyAPI

def listToStr(inputList):
    out = ''
    for item in inputList:
        out += item + ' '
    return out

def extractAlchemy(brand, startIndex, stopIndex):
    if startIndex > 0:
        outputAlchemyFile = open('HybridData/Original/' + brand + '.alchemy', 'a')
    else:
        outputAlchemyFile = open('HybridData/Original/' + brand + '.alchemy', 'w')
    contentFile = open('HybridData/Original/' + brand + '.content', 'r')
    content = []

    alchemyapi = AlchemyAPI()

    for line in contentFile:
        content.append(line.strip())

    index = 0
    for item in content:
        if index < startIndex:
            index += 1
            continue
        if index % 1000 == 1:
            print(index)
        try:
            response = alchemyapi.taxonomy('text', item)
            if response['status'] == 'OK':
                output = ''
                for category in response['taxonomy']:
                    output = output + category['label'].replace(' ', '_') + ':' + category['score'] + ' '
                outputAlchemyFile.write(output + '\n')
            else:
                outputAlchemyFile.write('ERROR\n')
        except:
            print('Error in calling Alchemy')
        index += 1
        if index > stopIndex:
            break

    outputAlchemyFile.close()


def fixAlchemy(brand):
    contentFile = open('HybridData/Original/' + brand + '.content', 'r')
    content = []
    for line in contentFile:
        content.append(line.strip())
    contentFile.close()

    alchemyFile = open('HybridData/Original/' + brand + '.alchemy', 'r')
    data = {}
    fixList = []
    lineCount = 0
    for index, line in enumerate(alchemyFile):
        lineCount += 1
        items = line.strip().split(' ')

        if len(items) < 4:
            fixList.append(index)
        elif items[0] == 'ERROR':
            fixList.append(index)
        data[index] = listToStr(items)
    alchemyFile.close()

    print ('Recalling Alchemy API...')
    alchemyapi = AlchemyAPI()
    fixOutput = []
    for index in fixList:
        try:
            response = alchemyapi.taxonomy('text', content[index])
            if response['status'] == 'OK':
                output = ''
                for category in response['taxonomy']:
                    output = output + category['label'].replace(' ', '_') + ':' + category['score'] + ' '
                fixOutput.append(output.strip())
            else:
                fixOutput.append('ERROR')
        except:
            print('Error in calling Alchemy')

    for index, lineNum in enumerate(fixList):
        data[lineNum] = fixOutput[index]

    outputFile = open('HybridData/Original/' + brand + '.alchemy2', 'w')
    for index in range(lineCount):
        outputFile.write(data[index]+'\n')
    outputFile.close()


def cleanFiles(brand):
    contentFile = open('HybridData/Original/' + brand + '.content', 'r')
    content = []
    for line in contentFile:
        content.append(line)
    contentFile.close()

    keyword = []
    labelFile = open('HybridData/Original/' + brand + '.keyword', 'r')
    for line in labelFile:
        keyword.append(line)
    labelFile.close()

    alchemyFile = open('HybridData/Original/' + brand + '.alchemy', 'r')
    alchemy = []
    exceptList = []
    for index, line in enumerate(alchemyFile):
        items = line.strip().split(' ')
        if len(items) < 3:
            exceptList.append(index)
        elif items[0] == 'ERROR':
            exceptList.append(index)
        alchemy.append(line)
    alchemyFile.close()

    contentOutputFile = open('HybridData/Original/' + brand + '.content2', 'w')
    labelOutputFile = open('HybridData/Original/' + brand + '.keyword2', 'w')
    alchemyOutputFile = open('HybridData/Original/' + brand + '.alchemy2', 'w')
    for index, line in enumerate(content):
        if index not in exceptList:
            contentOutputFile.write(line)
            labelOutputFile.write(keyword[index])
            alchemyOutputFile.write(alchemy[index])

    contentOutputFile.close()
    labelOutputFile.close()
    alchemyOutputFile.close()

if __name__ == "__main__":
    brand = 'POCruisesAustralia'
    startIndex = 0
    stopIndex = 15255

    extractAlchemy(brand, startIndex, stopIndex)
    #fixAlchemy(brand)
    #cleanFiles(brand)