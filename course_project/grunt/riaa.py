# Gathering data from RIAA about Gold & Platinum LP/EP/Single and saving into ../data/riaa.csv

# 1. Get list of awards
# 2. Get Award, Artist, Title, Certification date, Label, Format and ID
# 3. Get detailed information by ID: Release date, Category, Type, Certified Units and Genre (from Jan '15)

import re
import ast
import requests
from bs4 import BeautifulSoup


class Row:
    def __init__(self):
        self.award = None
        self.artist = None
        self.title = None
        self.certification_date = None
        self.label = None
        self.format = None
        self.ID = None
        self.release_date = None
        self.category = None
        self.type = None
        self.certified_units = None
        self.genre = None

    def export(self, sep):
        return sep.join([
            self.ID.replace(sep, '\\' + sep),
            self.award.replace(sep, '\\' + sep),
            self.artist.replace(sep, '\\' + sep),
            self.title.replace(sep, '\\' + sep),
            self.certification_date.replace(sep, '\\' + sep),
            self.label.replace(sep, '\\' + sep),
            self.format.replace(sep, '\\' + sep),
            self.release_date.replace(sep, '\\' + sep),
            self.category.replace(sep, '\\' + sep),
            self.type.replace(sep, '\\' + sep),
            self.certified_units.replace(sep, '\\' + sep),
            self.genre.replace(sep, '\\' + sep)
        ])


def save(rows):
    with open('../data/riaa.csv', 'a') as file:
        file.write('\n'.join([ row.export(';') for row in rows ]))
        file.write('\n')

def parse_list(data):
    parsed = []
    for item in data.find_all('tr'):
        item_parsed = parse_item(item)
        if item_parsed is None:
            continue
        parsed.append(item_parsed)
    return parsed

IDs = []

js_id_regex = re.compile('(\\d+)')
award_id_regex = re.compile('/icons/(.*)\\.png')
award_given = re.compile('(\\d+)_big')
def parse_item(item):
    row = Row()
    row.ID = js_id_regex.search(item.find('a')['onclick']).groups()[0]
    if row.ID in IDs:
        print('Skipping ID duplicate, ' + row.ID)
        return None
    
    IDs.append(row.ID)

    td = item.find_all('td')
    td_award = td[0].find('img')['src']
    award_id = award_id_regex.search(td_award).groups()[0]
    award_id = award_id.replace('la_', '')

    award = award_given.search(award_id)
    if len(award.groups()) == 1:
        given = int(award.groups()[0])
        if given == 0:
            row.award = 'Gold'
        elif given > 0 and given < 10:
            row.award = 'Platinum'
        elif given > 9:
            row.award = 'Diamond'
        else:
            row.award = award_id
    else:
        row.award = award_id

    row.artist = td[1].text
    row.title = td[2].text
    row.certification_date = td[3].text
    row.label = td[4].text
    row.format = td[5].text

    return add_details(row)

def add_details(row):
    body = {
        'action': 'load_detail_from_recent',
        'id': row.ID,
        'mobile': 'false'
    }
    response = get_data('https://www.riaa.com/wp-admin/admin-ajax.php', body)
    print('[%d] %s, Get details for %s' % (response.status_code, response.reason, row.ID))

    data_raw = response.text.encode('utf-8').decode('unicode_escape')[1:-1]
    data_raw = data_raw.replace('\\n', '\n').replace('\\/', '/').replace('\\"', '"')
    data_raw = '<table><tbody>' + data_raw + '</tbody></table>'
    data = BeautifulSoup(data_raw, 'html.parser')

    return parse_detailed(row, data)

def parse_detailed(row, data):
    td = data.find('tbody').find('td').find_all('td')

    row.release_date = td[0].text
    row.category = td[2].text
    row.type = td[3].text
    row.certified_units = td[4].text
    row.genre = td[5].text

    return row

def get_data(uri, body):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en,ru;q=0.9,en-US;q=0.8',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.riaa.com',
        'pragma': 'no-cache',
        'referer': uri,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    response = requests.post(uri, data=body, headers=headers)
    # print('Request: ' + uri)
    # print(response.headers)
    # print(body)
    return response

page_items = 30
start_year = 2018

for current in range(0, 43): # till 1963
    year = start_year - current
    print('Year %d' % year)
    for page in range(1, 1000):
        body = {
            'action': 'load_more_search_default',
            'inf': str(page * page_items),
            'sup': str(page_items)
        }
        query = 'tab_active=default-award&ar=&ti=&lab=&genre=&format=&date_option=certification&from=%d-01-01&to=%d-12-31&award=&type=&category=&adv=SEARCH&ord=desc&col=certification_date'
        query = query % (year, year)
        response = get_data('https://www.riaa.com/wp-admin/admin-ajax.php?' + query, body)
        print('[%d] %s, Page %d' % (response.status_code, response.reason, page))

        data_raw = response.text.encode('utf-8').decode('unicode_escape')[1:-1]
        data_raw = data_raw.replace('\\n', '\n').replace('\\/', '/').replace('\\"', '"')
        data_raw = '<table><tbody>' + data_raw + '</tbody></table>'
        data = BeautifulSoup(data_raw, 'html.parser')

        parsed = parse_list(data)
        if len(parsed) == 0:
            break

        save(parsed)
