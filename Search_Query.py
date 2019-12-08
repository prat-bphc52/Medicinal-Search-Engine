import nltk
import os
import pickle
from nltk.stem.porter import *
import math
import re, collections
import pyttsx3 as pyttsx
import time


class Query:
    def loadFiles(self):
        """
        loads all the pickle files containing indexes and tf-idf into python dictionary
        """
        print('Powering on...Please wait..')
        self.invertedIndex_overview = pickle.load(open("inverted_ind_overview.p","rb"))
        self.invertedIndex_sideeffects = pickle.load(open("inverted_ind_side_effects.p","rb"))
        print('* Indexes loaded *')
        self.tf_idf_overview = pickle.load(open("tf_idf_overview.p","rb"))
        self.tf_idf_sideeffects = pickle.load(open("tf_idf_side_effects.p","rb"))
        print('* TF-IDF loaded *')

    
    def createVectorSpace(self):
        """
        creates vector space for normalisation of score assigned to a doc
        """
        print('Creating vector space model')
        self.N = 16309 #len of dictionary_overview
        self.N2 = 16746 # len of dict_sideeffects
        self.lengths = {}
        self.lengths2 = {}
        for key in self.tf_idf_overview:  #Finding the length of each vector(doc represented as a vector)
            temp = 0.0
            for word in self.tf_idf_overview[key]:
                temp = temp + self.tf_idf_overview[key][word] * self.tf_idf_overview[key][word]
            self.lengths[key] = math.sqrt(temp)

        for key in self.tf_idf_sideeffects:  #Finding the length of each vector(doc represented as a vector)
            temp = 0.0
            for word in self.tf_idf_sideeffects[key]:
                temp = temp + self.tf_idf_sideeffects[key][word] * self.tf_idf_sideeffects[key][word]
            self.lengths2[key] = math.sqrt(temp)
        print('** Initialization complete **')

    
    def Page_Ranking_Algo(self,query):   
        """
        Uses cosine vector model to rank each document based on the query string and prints the top 10 documents
        based on their normalised ranks
        Arguments:
            query (str): The input string which has to be queried
        """
        Query_Dictionary = {}
        Query_List = []

        stemmer = PorterStemmer()
        for word in query.split():  #Representing query as a vector
            word=word.lower()
            word = stemmer.stem(word)
            if word in Query_Dictionary:
                k=Query_Dictionary[word]
                Query_Dictionary[word] = k+1
            else:
                Query_Dictionary[word] = 1

        for key in Query_Dictionary:
            Query_List.append(key)

        score = {}

        for word in Query_List:     #Calculating the cosine similarity of the query vector with the docs
            weight_q = 0
            if word in self.invertedIndex_overview:
                df = len(self.invertedIndex_overview[word])
                idf = math.log( self.N/( df * 1.0 ), 10.0 )
                weight_q = idf * ( 1.0 + math.log( Query_Dictionary[word] , 10.0))

                for doc in self.invertedIndex_overview[word]:
                    if doc in score:
                        temp = score[doc]
                        weight_d = self.tf_idf_overview[doc][word]
                        score[doc] = temp + weight_q * weight_d
                    else:
                        weight_d = self.tf_idf_overview[doc][word]
                        score[doc] = weight_q * weight_d


        score2 = {}

        for word in Query_List:     #Calculating the cosine similarity of the query vector with the docs
            weight_q = 0
            if word in self.invertedIndex_sideeffects:
                df = len(self.invertedIndex_sideeffects[word])
                idf = math.log( self.N2/( df * 1.0 ), 10.0 )
                weight_q = idf * ( 1.0 + math.log( Query_Dictionary[word] , 10.0))

                for doc in self.invertedIndex_sideeffects[word]:
                    if doc in score:
                        temp = score[doc]
                        weight_d = self.tf_idf_sideeffects[doc][word]
                        score2[doc] = temp + weight_q * weight_d
                    else:
                        weight_d = self.tf_idf_sideeffects[doc][word]
                        score2[doc] = weight_q * weight_d

        rank = []

        for key in score:   #Length Normalization of the cosine similarity
            score[key] = score[key]/(1.0 * self.lengths[key])
            if key in score2 and key in self.lengths2:
                score[key] = score[key] - 0.5*(score2[key]/(1.0 * self.lengths2[key]))
            rank.append((key, score[key]))

        rank = sorted(rank , key=lambda x: x[1], reverse = True)  #sorting all the docs on the basis of their cosine similarity
        print('\nPrescribed Medications for this disease are :\n')
        for i in range(min(10, len(rank))):
            print(rank[i][0])
    
    def Show_Results(self):
        """
        Take search query from user and return a set of relevant medications
        """
        while True:
            print("\nEnter your search query:")
            key = input()
            if key.lower() =='exit':
                exit()
            starttime=time.time()
            self.Page_Ranking_Algo(key)
            print(" ** Query results in ",time.time()-starttime, " seconds **")

if __name__ == '__main__':
    q = Query()
    q.loadFiles()
    q.createVectorSpace()
    q.Show_Results()
