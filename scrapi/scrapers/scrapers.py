from furl import furl
from bs4 import BeautifulSoup

from scrapi.scrapers import utils


def collect_scraped(uri):

    base = furl(uri).host.replace('www.', '')
    if base == 'sciencedirect.com':
        info = science_direct(uri)
    elif base == 'link.springer.com':
        info = springer_link(uri)
    else:
        info = {}

    return info


# Science Direct


def science_direct(uri):
    '''
    Future potential
    <div id="cited_by_articles">
    <li id="kw0005" class="svKeywords">
    '''

    return parse_sd_author_list(uri)


def parse_sd_author_list(uri):

    soup = BeautifulSoup(utils.get_html_from_link(uri), "lxml")

    auth_affil = soup.find_all("ul", class_="authorGroup")
    lis = [item.find_all('li') for item in auth_affil][0]
    theas = [thing.find_all('a') for thing in lis]

    full_author_info = []
    for author_pair in theas:
        author_info = {}
        for author_part in author_pair:
            author_info = utils.merge_dicts(author_part.attrs, author_info)
            author_info['matcher'] = author_info['href'][0]

        full_author_info.append(author_info)

    # Get affiliations and put them with the original author dict
    outer_affilations = soup.find_all("ul", class_="authAffil")
    affiliations = [item.find_all('li') for item in outer_affilations]

    affils = []
    for person in affiliations:
        for result in person:
            d = result.attrs
            d['institution'] = result.text
            d['matcher'] = d['id']
            affils.append(d)

    all_authors = []
    for author in full_author_info:
        del author['data-pos']
        del author['data-t']
        del author['data-tb']

        for affil in affils:
            if author['matcher'].replace('#', '') == affil['matcher']:
                combined = author.copy()
                combined.update(affil)
                all_authors.append(combined)
        del author['matcher']

    return all_authors


# Springer Link

def springer_link(uri):
    element = utils.get_elements_from_link(uri)
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
