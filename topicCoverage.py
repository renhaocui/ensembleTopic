import operator

__author__ = 'renhao.cui'

brand = 'Chilis'

keywordFile = open('semanticMapping\\'+brand+'.keyword', 'r')

keywordList = []
topicCorpus = {}
topicSize = {}
for line in keywordFile:
    topics = line.strip().split(' ')
    size = len(topics)
    if size not in topicSize.keys():
        topicSize[size] = 1
    else:
        topicSize[size] += 1
    keywordList.append(topics)
    for topic in topics:
        if topic not in topicCorpus.keys():
            topicCorpus[topic] = 1
        else:
            topicCorpus[topic] += 1

print len(topicCorpus.items())
print len(keywordList)

sorted_corpusCount = sorted(topicCorpus.items(), key=operator.itemgetter(1))
for (topic, value) in sorted_corpusCount:
    print topic + ': ' + str(value)

for (size, num) in topicSize.items():
    print str(size) +': '+ str(num)

