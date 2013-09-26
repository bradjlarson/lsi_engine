from gensim import corpora, models, similarities
from urllib import unquote_plus
import MySQLdb as mdb
import sys
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

stop_list = set("the of and he our ? had it?s there time out know  one you're what just so get like could people \
, - it's some how but av don't their who when we're would do don?t they me his were she her had its to a in for \
is on that by this with i you it not or be are from at as your all have new more an was we will home can us about \
if page my has".split())

#This assumes a query to a MySQL DB, but this can be changed
def get_data(query, con):
	with con:
		cur = con.cursor(mdb.cursors.DictCursor)
		cur.execute(query)
		return cur.fetchall()

#This function assumes takes escaped text and returns the un-escaped form				
def clean_text(dirty):
	return unquote_plus(dirty)

#This is a generator that yields one DB result at a time	
def prep_data(query, con):
	data = get_data(query, con)
	for row in data:
		#cleaned = clean_text(row[article_text])
		yield clean_text(row["article_text"])			

#This function isn't working yet, but eventually it will remove all words that only appear once from the corpus
def remove_singles(texts):
	return [[word for word in text if word not in tokens_once] for text in texts]

#this converts normal text documents (spaces and the like) to tokens		
def to_texts(docs, stop_list):
	texts = [[word for word in doc.lower().split() if word not in stop_list] for doc in docs]
	return texts

#this converts a collection of tokens to a bag of words count
def to_dict(texts, filename=False):
	dictnry = corpora.Dictionary(texts)
	if filename:
		dictnry.save('%s.dict' % filename)
	return dictnry

#this converts a collection of tokens to an id mapping based on a dictionary
def to_corpus(dictnry, texts, filename=False):
	corpus = [dictnry.doc2bow(text) for text in texts]
	if filename:
		corpora.MmCorpus.serialize('%s.mm' % filename, corpus)
	return corpus

#this returns a corpus and dictionary based on a query and a connection
#It also provides options for a stop list and the ability to save the dictionary and corpus	
def get_corpus(query, con, stop_list=[], filename=False):
	docs = prep_data(query, con)
	texts = to_texts(docs, stop_list)
	dictnry = to_dict(texts, filename)
	return (to_corpus(dictnry, texts, filename), dictnry)

#this returns a TF-IDF model and a TF-IDF transformed corpus, with the option to save to filename	
def build_tfidf(corpus, filename=False):
	tfidf = models.TfidfModel(corpus)
	if filename:
		tfidf.save('%s.tfidf' % filename)
	return (tfidf[corpus], tfidf)

#this returns TF-IDF and LSI models, a LSI transformed corpus and an index for searching, with the option to save to a filename	
def build_lsi(corpus, dictnry, filename=False, n_topics=150):
	(t_corpus, tfidf) = build_tfidf(corpus, filename)
	lsi = models.LsiModel(t_corpus, id2word=dictnry, num_topics=n_topics)
	l_corpus = lsi[t_corpus]
	#index = similarities.MatrixSimilarity(l_corpus)
	index = similarities.Similarity('%s_shard' % filename, l_corpus, n_topics)
	if filename:
		lsi.save('%s.lsi' % filename)
		index.save('%s.index' % filename)
	return (l_corpus, tfidf, lsi, index)

#returns a list with the n best matches in tuple form, requires you to pass in the objects
def query_lsi(query, con, dictnry, tfidf, lsi, index, stop_list=[], num_matches=10):
	data = to_texts(prep_data(query, con), stop_list)
	data_bow = [dictnry.doc2bow(doc) for doc in data]
	data_tfidf = tfidf[data_bow]
	data_lsi = lsi[data_tfidf]
	sims = [top_n(index[doc], num_matches) for doc in data_lsi]
	return sims

#returns a list with the n best matches in tuple form, loads the objects from disk
def query_lsi_stored(query, con, filename, stop_list=[], num_matches=10):
	dictnry = corpora.Dictionary.load('%s.dict' % filename)
	tfidf = models.TfidfModel.load('%s.tfidf' % filename)
	lsi = models.LsiModel.load('%s.lsi' % filename)
	index = similarities.Similarity.load('%s.index' % filename)
	data = to_texts(prep_data(query, con), stop_list)
	data_bow = [dictnry.doc2bow(doc) for doc in data]
	data_tfidf = tfidf[data_bow]
	data_lsi = lsi[data_tfidf]
	sims = [top_n(index[doc], num_matches) for doc in data_lsi]
	return sims

#returns the n best matches	
def top_n(query, n):	
	sims = sorted(enumerate(query), key=lambda item: -item[1])
	return sims[:n]