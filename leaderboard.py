import argparse
from collections import Counter, defaultdict

from tuples import *
from scrape import load_conference

def author_lookup(confs):
    author_names = {}
    for conf in confs:
        for paper in conf.papers:
            for author in paper.authors:
                author_names[author.id] = author.name
    return author_names

def authors_by_year(confs):
    authors = defaultdict(lambda: defaultdict(lambda: 0))

    for conf in confs:
        for paper in conf.papers:
            for author in paper.authors:
                authors[author.id][conf.year] += 1

    return authors

def authors_overall(authors):
    summary = Counter()
    for a in authors:
        summary[a] = sum(authors[a][y] for y in authors[a])

    return summary

def leaderboard_html(confs, name):
    authors = authors_by_year(confs)
    summary = authors_overall(authors)
    names = author_lookup(confs)
    years = set([conf.year for conf in confs])

    f = open(name, "w")
    f.write("<link rel='stylesheet' href='table.css' />\n")
    f.write("<table>\n")
    f.write("<tr>\n")
    f.write("<th class='author'>Author</th>")
    for y in sorted(years):
        f.write("<th>%s</th>" % y)
    f.write("<th>Total</th>\n")
    f.write("</tr>\n")

    last_n = summary.most_common(1)[0][1]
    for aid, n in summary.most_common():
        if n < 3:
            break
        if last_n != n:
            f.write("<tr class='new-total'>")
            last_n = n
        else:
            f.write("<tr>")
        f.write(u"<td class='author'>{0}</td>".format(names[aid]).encode('utf8'))
        for y in sorted(years):
            ny = authors[aid][y]
            f.write("<td>%s</td>" % (ny if ny > 0 else ""))
        f.write("<td>%s</td>" % n)
        f.write("</tr>\n")

    f.write("</table>")
    f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape a DBLP conference')
    parser.add_argument('conference', help="The conference short name")
    args = parser.parse_args()

    name = args.conference.lower()

    confs = load_conference(name)
    leaderboard_html(confs, "output/%s.html" % name)
