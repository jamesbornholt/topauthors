from collections import namedtuple

Conference = namedtuple('Conference', ['name', 'year', 'papers'])
Paper = namedtuple('Paper', ['id', 'title', 'authors'])
Author = namedtuple('Author', ['id', 'name'])
