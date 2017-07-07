#!/usr/bin/python
import os


#title-id dictionary
idTitleDic={}
titleIdDic={}



#To create page title-id dictionary

def setPageDic():
  global titleIdDic, idTitleDic
  
  fread=open("getPageTitleById.txt","r")
  
  for line in fread:
    word=line.split()
    #print word
    try:
      titleIdDic[word[1]]=word[0]
      idTitleDic[word[0]]=word[1]
    except:
      pass


#To create category title-id dictionary

def setCatDic():
  global titleIdDic, idTitleDic
  
  fread=open("getCategoryTitleById.txt","r")
  
  for line in fread:
    word=line.split()
    titleIdDic[word[1]]=word[0]
    idTitleDic[word[0]]=word[1]
    

#To create category  title-id and page id-title dictionary

def setPageCatDic():
  global titleIdDic, idTitleDic
  
  freadCat=open("getCategoryTitleById.txt","r")
  
  for line in freadCat:
    word=line.split()
    titleIdDic[word[1]]=word[0]

  fread=open("getPageTitleById.txt","r")
  
  for line in fread:
    word=line.split()
    idTitleDic[word[0]]=word[1]
  

#links=0 means key = title and value = id
#links=1 means key = id and value = title

def catGetListAndTotal(fread, flistIdById, flistIdByTitle, flistTitleByTitle, ftotalById, ftotalByTitle, links):
  
  global titleIdDic, idTitleDic, cursor

  listOfId=[]
  listOfTitle=[]
  prevKey=""
  first=0
  
  fcatbyvalue=open("../sql/fcatbyvalue.txt","w")
  fpagebyvalue=open("../sql/fpagebyvalue.txt","w")
  
  fread.seek(1896,1)
  #fread.readline(44)
  ch=fread.read(1)
  while ch!="":
    if ch=='(':
      key=""
      value=""
      catType=""
      
#Extracting Key
      ch=fread.read(1)
      while ch!=",":
	  key=key+ch
	  ch=fread.read(1)
	  	  
#Extracting Value
      fread.seek(1,1)
      ch=fread.read(1)
      while ch!="'":
	  value=value+ch
	  ch=fread.read(1)
      
      count=0
      while count<5:
	ch=fread.read(1)
	if ch==',':
	  count=count+1;
      
#Extracting Category type
      fread.seek(1,1)
      ch=fread.read(1)
      while ch!="'":
	  catType=catType+ch
	  ch=fread.read(1)
	  
  
      if catType=='subcat':
	fcatbyvalue.write(("%s\t%s\n") %(value,key))
    
	if prevKey==key:
	  listOfId=addValueToListOfId(key, value, listOfId, links)      
	  listOfTitle=addValueToListOfTitle(key, value, listOfTitle, links)
	  
	else:
	  if first!=0:
	    if links==0:
	      if not titleIdDic.has_key(prevKey):
		prevKey=key
		continue
	      writeListAndTotal(titleIdDic[prevKey], listOfId, ftotalById, flistIdById)
	      writeListAndTotal(prevKey, listOfId, ftotalByTitle, flistIdByTitle)
	      writeList(prevKey, listOfTitle, flistTitleByTitle)
	    else:
	      if not idTitleDic.has_key(prevKey):
		prevKey=key
		continue
	      writeListAndTotal(prevKey, listOfId, ftotalById, flistIdById)
	      writeListAndTotal(idTitleDic[prevKey], listOfId, ftotalByTitle, flistIdByTitle)
	      writeList(idTitleDic[prevKey], listOfTitle, flistTitleByTitle)
	    
	  listOfId=[]
	  prevKey=key
	  listOfTitle=[]
	  
	  listOfId=addValueToListOfId(key, value, listOfId, links)      
	  listOfTitle=addValueToListOfTitle(key, value, listOfTitle, links)
    
      if catType=="page":
	fpagebyvalue.write(("%s\t%s\n") %(value,key))
    first=1
    ch=fread.read(1)
	
  
  
  if links==0:
    if titleIdDic.has_key(key):
      writeListAndTotal(titleIdDic[key], listOfId, ftotalById, flistIdById)
      writeListAndTotal(key, listOfId, ftotalByTitle, flistIdByTitle)
      writeList(key, listOfTitle, flistTitleByTitle)
  else:
    if idTitleDic.has_key(key):  
      writeListAndTotal(key, listOfId, ftotalById, flistIdById)
      writeListAndTotal(idTitleDic[key], listOfId, ftotalByTitle, flistIdByTitle)
      writeList(idTitleDic[key], listOfTitle, flistTitleByTitle)
    
  del listOfId
  del listOfTitle
  flistIdById.close()
  flistIdByTitle.close()
  flistTitleByTitle.close()
  ftotalById.close()
  ftotalByTitle.close()
  
  
