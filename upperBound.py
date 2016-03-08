__author__ = 'renhao.cui'
import operator

fold = 5
brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']
limitSet = [0.0]

for brand in brandList:
    for limit in limitSet:
        accuracyList = [0.0, 0.0, 0.0, 0.0]
        for j in range(fold):
            # split the data
            LLDAData = {}
            maxEntData = {}
            trueLabelData = {}
            mappingData = {}

            LLDAoutputFile = open('LLDAoutput//' + brand + '.' + str(j)+','+str(limit), 'r')
            trueLabelFile = open('trueLabel//'+brand+'.'+str(j), 'r')
            maxEntFile = open('MaxEntoutput//' + brand + '.' + str(j)+','+str(limit), 'r')
            mappingFile = open('AlchemyOutput//' + brand + '.' + str(j), 'r')

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
                print str(len(trueLabelData))+' '+str(len(LLDAData))+' '+str(len(maxEntData))
                break

            correctList = [0.0, 0.0, 0.0, 0.0]
            totalList = [0.0, 0.0, 0.0, 0.0]
            for i in range(testSize):
                LLDATopics = LLDAData[i]
                maxEntTopics = maxEntData[i]
                mappingTopics = mappingData[i]
                predTopics = {}
                if len(LLDATopics) > 0:
                    (LLDATopic, LLDAProb) = max(LLDATopics.iteritems(), key=operator.itemgetter(1))
                (maxEntTopic, maxEntProb) = max(maxEntTopics.iteritems(), key=operator.itemgetter(1))
                (mappingTopic, mappingProb) = max(mappingTopics.iteritems(), key=operator.itemgetter(1))


                # LLDA + MaxEnt
                prediction = []
                if len(LLDATopics) > 0:
                    prediction = [LLDATopic, maxEntTopic]
                else:
                    prediction = [maxEntTopic]
                for trueLabel in trueLabelData[i]:
                    if trueLabel in prediction:
                        correctList[0] += 1.0
                        break
                totalList[0] += 1.0

                # LLDA + Mapping
                prediction = []
                if len(LLDATopics) > 0:
                    prediction = [LLDATopic, mappingTopic]
                else:
                    prediction = [mappingTopic]
                for trueLabel in trueLabelData[i]:
                    if trueLabel in prediction:
                        correctList[1] += 1.0
                        break
                totalList[1] += 1.0

                # MaxEnt + Mapping
                prediction = []
                prediction = [maxEntTopic, mappingTopic]
                for trueLabel in trueLabelData[i]:
                    if trueLabel in prediction:
                        correctList[2] += 1.0
                        break
                totalList[2] += 1.0

                # All
                prediction = []
                if len(LLDATopics) > 0:
                    prediction = [LLDATopic, mappingTopic, maxEntTopic]
                else:
                    prediction = [mappingTopic, maxEntTopic]
                for trueLabel in trueLabelData[i]:
                    if trueLabel in prediction:
                        correctList[3] += 1.0
                        break
                totalList[3] += 1.0

            for i in range(4):
                accuracyList[i] += (correctList[i] * 100)/totalList[i]

        print brand
        print limit
        for accuracy in accuracyList:
            print accuracy/fold