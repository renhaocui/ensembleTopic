__author__ = 'renhao.cui'
import utilities
import operator

def normalization(inputList):
    outputList = []
    total = sum(inputList)
    for score in inputList:
        outputList.append(score/total)

    return outputList

def mappingTrainer(labelSet1, labelSet2, limit):
    set2 = []
    for sets in labelSet2:
        seg = sets.split(' ')
        set2.append(seg)
    corpus1 = [] #alchemy
    corpus2 = [] #keyword
    trainSet1 = []
    trainSet2 = []
    for topics in labelSet1:
        trainSet1.append(topics)
        for topic in topics:
            if topic not in corpus1:
                corpus1.append(topic)
    for topics in set2:
        trainSet2.append(topics)
        for topic in topics:
            if topic not in corpus2:
                corpus2.append(topic)

    (confScore, model, cand) = utilities.generateModel(corpus1, corpus2, trainSet1, trainSet2)
    outputModel = utilities.filterModel(confScore, limit)

    return outputModel, cand

def mappingTrainer2(labelSet1, labelSet2, limit):
    set2 = []
    for sets in labelSet2:
        seg = sets.split(' ')
        set2.append(seg)
    corpus1 = [] # from domain
    corpus2 = [] # to domain
    trainSet1 = []
    trainSet2 = []
    for topics in labelSet1:
        trainSet1.append(topics)
        for topic in topics:
            if topic not in corpus1:
                corpus1.append(topic)
    for topics in set2:
        trainSet2.append(topics)
        for topic in topics:
            if topic not in corpus2:
                corpus2.append(topic)

    (confScore, model, cand, candProb) = utilities.generateModel(corpus1, corpus2, trainSet1, trainSet2)
    outputModel = utilities.filterModel(confScore, limit)

    return model, cand, candProb

def mappingTrainer3(labelSet1, labelSet2):
    set2 = []
    for sets in labelSet2:
        seg = sets.split(' ')
        set2.append(seg)
    corpus1 = [] # from domain
    corpus2 = [] # to domain
    trainSet1 = []
    trainSet2 = []
    for topics in labelSet1:
        topic = sorted(topics.items(), key=operator.itemgetter(1))[2][0]
        topicList = [topic]
        trainSet1.append(topicList)
        for topic in topicList:
            if topic not in corpus1:
                corpus1.append(topic)
    for topics in set2:
        trainSet2.append(topics)
        for topic in topics:
            if topic not in corpus2:
                corpus2.append(topic)
    (confScore, model, cand, candProb) = utilities.generateModel2(corpus1, corpus2, trainSet1, trainSet2)

    return model, cand, candProb

def mappingTrainer4(alchemyLabels, keywordLabels):
    alchemyCorpus = [] # from domain
    keywordCorpus = [] # to domain
    alchemySet = []
    keywordSet = []

    for label in alchemyLabels:
        tempList = []
        for (topic, prob) in label.items():
            if topic not in alchemyCorpus:
                alchemyCorpus.append(topic)
            tempList.append(prob)
        normList = normalization(tempList)
        tempDict = {}
        for index, (topic, prob) in enumerate(label.items()):
            tempDict[topic] = normList[index]
        alchemySet.append(tempDict)

    for label in keywordLabels:
        if label not in keywordCorpus:
            keywordCorpus.append(label)
        keywordSet.append({label: 1.0})

    if len(keywordSet) != len(alchemySet):
        print 'Error in data size!'

    (model, cand, candProb) = utilities.generateModel3(alchemyCorpus, keywordCorpus, alchemySet, keywordSet)
    return model, cand, candProb


def mappingInfer(model, cand, testSet, testList):
    predictions = utilities.outputMappingResult(model, cand, testSet, testList, 3)
    return predictions

def mappingInfer2(model, cand, testSet, testList):
    predictions = utilities.outputMappingResult2(model, cand, testSet, testList)
    return predictions

def mappingInfer3(model, cand, candProb, testSet):
    predictions = utilities.outputMappingResult3(model, cand, candProb, testSet, 3)
    return predictions
