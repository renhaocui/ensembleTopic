import ensembleUtility as eu
import sys

def evaluator(predictions, labels, testSize):
    correct = 0.0
    total = 0.0
    for index in range(testSize):
        if predictions[index] in labels[index]:
            correct += 1.0
        total += 1.0
    return correct / total

def prodProb(probData, modelList, labelCorpus, dataSize):
    output = {}
    for index in range(dataSize):
        prod = {}
        for label in labelCorpus:
            prod[label] = 1.0
        for model in modelList:
            labelProb = probData[model][str(index)]
            for label in labelCorpus:
                prod[label] *= labelProb[label]

        output[index] = max(prod, key=prod.get)
    return output


def PoE(brandList, modelList):
    print str(modelList)
    resultFile = open('HybridData/Experiment/PoE.result', 'a')
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
            #print 'Fold: ' + str(fold)
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
            sumPredictions = prodProb(testProbData, modelList, labelCorpus, testSize)
            accuracySum += evaluator(sumPredictions, testLabels, testSize)

        print 'PeO: ' + str(accuracySum / 5)

        resultFile.write(brand + '\tPoE:\t' + str(accuracySum / 5) + '\n')

if __name__ == "__main__":
    brandList = ['Elmers', 'Chilis', 'Dominos', 'Triclosan', 'TriclosanV', 'BathAndBodyWorks', 'POCruisesAustraliaV']
    runModelList = [['NaiveBayes', 'Alchemy'], ['LLDA', 'Alchemy'], ['LLDA', 'NaiveBayes'], ['LLDA', 'NaiveBayes', 'Alchemy']]
    for modelList in runModelList:
        PoE(brandList, modelList)