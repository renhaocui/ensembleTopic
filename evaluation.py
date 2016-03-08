
def eval(model):
    if model == 'mapping':
        predictLabelsFile = open('LLDAdata\\mappingLabels.txt', 'r')
    elif model == 'hybrid':
        predictLabelsFile = open('LLDAdata\\combinedLabels.txt', 'r')
    else:
        predictLabelsFile = open('LLDAdata\\docLabels.txt', 'r')
    labellistFile = open('LLDAdata\\topic.corpus', 'r')
    sampleLabelsFile = open('TMT\\LDAFormatTest.csv', 'r')

    predictLabels = []
    sampleLabels = []
    validIndex = []
    labelDict = {}

    index = 0
    for line in labellistFile:
        labelDict[line.strip()] = index
        index += 1

    for line in predictLabelsFile:
        line = line.replace('NewTopic ', '')
        seg = line.strip().split(' ')
        labels = seg[1:]
        if len(labels) > 0:
            validIndex.append(int(seg[0]))
            predictLabels.append(labels)
    coverCount = len(predictLabels)

    index = 0
    for line in sampleLabelsFile:
        if index in validIndex:
            seg = line.strip().split('","')
            labels = seg[0][1:].split(' ')
            sampleLabels.append(labels)
        index += 1
    totalCount = index

    correct = 0.0
    for i in range(len(validIndex)):
        for topic in predictLabels[i]:
            if topic in sampleLabels[i]:
                correct += 1
                break

    if totalCount == 0:
        totalCount = 1
    if len(validIndex) == 0:
        validIndex.append(0)
    return 0, 0, 0, correct*100/len(validIndex), float(coverCount) * 100 / totalCount

    conMatrix = []
    for i in range(index):
        temp = []
        for j in range(index):
            temp.append(0.0)
        conMatrix.append(temp)

    for i in range(len(sampleLabels)):
        sample = sampleLabels[i]
        prediction = predictLabels[i]
        total = len(sample)*len(prediction)
        for item in sample:
            for thing in prediction:
                conMatrix[labelDict[thing]][labelDict[item]] += 1.0/total

    predictLabelsFile.close()
    sampleLabelsFile.close()
    labellistFile.close()

    precision = []
    recall = []
    fmeasure = []

    #calculate recall
    for i in range(len(labelDict)):
        totalSum = 0.0
        for j in range(len(labelDict)):
            totalSum += conMatrix[j][i]
        if totalSum == 0:
            recall.append(0.0)
        else:
            recall.append(conMatrix[i][i]/totalSum)

    #calculate precision
    for i in range(len(labelDict)):
        totalSum = 0.0
        for j in range(len(labelDict)):
            totalSum += conMatrix[i][j]
        if totalSum == 0:
            precision.append(0.0)
        else:
            precision.append(conMatrix[i][i]/totalSum)

    for i in range(len(labelDict)):
        if precision[i] == 0 or recall[i] == 0:
            fmeasure.append(0.0)
        else:
            fmeasure.append((2 * recall[i] * precision[i]) / (precision[i] + recall[i]))

    averageRecall = sum(recall)/len(labelDict)
    averagePrecision = sum(precision)/len(labelDict)
    averageFmeasure = sum(fmeasure)/len(labelDict)

    return averageRecall*100, averagePrecision*100, averageFmeasure*100, correct*100/len(validIndex), float(coverCount) * 100 / totalCount
