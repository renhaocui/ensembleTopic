import numpy

__author__ = 'renhao.cui'
import os
import shutil
import glob
import subprocess
import readable_infer as ri
from evaluation import eval
import combinedMapping as cm
from sklearn import svm, linear_model, preprocessing
import mlpy
from sklearn import tree
from sklearn.naive_bayes import GaussianNB
from tokenizer import simpleTokenize

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

fold = 5
brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']
LDAThreshold = 0.7

for brand in brandList:
    limitSet = [0.0]
    accuracySet = [0.0]

    docFile = open('Hybrid\\' + brand + '.content', 'r')
    topicFile = open('Hybrid\\' + brand + '.keyword', 'r')
    alchemyFile = open('Hybrid\\' + brand + '.alchemy', 'r')
    topicCorpusFile = open('LLDAdata\\topic.corpus', 'w')

    docContent = []
    topicContent = []
    topicCorpus = {}
    alchemyContent = []
    docLength = []
    URLFlag = []
    hashFlag = []

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
        docLength.append(len(simpleTokenize(content)))
        if '<URL>' in content:
            URLFlag.append(0)
        else:
            URLFlag.append(1)
        if '#' in content:
            hashFlag.append(0)
        else:
            hashFlag.append(1)
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
        lenTrain = []
        lenTest = []
        URLTest = []
        URLTrain = []
        hashTrain = []
        hashTest = []
        topicTrain = []
        topicTest = []
        alchemyTrain = []
        alchemyTest = []
        for i in range(size):
            if i % fold == j:
                docTest.append(docContent[i])
                lenTest.append(docLength[i])
                URLTest.append(URLFlag[i])
                topicTest.append(topicContent[i])
                alchemyTest.append(alchemyContent[i])
                hashTest.append(hashFlag[i])
            else:
                docTrain.append(docContent[i])
                lenTrain.append(docLength[i])
                URLTrain.append(URLFlag[i])
                hashTrain.append(hashFlag[i])
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
        subprocess.check_output('java -jar TMT\\tmt-0.4.0.jar TMT\\test2.scala', shell=True)

        #Convert inference result
        shutil.copy('TMT Snapshots\\LDAFormatTest-document-topic-distributuions.csv', 'TMT\\')
        shutil.copy('TMT Snapshots\\LDAFormatTrain-document-topic-distributuions.csv', 'TMT\\')
        shutil.copy('TMT Snapshots\\01000\\label-index.txt', 'LLDAdata\\')

        # dict[docNo] = (label, prob)
        LDACoveredOutput = ri.convertOutput2('test')
        LDATrainingOutput = ri.convertOutput2('train')

        testSize = len(topicTest)
        for h in range(len(limitSet)):
            print 'train Mapping Rule...'
            (model, cand, candProb) = cm.mappingTrainer3(alchemyTrain, topicTrain)

            trueTrainLabels = []
            for labels in topicTrain:
                trueTrainLabels.append(labels.split(' '))
            mappingTrainOutput = cm.mappingInfer3(model, cand, candProb, alchemyTrain)
            # dict[docNo] = (LDAProb, mappingProb, class)
            SVMTrainData = {}
            svmTrainingFile = open('testDetailedOutput\\'+brand+'.svmTrain', 'w')
            svmInferenceFile = open('testDetailedOutput\\'+brand+'.svmInfer', 'w')
            classAssign_disagree = []
            URL_disagree = []
            hash_disagree = []
            LDAProbList_disagree = []
            mappingProbList_disagree = []
            higherClass_disagree = []

            for i in range(len(mappingTrainOutput)):
                trueLabels = ''
                for label in trueTrainLabels[i]:
                    trueLabels += label+' '
                #disagree
                if (i in LDATrainingOutput) and (LDATrainingOutput[i][0] != mappingTrainOutput[i][0]) and (mappingTrainOutput[i][1] != -1.0):
                    #LDA -> 0   Mapping -> 1
                    if mappingTrainOutput[i][0] == cand:
                        sameAsCandFlag = 0
                    else:
                        sameAsCandFlag = 1
                    # both are correct
                    if (LDATrainingOutput[i][0] in trueTrainLabels[i]) and (mappingTrainOutput[i][0] in trueTrainLabels[i]):
                        svmTrainingFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t' + mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t2\t'+trueLabels+'\n')
                    # only one of them is correct
                    elif (LDATrainingOutput[i][0] in trueTrainLabels[i]) and (mappingTrainOutput[i][0] not in trueTrainLabels[i]) and (LDATrainingOutput[i][1] < LDAThreshold):
                        SVMTrainData[i] = (LDATrainingOutput[i][1], mappingTrainOutput[i][1], lenTrain[i], sameAsCandFlag, URLTrain[i], hashTrain[i], 0)
                        svmTrainingFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t' + mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t0\t'+trueLabels+'\n')
                        URL_disagree.append(URLTrain[i])
                        hash_disagree.append(hashTrain[i])
                        LDAProbList_disagree.append(LDATrainingOutput[i][1])
                        mappingProbList_disagree.append(mappingTrainOutput[i][1])
                        if LDATrainingOutput[i][1] >= mappingTrainOutput[i][1]:
                            higherClass_disagree.append(0.0)
                        else:
                            higherClass_disagree.append(1.0)
                        classAssign_disagree.append(0.0)
                    elif (mappingTrainOutput[i][0] in trueTrainLabels[i]) and (LDATrainingOutput[i][0] not in trueTrainLabels[i]) and (LDATrainingOutput[i][1] < LDAThreshold):
                        SVMTrainData[i] = (LDATrainingOutput[i][1], mappingTrainOutput[i][1], lenTrain[i], sameAsCandFlag, URLTrain[i], hashTrain[i], 1)
                        svmTrainingFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t' + mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t1\t'+trueLabels+'\n')
                        URL_disagree.append(URLTrain[i])
                        hash_disagree.append(hashTrain[i])
                        LDAProbList_disagree.append(LDATrainingOutput[i][1])
                        mappingProbList_disagree.append(mappingTrainOutput[i][1])
                        if LDATrainingOutput[i][1] >= mappingTrainOutput[i][1]:
                            higherClass_disagree.append(0.0)
                        else:
                            higherClass_disagree.append(1.0)
                        classAssign_disagree.append(1.0)
            svmTrainingFile.close()
            featureSet = []
            labelSet = []
            for (LDAProb, mappingProb, docLen, sameFlag, URL, hashtag, classNo) in SVMTrainData.values():
                featureSet.append([LDAProb, mappingProb])
                labelSet.append(classNo)

            CC1_disagree = numpy.corrcoef(LDAProbList_disagree, mappingProbList_disagree)[0, 1]
            CC2_disagree = numpy.corrcoef(higherClass_disagree, classAssign_disagree)[0, 1]

            #CCURL_disagree = numpy.corrcoef(URL_disagree, classAssign_disagree)[0, 1]
            #CChash_disagree = numpy.corrcoef(hash_disagree, classAssign_disagree)[0, 1]

            #featureSet_scale = preprocessing.scale(featureSet)
            #scaler = preprocessing.StandardScaler().fit(featureSet_scale)

            # decision tree
            #clf = tree.DecisionTreeClassifier()
            #clf = clf.fit(featureSet, labelSet)
            #LDAC
            #ldac = mlpy.LDAC()
            #ldac.learn(featureSet, labelSet)
            # linear regression
            #regr = linear_model.LinearRegression()
            #regr.fit(featureSet, labelSet)
            # SVM
            svmModel = svm.SVC()
            svmModel.fit(featureSet, labelSet)
            # naive baysian
            #nbModel = GaussianNB()
            #nbModel.fit(featureSet, labelSet)

            mappingOutput = cm.mappingInfer3(model, cand, candProb, alchemyTest)
            sampleLabelsFile = open('TMT\\LDAFormatTest.csv', 'r')
            sampleLabels = []
            for line in sampleLabelsFile:
                seg = line.strip().split('","')
                labels = seg[0][1:].split(' ')
                sampleLabels.append(labels)
            sampleLabelsFile.close()

            correct = 0.0
            for i in range(testSize):
                if i in LDACoveredOutput and i in mappingOutput:
                    if LDACoveredOutput[i][0] == mappingOutput[i][0]:
                        # when they agree
                        out = LDACoveredOutput[i][0]
                    else:
                        # disagreed
                        if mappingOutput[i][0] == cand:
                            sameAsCandFlag = 0
                        else:
                            sameAsCandFlag = 1

                        if LDACoveredOutput[i][1] >= LDAThreshold:
                            out = LDACoveredOutput[i][0]
                        else:
                            #testFeatureSet_scale = scaler.transform([LDACoveredOutput[i][1], mappingOutput[i][1]])
                            testFeatureSet = [LDACoveredOutput[i][1], mappingOutput[i][1]]
                            #classLabel = ldac.pred(testFeatureSet)
                            #classLabel = clf.predict(testFeatureSet)[0]
                            #classLabel = regr.predict(testFeatureSet)
                            classLabel = svmModel.predict(testFeatureSet)[0]
                            #classLabel = nbModel.predict([LDACoveredOutput[i][1], mappingOutput[i][1]])
                            if classLabel == 0:
                                out = LDACoveredOutput[i][0]
                                svmInferenceFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t0\n')
                            else:
                                out = mappingOutput[i][0]
                                svmInferenceFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t1\n')
                else:
                    if i not in LDACoveredOutput:
                        out = mappingOutput[i][0]
                if out in sampleLabels[i]:
                    correct += 1.0
            svmInferenceFile.close()
            accuracySet[h] += correct/i
    print brand
    print len(topicCorpus.keys())
    for g in range(len(limitSet)):
        print 'limit: '+str(limitSet[g])
        print CC1_disagree
        print CC2_disagree
        print str(accuracySet[g] / fold)+'\n'