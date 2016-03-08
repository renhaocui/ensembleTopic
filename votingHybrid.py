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
brandList = ['Dominos', 'Triclosan']

for brand in brandList:
    limitSet = [0.0]
    precisionSet = [0.0, 0.0, 0.0]
    recallSet = [0.0, 0.0, 0.0]
    fMeasureSet = [0.0, 0.0, 0.0]
    accuracySet = [0.0, 0.0, 0.0]
    coverageSet = [0.0, 0.0, 0.0]

    docFile = open('Hybrid\\' + brand + '.content', 'r')
    topicFile = open('Hybrid\\' + brand + '.keyword', 'r')
    alchemyFile = open('Hybrid\\' + brand + '.alchemy', 'r')
    topicCorpusFile = open('LLDAdata\\topic.corpus', 'w')

    docContent = []
    topicContent = []
    topicCorpus = {}
    alchemyContent = []
    docLength = []

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
        docContent.append(line.strip())
        docLength.append(len(simpleTokenize(line.strip())))
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
        topicTrain = []
        topicTest = []
        alchemyTrain = []
        alchemyTest = []
        alchemyTestFile = open('LLDAdata\\alchemyTestData', 'w')
        for i in range(size):
            if i % fold == j:
                docTest.append(docContent[i])
                lenTest.append(docLength[i])
                topicTest.append(topicContent[i])
                alchemyTest.append(alchemyContent[i])
                alchemyTestFile.write(str(alchemyContent[i]) + '\n')
            else:
                docTrain.append(docContent[i])
                lenTrain.append(docLength[i])
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

        #test differnt configurations on generating output topics
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
            #oddProbTrainFile = open('testDetailedOutput\\'+brand+'.oddProbTrain', 'w')
            #oddProbInferFile = open('testDetailedOutput\\'+brand+'.oddProbInfer', 'w')
            #LDAProbList_agree = []
            #mappingProbList_agree = []
            #LDAProbList_disagree = []
            #mappingProbList_disagree = []
            #higherClass_disagree = []
            classAssign_disagree = []
            #len_disagree = []
            sameAsCand_disagree = []

            for i in range(len(mappingTrainOutput)):
                trueLabels = ''
                for label in trueTrainLabels[i]:
                    trueLabels += label+' '
                '''
                if i in LDATrainingOutput and LDATrainingOutput[i][1] < 0.3 and mappingTrainOutput[i][1] < 0.3:
                    if LDATrainingOutput[i][0] in trueTrainLabels[i] and mappingTrainOutput[i][0] in trueTrainLabels[i]:
                        oddProbTrainFile.write(str(i)+'\t'+docTrain[i]+'\t'+trueLabels+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t2\n')
                    elif LDATrainingOutput[i][0] in trueTrainLabels[i]:
                        oddProbTrainFile.write(str(i)+'\t'+docTrain[i]+'\t'+trueLabels+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t0\n')
                    elif mappingTrainOutput[i][0] in trueTrainLabels[i]:
                        oddProbTrainFile.write(str(i)+'\t'+docTrain[i]+'\t'+trueLabels+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t1\n')
                    else:
                        oddProbTrainFile.write(str(i)+'\t'+docTrain[i]+'\t'+trueLabels+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t3\n')
                '''
                #agree
                #if (i in LDATrainingOutput) and (LDATrainingOutput[i][0] == mappingTrainOutput[i][0]) and (mappingTrainOutput[i][1] != -1.0) and (LDATrainingOutput[i][0] in trueTrainLabels[i]):
                    #LDAProbList_agree.append(LDATrainingOutput[i][1])
                    #mappingProbList_agree.append(mappingTrainOutput[i][1])
                #disagree
                if (i in LDATrainingOutput) and (LDATrainingOutput[i][0] != mappingTrainOutput[i][0]) and (mappingTrainOutput[i][1] != -1.0):
                    #LDA -> 0   Mapping -> 1

                    #LDAProbList_disagree.append(LDATrainingOutput[i][1])
                    #mappingProbList_disagree.append(mappingTrainOutput[i][1])

                    if mappingTrainOutput[i][0] == cand:
                        sameAsCandFlag = 0
                    else:
                        sameAsCandFlag = 1

                    if (LDATrainingOutput[i][0] in trueTrainLabels[i]) and (mappingTrainOutput[i][0] in trueTrainLabels[i]):
                        svmTrainingFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t2\t'+trueLabels+'\n')
                        '''
                        if LDATrainingOutput[i][1] >= mappingTrainOutput[i][1]:
                            SVMTrainData[i] = (LDATrainingOutput[i][1], mappingTrainOutput[i][1], 0)
                            svmTrainingFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t0\t'+trueLabels+'\n')
                        else:
                            SVMTrainData[i] = (LDATrainingOutput[i][1], mappingTrainOutput[i][1], 1)
                            svmTrainingFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t1\t'+trueLabels+'\n')
                    '''
                    elif (LDATrainingOutput[i][0] in trueTrainLabels[i]) and (mappingTrainOutput[i][0] not in trueTrainLabels[i]):
                        SVMTrainData[i] = (LDATrainingOutput[i][1], mappingTrainOutput[i][1], lenTrain[i], sameAsCandFlag, 0)
                        svmTrainingFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t0\t'+trueLabels+'\n')
                        '''
                        if LDATrainingOutput[i][1] >= mappingTrainOutput[i][1]:
                            higherClass_disagree.append(0.0)
                        else:
                            higherClass_disagree.append(1.0)
                        sameAsCand_disagree.append(sameAsCandFlag)
                        '''
                        sameAsCand_disagree.append(sameAsCandFlag)
                        classAssign_disagree.append(0.0)
                    elif (mappingTrainOutput[i][0] in trueTrainLabels[i]) and (LDATrainingOutput[i][0] not in trueTrainLabels[i]):
                        SVMTrainData[i] = (LDATrainingOutput[i][1], mappingTrainOutput[i][1], lenTrain[i], sameAsCandFlag, 1)
                        svmTrainingFile.write(str(i)+'\t'+LDATrainingOutput[i][0]+'\t'+str(LDATrainingOutput[i][1])+'\t'+mappingTrainOutput[i][0]+'\t'+str(mappingTrainOutput[i][1])+'\t1\t'+trueLabels+'\n')
                        '''
                        if LDATrainingOutput[i][1] >= mappingTrainOutput[i][1]:
                            higherClass_disagree.append(0.0)
                        else:
                            higherClass_disagree.append(1.0)
                        sameAsCand_disagree.append(sameAsCandFlag)
                        '''
                        sameAsCand_disagree.append(sameAsCandFlag)
                        classAssign_disagree.append(1.0)
            svmTrainingFile.close()
            featureSet = []
            labelSet = []
            for (LDAProb, mappingProb, docLen, sameFlag, classNo) in SVMTrainData.values():
                featureSet.append([LDAProb, mappingProb, docLen, sameAsCandFlag])
                labelSet.append(classNo)

            CC_disagree = numpy.corrcoef(sameAsCand_disagree, classAssign_disagree)[0, 1]
            '''
            CC1_agree = numpy.corrcoef(LDAProbList_agree, mappingProbList_agree)[0, 1]
            CC1_disagree = numpy.corrcoef(LDAProbList_disagree, mappingProbList_disagree)[0, 1]
            CC2_disagree = numpy.corrcoef(higherClass_disagree, classAssign_disagree)[0, 1]

            CC1_agree_set = []
            for i in range(len(LDAProbList_agree)):
                CC1_agree_set.append([LDAProbList_agree[i], mappingProbList_agree[i]])
            CC1_agree_set_scale = preprocessing.scale(CC1_agree_set)
            LDAProbList_agree_scale = []
            mappingProbList_agree_scale = []
            for (LDA, mapping) in CC1_agree_set_scale:
                LDAProbList_agree_scale.append(LDA)
                mappingProbList_agree_scale.append(mapping)
            CC1_agree_scale = numpy.corrcoef(LDAProbList_agree_scale, mappingProbList_agree_scale)[0, 1]


            CC1_disagree_set = []
            for i in range(len(LDAProbList_disagree)):
                CC1_disagree_set.append([LDAProbList_disagree[i], mappingProbList_disagree[i]])
            CC1_disagree_set_scale = preprocessing.scale(CC1_disagree_set)
            LDAProbList_disagree_scale = []
            mappingProbList_disagree_scale = []
            for (LDA, mapping) in CC1_disagree_set_scale:
                LDAProbList_disagree_scale.append(LDA)
                mappingProbList_disagree_scale.append(mapping)
            CC1_disagree_scale = numpy.corrcoef(LDAProbList_disagree_scale, mappingProbList_disagree_scale)[0, 1]


            CC2_disagree_set = []
            for i in range(len(higherClass_disagree)):
                CC2_disagree_set.append([higherClass_disagree[i], classAssign_disagree[i]])
            CC2_disagree_set_scale = preprocessing.scale(CC2_disagree_set)
            higherClass_disagree_scale = []
            classAssign_disagree_scale = []
            for (higherClass, classAssign) in CC2_disagree_set_scale:
                higherClass_disagree_scale.append(higherClass)
                classAssign_disagree_scale.append(classAssign)
            CC2_disagree_scale = numpy.corrcoef(higherClass_disagree_scale, classAssign_disagree_scale)[0, 1]
            '''
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

                        if mappingOutput[i][0] == cand:
                            sameAsCandFlag = 0
                        else:
                            sameAsCandFlag = 1

                        if mappingOutput[i][1] == -1.0:
                            out += LDACoveredOutput[i][0]
                        else:
                            #testFeatureSet_scale = scaler.transform([LDACoveredOutput[i][1], mappingOutput[i][1]])
                            testFeatureSet = [LDACoveredOutput[i][1], mappingOutput[i][1], lenTest[i], sameAsCandFlag]
                            #classLabel = ldac.pred(testFeatureSet)
                            #classLabel = clf.predict(testFeatureSet)[0]
                            #classLabel = regr.predict(testFeatureSet)
                            classLabel = svmModel.predict(testFeatureSet)[0]
                            #classLabel = nbModel.predict([LDACoveredOutput[i][1], mappingOutput[i][1]])
                            if classLabel == 0:
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
            svmInferenceFile.close()
            mapLabelFile.close()
            combinedTopicFile.close()
            #Evaluate
            (tempRecall, tempPrecision, tempFmeasure, tempAccuracy, tempCoverage) = eval('hybrid')
            recallSet[h] += tempRecall
            precisionSet[h] += tempPrecision
            fMeasureSet[h] += tempFmeasure
            accuracySet[h] += tempAccuracy
            coverageSet[h] += tempCoverage

    print brand
    print len(topicCorpus.keys())
    for g in range(len(limitSet)):
        print 'limit: '+str(limitSet[g])
        print CC_disagree
        #print 'CC1_agree: '+str(CC1_agree_scale)
        #print 'CC1_disagree: '+str(CC1_disagree_scale)
        #print 'CC2_disagree: '+str(CC2_disagree_scale)
        #print str(recallSet[g] / fold)
        #print str(precisionSet[g] / fold)
        #print str(fMeasureSet[g] / fold)
        print str(accuracySet[g] / fold)
        print str(coverageSet[g] / fold) + '\n'