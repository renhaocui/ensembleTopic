import json
import sys
import operator
import ensembleUtility as eu

def iniWeight(modelList):
    output = {}
    totalOutput = {}
    updateCount = {}
    size = len(modelList)
    for model in modelList:
        output[model] = 1.0 / size
        totalOutput[model] = 0.0
        updateCount[model] = 0.0
    return output, totalOutput, updateCount


def iniVectorWeight(modelList, labelCorpus):
    weights = {}
    totalWeights = {}
    updateCount = {}
    size = len(modelList)
    for model in modelList:
        tempWeight = {}
        tempTotalWeight = {}
        tempCount = {}
        for label in labelCorpus:
            tempWeight[label] = 1.0 / size
            tempTotalWeight[label] = 0.0
            tempCount[label] = 0.0
        weights[model] = tempWeight
        totalWeights[model] = tempTotalWeight
        updateCount[model] = tempCount
    return weights, totalWeights, updateCount


def normalization(weightDict):
    output = {}
    sumNum = sum(weightDict.values())
    for model, weight in weightDict.items():
        output[model] = weight / sumNum
    return output


def vectorNormalization(weightDict, labelCorpus):
    output = {}
    for model in weightDict:
        output[model] = {}
    for label in labelCorpus:
        temp = {}
        for model in weightDict:
            temp[model] = weightDict[model][label]
        tempOut = normalization(temp)
        for model, weight in tempOut.items():
            output[model][label] = weight
    return output


def weightedPred(probData, modelList, weights, size):
    output = {}
    for index in range(size):
        tempDict = {}
        for model in modelList:
            probDict = probData[model][str(index)]
            for label, prob in probDict.items():
                if label not in tempDict:
                    tempDict[label] = prob * weights[model]
                else:
                    tempDict[label] += prob * weights[model]
        predTopic = max(tempDict.iteritems(), key=operator.itemgetter(1))[0]
        predScore = max(tempDict.iteritems(), key=operator.itemgetter(1))[1]
        output[index] = (predTopic, predScore)
    return output


def vectorWeightedPred(probData, modelList, weights, size):
    output = {}
    for index in range(size):
        tempDict = {}
        for model in modelList:
            probDict = probData[model][str(index)]
            for label, prob in probDict.items():
                if label not in tempDict:
                    tempDict[label] = prob * weights[model][label]
                else:
                    tempDict[label] += prob * weights[model][label]
        predTopic = max(tempDict.iteritems(), key=operator.itemgetter(1))[0]
        predScore = max(tempDict.iteritems(), key=operator.itemgetter(1))[1]
        output[index] = (predTopic, predScore)
    return output


def modelDiff(trainData, modelList, trueLabels, trainSize, outputFileName):
    outputFile = open(outputFileName, 'w')
    output = {}
    for index in range(trainSize):
        modelOutput = {}
        temp = eu.iniPred(trainData[modelList[0]][str(index)])
        flag = False
        for model in modelList:
            modelOutput[model] = eu.iniPred(trainData[model][str(index)])
            if modelOutput[model] != temp:
                flag = True
            temp = modelOutput[model]
        if flag:
            out = trueLabels[index]
            for model in modelList:
                out += '\t' + modelOutput[model]
            outputFile.write(out.strip() + '\n')
    outputFile.close()


def idealOutput(testProbData, modelList, testSize):
    output = {}
    for index in range(testSize):
        temp = []
        for model in modelList:
            temp.append(eu.iniPred(testProbData[model][str(index)]))
        output[index] = temp
    return output


def singleWeightTraining(weights, totalWeights, updateCounts, trainProbData, trainLabels, modelList, iterations,
                         learningRate, trainSize):
    for iter in range(iterations):
        predOutput = weightedPred(trainProbData, modelList, weights, trainSize)
        for index in range(trainSize):
            outputLabel = predOutput[index][0]
            outputScore = predOutput[index][1]
            if outputLabel != trainLabels[index]:
                for model in modelList:
                    if trainLabels[index] != eu.iniPred(trainProbData[model][str(index)]):
                        weights[model] *= learningRate * outputScore

                weights = normalization(weights)
                for model in modelList:
                    totalWeights[model] += weights[model]
                    updateCounts[model] += 1.0

    return weights, totalWeights, updateCounts

