__author__ = 'renhao.cui'
import operator
import crossRef as cr
import math

def genFreq(corpus, data):
    corpusCount = {}
    for word in corpus:
        corpusCount[word] = 0.0
    for uttr in data:
        for word in uttr:
            corpusCount[word] += 1
    sorted_corpusCount = sorted(corpusCount.items(), key=operator.itemgetter(1))

    return reversed(sorted_corpusCount), corpusCount, sum(corpusCount.values())

def normalization(scoreList):
    outputList = []
    total = sum(scoreList)
    for score in scoreList:
        outputList.append(score/total)
    '''
    if len(scoreList) == 0:
        return []
    else:
        minNum = min(scoreList)
        maxNum = max(scoreList)
        diff = maxNum-minNum
        if diff == 0:
            print scoreList
        for score in scoreList:
            outputList.append((score-minNum)/diff)
    '''
    return outputList

def generateModel(corpusA, corpusB, trainDataA, trainDataB):
    ruleCount = {}
    countA = {}
    countB = {}
    confScore = {}
    #initialize
    for i in corpusA:
        for j in corpusB:
            ruleCount[i + ' ~ ' + j] = 0.0
    for i in corpusA:
        countA[i] = 0.0
    for i in corpusB:
        countB[i] = 0.0

    #counting
    for i in range(len(trainDataA)):
        for wordA in trainDataA[i]:
            countA[wordA] += 1
            for wordB in trainDataB[i]:
                ruleCount[wordA + ' ~ ' + wordB] += 1
        for wordB in trainDataB[i]:
            countB[wordB] += 1

    # calculate confidence score
    for i in corpusA:
        for j in corpusB:
            if countA[i] + countB[j] == 0:
                confScore[i + ' ~ ' + j] = 0.0
            else:
                confScore[i + ' ~ ' + j] = ruleCount[i + ' ~ ' + j] / (countA[i] + countB[j])
    output = {}
    for (key, value) in confScore.items():
        if value > 0:
            output[key] = value
    #ascending order
    sorted_output = sorted(output.items(), key=operator.itemgetter(1))
    # confidence score/rule from A to B: A ~ B
    # model from A to B: model[A] = B
    model = {}
    for item in sorted_output:
        temp = item[0].split(' ~ ')
        model[temp[0]] = (temp[1], float(item[1]))
    mostFreqB = max([(value, key) for key, value in countB.items()])[1]
    candProb = max([(value, key) for key, value in countB.items()])[0]/float(len(trainDataB))

    return output, model, mostFreqB, candProb

def generateModel2(corpusA, corpusB, trainDataA, trainDataB):
    ruleCount = {}
    support = {}
    countA = {}
    countB = {}
    confScore = {}
    #initialize
    for i in corpusA:
        for j in corpusB:
            ruleCount[i + ' ~ ' + j] = 0.0
    for i in corpusA:
        countA[i] = 0.0
    for i in corpusB:
        countB[i] = 0.0

    #counting
    for i in range(len(trainDataA)):
        for wordA in trainDataA[i]:
            countA[wordA] += 1.0
            for wordB in trainDataB[i]:
                ruleCount[wordA + ' ~ ' + wordB] += 1.0
        for wordB in trainDataB[i]:
            countB[wordB] += 1.0
    # calculate confidence score
    for i in corpusA:
        for j in corpusB:
            support[i + ' ~ ' + j] = ruleCount[i + ' ~ ' + j]/len(trainDataA)
            if countA[i] + countB[j] == 0:
                confScore[i + ' ~ ' + j] = 0
            else:
                confScore[i + ' ~ ' + j] = ruleCount[i + ' ~ ' + j] / countA[i]
    output = {}
    for (key, value) in confScore.items():
        if value > 0:
            output[key] = value
    sorted_output = sorted(output.items(), key=operator.itemgetter(1))
    # confidence score/rule from A to B: A ~ B
    # model from A to B: model[A] = B
    model = {}
    for item in sorted_output:
        temp = item[0].split(' ~ ')
        model[temp[0]] = (temp[1], float(item[1]))
    mostFreqB = max([(value, key) for key, value in countB.items()])[1]
    candProb = max([(value, key) for key, value in countB.items()])[0]/float(len(trainDataB))

    return output, model, mostFreqB, candProb

