# -*- coding: utf-8 -*-
from __future__ import print_function
from alchemyapi import AlchemyAPI

brand = 'BathAndBodyWorks'
startIndex = 33001
stopIndex = 60000

if startIndex > 0:
    outputAlchemyFile = open('alchemyData\\'+brand+'.alchemy', 'a')
else:
    outputAlchemyFile = open('alchemyData\\'+brand+'.alchemy', 'w')
contentFile = open('alchemyData\\'+brand+'.content', 'r')
content = []

alchemyapi = AlchemyAPI()

for line in contentFile:
    content.append(line.strip())

index = 0
for item in content:
    if index < startIndex:
        index += 1
        continue
    print(index)
    try:
        response = alchemyapi.taxonomy('text', item)
        if response['status'] == 'OK':
            output = ''
            for category in response['taxonomy']:
                output = output + category['label'].replace(' ', '_')+':'+category['score']+' '
            outputAlchemyFile.write(str(index) + ' ' + output + '\n')
        else:
            outputAlchemyFile.write(str(index) + ' ERROR\n')
    except:
        print('Error in calling Alchemy')
    index += 1
    if index > stopIndex:
        break

outputAlchemyFile.close()