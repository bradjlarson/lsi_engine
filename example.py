import lsi_engine
import MySQLdb as mdb
import sys
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

#set up DB connection
con = mdb.connect('url', 'user', 'pass', 'db');
#create our stop list
stop_list = set("the of and he our ? had it?s there time out know  one you're what just so get like could people \
, - it's some how but av don't their who when we're would do don?t they me his were she her had its to a in for \
is on that by this with i you it not or be are from at as your all have new more an was we will home can us about \
if page my has".split())

#set our query to build model
query = "select article_text from db.testing_corpus limit 1000"
#set filename
filename = 'testing'
#get the initial corpus
(corpus, dictnry) = get_corpus(query, con, stop_list, filename)
#build the models and index, with 150 features (or topics)
(l_corpus, tfidf, lsi, index) = build_lsi(corpus, dictnry, filename, 150)
#lsi.print_topics(20) #this would print 20 of the topics used by the model
#set our query again, this time to query against the model	
query = "select article_text from db.testing_corpus limit 10"
#return the 5 best matches for each document
testing = query_lsi(query, con, dictnry, tfidf, lsi, index, stop_list, 5)
#print the results
print testing