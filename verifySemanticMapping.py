__author__ = 'renhao.cui'

brand = 'Elmers'

keywordFile = open('semanticMapping\\'+brand+'.keyword', 'r')
outputFile = open('semanticMapping\\'+brand+'.semantic', 'r')

correct = 0
prediction = []
for line in outputFile:
    prediction.append(line.strip().split(': ')[1])

index = 0
for line in keywordFile:
    trueTopics = line.strip().split(' ')
    if prediction[index] in trueTopics:
        correct += 1
    index += 1
print correct
print index