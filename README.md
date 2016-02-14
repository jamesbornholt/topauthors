# Top Conference Authors

This is a set of scripts to tell you who the most prolific authors at a conference are.
Inspired by existing lists for [ISCA](http://pages.cs.wisc.edu/~arch/www/iscabibhall.html)
and [OSDI & SOSP](http://from-a-to-remzi.blogspot.com/2013/05/the-systems-top-50.html).

Requires Python 3.

To set up:

    pip3 install -r requirements.txt

To use:

    python3 leaderboard.py asplos

Then open `output/asplos.html`.

You can pass one conference, or many to get an aggregate across all:

    python3 leaderboard.py -o output/systems.html sosp osdi
