from collections import namedtuple
import argparse
import os
import pickle
import re
import time

import requests
from bs4 import BeautifulSoup

from tuples import *

ROOT_URL = "http://dblp.uni-trier.de/db/conf/"
SESSION_STOPWORDS = ["panel", "keynote", "poster"]
LINK_STOPWORDS = ["best", "w.html"]

def load_name_mappings(path):
    renames = {}
    f = open(path)
    for line in f:
        before, after = line.split("->")
        renames[before.strip()] = after.strip()
    f.close()
    return renames

def get_conf_urls(name):
    root = ROOT_URL + name + "/"
    actual = root + name

    print("Downloading: {0}".format(root))
    r = requests.get(root)
    index = r.content
    page = BeautifulSoup(index, 'html.parser')

    groups = page.select("ul.publ-list")
    confs = []
    for group in groups:
        links = group.select("nav a")
        urls = []
        for l in links:
            href = l.get('href')
            if href.startswith(actual) and all(s not in href for s in LINK_STOPWORDS):
                if href not in urls:
                    urls.append(href)
        # try to select the "best" url for this group: the "conf2015.html" link
        # if it exists, otherwise the first if it exists
        for url in urls:
            if re.search("{0}[0-9]{{2,4}}\.html$".format(name), url):
                confs.append(url)
                break
        else:
            if urls:
                confs.append(urls[0])

    return confs

def get_conf(name, url, renames):
    print("Downloading: {0}".format(url))
    r = requests.get(url)
    page = BeautifulSoup(r.content, 'html.parser')

    datePublished = page.select("span[itemprop=datePublished]")
    if not datePublished:
        print("  Skipped: no datePublished found")
        return None
    year = datePublished[0].get_text()

    elems = page.select("li.inproceedings")
    papers = []
    for p in elems:
        session = p.find_previous("header").get_text().lower()
        if any(s in session for s in SESSION_STOPWORDS):
            continue
        title = p.select(".title")[0].get_text()
        if title[-1] == ".":
            title = title[:-1]
        pid = p['id']
        auths = p.select('span[itemprop=author] a')
        authors = []
        for a in auths:
            author_id = a.get('href')
            author_name = a.span.get_text()
            if author_name in renames:
                author_name = renames[author_name]
            authors.append(Author(author_id, author_name))
        papers.append(Paper(pid, title, authors))

    print("  Found {0} papers".format(len(papers)))

    return Conference(name.upper(), year, papers)

def get_all_confs(name):
    renames = load_name_mappings("names.txt")
    urls = get_conf_urls(name)
    confs = []
    for u in urls:
        conf = get_conf(name, u, renames)
        if conf is not None:
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
