import nltk
import re
from nltk.tokenize import sent_tokenize
from nltk.tokenize import WordPunctTokenizer
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus import brown
import numpy as np
import pandas as pd
import json
import pandas as pd
import os
from yahoo_finance import Share
from datetime import datetime,timedelta
import nltk
import httplib
import urllib2
import unicodedata
import re
import socket
import urllib
import csv
import os.path



panda_database = pd.read_json("FT_Database/data.json",orient='index')
###taking articles after 2010
panda_database=panda_database[panda_database['timestamp']>datetime(2010,1,1)]
D30 = {}
Dow_30="""Apple,aapl
American Express,American_Express,Amex,axp
Boeing,ba
Caterpillar,cat
Cisco,csco
Chevron,cvx
Coca-Cola,ko
DuPont,dd
ExxonMobil,Exxon Mobil,Exxon,xom
General Electric,General_Electric,ge
Goldman Sachs,Goldman_Sachs,gs
Home Depot,Home_Depot,hd
IBM,ibm
Intel,intc
Johnson & Johnson,J&J,Johnson and Johnson,jnj
JPMorgan Chase,jpmc,jpm
McDonald's,McDonalds,McDonald,mcd
3M,mmm
Merck,mrk
Microsoft,msft
Nike,nke
Pfizer,pfe
Procter & Gamble,p&g,procter and gamble,pg
Travelers,trv
UnitedHealth,United_Health,unh
United Technologies,United_Technologies,utx
Visa,v
Verizon,vz
Wal-Mart,Walmart,wmt
Walt Disney,Disney,dis"""
f = Dow_30.split('\n')
#f = open('Dow30.txt','r')
for line in f:
	l = [w.lower().strip() for w in line.split(',')]
	#l.extend(similar_by_vector(vector, topn=10, restrict_vocab=None)(l[0]))
	D30[l[0]] = l

word_punct_tokenizer = WordPunctTokenizer()
porter_stemmer = PorterStemmer()
wordnet_lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
stop_words.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}','&']) # remove it if you need punctuation 

def tokenize_doc(doc,_type='LEMMA'):
	sent_tokenize_list = sent_tokenize(doc)
	wordlist = []
	for sentence in sent_tokenize_list:
		word_tokenize_list = [w.lower() for w in word_punct_tokenizer.tokenize(sentence) if w.lower() not in stop_words]
		#remove non alpha num hiphen using regex 
		word_tokenize_list = [w for w in word_tokenize_list if re.search('[A-Za-z0-9]+[._-]*[A-Za-z0-9]*',w) is not None]

		wordpos = nltk.pos_tag(word_tokenize_list)
		if _type is 'STEM':
			word_root_list = [porter_stemmer.stem(word) for word in word_tokenize_list]
		else:
			word_root_list=[]
			for word,postag in wordpos:
				tag = 'n'
				if 'VB' in postag:
					tag='v'
				word_root_list.append(wordnet_lemmatizer.lemmatize(word,tag))

		wordlist.extend(word_root_list)
		# print word_lemmatize_list
	return wordlist    

def search_doc(doc,searchlist):
	for searchterm in searchlist:
		if re.search(searchterm, doc) is not None:
			return True
def tag_corpus(corpus):
    indices = []
    dow_tags = []
    for i,doc in enumerate(corpus):
		for key in D30.keys():
			found = search_doc(doc,D30[key])
			if found is True:
				indices.append(i)
				dow_tags.append(key)
    corpus =[corpus[j] for j in indices]
    return corpus,dow_tags,indices

important_article=[]
important_tags= []

###creating a corpus
initial_corpus = []
for i in range(1000):
    article = (panda_database['content'][i])
    article = unicodedata.normalize('NFKD', article).encode('ascii','ignore')    
    initial_corpus.append(article)
    print i
important_article,important_tags,indices = tag_corpus(initial_corpus)
dates = []
for i in indices:
    temp = datetime.strftime(panda_database['timestamp'][i],'%d-%b-%Y')
    temp = temp[:7]+temp[9:]
    if temp[0]=='0':
        temp=temp[1:]
    dates.append(temp)

article_dataframe = pd.DataFrame({'date':dates,'content':important_article,'company':important_tags})
ticker_symbol = []
for i in range(len(article_dataframe)):
    word = article_dataframe['company'][i]
    ticker_symbol.append(D30[word][-1])
article_dataframe['ticker']=ticker_symbol

for i in indices:
    if os.path.exists("data/"+ticker_symbol[i]+".csv")==False:
        testfile = urllib.URLopener()
        testfile.retrieve("https://www.google.com/finance/historical?output=csv&startdate=Jan+01%2C+2010&q="+ticker_symbol[i], "data/"+ticker_symbol[i]+".csv")


openp=[]
closep=[]
nextopenp=[]
nextclosep=[]


for i in indices:
    my_list=[]
    with open("data/"+ticker_symbol[i]+".csv", 'r') as my_file:
        reader = csv.reader(my_file)
        my_list = list(reader)
    my_list=my_list[1:]

    sdates=[]
    for m in my_list:
        sdates.append(m[0])

    if dates[i] in sdates:
        try:
            pi = sdates.index(dates[i])
            openp.append(my_list[pi][1])
            closep.append(my_list[pi][4])
            nextopenp.append(my_list[pi+1][1])
            nextclosep.append(my_list[pi+1][4])
        except:
            print "Out of bound"
            openp.append(0)
            closep.append(0)
            nextopenp.append(0)
            nextclosep.append(0)
    else:
            openp.append(0)
            closep.append(0)
            nextopenp.append(0)
            nextclosep.append(0)

    # else:
    #     while True:
    #         temp=dates[i]
    #         tmy=temp[-7:]
    #         d=temp.split('-')[0]
    #         if (int(d)+1)>31:
    #             break
    #         temp=str(int(d)+1)+tmy
    #         if temp in sdates:
    #             try:
    #                 pi = sdates.index(temp)
    #                 openp.append(my_list[pi][1])
    #                 closep.append(my_list[pi][3])
    #                 nextopenp.append(my_list[pi+1][1])
    #                 nextclosep.append(my_list[pi+1][3])
    #             except:
    #                 print "Out of bound"
    #             break


article_dataframe["Open"]=openp
article_dataframe["Close"]=closep
article_dataframe["NextOpen"]=nextopenp
article_dataframe["NextClose"]=nextclosep

print article_dataframe[:][:6]

