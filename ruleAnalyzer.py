__author__ = 'rencui'
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

brand = 'Chilis'

ruleFile = open('topicRule\\'+brand+'-topics.txt', 'r')
outputFile = open('topicRule\\'+brand+'.rule', 'w')

topicRule = {}

line = ruleFile.readline()
data = json.loads(line.strip())
for item in data:
    topic = item['value'].replace(' ', '_')
    exactWords = item['exactPhraseTerms'] #keyword list
    orWords = item['orTerms']
    andWords = item['andTerms']
    keywordList = []
    if orWords is not None:
        for keyword in orWords:
            keywordList.append(keyword.replace(' ', '_'))
    if exactWords is not None:
        for keyword in exactWords:
            keywordList.append(keyword.replace(' ', '_'))
    if andWords is not None:
        for keyword in andWords:
            keywordList.append(keyword.replace(' ', '_'))
    if topic not in topicRule.keys():
        topicRule[topic] = keywordList
    else:
        temp = topicRule[topic]
        for keyword in keywordList:
            if keyword not in temp:
                temp.append(keyword)
        topicRule[topic] = temp

for (key, value) in topicRule.items():
    out = ''
    for keyword in value:
        out += keyword + '/'
    outputFile.write(key+': '+out[:-1]+'\n')

ruleFile.close()
outputFile.close()