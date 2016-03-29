import textCleaner
import random
import operator

def readData(docFileName, labelFileName):
    docFile = open(docFileName, 'r')
    labelFile = open(labelFileName, 'r')

    docOutput = []
    labelOutput = []
    labelCorpus = {}

    for line in labelFile:
        labels = line.strip().replace('"', '').split(' ')
        index = random.randint(0, len(labels)-1)
        output = labels[index]
        labelOutput.append(output)
        if output not in labelCorpus:
            labelCorpus[output] = 1.0
        else:
            labelCorpus[output] += 1.0
    labelFile.close()

    for line in docFile:
        docOutput.append(textCleaner.tweetCleaner(line.strip().lower()))
    docFile.close()

    candLabel = max(labelCorpus.iteritems(), key=operator.itemgetter(1))[0]

    return docOutput, labelOutput, candLabel


def readData2(labelFileName, alchemyFileName):
    labelFile = open(labelFileName, 'r')
    alchemyFile = open(alchemyFileName, 'r')

    labelOutput = []
    labelCorpus = {}
    alchemyOutput = []

    for line in labelFile:
        labels = line.strip().replace('"', '').split(' ')
        index = random.randint(0, len(labels)-1)
        output = labels[index]
        labelOutput.append(output)
        if output not in labelCorpus:
            labelCorpus[output] = 1.0
        else:
            labelCorpus[output] += 1.0
    labelFile.close()

    for line in alchemyFile:
        labels = {}
        temp = line.strip().split(' ')
        for item in temp:
            prob = float(item.split(':')[1])
            path = item.split(':')[0].split('/')
            label = path[len(path)-1]

            if label not in labels:
                labels[label] = prob
            else:
                labels[label] += prob
        alchemyOutput.append(labels)
    alchemyFile.close()

    return labelOutput, alchemyOutput

def readData3(docFileName, labelFileName, alchemyFileName):
    docFile = open(docFileName, 'r')
    labelFile = open(labelFileName, 'r')
    alchemyFile = open(alchemyFileName, 'r')

    docOutput = []
    labelOutput = []
    labelCorpus = {}
    alchemyOutput = []

    for line in labelFile:
        labels = line.strip().replace('"', '').split(' ')
        index = random.randint(0, len(labels)-1)
        output = labels[index]
        labelOutput.append(output)
        if output not in labelCorpus:
            labelCorpus[output] = 1.0
        else:
            labelCorpus[output] += 1.0
    labelFile.close()

    candLabel = max(labelCorpus.iteritems(), key=operator.itemgetter(1))[0]

    for line in docFile:
        docOutput.append(textCleaner.tweetCleaner(line.strip().lower()))
    docFile.close()

    for line in alchemyFile:
        labels = {}
        temp = line.strip().split(' ')
        for item in temp:
            prob = float(item.split(':')[1])
            path = item.split(':')[0].split('/')
            label = path[len(path)-1]

            if label not in labels:
                labels[label] = prob
            else:
                labels[label] += prob
        alchemyOutput.append(labels)
    alchemyFile.close()

    return docOutput, labelOutput, candLabel, alchemyOutput