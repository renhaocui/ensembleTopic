__author__ = 'renhao.cui'

def eval(target, testList):
    if target in testList:
        return True
    else:
        return False

def listToString(inputList):
    out = ''
    for item in inputList:
        out += str(item)+','
    return out[:-1]

testFile = open('TMT\\LDAFormatTest.csv', 'r')
LDAFile = open('LLDAdata\\docLabels.txt', 'r')
mappingFile = open('LLDAdata\\mappingLabels.txt', 'r')
outputFile = open('LLDAdata\\output.analysis', 'w')

trueList = {}
LDALabels = {}
mappingLabels = {}

index = 0
for line in testFile:
    seg = line.strip()[1:].split('","')
    labels = seg[0].split(' ')
    trueList[index] = labels
    index += 1

for line in LDAFile:
    seg = line.strip().split(' ')
    labels = seg[1].split(':')
    LDALabels[int(seg[0])] = (labels[0], float(labels[1]))

for line in mappingFile:
    seg = line.strip().split(' ')
    labels = seg[1][:-1].split(':')
    mappingLabels[int(seg[0])] = (labels[0], float(labels[1]))

testFile.close()
LDAFile.close()
mappingFile.close()


total = 0.0
correct = 0.0
LDACorrect = 0.0
mappingCorrect = 0.0
LDALabel = ''
LDAProb = 0.0
mappingLabel = ''
mappingProb = 0.0
testCount = 0.0
combineCount = 0.0
LDALargerCount = 0.0
bothCount = 0.0
for i in range(len(trueList)):
    trueLabels = trueList[i]
    out = str(i)+'\t'+listToString(trueLabels)+'\t'
    if i in LDALabels:
        (LDALabel, LDAProb) = LDALabels[i]
        out += LDALabel+'\t'+str(LDAProb)+'\t'
    if i in mappingLabels:
        (mappingLabel, mappingProb) = mappingLabels[i]
        out += mappingLabel+'\t'+str(mappingProb)
    if eval(LDALabel, trueLabels) or eval(mappingLabel, trueLabels):
        correct += 1.0
    if LDALabel != mappingLabel:
        if eval(LDALabel, trueLabels) or eval(mappingLabel, trueLabels):
            outputFile.write(out+'\n')
            if mappingProb == 1.0:
                if not eval(mappingLabel, trueLabels):
                    testCount += 1.0

        if LDAProb >= mappingProb:
            LDALargerCount += 1
            combineLabel = LDALabel
        else:
            combineLabel = mappingLabel
        if eval(combineLabel, trueLabels):
            combineCount += 1.0
        if eval(LDALabel, trueLabels):
            LDACorrect += 1.0
        if eval(mappingLabel, trueLabels):
            mappingCorrect += 1.0

        if eval(LDALabel, trueLabels) and eval(mappingLabel, trueLabels):
            bothCount += 1.0
        total += 1

print total
print correct/total
print LDACorrect
print mappingCorrect
print LDALargerCount
print combineCount
print bothCount
print testCount
outputFile.close()