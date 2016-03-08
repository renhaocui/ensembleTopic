import operator

__author__ = 'renhao.cui'
import os
import shutil
import glob
import subprocess
import readable_infer as ri
import combinedMapping as cm

def modifyFiles(fileName):
    file = open(fileName, 'r')
    fileContent = []
    for line in file:
        fileContent.append(line.replace('Labeled', ''))
    file.close()
    # os.remove(fileName)
    newFile = open(fileName, 'w')
    for line in fileContent:
        newFile.write(line)
    newFile.close()

def formatLDA(topicList, contentList, model):
    if model == 'train':
        outputFile = open('TMT\\LDAFormatTrain.csv', 'w')
    elif model == 'test':
        outputFile = open('TMT\\LDAFormatTest.csv', 'w')
    size = len(contentList)
    for t in range(size):
        outputFile.write('"' + topicList[t] + '","' + contentList[t].replace('"', "'") + '"\n')
    outputFile.close()

def listToString(inputList):
    output = ''
    for item in inputList:
        output += item+' '
    return output.strip()

fold = 5
brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']

for brand in brandList:
    limitSet = [0.3]
    accuracySet = [0.0, 0.0, 0.0, 0.0, 0.0]
    firstOneCorrectSet = [0.0, 0.0, 0.0, 0.0, 0.0]
    LLDACorrectSet = [0.0, 0.0, 0.0, 0.0, 0.0]
    mappingCorrectSet = [0.0, 0.0, 0.0, 0.0, 0.0]

    docFile = open('Hybrid\\' + brand + '.content', 'r')
    topicFile = open('Hybrid\\' + brand + '.keyword', 'r')
    alchemyFile = open('Hybrid\\' + brand + '.alchemy', 'r')
    topicCorpusFile = open('LLDAdata\\topic.corpus', 'w')

    docContent = []
    topicContent = []
    topicCorpus = {}
    alchemyContent = []

    for line in topicFile:
        topics = line.strip().replace('"', '')
        topicContent.append(topics)
        for topic in topics.split(' '):
            if topic not in topicCorpus:
                topicCorpus[topic] = 1.0
            else:
                topicCorpus[topic] += 1.0
    topicFile.close()

    for line in alchemyFile:
        words = line.strip().split(' ')
        tempList = {}
        for word in words:
            tempWord = word.split(':')[0]
            tempList[tempWord] = float(word.split(':')[1])
        alchemyContent.append(tempList)

    for line in docFile:
        content = line.strip()
        docContent.append(content)
    docFile.close()

    for topic in topicCorpus:
        topicCorpusFile.write(topic + '\n')
    topicCorpusFile.close()
    topicSize = len(topicCorpus)
    size = len(docContent)

    for j in range(fold):
        # split the data
        docTrain = []
        docTest = []
        topicTrain = []
        topicTest = []
        alchemyTrain = []
        alchemyTest = []
        for i in range(size):
            if i % fold == j:
                docTest.append(docContent[i])
                topicTest.append(topicContent[i])
                alchemyTest.append(alchemyContent[i])
            else:
                docTrain.append(docContent[i])
                topicTrain.append(topicContent[i])
                alchemyTrain.append(alchemyContent[i])

        # convert to LDA format
        formatLDA(topicTrain, docTrain, 'train')
        formatLDA(topicTest, docTest, 'test')
        shutil.copy('TMT\\LDAFormatTest.csv', 'testDetailedOutput\\'+brand+'.LDAformat')

        print "train LLDA..."
        #Run LDA training
        for file in glob.glob('TMT\\LDAFormat*.csv.term-counts.cache*'):
            os.remove(file)
        if os.path.exists('TMT Snapshots'):
            shutil.rmtree('TMT Snapshots')
        subprocess.check_output('java -jar TMT\\tmt-0.4.0.jar TMT\\train.scala', shell=True)

        print "generate LLDA output..."
        #Run LDA inference
        modifyFiles('TMT Snapshots\\01000\\description.txt')
        modifyFiles('TMT Snapshots\\01000\\params.txt')
        subprocess.check_output('java -jar TMT\\tmt-0.4.0.jar TMT\\test.scala', shell=True)
        #subprocess.check_output('java -jar TMT\\tmt-0.4.0.jar TMT\\test2.scala', shell=True)

        #Convert inference result
        shutil.copy('TMT Snapshots\\LDAFormatTest-document-topic-distributuions.csv', 'TMT\\')
        #shutil.copy('TMT Snapshots\\LDAFormatTrain-document-topic-distributuions.csv', 'TMT\\')
        shutil.copy('TMT Snapshots\\01000\\label-index.txt', 'LLDAdata\\')

        testSize = len(topicTest)
        for h in range(len(limitSet)):
            # output[lineNum] = [(label1, prob1),(label2, prob2)...]
            LDACoveredOutput = ri.convertOutput2_fullList('test', limitSet[h])
            outputFile = open('testDetailedOutput//output.'+brand+'_'+str(limitSet[h]), 'w')
            print 'train Mapping Rule...'
            (model, cand, candProb) = cm.mappingTrainer4(alchemyTrain, topicTrain)
            print 'Inference on mapping rule...'
            mappingOutput = cm.mappingInfer3_fullList(model, cand, alchemyTest)
            # gold standard labels
            sampleLabelsFile = open('TMT\\LDAFormatTest.csv', 'r')
            sampleLabels = []
            for line in sampleLabelsFile:
                seg = line.strip().split('","')
                labels = seg[0][1:].split(' ')
                sampleLabels.append(labels)
            sampleLabelsFile.close()
            correct = 0.0
            total = 0.0
            firstOneCorrect = 0.0
            firstOneTotal = 0.0
            LLDACorrect = 0.0
            mappingCorrect = 0.0

            for i in range(testSize):
                if i in LDACoveredOutput and i in mappingOutput:
                    outString = str(i)+'\t'
                    for item in LDACoveredOutput[i]:
                        if item[0] in sampleLabels[i]:
                            LLDACorrect += 1.0
                            break
                    for item in mappingOutput[i]:
                        if item[0] in sampleLabels[i]:
                            mappingCorrect += 1.0
                            break
                    if len(LDACoveredOutput[i]) == 0:
                        out = mappingOutput[i][0][0]
                    elif len(LDACoveredOutput[i]) == 1:
                        if LDACoveredOutput[i][0][0] in sampleLabels[i]:
                            firstOneCorrect += 1.0
                        firstOneTotal += 1.0
                        out = LDACoveredOutput[i][0][0]
                    elif len(mappingOutput[i]) == 0:
                        out = LDACoveredOutput[i][0][0]
                    elif LDACoveredOutput[i][0][0] == mappingOutput[i][0][0]:
                        # when they agree
                        out = LDACoveredOutput[i][0][0]
                    else:
                        outTopicDict = {}
                        for item in LDACoveredOutput[i]:
                            outTopicDict[item[0]] = item[1]
                            outString += item[0]+'\t'+str(item[1])+'\t'
                        outString += '\t'
                        for item in mappingOutput[i]:
                            if item[0] in outTopicDict:
                                outTopicDict[item[0]] += item[1]
                            outString += item[0]+'\t'+str(item[1])+'\t'
                        out = max(outTopicDict.items(), key=operator.itemgetter(1))[0]

                        outString += '\t'
                        outString += listToString(sampleLabels[i])
                        outputFile.write(outString+'\n')
                else:
                    if i not in LDACoveredOutput:
                        out = mappingOutput[i][0][0]
                total += 1.0
                if out in sampleLabels[i]:
                    correct += 1.0
            accuracySet[h] += correct/total
            if firstOneTotal == 0.0:
                firstOneCorrectSet[h] += 0.0
            else:
                firstOneCorrectSet[h] += firstOneCorrect/firstOneTotal
            LLDACorrectSet[h] += LLDACorrect/i
            mappingCorrectSet[h] += mappingCorrect/i
            outputFile.close()
    print brand
    print len(topicCorpus.keys())
    for g in range(len(limitSet)):
        print 'limit: '+str(limitSet[g])
        print str(accuracySet[g] * 100 / fold)
        print str(firstOneCorrectSet[g] * 100 / fold)
        print str(LLDACorrectSet[g] * 100 / fold)
        print str(mappingCorrectSet[g] * 100 / fold)+'\n'