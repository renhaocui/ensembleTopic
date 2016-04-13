import sys
import ensembleUtility as eu

def renormalize(inputDict):
    outputDict = {}
    total = sum(inputDict.values())
    for key, value in inputDict.items():
        outputDict[key] = float(value)/total
    return outputDict

def dynamicWeightTrain(probData, trainLabels, dataSize, modelList, labelCorpus, learningRate, iteration):
    modelWeightsSum = {}
    updateCount = 0.0
    modelWeights = {}
    for model in modelList:
        modelWeights[model] = 1.0/len(modelList)
        modelWeightsSum[model] = 0.0
    for iter in range(iteration):
        for index in range(dataSize):
            tempProbData = {}
            for model in modelList:
                tempProbData[model] = {'0': probData[model][str(index)]}
            tempPrediction = dynamicWeightInfer(tempProbData, 1, modelList, labelCorpus, modelWeights)
            if tempPrediction[0] != trainLabels[index]:
                for model in modelList:
                    if eu.iniPred(tempProbData[model]) != trainLabels[index]:
                        modelWeights[model] *= learningRate
                modelWeights = renormalize(modelWeights)
            for model in modelList:
                modelWeightsSum[model] += modelWeights[model]
            updateCount += 1.0

    outputWeights = {}
    for model in modelList:
        outputWeights[model] = modelWeightsSum[model]/updateCount

    return outputWeights


def dynamicWeightInfer(probData, dataSize, modelList, labelCorpus, modelWeights):
    output = {}
    for index in range(dataSize):
        temp = {}
        for model in modelList:
            for label in labelCorpus:
                if label != temp:
                    temp[label] = 0.0
                score = probData[model][str(index)][label]
                temp[label] += modelWeights[model] * score

        output[index] = max(temp, key=temp.get)
    return output


def evaluator(predictions, labels, testSize):
    correct = 0.0
    total = 0.0
    for index in range(testSize):
        if predictions[index] in labels[index]:
            correct += 1.0
        total += 1.0
    return correct / total


def baselines(brandList, modelList, learningRate, iteration):
    print str(modelList)
    resultFile = open('HybridData/Experiment/dynamicEnsembleBaselines.result2', 'a')
    resultFile.write(str(modelList) + '\n')

    for brand in brandList:
        print brand
        accuracySum = 0.0

        trainIndex = {}
        testIndex = {}
        trainIndexFile = open('HybridData/Experiment/TrainIndex/' + brand + '.train', 'r')
        testIndexFile = open('HybridData/Experiment/TestIndex/' + brand + '.test', 'r')
        for fold, line in enumerate(trainIndexFile):
            trainIndex[fold] = line.strip().split(',')
        for fold, line in enumerate(testIndexFile):
            testIndex[fold] = line.strip().split(',')
        trainIndexFile.close()
        testIndexFile.close()

        for fold in range(5):
            print 'Fold: ' + str(fold)
            trainProbData, testProbData, trainLabels, testLabels, labelCorpus = eu.consolidateReader(brand, fold,
                                                                                                     modelList, 0.001)

            flag, trainSize = eu.checkSize(trainProbData, modelList)
            if not flag:
                print 'Training data size error across models!'
                sys.exit()

            flag, testSize = eu.checkSize(testProbData, modelList)
            if not flag:
                print 'Test data size error across models!'
                sys.exit()

            # probDict[individualModel] = {lineNum: {topic: prob}}
            modelWeights = dynamicWeightTrain(trainProbData, trainLabels, trainSize, modelList, labelCorpus, learningRate, iteration)
            predictions = dynamicWeightInfer(testProbData, testSize, modelList, labelCorpus, modelWeights)
            accuracySum += evaluator(predictions, testLabels, testSize)

        print 'probComp: ' + str(accuracySum / 5)

        resultFile.write(brand + '\tprobComp:\t' + str(accuracySum / 5) + '\n')

    resultFile.close()

if __name__ == "__main__":
    brandList = ['Elmers', 'Chilis', 'Dominos', 'Triclosan', 'TriclosanV', 'BathAndBodyWorks', 'POCruisesAustraliaV']
    runModelList = [['NaiveBayes', 'Alchemy'], ['LLDA', 'Alchemy'], ['LLDA', 'NaiveBayes'], ['LLDA', 'NaiveBayes', 'Alchemy']]
    for modelList in runModelList:
        baselines(brandList, modelList, 0.9, 30)