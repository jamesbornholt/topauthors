import argparse
from collections import Counter, defaultdict
import string

from tuples import *
from scrape import load_conference

def authors_by_year(confs):
    authors = defaultdict(lambda: defaultdict(lambda: 0))

    for conf in confs:
        for paper in conf.papers:
            for author in paper.authors:
                authors[author.name][conf.year] += 1

    return authors

def authors_overall(authors):
    summary = Counter()
    for a in authors:
        summary[a] = sum(authors[a][y] for y in authors[a])

    return summary

def leaderboard_html(confs, name, path, min_papers):
    authors = authors_by_year(confs)
    summary = authors_overall(authors)
    years = set([conf.year for conf in confs])

    table  = "<tr>\n"
    table += "<th class='author'>Author</th>"
    table += "<th class='total'>Total</th>"
    for y in sorted(years):
        table += "<th class='year'>'{0}</th>".format(y[2:])
    table += "\n</tr>\n"

    last_n = summary.most_common(1)[0][1]
    most_common = summary.most_common()
    most_common.sort(key=lambda t: t[0].split()[-1])
    most_common.sort(key=lambda t: t[1], reverse=True)
    for author, n in most_common:
        if n < min_papers:
            break
        if last_n != n:
            table += "<tr class='new-group'>"
            last_n = n
        else:
            table += "<tr>"
        table += "<td class='author'>{0}</td>".format(author)
        table += "<td class='total'>{0}</td>".format(n)
        for y in sorted(years):
            ny = authors[author][y]
            table += "<td class='count'>{0}</td>".format(ny if ny > 0 else "")
        table += "</tr>\n"

    f = open("template.html")
    template = f.read()
    f.close()

    f = open(path, "w")
    f.write(string.Template(template).substitute({'name': name, 'table': table}))
    f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape a DBLP conference')
    parser.add_argument('conference', nargs='+', help="The conference short name")
    parser.add_argument('--min-papers', type=int, default=5, help="Min. papers to include")
    parser.add_argument('--output', '-o', help="Output file")
    args = parser.parse_args()

    confs = []
    for name in args.conference:
        confs.extend(load_conference(name.lower()))

    title = ", ".join(name.upper() for name in args.conference)
    if args.output is None:
        filename = "_".join(name.lower() for name in args.conference)
        output_path = "output/{0}.html".format(filename)
    else:
        output_path = args.output

    leaderboard_html(confs, title, output_path, args.min_papers)
