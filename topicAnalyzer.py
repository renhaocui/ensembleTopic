

def analyzer(brand):
    resultFile = open('HybridData/Experiment/topicDist.result', 'a')
    topicCorpus = {}
    for fold in range(5):
        trainLabelFile = open('../Experiment/Labels/Train/' + brand + '.' + str(fold), 'w')
        testLabelFile = open('../Experiment/Labels/Test/' + brand + '.' + str(fold), 'w')
        for line in trainLabelFile:
            topic = line.strip()
            if topic not in topicCorpus:
                topicCorpus[topic] = 1.0
            else:
                topicCorpus[topic] += 1.0
        trainLabelFile.close()

        for line in testLabelFile:
            topic = line.strip()
            if topic not in topicCorpus:
                topicCorpus[topic] = 1.0
            else:
                topicCorpus[topic] += 1.0
        testLabelFile.close()

    resultFile.write(brand+'\n')
    total = sum(topicCorpus.values())
    for topic, count in topicCorpus.items():
        resultFile.write(topic+'\t'+str(count/total))

    resultFile.write('\n')
    resultFile.close()

if __name__ == "__main__":
    brandList = ['Elmers', 'Chilis', 'Dominos', 'Triclosan', 'TriclosanV', 'BathAndBodyWorks', 'POCruisesAustraliaV']
    for brand in brandList:
        analyzer(brand)