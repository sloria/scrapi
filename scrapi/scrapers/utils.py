import requests
from lxml import etree


def merge_dicts(*dicts):
    d = {}
    for dict in dicts:
        for key in dict:
            try:
                d[key].append(dict[key])
            except KeyError:
                d[key] = [dict[key]]
    for key in d:
        if len(d[key]) == 1:
            d[key] = d[key][0]

    return d


def get_elements_from_link(link):
    content = requests.get(link).content
    return etree.HTML(content)


def get_html_from_link(link):
    return requests.get(link).content