def singleWeightTest(testProbData, totalWeights, updateCounts, testLabels, testSize):
    inferWeights = {}
    for model, total in totalWeights.items():
        inferWeights[model] = total / updateCounts[model]

    predOutput = weightedPred(testProbData, modelList, inferWeights, testSize)
    # predOutput = idealOutput(testProbData, modelList, testSize)

    total = 0.0
    correct = 0.0
    for index in range(testSize):
        if predOutput[index][0] == testLabels[index]:
            correct += 1.0
        total += 1.0

    return correct/total

def singleWeight(brandList, modelList, iterations=30, learningRate=0.9):
    print str(modelList)
    resultFile = open('HybridData/Experiment/single.result', 'a')
    resultFile.write(str(modelList) + '\n')
    for brand in brandList:
        print brand
        accuracySum = 0.0
        for fold in range(5):
            print fold
            trainProbData, testProbData, trainLabels, testLabels, labelCorpus = eu.consolidateReader(brand, fold, modelList)

            flag, trainSize = eu.checkSize(trainProbData, modelList)
            if not flag:
                print 'Training data size error across models!'
                sys.exit()

            weights, totalWeights, updateCounts = iniWeight(modelList)
            # modelDiff(trainProbData, modelList, trainLabels, trainSize, '../Experiment/'+brand+'.output')

            # weight training
            weights, totalWeights, updateCounts = singleWeightTraining(weights, totalWeights, updateCounts,
                                                                       trainProbData, trainLabels, modelList,
                                                                       iterations, learningRate, trainSize)

            # test
            flag, testSize = eu.checkSize(testProbData, modelList)
            if not flag:
                print 'Test data size error across models!'
                sys.exit()
            accuracy = singleWeightTest(testProbData, totalWeights, updateCounts, testLabels, testSize)
            accuracySum += accuracy

        print accuracySum / 5
        resultFile.write(brand + '\t' + str(accuracySum / 5) + '\n')

    resultFile.close()


def vectorEnsemble(brandList, modelList, iterations=100, learningRate=0.9):
    resultFile = open('HybridData/Experiment/vector.result', 'a')
    resultFile.write(str(modelList) + '\n')
    for brand in brandList:
        print brand
        accuracySum = 0.0
        for fold in range(5):
            print fold
            trainProbData, testProbData, trainLabels, testLabels, labelCorpus = eu.consolidateReader(brand, fold, modelList)

            flag, trainSize = eu.checkSize(trainProbData, modelList)
            if not flag:
                print 'Training data size error across models!'
                sys.exit()

            weights, totalWeights, updateCounts = iniVectorWeight(modelList, labelCorpus)

            # weight training
            for iter in range(iterations):
                predOutput = vectorWeightedPred(trainProbData, modelList, weights, trainSize)
                for index in range(trainSize):
                    outputLabel = predOutput[index][0]
                    outputScore = predOutput[index][1]
                    if outputLabel != trainLabels[index]:
                        for model in modelList:
                            if trainLabels[index] != eu.iniPred(trainProbData[model][str(index)]):
                                for label in labelCorpus:
                                    if label != trainLabels[index]:
                                        weights[model][label] *= learningRate * outputScore

                        weights = vectorNormalization(weights, labelCorpus)
                        for model in modelList:
                            for label in labelCorpus:
                                totalWeights[model][label] += weights[model][label]
                                updateCounts[model][label] += 1.0

            # test
            flag, testSize = eu.checkSize(testProbData, modelList)
            if not flag:
                print 'Test data size error across models!'
                sys.exit()

            inferWeights = {}
            for model, total in totalWeights.items():
                inferWeights[model] = {}
                for label in labelCorpus:
                    inferWeights[model][label] = total[label] / updateCounts[model][label]

            predOutput = vectorWeightedPred(testProbData, modelList, inferWeights, testSize)
            total = 0.0
            correct = 0.0
            for index in range(testSize):
                if predOutput[index][0] == testLabels[index]:
                    correct += 1.0
                total += 1.0
            accuracySum += correct / total

        print accuracySum / 5
        resultFile.write(brand + '\t' + str(accuracySum / 5) + '\n')
    resultFile.close()


brandList = ['Elmers', 'Chilis', 'Dominos', 'Triclosan', 'BathAndBodyWorks']
# runModelList = [['MaxEnt', 'NaiveBayes']]
runModelList = [['MaxEnt', 'NaiveBayes'], ['LLDA', 'Alchemy'], ['LLDA', 'MaxEnt'], ['Alchemy', 'MaxEnt'],
                ['LLDA', 'MaxEnt', 'NaiveBayes', 'Alchemy']]

if __name__ == "__main__":
    for modelList in runModelList:
        singleWeight(brandList=brandList, modelList=modelList)
