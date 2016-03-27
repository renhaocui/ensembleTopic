import json
import os

brandList = ['Triclosan']

for brand in brandList:
    print brand
    contentFile = open('testData/'+brand+'.content', 'w')
    labelFile = open('testData/'+brand+'.keyword', 'w')
    brandData = {}
    path = 'userVerified/'+brand+'/'
    listing = os.listdir(path)
    for file in listing:
        if file.endswith('.txt'):
            inputFile = open(path+file, 'r')
            for line in inputFile:
                temp = json.loads(line.strip())
                for tweet in temp:
                    brandData[tweet['id']] = (tweet['content'], tweet['topics'])
            inputFile.close()

    for (content, topics) in brandData.values():
        label = ''
        for topic in topics:
            label += topic.replace(' ', '_')+' '
        labelFile.write(label+'\n')
        contentFile.write()

    contentFile.close()
    labelFile.close()
    print len(brandData.keys())
