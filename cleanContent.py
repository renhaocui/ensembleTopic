import re

__author__ = 'renhao.cui'

brand = 'Dominos'
puncList = ''' !()-[]{};:'"\,<>./?@#$%^&*_~'''

inputContentFile = open('keywordData\\'+brand+'.content', 'r')
outputContentFile = open('keywordData\\'+brand+'.cleanContent', 'w')

def shrinkPuncuation(input):
    input = re.sub('\.+', '.', input)
    input = re.sub(',+', ',', input)
    input = re.sub(' +', ' ', input)
    input = re.sub('=+', '=', input)
    input = re.sub('-+', '-', input)
    input = re.sub('_+', '_', input)
    input = re.sub(' +', ' ', input)
    return input

def cleanHead(input):
    size = len(input)
    for i in range(size):
        if input[0] in puncList:
            input = input[1:]
        else:
            break
    return input

for line in inputContentFile:
    content = unicode(line.strip(), 'ascii', 'ignore')
    content = content.replace('"', "'")
    content = cleanHead(content)
    content = content.replace('@', '')
    content = shrinkPuncuation(content)
    outputContentFile.write(content+'\n')

inputContentFile.close()
outputContentFile.close()