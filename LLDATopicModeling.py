__author__ = 'renhao.cui'
from sklearn import cross_validation
import os
import shutil
import glob
import subprocess
import readable_infer as ri
import modelUtility
import sys

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

def LLDATrainInfer(doc_train, label_train, doc_test, label_test, candTopic, trainProbFlag):
    formatLDA(label_train, doc_train, 'train')
    formatLDA(label_test, doc_test, 'test')

    print "train LLDA..."
    subprocess.check_output('java -jar TMT\\tmt-0.4.0.jar TMT\\train.scala', shell=True)

    print "generate LLDA test output..."
    modifyFiles('TMT Snapshots\\01000\\description.txt')
    modifyFiles('TMT Snapshots\\01000\\params.txt')
    subprocess.check_output('java -jar TMT\\tmt-0.4.0.jar TMT\\test.scala', shell=True)
    shutil.copy('TMT Snapshots\\LDAFormatTest-document-topic-distributuions.csv', 'TMT\\')
    shutil.copy('TMT Snapshots\\01000\\label-index.txt', 'LLDAdata\\')

    #{lineNum: {rank: {topic: prob}}}
    LDACoveredOutput = ri.convertOutput2_fullList('test', 0.0) #limitSet[h]
    LDACoveredOutputTrain = {}
    if trainProbFlag:
        print 'generate LLDA output on training data...'
        subprocess.check_output('java -jar TMT\\tmt-0.4.0.jar TMT\\test2.scala', shell=True)
        shutil.copy('TMT Snapshots\\LDAFormatTrain-document-topic-distributuions.csv', 'TMT\\')
        LDACoveredOutputTrain = ri.convertOutput2_fullList('train', 0.0) #limitSet[h]
        if len(LDACoveredOutputTrain) != len(doc_train):
            print 'Train prob output size error!'
            sys.exit()

    for file in glob.glob('TMT\\LDAFormat*.csv.term-counts.cache*'):
        os.remove(file)
    if os.path.exists('TMT Snapshots'):
        shutil.rmtree('TMT Snapshots')

    testSize = len(label_test)
    correct = 0.0
    total = 0.0
    if len(LDACoveredOutput) != testSize:
        print 'Test output size error!'
        sys.exit()

    for index in range(testSize):
        total += 1.0
        if LDACoveredOutput[index][1].keys()[0] in label_test[index].split(' '):
            correct += 1.0

    return correct/total, LDACoveredOutput, LDACoveredOutputTrain

def run():
    brandList = ['Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']
    outputFile = open('HybridData/Experiment/result', 'w')
    for brand in brandList:
        print brand
        docContent, topics, candTopic = modelUtility.readData('HybridData/Original/' + brand + '.content', 'HybridData/Original/' + brand + '.keyword')

        accuracySum = 0.0
        for i in range(5):
            print 'fold num: '+str(i)
            doc_train, doc_test, label_train, label_test = cross_validation.train_test_split(docContent, topics, test_size=0.2, random_state=0)
            accuracy, testOutput, trainOutput = LLDATrainInfer(doc_train, label_train, doc_test, label_test, candTopic, True)
            accuracySum += accuracy
        print accuracySum/5
        outputFile.write(brand+'\t'+str(accuracySum/5)+'\n')

    outputFile.close()