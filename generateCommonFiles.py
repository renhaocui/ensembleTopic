__author__ = 'renhao.cui'

def listToString(topics):
    output = ''
    for item in topics:
        output = output + item + ' '
    return output

brand = 'Dominos'

alchemyFlag = True
openCalaisFlag = False

keywordTopicFile = open('keywordData\\' + brand + '.keyword', 'r')
keywordCommonFile = open('topicData\\' + brand + '.keyword', 'w')
contentFile = open('keywordData\\' + brand + '.content', 'r')
newContentFile = open('topicData\\' + brand + '.content', 'w')

keywordTopic = []
commonTopic = []
commonIndex = []
keywordCommonList = []
contentList = []
contentCommonList = []

for line in contentFile:
    contentList.append(line.strip())
contentFile.close()

for line in keywordTopicFile:
    topics = line.strip().split(' ')
    keywordTopic.append(topics)
keywordTopicFile.close()

removeList = []
for i in range(len(keywordTopic)):
    if 'Fandago_"Check-In_to_Win"' in keywordTopic[i]:
        removeList.append(i)

if alchemyFlag:
    alchemyTopicFile = open('alchemyData\\' + brand + '.alchemy', 'r')
    alchemyCommonFile = open('topicData\\' + brand + '.alchemy', 'w')
    alchemyTopic = {}
    alchemyCommonList = []
    for line in alchemyTopicFile:
        if line.strip() == '':
            continue
        ele = line.strip().split(' ')
        index = int(ele[0])
        topics = ele[1:]
        if len(topics) > 0 and topics[0] != 'ERROR' and index not in removeList:
            commonIndex.append(index)
            alchemyTopic[index] = topics
    alchemyTopicFile.close()
print len(commonIndex)
'''
if openCalaisFlag:
    calaisTopicFile = open('openCalais\\' + brand + '.openCalais', 'r')
    calaisCommonFile = open('topicData\\' + brand + '.openCalais', 'w')
    calaisTopic = {}
    calaisCommonList = []
    i = 0
    for line in calaisTopicFile:
        ele = line.strip().split(' ')
        index = ele[0]
        topics = ele[1:]
        if len(topics) > 0:
            if topics[0] != 'ERROR':
                calaisTopic[int(index)] = topics
        i += 1
    calaisTopicFile.close()
'''
for i in range(len(keywordTopic)):
    # manually change this one
    if i in commonIndex:  # and i in calaisTopic.keys():
        keywordCommonList.append(keywordTopic[i])
        contentCommonList.append(contentList[i])
        if alchemyFlag:
            alchemyCommonList.append(alchemyTopic[i])
            '''
        if openCalaisFlag:
            calaisCommonList.append(calaisTopic[i])
        '''

for item in keywordCommonList:
    keywordCommonFile.write(listToString(item) + '\n')
keywordCommonFile.close()

for line in contentCommonList:
    newContentFile.write(line+'\n')

if alchemyFlag:
    for item in alchemyCommonList:
        alchemyCommonFile.write(listToString(item) + '\n')
    alchemyCommonFile.close()
'''
if openCalaisFlag:
    for item in calaisCommonList:
        calaisCommonFile.write(listToString(item) + '\n')
    calaisCommonFile.close()
'''