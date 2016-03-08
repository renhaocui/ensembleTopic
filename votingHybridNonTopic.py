__author__ = 'renhao.cui'
import os
import shutil
import glob
import subprocess
import readable_infer as ri
import combinedMapping as cm
from sklearn import svm

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
        for i in range(len(contentList)):
            outputFile.write('"' + topicList[i] + '","' + contentList[i].replace('"', "'") + '"\n')
    elif model == 'test':
        outputFile = open('TMT\\LDAFormatTest.csv', 'w')
        for i in range(len(contentList)):
            outputFile.write('"NONE","' + contentList[i].replace('"', "'") + '"\n')
    outputFile.close()

iters = 1
brandList = ['BathAndBodyWorks']

for brand in brandList:
    limitSet = [0.05]
    docFile = open('Hybrid\\' + brand + '.content', 'r')
    topicFile = open('Hybrid\\' + brand + '.keyword', 'r')
    alchemyFile = open('Hybrid\\' + brand + '.alchemy', 'r')
    nonTopicContentFile = open('supportData\\'+brand+'.nonTopic', 'r')
    nonTopicAlchemyFile = open('supportData\\'+brand+'.alchemy', 'r')
    topicCorpusFile = open('LLDAdata\\topic.corpus', 'w')

    docTrain = []
    docTest = []
    topicTrain = []
    topicTest = []
    alchemyTrain = []
    alchemyTest = []
    topicCorpus = {}

    for line in topicFile:
        topics = line.strip().replace('"', '')
        topicTrain.append(topics)
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
        alchemyTrain.append(tempList)

    for line in docFile:
        docTrain.append(line.strip())
    docFile.close()

    for topic in topicCorpus:
        topicCorpusFile.write(topic + '\n')
    topicCorpusFile.close()
    topicSize = len(topicCorpus)

    for line in nonTopicContentFile:
        docTest.append(line.strip())
    nonTopicContentFile.close()

    for line in nonTopicAlchemyFile:
        words = line.strip().split(' ')
        tempList = {}
        for word in words:
            tempWord = word.split(':')[0]
            tempList[tempWord] = float(word.split(':')[1])
        alchemyTest.append(tempList)
    nonTopicAlchemyFile.close()

    for j in range(iters):
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

        # dict[docNo] = (label, prob)
        LDACoveredOutput = ri.convertOutput2('test')
        LDATrainingOutput = ri.convertOutput2('train')

        #test differnt configurations on generating output topics
        testSize = len(topicTest)
        for h in range(len(limitSet)):
            print 'train Mapping Rule...'
            (model, cand, candProb) = cm.mappingTrainer2(alchemyTrain, topicTrain, limitSet[h])

            trueTrainLabels = []
            for labels in topicTrain:
                trueTrainLabels.append(labels.split(' '))

            mappingTrainOutput = cm.mappingInfer3(model, cand, candProb, alchemyTrain)
            SVMTrainData = {}
            svmTrainingFile = open('testDetailedOutput\\'+brand+'.svmTrain', 'w')
            svmInferenceFile = open('testDetailedOutput\\'+brand+'.svmInfer', 'w')
            for i in range(len(mappingTrainOutput)):
                if (i in LDATrainingOutput) and (LDATrainingOutput[i][0] != mappingTrainOutput[i][0]) and (mappingTrainOutput[i][1] != -1.0):
                    #LDA -> 0
                    if (LDATrainingOutput[i][0] in trueTrainLabels[i]) and (mappingTrainOutput[i][0] in trueTrainLabels[i]):
                        if LDATrainingOutput[i][1] >= mappingTrainOutput[i][1]:
                            SVMTrainData[i] = (LDATrainingOutput[i][1], mappingTrainOutput[i][1], 0)
                            svmTrainingFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t0\n')
                        else:
                            SVMTrainData[i] = (LDATrainingOutput[i][1], mappingTrainOutput[i][1], 1)
                            svmTrainingFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t1\n')
                    elif LDATrainingOutput[i][0] in trueTrainLabels[i]:
                        SVMTrainData[i] = (LDATrainingOutput[i][1], mappingTrainOutput[i][1], 0)
                        svmTrainingFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t0\n')
                    elif mappingTrainOutput[i][0] in trueTrainLabels[i]:
                        SVMTrainData[i] = (LDATrainingOutput[i][1], mappingTrainOutput[i][1], 1)
                        svmTrainingFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t1\n')
            featureSet = []
            labelSet = []
            for (LDAProb, mappingProb, classNo) in SVMTrainData.values():
                featureSet.append([LDAProb, mappingProb])
                labelSet.append(classNo)
            svmModel = svm.SVC()
            svmModel.fit(featureSet, labelSet)

            mappingOutput = cm.mappingInfer3(model, cand, candProb, alchemyTest)
            mapLabelFile = open('LLDAdata\\mappingLabels.txt', 'w')
            combinedTopicFile = open('LLDAdata\\combinedLabels.txt', 'w')
            for i in range(testSize):
                out = str(i) + ' '
                if i in LDACoveredOutput and i in mappingOutput:
                    if LDACoveredOutput[i][0] == mappingOutput[i][0]:
                        # when they agree
                        out += LDACoveredOutput[i][0]
                    else:
                        # disagreed
                        if mappingOutput[i][1] == -1.0:
                            out += LDACoveredOutput[i][0]
                        else:
                            svmClass = svmModel.predict([LDACoveredOutput[i][1], mappingOutput[i][1]])
                            if svmClass[0] == 0:
                                out += LDACoveredOutput[i][0]
                                svmInferenceFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t0\n')
                            else:
                                out += mappingOutput[i][0]
                                svmInferenceFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t1\n')
                else:
                    if i not in LDACoveredOutput:
                        out += mappingOutput[i][0]

                combinedTopicFile.write(out + '\n')
                out = str(i)
                mapLabelFile.write(out + ' ' + mappingOutput[i][0] + ':' + str(mappingOutput[i][1]) + ', ' + str(
                    mappingOutput[i][2]) + ', ' + str(mappingOutput[i][3]) + '\n')
            mapLabelFile.close()
            combinedTopicFile.close()

    print brand