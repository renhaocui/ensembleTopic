__author__ = 'renhao.cui'

brand = 'Elmers'

keywordFile = open('semanticMapping\\'+brand+'.keyword', 'r')
#ruleFile = open('topicRule\\'+brand+'old.rule', 'r')
#newRuleFile = open('topicRule\\'+brand+'.rule', 'w')
keywordCorpus = {}

for line in keywordFile:
    topics = line.strip().split(' ')
    for topic in topics:
        if topic not in keywordCorpus.keys():
            keywordCorpus[topic] = 1
        else:
            keywordCorpus[topic] += 1
keywordFile.close()
print len(keywordCorpus.keys())
for i in keywordCorpus.keys():
    print i+': '+str(keywordCorpus[i])
'''
for line in ruleFile:
    item = line.strip().split(': ')
    topic = item[0]
    if topic in keywordCorpus.keys():
        newRuleFile.write(line)
'''