import random

__author__ = 'renhao.cui'
brand = 'BathAndBodyWorks'
testFile = open('TMT\\LDAFormatTest.csv', 'r')
LDAoutput = open('LLDAdata\\docLabels.txt', 'r')
mappingLabelFile = open('LLDAdata\\mappingLabels.txt', 'r')
outputFile = open('sampleOutput\\sampleOutput.'+brand, 'w')
alchemyOutputFile = open('sampleOutput\\sampleAlchemyOutput.'+brand, 'w')
alchemyFile = open('LLDAdata\\alchemyTestData', 'r')

sampleLimit = 100
randomNums = []
LDAtopics = {}
trueLabels = []
content = []
mappingTopics = {}
alchemyTopics = {}

for line in testFile:
    seg = line[1:].strip().split('","')
    text = seg[1][:-1]
    trueLabels.append(seg[0])
    content.append(text)

testSize = len(content)

for i in range(testSize):
    index = random.randint(0, testSize-1)
    if index not in randomNums:
        randomNums.append(index)
    if len(randomNums) == sampleLimit:
        break

for line in LDAoutput:
    seg = line.strip().split(' ')
    if len(seg) > 1:
        LDAtopics[int(seg[0])] = seg[1]

for line in mappingLabelFile:
    seg = line.strip().split(' ')
    mappingTopics[int(seg[0])] = seg[1]

i = 0
for line in alchemyFile:
    alchemyTopics[i] = line.strip()
    i += 1

for index in randomNums:
    out = str(index) + '\t'+content[index]+'\t'+trueLabels[index]
    if index in LDAtopics:
        out += '\t' + LDAtopics[index]
    else:
        out += '\tN/A'
    out += '\t' + mappingTopics[index]
    outputFile.write(out+'\n')
    alchemyOutputFile.write(str(index) + '\t' + alchemyTopics[index]+'\n')