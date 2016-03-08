import utilities

__author__ = 'renhao.cui'

brand = 'BathAndBodyWorks'

keywordCommonFile = open('semanticMapping\\' + brand + '.keyword', 'r')
alchemyCommonFile = open('semanticMapping\\' + brand + '.alchemy', 'r')
ruleFile = open('topicRule\\'+brand+'.rule', 'r')
# calaisCommonFile = open('topicData\\' + brand + '.openCalais', 'r')
# indexCommonFile = open('topicData\\'+brand+'.index', 'r')

keyword = []
alchemy = []
ruleList = {}
# calais = []
# calaisCorpus = []

# read in data
for line in keywordCommonFile:
    words = line.strip().split(' ')
    keyword.append(words)

for line in alchemyCommonFile:
    words = line.strip().split(' ')
    tempList = {}
    for word in words:
        tempWord = word.split(':')[0]
        tempList[tempWord] = float(word.split(':')[1])
        if tempWord not in alchemyCorpus:
            alchemyCorpus.append(tempWord)
    alchemy.append(tempList)

for line in ruleFile:
    seg = line.strip().split(': ')
    topic = seg[0]
    seeds = seg[1].split('/')
    ruleList[topic] = seeds
ruleFile.close()


'''
for line in calaisCommonFile:
    words = line.strip().split(' ')
    calais.append(words)
    for word in words:
        if word not in calaisCorpus:
            calaisCorpus.append(word)
'''
print 'alchemy corpus size: ' + str(len(alchemyCorpus))
print 'data size: ' + str(len(keyword))
# print len(calaisCorpus)

fold = 5

