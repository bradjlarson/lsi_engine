import lsi_engine as _
import db
import sys
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

#set up DB connection
con = db.con;
#set our query to build model
query = "select article_id, article_text from jobs.testing_corpus order by RAND()"
#set filename
filename = 'testing'
#this returns an lsi transformed corpus, the original corpus, the TF-IDF and LSI models, index, dictnry, and article_id to index id dictionary
#(l_corpus, o_corpus, tfidf, lsi, index, dictnry, id_mapping) = _.model_lsi_id(query, con, filename)
o_corpus = _.corpora.MmCorpus('%s.mm' % filename)
id_mapping = _.cPickle.load(open('%s.idmap' % filename, 'rb'))
query = "select a.article_id, article_text from jobs.testing_corpus a, jobs.unique_likes b where a.article_id = b.article_id"
#get the 100 most similar documents for each document queried against the model
(q_corpus, q_id_mapping, sims_id) = _.query_lsi_stored_id(query, con, filename, num_matches=151)
probs = _.classifier(con, sims_id, id_mapping, o_corpus, q_id_mapping, q_corpus)
_.save_results(con, probs, 'num matches=151')

#things that i can adjust:
#number of matches to use in NB
#number of features to keep in LSI
#"like" threshold in NB
#similarity threshold in LSI
#number of words to use in classifier (PG modified NB)



"""
reverse_q_mapping = _.invert_dict(q_id_mapping)
#this is a bit manual right now, but in the future there will be a seamless bridge
sql_stmts = _.bridge_lsi_nb(sims_id, id_mapping, corpus)
print sql_stmts
for stmt in sql_stmts:
	model = build_nb(stmt, con, id_mapping, o_corpus)
	index_id = reverse_q_mapping[sql_stmts.index(stmt)]
	this_bow = q_corpus[index_id]
	prob = nb_classify(model, this_bow)
	print "The prob that you will like this article is: %.4f" % prob
	
#(corpus, dictnry, id_mapping, id_dict) = _.get_corpus_id(query, con, _.default_stop_list, 'testing3')

query = "select article_id, article_text from jobs.testing_corpus order by RAND() limit 5"
(sims, sims_id) = _.query_lsi_stored_id(query, con, 'testing3', _.default_stop_list, 5)
print sims_id

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
