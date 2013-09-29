from gensim import corpora, models, similarities
from urllib import unquote_plus
import MySQLdb as mdb
import sys
import cPickle
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

default_stop_list = set("the of and he our ? had it?s there time out know  one you're what just so get like could people \
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
def to_texts(docs, stop_list=default_stop_list):
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
def get_corpus(query, con, stop_list=default_stop_list, filename=False):
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

#allows you to build a LSI model from just a query and a MySQL connection 	
def model_lsi(query, con, filename=False, stop_list=default_stop_list, n_topics=150):
	(corpus, dictnry) = get_corpus(query, con, stop_list, filename)
	(l_corpus, tfidf, lsi, index) = build_lsi(corpus, dictnry, filename, n_topics)
	return (l_corpus, tfidf, lsi, index, dictnry)

#returns a list with the n best matches in tuple form, requires you to pass in the objects
def query_lsi(query, con, dictnry, tfidf, lsi, index, stop_list=default_stop_list, num_matches=10):
	data = to_texts(prep_data(query, con), stop_list)
	data_bow = [dictnry.doc2bow(doc) for doc in data]
	data_tfidf = tfidf[data_bow]
	data_lsi = lsi[data_tfidf]
	sims = [top_n(index[doc], num_matches) for doc in data_lsi]
	return sims

#returns a list with the n best matches in tuple form, loads the objects from disk
def query_lsi_stored(query, con, filename, stop_list=default_stop_list, num_matches=10):
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

#This is a generator that yields one DB result at a time, with two columns,
# one for the db.id, and the other containing the text
def prep_data_id(query, con):
	data = get_data(query, con)
	for row in data:
		#for now i am hard coding the column names, i'll have to add them as passed in values later
		yield [row["article_id"], clean_text(row["article_text"])]

#this converts normal text documents (spaces and the like) to tokens and retains the id value		
def to_texts_id(docs, stop_list=default_stop_list):
	texts = [[doc[0], [word for word in doc[1].lower().split() if word not in stop_list]] for doc in docs]
	return texts

#this converts a collection of tokens to a bag of words count and retains the id value
def to_dict_id(texts, filename=False):
	dictnry = corpora.Dictionary(text[1] for text in texts)
	dictnry.filter_extremes(5, 0.5)
	if filename:
		dictnry.save('%s.dict' % filename)
	return dictnry

#this converts a collection of tokens to an id mapping based on a dictionary as well as an id-to-index mapping
def to_corpus_id(dictnry, texts, filename=False):
	corpus_id = [[text[0], dictnry.doc2bow(text[1])] for text in texts]
	id_mapping = [doc[0] for doc in corpus_id]
	id_dict = {i : {'article_id' : v[0], 'bin_bow' : binary_bow(v[1])} for i, v in enumerate(corpus_id)} 
	corpus = [doc[1] for doc in corpus_id]
	if filename:
		corpora.MmCorpus.serialize('%s.mm' % filename, corpus)
		cPickle.dump(id_mapping, open('%s.idmap' % filename, 'wb'))
	return (corpus, id_mapping, id_dict)
	
#this returns a corpus and dictionary and id-to-index mapping based on a query and a connection
#It also provides options for a stop list and the ability to save the dictionary and corpus	
def get_corpus_id(query, con, stop_list=default_stop_list, filename=False):
	docs = prep_data_id(query, con)
	texts = to_texts_id(docs, stop_list)
	dictnry = to_dict_id(texts, filename)
	(corpus_only, id_mapping, id_dict) = to_corpus_id(dictnry, texts, filename)
	return (corpus_only, dictnry, id_mapping, id_dict)
	
#allows you to build a LSI model from just a query and a MySQL connection and then map results back to your DB
def model_lsi_id(query, con, filename=False, stop_list=default_stop_list, n_topics=150):
	(corpus, dictnry, id_mapping) = get_corpus_id(query, con, stop_list, filename)
	(l_corpus, tfidf, lsi, index) = build_lsi(corpus, dictnry, filename, n_topics)
	return (l_corpus, tfidf, lsi, index, dictnry, id_mapping)

#returns a list with the n best matches in tuple form, requires you to pass in the objects
def query_lsi_id(query, con, dictnry, tfidf, lsi, index, id_mapping, stop_list=default_stop_list, num_matches=10):
	texts = to_texts_id(prep_data_id(query, con), stop_list)
	(corpus, query_id_mapping) = to_corpus_id(dictnry, texts)
	corpus_tfidf = tfidf[corpus]
	corpus_lsi = lsi[corpus_tfidf]
	sims = [top_n(index[doc], num_matches) for doc in corpus_lsi]
	sims_id = [[query_id_mapping[sims.index(sim)][0], [(id_mapping[tup[0]][0], tup[1]) for tup in sim]] for sim in sims]
	return (sims, sims_id)	
			
#returns a list with the n best matches in tuple form, loads the objects from disk
def query_lsi_stored_id(query, con, filename, stop_list=default_stop_list, num_matches=10):
	dictnry = corpora.Dictionary.load('%s.dict' % filename)
	tfidf = models.TfidfModel.load('%s.tfidf' % filename)
	lsi = models.LsiModel.load('%s.lsi' % filename)
	index = similarities.Similarity.load('%s.index' % filename)
	id_mapping = cPickle.load(open('%s.idmap' % filename, 'rb'))
	texts = to_texts_id(prep_data_id(query, con), stop_list)
	(corpus, query_id_mapping) = to_corpus_id(dictnry, texts)
	corpus_tfidf = tfidf[corpus]
	corpus_lsi = lsi[corpus_tfidf]
	sims = [top_n(index[doc], num_matches) for doc in corpus_lsi]
	sims_id = [[query_id_mapping[sims.index(sim)][0], [(id_mapping[tup[0]][0], tup[1]) for tup in sim]] for sim in sims]
	#old: sims_id = [[(id_mapping[tup[0]][0], tup[1]) for tup in sim] for sim in sims]
	return (sims, sims_id)
	
#thought is to implement a dictionary to store the id_mappings, with the corpus number as the index
#would then have another dictionary as the value, with keys for any number of values
#each of those values could then be predicted against

#after i get the similar articles, i need to pull the like, dislike information
#step 1: get similar articles from dict
#step 2: split into like list, dislike list
#step 3: map list to word counts from corpus
#step 4: map word counts to binary has word/doesn't
#step 5: reduces the list to a single sparse vector, summing by word across articles
#step 6: reduce that list to a % of category
#step 7: for each word in the text to be classified, map to (% of like / % of like + % of dislike)
#step 8: reduce list by summing (ln(1-p) - ln(p)) across items
#step 9: return prob as (1 / 1 + e^(result from step 8))

def binary_bow(b_o_w):
	return [(w[0], one_or_zero(w[1])) for word in b_o_w]

def one_or_zero(num):
	if num >= 1:
		return 1
	else:
		return 0




