from collections import namedtuple
import argparse
import os
import pickle
import time

import requests
from bs4 import BeautifulSoup

from tuples import *

ROOT_URL = "http://dblp.uni-trier.de/db/conf/"

def get_conf_urls(name):
    root = ROOT_URL + name + "/"
    actual = root + name

    print "Downloading: %s" % root
    r = requests.get(root)
    index = r.content
    page = BeautifulSoup(index, 'html.parser')

    links = page.select("nav a")
    confs = []
    for l in links:
        href = l.get('href')
        if href.startswith(actual) and "best" not in href:
            try:
                i = confs.index(href)
            except ValueError:
                confs.append(href)

    return confs

def get_conf(name, url):
    print "Downloading: %s" % url
    r = requests.get(url)
    page = BeautifulSoup(r.content, 'html.parser')

    elems = page.select("li.inproceedings")
    papers = []
    for p in elems:
        title = p.select(".title")[0].get_text()
        if title[-1] == ".":
            title = title[:-1]
        pid = p['id']
        auths = p.select('span[itemprop=author] a')
        authors = []
        for a in auths:
            author_id = a.get('href')
            author_name = a.span.get_text()
            authors.append(Author(author_id, author_name))
        papers.append(Paper(pid, title, authors))

    year = page.select("span[itemprop=datePublished]")[0].get_text()
    return Conference(name.upper(), year, papers)

def get_all_confs(name):
    urls = get_conf_urls(name)
    confs = []
    for u in urls:
        conf = get_conf(name, u)
        confs.append(conf)
        time.sleep(1.0)
    return confs

def save_to_pickle(name, confs):
    f = open("confs/%s.pickle" % name, "wb")
    pickle.dump(confs, f, -1)
    f.close()

def load_from_pickle(name):
    f = open("confs/%s.pickle" % name, "rb")
    confs = pickle.load(f)
    f.close()
    return confs

def load_conference(name):
    if os.path.exists("confs/%s.pickle" % name):
        return load_from_pickle(name)
    else:
        c = get_all_confs(name)
        save_to_pickle(name, c)
        return c


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape a DBLP conference')
    parser.add_argument('conference', help="The conference short name")
    args = parser.parse_args()

    c = get_all_confs(args.conference.lower())
    save_to_pickle(args.conference.lower(), c)
