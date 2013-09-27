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
	
docs = _.prep_data_id(query, con)
#for doc in docs:
#	print doc
texts = _.to_texts_id(docs, _.default_stop_list)
texts_only = [text[1] for text in texts]
#print texts[:5]
dictnry = _.to_dict_id(texts, filename)
corpus = _.to_corpus_id(dictnry, texts)
id_to_cid = [doc[0], corpus.index(doc)] for doc in corpus]
print id_to_cid


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
