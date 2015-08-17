from furl import furl
import requests
from lxml import etree
from bs4 import BeautifulSoup


def collect_scraped(uri):

    base = furl(uri).host.replace('www.', '')
    if base == 'sciencedirect.com':
        info = science_direct(base)
    elif base == 'link.springer.com':
        info = springer_link(base)
    else:
        info = {}

    return info


# Generic helpers

def get_elements_from_link(link):
    content = requests.get(link).content
    return etree.HTML(content)


def get_html_from_link(link):
    return requests.get(link).content


# Science Direct

def science_direct(uri):
    soup = BeautifulSoup(get_html_from_link(uri))
    all_authors = soup.find_all("a", class_="authorName")

    return parse_sd_author_list(all_authors)


# Springer Link

def springer_link(uri):
    element = get_elements_from_link(uri)
    return {'open_access': get_springer_open_access(element)}


def get_springer_open_access(element):
    links = element.xpath('//a')
    words = []
    for link in links:
        if 'viewtype' in link.keys():
            if 'webtrekk-track' in link.get('class'):
                words.append(link.get('viewtype'))
    if 'Denial' in words:
        return False
    else:
        return True


def parse_sd_author_list(author_list):
    all_authors = []
    for author in author_list:
        author_info = author.attrs
        author_info['full_name'] = author.text
        all_authors.append(author_info)

    return all_authors
