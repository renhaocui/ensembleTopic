import json
import sys
import operator

def iniWeight(modelList):
    output = {}
    totalOutput = {}
    updateCount = {}
    size = len(modelList)
    for model in modelList:
        output[model] = 1.0/size
        totalOutput[model] = 0.0
        updateCount[model] = 0.0
    return output, totalOutput, updateCount


def normalization(weightDict):
    output = {}
    sumNum = sum(weightDict.values())
    for model, weight in weightDict.items():
        output[model] = weight/sumNum
    return output

def checkSize(inputDict, modelList):
    size = -1
    for model in modelList:
        if size == -1:
            size = len(inputDict[model])
        else:
            if size != len(inputDict[model]):
                return False, size
    return True, size

def weightedPred(probData, modelList, weights, size):
    output = {}
    for index in range(size):
        tempDict = {}
        for model in modelList:
            probDict = probData[model][str(index)]
            for label, prob in probDict.items():
                if label not in tempDict:
                    tempDict[label] = prob*weights[model]
                else:
                    tempDict[label] += prob*weights[model]
        predTopic = max(tempDict.iteritems(), key=operator.itemgetter(1))[0]
        predScore = max(tempDict.iteritems(), key=operator.itemgetter(1))[1]
        output[index] = (predTopic, predScore)
    return output

def iniPred(inputDict):
    predTopic = max(inputDict.iteritems(), key=operator.itemgetter(1))[0]
    predScore = max(inputDict.iteritems(), key=operator.itemgetter(1))[1]
    return predTopic


def singleEnsemble(brandList, modelList, iterations=30, learningRate=0.9):
    print str(modelList)
    resultFile = open('HybridData/Experiment/single.result', 'a')
    resultFile.write(str(modelList)+'\n')
    for brand in brandList:
        print brand
        accuracySum = 0.0
        for fold in range(5):
            print fold
            probTrainFile = open('../Experiment/ProbData/'+brand+'/probTrain.'+str(fold), 'r')
            probTestFile = open('../Experiment/ProbData/'+brand+'/prob.'+str(fold), 'r')
            trainLabelFile = open('../Experiment/Labels/Train/'+brand+'.'+str(fold), 'r')
            testLabelFile = open('../Experiment/Labels/Test/'+brand+'.'+str(fold), 'r')

            # probDict[individualModel] = {lineNum: {topic: prob}}
            trainProbData = {}
            testProbData = {}
            for line in probTrainFile:
                trainProbData = json.loads(line.strip())
            probTrainFile.close()
            for line in probTestFile:
                testProbData = json.loads(line.strip())
            probTestFile.close()

            trainLabels = []
            testLabels = []
            for line in trainLabelFile:
                trainLabels.append(line.strip())
            for line in testLabelFile:
                testLabels.append(line.strip())

            flag, trainSize = checkSize(trainProbData, modelList)
            if not flag:
                print 'Training data size error across models!'
                sys.exit()

            weights, totalWeights, updateCounts = iniWeight(modelList)

            # weight training
            for iter in range(iterations):
                predOutput = weightedPred(trainProbData, modelList, weights, trainSize)
                for index in range(trainSize):
                    outputLabel = predOutput[index][0]
                    outputScore = predOutput[index][1]
                    if outputLabel != trainLabels[index]:
                        for model in modelList:
                            if outputLabel != iniPred(trainProbData[model][str(index)]):
                                weights[model] *= learningRate*outputScore

                        weights = normalization(weights)
                        for model in modelList:
                            totalWeights[model] += weights[model]
                            updateCounts[model] += 1.0

            # test
            flag, testSize = checkSize(testProbData, modelList)
            if not flag:
                print 'Test data size error across models!'
                sys.exit()

            inferWeights = {}
            for model, total in totalWeights.items():
                inferWeights[model] = total/updateCounts[model]

            predOutput = weightedPred(testProbData, modelList, inferWeights, testSize)
            total = 0.0
            correct = 0.0
            for index in range(testSize):
                if predOutput[index][0] == testLabels[index]:
                    correct += 1.0
                total += 1.0
            accuracySum += correct/total

        print accuracySum/5
        resultFile.write(brand+'\t'+str(accuracySum/5)+'\n')
    resultFile.close()


def vectorEnsemble(brandList, modelList, iterations, learningRate):
    resultFile = open('HybridData/Experiment/vector.result', 'w')
    resultFile.write(str(modelList)+'\n')
    for brand in brandList:
        accuracySum = 0.0
        for fold in range(5):
            print fold
            probTrainFile = open('HybridData/Experiment/ProbData/'+brand+'/probTrain.'+str(fold), 'r')
            probTestFile = open('HybridData/Experiment/ProbData/'+brand+'/prob.'+str(fold), 'r')
            trainLabelFile = open('HybridData/Experiment/Labels/Train/'+brand+'.'+str(fold), 'r')
            testLabelFile = open('HybridData/Experiment/Labels/Test/'+brand+'.'+str(fold), 'r')

            # probDict[individualModel] = {lineNum: {topic: prob}}
            trainProbData = {}
            testProbData = {}
            for line in probTrainFile:
                trainProbData = json.loads(line.strip())
            probTrainFile.close()
            for line in probTestFile:
                testProbData = json.loads(line.strip())
            probTestFile.close()

            trainLabels = []
            testLabels = []
            for line in trainLabelFile:
                trainLabels.append(line.strip())
            for line in testLabelFile:
                testLabels.append(line.strip())

            flag, trainSize = checkSize(trainProbData, modelList)
            if not flag:
                print 'Training data size error across models!'
                sys.exit()

brandList = ['Elmers', 'Chilis', 'Dominos', 'Triclosan']
#modelList = ['MaxEnt', 'NaiveBayes']
runModelList = [['MaxEnt', 'NaiveBayes'], ['LLDA', 'Alchemy'], ['LLDA', 'MaxEnt'], ['Alchemy', 'MaxEnt'], ['LLDA', 'MaxEnt', 'NaiveBayes', 'Alchemy']]

if __name__ == "__main__":
    for modelList in runModelList:
        singleEnsemble(brandList=brandList, modelList=modelList)