from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

import pymongo,asyncio,pickle,math


global myclient,mydb,mycol,stop_words, dictionary, all_stemmed_words


def perform_stemming(name):
    obj = mycol.find_one({'_id':name})
    if obj is None:
        return
    if not 'overview' in obj:
        return
    overview = obj['overview']
    data=''
    for i in overview:
        temp = i.lower()
        i1 = temp.find('side effects')
        i2 = temp.find('side effect')
        if i1>=0 or i2>=0:
            continue
        data=data+overview[i]
    dictionary[name]={}
    if not data=='':
        #do stemming here
        p = PorterStemmer()
        word=''
        for c in data:
            if c.isalpha():
                word += c.lower()
            else:
                if word:
                    if word not in stop_words:
                        stemmedword = p.stem(word)
                        all_stemmed_words.add(stemmedword)
                        if stemmedword in dictionary[name]:
                            k=dictionary[name][stemmedword]
                            dictionary[name][stemmedword]=k+1
                        else:
                            dictionary[name][stemmedword]=1
                    word=''
    print('completed')


if __name__ == '__main__':
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["irproject"]
    mycol = mydb["medicines"]
    dictionary={}
    all_stemmed_words=set()
    stop_words = set(stopwords.words('english'))
    fr = open("all_medicines.txt", "r")
    filenames = []
    total_docs = 20000
    for i in range(total_docs):
        val = fr.readline().split("=")
        print(str(i+1))
        filenames.append(val[0])
        perform_stemming(val[0])

    inverted_ind={}

    for term in all_stemmed_words:
        inverted_ind[term]=[]
        for file in filenames:
            if file not in dictionary:
                continue
            if term in dictionary[file]:
                inverted_ind[term].append(file)
    tf_idf={}
    n=len(filenames)
    for file in  filenames:
        tf_idf[file]={}
        if file not in dictionary:
            continue
        for key in dictionary[file]:
            tf_idf[file][key]=(1+math.log(dictionary[file][key],10.0))*(math.log(n/(1.0*len(inverted_ind[key])),10.0))
    pickle.dump(dictionary,open("dictionary_overview.p","wb"))
    pickle.dump(inverted_ind,open("inverted_ind_overview.p","wb"))
    pickle.dump(tf_idf,open("tf_idf_overview.p","wb"))

