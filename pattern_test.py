from pattern.web import Newsfeed, Crawler, crawl
import requests
import justext
import sys

hn = 'https://news.ycombinator.com/rss'
for result in Newsfeed().search(hn)[:5]:
	#for link, source in crawl(result.url):
	#	print link
	#	print source
	print result.title
	response = requests.get(result.url)
	try:
		paragraphs = justext.justext(response.content, justext.get_stoplist("English"))
	except:
		print "Could not retreive:", sys.exc_info()[0]
	else:	
		for para in paragraphs:
			if not para.is_boilerplate:
				print para.text

