__author__ = 'renhao.cui'
import random
import operator


def normalization(scoreList):
    outputList = []
    total = sum(scoreList)
    for score in scoreList:
        outputList.append(score / total)
    return outputList


def getInitialList(num):
    if num == 2:
        dist = random.random(0.001, 0.9)
        return [dist, 1 - dist]
    else:
        dist1 = random.random(0.001, 0.7)
        dist2 = random.random(0.001, 0.9 - dist1)
        return [dist1, dist2, 1 - dist1 - dist2]


def LLDAwithMaxEnt(LLDATopics, LLDATopic, LLDAProb, maxEntTopics, maxEntTopic, maxEntProb, AlchemyTopics,
                   LLDAWeightList, maxEntWeightList):
    predTopics = {}
    if len(LLDATopics) == 0:
        if len(maxEntTopics) == 0:
            predTopic = random.choice(AlchemyTopics.keys())
            predScore = AlchemyTopics[predTopic]
        else:
            predTopic = maxEntTopic
            predScore = maxEntTopics[predTopic]
    else:
        if len(maxEntTopics) == 0:
            predTopic = LLDATopic
            predScore = LLDATopics[predTopic]
        else:
            topicList = []
            for topic in maxEntTopics:
                topicList.append(topic)
            for topic in LLDATopics:
                topicList.append(topic)
            uniqueTopics = list(set(topicList))
            for topic in uniqueTopics:
                predTopics[topic] = 0.0
                if topic in maxEntTopics:
                    predTopics[topic] += maxEntTopics[topic] * maxEntWeightList[topic]
                if topic in LLDATopics:
                    predTopics[topic] += LLDATopics[topic] * LLDAWeightList[topic]
            predTopic = max(predTopics.iteritems(), key=operator.itemgetter(1))[0]
            predScore = max(predTopics.iteritems(), key=operator.itemgetter(1))[1]
    return predTopic, 1


def LLDAwithAlchemy(LLDATopics, LLDATopic, LLDAProb, AlchemyTopics, AlchemyTopic, LLDAWeightList, AlchemyWeightList):
    predTopics = {}
    if len(LLDATopics) == 0:
        predTopic = AlchemyTopic
        predScore = AlchemyTopics[predTopic]
    else:
        for (topic, prob) in LLDATopics.items():
            prob = prob * LLDAWeightList[topic]
            if topic in AlchemyTopics:
                predTopics[topic] = prob + AlchemyTopics[topic] * AlchemyWeightList[topic]
            else:
                predTopics[topic] = prob
        predTopic = max(predTopics.iteritems(), key=operator.itemgetter(1))[0]
        predScore = max(predTopics.iteritems(), key=operator.itemgetter(1))[1]
    return predTopic, 1


def MaxEntwithAlchemy(maxEntTopics, maxEntTopic, maxEntProb, AlchemyTopics, AlchemyTopic, maxEntWeightList,
                      AlchemyWeightList):
    predTopics = {}
    if len(maxEntTopics) == 0:
        predTopic = AlchemyTopic
        predScore = AlchemyTopics[predTopic]
    else:
        topicList = []
        for topic in maxEntTopics:
            topicList.append(topic)
        for topic in AlchemyTopics:
            topicList.append(topic)
        uniqueTopics = list(set(topicList))
        for topic in uniqueTopics:
            predTopics[topic] = 0.0
            if topic in maxEntTopics:
                predTopics[topic] += maxEntTopics[topic] * maxEntWeightList[topic]
            if topic in AlchemyTopics:
                predTopics[topic] += AlchemyTopics[topic] * AlchemyWeightList[topic]
        predTopic = max(predTopics.iteritems(), key=operator.itemgetter(1))[0]
        predScore = max(predTopics.iteritems(), key=operator.itemgetter(1))[1]
    return predTopic, 1


