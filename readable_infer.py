import operator
import random

def normalization(scoreList):
    outputList = []
    total = sum(scoreList)
    for score in scoreList:
        outputList.append(score / total)
    return outputList


def thresholding(input, ratio):
    output = []
    index = 0
    for item in input:
        if float(item) > ratio:
            output.append(index)
        index += 1
    return output


def imIndex(input, ratio):
    line = {}
    output = []
    for index in range(len(input)):
        line[index] = float(input[index])
    sorted_line = sorted(line.iteritems(), key=operator.itemgetter(1))
    sorted_line.reverse()
    prob = 1
    for item in sorted_line:
        if (item[1]) >= prob * ratio:
            output.append(item[0])
            prob = prob - item[1]
        else:
            break
    return output


def convertOutput(ratio):
    distFile = open('TMT\\LDAFormatTest-document-topic-distributuions.csv', 'r')
    labelFile = open('LLDAdata\\label-index.txt', 'r')
    outputFile = open('LLDAdata\\docLabels.txt', 'w')

    labels = []
    validList = []

    for line in labelFile:
        labels.append(line[:-1])

    for line in distFile:
        seg = line[:-1].split(',')
        if seg[1] != 'NaN':
            nums = thresholding(seg[1:], ratio)
            out = seg[0]
            if len(nums) > 0:
                validList.append(int(out))
            for num in nums:
                out = out + ' ' + labels[num]
            out += " \n"
            outputFile.write(out)

    distFile.close()
    labelFile.close()
    outputFile.close()

    return validList


def convertOutput2(model):
    if model == 'train':
        distFile = open('TMT\\LDAFormatTrain-document-topic-distributuions.csv', 'r')
        outputFile = open('LLDAdata\\trainDocLabels.txt', 'w')
    else:
        distFile = open('TMT\\LDAFormatTest-document-topic-distributuions.csv', 'r')
        outputFile = open('LLDAdata\\docLabels.txt', 'w')
    labelFile = open('LLDAdata\\label-index.txt', 'r')

    labels = []
    outList = {}

    for line in labelFile:
        labels.append(line.strip())

    for line in distFile:
        seg = line.strip().split(',')
        if seg[1] != 'NaN':
            outIndex = 0
            maxProb = -1.0
            index = 0
            for item in seg[1:]:
                if float(item) >= maxProb:
                    outIndex = index
                    maxProb = float(item)
                index += 1
            num = int(seg[0])
            outList[num] = (labels[outIndex], maxProb)
            out = str(num) + ' ' + labels[outIndex] + ':' + str(maxProb) + '\n'
            outputFile.write(out)

    distFile.close()
    labelFile.close()
    outputFile.close()

    return outList


def convertOutput2_fullList(model, limit):
    if model == 'train':
        distFile = open('TMT\\LDAFormatTrain-document-topic-distributuions.csv', 'r')
    else:
        distFile = open('TMT\\LDAFormatTest-document-topic-distributuions.csv', 'r')
    labelFile = open('LLDAdata\\label-index.txt', 'r')

    labels = []
    tempLabels = []
    for line in labelFile:
        labels.append(line.strip())
        tempLabels.append(line.strip())
    labelFile.close()

    output = {}
    for line in distFile:
        seg = line.strip().split(',')
        lineNum = int(seg[0])
        if seg[1] != 'NaN':
            tempDict = {}
            for index, prob in enumerate(seg[1:]):
                if float(prob) >= limit:
                    tempDict[labels[index]] = float(prob)
            sorted_tempList = sorted(tempDict.items(), key=operator.itemgetter(1), reverse=True)
            tempList = []
            for (topic, prob) in sorted_tempList:
                tempList.append(prob)
            tempList_norm = normalization(tempList)
            outList = {}
            for index, (topic, prob) in enumerate(sorted_tempList):
                outList[index+1] = {topic: tempList_norm[index]}
            output[lineNum] = outList
        else:
            random.shuffle(tempLabels)
            outList = {}
            for index, label in enumerate(tempLabels):
                outList[index+1] = {label: 1.0/len(labels)}
            output[lineNum] = outList
    distFile.close()

    # output[lineNum] = {rank: {label: prob}}
    return output


def convertOutput3(ratio):
    distFile = open('TMT\\LDAFormatTest-document-topic-distributuions.csv', 'r')
    labelFile = open('LLDAdata\\label-index.txt', 'r')
    outputFile = open('LLDAdata\\docLabels.txt', 'w')

    labels = []
    outList = {}

    for line in labelFile:
        labels.append(line.strip())

    for line in distFile:
        seg = line.strip().split(',')
        if seg[1] != 'NaN':
            num = int(seg[0])
            index = 0
            for prob in seg[1:]:
                if float(prob) >= ratio:
                    outList[num] = labels[index]
                    out = str(num) + ' ' + labels[index] + '\n'
                    outputFile.write(out)
                    break
                index += 1

    distFile.close()
    labelFile.close()
    outputFile.close()

    return outList


def generateOutput(ratio, model):
    if model == 'train':
        distFile = open('TMT\\LDAFormatTrain-document-topic-distributuions.csv', 'r')
    else:
        distFile = open('TMT\\LDAFormatTest-document-topic-distributuions.csv', 'r')

    labelsList = {}

    for line in distFile:
        seg = line.strip().split(',')
        if seg[1] != 'NaN':
            labels = {}
            index = 0
            for item in seg[1:]:
                prob = float(item)
                if prob >= ratio:
                    labels[str(index)] = float(item)
                index += 1
            labelsList[int(seg[0])] = labels
    distFile.close()

    return labelsList


def generateOutput2(num, model):
    if model == 'train':
        distFile = open('TMT\\LDAFormatTrain-document-topic-distributuions.csv', 'r')
    else:
        distFile = open('TMT\\LDAFormatTest-document-topic-distributuions.csv', 'r')

    labelsList = {}

    for line in distFile:
        seg = line.strip().split(',')
        if seg[1] != 'NaN':
            labels = {}
            index = 0
            for item in seg[1:]:
                prob = float(item)
                labels[str(index)] = prob
                index += 1
            sorted_labels = sorted(labels.iteritems(), key=operator.itemgetter(1))
            sorted_labels.reverse()
            outputLabels = {}
            for j in range(num):
                outputLabels[sorted_labels[j][0]] = sorted_labels[j][1]
            labelsList[int(seg[0])] = outputLabels
    distFile.close()

    return labelsList


# top 1 label for each document, dict[docID] = label
def generateOutput3():
    distFile = open('TMT\\LDAFormatTest-document-topic-distributuions.csv', 'r')
    labelFile = open('LLDAdata\\label-index.txt', 'r')
    outputFile = open('LLDAdata\\docLabels.txt', 'w')

    labels = []
    outList = {}

    for line in labelFile:
        labels.append(line.strip())

    for line in distFile:
        seg = line.strip().split(',')
        if seg[1] != 'NaN':
            outLabels = {}
            index = 0
            for item in seg[1:]:
                prob = float(item)
                outLabels[labels[index]] = prob
                index += 1
            sorted_labels = sorted(outLabels.iteritems(), key=operator.itemgetter(1))
            sorted_labels.reverse()
            outList[int(seg[0])] = sorted_labels[0][0]
            outputFile.write(seg[0] + ' ' + sorted_labels[0][0] + '\n')
    distFile.close()
    outputFile.close()

    return outList
