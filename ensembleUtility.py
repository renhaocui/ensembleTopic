import json
import operator

def normalization(inputDict):
    outputDict = {}
    total = sum(inputDict.values())
    for key, value in inputDict.items():
        outputDict[key] = value/total
    return outputDict

def smooth(probData, labelCorpus, smoothFactor, model):
    for index, labelProb in probData[model].items():
        tempDict = {}
        for label in labelCorpus:
            if label not in labelProb:
                tempDict[label] = smoothFactor
            else:
                tempDict[label] = labelProb[label]
        probData[model][index] = normalization(tempDict)

    return probData

def iniPred(inputDict):
    predTopic = max(inputDict.iteritems(), key=operator.itemgetter(1))[0]
    # predScore = max(inputDict.iteritems(), key=operator.itemgetter(1))[1]
    return predTopic


def checkSize(inputDict, modelList):
    size = -1
    for model in modelList:
        if size == -1:
            size = len(inputDict[model])
        else:
            if size != len(inputDict[model]):
                return False, size
    return True, size


def consolidateReader(brand, fold, modelList, smoothFactor):
    # probDict[individualModel] = {lineNum: {topic: prob}}
    trainProbData = {}
    testProbData = {}
    for model in modelList:
        probTrainFile = open('../Experiment/ProbData/' + brand + '/' + model + 'probTrain.' + str(fold), 'r')
        probTestFile = open('../Experiment/ProbData/' + brand + '/' + model + 'prob.' + str(fold), 'r')
        tempProbDict = {}
        tempProbTrainDict = {}
        for line in probTrainFile:
            tempProbTrainDict = json.loads(line.strip())
        for line in probTestFile:
            tempProbDict = json.loads(line.strip())
        testProbData[model] = tempProbDict
        trainProbData[model] = tempProbTrainDict

    labelCorpus = []
    trainLabelFile = open('../Experiment/Labels/Train/' + brand + '.' + str(fold), 'r')
    testLabelFile = open('../Experiment/Labels/Test/' + brand + '.' + str(fold), 'r')
    trainLabels = []
    testLabels = []
    for line in trainLabelFile:
        label = line.strip()
        if label not in labelCorpus:
            labelCorpus.append(label)
        trainLabels.append(label)
    for line in testLabelFile:
        label = line.strip()
        if label not in labelCorpus:
            labelCorpus.append(label)
        testLabels.append(label)

    for model in modelList:
        trainProbData = smooth(trainProbData, labelCorpus, smoothFactor, model)
        testProbData = smooth(testProbData, labelCorpus, smoothFactor, model)

    return trainProbData, testProbData, trainLabels, testLabels, labelCorpus

