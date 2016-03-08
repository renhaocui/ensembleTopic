__author__ = 'renhao.cui'
import operator
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn import cross_validation
from sklearn.feature_extraction.text import *
import modelUtility
import sys

def normalization(scoreList):
    outputList = []
    total = sum(scoreList)
    for score in scoreList:
        outputList.append(score/total)
    return outputList


def trainInfer(doc_train, label_train, doc_test, label_test, classifier, trainProbFlag):
    if classifier == 'NaiveBayes':
        model = MultinomialNB()
    elif classifier == 'SVM':
        model = svm.SVC(probability=True)
    elif classifier == 'MaxEnt':
        model = LogisticRegression()
    else:
        print 'Ensemble Model Error!'
        sys.exit()

    model.fit(doc_train, label_train)
    labelList = model.classes_
    testProbs = model.predict_proba(doc_test)

    output = {}
    for num, probs in enumerate(testProbs):
        temp = {}
        for index, prob in enumerate(probs):
            inferTopic = labelList[index]
            temp[inferTopic] = prob
        sorted_temp = sorted(temp.items(), key=operator.itemgetter(1), reverse=True)
        outList = {}
        for index, (topic, prob) in enumerate(sorted_temp):
            outList[index+1] = {topic: prob}
        output[num] = outList

    trainOutput = {}
    if trainProbFlag:
        trainProbs = model.predict_proba(doc_train)
        for num, probs in enumerate(trainProbs):
            temp = {}
            for index, prob in enumerate(probs):
                inferTopic = labelList[index]
                temp[inferTopic] = prob
            sorted_temp = sorted(temp.items(), key=operator.itemgetter(1), reverse=True)
            outList = {}
            for index, (topic, prob) in enumerate(sorted_temp):
                outList[index+1] = {topic: prob}
            trainOutput[num] = outList

    return model.score(doc_test, label_test), output, trainOutput


def run(classifier):
    brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']
    outputFile = open('results/'+classifier+'.result', 'w')
    for brand in brandList:
        print brand
        docContent, topics, candTopic = modelUtility.readData('HybridData/Original/' + brand + '.content', 'HybridData/Original/' + brand + '.keyword')

        vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english')
        features = vectorizer.fit_transform(docContent)

        accuracySum = 0.0
        for i in range(5):
            print 'fold num: '+str(i)
            doc_train, doc_test, label_train, label_test = cross_validation.train_test_split(features, topics, test_size=0.2, random_state=0)
            accuracy, testOutput, trainOutput = trainInfer(doc_train, label_train, doc_test, label_test, classifier, True)
            accuracySum += accuracy

        print accuracySum/5
        outputFile.write(brand+'\t'+str(accuracySum/5)+'\n')

    outputFile.close()
