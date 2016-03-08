__author__ = 'rencui'

from nltk.corpus import wordnet as wn
from tokenizer import simpleTokenize
import string

def genSyn(word):
    outputList = []
    syns = wn.synsets('huge')
    for item in syns:
        for token in item.lemmas():
            name = token.name()
            if name != word:
                outputList.append(name)

    return outputList

def coOccur(tweet, target, length):
    exclude = set(string.punctuation)
    words = simpleTokenize(tweet)
    wordList = []
    if target not in words:
        return 'null'
    else:
        for word in words:
            if word[0] not in exclude:
                wordList.append(word)
        index = wordList.index(target)
        start = max(0, index - length)
        end = min(index + length, len(wordList)-1)
        return wordList[start:index]+wordList[index+1:end+1]

def wordSimilarity(word1, word2):
    scoreList = []
    synList1 = wn.synsets(word1, pos='n')
    synList2 = wn.synsets(word2, pos='n')
    if len(synList1) == 0 or len(synList2) == 0:
        return -1
    for syn1 in synList1:
        for syn2 in synList2:
            scoreList.append(wn.wup_similarity(syn1, syn2))
    return max(scoreList)

def phraseSimilarity(phr1, phr2):
    scoreList = []
    words1 = phr1.split('_')
    words2 = phr2.split('_')
    for word1 in words1:
        for word2 in words2:
            scoreList.append(wordSimilarity(word1, word2))
    return max(scoreList)
