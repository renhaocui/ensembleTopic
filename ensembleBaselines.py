__author__ = 'renhao.cui'
import operator
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
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


def trainInfer(doc_train, label_train, doc_test, label_test, ensemble):
    if ensemble == 'RandomForest':
        model = RandomForestClassifier()
    elif ensemble == 'AdaBoost':
        model = AdaBoostClassifier()
    else:
        print 'Ensemble Model Error!'
        sys.exit()

    model.fit(doc_train, label_train)
    '''
    #labelList = model.classes_
    #testProbs = model.predict_pro(doc_test)

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
    '''
    return model.score(doc_test, label_test)


def run(ensemble):
    brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']
    outputFile = open('HybridData/Experiment/result', 'w')
    for brand in brandList:
        print brand
        docContent, topics, candTopic = modelUtility.readData('HybridData/Original/' + brand + '.content', 'HybridData/Original/' + brand + '.keyword')

        vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english')
        features = vectorizer.fit_transform(docContent)

        accuracySum = 0.0
        for i in range(5):
            print 'fold num: '+str(i)
            doc_train, doc_test, label_train, label_test = cross_validation.train_test_split(features, topics, test_size=0.2, random_state=0)
            accuracy = trainInfer(doc_train, label_train, doc_test, label_test, ensemble)
            accuracySum += accuracy

        print accuracySum/5
        outputFile.write(brand+'\t'+str(accuracySum/5)+'\n')

    outputFile.close()