def getLinksListAndTotal(fread, flistIdById, flistIdByTitle, flistTitleByTitle, ftotalById, ftotalByTitle, links):
  
  global titleIdDic, idTitleDic, cursor

  listOfId=[]
  listOfTitle=[]
  prevKey=""
  first=0
  
  flinkbyvalue=open("../sql/flinkbyvalue.txt","w")
  
  #fread.seek(1896,1)
  fread.readline(38)
  ch=fread.read(1)
  while ch!="":
    if ch=='(':
      key=""
      value=""
      
#Extracting Key
      ch=fread.read(1)
      while ch!=",":
	  key=key+ch
	  ch=fread.read(1)
	  	  
#Extracting Value
      fread.seek(1,1)
      ch=fread.read(1)
      while ch!="'":
	ch=fread.read(1)
      
      ch=fread.read(1)
      while ch!="'":
	  value=value+ch
	  ch=fread.read(1)
      
      
      if prevKey==key:
	listOfId=addValueToListOfId(key, value, listOfId, links)      
	listOfTitle=addValueToListOfTitle(key, value, listOfTitle, links)
	
      else:
	if first!=0:
	  if links==0:
	    if not titleIdDic.has_key(prevKey):
	      prevKey=key
	      continue
	    writeListAndTotal(titleIdDic[prevKey], listOfId, ftotalById, flistIdById)
	    writeListAndTotal(prevKey, listOfId, ftotalByTitle, flistIdByTitle)
	    writeList(prevKey, listOfTitle, flistTitleByTitle)
	  else:
	    if not idTitleDic.has_key(prevKey):
	      prevKey=key
	      continue
	    writeListAndTotal(prevKey, listOfId, ftotalById, flistIdById)
	    writeListAndTotal(idTitleDic[prevKey], listOfId, ftotalByTitle, flistIdByTitle)
	    writeList(idTitleDic[prevKey], listOfTitle, flistTitleByTitle)
	  
	listOfId=[]
	prevKey=key
	listOfTitle=[]
	
	listOfId=addValueToListOfId(key, value, listOfId, links)      
	listOfTitle=addValueToListOfTitle(key, value, listOfTitle, links)
    
      flinkbyvalue.write(("%s\t%s\n") %(value,key))
    first=1
    ch=fread.read(1)
	
  
  
  if links==0:
    if titleIdDic.has_key(key):
      writeListAndTotal(titleIdDic[key], listOfId, ftotalById, flistIdById)
      writeListAndTotal(key, listOfId, ftotalByTitle, flistIdByTitle)
      writeList(key, listOfTitle, flistTitleByTitle)
  else:
    if idTitleDic.has_key(key):  
      writeListAndTotal(key, listOfId, ftotalById, flistIdById)
      writeListAndTotal(idTitleDic[key], listOfId, ftotalByTitle, flistIdByTitle)
      writeList(idTitleDic[key], listOfTitle, flistTitleByTitle)
    
  del listOfId
  del listOfTitle
  flistIdById.close()
  flistIdByTitle.close()
  flistTitleByTitle.close()
  ftotalById.close()
  ftotalByTitle.close()

  
  
