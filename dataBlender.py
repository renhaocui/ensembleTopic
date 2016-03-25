import json
import os

brandList = ['Dominos', 'Triclosan']

for brand in brandList:
    print brand
    combinedOutputFile = open('testData/'+brand+'.json', 'w')
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
    combinedOutputFile.write(json.dumps(brandData))

    print len(brandData.keys())
