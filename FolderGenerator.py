#!/usr/bin/python

import os

#To save root folder path
root=""

#Dictionary to save metaData

metaDic={
  'checkCategoryTitle': 0,
  'checkRedirectByTitle' :0, 
  'checkPageTitle': 0, 
  'checkDisambiguationByTitle': 0, 
  'checkWord':0}


#To save path of all api's
def pathList():
  
  
  #Category
  path = {'checkCategoryId': 'finalDataSets/categoryDataSets/basics/checkCategoryId/'}
  path.update({'getCategoryIdByTitle': 'finalDataSets/categoryDataSets/basics/getCategoryIdByTitle/'})
  path.update({'checkCategoryTitle': 'finalDataSets/categoryDataSets/basics/checkCategoryTitle/'})
  path.update({'getCategoryTitleById': 'finalDataSets/categoryDataSets/basics/getCategoryTitleById/'})

  path.update({'getCategoryURLById': 'finalDataSets/categoryDataSets/url/getCategoryURLById/'})
  path.update({'getCategoryURLByTitle': 'finalDataSets/categoryDataSets/url/getCategoryURLByTitle/'})

  path.update({'getListOfChildrenIdById': 'finalDataSets/categoryDataSets/children/getListOfChildrenIdById/'})
  path.update({'getListOfChildrenIdByTitle': 'finalDataSets/categoryDataSets/children/getListOfChildrenIdByTitle/'})
  path.update({'getListOfChildrenTitleByTitle': 'finalDataSets/categoryDataSets/children/getListOfChildrenTitleByTitle/'})
  path.update({'getNoOfChildrenById': 'finalDataSets/categoryDataSets/children/getNoOfChildrenById/'})
  path.update({'getNoOfChildrenByTitle': 'finalDataSets/categoryDataSets/children/getNoOfChildrenByTitle/'})

  path.update({'getNoOfParentsById': 'finalDataSets/categoryDataSets/parent/getNoOfParentsById/'})
  path.update({'getNoOfParentsByTitle': 'finalDataSets/categoryDataSets/parent/getNoOfParentsByTitle/'})
  path.update({'getListOfParentsIdById': 'finalDataSets/categoryDataSets/parent/getListOfParentsIdById/'})
  path.update({'getListOfParentsIdByTitle': 'finalDataSets/categoryDataSets/parent/getListOfParentsIdByTitle/'})
  path.update({'getListOfParentsTitleByTitle': 'finalDataSets/categoryDataSets/parent/getListOfParentsTitleByTitle/'})

  path.update({'getNoOfPageById': 'finalDataSets/categoryDataSets/page/getNoOfPageById/'})
  path.update({'getNoOfPageByTitle': 'finalDataSets/categoryDataSets/page/getNoOfPageByTitle/'})
  path.update({'getListOfPageIdById': 'finalDataSets/categoryDataSets/page/getListOfPageIdById/'})
  path.update({'getListOfPageIdByTitle': 'finalDataSets/categoryDataSets/page/getListOfPageIdByTitle/'})
  path.update({'getListOfPageTitleByTitle': 'finalDataSets/categoryDataSets/page/getListOfPageTitleByTitle/'})


  #Page
  path.update({'checkPageId': 'finalDataSets/pageDataSets/basics/checkPageId/'})
  path.update({'checkPageTitle': 'finalDataSets/pageDataSets/basics/checkPageTitle/'})
  path.update({'getPageIdByTitle': 'finalDataSets/pageDataSets/basics/getPageIdByTitle/'})
  path.update({'getPageTitleById': 'finalDataSets/pageDataSets/basics/getPageTitleById/'})	#not using
  path.update({'getTotalCatById': 'finalDataSets/pageDataSets/category/getTotalCatById/'})
  path.update({'getTotalCatByTitle': 'finalDataSets/pageDataSets/category/getTotalCatByTitle/'})
  path.update({'getListOfCatById': 'finalDataSets/pageDataSets/category/getListOfCatById/'})
  path.update({'getListOfCatByTitle': 'finalDataSets/pageDataSets/category/getListOfCatByTitle/'})

  path.update({'checkDisambiguationByTitle': 'finalDataSets/pageDataSets/disambiguation/checkDisambiguationByTitle/'})
  path.update({'check+1DisambiguationById': 'finalDataSets/pageDataSets/disambiguation/checkDisambiguationById/'})	#not using

  path.update({'checkRedirectByTitle': 'finalDataSets/pageDataSets/redirect/checkRedirectByTitle/'})
  path.update({'checkRedirectById': 'finalDataSets/pageDataSets/redirect/checkRedirectById/'})
  path.update({'getTotalRedirectById': 'finalDataSets/pageDataSets/redirect/getTotalRedirectById/'})
  path.update({'getTotalRedirectByTitle': 'finalDataSets/pageDataSets/redirect/getTotalRedirectByTitle/'})	
  path.update({'getRedirectTitleByTitle': 'finalDataSets/pageDataSets/redirect/getRedirectTitleByTitle/'})
  path.update({'getRedirectTitleById': 'finalDataSets/pageDataSets/redirect/getRedirectTitleById/'})
  path.update({'getListOfRedirectTitleById': 'finalDataSets/pageDataSets/redirect/getListOfRedirectTitleById/'})
  path.update({'getListOfRedirectTitleByTitle': 'finalDataSets/pageDataSets/redirect/getListOfRedirectTitleByTitle/'})	

  path.update({'getPageURLById': 'finalDataSets/pageDataSets/url/getPageURLById/'})
  path.update({'getPageURLByTitle': 'finalDataSets/pageDataSets/url/getPageURLByTitle/'})

  path.update({'getListOfInlinksIdById': 'finalDataSets/pageDataSets/inlinks/getListOfInlinksIdById/'})	#missing
  path.update({'getListOfInlinksIdByTitle': 'finalDataSets/pageDataSets/inlinks/getListOfInlinksIdByTitle/'})#missing
  path.update({'getTotalInlinksById': 'finalDataSets/pageDataSets/inlinks/getTotalInlinksById/'})
  path.update({'getTotalInlinksByTitle': 'finalDataSets/pageDataSets/inlinks/getTotalInlinksByTitle/'})
  path.update({'getListOfInlinksTitleByTitle': 'finalDataSets/pageDataSets/inlinks/getListOfInlinksTitleByTitle/'})	

  #path.update({'getOutlinkListById': 'finalDataSets/pageDataSets/outlinks/getOutlinkListByIdgetListOfOutlinksIdByTitle/'})	#missing sqldumpextractor'''
  path.update({'getListOfOutlinksIdById': 'finalDataSets/pageDataSets/outlinks/getListOfOutlinksIdById/'})
  #path.update({'getOutlinkListByTitle': 'finalDataSets/pageDataSets/outlinks/getOutlinkListByTitle/'}) #missing
  path.update({'getListOfOutlinksIdByTitle': 'finalDataSets/pageDataSets/outlinks/getListOfOutlinksIdByTitle/'})
  path.update({'getTotalOutlinksById': 'finalDataSets/pageDataSets/outlinks/getTotalOutlinksById/'})
  path.update({'getTotalOutlinksByTitle': 'finalDataSets/pageDataSets/outlinks/getTotalOutlinksByTitle/'})
  path.update({'getListOfOutlinksTitleByTitle': 'finalDataSets/pageDataSets/outlinks/getListOfOutlinksTitleByTitle/'})	

  path.update({'getPlainTextById': 'finalDataSets/pageDataSets/text/getPlainTextById/'})	
  path.update({'getPlainTextByTitle': 'finalDataSets/pageDataSets/text/getPlainTextByTitle/'})
  path.update({'getXmlTextById': 'finalDataSets/pageDataSets/text/getXmlTextById/'})
  path.update({'getXmlTextByTitle': 'finalDataSets/pageDataSets/text/getXmlTextByTitle/'})

  #Word
  path.update({'getWordById': 'finalDataSets/wordSearchDataSets/getWordById/'})
  path.update({'checkWord': 'finalDataSets/wordSearchDataSets/checkWord/'})	
  path.update({'getIdByWord': 'finalDataSets/wordSearchDataSets/getIdByWord/'})
  path.update({'frequencyCount': 'finalDataSets/wordSearchDataSets/frequencyCount/'})
  path.update({'getNoOfPagesContainsTheWord': 'finalDataSets/wordSearchDataSets/getNoOfPagesContainsTheWord/'})
  path.update({'getListOfPagesContainsTheWord': 'finalDataSets/wordSearchDataSets/getListOfPagesContainsTheWord/'})
  path.update({'getWordsByPageId': 'finalDataSets/wordSearchDataSets/getWordsByPageId/'})
  
  #MetaData
  path.update({'getMetaData': 'finalDataSets/metaDataSets/'})
  
  return path