def fileGetListAndTotal(fread, flistIdById, flistIdByTitle, flistTitleByTitle, ftotalById, ftotalByTitle, links):
  
  global titleIdDic, idTitleDic, cursor

  
  listOfId=[]
  listOfTitle=[]
  prevKey=""
  firstline=True

  for line in fread:
    row = line.strip().split()
    
    key=str(row[0])
    value=str(row[1])
    
    if prevKey==key:
      listOfId=addValueToListOfId(key, value, listOfId, links)      
      listOfTitle=addValueToListOfTitle(key, value, listOfTitle, links)
      
    else:
      if not firstline:
	if links==0:
          if not titleIdDic.has_key(prevKey):
	    prevKey=key
            continue
	  writeListAndTotal(titleIdDic[prevKey], listOfId, ftotalById, flistIdById)
	  writeListAndTotal(prevKey, listOfId, ftotalByTitle, flistIdByTitle)
	  writeList(prevKey, listOfTitle, flistTitleByTitle)
	else:
          if not idTitleDic.has_key(prevKey):
	    prevKey=key
            continue
	  writeListAndTotal(prevKey, listOfId, ftotalById, flistIdById)
	  writeListAndTotal(idTitleDic[prevKey], listOfId, ftotalByTitle, flistIdByTitle)
	  writeList(idTitleDic[prevKey], listOfTitle, flistTitleByTitle)
	
      listOfId=[]
      prevKey=key
      listOfTitle=[]
      
      listOfId=addValueToListOfId(key, value, listOfId, links)      
      listOfTitle=addValueToListOfTitle(key, value, listOfTitle, links)      
	
    prevKey=key
    firstline=False
    
    
  if links==0:
    if titleIdDic.has_key(key):
      writeListAndTotal(titleIdDic[key], listOfId, ftotalById, flistIdById)
      writeListAndTotal(key, listOfId, ftotalByTitle, flistIdByTitle)
      writeList(key, listOfTitle, flistTitleByTitle)
  else:
    if idTitleDic.has_key(key):
      writeListAndTotal(key, listOfId, ftotalById, flistIdById)
      writeListAndTotal(idTitleDic[key], listOfId, ftotalByTitle, flistIdByTitle)
      writeList(idTitleDic[key], listOfTitle, flistTitleByTitle)
    
  del listOfId
  del listOfTitle
  flistIdById.close()
  flistIdByTitle.close()
  flistTitleByTitle.close()
  ftotalById.close()
  ftotalByTitle.close()
  



def addValueToListOfId(key , value, listOfId, links ):
  if links==0:
    if idTitleDic.has_key(value) and titleIdDic.has_key(key):
      listOfId.append(value)
  else:
    if titleIdDic.has_key(value) and idTitleDic.has_key(key):
      listOfId.append(titleIdDic[value]) 
    
  return listOfId


    
def addValueToListOfTitle(key , value, listOfTitle, links):
  if links==0:
    if idTitleDic.has_key(value) and titleIdDic.has_key(key):
      listOfTitle.append(idTitleDic[value])
  else:
    if titleIdDic.has_key(value) and idTitleDic.has_key(key):
      listOfTitle.append(value)
    
  return listOfTitle



def writeListAndTotal(key, listOfValue, ftotal, flist):
  flist.write(key+"\t")
  ftotal.write(key+"\t")
  count=len(listOfValue)
  for x in range(count):
    flist.write(str(listOfValue[x]))
    if x!=count-1:
      flist.write(",")
  flist.write("\n")
  ftotal.write(str(count)+"\n")
  

def writeList(key, listOfValue, flist):
  flist.write(key+"\t")
  count=len(listOfValue)
  for x in range(count):
    flist.write(str(listOfValue[x]))
    if x!=count-1:
      flist.write(",")
  flist.write("\n")



def inLinks():
  print "Creating inlink data..."
  os.system("sort ../sql/flinkbyvalue.txt >../sql/sortedpagelinks.txt")
  fgetListOfInlinksIdById= open("../sql/getListOfInlinksIdById.txt","w")
  fgetListOfInlinksIdByTitle= open("../sql/getListOfInlinksIdByTitle.txt","w")
  fgetListOfInlinksTitleByTitle= open("../sql/getListOfInlinksTitleByTitle.txt","w")
  fgetTotalInlinksById= open("../sql/getTotalInlinksById.txt","w")
  fgetTotalInlinksByTitle= open("../sql/getTotalInlinksByTitle.txt","w")
  
  filename=open("../sql/sortedpagelinks.txt","r")
  
  fileGetListAndTotal(filename, fgetListOfInlinksIdById, fgetListOfInlinksIdByTitle, fgetListOfInlinksTitleByTitle, fgetTotalInlinksById, fgetTotalInlinksByTitle, 0)
  
  fgetListOfInlinksIdById.close()
  fgetListOfInlinksIdByTitle.close()
  fgetListOfInlinksTitleByTitle.close()
  fgetTotalInlinksById.close()
  fgetTotalInlinksByTitle.close()
  print "Done"
 
  
def outLinks():
  print "Creating outlink data..."
  fgetListOfOutlinksIdById= open("../sql/getListOfOutlinksIdById.txt","w")
  fgetListOfOutlinksIdByTitle= open("../sql/getListOfOutlinksIdByTitle.txt","w")
  fgetListOfOutlinksTitleByTitle= open("../sql/getListOfOutlinksTitleByTitle.txt","w")
  fgetTotalOutlinksById= open("../sql/getTotalOutlinksById.txt","w")
  fgetTotalOutlinksByTitle= open("../sql/getTotalOutlinksByTitle.txt","w")
  
  filename=open("../WikiDatasets/enwiki-latest-pagelinks.sql","r")
  
  getLinksListAndTotal(filename, fgetListOfOutlinksIdById, fgetListOfOutlinksIdByTitle, fgetListOfOutlinksTitleByTitle, fgetTotalOutlinksById, fgetTotalOutlinksByTitle, 1)
 
  fgetListOfOutlinksIdById.close()
  fgetListOfOutlinksIdByTitle.close()
  fgetListOfOutlinksTitleByTitle.close()
  fgetTotalOutlinksById.close()
  fgetTotalOutlinksByTitle.close()
  print "Done"


