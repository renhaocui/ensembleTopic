__author__ = 'rencui'

fold = 5
brandList = ['Elmers', 'Chilis', 'BathAndBodyWorks', 'Dominos', 'Triclosan']

for brand in brandList:
    print brand
    docFile = open('Hybrid\\' + brand + '.content', 'r')
    docContent = []

    for line in docFile:
        docContent.append(line.strip())
    docFile.close()

    size = len(docContent)
    for j in range(fold):
        contentFile = open('contentOutput\\'+brand+'.'+str(j), 'w')
        for i in range(size):
            if i % fold == j:
                contentFile.write(docContent[i]+'\n')

        contentFile.close()
