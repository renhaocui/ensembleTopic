__author__ = 'renhao.cui'
import utilities
from sklearn import cross_validation
import combinedMapping as cm
import modelUtility

def alchemyTrainInfer(alchemy_train, alchemy_test, label_train, label_test, trainProbFlag):
    # model from A to B: model[A] = {B: score}
    (model, cand, candProb) = cm.mappingTrainer4(alchemy_train, label_train)

    predictions = utilities.outputMappingResult3_fullList(model, cand, candProb, alchemy_test)
    predictionsTrain = {}
    if trainProbFlag:
        predictionsTrain = utilities.outputMappingResult3_fullList(model, cand, candProb, alchemy_train)

    correct = 0.0
    total = 0.0
    for index, label in enumerate(label_test):
        pred = predictions[index][1].keys()[0]
        if pred == label:
            correct += 1.0
        total += 1.0

    return correct/total, predictions, predictionsTrain


def run():
    brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']
    outputFile = open('results/alchemy.result', 'w')
    for brand in brandList:
        print brand
        topics, alchemyOutput = modelUtility.readData2('HybridData/Original/' + brand + '.keyword', 'HybridData/Original/' + brand + '.alchemy')

        accuracySum = 0.0
        for i in range(5):
            alchemy_train, alchemy_test, label_train, label_test = cross_validation.train_test_split(alchemyOutput, topics, test_size=0.2, random_state=0)

            accuracy, testOutput, trainOutput = alchemyTrainInfer(alchemy_train, alchemy_test, label_train, label_test, True)
            accuracySum += accuracy

        print accuracySum / 5
        outputFile.write(brand+'\t'+str(accuracySum/5)+'\n')

    outputFile.close()
