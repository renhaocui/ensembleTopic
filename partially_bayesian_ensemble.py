import random

__author__ = 'renhao.cui'
import operator

def normalization(scoreList):
    outputList = []
    total = sum(scoreList)
    for score in scoreList:
        outputList.append(score/total)

    return outputList


fold = 5
brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']
perfList = {'Elmers': {'LLDA': 0.89043, 'MaxEnt': 0.95257, 'Mapping': 0.82081},
            'Chilis': {'LLDA': 0.87825, 'MaxEnt': 0.94148, 'Mapping': 0.68560},
            'BathAndBodyWorks': {'LLDA': 0.66882, 'MaxEnt': 0.89837, 'Mapping': 0.55506},
            'Dominos': {'LLDA': 0.83622, 'MaxEnt': 0.90952, 'Mapping': 0.54575},
            'Triclosan': {'LLDA': 0.68289, 'MaxEnt': 0.70626, 'Mapping': 0.48811}}
#modelList = {'LLDA': 0.6, 'MaxEnt': 0.3, 'Mapping': 0.1}
#priorityLimitSet = [2.0]
priorPower = [0, 1, 3, 7, 9]

for brand in brandList:
    #print brand
    limit = 2.0
    output = []
    for power in priorPower:
        accuracy = 0.0
        for j in range(fold):
            # split the data
            LLDAData = {}
            maxEntData = {}
            trueLabelData = {}
            mappingData = {}

            LLDAoutputFile = open('HybridData//LLDATest//' + brand + '.' + str(j) + ',0.0', 'r')
            trueLabelFile = open('HybridData//trueLabelTest//' + brand + '.' + str(j), 'r')
            maxEntFile = open('HybridData//MaxEntTest//' + brand + '.' + str(j) + ',0.0', 'r')
            mappingFile = open('HybridData//AlchemyTest//' + brand + '.' + str(j), 'r')

            index = 0
            for line in LLDAoutputFile:
                temp = {}
                if len(line.strip()) > 0:
                    items = line.strip().split('\t')
                    for item in items:
                        seg = item.split(':')
                        temp[seg[0]] = float(seg[1])
                LLDAData[index] = temp
                index += 1
            LLDAoutputFile.close()

            index = 0
            for line in maxEntFile:
                temp = {}
                if len(line.strip()) > 0:
                    items = line.strip().split('\t')
                    for item in items:
                        seg = item.split(':')
                        temp[seg[0]] = float(seg[1])
                maxEntData[index] = temp
                index += 1
            maxEntFile.close()

            index = 0
            for line in mappingFile:
                temp = {}
                if len(line.strip()) > 0:
                    items = line.strip().split('\t')
                    for item in items:
                        seg = item.split(':')
                        temp[seg[0]] = float(seg[1])
                mappingData[index] = temp
                index += 1
            mappingFile.close()

            index = 0
            for line in trueLabelFile:
                labelList = line.strip().split(' ')
                trueLabelData[index] = labelList
                index += 1
            trueLabelFile.close()

            if len(trueLabelData) == len(LLDAData) and len(LLDAData) == len(maxEntData):
                testSize = len(trueLabelData)
            else:
                print 'input file sizes do not match iter: ' + str(j)
                print str(len(trueLabelData)) + ' ' + str(len(LLDAData)) + ' ' + str(len(maxEntData))
                break

            correct = 0.0
            total = 0.0
            for i in range(testSize):
                LLDATopics = LLDAData[i]
                maxEntTopics = maxEntData[i]
                mappingTopics = mappingData[i]
                predTopics = {}
                if len(LLDATopics) > 0:
                    (LLDATopic, LLDAProb) = max(LLDATopics.iteritems(), key=operator.itemgetter(1))
                if len(maxEntTopics) > 0:
                    (maxEntTopic, maxEntProb) = max(maxEntTopics.iteritems(), key=operator.itemgetter(1))
                (mappingTopic, mappingProb) = max(mappingTopics.iteritems(), key=operator.itemgetter(1))

                # LLDA + MaxEnt
                '''
                if len(LLDATopics) == 0:
                    if len(maxEntTopics) == 0:
                        predTopic = random.choice(mappingTopics.keys())
                    else:
                        predTopic = maxEntTopic
                else:
                    if len(maxEntTopics) == 0:
                        predTopic = LLDATopic
                    elif maxEntProb > limit:
                        predTopic = maxEntTopic
                    elif LLDAProb > limit:
                        predTopic = LLDATopic
                    else:
                        topicList = []
                        for topic in maxEntTopics:
                            topicList.append(topic)
                        for topic in LLDATopics:
                            topicList.append(topic)
                        uniqueTopics = list(set(topicList))
                        inputList = [perfList[brand]['MaxEnt'], perfList[brand]['LLDA']]
                        priorList = inputList
                        for topic in uniqueTopics:
                            predTopics[topic] = 0.0
                            if topic in maxEntTopics:
                                predTopics[topic] += maxEntTopics[topic]*priorList[0]**power
                            if topic in LLDATopics:
                                predTopics[topic] += LLDATopics[topic]*priorList[1]**power
                        predTopic = max(predTopics.iteritems(), key=operator.itemgetter(1))[0]
                '''
                # LLDA + Alchemy
                '''
                if len(LLDATopics) == 0:
                    predTopic = mappingTopic
                elif LLDAProb > limit:
                    predTopic = LLDATopic
                else:
                    inputList = [perfList[brand]['Mapping'], perfList[brand]['LLDA']]
                    priorList = inputList
                    for (topic, prob) in LLDATopics.items():
                        prob *= priorList[1] ** power
                        if topic in mappingTopics:
                            predTopics[topic] = prob + mappingTopics[topic]*priorList[0]**power
                        else:
                            predTopics[topic] = prob
                    predTopic = max(predTopics.iteritems(), key=operator.itemgetter(1))[0]
                '''
                # MaxEnt + Alchemy

                if len(maxEntTopics) == 0:
                    predTopic = mappingTopic
                elif maxEntProb > limit:
                    predTopic = maxEntTopic
                else:
                    topicList = []
                    for topic in maxEntTopics:
                        topicList.append(topic)
                    for topic in mappingTopics:
                        topicList.append(topic)
                    uniqueTopics = list(set(topicList))
                    inputList = [perfList[brand]['MaxEnt'], perfList[brand]['Mapping']]
                    priorList = inputList
                    for topic in uniqueTopics:
                        predTopics[topic] = 0.0
                        if topic in maxEntTopics:
                            predTopics[topic] += maxEntTopics[topic]*priorList[0]**power
                        if topic in mappingTopics:
                            predTopics[topic] += mappingTopics[topic]*priorList[1]**power
                    predTopic = max(predTopics.iteritems(), key=operator.itemgetter(1))[0]

                # all
                '''
                if LLDATopic == maxEntTopic:
                    predTopic = LLDATopic
                elif LLDATopic == mappingTopic:
                    predTopic = LLDATopic
                elif maxEntTopic == mappingTopic:
                    predTopic = mappingTopic

                elif len(LLDATopics) == 0:
                    if len(maxEntTopics) == 0:
                        predTopic = mappingTopic
                    else:
                        if maxEntProb > limit:
                            predTopic = maxEntTopic
                        else:
                            topicList = []
                            for topic in maxEntTopics:
                                topicList.append(topic)
                            for topic in mappingTopics:
                                topicList.append(topic)
                            uniqueTopics = list(set(topicList))
                            inputList = [perfList[brand]['MaxEnt'], perfList[brand]['Mapping']]
                            priorList = inputList
                            for topic in uniqueTopics:
                                predTopics[topic] = 0.0
                                if topic in maxEntTopics:
                                    predTopics[topic] += maxEntTopics[topic] * priorList[0]**power
                                if topic in mappingTopics:
                                    predTopics[topic] += mappingTopics[topic]* priorList[1]**power
                            predTopic = max(predTopics.iteritems(), key=operator.itemgetter(1))[0]
                elif len(maxEntTopics) == 0:
                    if LLDAProb > limit:
                        predTopic = LLDATopic
                    else:
                        topicList = []
                        for topic in LLDATopics.keys():
                            topicList.append(topic)
                        for topic in mappingTopics.keys():
                            topicList.append(topic)
                        uniqueTopics = list(set(topicList))
                        inputList = [perfList[brand]['Mapping'], perfList[brand]['LLDA']]
                        priorList = inputList
                        for topic in uniqueTopics:
                            predTopics[topic] = 0.0
                            if topic in LLDATopics:
                                predTopics[topic] += LLDATopics[topic] * priorList[1] ** power
                            if topic in mappingTopics:
                                predTopics[topic] += mappingTopics[topic] * priorList[0] ** power
                        predTopic = max(predTopics.iteritems(), key=operator.itemgetter(1))[0]
                elif maxEntProb > limit:
                    predTopic = maxEntTopic
                else:
                    if LLDAProb > limit:
                        predTopic = LLDATopic
                    else:
                        topicList = []
                        for topic in LLDATopics.keys():
                            topicList.append(topic)
                        for topic in mappingTopics.keys():
                            topicList.append(topic)
                        for topic in maxEntTopics.keys():
                            topicList.append(topic)
                        uniqueTopics = list(set(topicList))
                        inputList = [perfList[brand]['MaxEnt'], perfList[brand]['LLDA'], perfList[brand]['Mapping']]
                        priorList = inputList
                        for topic in uniqueTopics:
                            predTopics[topic] = 0.0
                            if topic in LLDATopics:
                                predTopics[topic] += LLDATopics[topic] * priorList[1] ** power
                            if topic in mappingTopics:
                                predTopics[topic] += mappingTopics[topic] * priorList[2] ** power
                            if topic in maxEntTopics:
                                predTopics[topic] += maxEntTopics[topic] * priorList[0] ** power
                        predTopic = max(predTopics.iteritems(), key=operator.itemgetter(1))[0]
                    '''

                if predTopic in trueLabelData[i]:
                    correct += 1.0
                total += 1.0

            accuracy += correct / total

        # print brand
        #print limit
        output.append(round(accuracy * 100 / fold,3))
        #print accuracy * 100 / fold
    out = brand+'&'
    for item in output:
        out += str(item)+'&'
    print out[:-1]