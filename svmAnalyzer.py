__author__ = 'renhao.cui'
from sklearn import svm

brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']

for brand in brandList:
    svmInferFile = open('testDetailedOutput\\'+brand+'.svmInfer', 'r')
    svmTrainFile = open('testDetailedOutput\\'+brand+'.svmTrain', 'r')
    LDAFile = open('testDetailedOutput\\'+brand+'.LDAformat', 'r')
    outputFile = open('testDetailedOutput\\'+brand+'.svmAnalyze', 'w')

    content = {}
    trueLabel = {}
    svmTrain = {}
    svmInfer = {}

    index = 0
    for line in LDAFile:
        seg = line.strip()[1:-1].split('","')
        content[index] = seg[1]
        trueLabel[index] = seg[0].split(' ')
        index += 1
    LDAFile.close()

    index = 0
    for line in svmTrainFile:
        try:
            seg = line.strip().split('\t')
            temp = {}
            temp['LDA'] = (seg[1], float(seg[2]))
            temp['Map'] = (seg[3], float(seg[4]))
            temp['Out'] = int(seg[5])
            svmTrain[index] = temp
            index += 1
        except:
            print 'Error'
            index += 1
    svmTrainFile.close()

    index = 0
    for line in svmInferFile:
        try:
            seg = line.strip().split('\t')
            temp = {}
            temp['LDA'] = (seg[1], float(seg[2]))
            temp['Map'] = (seg[3], float(seg[4]))
            temp['Out'] = int(seg[5])
            svmInfer[index] = temp
            index += 1
        except:
            print 'Error'
            index += 1
    svmInferFile.close()

    # analyze on training data
    LDAcount = 0.0
    largerCorrect = 0.0
    total = 0.0
    for (index, value) in svmTrain.items():
        if value['Out'] == 0:
            LDAcount += 1.0
        if value['LDA'][1] >= value['Map'][1]:
            if value['Out'] == 0:
                largerCorrect += 1.0
        else:
            if value['Out'] == 1:
                largerCorrect += 1.0
        total += 1.0
    print '\n'+brand
    print 'For training data, choice of larger item: '+str(largerCorrect*100/total)
    print 'LDA percentage: '+str(LDAcount*100/total)

    # analyze on inference data
    LDAcount = 0.0
    total = 0.0
    correct = 0.0
    largerCorrect = 0.0
    for (index, value) in svmInfer.items():
        if value['Out'] == 0:
            LDAcount += 1.0
            if value['LDA'][0] in trueLabel[index]:
                correct += 1.0
        else:
            if value['Map'][0] in trueLabel[index]:
                correct += 1.0
        if value['LDA'][1] >= value['Map'][1]:
            if value['Out'] == 0:
                largerCorrect += 1.0
        else:
            if value['Out'] == 1:
                largerCorrect += 1.0
        labels = ''
        for label in trueLabel[index]:
            labels += label+' '
        outputFile.write(str(index)+'\t'+content[index]+'\t'+labels+'\t'+value['LDA'][0]+'\t'+str(value['LDA'][1])+'\t'+value['Map'][0]+'\t'+str(value['Map'][1])+'\t'+str(value['Out'])+'\n')
        total += 1.0

    print 'For inference data, choice of larger item: '+str(largerCorrect*100/total)
    print 'Correct: '+str(correct*100/total)
    print 'LDA percentage: '+str(LDAcount*100/total)

'''
# run svm classifier
print '\nSVM training...'
svmModel = svm.SVC()
featureSet = []
labelSet = []
for (index, value) in svmTrain.items():
    labelSet.append(value['Out'])
    featureSet.append([value['LDA'][1], value['Map'][1]])
svmModel.fit(featureSet, labelSet)

print 'SVM inference...'
correct = 0.0
total = 0.0
for (index, value) in svmInfer.items():
    svmClass = svmModel.predict([value['LDA'][1], value['Map'][1]])
    if svmClass[0] == 0:
        prediction = value['LDA'][0]
    else:
        prediction = value['Map'][0]
    if prediction in trueLabel[index]:
        correct += 1.0
    total += 1.0

print 'SVM classifier accuracy: '+str(correct*100/total)
'''