import os
import shutil
import glob
import subprocess
import readable_infer as ri
from evaluation import eval

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
        outputFile.write('"'+topicList[i]+'","'+contentList[i].replace('"', "'")+'"\n')
    outputFile.close()

fold = 5

ratioSet = [0.1, 0.3, 0.5, 0.7, 0.9]
precisionSet = [0, 0, 0, 0, 0]
recallSet = [0, 0, 0, 0, 0]
fMeasureSet = [0, 0, 0, 0, 0]
accuracySet = [0, 0, 0, 0, 0]
coverageSet = [0, 0, 0, 0, 0]

brand = 'BathAndBodyWorks'
docFile = open('Hybrid\\'+brand+'.content', 'r')
topicFile = open('Hybrid\\'+brand+'.keyword', 'r')
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
for line in docFile:
    docContent.append(line.strip())
for topic in topicCorpus:
    topicCorpusFile.write(topic + '\n')
docFile.close()
topicFile.close()
topicCorpusFile.close()

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

    #convert to LDA format
    formatLDA(topicTrain, docTrain, 'train')
    formatLDA(topicTest, docTest, 'test')

    print "train"
    #Run LDA training
    for file in glob.glob('TMT\\LDAFormat*.csv.term-counts.cache*'):
        os.remove(file)
    if os.path.exists('TMT Snapshots'):
        shutil.rmtree('TMT Snapshots')
    subprocess.check_output('java -jar TMT\\tmt-0.4.0.jar TMT\\train.scala', shell=True)

    print "infer"
    #Run LDA inference
    modifyFiles('TMT Snapshots\\01000\\description.txt')
    modifyFiles('TMT Snapshots\\01000\\params.txt')
    subprocess.check_output('java -jar TMT\\tmt-0.4.0.jar TMT\\test.scala', shell=True)

    #Convert inference result
    shutil.copy('TMT Snapshots\\LDAFormatTest-document-topic-distributuions.csv', 'TMT\\')
    #addLatent('LLDAdata\\label-index.txt')

    #test differnt configurations on generating output topics
    for h in range(len(precisionSet)):
        ri.convertOutput(ratioSet[h])

        #Evaluate
        (tempRecall, tempPrecision, tempFmeasure, tempAccuracy, tempCoverage) = eval()
        recallSet[h] += tempRecall
        precisionSet[h] += tempPrecision
        fMeasureSet[h] += tempFmeasure
        accuracySet[h] += tempAccuracy
        coverageSet[h] += tempCoverage

for g in range(len(precisionSet)):
    print str(recallSet[g] / fold)
    print str(precisionSet[g] / fold)
    print str(fMeasureSet[g] / fold)
    print str(accuracySet[g]/fold)
    print str(coverageSet[g] / fold)+'\n'