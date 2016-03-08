# -*- coding: utf-8 -*-
__author__ = 'renhao.cui'

from calais import Calais

brand = 'BathAndBodyWorks'
startIndex = 0

if startIndex > 0:
    outputFile = open('openCalais\\'+brand+'.openCalais', 'a')
else:
    outputFile = open('openCalais\\'+brand+'.openCalais', 'w')
contentFile = open('openCalais\\'+brand+'.content', 'r')


API_KEY = "a9gvpqrvzvxt5vx8upgw2pyf"
calais = Calais(API_KEY, submitter="python-calais topicGenerator")

index = 0
for line in contentFile:
    if index < startIndex:
        continue
    print index
    content = line.strip()
    try:
        result = calais.analyze(content)
        response = result.simplified_response
        if 'topics' in response.keys():
            output = ''
            for item in response['topics']:
                output = output + item['categoryName'].replace(' ', '_') + ' '
            outputFile.write(str(index)+' '+output+'\n')
        else:
            outputFile.write(str(index)+' ERROR\n')
        outputFile.flush()
    except:
        print('Error in calling openCalais')
    index += 1

contentFile.close()
outputFile.close()