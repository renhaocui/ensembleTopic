__author__ = 'renhao.cui'
import operator
from sklearn.linear_model import LogisticRegression
from sklearn import cross_validation
from sklearn.feature_extraction.text import *
import modelUtility

def normalization(scoreList):
    outputList = []
    total = sum(scoreList)
    for score in scoreList:
        outputList.append(score/total)
    return outputList


def maxEntTrainInfer(doc_train, label_train, doc_test, label_test):
    model = LogisticRegression()
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

    return model.score(doc_test, label_test), output


def run():
    brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']
    outputFile = open('results/MaxEnt.result', 'w')
    for brand in brandList:
        print brand
        docContent, topics, candTopic = modelUtility.readData('HybridData/Original/' + brand + '.content', 'HybridData/Original/' + brand + '.keyword')

        vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english')
        features = vectorizer.fit_transform(docContent)

        accuracySum = 0.0
        for i in range(5):
            print 'fold num: '+str(i)
            doc_train, doc_test, label_train, label_test = cross_validation.train_test_split(features, topics, test_size=0.2, random_state=0)
            accuracy, testOutput = maxEntTrainInfer(doc_train, label_train, doc_test, label_test)
            accuracySum += accuracy

        print accuracySum/5
        outputFile.write(brand+'\t'+str(accuracySum/5)+'\n')

    outputFile.close()

run()



