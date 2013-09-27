import lsi_engine as _
import db
import sys
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

#set up DB connection
con = db.con;
#set our query to build model
query = "select article_id, article_text from jobs.testing_corpus order by RAND() limit 5"
#set filename
filename = 'testing'

def prep_data2(query, con):
	data = _.get_data(query, con)
	for row in data:
		yield [row["article_id"], _.clean_text(row["article_text"])]

def to_texts2(docs, stop_list):
	texts = [[doc[0], [word for word in doc[1].lower().split() if word not in stop_list]] for doc in docs]		
	return text
	
docs = prep_data2(query, con)
#for doc in docs:
#	print doc
texts = to_texts2(docs, _.default_stop_list)
#print texts[:5]	


"""
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
#example of simultaneous corpus and model construction
(l_corpus, tfidf, lsi, index, dictnry) = lsi_engine.model_lsi(query, con, 'testing2')
#example of querying a saved model
testing2 = lsi_engine.query_lsi_stored(query, con, 'testing2', lsi_engine.stop_list, 5)
print testing2
"""
