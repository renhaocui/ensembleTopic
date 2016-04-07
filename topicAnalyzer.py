
def analyzer(brand):
    print brand
    resultFile = open('HybridData/Experiment/TopicDist/topicDist.result', 'a')
    topicCorpus = {}
    total = 0
    topicCount = 0
    for fold in range(5):
        trainLabelFile = open('../Experiment/Labels/Train/' + brand + '.' + str(fold), 'r')
        testLabelFile = open('../Experiment/Labels/Test/' + brand + '.' + str(fold), 'r')
        for line in trainLabelFile:
            total += 1
            topic = line.strip()
            if topic not in topicCorpus:
                topicCorpus[topic] = 1.0
            else:
                topicCorpus[topic] += 1.0
        trainLabelFile.close()

        for line in testLabelFile:
            total += 1
            topic = line.strip()
            if topic not in topicCorpus:
                topicCorpus[topic] = 1.0
            else:
                topicCorpus[topic] += 1.0
        testLabelFile.close()
        topicCount += len(topicCorpus)

    print total/5
    print topicCount/5
    resultFile.write(brand+'\n')
    total = sum(topicCorpus.values())
    for topic, count in topicCorpus.items():
        resultFile.write(topic+'\t'+str(count/total)+'\n')

    resultFile.write('\n')
    resultFile.close()

if __name__ == "__main__":
    brandList = ['Elmers', 'Chilis', 'Dominos', 'Triclosan', 'TriclosanV', 'BathAndBodyWorks', 'POCruisesAustraliaV']
    for brand in brandList:
        analyzer(brand)