from scipy.sparse import hstack, csr_matrix
import numpy
from sklearn.feature_extraction.text import TfidfVectorizer
import modelUtility
import ensembleUtility as eu
import sys
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.neural_network import MLPClassifier

def docAppend(vectorData, probData, labelCorpus, modelList, trainSize, useDocVector):
    probFeatures = []
    for index in range(trainSize):
        temp = []
        for model in modelList:
            for label in labelCorpus:
                if label in probData[model][str(index)]:
                    temp.append(probData[model][str(index)][label])
                else:
                    temp.append(0.0)
        probFeatures.append(numpy.array(temp))
    if useDocVector:
        features = hstack((vectorData, csr_matrix(numpy.array(probFeatures))), format='csr')
    else:
        features = csr_matrix(numpy.array(probFeatures))
    return features


def testLabeler(features, testProbData, trueTestLabels, modelList, testSize):
    validIndex = []
    labelList = []
    for index in range(testSize):
        outputList = []
        for num, model in enumerate(modelList):
            if eu.iniPred(testProbData[model][str(index)]) == trueTestLabels[index]:
                outputList.append(num)
        if len(outputList) > 0:
            validIndex.append(index)
            labelList.append(outputList)

    return features[validIndex], labelList

def trainLabeler(trainProbData, trueTrainLabels, modelList, trainSize):
    labelList = []
    validIndex = []
    for index in range(trainSize):
        outputList = []
        for num, model in enumerate(modelList):
            if eu.iniPred(trainProbData[model][str(index)]) == trueTrainLabels[index]:
                outputList.append(num)
        if len(outputList) > 0:
            for item in outputList:
                validIndex.append(index)
                labelList.append(item)
            #labelList.append(random.choice(outputList))

    return labelList, validIndex

def evaluator(predictions, labels):
    correct = 0.0
    total = 0.0
    for index, pred in enumerate(predictions):
        if pred in labels[index]:
            correct += 1.0
        total += 1.0
    return correct/total

def evaluator2(predictions, modelList, testProbData, testLabels):
    correct = 0.0
    total = 0.0
    for index, pred in enumerate(predictions):
        if eu.iniPred(testProbData[modelList[pred]][str(index)]) == testLabels[index]:
            correct += 1.0
        total += 1.0
    return correct/total

def singleWeight(brandList, modelList, classifier, useDocVector):
    print str(modelList)
    resultFile = open('HybridData/Experiment/'+classifier+'_'+str(useDocVector)+'.result', 'a')
    resultFile.write(str(modelList) + '\n')
    for brand in brandList:
        print brand
        accuracySum = 0.0

        trainIndex = {}
        testIndex = {}
        trainIndexFile = open('HybridData/Experiment/TrainIndex/'+brand+'.train', 'r')
        testIndexFile = open('HybridData/Experiment/TestIndex/'+brand+'.test', 'r')
        for fold, line in enumerate(trainIndexFile):
            trainIndex[fold] = line.strip().split(',')
        for fold, line in enumerate(testIndexFile):
            testIndex[fold] = line.strip().split(',')
        trainIndexFile.close()
        testIndexFile.close()
        for fold in range(5):
            print 'Fold: '+str(fold)
            trainProbData, testProbData, trainLabels, testLabels, labelCorpus = eu.consolidateReader(brand, fold, modelList)

            flag, trainSize = eu.checkSize(trainProbData, modelList)
            if not flag:
                print 'Training data size error across models!'
                sys.exit()

            # read in
            docContent, labels, candTopic = modelUtility.readData('HybridData/Original/' + brand + '.content', 'HybridData/Original/' + brand + '.keyword')

            vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english')
            docVectors = vectorizer.fit_transform(docContent)

            trainDocVector =docVectors[trainIndex[fold]]
            testDocVector = docVectors[testIndex[fold]]

            # training
            features = docAppend(trainDocVector, trainProbData, labelCorpus, modelList, trainSize, useDocVector)
            #trainLabels, validList = trainLabeler(trainProbData, trainLabels, modelList, trainSize)
            #trainFeature = features[validList]
            '''
            if classifier == 'MaxEnt':
                model = LogisticRegression()
            elif classifier == 'SVM':
                model = svm.SVC()
            '''
            if classifier == 'MLP':
                model = MLPClassifier(algorithm='sgd', activation='logistic', learning_rate_init=0.02, learning_rate='constant', batch_size=10)

            model.fit(features, trainLabels)

            # testing
            flag, testSize = eu.checkSize(testProbData, modelList)
            if not flag:
                print 'Test data size error across models!'
                sys.exit()

            testFeatures = docAppend(testDocVector, testProbData, labelCorpus, modelList, testSize, useDocVector)

            #testFeatures1, labels1 = testLabeler(features, testProbData, testLabels, modelList, testSize)

            predictions = model.predict(testFeatures)

            accuracySum += evaluator(predictions, testLabels)

            #accuracySum3 += evaluator2(predictions3, modelList, testProbData, testLabels)
            #accuracySum4 += evaluator2(predictions4, modelList, testProbData, testLabels)

        print 'MLP \t '+str(accuracySum / 5.0)

        resultFile.write(brand + '\t' + str(accuracySum / 5.0) + '\n')

    resultFile.close()


#brandList = ['Elmers', 'Chilis', 'Dominos', 'Triclosan', 'BathAndBodyWorks']
brandList = ['Dominos']
#runModelList = [['NaiveBayes', 'Alchemy'], ['LLDA', 'Alchemy'], ['LLDA', 'NaiveBayes'], ['LLDA', 'NaiveBayes', 'Alchemy']]
runModelList = [['LLDA', 'NaiveBayes']]


if __name__ == "__main__":
    for modelList in runModelList:
        #print 'True'
        singleWeight(brandList=brandList, modelList=modelList, classifier='MLP',useDocVector=True)
        #print 'True'
        #singleWeight(brandList=brandList, modelList=modelList, classifier='SVM', useDocVector=True)