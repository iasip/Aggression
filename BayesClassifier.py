from __future__ import division
import math, os, pickle
from PreProcessor import *

class BayesClassifier:

   def __init__(self):
       '''This method initializes the Naive Bayes classifier'''
       self.labels = []
       self.classes = {}
       self.doc_counts = {}
       self.all_features = set()
       self.total_feature_counts = {}
   
   def train(self, dataFile):   
       '''Trains the Naive Bayes Sentiment Classifier.'''
       reader = PreProcessor(dataFile)
       for label, tokens in reader:
           # remove duplicate tokens because we are only looking at presence
           # not frequency
           tokens_present = set(tokens)
           if label not in self.classes:
               self.classes[label] = {}
               self.doc_counts[label] = 0
               self.labels.append(label)
           else:
               self.doc_counts[label] = self.doc_counts[label]+1
           for token in tokens_present:
               if token in self.classes[label]:
                   self.classes[label][token] = self.classes[label][token]+1
               else:
                   self.all_features.add(token)
                   self.classes[label][token] = 1
       for some_class, features in self.classes.items():
           self.total_feature_counts[some_class] = sum(features.values())

       if len(self.labels) is 2:
           self.filterDicts()

   def classify(self, tweet):
       '''
       Given a target tweet, this function returns the most likely
       class to which the tweet belongs (i.e., aggressive or subdued).
       '''

       total_doc_count = sum(self.doc_counts.values())
       p = lambda label: math.log(self.doc_counts[label] / total_doc_count)
       probs = {label: p(label) for label in self.classes.keys()}
       # define l for smoothing 
       l = 0.01
       
       text = tokenize(tweet)
       for word in text:
           for some_class, features in self.classes.items():
               # ignore word if it doesn't appear in any class of documents
               if word in self.all_features:    
                   total_feature_count = self.total_feature_counts[some_class]
                   if word in features:
                       probs[some_class] +=  math.log((self.classes[some_class][word]+l) / (total_feature_count + (total_feature_count*l)))
               # smooth count of a word that appears in other classes but not this one
                   else:
                       probs[some_class] += math.log((l / (total_feature_count + (total_feature_count*l))))
       
       
       previous = float("-inf")
       max_label = ""
       for label, probability in probs.items():
           if probability > previous:
               previous = probability
               max_label = label
       return max_label

   def save(self, sFilename):
       '''Save the learned data during training to a file using pickle.'''

       f = open(sFilename, "w")
       p = pickle.Pickler(f)
       # use dump to dump your variables
       p.dump(self.labels)
       p.dump(self.classes)
       p.dump(self.doc_counts)
       p.dump(self.all_features)
       p.dump(self.total_feature_counts)
       f.close()

   def load(self, sFilename):
       '''Given a file name of stored data, load and return the object stored in the file.'''

       f = open(sFilename, "r")
       u = pickle.Unpickler(f)
       # use load to load in previously dumped variables
       self.labels = u.load()
       self.classes = u.load()
       self.doc_counts = u.load()
       self.all_features = u.load()
       self.total_feature_counts = u.load()
       f.close()

   def calculate_cpds(self):
       '''
       Categorical Proportional Difference tells us that 
       a feature is more useful if it appears more often 
       in one class than the other.  
       Call this function only if there are two labels.
       '''
       cpds = {}
       class1 = self.labels[0]
       class2 = self.labels[1]

       for key, value in self.classes[class1].items():
           if key in self.classes[class2]:
               # how many documents in class1 have a feature
               df1 = value
               # how many documents in class2 have a feature
               df2 = self.classes[class2][key]
               # how asymmetric the presence of a unigram 
               # is between the two classes
               cpd = math.fabs(df1-df2) / (df1+df2)
               cpds[key] = cpd
       return cpds

   def filterDicts(self):
       '''
       Use the Categorical Proportional Difference metric to 
       prune dictionary / reduce number of features.
       Call this function only if there are two labels.
       '''
       class1 = self.labels[0]
       class2 = self.labels[1]
       cpds = self.calculate_cpds()
       threshold = 0.125
       for feature, cpd in cpds.items():
           if cpd < threshold:
               del self.classes[class1][feature]
               del self.classes[class2][feature]

