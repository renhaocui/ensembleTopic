__author__ = 'renhao.cui'
import os
import shutil
import glob
import subprocess
import readable_infer as ri
from evaluation import eval
import operator

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
    for i in range(len(contentList)):
        outputFile.write('"' + topicList[i] + '","' + contentList[i].replace('"', "'") + '"\n')
    outputFile.close()

fold = 5
brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']

for brand in brandList:
    ratioSet = [0.5, 0.7, 0.9]
    precisionSet1 = [0.0, 0.0, 0.0]
    recallSet1 = [0.0, 0.0, 0.0]
    fMeasureSet1 = [0.0, 0.0, 0.0]
    accuracySet1 = [0.0, 0.0, 0.0]
    coverageSet1 = [0.0, 0.0, 0.0]
    accuracySet2 = [0.0, 0.0, 0.0]
    coverageSet2 = [0.0, 0.0, 0.0]
    accuracySet3 = [0.0, 0.0, 0.0]
    coverageSet3 = [0.0, 0.0, 0.0]

    docFile = open('Hybrid\\' + brand + '.content', 'r')
    topicFile = open('Hybrid\\' + brand + '.keyword', 'r')
    topicCorpusFile = open('LLDAdata\\topic.corpus', 'w')

    docContent = []
    topicContent = []
    topicCorpus = {}

    for line in topicFile:
        topics = line.strip().replace('"', '')
        topicContent.append(topics)
        for topic in topics.split(' '):
            if topic not in topicCorpus:
                topicCorpus[topic] = 1.0
            else:
                topicCorpus[topic] += 1.0
    topicFile.close()
    sorted_topicCorpus = sorted(topicCorpus.items(), key=operator.itemgetter(1))
    sorted_topicCorpus.reverse()
    cand = sorted_topicCorpus[0][0]

    for line in docFile:
        docContent.append(line.strip())
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
        for i in range(size):
            if i % fold == j:
                docTest.append(docContent[i])
                topicTest.append(topicContent[i])
            else:
                docTrain.append(docContent[i])
                topicTrain.append(topicContent[i])

        # convert to LDA format
        formatLDA(topicTrain, docTrain, 'train')
        formatLDA(topicTest, docTest, 'test')

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
        subprocess.check_output('java -jar TMT\\tmt-0.4.0.jar TMT\\test2.scala', shell=True)

        #Convert inference result
        shutil.copy('TMT Snapshots\\LDAFormatTest-document-topic-distributuions.csv', 'TMT\\')
        shutil.copy('TMT Snapshots\\LDAFormatTrain-document-topic-distributuions.csv', 'TMT\\')
        shutil.copy('TMT Snapshots\\01000\\label-index.txt', 'LLDAdata\\')

        #test differnt configurations on generating output topics
        testSize = len(topicTest)
        for h in range(len(ratioSet)):
            # dict[docNo] = label
            LDACoveredOutput = ri.convertOutput3(ratioSet[h])
            combinedTopicFile = open('LLDAdata\\combinedLabels.txt', 'w')
            for i in range(testSize):
                out = str(i) + ' '
                if i not in LDACoveredOutput:
                    out += cand
                else:
                    out += LDACoveredOutput[i]
                combinedTopicFile.write(out + '\n')
                out = str(i)
            combinedTopicFile.close()
            #Evaluate
            (tempRecall1, tempPrecision1, tempFmeasure1, tempAccuracy1, tempCoverage1) = eval('LLDA')
            (tempRecall2, tempPrecision2, tempFmeasure2, tempAccuracy2, tempCoverage2) = eval('hybrid')
            recallSet1[h] += tempRecall1
            precisionSet1[h] += tempPrecision1
            fMeasureSet1[h] += tempFmeasure1
            accuracySet1[h] += tempAccuracy1
            coverageSet1[h] += tempCoverage1
            accuracySet2[h] += tempAccuracy2
            coverageSet2[h] += tempCoverage2

            LDACoveredOutput = ri.generateOutput3()
            combinedTopicFile = open('LLDAdata\\combinedLabels.txt', 'w')
            for i in range(testSize):
                out = str(i) + ' '
                if i not in LDACoveredOutput:
                    out += cand
                else:
                    out += LDACoveredOutput[i]
                combinedTopicFile.write(out + '\n')
                out = str(i)
            combinedTopicFile.close()
            (tempRecall3, tempPrecision3, tempFmeasure3, tempAccuracy3, tempCoverage3) = eval('hybrid')
            accuracySet3[h] += tempAccuracy3
            coverageSet3[h] += tempCoverage3

    print brand
    for g in range(len(ratioSet)):
        #print str(recallSet[g] / fold)
        #print str(precisionSet[g] / fold)
        #print str(fMeasureSet[g] / fold)
        print 'Baseline 1'
        print str(accuracySet1[g] / fold)
        print str(coverageSet1[g] / fold)
        print 'Baseline 2'
        print str(accuracySet2[g] / fold)
        print str(coverageSet2[g] / fold)
        print 'Baseline 3'
        print str(accuracySet3[g] / fold)
        print str(coverageSet3[g] / fold) + '\n'