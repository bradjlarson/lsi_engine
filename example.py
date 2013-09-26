import lsi_engine
import db
import sys
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

#set up DB connection
con = db.con;
#set our query to build model
query = "select article_text from jobs.testing_corpus order by RAND() limit 1000"
#set filename
filename = 'testing'
#get the initial corpus
(corpus, dictnry) = lsi_engine.get_corpus(query, con, lsi_engine.stop_list, filename)
#build the models and index, with 150 features (or topics)
(l_corpus, tfidf, lsi, index) = lsi_engine.build_lsi(corpus, dictnry, filename, 150)
#lsi.print_topics(20) #this would print 20 of the topics used by the model
#set our query again, this time to query against the model	
query = "select article_text from jobs.testing_corpus order by RAND() limit 10"
#return the 5 best matches for each document
testing = lsi_engine.query_lsi(query, con, dictnry, tfidf, lsi, index, lsi_engine.stop_list, 5)
#print the results
print testing
testing2 = lsi_engine.query_lsi_stored(query, con, filename, lsi_engine.stop_list, 5)
print testing2
