__author__ = 'renhao.cui'
import os
import shutil
import glob
import subprocess
import readable_infer as ri
from evaluation import eval
import combinedMapping as cm

def modifyFiles(fileName, prevNum, num):
    file = open(fileName, 'r')
    fileContent = []
    for line in file:
        fileContent.append(line.replace('numTopics = ' + str(prevNum), 'numTopics = ' + str(num)))
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
topicNumSet = [100, 200, 300, 500]
numSet = [3, 5, 10, 20, 50, 100]
ratioSet = [0.0001]


brand = 'Elmers'
docFile = open('Hybrid\\' + brand + '.content', 'r')
topicFile = open('Hybrid\\' + brand + '.keyword', 'r')
topicCorpusFile = open('LLDAdata\\topic.corpus', 'w')
resultFile = open(brand + '.resultOutput', 'w')
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
for line in docFile:
    docContent.append(line.strip())
for topic in topicCorpus:
    topicCorpusFile.write(topic + '\n')
docFile.close()
topicFile.close()
topicCorpusFile.close()

size = len(docContent)

for o in range(len(topicNumSet)):
    precisionSet = [0, 0, 0, 0, 0, 0]
    recallSet = [0, 0, 0, 0, 0, 0]
    fMeasureSet = [0, 0, 0, 0, 0, 0]
    accuracySet = [0, 0, 0, 0, 0, 0]
    coverageSet = [0, 0, 0, 0, 0, 0]
    if o == 0:
        modifyFiles('TMT\\train2.scala', 200, topicNumSet[o])
    else:
        modifyFiles('TMT\\train2.scala', topicNumSet[o-1], topicNumSet[o])

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

        print "train"
        # Run LDA training
        for file in glob.glob('TMT\\LDAFormat*.csv.term-counts.cache*'):
            os.remove(file)
        if os.path.exists('TMT Snapshots'):
            shutil.rmtree('TMT Snapshots')
        subprocess.check_output('java -jar TMT\\tmt-0.4.0.jar TMT\\train2.scala', shell=True)

        print "infer"
        #Run LDA inference
        subprocess.check_output('java -jar TMT\\tmt-0.4.0.jar TMT\\test2.scala', shell=True)
        subprocess.check_output('java -jar TMT\\tmt-0.4.0.jar TMT\\test.scala', shell=True)

        #Convert inference result
        shutil.copy('TMT Snapshots\\LDAFormatTest-document-topic-distributuions.csv', 'TMT\\')
        shutil.copy('TMT Snapshots\\LDAFormatTrain-document-topic-distributuions.csv', 'TMT\\')

        #test differnt configurations on generating output topics
        for h in range(len(precisionSet)):
            outputTopicsList = ri.generateOutput2(numSet[h], 'train')
            topicTrainSet = []
            tempSet = []
            for i in range(len(topicTrain)):
                if i in outputTopicsList:
                    topicTrainSet.append(topicTrain[i])
                    tempSet.append(outputTopicsList[i])
            (model, cand) = cm.mappingTrainer2(tempSet, topicTrainSet, 0.05)
            validList = []
            testTopicList = ri.generateOutput(0, 'test')
            testSet = []
            for j in range(len(topicTest)):
                if j in testTopicList:
                    validList.append(j)
            mappingOutput = cm.mappingInfer2(model, cand, testTopicList, validList)
            LDAtopicFile = open('LLDAdata\\docLabels.txt', 'w')
            for i in range(len(topicTest)):
                if i in validList:
                    LDAtopicFile.write(str(i) + ' ' + mappingOutput[i] + '\n')
                else:
                    LDAtopicFile.write(str(i) + ' ' + '\n')
            LDAtopicFile.close()
            #Evaluate
            (tempRecall, tempPrecision, tempFmeasure, tempAccuracy, tempCoverage) = eval('LLDA')
            recallSet[h] += tempRecall
            precisionSet[h] += tempPrecision
            fMeasureSet[h] += tempFmeasure
            accuracySet[h] += tempAccuracy
            coverageSet[h] += tempCoverage

    resultFile.write('\nnumber of topics for LDA: '+str(topicNumSet[o])+'\n')
    for g in range(len(precisionSet)):
        resultFile.write('number of topics for rule mining: '+str(numSet[g])+'\n')
        #resultFile.write('recall: '+str(recallSet[g] / fold)+'\n')
        #resultFile.write('precision: '+str(precisionSet[g] / fold)+'\n')
        #resultFile.write('fmeasure: '+str(fMeasureSet[g] / fold)+'\n')
        resultFile.write('accuracy: '+ str(accuracySet[g] / fold)+'\n')
        resultFile.write('coverage: '+str(coverageSet[g] / fold)+'\n')
    resultFile.flush()
'''
        print str(recallSet[g] / fold)
        print str(precisionSet[g] / fold)
        print str(fMeasureSet[g] / fold)
        print str(accuracySet[g] / fold)
        print str(coverageSet[g] / fold) + '\n'
        '''
resultFile.close()