#Function to generate MetaData

def metaDataWriter():
  global metaDic
  fmetaDatasets=open("metaData.txt","w")
  
  fmetaDatasets.write("getLanguage\tEnglish\n")
  fmetaDatasets.write("getMainCategory\tContents\n")
  fmetaDatasets.write("getMetaId\tnull\n")
  fmetaDatasets.write("getDisAmbiguationCategory\tDisambiguation_pages\n")
  
  fmetaDatasets.write("getTotalCategory\t%d\n"%(metaDic['checkCategoryTitle']))
  fmetaDatasets.write("getTotalRedirectPages\t%d\n"%(metaDic['checkRedirectByTitle']))
  fmetaDatasets.write("getTotalPages\t%d\n"%(metaDic['checkPageTitle']))
  fmetaDatasets.write("getTotalDisambiguationPages\t%d\n"%(metaDic['checkDisambiguationByTitle']))
  fmetaDatasets.write("getToatalNoofDistinctWords\t%d\n"%(metaDic['checkWord']))
  
  fmetaDatasets.close()
  
  
#To divide file into small chungs of 400 entries per file

def fileDivider(file, path):
  filename=file+".txt"
  global root, metaDic
  count=0
  os.chdir(root)
  if os.path.isfile(filename):
    print "Dividing %s to chunks..."%(filename)
    with open(filename) as infile:
      i=0
      newfile=0
      os.chdir(path)
      ftable=open("table.txt","w")
      for line in infile:
        count=count+1
        if i%400==0:
	      ftable.write(line.split("\t")[0]+"\n")
	      fwrite=open(str(newfile),"w")
	      newfile+=1
	      i=0
        fwrite.write(line)
        i+=1
    if metaDic.has_key(file):
      metaDic[file]=count
  else:
    print filename, "is missing"
  

#Create all folders

def folderGen():
  
  path=pathList()

  for key in path.keys():
    global root
    root=os.getcwd();
    listLine = path[key].split('/');
    for i in range(len(listLine)-1):
      folder=listLine[i]
      if not os.path.exists(folder):
	if os.path.exists((listLine[i-1])):
	  os.chdir(listLine[i-1])
	os.mkdir(folder)
	
	if i==len(listLine)-2:
	  #print os.getcwd()
	  os.chdir(folder)
	  if key=='getMetaData':
	    metaDataWriter()
	    
	  else:
	    fileDivider(key, os.getcwd())
      else:
	if i==len(listLine)-2:
	  #print os.getcwd()
	  os.chdir(folder)
	  print "fthfh"
	  if key=='getMetaData':
	    metaDataWriter()
	    
	  else:
	    fileDivider(key, os.getcwd())
	else:
	  os.chdir(folder)
    os.chdir(root);
    
folderGen()
