__author__ = 'rencui'

brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']

for brand in brandList:
    print brand
    docFile = open('Hybrid//' + brand + '.content', 'r')
    inputTrainFile = open('testDetailedOutput//'+brand+'.svmTrain', 'r')
    inputInferFile = open('testDetailedOutput//'+brand+'.svmInfer', 'r')
    outputTrainFile = open('testDetailedOutput//'+brand+'.trainContent', 'w')
    outputInferFile = open('testDetailedOutput//'+brand+'.inferContent', 'w')
    docContent = []
    trainIDList = []
    inferIDList = []

    for line in docFile:
        docContent.append(line.strip())
    docFile.close()

    for line in inputTrainFile:
        try:
            trainID = int(line.strip().split('\t')[0])
            trainIDList.append(trainID)
        except:
            print 'error at '+line

    inputTrainFile.close()

    for line in inputInferFile:
        try:
            inferID = int(line.strip().split('\t')[0])
            inferIDList.append(inferID)
        except:
            print 'error at '+line
    inputInferFile.close()

    size = len(docContent)
    # split the data
    docTrain = []
    docTest = []
    topicTrain = []
    topicTest = []
    alchemyTrain = []
    alchemyTest = []
    for i in range(size):
        if i % 5 == 4:
            docTest.append(docContent[i])
        else:
            docTrain.append(docContent[i])

    for i in trainIDList:
        outputTrainFile.write(str(i)+'\t'+docTrain[i]+'\n')

    for i in inferIDList:
        outputInferFile.write(str(i)+'\t'+docTest[i]+'\n')

    outputTrainFile.close()
    outputInferFile.close()