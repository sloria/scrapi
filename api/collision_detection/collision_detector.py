# This file will take an input (JSON) document, and find collision in the database
import sys
import os
import json
sys.path.insert(1, os.path.abspath(os.path.join(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.pardir), os.pardir),
))
from website import search


def detect(doc):

	doc_doc = open(doc, 'r')
	doc_json = json.loads(doc_doc.read())
	title = doc_json['title']

	print title 
	bigword = max(title.split(' '), key=len)
	print json.dumps(search.search('scrapi', str(bigword))

detect('../../collision_test/PLoS/10.1371journal.pbio.0020137/2014-07-08 14:33:06.336347/parsed.json')