limitList = [0.05]
for limit in limitList:
    total1 = 0.0
    total2 = 0.0
    total3 = 0.0
    total4 = 0.0
    total5 = 0.0
    fullCoverageTotal = 0.0
    coverageTotal = 0.0
    rulesTotal = 0.0
    baseTotal = 0.0
    for iteration in range(fold):
        #print '\niteration: ' + str(iteration)
        alchemyTrain = []
        alchemyTest = []
        keywordTrain = []
        keywordTest = []
        calaisTrain = []
        calaisTest = []

        # devide training and test data
        for se in range(len(keyword)):
            if se % fold == iteration:
                keywordTest.append(keyword[se])
                alchemyTest.append(alchemy[se])
                #calaisTest.append(calais[se])
            else:
                keywordTrain.append(keyword[se])
                alchemyTrain.append(alchemy[se])
                #calaisTrain.append(calais[se])

        alchemyCorpus = []
        keywordCorpus = []

        for topics in keywordTrain:
            for topic in topics:
                if topic not in keywordCorpus:
                    keywordCorpus.append(topic)

        for topics in alchemyTrain:
            for topic in topics:
                if topic not in alchemyCorpus:
                    alchemyCorpus.append(topic)

        #project alchemy -> keyword
        (alchemyFreq, alchemyCount, alchemyTotalCount) = utilities.genFreq(alchemyCorpus, alchemyTrain)
        (keywordFreq, keywordCount, keywordTotalCount) = utilities.genFreq(keywordCorpus, keywordTrain)
        (confScore, model, cand) = utilities.generateModel(alchemyCorpus, keywordCorpus, alchemyTrain, keywordTrain)
        majorModel = utilities.baseModel(cand, alchemyCorpus)
        outputModel = utilities.filterModel(confScore, limit)

        #print '# of mapping from Alchemy: ' + str(len(model))
        #print '# of total rules: ' + str(len(confScore))
        rulesTotal += len(outputModel.items())
        #print 'alchemy total frequency count: '+str(alchemyTotalCount)
        #print 'keyword total frequency count: '+str(keywordTotalCount)
        '''
    for (key, value) in outputModel.items():
        print key + ': ' + str(alchemyCount[key])
        print value + ': ' + str(keywordCount[value])
        print 'score: ' + str(confScore[key + ' ~ ' + value])
    '''
        ##evaluation results
        testNum = 1
        (tempTotal, correctCount, coverage) = utilities.evaluateModel1(model, cand, alchemyTest, keywordTest, testNum)
        total1 += tempTotal
        fullCoverageTotal += coverage
        (tempTotal, correctCount, coverage) = utilities.evaluateModel1(majorModel, cand, alchemyTest, keywordTest,
                                                                       testNum)
        baseTotal += tempTotal
        (tempTotal, correctCount, coverage) = utilities.evaluateModel1(outputModel, cand, alchemyTest, keywordTest,
                                                                       testNum)
        total2 += tempTotal
        coverageTotal += coverage
        (tempTotal, outputCount, useCount) = utilities.evaluateModel2(outputModel, alchemyTest, keywordTest, testNum)
        total3 += tempTotal
        total4 += utilities.evaluateModel3(model, alchemyTest, keywordTest, 3)
        total5 += utilities.evaluateModel4(model, alchemyTest, keywordTest, ruleList, 3)
        #print outputCount
        #print useCount
        '''
    ##project openCalais -> keyword
    (calaisFreq, calaisCount, totalCount) = utilities.genFreq(calaisCorpus, calaisTrain)
    (keywordFreq, keywordCount, keywordTotalCount) = utilities.genFreq(keywordCorpus, keywordTrain)
    (confScore, model, cand) = utilities.generateModel(calaisCorpus, keywordCorpus, calaisTrain, keywordTrain)
    majorModel = utilities.baseModel(cand, calaisCorpus)
    outputModel = utilities.filterModel(confScore, limit)
    outputFile1 = open('1.txt', 'w')
    outputFile2 = open('2.txt', 'w')
    for (key, value) in model.items():
        outputFile1.write(key + ': ' + str(value) + '\n')
    for (key, value) in outputModel.items():
        outputFile2.write(key + ': ' + str(value) + '\n')
    print '# of mapping from openCalais: ' + str(len(model))
    print '# of total rules: ' + str(len(confScore))
    rulesTotal += len(outputModel.items())
    print 'openCalais total frequency count: '+str(totalCount)
    print 'keyword total frequency count: '+str(keywordTotalCount)

    for (key, value) in outputModel.items():
        print key + ': ' + str(calaisCount[key])
        print value + ': ' + str(keywordCount[value])
        print 'score: ' + str(confScore[key + ' ~ ' + value])

    ##evaluation results
    (tempTotal, correctCount, coverage) = utilities.evaluateModel(model, cand, calaisTest, keywordTest)
    total1 += tempTotal
    fullCoverageTotal += coverage
    (tempTotal, correctCount, coverage) = utilities.evaluateModel(majorModel, cand, calaisTest, keywordTest)
    baseTotal += tempTotal
    (tempTotal, correctCount, coverage) = utilities.evaluateModel(outputModel, cand, calaisTest, keywordTest)
    total2 += tempTotal
    coverageTotal += coverage
    (tempTotal, outputCount, useCount) = utilities.evaluateModel2(outputModel, calaisTest, keywordTest)
    total3 += tempTotal
    print outputCount
    print useCount
    '''
        '''
    #calais -> alchemy
    (confScore, model, cand) = utilities.generateModel(calaisCorpus, alchemyCorpus, calaisTrain, alchemyTrain)
    otherTotal += utilities.evaluateModel(model, calaisTest, alchemyTest)
    '''
    print '\nlimit: ' + str(limit)
    #print 'Non-filtered model: ' + str(total1 / fold)
    print 'Filtered model: ' + str(total2 / fold)
    print 'Filtered model without unseen cases: ' + str(total3 / fold)
    #print 'All rules coverage: ' + str(fullCoverageTotal / fold)
    print 'Filtered rules coverage: ' + str(coverageTotal / fold)
    print 'Rules over limit ' + str(limit) + ': ' + str(rulesTotal / fold)
    print 'Majority classifier: ' + str(baseTotal / fold)
    print 'Combined Priority: '+str(total4/fold)
    print 'Sementic Priority: '+str(total5/fold)
    #print 'Calais: '+str(calaisTotal/fold)
    #print 'Other: '+str(otherTotal/fold)
