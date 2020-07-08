#!/home/xeroxcat/python-virtualenvs/org-scrape/bin/python3
"""Scrape to org-mode formatted text.

Usage:
  scrape.py <url> [-e element] [-n] [-t]

Options:
  -e element  A CSS select string specifying the element to scrape from
  -n          Remove blank lines from output
  -t          Removes all org mode <<targets>> generated by pandoc
"""

import requests
from bs4 import BeautifulSoup
import pypandoc
import docopt

def demote_headers(result_set):
    def demote_next(heading_val, parent_val):
        depth = parent_val + 1
        heads = result_set.find_all('h' + str(heading_val))
        while not heads and heading_val < 6:
            heading_val += 1
            heads = result_set.find_all('h' + str(heading_val))

        if heading_val == 6:
            new_head = 'b'
        else:
            new_head = 'h' + str(depth)
            demote_next(heading_val + 1, depth)

        for heading in heads:
            heading.name = new_head

    demote_next(1, 1)
    return result_set


if __name__ == '__main__':
    argv = docopt.docopt(__doc__, version='org-scrape 0.01')

    page = requests.get(argv['<url>'])
    page.raise_for_status()

    soup = BeautifulSoup(page.content, 'html.parser')
    title = '* ' + str(soup.title.contents[0])
    if argv['-e'] and soup.select(argv['-e']):
        cont = soup.select(argv['-e'])[0]
        title += ': ' + argv['-e']
    else:
        cont = soup.body

    cont = demote_headers(cont)

    output = ([title] +
              pypandoc.convert_text(str(cont), 'org', format='html').splitlines())


    if not argv['-t']:
        targetless = []
        for line in output:
            t_beg = line.find('<<') 
            t_end = line[t_beg:].find('>>')
            while t_beg != -1 and t_end != -1:
                line = line[:t_beg] + line[t_end+2:]
                t_beg = line.find('<<') 
                t_end = line[t_beg:].find('>>')
            targetless += [line]
        output = targetless

    if not argv['-n']:
        output = '\n'.join([line for line in output if line.strip() != ""])

    print(output)