def all(LLDATopics, LLDATopic, LLDAProb, maxEntTopics, maxEntTopic, maxEntProb, AlchemyTopics, AlchemyTopic,
        LLDAWeightList, maxEntWeightList, AlchemyWeightList):
    if len(LLDATopics) == 0:
        return MaxEntwithAlchemy(maxEntTopics, maxEntTopic, maxEntProb, AlchemyTopics, AlchemyTopic, maxEntWeightList,
                                 AlchemyWeightList)
    elif len(maxEntTopics) == 0:
        return LLDAwithAlchemy(LLDATopics, LLDATopic, LLDAProb, AlchemyTopics, AlchemyTopic, LLDAWeightList,
                               AlchemyWeightList)
    else:
        predTopics = {}
        topicList = []
        for topic in LLDATopics.keys():
            topicList.append(topic)
        for topic in AlchemyTopics.keys():
            topicList.append(topic)
        for topic in maxEntTopics.keys():
            topicList.append(topic)
        uniqueTopics = list(set(topicList))
        for topic in uniqueTopics:
            predTopics[topic] = 0.0
            if topic in LLDATopics:
                predTopics[topic] += LLDATopics[topic] * LLDAWeightList[topic]
            if topic in AlchemyTopics:
                predTopics[topic] += AlchemyTopics[topic] * AlchemyWeightList[topic]
            if topic in maxEntTopics:
                predTopics[topic] += maxEntTopics[topic] * maxEntWeightList[topic]
        predTopic = max(predTopics.iteritems(), key=operator.itemgetter(1))[0]
        predScore = max(predTopics.iteritems(), key=operator.itemgetter(1))[1]
    return predTopic, 1


fold = 5
brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']
iterations = 100
learningRateList = [0.9]