#latest
def generateModel3(alchemyCorpus, keywordCorpus, alchemySet, keywordSet):
    ruleCount = {}
    alchemyCount = {}
    keywordCount = {}
    confScore = {}

    #initialize
    for alchemyLabel in alchemyCorpus:
        tempDict = {}
        for keywordLabel in keywordCorpus:
            tempDict[keywordLabel] = 0.0
        ruleCount[alchemyLabel] = tempDict
    for alchemyLabel in alchemyCorpus:
        alchemyCount[alchemyLabel] = 0.0
    for keywordLabel in keywordCorpus:
        keywordCount[keywordLabel] = 0.0

    #counting
    for index, alchemyData in enumerate(alchemySet):
        for (labelA, probA) in alchemyData.items():
            alchemyCount[labelA] += probA
            for (labelB, probB) in keywordSet[index].items():
                ruleCount[labelA][labelB] += min(probA, probB)
        for (labelB, probB) in keywordSet[index].items():
            keywordCount[labelB] += probB

    # calculate confidence score
    for alchemyLabel in alchemyCorpus:
        tempDict = {}
        for keywordLabel in keywordCorpus:
            if alchemyCount[alchemyLabel] + keywordCount[keywordLabel] == 0:
                tempDict[keywordLabel] = 0.0
            else:
                tempDict[keywordLabel] = ruleCount[alchemyLabel][keywordLabel] / alchemyCount[alchemyLabel]
        confScore[alchemyLabel] = tempDict

    model = {}
    for (alchemyLabel, keywordValue) in confScore.items():
        output = {}
        for (keywordLabel, value) in keywordValue.items():
            output[keywordLabel] = value
        sorted_output = sorted(output.items(), key=operator.itemgetter(1), reverse=True)
        model[alchemyLabel] = {sorted_output[0][0]: sorted_output[0][1]}
    # model from A to B: model[A] = {B: score}

    candKeywordLabel = max([(value, key) for key, value in keywordCount.items()])[1]
    candProb = float(max([(value, key) for key, value in keywordCount.items()])[0])/float(len(keywordSet))

    return model, candKeywordLabel, candProb

def baseModel(cand, corpusA):
    outputModel = {}
    for word in corpusA:
        outputModel[word] = (cand, 1)
    return outputModel

def filterModel(confScore, limit):
    sorted_confScore = sorted(confScore.items(), key=operator.itemgetter(1))
    outputModel = {}
    '''
    for item in confScore.keys():
        if confScore[item] >= limit:
            temp = item.split(' ~ ')
            outputModel[temp[0]] = temp[1]
    '''
    for item in sorted_confScore:
        if item[1] > limit:
            temp = item[0].split(' ~ ')
            outputModel[temp[0]] = (temp[1], float(item[1]))

    return outputModel

def evaluateModel1(model, cand, testDataA, testDataB, testNum):
    correctCount = {}
    notFoundCount = 0.0
    totalUse = 0.0
    for (key, value) in model.items():
        correctCount[key + ' ~ ' + value[0]] = 0
    count = 0.0
    index = 0
    for itemDict in testDataA:
        correctFlag = False
        for i in range(testNum):
            item = itemDict.keys()
            if item[i] not in model.keys():
                prediction = cand
                notFoundCount += 1
            else:
                prediction = model[item[i]][0]
            totalUse += 1
            if prediction in testDataB[index]:
                correctFlag = True
                if item[i] + ' ~ ' + prediction in correctCount.keys():
                    correctCount[item[i] + ' ~ ' + prediction] += 1
        if correctFlag:
            count += 1
        index += 1

    return count / index, correctCount, 1 - (notFoundCount / totalUse)

def evaluateModel2(model, testDataA, testDataB, testNum):
    correctCount = {}
    useCount = {}

    for (key, value) in model.items():
        correctCount[key + ' ~ ' + value[0]] = 0.0
    for (key, value) in model.items():
        useCount[key + ' ~ ' + value[0]] = 0.0
    validCount = 0
    index = 0
    count = 0.0
    for itemDict in testDataA:
        validFlag = False
        correctFlag = False
        predTopicList = []
        for i in range(testNum):
            item = itemDict.keys()
            if item[i] in model.keys():
                prediction = model[item[i]][0]
                predTopicList.append(prediction)
                validFlag = True
                useCount[item[i] + ' ~ ' + prediction] += 1
                if prediction in testDataB[index]:
                    correctFlag = True
                    correctCount[item[i] + ' ~ ' + prediction] += 1
        if validFlag:
            validCount += 1
        if correctFlag:
            count += 1
        index += 1

    if validCount == 0:
        return 0, 0, 0
    else:
        return count / validCount, correctCount, useCount

def evaluateModel3(model, testDataA, testDataB, testNum):
    count = 0.0
    index = 0
    for itemDict in testDataA:
        predictionList = []
        confScoreList = []
        probList = []
        for i in range(testNum):
            item = itemDict.keys()
            alTopic = item[i]
            if alTopic in model.keys():
                probList.append(itemDict[alTopic])
                predictionList.append(model[alTopic][0])
                confScoreList.append(model[item[i]][1])
        probs = normalization(probList)
        confScores = normalization(confScoreList)
        maxScore = 0.0
        maxPrediction = ''
        for j in range(len(probs)):
            if probs[j]*confScores[j] >= maxScore:
                maxScore = probs[j]*confScores[j]
                maxPrediction = predictionList[j]
        if maxPrediction in testDataB[index]:
            count += 1
        index += 1

    return count / index

