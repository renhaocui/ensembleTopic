import modelUtility
from sklearn.feature_extraction.text import *
from sklearn import cross_validation
import individualModels
import ensembleBaselines
import LLDATopicModeling
import json
import alchemyMapping_TopicModeling

def arrayToStr(inputArray):
    output = ''
    for item in inputArray:
        output = output + str(item)+','
    return output[:-1]

def transProb(inputDict):
    outputDict = {}
    for num, item in inputDict.items():
        tempDict = {}
        for labelProbs in item.values():
            for label, prob in labelProbs.items():
                tempDict[label] = prob
        outputDict[num] = tempDict
    return outputDict

def main(brandList=['Elmers'], iniModelList=['MaxEnt'], ensModelList=['RandomForest'], trainProbFlag=False):
    resultFile = open('HybridData/Experiment/result', 'w')
    for brand in brandList:
        print brand
        docContent, keywordLabels, candLabel, alchemyLabels = modelUtility.readData3(
            'HybridData/Original/' + brand + '.content', 'HybridData/Original/' + brand + '.keyword',
            'HybridData/Original/' + brand + '.alchemy')

        vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 1), min_df=2, stop_words='english')
        features = vectorizer.fit_transform(docContent)

        kFold = cross_validation.KFold(n=len(docContent), n_folds=5, shuffle=True)

        trainIndexFile = open('HybridData/Experiment/TrainIndex/'+brand+'.train', 'w')
        testIndexFile = open('HybridData/Experiment/TestIndex/'+brand+'.test', 'w')

        accuracySumList = {}
        for model in iniModelList:
            accuracySumList[model] = 0.0
        for model in ensModelList:
            accuracySumList[model] = 0.0

        for fold, (train_index, test_index) in enumerate(kFold):
            print fold
            trainIndexFile.write(arrayToStr(train_index)+'\n')
            testIndexFile.write(arrayToStr(test_index)+'\n')
            trainIndexFile.flush()
            testIndexFile.flush()

            trainLabelFile = open('../Experiment/Labels/Train/'+brand+'.'+str(fold), 'w')
            testLabelFile = open('../Experiment/Labels/Test/'+brand+'.'+str(fold), 'w')

            feature_train = features[train_index]
            feature_test = features[test_index]
            doc_train = []
            doc_test = []
            keyword_train = []
            keyword_test = []
            alchemy_train = []
            alchemy_test = []
            for index in train_index:
                doc_train.append(docContent[index])
                keyword_train.append(keywordLabels[index])
                alchemy_train.append(alchemyLabels[index])
            for index in test_index:
                doc_test.append(docContent[index])
                keyword_test.append(keywordLabels[index])
                alchemy_test.append(alchemyLabels[index])

            for label in keyword_train:
                trainLabelFile.write(label+'\n')
            for label in keyword_test:
                testLabelFile.write(label+'\n')
            trainLabelFile.close()
            testLabelFile.close()

            print 'running individual models...'

            for model in iniModelList:
                probFile = open('../Experiment/ProbData/'+brand+'/'+model+'prob.'+str(fold), 'w')
                probTrainFile = open('../Experiment/ProbData/'+brand+'/'+model+'probTrain.'+str(fold), 'w')

                if model == 'LLDA':
                    accuracy, output, trainOutput = LLDATopicModeling.LLDATrainInfer(doc_train, keyword_train, doc_test, keyword_test, candLabel, trainProbFlag)
                elif model == 'Alchemy':
                    accuracy, output, trainOutput = alchemyMapping_TopicModeling.alchemyTrainInfer(alchemy_train, alchemy_test, keyword_train, keyword_test, trainProbFlag)
                else:
                    accuracy, output, trainOutput = individualModels.trainInfer(feature_train, keyword_train, feature_test, keyword_test, model, trainProbFlag)
                accuracySumList[model] += accuracy
                print model + ': ' + str(accuracy)

                # {lineNum: {topic: prob}}
                probFile.write(json.dumps(transProb(output)))
                probTrainFile.write(json.dumps(transProb(trainOutput)))
                probFile.close()
                probTrainFile.close()

            print 'running ensemble baselines...'
            for model in ensModelList:
                accuracy = ensembleBaselines.trainInfer(feature_train, keyword_train, feature_test, keyword_test, model)
                accuracySumList[model] += accuracy
                print model + ': ' + str(accuracy)

        trainIndexFile.close()
        testIndexFile.close()

        for model, sumValue in accuracySumList.items():
            resultFile.write(brand+'\t'+model+'\t'+str(sumValue/5.0))
            resultFile.write('\n')
            resultFile.flush()

    resultFile.close()


brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']
iniModelList = ['NaiveBayes', 'SVM', 'MaxEnt', 'LLDA', 'Alchemy']
ensModelList = ['RandomForest', 'AdaBoost']

if __name__ == "__main__":
    main(brandList=brandList, iniModelList=iniModelList, ensModelList=ensModelList, trainProbFlag=True)