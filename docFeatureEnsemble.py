from scipy.sparse import hstack, csr_matrix
import numpy
from sklearn.feature_extraction.text import TfidfVectorizer
import random
import modelUtility
import ensembleUtility as eu
import sys
from sklearn.linear_model import LogisticRegression

def trainDocAppend(trainVectorData, probData, labelCorpus, modelList, trainSize):
    probFeatures = []
    for index in range(trainSize):
        temp = []
        for model in modelList:
            for label in labelCorpus:
                temp.append(probData[model][str(index)][label])
        probFeatures.append(numpy.array(temp))

    features = hstack((trainVectorData, csr_matrix(numpy.array(probFeatures))), format='csr')
    return features


def testDocAppend(testVectorData, probData, modelList, labelCorpus, testSize):
    validIndex = []
    probFeatures = []
    for index in range(testSize):
        temp = eu.iniPred(probData[modelList[0]][str(index)])
        flag = False
        tempFeature = []
        for model in modelList:
            if eu.iniPred(probData[model][str(index)]) != temp:
                flag = True
                break
            temp = eu.iniPred(probData[model][str(index)])
            for label in labelCorpus:
                tempFeature.append(probData[model][str(index)][label])
        if flag:
            validIndex.append(index)
            probFeatures.append(numpy.array(tempFeature))

    features = hstack((testVectorData[validIndex], csr_matrix(numpy.array(probFeatures))), format='csr')
    return features, validIndex


def dataAssigner(features, trainIndex, testIndex, fold):
    trainFeature = []
    testFeature = []
    for index in trainIndex[fold]:
        trainFeature.append(features[index])
    for index in testIndex[fold]:
        testFeature.append(features[index])

    return trainFeature, testFeature


def labeler(trainProbData, trueTrainLabels, modelList, trainSize):
    labelList = []
    validIndex = []
    for index in range(trainSize):
        outputList = []
        for num, model in enumerate(modelList):
            if eu.iniPred(trainProbData[model][str(index)]) == trueTrainLabels[index]:
                outputList.append(num)
        if len(outputList) > 0:
            validIndex.append(index)
            labelList.append(random.choice(outputList))

    return labelList, validIndex

def singleWeight(brandList, modelList):
    print str(modelList)
    resultFile = open('HybridData/Experiment/single.result', 'a')
    resultFile.write(str(modelList) + '\n')
    for brand in brandList:
        print brand
        accuracySum = 0.0
        trainIndex = {}
        testIndex = {}
        trainIndexFile = open('HybridData/Experiment/TrainIndex/'+brand+'.train', 'r')
        testIndexFile = open('HybridData/Experiment/TrainIndex/'+brand+'.test', 'r')
        for fold, line in enumerate(trainIndexFile):
            trainIndex[fold] = line.strip().split(',')
        for fold, line in enumerate(testIndexFile):
            testIndex[fold] = line.strip().split(',')
        trainIndexFile.close()
        testIndexFile.close()
        for fold in range(5):
            trainProbData, testProbData, trainLabels, testLabels, labelCorpus = eu.consolidateReader(brand, fold, modelList)

            flag, trainSize = eu.checkSize(trainProbData, modelList)
            if not flag:
                print 'Training data size error across models!'
                sys.exit()

            docContent, labels, candTopic = modelUtility.readData('HybridData/Original/' + brand + '.content', 'HybridData/Original/' + brand + '.keyword')
            vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english')
            docVectors = vectorizer.fit_transform(docContent)

            trainDocVector, testDocVector = dataAssigner(docVectors, labels, trainIndex, testIndex, fold)

            features = trainDocAppend(trainDocVector, trainProbData, labelCorpus, modelList, trainSize)
            trainLabels, validList = labeler(trainProbData, trainLabels, modelList, trainSize)
            trainFeature = features[validList]

            model = LogisticRegression()
            model.fit(trainFeature, trainLabels)

            # test
            flag, testSize = eu.checkSize(testProbData, modelList)
            if not flag:
                print 'Test data size error across models!'
                sys.exit()
            testFeature, validList = testDocAppend(testDocVector, testProbData, modelList, labelCorpus, testSize)

            labels = []
            for index in validList:
                labels.append(testLabels[index])
            accuracySum += model.score(testFeature, labels)

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