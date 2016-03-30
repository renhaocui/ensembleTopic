import sys
import ensembleUtility as eu
import operator


def probSum(probData, dataSize, modelList, labelCorpus):
    output = {}
    for index in range(dataSize):
        temp = {}
        for model in modelList:
            for label in labelCorpus:
                if label not in temp:
                    temp[label] = 0.0
                if label in probData[model][str(index)]:
                    score = probData[model][str(index)][label]
                    temp[label] += score
        output[index] = max(temp, key=temp.get)
    return output


def probComp(probData, dataSize, modelList):
    output = {}
    for index in range(dataSize):
        comp = {}
        temp = {}
        for model in modelList:
            pred = max(probData[model][str(index)], key=probData[model][str(index)].get)
            comp[model] = probData[model][str(index)][pred]
            temp[model] = pred
        output[index] = temp[max(comp, key=comp.get)]
    return output


def evaluator(predictions, labels, testSize):
    correct = 0.0
    total = 0.0
    for index in range(testSize):
        if predictions[index] in labels[index]:
            correct += 1.0
        total += 1.0
    return correct / total


def baselines(brandList, modelList):
    print str(modelList)
    resultFile = open('HybridData/Experiment/probEnsembleBaselines.result', 'a')
    resultFile.write(str(modelList) + '\n')
    for brand in brandList:
        print brand
        accuracySum1 = 0.0
        accuracySum2 = 0.0

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
                                                                                                     modelList)

            flag, trainSize = eu.checkSize(trainProbData, modelList)
            if not flag:
                print 'Training data size error across models!'
                sys.exit()

            flag, testSize = eu.checkSize(testProbData, modelList)
            if not flag:
                print 'Test data size error across models!'
                sys.exit()

            # probDict[individualModel] = {lineNum: {topic: prob}}
            sumPredictions = probSum(testProbData, testSize, modelList, labelCorpus)
            accuracySum1 += evaluator(sumPredictions, testLabels, testSize)
            compPredictions = probComp(testProbData, testSize, modelList)
            accuracySum2 += evaluator(compPredictions, testLabels, testSize)

        print 'probSum: ' + str(accuracySum1 / 5)
        print 'probComp: ' + str(accuracySum2 / 5)

        resultFile.write(brand + '\tprobSum:\t' + str(accuracySum1 / 5) + '\n')
        resultFile.write(brand + '\tprobComp:\t' + str(accuracySum2 / 5) + '\n')


if __name__ == "__main__":
    brandList = ['Elmers', 'Chilis', 'Dominos', 'Triclosan', 'TriclosanV', 'BathAndBodyWorks']
    runModelList = [['NaiveBayes', 'Alchemy'], ['LLDA', 'Alchemy'], ['LLDA', 'NaiveBayes'], ['LLDA', 'NaiveBayes', 'Alchemy']]
    for modelList in runModelList:
        baselines(brandList, modelList)