def catChildren():
  print "Creating category children data..."
  fgetListOfChildrenIdById= open("../sql/getListOfChildrenIdById.txt","w")
  fgetListOfChildrenIdByTitle= open("../sql/getListOfChildrenIdByTitle.txt","w")
  fgetListOfChildrenTitleByTitle= open("../sql/getListOfChildrenTitleByTitle.txt","w")
  fgetNoOfChildrenById= open("../sql/getNoOfChildrenById.txt","w")
  fgetNoOfChildrenByTitle= open("../sql/getNoOfChildrenByTitle.txt","w")
  
  filename=open("../sql/sortedcat.txt","r")

  fileGetListAndTotal(filename, fgetListOfChildrenIdById, fgetListOfChildrenIdByTitle, fgetListOfChildrenTitleByTitle, fgetNoOfChildrenById, fgetNoOfChildrenByTitle, 0)
 
  fgetListOfChildrenIdById.close()
  fgetListOfChildrenIdByTitle.close()
  fgetListOfChildrenTitleByTitle.close()
  fgetNoOfChildrenById.close()
  fgetNoOfChildrenByTitle.close()
  print "Done"
 

def catParent():
  print "Creating category parents  data..."
  fgetListOfParentsIdById= open("../sql/getListOfParentsIdById.txt","w")
  fgetListOfParentsIdByTitle= open("../sql/getListOfParentsIdByTitle.txt","w")
  fgetListOfParentsTitleByTitle= open("../sql/getListOfParentsTitleByTitle.txt","w")
  fgetNoOfParentsById= open("../sql/getNoOfParentsById.txt","w")
  fgetNoOfParentsByTitle= open("../sql/getNoOfParentsByTitle.txt","w")
  
  filename=open("../WikiDatasets/enwiki-latest-categorylinks.sql","r")

  catGetListAndTotal(filename, fgetListOfParentsIdById, fgetListOfParentsIdByTitle, fgetListOfParentsTitleByTitle, fgetNoOfParentsById, fgetNoOfParentsByTitle, 1)
 
  fgetListOfParentsIdById.close()
  fgetListOfParentsIdByTitle.close()
  fgetListOfParentsTitleByTitle.close()
  fgetNoOfParentsById.close()
  fgetNoOfParentsByTitle.close()
  print "Done"
  

def catPage():
  print "Creating category page data..."
  fgetListOfPageIdById= open("../sql/getListOfPageIdById.txt","w")
  fgetListOfPageIdByTitle= open("../sql/getListOfPageIdByTitle.txt","w")
  fgetListOfPageTitleByTitle= open("../sql/getListOfPageTitleByTitle.txt","w")
  fgetNoOfPageById= open("../sql/getNoOfPageById.txt","w")
  fgetNoOfPageByTitle= open("../sql/getNoOfPageByTitle.txt","w")
  
  filename=open("../sql/sortedcatpage.txt","r")

  fileGetListAndTotal(filename, fgetListOfPageIdById, fgetListOfPageIdByTitle, fgetListOfPageTitleByTitle, fgetNoOfPageById, fgetNoOfPageByTitle, 0)
 
  fgetListOfPageIdById.close()
  fgetListOfPageIdByTitle.close()
  fgetListOfPageTitleByTitle.close()
  fgetNoOfPageById.close()
  fgetNoOfPageByTitle.close()
  print "Done"



def sortFiles():
  os.system("sort ../sql/fcatbyvalue.txt >../sql/sortedcat.txt")
  os.system("sort ../sql/fpagebyvalue.txt >../sql/sortedcatpage.txt")
  
 
 
if __name__ == '__main__':

  titleIdDic.clear()
  idTitleDic.clear()
  os.mkdir("../sql")
  setCatDic()
  catParent()
  sortFiles()
  catChildren()
  titleIdDic.clear()
  idTitleDic.clear()
  setPageCatDic()
  catPage()
  titleIdDic.clear()
  idTitleDic.clear()
  setPageDic()
  outLinks()
  inLinks()
  del titleIdDic
  del idTitleDic
