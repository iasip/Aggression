import json
import urllib2
import re, random

class PreProcessor:
    '''
    This class supports a functionality to read in data from a data file.
    The class supports iteration.
    '''
    def __init__(self, dataFile):
       '''Initialize the DataReader.  Pass in a datafile'''
       self.f = open(dataFile, "r")
       
    def __iter__(self):
       return self

    def next(self):
       ''' Returns the next label/data pair from the data file'''
       self.readNext()

       if self.data == "":
          raise StopIteration
       else:
          return (self.label, self.data)

    def readNext(self):
        '''Read and tokenize the next label/data pair from the file'''
        self.data = ""
        self.label = ""

        for line in self.f:
           line = line.strip()
           match = re.match(r"<LABEL>(.*)<\/LABEL>", line)

           if match:
              self.label = match.group(1)
           elif line == "</TWEET>":
              if self.data != "" and self.label != "":
                 self.data = tokenize(self.data)
                 break
              else:
                 print "Warning: found empty doc"
           elif line == "<TWEET>":
              # a new tweet
              self.data = ""
              self.label = ""
           else:
              self.data += line + "\n"
            
def tokenize(sText):
    '''
    Given a string of text sText, 
    returns a list of the individual tokens 
    that occur in that string (in order).
    '''
    lTokens = []
    sText = sText.lower().strip()
    sToken = ""
    for c in sText:
       if re.match("[a-zA-Z0-9]", str(c)) != None or c == "\'" or c == "_" or c == '-':
          sToken += c
       else:
          if sToken != "":
             lTokens.append(sToken)
             sToken = ""
          if c.strip() != "":
             lTokens.append(str(c.strip()))
               
    if sToken != "":
       lTokens.append(sToken)

    return lTokens

def translate(sText):
    '''
    Given a string of text sText, 
    returns a translation using
    the MyMemory Translation API.
    '''
    url = 'http://api.mymemory.translated.net/get?q='+text+'&langpair=ko|en'.encode('utf-8')
    response = json.load(urllib2.urlopen(url))
    return response['responseData']['translatedText'].encode('utf-8')