for brand in brandList:
    print brand
    for learningRate in learningRateList:
        accuracy = []
        for l in range(4):
            accuracy.append(0.0)
        for j in range(fold):
            # read in the data
            LLDATestData = {}
            MaxEntTestData = {}
            TrueLabelTestData = {}
            AlchemyTestData = {}

            LLDATrainData = {}
            MaxEntTrainData = {}
            TrueLabelTrainData = {}
            AlchemyTrainData = {}

            topicCorpus = {}

            LLDATrainFile = open('HybridData//LLDATrain//' + brand + '.' + str(j), 'r')
            trueLabelTrainFile = open('HybridData//TrueLabelTrain//' + brand + '.' + str(j), 'r')
            maxEntTrainFile = open('HybridData//MaxEntTrain//' + brand + '.' + str(j), 'r')
            AlchemyTrainFile = open('HybridData//AlchemyTrain//' + brand + '.' + str(j), 'r')

            LLDATestFile = open('HybridData//LLDATest//' + brand + '.' + str(j) + ',0.0', 'r')
            trueLabelTestFile = open('HybridData//TrueLabelTest//' + brand + '.' + str(j), 'r')
            maxEntTestFile = open('HybridData//MaxEntTest//' + brand + '.' + str(j) + ',0.0', 'r')
            AlchemyTestFile = open('HybridData//AlchemyTest//' + brand + '.' + str(j), 'r')

            # read in test data
            index = 0
            for line in LLDATestFile:
                temp = {}
                if len(line.strip()) > 0:
                    items = line.strip().split('\t')
                    for item in items:
                        seg = item.split(':')
                        temp[seg[0]] = float(seg[1])
                LLDATestData[index] = temp
                index += 1
            LLDATestFile.close()

            index = 0
            for line in maxEntTestFile:
                temp = {}
                if len(line.strip()) > 0:
                    items = line.strip().split('\t')
                    for item in items:
                        seg = item.split(':')
                        temp[seg[0]] = float(seg[1])
                MaxEntTestData[index] = temp
                index += 1
            maxEntTestFile.close()

            index = 0
            for line in AlchemyTestFile:
                temp = {}
                if len(line.strip()) > 0:
                    items = line.strip().split('\t')
                    for item in items:
                        seg = item.split(':')
                        temp[seg[0]] = float(seg[1])
                AlchemyTestData[index] = temp
                index += 1
            AlchemyTestFile.close()

            index = 0
            for line in trueLabelTestFile:
                labelList = line.strip().split(' ')
                TrueLabelTestData[index] = labelList
                index += 1
            trueLabelTestFile.close()

            if len(TrueLabelTestData) == len(LLDATestData) and len(LLDATestData) == len(MaxEntTestData) and len(
                    AlchemyTestData) == len(MaxEntTestData):
                testSize = len(TrueLabelTestData)
            else:
                print 'Test input file sizes do not match iter: ' + str(j)
                print str(len(TrueLabelTestData)) + ' ' + str(len(LLDATestData)) + ' ' + str(
                    len(MaxEntTestData)) + ' ' + str(len(AlchemyTestData))
                break

            # read in train data
            index = 0
            for line in LLDATrainFile:
                temp = {}
                if len(line.strip()) > 0:
                    items = line.strip().split('\t')
                    for item in items:
                        seg = item.split(':')
                        temp[seg[0]] = float(seg[1])
                LLDATrainData[index] = temp
                index += 1
            LLDATrainFile.close()

            index = 0
            for line in maxEntTrainFile:
                temp = {}
                if len(line.strip()) > 0:
                    items = line.strip().split('\t')
                    for item in items:
                        seg = item.split(':')
                        temp[seg[0]] = float(seg[1])
                MaxEntTrainData[index] = temp
                index += 1
            maxEntTrainFile.close()

            index = 0
            for line in AlchemyTrainFile:
                temp = {}
                if len(line.strip()) > 0:
                    items = line.strip().split('\t')
                    for item in items:
                        seg = item.split(':')
                        temp[seg[0]] = float(seg[1])
                AlchemyTrainData[index] = temp
                index += 1
            AlchemyTrainFile.close()

            index = 0
            for line in trueLabelTrainFile:
                labelList = line.strip().split(' ')
                TrueLabelTrainData[index] = labelList
                for label in labelList:
                    if label not in topicCorpus:
                        topicCorpus[label] = 0
                    else:
                        topicCorpus[label] += 1
                index += 1
            trueLabelTrainFile.close()

            if len(TrueLabelTrainData) == len(LLDATrainData) and len(LLDATrainData) == len(MaxEntTrainData) and len(
                    MaxEntTrainData) == len(AlchemyTrainData):
                trainSize = len(TrueLabelTrainData)
            else:
                print 'Train input file sizes do not match iter: ' + str(j)
                print str(len(TrueLabelTrainData)) + ' ' + str(len(LLDATrainData)) + ' ' + str(
                    len(MaxEntTrainData)) + ' ' + str(len(AlchemyTrainData))
                break

            # train voting weights
            LLDAWeightList = []
            maxEntWeightList = []
            AlchemyWeightList = []
            LLDAWeightTotalList = []
            maxEntWeightTotalList = []
            AlchemyWeightTotalList = []
            updateCount = []
            # 0-> LLDA+MaxEnt, 1-> LLDA+Alchemy, 2-> MaxEnt + Alchemy, 3-> All
            for l in range(4):
                LLDATemp = {}
                maxEntTemp = {}
                AlchemyTemp = {}
                LLDATotalTemp = {}
                maxEntTotalTemp = {}
                AlchemyTotalTemp = {}
                updateCountTemp = {}
                for topic in topicCorpus:
                    if l != 3:
                        LLDATemp[topic] = 1 / 2.0
                        maxEntTemp[topic] = 1 / 2.0
                        AlchemyTemp[topic] = 1 / 2.0
                    else:
                        LLDATemp[topic] = 1 / 3.0
                        maxEntTemp[topic] = 1 / 3.0
                        AlchemyTemp[topic] = 1 / 3.0
                    LLDATotalTemp[topic] = 0.0
                    maxEntTotalTemp[topic] = 0.0
                    AlchemyTotalTemp[topic] = 0.0
                    updateCountTemp[topic] = 0.0
                LLDAWeightList.append(LLDATemp)
                maxEntWeightList.append(maxEntTemp)
                AlchemyWeightList.append(AlchemyTemp)
                LLDAWeightTotalList.append(LLDATotalTemp)
                maxEntWeightTotalList.append(maxEntTotalTemp)
                AlchemyWeightTotalList.append(AlchemyTotalTemp)
                updateCount.append(updateCountTemp)

            for iter in range(iterations):
                # print 'iteration: '+str(iter)
                #print str(LLDATrainWeight) + ' '+str(maxEntTrainWeight)
                for index in range(trainSize):
                    LLDATrainTopics = LLDATrainData[index]
                    maxEntTrainTopics = MaxEntTrainData[index]
                    AlchemyTrainTopics = AlchemyTrainData[index]
                    if len(LLDATrainTopics) > 0:
                        (LLDATrainTopic, LLDATrainProb) = max(LLDATrainTopics.iteritems(), key=operator.itemgetter(1))
                    if len(maxEntTrainTopics) > 0:
                        (maxEntTrainTopic, maxEntTrainProb) = max(maxEntTrainTopics.iteritems(),
                                                                  key=operator.itemgetter(1))
                    (AlchemyTrainTopic, AlchemyTrainProb) = max(AlchemyTrainTopics.iteritems(),
                                                                key=operator.itemgetter(1))

                    # LLDA + MaxEnt
                    predTopic, predScore = LLDAwithMaxEnt(LLDATrainTopics, LLDATrainTopic, LLDATrainProb,
                                                          maxEntTrainTopics, maxEntTrainTopic, maxEntTrainProb,
                                                          AlchemyTrainTopics, LLDAWeightList[0], maxEntWeightList[0])
                    if predTopic not in TrueLabelTrainData[index]:
                        updatedLLDATopics = {}
                        updatedMaxEntTopics = {}
                        temp = {}
                        for topic in topicCorpus:
                            updatedLLDATopics[topic] = LLDATrainTopics[topic] * LLDAWeightList[0][topic]
                            updatedMaxEntTopics[topic] = maxEntTrainTopics[topic] * maxEntWeightList[0][topic]
                            temp[topic] = updatedMaxEntTopics[topic] + updatedLLDATopics[topic]
                        (LLDATrainTopic, LLDATrainProb) = max(updatedLLDATopics.iteritems(), key=operator.itemgetter(1))
                        (maxEntTrainTopic, maxEntTrainProb) = max(updatedMaxEntTopics.iteritems(),
                                                                  key=operator.itemgetter(1))


                        if (LLDATrainTopic not in TrueLabelTrainData[index]) and (
                                    maxEntTrainTopic in TrueLabelTrainData[index]):
                            tempList = normalization([LLDAWeightList[0][LLDATrainTopic] * learningRate * predScore,
                                                      maxEntWeightList[0][LLDATrainTopic]])
                            LLDAWeightList[0][LLDATrainTopic] = tempList[0]
                            maxEntWeightList[0][LLDATrainTopic] = tempList[1]
                            LLDAWeightTotalList[0][LLDATrainTopic] += tempList[0]
                            maxEntWeightTotalList[0][LLDATrainTopic] += tempList[1]
                            updateCount[0][LLDATrainTopic] += 1.0
                        elif (LLDATrainTopic in TrueLabelTrainData[index]) and (
                                    maxEntTrainTopic not in TrueLabelTrainData[index]):
                            tempList = normalization([LLDAWeightList[0][maxEntTrainTopic],
                                                      maxEntWeightList[0][maxEntTrainTopic] * learningRate * predScore])
                            LLDAWeightList[0][maxEntTrainTopic] = tempList[0]
                            maxEntWeightList[0][maxEntTrainTopic] = tempList[1]
                            LLDAWeightTotalList[0][maxEntTrainTopic] += tempList[0]
                            maxEntWeightTotalList[0][maxEntTrainTopic] += tempList[1]
                            updateCount[0][maxEntTrainTopic] += 1.0


                    # LLDA + Alchemy
                    predTopic, predScore = LLDAwithAlchemy(LLDATrainTopics, LLDATrainTopic, LLDATrainProb,
                                                           AlchemyTrainTopics, AlchemyTrainTopic, LLDAWeightList[1],
                                                           AlchemyWeightList[1])
                    if predTopic not in TrueLabelTrainData[index]:
                        updatedLLDATopics = {}
                        updatedAlchemyTopics = {}
                        temp = {}
                        for topic in topicCorpus:
                            updatedLLDATopics[topic] = LLDATrainTopics[topic] * LLDAWeightList[1][topic]
                            temp[topic] = updatedLLDATopics[topic]
                            if topic in AlchemyTrainTopics:
                                updatedAlchemyTopics[topic] = AlchemyTrainTopics[topic] * AlchemyWeightList[1][topic]
                                temp[topic] += updatedAlchemyTopics[topic]
                        (LLDATrainTopic, LLDATrainProb) = max(updatedLLDATopics.iteritems(), key=operator.itemgetter(1))
                        (AlchemyTrainTopic, AlchemyTrainProb) = max(updatedAlchemyTopics.iteritems(),
                                                                    key=operator.itemgetter(1))

                        if (LLDATrainTopic not in TrueLabelTrainData[index]) and (
                                    AlchemyTrainTopic in TrueLabelTrainData[index]):
                            tempList = normalization([LLDAWeightList[1][LLDATrainTopic] * learningRate * predScore,
                                                      AlchemyWeightList[1][LLDATrainTopic]])
                            LLDAWeightList[1][LLDATrainTopic] = tempList[0]
                            AlchemyWeightList[1][LLDATrainTopic] = tempList[1]
                            LLDAWeightTotalList[1][LLDATrainTopic] += tempList[0]
                            AlchemyWeightTotalList[1][LLDATrainTopic] += tempList[1]
                            updateCount[1][LLDATrainTopic] += 1.0
                        elif (LLDATrainTopic in TrueLabelTrainData[index]) and (
                                    AlchemyTrainTopic not in TrueLabelTrainData[index]):
                            tempList = normalization([LLDAWeightList[1][AlchemyTrainTopic], AlchemyWeightList[1][
                                AlchemyTrainTopic] * learningRate * predScore])
                            LLDAWeightList[1][AlchemyTrainTopic] = tempList[0]
                            AlchemyWeightList[1][AlchemyTrainTopic] = tempList[1]
                            LLDAWeightTotalList[1][AlchemyTrainTopic] += tempList[0]
                            AlchemyWeightTotalList[1][AlchemyTrainTopic] += tempList[1]
                            updateCount[1][AlchemyTrainTopic] += 1.0

                    #MaxEnt + Alchemy
                    predTopic, predScore = MaxEntwithAlchemy(maxEntTrainTopics, maxEntTrainTopic, maxEntTrainProb,
                                                             AlchemyTrainTopics, AlchemyTrainTopic, maxEntWeightList[2],
                                                             AlchemyWeightList[2])
                    if predTopic not in TrueLabelTrainData[index]:
                        updatedMaxEntTopics = {}
                        updatedAlchemyTopics = {}
                        temp = {}
                        for topic in topicCorpus:
                            updatedMaxEntTopics[topic] = maxEntTrainTopics[topic] * maxEntWeightList[2][topic]
                            temp[topic] = updatedMaxEntTopics[topic]
                            if topic in AlchemyTrainTopics:
                                updatedAlchemyTopics[topic] = AlchemyTrainTopics[topic] * AlchemyWeightList[2][topic]
                                temp[topic] += updatedAlchemyTopics[topic]
                        (maxEntTrainTopic, maxEntTrainProb) = max(updatedMaxEntTopics.iteritems(),
                                                                  key=operator.itemgetter(1))
                        (AlchemyTrainTopic, AlchemyTrainProb) = max(updatedAlchemyTopics.iteritems(),
                                                                    key=operator.itemgetter(1))

                        if (maxEntTrainTopic not in TrueLabelTrainData[index]) and (
                                    AlchemyTrainTopic in TrueLabelTrainData[index]):
                            tempList = normalization([maxEntWeightList[2][maxEntTrainTopic] * learningRate * predScore,
                                                      AlchemyWeightList[2][maxEntTrainTopic]])
                            maxEntWeightList[2][maxEntTrainTopic] = tempList[0]
                            AlchemyWeightList[2][maxEntTrainTopic] = tempList[1]
                            maxEntWeightTotalList[2][maxEntTrainTopic] += tempList[0]
                            AlchemyWeightTotalList[2][maxEntTrainTopic] += tempList[1]
                            updateCount[2][maxEntTrainTopic] += 1.0
                        elif (maxEntTrainTopic in TrueLabelTrainData[index]) and (
                                    AlchemyTrainTopic not in TrueLabelTrainData[index]):
                            tempList = normalization([maxEntWeightList[2][AlchemyTrainTopic], AlchemyWeightList[2][
                                AlchemyTrainTopic] * learningRate * predScore])
                            maxEntWeightList[2][AlchemyTrainTopic] = tempList[0]
                            AlchemyWeightList[2][AlchemyTrainTopic] = tempList[1]
                            maxEntWeightTotalList[2][AlchemyTrainTopic] += tempList[0]
                            AlchemyWeightTotalList[2][AlchemyTrainTopic] += tempList[1]
                            updateCount[2][AlchemyTrainTopic] += 1.0

                    # all
                    predTopic, predScore = all(LLDATrainTopics, LLDATrainTopic, LLDATrainProb, maxEntTrainTopics,
                                               maxEntTrainTopic, maxEntTrainProb, AlchemyTrainTopics, AlchemyTrainTopic,
                                               LLDAWeightList[3], maxEntWeightList[3], AlchemyWeightList[3])
                    if predTopic not in TrueLabelTrainData[index]:
                        updatedMaxEntTopics = {}
                        updatedAlchemyTopics = {}
                        updatedLLDATopics = {}
                        temp = {}
                        for topic in topicCorpus:
                            updatedLLDATopics[topic] = LLDATrainTopics[topic] * LLDAWeightList[3][topic]
                            updatedMaxEntTopics[topic] = maxEntTrainTopics[topic] * maxEntWeightList[3][topic]
                            temp[topic] = updatedMaxEntTopics[topic] + updatedLLDATopics[topic]
                            if topic in AlchemyTrainTopics:
                                updatedAlchemyTopics[topic] = AlchemyTrainTopics[topic] * AlchemyWeightList[3][topic]
                                temp[topic] += updatedAlchemyTopics[topic]
                        (LLDATrainTopic, LLDATrainProb) = max(updatedLLDATopics.iteritems(), key=operator.itemgetter(1))
                        (maxEntTrainTopic, maxEntTrainProb) = max(updatedMaxEntTopics.iteritems(),
                                                                  key=operator.itemgetter(1))
                        (AlchemyTrainTopic, AlchemyTrainProb) = max(updatedAlchemyTopics.iteritems(),
                                                                    key=operator.itemgetter(1))

                        if LLDATrainTopic in TrueLabelTrainData[index] and maxEntTrainTopic in TrueLabelTrainData[
                            index] and AlchemyTrainTopic not in TrueLabelTrainData[index]:
                            tempList = normalization(
                                [LLDAWeightList[3][AlchemyTrainTopic], maxEntWeightList[3][AlchemyTrainTopic],
                                 AlchemyWeightList[3][AlchemyTrainTopic] * learningRate * predScore])
                            LLDAWeightList[3][AlchemyTrainTopic] = tempList[0]
                            maxEntWeightList[3][AlchemyTrainTopic] = tempList[1]
                            AlchemyWeightList[3][AlchemyTrainTopic] = tempList[2]
                            LLDAWeightTotalList[3][AlchemyTrainTopic] += tempList[0]
                            maxEntWeightTotalList[3][AlchemyTrainTopic] += tempList[1]
                            AlchemyWeightTotalList[3][AlchemyTrainTopic] += tempList[2]
                            updateCount[3][AlchemyTrainTopic] += 1.0
                        elif LLDATrainTopic in TrueLabelTrainData[index] and maxEntTrainTopic not in TrueLabelTrainData[
                            index] and AlchemyTrainTopic in TrueLabelTrainData[index]:
                            tempList = normalization([LLDAWeightList[3][maxEntTrainTopic],
                                                      maxEntWeightList[3][maxEntTrainTopic] * learningRate * predScore,
                                                      AlchemyWeightList[3][maxEntTrainTopic]])
                            LLDAWeightList[3][maxEntTrainTopic] = tempList[0]
                            maxEntWeightList[3][maxEntTrainTopic] = tempList[1]
                            AlchemyWeightList[3][maxEntTrainTopic] = tempList[2]
                            LLDAWeightTotalList[3][maxEntTrainTopic] += tempList[0]
                            maxEntWeightTotalList[3][maxEntTrainTopic] += tempList[1]
                            AlchemyWeightTotalList[3][maxEntTrainTopic] += tempList[2]
                            updateCount[3][maxEntTrainTopic] += 1.0
                        elif LLDATrainTopic in TrueLabelTrainData[index] and maxEntTrainTopic not in TrueLabelTrainData[
                            index] and AlchemyTrainTopic not in TrueLabelTrainData[index]:
                            tempList = normalization([LLDAWeightList[3][maxEntTrainTopic],
                                                      maxEntWeightList[3][maxEntTrainTopic] * learningRate * predScore,
                                                      AlchemyWeightList[3][maxEntTrainTopic]])
                            LLDAWeightList[3][maxEntTrainTopic] = tempList[0]
                            maxEntWeightList[3][maxEntTrainTopic] = tempList[1]
                            AlchemyWeightList[3][maxEntTrainTopic] = tempList[2]
                            LLDAWeightTotalList[3][maxEntTrainTopic] += tempList[0]
                            maxEntWeightTotalList[3][maxEntTrainTopic] += tempList[1]
                            AlchemyWeightTotalList[3][maxEntTrainTopic] += tempList[2]
                            updateCount[3][maxEntTrainTopic] += 1.0

                            tempList = normalization(
                                [LLDAWeightList[3][AlchemyTrainTopic], maxEntWeightList[3][AlchemyTrainTopic],
                                 AlchemyWeightList[3][AlchemyTrainTopic] * learningRate * predScore])
                            LLDAWeightList[3][AlchemyTrainTopic] = tempList[0]
                            maxEntWeightList[3][AlchemyTrainTopic] = tempList[1]
                            AlchemyWeightList[3][AlchemyTrainTopic] = tempList[2]
                            LLDAWeightTotalList[3][AlchemyTrainTopic] += tempList[0]
                            maxEntWeightTotalList[3][AlchemyTrainTopic] += tempList[1]
                            AlchemyWeightTotalList[3][AlchemyTrainTopic] += tempList[2]
                            updateCount[3][AlchemyTrainTopic] += 1.0

                        elif LLDATrainTopic not in TrueLabelTrainData[index] and maxEntTrainTopic in TrueLabelTrainData[
                            index] and AlchemyTrainTopic in TrueLabelTrainData[index]:
                            tempList = normalization([LLDAWeightList[3][LLDATrainTopic] * learningRate * predScore,
                                                      maxEntWeightList[3][LLDATrainTopic],
                                                      AlchemyWeightList[3][LLDATrainTopic]])
                            LLDAWeightList[3][LLDATrainTopic] = tempList[0]
                            maxEntWeightList[3][LLDATrainTopic] = tempList[1]
                            AlchemyWeightList[3][LLDATrainTopic] = tempList[2]
                            LLDAWeightTotalList[3][LLDATrainTopic] += tempList[0]
                            maxEntWeightTotalList[3][LLDATrainTopic] += tempList[1]
                            AlchemyWeightTotalList[3][LLDATrainTopic] += tempList[2]
                            updateCount[3][LLDATrainTopic] += 1.0
                        elif LLDATrainTopic not in TrueLabelTrainData[index] and maxEntTrainTopic in TrueLabelTrainData[
                            index] and AlchemyTrainTopic not in TrueLabelTrainData[index]:
                            tempList = normalization([LLDAWeightList[3][LLDATrainTopic] * learningRate * predScore,
                                                      maxEntWeightList[3][LLDATrainTopic],
                                                      AlchemyWeightList[3][LLDATrainTopic]])
                            LLDAWeightList[3][LLDATrainTopic] = tempList[0]
                            maxEntWeightList[3][LLDATrainTopic] = tempList[1]
                            AlchemyWeightList[3][LLDATrainTopic] = tempList[2]
                            LLDAWeightTotalList[3][LLDATrainTopic] += tempList[0]
                            maxEntWeightTotalList[3][LLDATrainTopic] += tempList[1]
                            AlchemyWeightTotalList[3][LLDATrainTopic] += tempList[2]
                            updateCount[3][LLDATrainTopic] += 1.0

                            tempList = normalization(
                                [LLDAWeightList[3][AlchemyTrainTopic], maxEntWeightList[3][AlchemyTrainTopic],
                                 AlchemyWeightList[3][AlchemyTrainTopic] * learningRate * predScore])
                            LLDAWeightList[3][AlchemyTrainTopic] = tempList[0]
                            maxEntWeightList[3][AlchemyTrainTopic] = tempList[1]
                            AlchemyWeightList[3][AlchemyTrainTopic] = tempList[2]
                            LLDAWeightTotalList[3][AlchemyTrainTopic] += tempList[0]
                            maxEntWeightTotalList[3][AlchemyTrainTopic] += tempList[1]
                            AlchemyWeightTotalList[3][AlchemyTrainTopic] += tempList[2]
                            updateCount[3][AlchemyTrainTopic] += 1.0

                        elif LLDATrainTopic not in TrueLabelTrainData[index] and maxEntTrainTopic not in \
                                TrueLabelTrainData[index] and AlchemyTrainTopic in TrueLabelTrainData[index]:
                            tempList = normalization([LLDAWeightList[3][LLDATrainTopic] * learningRate * predScore,
                                                      maxEntWeightList[3][LLDATrainTopic],
                                                      AlchemyWeightList[3][LLDATrainTopic]])
                            LLDAWeightList[3][LLDATrainTopic] = tempList[0]
                            maxEntWeightList[3][LLDATrainTopic] = tempList[1]
                            AlchemyWeightList[3][LLDATrainTopic] = tempList[2]
                            LLDAWeightTotalList[3][LLDATrainTopic] += tempList[0]
                            maxEntWeightTotalList[3][LLDATrainTopic] += tempList[1]
                            AlchemyWeightTotalList[3][LLDATrainTopic] += tempList[2]
                            updateCount[3][LLDATrainTopic] += 1.0

                            tempList = normalization([LLDAWeightList[3][maxEntTrainTopic],
                                                      maxEntWeightList[3][maxEntTrainTopic] * learningRate * predScore,
                                                      AlchemyWeightList[3][maxEntTrainTopic]])
                            LLDAWeightList[3][maxEntTrainTopic] = tempList[0]
                            maxEntWeightList[3][maxEntTrainTopic] = tempList[1]
                            AlchemyWeightList[3][maxEntTrainTopic] = tempList[2]
                            LLDAWeightTotalList[3][maxEntTrainTopic] += tempList[0]
                            maxEntWeightTotalList[3][maxEntTrainTopic] += tempList[1]
                            AlchemyWeightTotalList[3][maxEntTrainTopic] += tempList[2]
                            updateCount[3][maxEntTrainTopic] += 1.0


            # test
            # print 'Resulting weights: '+str(LLDAWeightList) + ' '+str(maxEntWeightList) + ' ' + str(AlchemyWeightList)
            correct = []
            for l in range(4):
                correct.append(0.0)
            total = 0.0
            for i in range(testSize):
                LLDATestTopics = LLDATestData[i]
                maxEntTestTopics = MaxEntTestData[i]
                AlchemyTestTopics = AlchemyTestData[i]
                if len(LLDATestTopics) > 0:
                    (LLDATestTopic, LLDATestProb) = max(LLDATestTopics.iteritems(), key=operator.itemgetter(1))
                if len(maxEntTestTopics) > 0:
                    (maxEntTestTopic, maxEntTestProb) = max(maxEntTestTopics.iteritems(), key=operator.itemgetter(1))
                (AlchemyTestTopic, mappingTestProb) = max(AlchemyTestTopics.iteritems(), key=operator.itemgetter(1))

                # LLDA + MaxEnt
                LLDAWeightTemp = {}
                maxEntWeightTemp = {}
                for topic in topicCorpus:
                    if updateCount[0][topic] == 0:
                        LLDAWeightTemp[topic] = LLDAWeightList[0][topic]
                        maxEntWeightTemp[topic] = maxEntWeightList[0][topic]
                    else:
                        LLDAWeightTemp[topic] = LLDAWeightTotalList[0][topic] / updateCount[0][topic]
                        maxEntWeightTemp[topic] = maxEntWeightTotalList[0][topic] / updateCount[0][topic]
                predTopic, predScore = LLDAwithMaxEnt(LLDATestTopics, LLDATestTopic, LLDATestProb, maxEntTestTopics,
                                                      maxEntTestTopic, maxEntTestProb, AlchemyTestTopics,
                                                      LLDAWeightTemp, maxEntWeightTemp)
                if predTopic in TrueLabelTestData[i]:
                    correct[0] += 1.0

                # LLDA + Alchemy
                LLDAWeightTemp = {}
                AlchemyWeightTemp = {}
                for topic in topicCorpus:
                    if updateCount[1][topic] == 0:
                        LLDAWeightTemp[topic] = LLDAWeightList[1][topic]
                        AlchemyWeightTemp[topic] = AlchemyWeightList[1][topic]
                    else:
                        LLDAWeightTemp[topic] = LLDAWeightTotalList[1][topic] / updateCount[1][topic]
                        AlchemyWeightTemp[topic] = AlchemyWeightTotalList[1][topic] / updateCount[1][topic]
                predTopic, predScore = LLDAwithAlchemy(LLDATestTopics, LLDATestTopic, LLDATestProb, AlchemyTestTopics,
                                                       AlchemyTestTopic, LLDAWeightTemp, AlchemyWeightTemp)
                if predTopic in TrueLabelTestData[i]:
                    correct[1] += 1.0

                # MaxEnt + Alchemy
                AlchemyWeightTemp = {}
                maxEntWeightTemp = {}
                for topic in topicCorpus:
                    if updateCount[2][topic] == 0:
                        AlchemyWeightTemp[topic] = AlchemyWeightList[2][topic]
                        maxEntWeightTemp[topic] = maxEntWeightList[2][topic]
                    else:
                        AlchemyWeightTemp[topic] = AlchemyWeightTotalList[2][topic] / updateCount[2][topic]
                        maxEntWeightTemp[topic] = maxEntWeightTotalList[2][topic] / updateCount[2][topic]
                predTopic, predScore = MaxEntwithAlchemy(maxEntTestTopics, maxEntTestTopic, maxEntTestProb,
                                                         AlchemyTestTopics, AlchemyTestTopic, maxEntWeightTemp,
                                                         AlchemyWeightTemp)
                if predTopic in TrueLabelTestData[i]:
                    correct[2] += 1.0

                # all
                LLDAWeightTemp = {}
                maxEntWeightTemp = {}
                AlchemyWeightTemp = {}
                for topic in topicCorpus:
                    if updateCount[3][topic] == 0:
                        AlchemyWeightTemp[topic] = AlchemyWeightList[3][topic]
                        maxEntWeightTemp[topic] = maxEntWeightList[3][topic]
                        LLDAWeightTemp[topic] = LLDAWeightList[3][topic]
                    else:
                        AlchemyWeightTemp[topic] = AlchemyWeightTotalList[3][topic] / updateCount[3][topic]
                        LLDAWeightTemp[topic] = LLDAWeightTotalList[3][topic] / updateCount[3][topic]
                        maxEntWeightTemp[topic] = maxEntWeightTotalList[3][topic] / updateCount[3][topic]
                predTopic, predScore = all(LLDATestTopics, LLDATestTopic, LLDATestProb, maxEntTestTopics,
                                           maxEntTestTopic, maxEntTestProb, AlchemyTestTopics, AlchemyTestTopic,
                                           LLDAWeightTemp, maxEntWeightTemp, AlchemyWeightTemp)
                if predTopic in TrueLabelTestData[i]:
                    correct[3] += 1.0

                total += 1.0

            for l in range(4):
                accuracy[l] += correct[l] / total

        print learningRate
        print iterations
        for l in range(4):
            print l
            print accuracy[l] * 100 / fold
        print ''