__author__ = 'renhao.cui'
import random
import operator

def normalization(scoreList):
    outputList = []
    total = sum(scoreList)
    for score in scoreList:
        outputList.append(score/total)
    return outputList


def getInitialList(num):
    if num == 2:
        dist = random.random(0.001, 0.9)
        return [dist, 1-dist]
    else:
        dist1 = random.random(0.001, 0.7)
        dist2 = random.random(0.001, 0.9 - dist1)
        return [dist1, dist2, 1-dist1-dist2]


def LLDAwithMaxEnt(LLDATopics, LLDATopic, LLDAProb, maxEntTopics, maxEntTopic, maxEntProb, AlchemyTopics, LLDAWeight, maxEntWeight):
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
                    predTopics[topic] += maxEntTopics[topic]*maxEntWeight
                if topic in LLDATopics:
                    predTopics[topic] += LLDATopics[topic]*LLDAWeight
            predTopic = max(predTopics.iteritems(), key=operator.itemgetter(1))[0]
            predScore = max(predTopics.iteritems(), key=operator.itemgetter(1))[1]
    return predTopic, predScore


def LLDAwithAlchemy(LLDATopics, LLDATopic, LLDAProb, AlchemyTopics, AlchemyTopic, LLDAWeight, AlchemyWeight):
    predTopics = {}
    if len(LLDATopics) == 0:
        predTopic = AlchemyTopic
        predScore = AlchemyTopics[predTopic]
    else:
        for (topic, prob) in LLDATopics.items():
            prob = prob * LLDAWeight
            if topic in AlchemyTopics:
                predTopics[topic] = prob + AlchemyTopics[topic]*AlchemyWeight
            else:
                predTopics[topic] = prob
        predTopic = max(predTopics.iteritems(), key=operator.itemgetter(1))[0]
        predScore = max(predTopics.iteritems(), key=operator.itemgetter(1))[1]
    return predTopic, predScore


def MaxEntwithAlchemy(maxEntTopics, maxEntTopic, maxEntProb, AlchemyTopics, AlchemyTopic, maxEntWeight, AlchemyWeight):
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
                predTopics[topic] += maxEntTopics[topic]*maxEntWeight
            if topic in AlchemyTopics:
                predTopics[topic] += AlchemyTopics[topic]*AlchemyWeight
        predTopic = max(predTopics.iteritems(), key=operator.itemgetter(1))[0]
        predScore = max(predTopics.iteritems(), key=operator.itemgetter(1))[1]
    return predTopic, predScore

def all(LLDATopics, LLDATopic, LLDAProb, maxEntTopics, maxEntTopic, maxEntProb, AlchemyTopics, AlchemyTopic, LLDAWeight, maxEntWeight, AlchemyWeight):
    if len(LLDATopics) == 0:
        return MaxEntwithAlchemy(maxEntTopics, maxEntTopic, maxEntProb, AlchemyTopics, AlchemyTopic, maxEntWeight, AlchemyWeight)
    elif len(maxEntTopics) == 0:
        return LLDAwithAlchemy(LLDATopics, LLDATopic, LLDAProb, AlchemyTopics, AlchemyTopic, LLDAWeight, AlchemyWeight)
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
                predTopics[topic] += LLDATopics[topic]  *LLDAWeight
            if topic in AlchemyTopics:
                predTopics[topic] += AlchemyTopics[topic]  *AlchemyWeight
            if topic in maxEntTopics:
                predTopics[topic] += maxEntTopics[topic]  *maxEntWeight
        predTopic = max(predTopics.iteritems(), key=operator.itemgetter(1))[0]
        predScore = max(predTopics.iteritems(), key=operator.itemgetter(1))[1]
    return predTopic, predScore




