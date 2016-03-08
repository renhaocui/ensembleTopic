__author__ = 'renhao.cui'
import operator
from sklearn import svm

fold = 5
brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']

for brand in brandList:
    print brand
    accuracy = [0.0, 0.0, 0.0, 0.0]
    for j in range(fold):
        # split the data
        LLDAData = {}
        maxEntData = {}
        trueLabelData = {}
        mappingData = {}

        LLDAoutputFile = open('LLDAoutput//' + brand + '.' + str(j)+',0.0', 'r')
        trueLabelFile = open('trueLabel//'+brand+'.'+str(j), 'r')
        maxEntFile = open('MaxEntoutput//' + brand + '.' + str(j)+',0.0', 'r')
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

        '''
        LLDATrainData = []
        maxEntTrainData = []
        mappingTrainData = []
        trueLabelTrainData = []

        for h in range(5):
            if h != j:
                LLDAoutputFile = open('LLDAoutput//' + brand + '.' + str(h)+',0.0', 'r')
                trueLabelFile = open('trueLabel//'+brand+'.'+str(h), 'r')
                maxEntFile = open('MaxEntoutput//' + brand + '.' + str(h)+',0.0', 'r')
                mappingFile = open('AlchemyOutput//' + brand + '.' + str(h), 'r')

                for line in LLDAoutputFile:
                    temp = {}
                    if len(line.strip()) > 0:
                        items = line.strip().split('\t')
                        for item in items:
                            seg = item.split(':')
                            temp[seg[0]] = float(seg[1])
                    LLDATrainData.append(temp)
                LLDAoutputFile.close()

                for line in maxEntFile:
                    temp = {}
                    if len(line.strip()) > 0:
                        items = line.strip().split('\t')
                        for item in items:
                            seg = item.split(':')
                            temp[seg[0]] = float(seg[1])
                    maxEntTrainData.append(temp)
                maxEntFile.close()

                for line in mappingFile:
                    temp = {}
                    if len(line.strip()) > 0:
                        items = line.strip().split('\t')
                        for item in items:
                            seg = item.split(':')
                            temp[seg[0]] = float(seg[1])
                    mappingTrainData.append(temp)
                mappingFile.close()

                for line in trueLabelFile:
                    labelList = line.strip().split(' ')
                    trueLabelTrainData.append(labelList)
                trueLabelFile.close()

        featureSet1 = [] # LLDA + Mapping
        featureSet2 = [] # LLDA + MaxEnt
        featureSet3 = [] # MaxEnt + Mapping
        featureSet4 = [] # All
        labelSet1 = []
        labelSet2 = []
        labelSet3 = []
        labelSet4 = []
        for s in range(len(trueLabelTrainData)):
            if len(LLDATrainData[s]) > 0 and len(maxEntTrainData[s]) > 0:
                (LLDATrainTopic, LLDATrainProb) = max(LLDATrainData[s].iteritems(), key=operator.itemgetter(1))
                (mappingTrainTopic, mappingTrainProb) = max(mappingTrainData[s].iteritems(), key=operator.itemgetter(1))
                (maxEntTrainTopic, maxEntTrainProb) = max(maxEntTrainData[s].iteritems(), key=operator.itemgetter(1))
                for trueLabel in trueLabelTrainData[s]:
                    if trueLabel == LLDATrainTopic and trueLabel != mappingTrainTopic:
                        labelSet1.append(0)
                        featureSet1.append([LLDATrainProb, mappingTrainProb])
                    elif trueLabel != LLDATrainTopic and trueLabel == mappingTrainTopic:
                        labelSet1.append(1)
                        featureSet1.append([LLDATrainProb, mappingTrainProb])

                    if trueLabel == LLDATrainTopic and trueLabel != maxEntTrainTopic:
                        labelSet2.append(0)
                        featureSet2.append([LLDATrainProb, maxEntTrainProb])
                    elif trueLabel != LLDATrainTopic and trueLabel == maxEntTrainTopic:
                        labelSet2.append(1)
                        featureSet2.append([LLDATrainProb, maxEntTrainProb])

                    if trueLabel == maxEntTrainTopic and trueLabel != mappingTrainTopic:
                        labelSet3.append(0)
                        featureSet3.append([maxEntTrainProb, mappingTrainProb])
                    elif trueLabel != maxEntTrainTopic and trueLabel == mappingTrainTopic:
                        labelSet3.append(1)
                        featureSet3.append([maxEntTrainProb, mappingTrainProb])

                    if trueLabel == LLDATrainTopic and trueLabel != maxEntTrainTopic and trueLabel != mappingTrainTopic:
                        labelSet4.append(0)
                        featureSet4.append([LLDATrainProb, maxEntTrainProb, mappingTrainProb])
                    if trueLabel != LLDATrainTopic and trueLabel == maxEntTrainTopic and trueLabel != mappingTrainTopic:
                        labelSet4.append(1)
                        featureSet4.append([LLDATrainProb, maxEntTrainProb, mappingTrainProb])
                    if trueLabel != LLDATrainTopic and trueLabel != maxEntTrainTopic and trueLabel == mappingTrainTopic:
                        labelSet4.append(2)
                        featureSet4.append([LLDATrainProb, maxEntTrainProb, mappingTrainProb])


        svmModel1 = svm.SVC()
        svmModel2 = svm.SVC()
        svmModel3 = svm.SVC()
        svmModel4 = svm.SVC()
        svmModel1.fit(featureSet1, labelSet1)
        svmModel2.fit(featureSet2, labelSet2)
        svmModel3.fit(featureSet3, labelSet3)
        svmModel4.fit(featureSet4, labelSet4)
        '''
        correct = [0.0, 0.0, 0.0, 0.0]
        total = 0.0
        for i in range(testSize):
            LLDATopics = LLDAData[i]
            maxEntTopics = maxEntData[i]
            mappingTopics = mappingData[i]

            if len(LLDATopics) > 0:
                (LLDATopic, LLDAProb) = max(LLDATopics.iteritems(), key=operator.itemgetter(1))
            if len(maxEntTopics) > 0:
                (maxEntTopic, maxEntProb) = max(maxEntTopics.iteritems(), key=operator.itemgetter(1))
            (mappingTopic, mappingProb) = max(mappingTopics.iteritems(), key=operator.itemgetter(1))


            # more powerful system

            # LLDA + Alchemy
            if len(LLDATopics) == 0:
                predTopic = mappingTopic
            elif len(mappingTopics) == 0:
                predTopic = LLDATopic
            elif mappingTopic == LLDATopic:
                predTopic = mappingTopic
            else:
                predTopic = LLDATopic
            if predTopic in trueLabelData[i]:
                correct[0] += 1.0
            # LLDA + MaxEnt
            if len(LLDATopics) == 0:
                predTopic = maxEntTopic
            elif len(maxEntTopics) == 0:
                predTopic = LLDATopic
            elif maxEntTopic == LLDATopic:
                predTopic = maxEntTopic
            else:
                predTopic = maxEntTopic
            if predTopic in trueLabelData[i]:
                correct[1] += 1.0
            # MaxEnt + Alchemy
            if len(maxEntTopics) == 0:
                predTopic = mappingTopic
            elif len(mappingTopics) == 0:
                predTopic = maxEntTopic
            elif maxEntTopic == mappingTopic:
                predTopic = maxEntTopic
            else:
                predTopic = maxEntTopic
            if predTopic in trueLabelData[i]:
                correct[2] += 1.0
            # All
            if len(LLDATopics) == 0:
                if len(maxEntTopics) == 0:
                    predTopic = mappingTopic
                elif len(mappingTopics) == 0:
                    predTopic = maxEntTopic
                elif maxEntTopic == mappingTopic:
                    predTopic = maxEntTopic
                else:
                    predTopic = maxEntTopic
            elif len(maxEntTopics) == 0:
                if len(LLDATopics) == 0:
                    predTopic = mappingTopic
                elif len(mappingTopics) == 0:
                    predTopic = LLDATopic
                elif mappingTopic == LLDATopic:
                    predTopic = mappingTopic
                else:
                    predTopic = LLDATopic
            elif len(mappingTopics) == 0:
                if len(LLDATopics) == 0:
                    predTopic = maxEntTopic
                elif len(maxEntTopics) == 0:
                    predTopic = LLDATopic
                elif maxEntTopic == LLDATopic:
                    predTopic = maxEntTopic
                else:
                    predTopic = maxEntTopic
            elif mappingTopic == LLDATopic and LLDATopic == maxEntTopic:
                predTopic = LLDATopic
            else:
                predTopic = maxEntTopic
            if predTopic in trueLabelData[i]:
                correct[3] += 1.0
            if maxEntTopic not in trueLabelData[i] and LLDATopic not in trueLabelData[i] and mappingTopic not in trueLabelData[i]:
                print str(j) + ' '+str(i)
            total += 1.0


            # higher probability
            '''
            # LLDA + Alchemy
            if len(LLDATopics) == 0:
                predTopic = mappingTopic
            elif len(mappingTopics) == 0:
                predTopic = LLDATopic
            elif mappingTopic == LLDATopic:
                predTopic = mappingTopic
            elif mappingProb > LLDAProb:
                predTopic = mappingTopic
            else:
                predTopic = LLDATopic
            if predTopic in trueLabelData[i]:
                correct[0] += 1.0
            # LLDA + MaxEnt
            if len(LLDATopics) == 0:
                predTopic = maxEntTopic
            elif len(maxEntTopics) == 0:
                predTopic = LLDATopic
            elif maxEntTopic == LLDATopic:
                predTopic = maxEntTopic
            elif LLDAProb > maxEntProb:
                predTopic = LLDATopic
            else:
                predTopic = maxEntTopic
            if predTopic in trueLabelData[i]:
                correct[1] += 1.0
            # MaxEnt + Alchemy
            if len(maxEntTopics) == 0:
                predTopic = mappingTopic
            elif len(mappingTopics) == 0:
                predTopic = maxEntTopic
            elif maxEntTopic == mappingTopic:
                predTopic = maxEntTopic
            elif mappingProb > maxEntProb:
                predTopic = mappingTopic
            else:
                predTopic = maxEntTopic
            if predTopic in trueLabelData[i]:
                correct[2] += 1.0
            # All
            if len(LLDATopics) == 0:
                if len(maxEntTopics) == 0:
                    predTopic = mappingTopic
                elif len(mappingTopics) == 0:
                    predTopic = maxEntTopic
                elif maxEntTopic == mappingTopic:
                    predTopic = maxEntTopic
                elif mappingProb > maxEntProb:
                    predTopic = mappingTopic
                else:
                    predTopic = maxEntTopic
            elif len(maxEntTopics) == 0:
                if len(LLDATopics) == 0:
                    predTopic = mappingTopic
                elif len(mappingTopics) == 0:
                    predTopic = LLDATopic
                elif mappingTopic == LLDATopic:
                    predTopic = mappingTopic
                elif mappingProb > LLDAProb:
                    predTopic = mappingTopic
                else:
                    predTopic = LLDATopic
            elif len(mappingTopics) == 0:
                if len(LLDATopics) == 0:
                    predTopic = maxEntTopic
                elif len(maxEntTopics) == 0:
                    predTopic = LLDATopic
                elif maxEntTopic == LLDATopic:
                    predTopic = maxEntTopic
                elif LLDAProb > maxEntProb:
                    predTopic = LLDATopic
                else:
                    predTopic = maxEntTopic
            elif mappingTopic == LLDATopic and LLDATopic == maxEntTopic:
                predTopic = LLDATopic
            elif mappingProb > maxEntProb and mappingProb > LLDAProb:
                predTopic = mappingTopic
            elif maxEntProb > mappingProb and maxEntProb > LLDAProb:
                predTopic = maxEntTopic
            else:
                predTopic = LLDATopic
            if predTopic in trueLabelData[i]:
                correct[3] += 1.0

            total += 1.0
            '''

            # machine learning
            '''
            # 1. LLDA + Mapping
            if len(LLDATopics) == 0:
                predTopic = mappingTopic
            elif LLDATopic == mappingTopic:
                predTopic = mappingTopic
            else:
                testFeatureSet = [LLDAProb, mappingProb]
                classNo = svmModel1.predict(testFeatureSet)[0]
                if classNo == 0:
                    predTopic = LLDATopic
                else:
                    predTopic = mappingTopic
            if predTopic in trueLabelData[i]:
                correct[0] += 1.0


            # 2. LLDA + MaxEnt
            if len(LLDATopics) == 0:
                predTopic = maxEntTopic
            elif len(maxEntTopics) == 0:
                predTopic = LLDATopic
            elif maxEntTopic == LLDATopic:
                predTopic = maxEntTopic
            else:
                testFeatureSet = [LLDAProb, maxEntProb]
                clsssNo = svmModel2.predict(testFeatureSet)[0]
                if classNo == 0:
                    predTopic = LLDATopic
                else:
                    predTopic = maxEntTopic

            if predTopic in trueLabelData[i]:
                correct[1] += 1.0

            # 3. MaxEnt + Mapping
            if len(maxEntTopics) == 0:
                predTopic = mappingTopic
            elif maxEntTopic == mappingTopic:
                predTopic = mappingTopic
            else:
                testFeatureSet = [maxEntProb, mappingProb]
                classNo = svmModel3.predict(testFeatureSet)[0]
                if classNo == 0:
                    predTopic = maxEntTopic
                else:
                    predTopic = mappingTopic

            if predTopic in trueLabelData[i]:
                correct[2] += 1.0

            # 4. All
            if len(LLDATopics) == 0:
                if len(maxEntTopics) == 0:
                    predTopic = mappingTopic
                elif maxEntTopic == mappingTopic:
                    predTopic = mappingTopic
                else:
                    testFeatureSet = [maxEntProb, mappingProb]
                    classNo = svmModel3.predict(testFeatureSet)[0]
                    if classNo == 0:
                        predTopic = maxEntTopic
                    else:
                        predTopic = mappingTopic
            elif len(maxEntTopics) == 0:
                if len(LLDATopics) == 0:
                    predTopic = mappingTopic
                elif LLDATopic == mappingTopic:
                    predTopic = mappingTopic
                else:
                    testFeatureSet = [LLDAProb, mappingProb]
                    classNo = svmModel1.predict(testFeatureSet)[0]
                    if classNo == 0:
                        predTopic = LLDATopic
                    else:
                        predTopic = mappingTopic
            elif mappingTopic == LLDATopic and LLDATopic == maxEntTopic:
                predTopic = mappingTopic
            else:
                testFeatureSet = [LLDAProb, maxEntProb, mappingProb]
                classNo = svmModel4.predict(testFeatureSet)
                if classNo == 0:
                    predTopic = LLDATopic
                elif classNo == 1:
                    predTopic = maxEntTopic
                else:
                    predTopic = mappingTopic

            if predTopic in trueLabelData[i]:
                correct[3] += 1.0

            total += 1.0
            '''

        for i in range(4):
            accuracy[i] += correct[i]/total

    for i in range(4):
        print accuracy[i] * 100 / fold