__author__ = 'rencui'
import operator

fold = 5
brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']

def listToString(inputList):
    out = ''
    for item in inputList:
        out += item + ' '
    return out.strip()

for brand in brandList:
    print brand
    content = []
    LLDA = []
    true = []
    mapping = []
    maxEnt = []

    for j in range(fold):
        print j
        contentFile = open('contentOutput//'+brand+'.'+str(j), 'r')
        LLDAoutputFile = open('LLDAoutput//' + brand + '.' + str(j)+',0.0', 'r')
        trueLabelFile = open('trueLabel//'+brand+'.'+str(j), 'r')
        AlchemyOutputFile = open('AlchemyOutput//' + brand + '.' + str(j), 'r')
        MaxEntOutputFile = open('MaxEntoutput//' + brand + '.' + str(j)+',0.0', 'r')

        for line in contentFile:
            content.append(line.strip())
        contentFile.close()

        for line in trueLabelFile:
            true.append(line.strip().split(' '))
        trueLabelFile.close()

        for line in LLDAoutputFile:
            seg = line.strip().split('\t')
            LLDA.append(seg[0].split(':')[0])
        LLDAoutputFile.close()

        for line in MaxEntOutputFile:
            temp = {}
            seg = line.strip().split('\t')
            for item in seg:
                tt = item.split(':')
                temp[tt[0]] = float(tt[1])
            sorted_temp = sorted(temp.items(), key=operator.itemgetter(1))
            sorted_temp.reverse()
            maxEnt.append(sorted_temp[0][0])
        MaxEntOutputFile.close()

        for line in AlchemyOutputFile:
            seg = line.strip().split('\t')
            mapping.append(seg[0].split(':')[0])
        AlchemyOutputFile.close()

    outputFile = open('caseStudy\\'+brand, 'w')
    for i in range(len(content)):
        if LLDA[i] not in true[i]:
            out = content[i] + '\t' + LLDA[i] + '\t' + listToString(true[i]) + '\n'
            outputFile.write(out)
    outputFile.close()