import random

__author__ = 'rencui'


brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks']
randomSize = 2000


for brand in brandList:

    docFile = open('Hybrid\\' + brand + '.content', 'r')
    topicFile = open('Hybrid\\' + brand + '.keyword', 'r')
    alchemyFile = open('Hybrid\\' + brand + '.alchemy', 'r')

    docOutFile = open('Sample\\' + brand + '.content', 'w')
    topicOutFile = open('Sample\\' + brand + '.keyword', 'w')
    alchemyOutFile = open('Sample\\' + brand + '.alchemy', 'w')

    docList = []
    topicList = []
    alchemyList = []

    for line in docFile:
        docList.append(line.strip())

    for line in topicFile:
        topicList.append(line.strip())

    for line in alchemyFile:
        alchemyList.append(line.strip())

    docFile.close()
    topicFile.close()
    alchemyFile.close()

    size = len(docList)
    randomList = []

    while True:
        if len(randomList) == randomSize:
            break
        else:
            num = random.randint(0, size-1)
            if num not in randomList:
                randomList.append(num)

    for i in randomList:
        docOutFile.write(docList[i]+'\n')
        topicOutFile.write(topicList[i]+'\n')
        alchemyOutFile.write(alchemyList[i]+'\n')

    docOutFile.close()
    topicOutFile.close()
    alchemyOutFile.close()