fold = 5
brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']
iterations = 30
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

            if len(TrueLabelTestData) == len(LLDATestData) and len(LLDATestData) == len(MaxEntTestData) and len(AlchemyTestData) == len(MaxEntTestData):
                testSize = len(TrueLabelTestData)
            else:
                print 'Test input file sizes do not match iter: ' + str(j)
                print str(len(TrueLabelTestData)) + ' ' + str(len(LLDATestData)) + ' ' + str(len(MaxEntTestData)) + ' ' + str(len(AlchemyTestData))
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

            if len(TrueLabelTrainData) == len(LLDATrainData) and len(LLDATrainData) == len(MaxEntTrainData) and len(MaxEntTrainData) == len(AlchemyTrainData):
                trainSize = len(TrueLabelTrainData)
            else:
                print 'Train input file sizes do not match iter: ' + str(j)
                print str(len(TrueLabelTrainData)) + ' ' + str(len(LLDATrainData)) + ' ' + str(len(MaxEntTrainData)) + ' ' + str(len(AlchemyTrainData))
                break

            # train voting weights
            LLDAWeight = []
            maxEntWeight = []
            AlchemyWeight = []
            LLDAWeightTotal = []
            maxEntWeightTotal = []
            AlchemyWeightTotal = []
            updateCount = []
            # 0-> LLDA+MaxEnt, 1-> LLDA+Alchemy, 2-> MaxEnt + Alchemy, 3-> All
            for l in range(4):
                LLDAWeight.append(1/2.0)
                maxEntWeight.append(1/2.0)
                AlchemyWeight.append(1/2.0)

                LLDAWeightTotal.append( 0.0)
                maxEntWeightTotal.append( 0.0)
                AlchemyWeightTotal.append( 0.0)
                updateCount.append(0.0)
            LLDAWeight[3] = 1/3.0
            maxEntWeight[3] = 1/3.0
            AlchemyWeight[3] = 1/3.0

            for iter in range(iterations):
                #print 'iteration: '+str(iter)
                #print str(LLDATrainWeight) + ' '+str(maxEntTrainWeight)
                for index in range(trainSize):
                    LLDATrainTopics = LLDATrainData[index]
                    maxEntTrainTopics = MaxEntTrainData[index]
                    AlchemyTrainTopics = AlchemyTrainData[index]
                    predTrainTopics = {}
                    if len(LLDATrainTopics) > 0:
                        (LLDATrainTopic, LLDATrainProb) = max(LLDATrainTopics.iteritems(), key=operator.itemgetter(1))
                    if len(maxEntTrainTopics) > 0:
                        (maxEntTrainTopic, maxEntTrainProb) = max(maxEntTrainTopics.iteritems(), key=operator.itemgetter(1))
                    (AlchemyTrainTopic, AlchemyTrainProb) = max(AlchemyTrainTopics.iteritems(), key=operator.itemgetter(1))

                    # LLDA + MaxEnt
                    predTopic, predScore = LLDAwithMaxEnt(LLDATrainTopics, LLDATrainTopic, LLDATrainProb, maxEntTrainTopics, maxEntTrainTopic, maxEntTrainProb, AlchemyTrainTopics, LLDAWeight[0], maxEntWeight[0])
                    if predTopic not in TrueLabelTrainData[index]:
                        if (LLDATrainTopic not in TrueLabelTrainData[index]) and (maxEntTrainTopic in TrueLabelTrainData[index]):
                            LLDAWeight[0] *= learningRate*predScore
                        elif (LLDATrainTopic in TrueLabelTrainData[index]) and (maxEntTrainTopic not in TrueLabelTrainData[index]):
                            maxEntWeight[0] *= learningRate*predScore

                        tempList = normalization([LLDAWeight[0], maxEntWeight[0]])
                        updateCount[0] += 1
                        LLDAWeight[0] = tempList[0]
                        maxEntWeight[0] = tempList[1]
                        LLDAWeightTotal[0] += LLDAWeight[0]
                        maxEntWeightTotal[0] += maxEntWeight[0]


                    # LLDA + Alchemy
                    predTopic, predScore = LLDAwithAlchemy(LLDATrainTopics, LLDATrainTopic, LLDATrainProb, AlchemyTrainTopics, AlchemyTrainTopic, LLDAWeight[1], AlchemyWeight[1])
                    if predTopic not in TrueLabelTrainData[index]:
                        if (LLDATrainTopic not in TrueLabelTrainData[index]) and (AlchemyTrainTopic in TrueLabelTrainData[index]):
                            LLDAWeight[1] *= learningRate*predScore
                        elif (LLDATrainTopic in TrueLabelTrainData[index]) and (AlchemyTrainTopic not in TrueLabelTrainData[index]):
                            AlchemyWeight[1] *= learningRate*predScore

                        tempList = normalization([LLDAWeight[1], AlchemyWeight[1]])
                        updateCount[1] += 1
                        LLDAWeight[1] = tempList[0]
                        AlchemyWeight[1] = tempList[1]
                        LLDAWeightTotal[1] += LLDAWeight[1]
                        AlchemyWeightTotal[1] += AlchemyWeight[1]


                    #MaxEnt + Alchemy
                    predTopic, predScore = MaxEntwithAlchemy(maxEntTrainTopics, maxEntTrainTopic, maxEntTrainProb, AlchemyTrainTopics, AlchemyTrainTopic, maxEntWeight[2], AlchemyWeight[2])
                    if predTopic not in TrueLabelTrainData[index]:
                        if (maxEntTrainTopic not in TrueLabelTrainData[index]) and (AlchemyTrainTopic in TrueLabelTrainData[index]):
                            maxEntWeight[2] *= learningRate*predScore
                        elif (maxEntTrainTopic in TrueLabelTrainData[index]) and (AlchemyTrainTopic not in TrueLabelTrainData[index]):
                            AlchemyWeight[2] *= learningRate*predScore

                        tempList = normalization([maxEntWeight[2], AlchemyWeight[2]])
                        maxEntWeight[2] = tempList[0]
                        AlchemyWeight[2] = tempList[1]
                        updateCount[2] += 1
                        maxEntWeightTotal[2] += maxEntWeight[2]
                        AlchemyWeightTotal[2] += AlchemyWeight[2]

                    # all
                    predTopic, predScore = all(LLDATrainTopics, LLDATrainTopic, LLDATrainProb, maxEntTrainTopics, maxEntTrainTopic, maxEntTrainProb, AlchemyTrainTopics, AlchemyTrainTopic, LLDAWeight[3], maxEntWeight[3], AlchemyWeight[3])
                    if predTopic not in TrueLabelTrainData[index]:
                        if LLDATrainTopic in TrueLabelTrainData[index] and maxEntTrainTopic in TrueLabelTrainData[index] and AlchemyTrainTopic not in TrueLabelTrainData[index]:
                            AlchemyWeight[3] *= learningRate*predScore
                        elif LLDATrainTopic in TrueLabelTrainData[index] and maxEntTrainTopic not in TrueLabelTrainData[index] and AlchemyTrainTopic in TrueLabelTrainData[index]:
                            maxEntWeight[3] *= learningRate*predScore
                        elif LLDATrainTopic in TrueLabelTrainData[index] and maxEntTrainTopic not in TrueLabelTrainData[index] and AlchemyTrainTopic not in TrueLabelTrainData[index]:
                            maxEntWeight[3] *= learningRate*predScore
                            AlchemyWeight[3] *= learningRate*predScore
                        elif LLDATrainTopic not in TrueLabelTrainData[index] and maxEntTrainTopic in TrueLabelTrainData[index] and AlchemyTrainTopic in TrueLabelTrainData[index]:
                            LLDAWeight[3] *= learningRate*predScore
                        elif LLDATrainTopic not in TrueLabelTrainData[index] and maxEntTrainTopic in TrueLabelTrainData[index] and AlchemyTrainTopic not in TrueLabelTrainData[index]:
                            LLDAWeight[3] *= learningRate*predScore
                            AlchemyWeight[3] *= learningRate*predScore
                        elif LLDATrainTopic not in TrueLabelTrainData[index] and maxEntTrainTopic not in TrueLabelTrainData[index] and AlchemyTrainTopic in TrueLabelTrainData[index]:
                            LLDAWeight[3] *= learningRate*predScore
                            maxEntWeight[3] *= learningRate*predScore

                        tempList = normalization([LLDAWeight[3], maxEntWeight[3], AlchemyWeight[3]])

                        LLDAWeight[3] = tempList[0]
                        maxEntWeight[3] = tempList[1]
                        AlchemyWeight[3] = tempList[2]
                        updateCount[3] += 1
                        LLDAWeightTotal[3] += LLDAWeight[3]
                        maxEntWeightTotal[3] += maxEntWeight[3]
                        AlchemyWeightTotal[3] += AlchemyWeight[3]


            # test
            #print 'Resulting weights: '+ str(LLDAWeight)+' ' + str(maxEntWeight) + ' ' +str(AlchemyWeight)
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
                predTopic, predScore = LLDAwithMaxEnt(LLDATestTopics, LLDATestTopic, LLDATestProb, maxEntTestTopics, maxEntTestTopic, maxEntTestProb, AlchemyTestTopics, LLDAWeightTotal[0]/updateCount[0], maxEntWeightTotal[0]/updateCount[0])
                if predTopic in TrueLabelTestData[i]:
                    correct[0] += 1.0

                # LLDA + Alchemy
                predTopic, predScore = LLDAwithAlchemy(LLDATestTopics, LLDATestTopic, LLDATestProb, AlchemyTestTopics, AlchemyTestTopic, LLDAWeightTotal[1]/updateCount[1], AlchemyWeightTotal[1]/updateCount[1])
                if predTopic in TrueLabelTestData[i]:
                    correct[1] += 1.0

                # MaxEnt + Alchemy
                predTopic, predScore = MaxEntwithAlchemy(maxEntTestTopics, maxEntTestTopic, maxEntTestProb, AlchemyTestTopics, AlchemyTestTopic, maxEntWeightTotal[2]/updateCount[2], AlchemyWeightTotal[2]/updateCount[2])
                if predTopic in TrueLabelTestData[i]:
                    correct[2] += 1.0

                # all
                predTopic, predScore = all(LLDATestTopics, LLDATestTopic, LLDATestProb, maxEntTestTopics, maxEntTestTopic, maxEntTestProb, AlchemyTestTopics, AlchemyTestTopic, LLDAWeightTotal[3]/updateCount[3], maxEntWeightTotal[3]/updateCount[3], AlchemyWeightTotal[3]/updateCount[3])
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