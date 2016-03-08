__author__ = 'renhao.cui'
import crossRef as cr
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

brand = 'Elmers'

ruleFile = open('topicRule\\'+brand+'.rule', 'r')
alchemyFile = open('semanticMapping\\'+brand+'.alchemy', 'r')
keywordFile = open('semanticMapping\\'+brand+'.keyword', 'r')
outputFile = open('semanticMapping\\'+brand+'.semantic', 'w')

ruleList = {}
topicList = []
alchemyList = []
alchemyCorpus = {}
keywordList = []
keywordCorpus = {}

for line in ruleFile:
    seg = line.strip().split(': ')
    topic = seg[0]
    topicList.append(topic)
    words = seg[1].split('/')
    for word in words:
        ruleList[word] = topic

ruleFile.close()

for line in keywordFile:
    words = line.strip().split(' ')
    keywordList.append(words)
    for word in words:
        if word not in keywordCorpus.keys():
            keywordCorpus[word] = 1
        else:
            keywordCorpus[word] += 1
keywordFile.close()

for line in alchemyFile:
    words = line.strip().split(' ')
    tempList = {}
    for word in words:
        tempWord = word.split(':')[0]
        tempList[tempWord] = float(word.split(':')[1])
        if tempWord not in alchemyCorpus.keys():
            alchemyCorpus[tempWord] = 1
        else:
            alchemyCorpus[tempWord] += 1
    alchemyList.append(tempList)
alchemyFile.close()

totalSize = len(alchemyList)

predictedTopicList = []
index = 0
correctCount = 0.0
totalCount = 0.0
for topics in alchemyList:
    print str(index)+'/'+str(totalSize)
    maxTopic = ''
    maxProb = -1
    for (topic, prob) in topics.items():
        seg = topic[1:].split('/')
        targetTopic = seg[len(seg)-1]
        maxSeed = ''
        maxScore = -1
        for ruleSeed in ruleList.keys():
            score = cr.phraseSimilarity(targetTopic, ruleSeed)
            if score >= maxScore:
                maxSeed = ruleSeed
                maxScore = score
        if maxScore >= maxProb:
            maxProb = maxScore
            maxTopic = maxSeed
        prediction = ruleList[maxTopic]
    predictedTopicList.append(prediction)
    outputFile.write(maxTopic + ': ' + prediction+'\n')
    if prediction in keywordList[index]:
        correctCount += 1
    totalCount += 1
    index += 1

print correctCount
print totalCount
outputFile.close()