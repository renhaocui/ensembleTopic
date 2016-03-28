import json
import os
import re
from langdetect import detect

__author__ = 'renhao.cui'

brand = 'TriclosanV'

puncList = ''' !()-[]{};:'"\,<>./?@#$%^&*_~'''

def extractLinks(input):
    urls = re.findall("(?P<url>https?://[^\s]+)", input)
    if len(urls) != 0:
        for url in urls:
            input = input.replace(url, '<URL>')
    return input

def removeUsername(input):
    users = re.findall(r'@(\w+)', input)
    if len(users) != 0:
        for user in users:
            input = input.replace(user, '')
            input = input.replace('RT @', '')
            input = input.replace('@', '')
    return input

def shrinkPuncuation(input):
    input = re.sub('\.+', '.', input)
    input = re.sub(',+', ',', input)
    input = re.sub(' +', ' ', input)
    input = re.sub('=+', '=', input)
    input = re.sub('-+', '-', input)
    input = re.sub('_+', '_', input)
    return input

def cleanHead(input):
    size = len(input)
    for i in range(size):
        if input[0] in puncList:
            input = input[1:]
        else:
            break
    return input

outputContentFile = open('HybridData/Original/'+brand+'.content', 'w')
outputLabelFile = open('HybridData/Original/'+brand+'.keyword', 'w')
#nonTopicFile = open('supportData\\'+brand+'.nonTopic', 'w')

path = 'userVerified/'+brand

tweets = {}
nonTopicTweets = []

listing = os.listdir(path)

size = len(listing)

index = 1

for file in listing:
    print('processing file: ' + str(index))

    inputFile = open(path + '/' + file, 'r')
    line = inputFile.readline()
    data = json.loads(line.strip())
    for item in data:
        string = item['content'].replace('\n', '')
        string = string.replace('\r', '')
        string = extractLinks(string)
        string = removeUsername(string)
        string = shrinkPuncuation(string)
        string = string.replace('"', "'")

        topic = item['topics']

        if len(topic) > 0 and len(string) > 10:
            try:
                if detect(string) == 'en':
                    if string not in tweets.keys():
                        tweets[string] = topic
            except:
                print('error in language detection for tweet: ' + string)
        '''
        if len(topic) == 0 and len(nonTopicTweets) <= 10000 and len(string) > 10:
            try:
                if detect(string) == 'en':
                    if string not in nonTopicTweets:
                        nonTopicTweets.append(string)
                        nonTopicFile.write(string.encode('utf-8') + '\n')
                        nonTopicFile.flush()
            except:
                print('error in language detection for tweet: ' + string)
        '''
    index += 1
    inputFile.close()

for (key, value) in tweets.items():
    outputContentFile.write(key.decode('ascii', 'ignore').encode("ascii") + '\n')
    output = ''
    for item in value:
        temp = item.replace(' ', '_')
        output = output+temp.replace("'", '') + ' '
    outputLabelFile.write(output + '\n')

outputContentFile.close()
outputLabelFile.close()
#nonTopicFile.close()