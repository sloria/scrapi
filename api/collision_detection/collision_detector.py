# This file will take an input (JSON) document, and find collision in the database
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import json
from fuzzywuzzy import fuzz
sys.path.insert(1, os.path.abspath(os.path.join(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.pardir), os.pardir),
))
from website import search


def detect(doc):

    original_doc = open(doc, 'r')
    original_json = json.loads(original_doc.read())
    original_title = original_json['title']
    original_authors = []
    for author in original_json['contributors']:
        original_authors.append(author['full_name'])
    original_author_string = ','.join(original_authors)

    keyword = max(original_title.split(' '), key=len)
    for compare_doc in search.search('scrapi', str(keyword)):
        compare_title = compare_doc['title']
        title_ratio = fuzz.partial_ratio(original_title, compare_title)
        if title_ratio >= 80:
            compare_authors = []
            for author in compare_doc['contributors']:
                compare_authors.append(author['full_name'])
            compare_author_string = ','.join(compare_authors)
            author_ratio = fuzz.token_sort_ratio(original_author_string, compare_author_string)
            if author_ratio >= 70:
                print "\"" + str(compare_title) + "\"" + " is a COLLISION with " + "\"" + str(original_title) + "\""
                return True
            else:
                print "\"" + str(compare_title) + "\"" + " is NOT A COLLISION with " + "\"" + str(original_title) + "\""
                return False
        else: 
            print "\"" + str(compare_title) + "\"" + " is NOT A COLLISION with " + "\"" + str(original_title) + "\""
            return False

# detect('collision_test/PLoS/10.1371journal.pone.0094835/2014-07-09 13:22:14.748995/parsed.json')