def evaluateModel4(model, testDataA, testDataB, ruleList, testNum):
    count = 0.0
    index = 0
    for itemDict in testDataA:
        probList = []
        similScoreList = []
        predictionList = []
        for i in range(testNum):
            item = itemDict.keys()
            alTopic = item[i]
            if alTopic in model.keys():
                tempScore = []
                seg = alTopic[1:].split('/')
                probList.append(itemDict[alTopic])
                sourceTopic = seg[len(seg)-1]
                prediction = model[alTopic][0]
                if prediction == 'Chilis_Alaska':
                    prediction = "Chili's_Alaska"
                predictionSeeds = ruleList[prediction]
                for seed in predictionSeeds:
                    tempScore.append(cr.phraseSimilarity(seed, sourceTopic))
                similScoreList.append(max(tempScore))
                predictionList.append(prediction)
        probs = normalization(probList)
        maxScore = 0.0
        maxPrediction = ''
        for j in range(len(probs)):
            combScore = probs[j] * similScoreList[j]
            if combScore >= maxScore:
                maxScore = combScore
                maxPrediction = predictionList[j]
        if maxPrediction in testDataB[index]:
            count += 1
        index += 1
    return count / index

def outputMappingResult(model, cand, testDataA, testList, testNum):
    outputPrediction = {}
    for validIndex in testList:
        itemDict = testDataA[validIndex]
        predictionList = []
        confScoreList = []
        probList = []
        for i in range(testNum):
            item = itemDict.keys()
            alTopic = item[i]
            if alTopic in model.keys():
                probList.append(itemDict[alTopic])
                predictionList.append(model[alTopic][0])
                confScoreList.append(model[item[i]][1])
        probs = normalization(probList)
        confScores = normalization(confScoreList)
        maxScore = 0.0
        maxPrediction = ''
        for j in range(len(probs)):
            if probs[j]*confScores[j] >= maxScore:
                maxScore = probs[j]*confScores[j]
                maxPrediction = predictionList[j]
        if maxPrediction == '':
            maxPrediction = cand
        outputPrediction[validIndex] = maxPrediction

    return outputPrediction

def outputMappingResult2(model, cand, testDataA, testList):
    outputPrediction = {}
    for validIndex in testList:
        itemDict = testDataA[validIndex]
        predictionList = []
        confScoreList = []
        probList = []
        for i in range(len(itemDict)):
            item = itemDict.keys()
            alTopic = item[i]
            if alTopic in model.keys():
                probList.append(itemDict[alTopic])
                predictionList.append(model[alTopic][0])
                confScoreList.append(model[item[i]][1])
        probs = normalization(probList)
        confScores = normalization(confScoreList)
        maxScore = 0.0
        maxPrediction = ''
        for j in range(len(probs)):
            if probs[j]*confScores[j] >= maxScore:
                maxScore = probs[j]*confScores[j]
                maxPrediction = predictionList[j]
        if maxPrediction == '':
            maxPrediction = cand
        outputPrediction[validIndex] = maxPrediction

    return outputPrediction

def outputMappingResult3(model, cand, candProb, testDataA, testNum):
    outputPrediction = {}
    for validIndex in range(len(testDataA)):
        itemDict = testDataA[validIndex]
        predictionList = []
        confScoreList = []
        probList = []
        item = itemDict.keys()
        for i in range(testNum):
            alTopic = item[i]
            if alTopic in model.keys():
                probList.append(itemDict[alTopic])
                predictionList.append(model[alTopic][0])
                confScoreList.append(model[alTopic][1])
        probs = probList
        if len(probs) == 0:
            outputPrediction[validIndex] = (cand, candProb, candProb, -1.0)
        else:
            confScores = confScoreList
            combScores = []
            for j in range(len(probs)):
                combScores.append(probs[j]*confScores[j])
            scores = combScores
            maxScore = -1.0
            maxPrediction = ''
            maxProb = 0.0
            maxConf = 0.0
            for j in range(len(scores)):
                if scores[j] >= maxScore:
                    maxScore = scores[j]
                    maxPrediction = predictionList[j]
                    maxProb = probs[j]
                    maxConf = confScores[j]
            outputPrediction[validIndex] = (maxPrediction, maxScore, maxProb, maxConf)

    return outputPrediction

def outputMappingResult3_fullList(model, cand, candProb, testData):
    prediction = {}
    for num, data in enumerate(testData):
        predictionList = []
        confScoreList = []
        probList = []
        combList = []

        for (topic, prob) in data.items():
            if topic in model:
                probList.append(prob)
                predictionList.append(model[topic].keys()[0])
                confScoreList.append(model[topic].values()[0])
                combList.append(prob*model[topic].values()[0])
            else:
                predictionList.append(cand)
                combList.append(candProb*0.0001)
        if len(probList) == 0:
            prediction[num] = {1: {cand: candProb*0.0001}}
        else:
            normProbs = normalization(combList)
            tempDict = {}
            for index, label in enumerate(predictionList):
                if label in tempDict:
                    tempDict[label] = tempDict[label] + float(normProbs[index])
                else:
                    tempDict[label] = float(normProbs[index])

            sorted_tempList = sorted(tempDict.items(), key=operator.itemgetter(1), reverse=True)
            tempDict = {}
            for index, (label, prob) in enumerate(sorted_tempList):
                tempDict[index+1] = {label: prob}
            prediction[num] = tempDict

    return prediction
