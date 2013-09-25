from gensim import corpora, models, similarities
from urllib import unquote_plus
import MySQLdb as mdb
import sys
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def get_data(query, con):
	with con:
		cur = con.cursor(mdb.cursors.DictCursor)
		cur.execute(query)
		return cur.fetchall()
				
def clean_text(dirty):
	return unquote_plus(dirty)
	
def prep_data(query, con):
	data = get_data(query, con)
	for row in data:
		#cleaned = clean_text(row[article_text])
		yield clean_text(row["article_text"])	
	
def to_texts(docs):
	return [[word for word in doc.lower().split()] for doc in docs]

def to_dict(texts, filename=False):
	dictnry = corpora.Dictionary(texts)
	if filename:
		dictnry.save('%s.dict' % filename)
	return dictnry

def to_corpus(dictnry, texts, filename=False):
	corpus = [dictnry.doc2bow(text) for text in texts]
	if filename:
		corpora.MmCorpus.serialize('%s.mm' % filename, corpus)
	return corpus
	
def get_corpus(query, con, filename=False):
	docs = prep_data(query, con)
	texts = to_texts(docs)
	dictnry = to_dict(texts, filename)
	return (to_corpus(dictnry, texts, filename), dictnry)
	
def build_tfidf(corpus, filename=False):
	tfidf = models.TfidfModel(corpus)
	if filename:
		tfidf.save('%s.tfidf' % filename)
	return (tfidf[corpus], tfidf)
	
def build_lsi(corpus, dictnry, filename=False, n_topics=200):
	(t_corpus, tfidf) = build_tfidf(corpus, filename)
	lsi = models.LsiModel(t_corpus, id2word=dictnry, num_topics=n_topics)
	index = similarities.MatrixSimilarity(lsi[t_corpus])
	#index = similarities.Similarity('%s_shard' % filename, lsi[t_corpus], n_topics, num_best=10)
	if filename:
		lsi.save('%s.lsi' % filename)
		index.save('%s.index' % filename)
	return (tfidf, lsi, index)
			
def sort(thing):
	return sorted(enumerate(thing), key=lambda item: -item[1])

def transform_query(docs, dictnry, tfidf, lsi):
	return lsi[tfidf[dictnry.doc2bow(docs)]]

def query_lsi(query, con, dictnry, tfidf, lsi, index, n_results=10):
	query_docs = prep_data(query, con)
	print query_docs
	results = sort(index[transform_query(query_docs, dictnry, tfidf, lsi)])
	return results
			
def query_lsi_stored(query, con, filename, n_results=10):
	dictnry = corpora.Dictionary.load('%s.dict' % filename)
	tfidf = models.TfidfModel.load('%s.tfidf' % filename)
	lsi = models.LsiModel.load('%s.lsi' % filename)
	index = similarities.Similarity.load('%s.index' % filename)
	query_docs = prep_data(query, con)
	results = sort(index[transform_query(query_docs, dictnry, tfidf, lsi)])
	return results