#!/usr/bin/python

import re
import sys
import subprocess
import os


def wordGen():
    #print "Creating word api's data..."

    #fread = open("/WikiXMLOutputFiles/getPlainTextById.txt", "r")

    #fgetWordsByPageId = open("/wiki/getWordsByPageId.txt", "w")

    fgetWordsByPageId = '/words/getWordsByPageId/getWordsByPageId.txt' + os.getenv('mapred_task_id')
    fgetWordsByPageIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetWordsByPageId], stdin=subprocess.PIPE)

    # To store the list of pages with frequency
    oldList = []

    wordDic = {}

    pageDic = {}

    idLine = True
    #for line in fread:
    for line in sys.stdin:
        sect = line.split("\t")
        id = sect[0].strip()
        pageDic.clear()
        pattern = re.compile("[^\w']|_")
        sect[1] = pattern.sub(' ', sect[1])
        words = sect[1].split()
        for word in words:
            word = word.lower()
            if word.isalpha():
                if not pageDic.has_key(word):
                    pageDic[word] = 1
                else:
                    pageDic[word] = pageDic[word] + 1

                if not wordDic.has_key(word):
                    newList = [1, id]
                    wordDic[word] = newList

                else:
                    oldList = (wordDic.get(word))
                    oldList[0] = oldList[0] + 1

                    if id not in oldList:
                        oldList.append(id)

                    wordDic[word] = oldList

        #fgetWordsByPageId.write(id + "\t")
        fgetWordsByPageIdProc.stdin.write(id + "\t")

        count = len(pageDic)
        for x in range(count):
            word = pageDic.keys()[x]
            value = word + " " + str(pageDic[word])
            #fgetWordsByPageId.write(value)
            fgetWordsByPageIdProc.stdin.write(value)
            if x != count - 1:
                #fgetWordsByPageId.write(",")
                fgetWordsByPageIdProc.stdin.write(",")
        #fgetWordsByPageId.write("\n")
        fgetWordsByPageIdProc.stdin.write("\n")

    #fread.close()

    #fcheckWord = open("/wiki/checkWord.txt", "w")

    fcheckWord = '/words/checkWord/checkWord.txt' + os.getenv('mapred_task_id')
    fcheckWordProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fcheckWord], stdin=subprocess.PIPE)

    #fgetIdByWord = open("/wiki/getIdByWord.txt", "w")

    fgetIdByWord = '/words/getIdByWord/getIdByWord.txt' + os.getenv('mapred_task_id')
    fgetIdByWordProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetIdByWord], stdin=subprocess.PIPE)

    #fgetWordById = open("/words/getWordById.txt", "w")

    fgetWordById = '/words/getWordById/getWordById.txt' + os.getenv('mapred_task_id')
    fgetWordByIdProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetWordById], stdin=subprocess.PIPE)

    #ffrequencyCount = open("/wiki/frequencyCount.txt", "w")

    ffrequencyCount = '/words/frequencyCount/frequencyCount.txt' + os.getenv('mapred_task_id')
    ffrequencyCountProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', ffrequencyCount], stdin=subprocess.PIPE)

    #fgetNoOfPagesContainsTheWord = open("/wiki/getNoOfPagesContainsTheWord.txt", "w")

    fgetNoOfPagesContainsTheWord = '/words/getNoOfPagesContainsTheWord/getNoOfPagesContainsTheWord.txt' + os.getenv('mapred_task_id')
    fgetNoOfPagesContainsTheWordProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetNoOfPagesContainsTheWord], stdin=subprocess.PIPE)

    #fgetListOfPagesContainsTheWord = open("/wiki/getListOfPagesContainsTheWord.txt", "w")

    fgetListOfPagesContainsTheWord = '/words/getListOfPagesContainsTheWord/getListOfPagesContainsTheWord.txt' + os.getenv('mapred_task_id')
    fgetListOfPagesContainsTheWordProc = subprocess.Popen(['hadoop', 'fs', '-put', '-', fgetListOfPagesContainsTheWord],
                                                        stdin=subprocess.PIPE)

    i = 0
    for key in sorted(wordDic.keys()):

        count = len(wordDic[key])  # number of pages

        #fcheckWord.write(key + "\ttrue\n")
        fcheckWordProc.stdin.write(key + "\ttrue\n")
        #fgetIdByWord.write(key + "\t" + str(i) + "\n")
        fgetIdByWordProc.stdin.write(key + "\t" + str(i) + "\n")
        #fgetWordById.write(str(i) + "\t" + key + "\n")
        fgetWordByIdProc.stdin.write(str(i) + "\t" + key + "\n")
        #ffrequencyCount.write(key + "\t" + str(wordDic[key][0]) + "\n")
        ffrequencyCountProc.stdin.write(key + "\t" + str(wordDic[key][0]) + "\n")
        #fgetNoOfPagesContainsTheWord.write(key + "\t" + str(count - 1) + "\n")
        fgetNoOfPagesContainsTheWordProc.stdin.write(key + "\t" + str(count - 1) + "\n")
        #fgetListOfPagesContainsTheWord.write(key + "\t")
        fgetListOfPagesContainsTheWordProc.stdin.write(key + "\t")

        for x in range(1, count):
            #fgetListOfPagesContainsTheWord.write(str(wordDic[key][x]))
            fgetListOfPagesContainsTheWordProc.stdin.write(str(wordDic[key][x]))
            if x != count - 1:
                #fgetListOfPagesContainsTheWord.write(",")
                fgetListOfPagesContainsTheWordProc.stdin.write(",")
        #fgetListOfPagesContainsTheWord.write("\n")
        fgetListOfPagesContainsTheWordProc.stdin.write("\n")

        i = i + 1

    del wordDic

    '''fcheckWord.flush()
    fgetIdByWord.flush()
    fgetWordById.flush()
    ffrequencyCount.flush()
    fgetNoOfPagesContainsTheWord.flush()
    fgetListOfPagesContainsTheWord.flush()'''

    fcheckWordProc.stdin.close()
    fgetIdByWordProc.stdin.close()
    fgetWordByIdProc.stdin.close()
    ffrequencyCountProc.stdin.close()
    fgetNoOfPagesContainsTheWordProc.stdin.close()
    fgetListOfPagesContainsTheWordProc.stdin.close()

    #print "Done"


if __name__ == '__main__':
    wordGen()
