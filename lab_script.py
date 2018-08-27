"""Lab Script.

Usage:
  lab_script.py (--lab LABORATORIO ) [-s SECCION ] [--debug]

Options:
  -h --help                   Show this screen.
  -s --seccion SECCION        Seccion que desea filtrar.
  --version                   Muestra la version.
  -d --debug                  Muestra tabla de puntajes.
  -l --lab LABORATORIO        Laboratorio que desea consultar.

"""

import csv
from docopt import docopt
import requests as req
import json
import datetime
from tabulate import tabulate
import sys
from docopt import docopt

def get_leadearboard(url=None):
    hackers = []
    if not(url):
        return None
    finish = False
    offset = 0
    while not(finish):
        res = req.get(url(offset,100))
        res = json.loads(res.text)
        _hackers = res['models']
        _page = res['page']
        hackers.extend(_hackers)
        offset = _page * 100
        if (_page-1)*100 + len(_hackers) >= res['total']:
            finish = True
    return hackers


def readable_date(date):
    return datetime.datetime.fromtimestamp(int(date)).strftime("%m/%d/%Y %H:%M:%S")


def filter_section(hackers,section):
    if not(section):
        return hackers
    return list(filter(lambda user: len(user['hacker']) >= 7 and str(section) == user['hacker'][6], hackers))


def new_hacker(hacker, params):
    _new_hacker = {param: hacker[param] for param in params}
    return _new_hacker

def add_fecha(hackers):
    for hacker in hackers:
        hacker['fecha'] = readable_date(hacker['timestamp'])
        hacker.pop('timestamp',None)
    return hackers

def map_hackers(hackers, params=['hacker', 'score','timestamp']):
    _new_hackers = list(map(lambda hacker: new_hacker(hacker, params), hackers))
    return _new_hackers


def pretty_print(hackers,headers):
    hackers = list(map(lambda hacker: [hacker[header]for header in headers],hackers))
    print(tabulate(hackers, headers=headers,tablefmt="pipe"))

def get_hackers(lab, section=None,debug=False):
    url = (
            "https://www.hackerrank.com/rest/contests/"
            "iic1103-2018-2-lab{0}/"
            "leaderboard?offset={1}&limit={2}&_=1489594857572"
            )
    url2 = lambda offset,limit: url.format(lab,offset,limit)
    hackers = get_leadearboard(url2)
    function_pipe = [
                        lambda hackers: filter_section(hackers, section),
                        lambda hackers: map_hackers(hackers),
                        lambda hackers: sorted(hackers, key=lambda hacker: (hacker['timestamp'],hacker['score'])),
                        lambda hackers: add_fecha(hackers)
                    ]

    for func in function_pipe:
        hackers = func(hackers)

    print("Cantidad: {0}".format(len(hackers)))
    if debug:
        pretty_print(hackers,headers=['hacker','score','fecha'])
    else:
        with open('Laboratorio {} - {}.csv'.format(lab, section), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["Alumno", "Puntaje"])
            _hackers = list(map(lambda hacker: (hacker['hacker'],hacker['score']), hackers))
            for hacker in _hackers:
                writer.writerow([hacker[0], str(hacker[1])])

def main(arguments):
    lab = arguments["--lab"]
    section = arguments["--seccion"]
    debug = arguments["--debug"]
    get_hackers(lab,section,debug)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Lab Script 0.2')
    main(arguments)
