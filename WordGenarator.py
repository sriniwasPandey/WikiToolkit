#!/usr/bin/python

import re

def wordGen():
  
  print "Creating word api's data..."
  
  fread=open("getPlainTextById.txt","r")
  
  fgetWordsByPageId=open("getWordsByPageId.txt","w")
 
  #To store the list of pages with frequency
  oldList=[]
  
  wordDic={}

  pageDic={}
  
  idLine=True
  for line in fread:
    sect=line.split("\t")
    id=sect[0].strip()
    pageDic.clear()
    pattern=re.compile("[^\w']|_")
    sect[1] =  pattern.sub(' ', sect[1])
    words=sect[1].split()
    for word in words: 
      word=word.lower()
      if word.isalpha():
	if not pageDic.has_key(word):
	  pageDic[word]=1
	else:
	  pageDic[word]=pageDic[word]+1
	  
	if not wordDic.has_key(word):
	  newList=[1,id]
	  wordDic[word]=newList
	
	else:
	  oldList=(wordDic.get(word))
	  oldList[0]=oldList[0]+1
	  
	  if id not in oldList:
	    oldList.append(id)
	  
	  wordDic[word]=oldList

    fgetWordsByPageId.write(id+"\t")
    
    count=len(pageDic)
    for x in range(count):
      word=pageDic.keys()[x]
      value=word+" "+str(pageDic[word])
      fgetWordsByPageId.write(value)
      if x!=count-1:
	fgetWordsByPageId.write(",")
    fgetWordsByPageId.write("\n")
	
  fread.close()
  
  fcheckWord=open("checkWord.txt","w")
  fgetIdByWord=open("getIdByWord.txt","w")
  fgetWordById=open("getWordById.txt","w")
  ffrequencyCount=open("frequencyCount.txt","w")
  fgetNoOfPagesContainsTheWord=open("getNoOfPagesContainsTheWord.txt","w")
  fgetListOfPagesContainsTheWord=open("getListOfPagesContainsTheWord.txt","w")
  
  i=0
  for key in sorted(wordDic.keys()):
    
    count=len(wordDic[key])#number of pages
    
    fcheckWord.write(key+"\ttrue\n")
    fgetIdByWord.write(key+"\t"+str(i)+"\n")
    fgetWordById.write(str(i)+"\t"+key+"\n")
    ffrequencyCount.write(key+"\t"+str(wordDic[key][0])+"\n")
    fgetNoOfPagesContainsTheWord.write(key+"\t"+str(count-1)+"\n")
    fgetListOfPagesContainsTheWord.write(key+"\t")
    

    for x in range(1,count):
      fgetListOfPagesContainsTheWord.write(str(wordDic[key][x]))
      if x!=count-1:
	fgetListOfPagesContainsTheWord.write(",")
    fgetListOfPagesContainsTheWord.write("\n")
    
    i=i+1
    
    
  del wordDic
  
  fcheckWord.flush()
  fgetIdByWord.flush()
  fgetWordById.flush()
  ffrequencyCount.flush()
  fgetNoOfPagesContainsTheWord.flush()
  fgetListOfPagesContainsTheWord.flush()
  
  fcheckWord.close()
  fgetIdByWord.close()
  fgetWordById.close()
  ffrequencyCount.close()
  fgetNoOfPagesContainsTheWord.close()
  fgetListOfPagesContainsTheWord.close()
  
  print "Done"

if __name__ == '__main__':
  wordGen()
